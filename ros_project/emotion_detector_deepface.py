#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"      # TF 로그 줄이기
os.environ["CUDA_VISIBLE_DEVICES"] = ""       # GPU 미사용 강제(경고 제거용)

import cv2
import numpy as np
from deepface import DeepFace

# 성능/안정화 옵션
DETECTOR = "opencv"   # ['opencv','retinaface','mediapipe','mtcnn' ...] 중 가벼운 opencv 권장
ACTIONS = ['emotion'] # 감정만 수행(속도↑)
SCALE = 0.7           # 프레임 축소 비율(속도↑), 1.0이면 원본
EMO_MAP = ['angry','disgust','fear','happy','sad','surprise','neutral']

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("웹캠을 열 수 없습니다. VideoCapture(0) 실패")

print("▶ 실시간 감정 인식 시작 (종료: q)")
while True:
    ok, frame = cap.read()
    if not ok:
        break

    # 프레임 리사이즈(속도↑)
    if SCALE != 1.0:
        small = cv2.resize(frame, (0,0), fx=SCALE, fy=SCALE)
    else:
        small = frame

    # DeepFace 분석
    try:
        # enforce_detection=False : 얼굴 탐지 실패 시 예외 방지
        result = DeepFace.analyze(
            small,
            actions=ACTIONS,
            detector_backend=DETECTOR,
            enforce_detection=False
        )
        # DeepFace >=0.0.79 계열은 dict 혹은 list로 반환될 수 있어 방어코드
        if isinstance(result, list):
            result = result[0]

        # 박스/감정 꺼내기
        region = result.get('region', None)  # {'x','y','w','h'}
        emo_dict = result.get('emotion', {})
        dominant = result.get('dominant_emotion', None)

        # 원본 프레임 좌표계로 복원
        if region and SCALE != 1.0:
            x = int(region['x'] / SCALE)
            y = int(region['y'] / SCALE)
            w = int(region['w'] / SCALE)
            h = int(region['h'] / SCALE)
        elif region:
            x, y, w, h = region['x'], region['y'], region['w'], region['h']
        else:
            x = y = w = h = None

        # 시각화
        if dominant:
            label = f"{dominant} ({emo_dict.get(dominant, 0):.1f})"
        else:
            label = "no-face"

        if x is not None and w and h:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
            cv2.putText(frame, label, (x, max(y-8, 12)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,255,0), 2)
        else:
            cv2.putText(frame, label, (12, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    except Exception as e:
        # 드물게 백엔드 내부 예외 발생 시 프레임에만 표기
        cv2.putText(frame, f"error: {e}", (12, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

    cv2.imshow("DeepFace Emotion (q to quit)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
