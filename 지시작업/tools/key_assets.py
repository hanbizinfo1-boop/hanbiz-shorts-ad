# -*- coding: utf-8 -*-
r"""Codex 누끼 소재 → 알파 PNG(<이름>_a.png). 흰 바탕은 «테두리에 이어진 흰색만» 지우고(돈 띠·종이처럼 안쪽 흰색은 남김),
초록(#00FF00) 바탕은 색 키 + 초록 번짐 제거. 가장자리는 1px 깎고 살짝 흐려 붙인 티를 없앤다. 끝에 투명 여백을 잘라 낸다.

    python 지시작업/tools/key_assets.py            # 지시작업/소재/codex/ 의 정해진 목록
"""
import sys
from pathlib import Path

import cv2
import numpy as np

D = Path(__file__).resolve().parents[1] / "소재" / "codex"
WHITE = ["s1_money", "s3_card"]
GREEN = ["2d_scanner", "2d_window", "2d_belt", "2d_doc", "2d_window2",
         "r4_building", "r4_bill", "r4_figure", "r4_house_key", "r4_figure_puzzled",
         "r4x_fig_push", "r4x_fig_flex", "r4x_fig_hit", "r4x_building", "r4y_snail", "r4y_flag"]   # r4m_bundle 은 검은 바탕이라 rembg 로 땀(다시 돌리면 덮어씀)   # 10-20 앞부분 빌딩·인형   # 10-19 4번 레퍼연출 3D 소재
BLACK = ["r4_moneybag", "r4_chartup"]   # 10-19 Codex 가 초록 대신 검은 바탕으로 줌 → 테두리에 이어진 검정만 지운다


def key_white(img, thr=236):
    h, w = img.shape[:2]
    near = (img.min(axis=2) >= thr).astype(np.uint8)
    mask = np.zeros((h + 2, w + 2), np.uint8)
    bg = np.zeros((h, w), np.uint8)
    # 테두리 픽셀 중 흰 것에서만 채우기 시작 — 안쪽 흰색(띠·종이)은 테두리와 이어지지 않으면 남는다
    filled = near.copy() * 255
    for x in range(0, w, 4):
        for y in (0, h - 1):
            if filled[y, x] == 255:
                cv2.floodFill(filled, mask, (x, y), 128)
    for y in range(0, h, 4):
        for x in (0, w - 1):
            if filled[y, x] == 255:
                cv2.floodFill(filled, mask, (x, y), 128)
    bg = (filled == 128).astype(np.uint8)
    a = (1 - bg) * 255
    return a.astype(np.uint8)


def key_black(img, thr=28):
    """테두리에 이어진 거의 검정만 지운다(물체 안 어두운 그림자는 남김)."""
    return key_white(255 - img, 255 - thr)


def key_green(img):
    b, g, r = [img[..., i].astype(np.int16) for i in range(3)]
    spill = g - np.maximum(r, b)
    a = np.clip(255 - (spill - 40) * 4, 0, 255).astype(np.uint8)   # 초록이 40 넘게 앞서면 투명으로
    out = img.copy()
    gg = np.minimum(g, np.maximum(r, b))                             # 초록 번짐 제거
    out[..., 1] = gg.astype(np.uint8)
    return out, a


def finish(bgr, a, path):
    a = cv2.erode(a, np.ones((3, 3), np.uint8), 1)
    a = cv2.GaussianBlur(a, (3, 3), 0)
    ys, xs = np.where(a > 8)
    y0, y1, x0, x1 = max(0, ys.min() - 6), min(a.shape[0], ys.max() + 7), max(0, xs.min() - 6), min(a.shape[1], xs.max() + 7)
    rgba = np.dstack([bgr, a])[y0:y1, x0:x1]
    cv2.imencode(".png", rgba)[1].tofile(str(path))
    print(path.name, rgba.shape[1], "x", rgba.shape[0])


def main():
    for n in WHITE + GREEN + BLACK:
        p = D / f"{n}.png"
        if not p.exists():
            print("없음", p.name)
            continue
        img = cv2.imdecode(np.fromfile(str(p), np.uint8), cv2.IMREAD_COLOR)
        if n in WHITE:
            finish(img, key_white(img), D / f"{n}_a.png")
        elif n in BLACK:
            finish(img, key_black(img), D / f"{n}_a.png")
        else:
            bgr, a = key_green(img)
            finish(bgr, a, D / f"{n}_a.png")


if __name__ == "__main__":
    sys.exit(main())
