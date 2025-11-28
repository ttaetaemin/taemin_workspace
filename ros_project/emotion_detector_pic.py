#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import numpy as np
from deepface import DeepFace

# 분석할 이미지 경로
img_path = "/home/addinedu/dev_ws/ros_project/src/emotion.jpg"

# 분석 옵션
DETECTOR = "opencv"   # ['opencv', 'mediapipe', 'retinaface', 'mtcnn'] 가능
ACTIONS = ['emotion']

# 이미지 로드
frame = cv2.imread(img_path)
if frame is None:
    raise FileNotFoundError(f"이미지를 찾을 수 없습니다: {img_path}")

# DeepFace 분석
results = DeepFace.analyze(
    img_path=frame,
    actions=ACTIONS,
    detector_backend=DETECTOR,
    enforce_detection=False
)

# DeepFace 버전에 따라 list 또는 dict로 반환되므로 방어적으로 처리
if isinstance(results, dict):
    results = [results]

# 분석 결과 표시
for i, result in enumerate(results, 1):
    region = result.get("region", {})
    dominant = result.get("dominant_emotion", "unknown")
    emo_dict = result.get("emotion", {})
    conf = emo_dict.get(dominant, 0)

    x, y, w, h = region.get("x", 0), region.get("y", 0), region.get("w", 0), region.get("h", 0)

    # 바운딩 박스 + 라벨
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    label = f"{dominant} ({conf:.1f}%)"
    cv2.putText(frame, label, (x, max(y - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

# 출력
cv2.imshow("Emotion Detection (Image)", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()

