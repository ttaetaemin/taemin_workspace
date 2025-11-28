# camera_receiver.py
import socket
import struct
import time
import cv2
import numpy as np

PORT = 5005
GC_SEC = 0.7    # 프레임 타임아웃(수신 느리면 1.0~1.5로)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8 * 1024 * 1024)
sock.bind(("0.0.0.0", PORT))
sock.settimeout(0.5)

frames = {}  # frame_id -> {"chunks": dict, "total": int, "t0": float}

print("[UdpVideoReceiver] listening on UDP", PORT)
last_gc = time.time()
frame_counter = 0


def process_frame(img):
    """여기서 프레임 처리 (나중에 PyQt QLabel에 표시할 때 이 함수만 수정하면 됨)"""
    global frame_counter
    frame_counter += 1
    if frame_counter % 30 == 0:
        h, w, _ = img.shape
        print(f"[UdpVideoReceiver] frame #{frame_counter}, size={w}x{h}")


try:
    while True:
        # 가비지 컬렉션
        now = time.time()
        if now - last_gc > 0.2:
            stale = [fid for fid, d in frames.items() if now - d["t0"] > GC_SEC]
            for fid in stale:
                del frames[fid]
            last_gc = now

        try:
            data, _ = sock.recvfrom(65535)
        except socket.timeout:
            # 타임아웃이면 그냥 다시 대기
            continue

        if len(data) < 8:
            continue

        frame_id, seq, total = struct.unpack("!IHH", data[:8])
        payload = data[8:]

        if frame_id not in frames:
            frames[frame_id] = {"chunks": {}, "total": total, "t0": time.time()}
        entry = frames[frame_id]
        entry["chunks"][seq] = payload
        entry["total"] = total

        if len(entry["chunks"]) == entry["total"]:
            jpg = b"".join(entry["chunks"][i] for i in range(entry["total"]))
            del frames[frame_id]

            img = cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                with open(f"bad_{frame_id}.jpg", "wb") as f:
                    f.write(jpg)
                continue

            # 필요하면 180도 회전
            img = cv2.rotate(img, cv2.ROTATE_180)

            process_frame(img)

finally:
    sock.close()
