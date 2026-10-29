# -*- coding: utf-8 -*-
"""한비즈 심볼(S 두 획) 윤곽을 SVG path 로 뽑는다 — 레이저 엔딩이 따라 그릴 경로.

입력  소재/브랜드/logo_part_blue.png · logo_part_warm.png (1254x1254, 투명, 원래 위치)
출력  소재/브랜드/logo_paths.json   {viewBox, paths:[{id, d, length, start}]}
      _tmp/laser/paths_check.png    경로를 원본 위에 겹친 확인 이미지

방법  알파 128 기준 바깥 윤곽(findContours) → 윤곽 좌표를 순환 가우시안으로 살짝 매끈하게 →
      approxPolyDP(아주 약하게) → Catmull-Rom → 3차 베지어 닫힌 경로.
시작점  파랑: 오른쪽 위 뾰족 끝에서 바깥 호(위쪽 → 왼쪽)를 먼저 돈다 / 주황: 위쪽 뾰족 끝에서 바깥 호(왼쪽 → 아래)를 먼저 돈다.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d

ROOT = Path(__file__).resolve().parents[2]
BR = ROOT / "소재" / "브랜드"
TMP = ROOT / "_tmp" / "laser"
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# (id, 파일, 시작 근처 좌표(뾰족 끝), 처음 도는 방향 검사: 시작 후 8% 지점이 있어야 할 영역)
PARTS = [
    ("blue", "logo_part_blue.png", (1158, 420), lambda p: p[1] < 330 and p[0] < 1100),    # 위쪽 바깥 호로 간다
    ("warm", "logo_part_warm.png", (160, 378), lambda p: p[0] < 200 and p[1] > 450),     # 왼쪽 바깥 호로 간다
]


def largest_contour(alpha):
    a = cv2.GaussianBlur(alpha, (0, 0), 1.0)
    m = (a >= 128).astype(np.uint8) * 255
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    return c[:, 0, :].astype(np.float64)


def smooth_closed(pts, sigma):
    return np.stack([gaussian_filter1d(pts[:, k], sigma, mode="wrap") for k in range(2)], axis=1)


def simplify_closed(pts, eps):
    c = pts.astype(np.float32).reshape(-1, 1, 2)
    ap = cv2.approxPolyDP(c, eps, True)
    return ap[:, 0, :].astype(np.float64)


def catmull_rom_closed(P):
    """닫힌 Catmull-Rom(균일, tension 1/6) → 베지어 path 문자열."""
    n = len(P)
    f = lambda v: ("%.1f" % v).rstrip("0").rstrip(".")  # noqa: E731
    d = "M%s %s" % (f(P[0][0]), f(P[0][1]))
    for i in range(n):
        p0, p1, p2, p3 = P[(i - 1) % n], P[i], P[(i + 1) % n], P[(i + 2) % n]
        c1 = p1 + (p2 - p0) / 6.0
        c2 = p2 - (p3 - p1) / 6.0
        d += "C%s %s %s %s %s %s" % (f(c1[0]), f(c1[1]), f(c2[0]), f(c2[1]), f(p2[0]), f(p2[1]))
    return d + "Z"


def bezier_points(P, per=24):
    n = len(P)
    out = []
    for i in range(n):
        p0, p1, p2, p3 = P[(i - 1) % n], P[i], P[(i + 1) % n], P[(i + 2) % n]
        c1 = p1 + (p2 - p0) / 6.0
        c2 = p2 - (p3 - p1) / 6.0
        for k in range(per):
            u = k / per
            out.append((1 - u) ** 3 * p1 + 3 * (1 - u) ** 2 * u * c1 + 3 * (1 - u) * u ** 2 * c2 + u ** 3 * p2)
    out.append(P[0])
    return np.array(out)


def polyline_length(pts):
    return float(np.sum(np.hypot(*np.diff(pts, axis=0).T)))


def save_png(path, bgr):   # cv2.imwrite 는 한글 경로를 못 쓴다
    Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)).save(path)


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    result = {"viewBox": [1254, 1254], "paths": []}
    sym = np.array(Image.open(BR / "logo_symbol.png").convert("RGBA"))
    bg = np.full((1254, 1254, 3), 8, np.uint8)
    bg[..., 0], bg[..., 1], bg[..., 2] = 8, 13, 34
    a = sym[..., 3:4] / 255.0
    check = (sym[..., :3] * a + bg * (1 - a)).astype(np.uint8)
    check = cv2.cvtColor(check, cv2.COLOR_RGB2BGR)
    for pid, fn, tip, ok_dir in PARTS:
        alpha = np.array(Image.open(BR / fn).convert("RGBA"))[..., 3]
        c = largest_contour(alpha)
        c = smooth_closed(c, 2.0)
        # 시작점 = 뾰족 끝(주어진 좌표에서 가장 가까운 점)
        i0 = int(np.argmin(np.hypot(c[:, 0] - tip[0], c[:, 1] - tip[1])))
        c = np.roll(c, -i0, axis=0)
        # 방향 확인: 8% 지점이 «처음 도는 호» 쪽이어야 한다. 아니면 뒤집는다.
        if not ok_dir(c[int(len(c) * 0.08)]):
            c = np.concatenate([c[:1], c[1:][::-1]])
        assert ok_dir(c[int(len(c) * 0.08)]), pid + " 방향 검사 실패"
        P = simplify_closed(c, 0.7)
        # approxPolyDP 가 시작점을 보존하는지 — 시작 끝점에서 가장 가까운 꼭짓점으로 다시 굴린다
        j = int(np.argmin(np.hypot(P[:, 0] - c[0, 0], P[:, 1] - c[0, 1])))
        P = np.roll(P, -j, axis=0)
        d = catmull_rom_closed(P)
        L = polyline_length(bezier_points(P))
        result["paths"].append({"id": pid, "d": d, "length": round(L, 1), "start": [round(float(P[0][0]), 1), round(float(P[0][1]), 1)], "points": int(len(P))})
        pl = bezier_points(P).astype(np.int32).reshape(-1, 1, 2)
        cv2.polylines(check, [pl], True, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.circle(check, (int(P[0][0]), int(P[0][1])), 9, (0, 255, 255), 2, cv2.LINE_AA)
        q = bezier_points(P)[int(len(bezier_points(P)) * 0.12)]
        cv2.circle(check, (int(q[0]), int(q[1])), 7, (255, 0, 255), 2, cv2.LINE_AA)   # 12% 지점 = 진행 방향 표시
        print(pid, "꼭짓점", len(P), "길이", round(L, 1), "시작", P[0].round(1))
    (BR / "logo_paths.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    save_png(TMP / "paths_check.png", check)
    zoom = check[300:900, 700:1254]
    save_png(TMP / "paths_check_zoom.png", cv2.resize(zoom, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST))
    print("저장:", BR / "logo_paths.json", TMP / "paths_check.png")


if __name__ == "__main__":
    main()
