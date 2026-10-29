# -*- coding: utf-8 -*-
"""한비즈 로고 원본 이미지를 조각(투명 PNG)으로 자른다 — 로고를 새로 그리지 않고 주신 픽셀을 그대로 쓴다.

입력  소재/브랜드/logo_symbol_src.png (심볼, 흰 배경 RGB) · logo_horizontal.png (가로형, 실제로는 흰 배경 불투명)
출력  소재/브랜드/logo_symbol.png · logo_part_blue.png · logo_part_warm.png (원래 캔버스 크기·위치)
      logo_wordmark.png · logo_word_ko.png · logo_word_en.png (검정 글자 + 알파)
마지막에 조각을 흰 바탕에 합쳐 원본과의 차이 최대값을 출력한다.
"""
import colorsys
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[2]
BR = ROOT / "소재" / "브랜드"
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def white_to_alpha(rgb, dead=0.025):
    """흰 배경 RGB → RGBA. 알파는 «가까운 안쪽 색에서 흰색까지의 거리 대비» 로, 색은 un-premultiply."""
    c = rgb.astype(np.float64)
    d = 255.0 - c
    m = d.max(2)
    interior = ndi.binary_erosion(m > 60, iterations=3)
    idx = ndi.distance_transform_edt(~interior, return_distances=False, return_indices=True)
    fest = c[idx[0], idx[1]]
    ref = 255.0 - fest
    a = (d * ref).sum(2) / np.maximum((ref * ref).sum(2), 1e-6)
    a = np.clip(a, 0, 1)
    a[a < dead] = 0
    a[a > 0.985] = 1
    f = (c - 255.0 * (1 - a[..., None])) / np.maximum(a[..., None], 1e-6)
    f = np.clip(f, 0, 255)
    f[a == 0] = 0
    return np.dstack([f, a * 255.0])


def save(arr, path):
    Image.fromarray(np.clip(np.rint(arr), 0, 255).astype(np.uint8), "RGBA").save(path)


def hue_deg(rgb):
    h = np.zeros(rgb.shape[:2])
    flat = rgb.reshape(-1, 3) / 255.0
    hh = np.array([colorsys.rgb_to_hsv(*p)[0] for p in flat[:: 1]]).reshape(rgb.shape[:2])
    return hh * 360.0


def composite_white(rgba):
    a = rgba[..., 3:4] / 255.0
    return rgba[..., :3] * a + 255.0 * (1 - a)


def main():
    src = np.array(Image.open(BR / "logo_symbol_src.png").convert("RGB"))
    sym = white_to_alpha(src)
    save(sym, BR / "logo_symbol.png")
    h = hue_deg(np.clip(sym[..., :3], 0, 255))
    blue = (h >= 180) & (h <= 280)
    pb, pw = sym.copy(), sym.copy()
    pb[~blue, 3] = 0
    pw[blue, 3] = 0
    save(pb, BR / "logo_part_blue.png")
    save(pw, BR / "logo_part_warm.png")
    print("심볼", sym.shape[:2], "파랑 픽셀", int((pb[..., 3] > 0).sum()), "주황 픽셀", int((pw[..., 3] > 0).sum()))

    hz = np.array(Image.open(BR / "logo_horizontal.png").convert("RGB")).astype(np.float64)
    # 글자 = 검정(#060606 근처) → 알파만, 색은 검정 그대로
    ink_a = np.clip((255.0 - hz.min(2)) / (255.0 - 6.0), 0, 1)
    ink_a[ink_a < 0.03] = 0
    word = np.dstack([np.full(hz.shape[:2] + (3,), 6.0), ink_a * 255.0])
    x0, x1 = 395, 1999
    save(word[70:357, x0:x1], BR / "logo_wordmark.png")
    save(word[70:252, x0:x1], BR / "logo_word_ko.png")
    save(word[252:357, x0:x1], BR / "logo_word_en.png")

    # 검증 1: 심볼 조각 합성 == 원본
    back = np.clip(composite_white(pb) , 0, 255)
    both = pb.copy()
    # 두 조각을 같은 캔버스에 겹쳐(서로 안 겹침) 합성
    comb = pb.copy()
    comb[pw[..., 3] > 0] = pw[pw[..., 3] > 0]
    rec = composite_white(comb)
    diff = np.abs(rec - src.astype(np.float64))
    print("심볼 조각 합성 vs 원본  최대 차이 %.1f  평균 %.3f  (>12 인 픽셀 %d)" % (diff.max(), diff.mean(), int((diff.max(2) > 12).sum())))
    # 검증 2: 글자 조각 합성 == 가로형 원본 해당 영역
    rec2 = composite_white(word[70:357, x0:x1])
    org2 = hz[70:357, x0:x1]
    d2 = np.abs(rec2 - org2)
    print("글자 합성 vs 원본 영역  최대 차이 %.1f  평균 %.3f" % (d2.max(), d2.mean()))
    # 조각 영역 경계 확인
    ys, xs = np.where(sym[..., 3] > 0)
    print("심볼 알파 영역 x %d~%d y %d~%d" % (xs.min(), xs.max(), ys.min(), ys.max()))


if __name__ == "__main__":
    main()
