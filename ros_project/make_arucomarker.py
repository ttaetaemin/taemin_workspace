# -*- coding: utf-8 -*-
# Pinky용 아루코 마커 자동 생성기 (3cm / 4cm / 5cm, IDs = 10, 11, 12)
# 실행: python make_arucomarker.py

import os
import cv2
import cv2.aruco as aruco
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

# 1cm = 72pt / 2.54
CM = 72.0 / 2.54

# 생성 기본 설정
DEFAULT_IDS = [10, 11, 12]
DEFAULT_DICT = aruco.DICT_4X4_50
DEFAULT_OUT = "Aruco_Test_Sheet_REAL_3_4_5cm.pdf"
DEFAULT_DPI = 600  # 이미지 렌더링 품질

# ---------------------------
def gen_marker_png(dictionary, marker_id, px, out_path):
    img = aruco.generateImageMarker(dictionary, marker_id, px)
    cv2.imwrite(out_path, img)

def add_size_row(story, styles, cm, ids, tmp_dir):
    story.append(Paragraph(f"<b>{cm} cm markers</b>", styles['Heading2']))
    row = []
    for mid in ids:
        png_path = os.path.join(tmp_dir, f"{int(cm)}cm_id{mid}.png")
        row.append(Image(png_path, width=cm*CM, height=cm*CM))
    t = Table([row], hAlign='CENTER')
    t.setStyle(TableStyle([
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),10),
        ("RIGHTPADDING",(0,0),(-1,-1),10),
        ("TOPPADDING",(0,0),(-1,-1),8),
        ("BOTTOMPADDING",(0,0),(-1,-1),8)
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

# ---------------------------
def main():
    os.makedirs("_aruco_tmp", exist_ok=True)
    tmp_dir = "_aruco_tmp"

    dictionary = aruco.getPredefinedDictionary(DEFAULT_DICT)
    print(f"[INFO] Dictionary: DICT_4X4_50 | IDs: {DEFAULT_IDS} | Output: {DEFAULT_OUT}")

    # 1) PNG 생성 (3/4/5 cm용)
    for cm in (3.0, 4.0, 5.0):
        for mid in DEFAULT_IDS:
            out_png = os.path.join(tmp_dir, f"{int(cm)}cm_id{mid}.png")
            gen_marker_png(dictionary, mid, DEFAULT_DPI, out_png)

    # 2) PDF 생성
    doc = SimpleDocTemplate(DEFAULT_OUT, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("<b>ArUco Marker Test Sheet (REAL 3/4/5 cm)</b>", styles['Title']))
    story.append(Paragraph("Dictionary: DICT_4X4_50 | Print at 100% (no fit-to-page).", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Tip: Use matte paper, strong contrast. Do NOT scale in printer dialog.", styles['Italic']))
    story.append(Spacer(1, 12))

    # 50mm 스케일 확인용 정사각형
    # story.append(Paragraph("<b>Calibration square (50 mm)</b>", styles['Heading3']))
    # white_png = os.path.join(tmp_dir, "cal_square_50mm.png")
    # cal_img = 255*np.ones((1000,1000), np.uint8)
    # cv2.rectangle(cal_img, (10,10), (990,990), 0, 6)
    # cv2.imwrite(white_png, cal_img)
    # story.append(Image(white_png, width=5.0*CM, height=5.0*CM))
    # story.append(Spacer(1, 16))

    # 3/4/5cm 마커 세트 추가
    for cm in (3.0, 4.0, 5.0):
        add_size_row(story, styles, cm, DEFAULT_IDS, tmp_dir)

    doc.build(story)
    print(f"[OK] PDF saved -> {DEFAULT_OUT}")
    print("✅ Print this file at 100% scale (no fit-to-page). Measure 50 mm box with a ruler.")

if __name__ == "__main__":
    main()
