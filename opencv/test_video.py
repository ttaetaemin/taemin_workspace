import cv2
import numpy as np

cap = cv2.VideoCapture("/dev/video0")

if not cap.isOpened():
    raise RuntimeError("ERROR! Unable to open camera")

filter_mode = 0  # 0=none, 1=R, 2=G, 3=B

def apply_filter(frame, mode):
    # frame은 BGR 컬러 영상
    if mode == 0:
        return frame
    h, w, _ = frame.shape
    filtered = np.zeros_like(frame)  # 모두 0으로 채운 영상 생성

    if mode == 1:  # R 필터: R 채널만 살림
        filtered[:, :, 2] = frame[:, :, 2]  # R 채널
    elif mode == 2:  # G 필터
        filtered[:, :, 1] = frame[:, :, 1]  # G 채널
    elif mode == 3:  # B 필터
        filtered[:, :, 0] = frame[:, :, 0]  # B 채널
    return filtered

def mouse_callback(event, x, y, flags, param):
    global filter_mode
    if event == cv2.EVENT_LBUTTONDOWN:
        filter_mode = (filter_mode + 1) % 4

cv2.namedWindow("frame")
cv2.setMouseCallback("frame", mouse_callback)

try:
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"width = {width}, height = {height}")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # 1은 좌우반전 (horizontal flip)

        filtered = apply_filter(frame, filter_mode)
        cv2.imshow("frame", filtered)

        if cv2.waitKey(1) == 27:
            break

finally:
    cap.release()
    cv2.destroyAllWindows()