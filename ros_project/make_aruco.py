# -*- coding: utf-8 -*-
"""
A4 한 페이지에 아루코 마커 20개(5x4) 배치하여 PDF 생성
- aruco_grid_3x3_20.pdf  (배치명만 3x3, 딕셔너리는 표준 DICT_4X4_50)
- aruco_grid_4x4_20.pdf  (동일 딕셔너리)
의존성: opencv-contrib-python, matplotlib
"""
import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt

def ensure_aruco():
    if not hasattr(cv2, "aruco"):
        raise RuntimeError(
            "cv2.aruco 모듈이 없습니다. opencv-contrib-python을 설치하세요:\n"
            "  pip install opencv-contrib-python"
        )

def make_grid_pdf(
    pdf_path: str,
    grid_cols: int,
    grid_rows: int,
    dict_name = cv2.aruco.DICT_4X4_50,  # 표준 4x4 딕셔너리로 통일
    first_id: int = 0,
    marker_px: int = 800,
    marker_mm: float = 36.0,   # A4 가로에 5개 들어가도록 조정
    gap_mm: float = 6.0,
    page_size_inch=(8.27, 11.69),  # A4
    dpi=300
):
    ensure_aruco()
    aruco_dict = cv2.aruco.getPredefinedDictionary(dict_name)

    fig = plt.figure(figsize=page_size_inch, dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    page_w_in, page_h_in = page_size_inch
    mm_to_in = 1.0 / 25.4
    marker_w_in = marker_mm * mm_to_in
    gap_w_in = gap_mm * mm_to_in

    total_w_in = grid_cols * marker_w_in + (grid_cols - 1) * gap_w_in
    total_h_in = grid_rows * marker_w_in + (grid_rows - 1) * gap_w_in

    offset_x_in = (page_w_in - total_w_in) / 2.0
    offset_y_in = (page_h_in - total_h_in) / 2.0

    def in_to_figx(x_in): return x_in / page_w_in
    def in_to_figy(y_in): return y_in / page_h_in

    for idx in range(grid_cols * grid_rows):
        marker_id = first_id + idx
        img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_px)
        img = cv2.copyMakeBorder(img, 12, 12, 12, 12, cv2.BORDER_CONSTANT, value=255)

        c = idx % grid_cols
        r = idx // grid_cols

        x_in = offset_x_in + c * (marker_w_in + gap_w_in)
        y_in = offset_y_in + (grid_rows - 1 - r) * (marker_w_in + gap_w_in)

        left = in_to_figx(x_in)
        bottom = in_to_figy(y_in)
        width = in_to_figx(marker_w_in)
        height = in_to_figy(marker_w_in)

        ax_img = fig.add_axes([left, bottom, width, height])
        ax_img.imshow(img, cmap="gray", vmin=0, vmax=255)
        ax_img.axis("off")

        # ID 라벨
        lab_h_in = 3.5 * mm_to_in
        ax_lab = fig.add_axes([left, bottom - in_to_figy(lab_h_in), width, in_to_figy(lab_h_in)])
        ax_lab.axis("off")
        ax_lab.text(0.5, 0.0, f"ID {marker_id}", ha="center", va="top", fontsize=6)

    fig.savefig(pdf_path, format="pdf", dpi=dpi)
    plt.close(fig)
    print(f"✅ Saved: {pdf_path}")

if __name__ == "__main__":
    try:
        # “3x3” 요청분: 한 페이지 20개(5x4) — ID 0~19
        make_grid_pdf("aruco_grid_3x3_20.pdf",
                      grid_cols=5, grid_rows=4,
                      dict_name=cv2.aruco.DICT_4X4_50,
                      first_id=0)

        # “4x4” 요청분: 한 페이지 20개(5x4) — ID 20~39 (겹치지 않게)
        make_grid_pdf("aruco_grid_4x4_20.pdf",
                      grid_cols=5, grid_rows=4,
                      dict_name=cv2.aruco.DICT_4X4_50,
                      first_id=20)
    except Exception as e:
        print("❌ Error:", e)
        sys.exit(1)
