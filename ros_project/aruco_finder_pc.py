import cv2
import cv2.aruco as aruco
import numpy as np

# --- 설정 (이전 생성 코드와 동일하게 유지) ---
ARUCO_DICT = aruco.DICT_4X4_50
TARGET_IDS = [10, 11, 12] # 감지할 마커 ID
# ---------------------------------------------

def detect_aruco_markers():
    """웹캠을 켜고 실시간으로 아루코 마커를 감지하고 결과를 표시합니다."""

    # 1. 아루코 딕셔너리 및 파라미터 로드
    aruco_dict = aruco.getPredefinedDictionary(ARUCO_DICT)
    parameters = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(aruco_dict, parameters)
    
    # 2. 웹캠 초기화 (대부분의 시스템에서 0번이 기본 웹캠입니다.)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ 웹캠을 열 수 없습니다. 카메라 인덱스를 확인하거나, 연결 상태를 확인해 주세요.")
        return

    print(f"[INFO] 웹캠 감지 시작... (Dictionary: {ARUCO_DICT})")
    print("      'q' 키를 누르면 종료됩니다.")

    while True:
        # 프레임 읽기
        ret, frame = cap.read()
        if not ret:
            print("프레임을 읽는 데 실패했습니다.")
            break

        # 프레임이 클 경우 (선택 사항)
        # frame = cv2.resize(frame, (640, 480))

        # 3. 아루코 마커 감지
        # corners: 감지된 마커의 네 모서리 좌표
        # ids: 감지된 마커의 ID
        corners, ids, rejectedImgPoints = detector.detectMarkers(frame)

        # 4. 감지된 마커 처리 및 화면 표시
        if ids is not None:
            # 감지된 마커 주변에 외곽선 및 ID 표시
            aruco.drawDetectedMarkers(frame, corners, ids)

            for i in range(len(ids)):
                marker_id = ids[i][0]
                
                # 생성했던 타겟 ID만 별도로 표시
                if marker_id in TARGET_IDS:
                    
                    # 마커 ID 텍스트 위치 계산 (마커 중앙)
                    c = corners[i][0]
                    center_x = int(np.mean(c[:, 0]))
                    center_y = int(np.mean(c[:, 1]))
                    
                    # 마커 ID 텍스트 표시
                    text = f"ID: {marker_id}"
                    cv2.putText(frame, text, (center_x - 50, center_y + 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
                    
                    # 터미널에 감지 정보 출력 (옵션)
                    # print(f"✅ Marker ID {marker_id} detected!")


        # 5. 결과 화면 표시
        cv2.imshow("ArUco Marker Detector", frame)

        # 'q' 키를 누르면 루프 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 6. 종료 정리
    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] 감지 종료.")

if __name__ == "__main__":
    detect_aruco_markers()