# -*- coding: utf-8 -*-
r"""7번 23.54~28.145 홀로그램 빌딩 분석 — 빌딩숲 영상(2배속) 위 빌딩 추적 (10-21).

사장님: «어떤빌딩이 손해를 ~ 어떤 빌딩이 돈을 벌 수 있는 빌딩인지 이부분 D:\26년 10월\261021 여기 있는 빌딩숲 영상을 활용해서 (원본 영상 한 2배속정도걸어줘)
  각각 건물을 홀로그램 데이터처럼 가격지표 확인하는 듯한 연출 … 준공년도, 현재가치, 미래예상가치, 임차인정보 … 미래시대에 존재할법한 홀로그램같은 그런느낌»
배경 = 빌딩숲.MP4 2.0~11.3초 2배속 → 지시작업/_tmp/r7h/bg2x.mp4 (900×1600 · 59.94).
대상(시작 프레임에서 상자 → 앞뒤로 LK 광류 + 닮음변환 누적):
  L  = 왼쪽 탑(꼭대기 회사 간판 — 상자 위쪽 12% 를 장면에서 덮음) · «손해를 보는 빌딩»
  R  = 오른쪽 광고판(얼굴 광고 — 덮음) · «돈을 벌 수 있는 빌딩»
  C  = 가운데 먼 유리 탑(«어떤 빌딩이» 훑기용)
→ 지시작업/tools/scenes/r7h_track.js (window.TRK = {L:[[x0,y0,x1,y1]|null…], …}) · 확인 _tmp/r7h/track_chk.jpg

    python 지시작업/tools/r7h_track.py
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
DZ = HERE.parent
BG = DZ / "_tmp/r7h/bg2x.mp4"
FPS = 60000 / 1001
# R(광고판 — 얼굴 광고·업체 로고) 는 원근으로 빠르게 커지며 밀려나 광류가 뒤처짐 → 0.5초마다 눈으로 읽은 상자를 이어 씀(_tmp/r7h/rgrid.jpg)
KEYS_R = [(0.0, (470, 440, 600, 612)), (0.67, (560, 418, 700, 606)), (1.0, (608, 410, 733, 620)), (1.5, (626, 414, 765, 630)), (2.0, (648, 396, 792, 594)), (2.5, (659, 356, 806, 594)),
          (3.0, (675, 284, 833, 531)), (3.5, (693, 212, 882, 495)), (4.0, (695, 144, 891, 495)), (4.66, (650, 80, 905, 490))]
# L 꼭대기 업체 간판(LS) · 외벽 세로 병원 간판(LV) — 광류 상자가 뒤로 갈수록 위로 밀려 눈으로 읽은 자리를 이어 씀(_tmp/r7h/lgrid.jpg)
KEYS_LS = [(0.0, (0, 360, 125, 420)), (0.6, (55, 330, 215, 388)), (1.2, (95, 345, 275, 398)), (1.8, (85, 350, 265, 402)), (2.4, (65, 330, 242, 388)),
           (3.0, (40, 275, 242, 332)), (3.5, (15, 235, 218, 296)), (4.0, (0, 205, 192, 268)), (4.66, (0, 198, 135, 268))]
KEYS_LV = [(0.0, (74, 565, 108, 686)), (0.6, (150, 528, 190, 705)), (1.2, (202, 538, 243, 745)), (1.8, (172, 548, 215, 765)), (2.4, (145, 556, 186, 765)),
           (3.0, (130, 486, 174, 684)), (3.5, (99, 446, 146, 664)), (4.0, (55, 425, 101, 644)), (4.66, (35, 425, 81, 634))]
TARGETS = {                        # 이름: (기준 시각, 상자 x0,y0,x1,y1, 유효 구간)
    "L": (1.2, (95, 300, 255, 820), (0.0, 4.66)),
    "C": (1.2, (300, 470, 360, 760), (0.0, 2.6)),
}


def read_frames():
    cap = cv2.VideoCapture(str(BG))
    fr = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        fr.append(f)
    return fr


def track(gray, k0, box, span):
    n = len(gray)
    out = [None] * n
    x0, y0, x1, y1 = box
    mask = np.zeros_like(gray[k0])
    mask[int(y0):int(y1), int(x0):int(x1)] = 255
    corners = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], np.float32)
    out[k0] = box
    for step in (1, -1):
        pts = cv2.goodFeaturesToTrack(gray[k0], 300, .01, 4, mask=mask)
        cur = corners.copy()
        k = k0
        while 0 <= k + step < n and span[0] <= (k + step) / FPS <= span[1] and pts is not None and len(pts) >= 6:
            nxt, st, _ = cv2.calcOpticalFlowPyrLK(gray[k], gray[k + step], pts, None, winSize=(21, 21), maxLevel=4)
            good = st.ravel() == 1
            if good.sum() < 6:
                break
            M, inl = cv2.estimateAffinePartial2D(pts[good], nxt[good], method=cv2.RANSAC, ransacReprojThreshold=3)
            if M is None:
                break
            cur = cv2.transform(cur[None], M)[0]
            k += step
            xs, ys = cur[:, 0], cur[:, 1]
            out[k] = [float(xs.min()), float(ys.min()), float(xs.max()), float(ys.max())]
            keep = nxt[good][inl.ravel() == 1] if inl is not None else nxt[good]
            pts = keep.reshape(-1, 1, 2)
            if len(pts) < 40:                                # 점이 줄면 지금 상자 안에서 다시 뽑음
                m2 = np.zeros_like(mask)
                bx = np.clip(out[k], 0, [900, 1600, 900, 1600]).astype(int)
                m2[bx[1]:bx[3], bx[0]:bx[2]] = 255
                p2 = cv2.goodFeaturesToTrack(gray[k], 300, .01, 4, mask=m2)
                if p2 is not None:
                    pts = p2
    return out


def main():
    fr = read_frames()
    gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in fr]
    res = {}
    for name, (t0, box, span) in TARGETS.items():
        k0 = round(t0 * FPS)
        tr = track(gray, k0, box, span)
        # 살짝 고르게(흔들림 줄임)
        arr = [b for b in tr]
        sm = []
        for i in range(len(arr)):
            win = [arr[j] for j in range(max(0, i - 3), min(len(arr), i + 4)) if arr[j] is not None]
            sm.append([round(float(np.mean([w[c] for w in win])), 1) for c in range(4)] if arr[i] is not None and win else None)
        res[name] = sm
        print(name, "프레임", sum(b is not None for b in sm), "/", len(sm))
    for name, keys in (("R", KEYS_R), ("LS", KEYS_LS), ("LV", KEYS_LV)):
        ts, bs = [k[0] for k in keys], np.array([k[1] for k in keys], float)
        res[name] = [[round(float(np.interp(i / FPS, ts, bs[:, c])), 1) for c in range(4)] if ts[0] <= i / FPS <= ts[-1] else None for i in range(len(fr))]
    (HERE / "scenes/r7h_track.js").write_text("// tools/r7h_track.py 가 만듦 — 프레임별 상자 [x0,y0,x1,y1] (900×1600 · 59.94)\nwindow.TRK = " + json.dumps(res) + ";\n", encoding="utf-8")
    # 확인 시트
    picks = [0, 40, 80, 120, 160, 200, 240, 275]
    tiles = []
    col = {"L": (0, 0, 255), "R": (0, 200, 0), "C": (255, 128, 0), "LS": (255, 0, 255), "LV": (0, 255, 255)}
    for k in picks:
        if k >= len(fr):
            continue
        im = fr[k].copy()
        for name, sm in res.items():
            if sm[k]:
                x0, y0, x1, y1 = map(int, sm[k])
                cv2.rectangle(im, (x0, y0), (x1, y1), col[name], 4)
        tiles.append(cv2.resize(im, (225, 400)))
    (DZ / "_tmp/r7h/track_chk.jpg").write_bytes(cv2.imencode(".jpg", np.hstack(tiles))[1].tobytes())   # 한글 경로라 imwrite 대신


if __name__ == "__main__" and len(sys.argv) == 1:
    sys.stdout.reconfigure(encoding="utf-8")
    main()


# 10-21 «멀리있는거랑 가까있는 건물들도 … 작게라도 분석하는 듯한 느낌» — 빌딩 위 특징점 여러 개를 광류로 따라가 작은 분석 표지를 붙일 자리(MICRO)
def micro():
    fr = read_frames()
    gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in fr]
    n = len(gray)
    mask = np.zeros_like(gray[0])
    mask[120:900, :] = 255                                   # 하늘~건물 높이(도로·차 제외)
    tracks = []
    for k0 in range(0, n - 40, 30):                          # 0.5초마다 새 점을 뽑아 앞으로 따라감
        pts = cv2.goodFeaturesToTrack(gray[k0], 40, .03, 60, mask=mask, blockSize=9)
        if pts is None:
            continue
        for p in pts.reshape(-1, 2):
            tracks.append({"k0": k0, "xy": [[float(p[0]), float(p[1])]]})
        alive = list(range(len(tracks) - len(pts), len(tracks)))
        cur = pts.astype(np.float32)
        for k in range(k0, min(n - 1, k0 + 110)):
            nxt, st, err = cv2.calcOpticalFlowPyrLK(gray[k], gray[k + 1], cur, None, winSize=(21, 21), maxLevel=3)
            keep = []
            for j, idx in enumerate(alive):
                x, y = nxt[j, 0]
                if st[j, 0] and 0 < x < 900 and 60 < y < 1000 and err[j, 0] < 18:
                    tracks[idx]["xy"].append([round(float(x), 1), round(float(y), 1)])
                    keep.append(j)
            alive = [alive[j] for j in keep]
            cur = nxt[keep].reshape(-1, 1, 2)
            if not alive:
                break
    good = [t for t in tracks if len(t["xy"]) >= 60]
    # 서로 너무 가까운(같은 시각 60px 안) 것 덜어냄
    sel = []
    for t in sorted(good, key=lambda t: -len(t["xy"])):
        a = np.array(t["xy"])
        ok = True
        for s in sel:
            o0, o1 = max(t["k0"], s["k0"]), min(t["k0"] + len(t["xy"]), s["k0"] + len(s["xy"]))
            if o1 - o0 > 20:
                b = np.array(s["xy"])
                d = np.linalg.norm(a[o0 - t["k0"]:o1 - t["k0"]] - b[o0 - s["k0"]:o1 - s["k0"]], axis=1).min()
                if d < 70:
                    ok = False
                    break
        if ok:
            sel.append(t)
    (HERE / "scenes/r7h_micro.js").write_text("// tools/r7h_track.py micro 가 만듦 — 작은 분석 표지 자리 {k0: 시작 프레임, xy: [[x,y]…]}\nwindow.MICRO = " + json.dumps(sel) + ";\n", encoding="utf-8")
    print("micro", len(tracks), "→", len(good), "→", len(sel))


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "micro":
    micro()
