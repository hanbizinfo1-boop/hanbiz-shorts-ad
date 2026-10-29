# -*- coding: utf-8 -*-
r"""4번 «그런 경험을 한 사람에게 ~ 하는 분이라면» 수강생 세미나 그리드 소재 (10-20).

원본 = 연금형부동산연구소 «새 폴더» 세미나 사진(읽기만) → 4×8 칸 조각(450×400, 칸 2배) · 얼굴 자동 모자이크.
뒤에서 찍힌 사진 위주로 골랐다. 확인용 모음 `_tmp/r4c/grid_check.jpg`.

    python -I 지시작업/tools/r4c_assets.py
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

SRC = Path(r"C:\Users\user\Downloads\연금형부동산연구소\새 폴더")
DZ = Path(__file__).resolve().parent.parent
OUT = DZ / "소재/r4c"
CHK = DZ / "_tmp/r4c"
PICK = ["1366182540193.jpg", "1371878897343.jpg", "1383828090712.jpg", "1385193311675.jpg", "1386401277117.jpg",
        "20150228_144845.jpg", "20150228_153555★.jpg", "20150228_153556.jpg", "20150228_153632.jpg", "20150228_154628.jpg",
        "20150228_154802.jpg", "20150425_140018.jpg", "20150425_140043.jpg", "20150425_141739.jpg", "20150425_143633.jpg",
        "IMG_8530.JPG", "IMG_8538.JPG", "IMG_8611.JPG", "IMG_8633.JPG", "KakaoTalk_20141213_170207764.jpg",
        "KakaoTalk_20141213_170255356.jpg", "KakaoTalk_20141213_170257280.jpg", "KakaoTalk_20141213_170259778.jpg",
        "KakaoTalk_20141213_170726371.jpg", "KakaoTalk_20141213_170726923.jpg", "KakaoTalk_20141220_170341920.jpg",
        "KakaoTalk_20141220_170343803.jpg", "KakaoTalk_20150328_154452540.jpg", "KakaoTalk_20150328_154500673.jpg",
        "KakaoTalk_20150328_154502366.jpg", "KakaoTalk_20150328_164648035.jpg", "KakaoTalk_20150328_164649149.jpg"]
TW, TH = 450, 400          # 칸 225×200 의 2배
YUNET = DZ / "_tmp/models/face_detection_yunet_2023mar.onnx"   # OpenCV 5 에 Haar 가 없어 YuNet(다시 받을 수 있는 모델이라 _tmp)


def mosaic_faces(im):
    """정면 얼굴을 찾아 모자이크(1600px 폭에서 찾음). 찾은 개수를 돌려줌."""
    a = np.array(im)
    s = 1600 / a.shape[1]
    g = cv2.cvtColor(cv2.resize(a, None, fx=s, fy=s), cv2.COLOR_RGB2BGR)
    buf = np.frombuffer(YUNET.read_bytes(), np.uint8)   # 한글 경로를 OpenCV 가 못 읽어 메모리로 넘김
    det = cv2.FaceDetectorYN.create("onnx", buf, np.array([], np.uint8), (g.shape[1], g.shape[0]), 0.55, 0.3, 5000)
    _, f = det.detect(g)
    boxes = [] if f is None else [tuple(int(v) for v in r[:4]) for r in f]
    for x, y, w, h in boxes:
        x0, y0 = int((x - w * .2) / s), int((y - h * .2) / s)
        x1, y1 = int((x + w * 1.2) / s), int((y + h * 1.3) / s)
        x0, y0 = max(0, x0), max(0, y0)
        roi = a[y0:y1, x0:x1]
        if roi.size == 0:
            continue
        k = max(2, (x1 - x0) // 6)
        sm = cv2.resize(roi, (max(1, roi.shape[1] // k), max(1, roi.shape[0] // k)), interpolation=cv2.INTER_LINEAR)
        a[y0:y1, x0:x1] = cv2.resize(sm, (roi.shape[1], roi.shape[0]), interpolation=cv2.INTER_NEAREST)
    return Image.fromarray(a), len(boxes)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    CHK.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGB", (4 * 225, 8 * 200))
    for i, n in enumerate(PICK):
        im = ImageOps.exif_transpose(Image.open(SRC / n)).convert("RGB")
        im, nf = mosaic_faces(im)
        w, h = im.size
        cw = min(w, int(h * TW / TH))                 # 가로 사진 → 칸 비율로 가운데 자름(약간 위쪽: 강사·화면이 들어오게)
        ch = int(cw * TH / TW)
        x0, y0 = (w - cw) // 2, max(0, int((h - ch) * .4))
        t = im.crop((x0, y0, x0 + cw, y0 + ch)).resize((TW, TH), Image.LANCZOS)
        t.save(OUT / f"c_{i:02d}.jpg", quality=92)
        sheet.paste(t.resize((225, 200)), ((i % 4) * 225, (i // 4) * 200))
        print(f"c_{i:02d} 얼굴 {nf} ← {n}")
    sheet.save(CHK / "grid_check.jpg", quality=90)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
