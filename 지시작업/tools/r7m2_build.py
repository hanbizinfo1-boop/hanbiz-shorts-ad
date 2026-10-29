# -*- coding: utf-8 -*-
r"""7번 3.971~7.124 상담 모자이크 V2 — 전체 화면: 상담 사진 한 장에서 줌아웃 → 사진들이 강남빌딩 모자이크 → 실제 건물 (10-21).

사장님(10-21): «뭔가 이게 사진이 너무작아서 상담사진인지 모를거같은데 이걸 전체화면으로하게되면 디자인이나 연출을 어떻게해야 괜찮을까?»
  → ① 한 장에서 줌아웃 추천 → «한번 만들어봐 V2로»
3.97~ 이라 «첫 3초 얼굴» 규칙 밖. 화면 전체를 덮으니 사장님 자막(V2)은 V5 로 올려야 보임.
소재: 상담 사진(소재/r4s5, 서서 찍은 컷 뺌) · 리모델링 후 건물 누끼 bldcut_uh. 장면 scenes/r7m2.html(칸 자리 scenes/r7m2_cells.js).
효과음·미리보기·XML 은 r7m_build 그대로(V4 · A4~ · 3.971).

    python 지시작업/tools/r7m2_build.py cells
    python tools/html_motion.py 지시작업/tools/scenes/r7m4.html --alpha --fps 59.94 --workers 2 --sub 4 --out 지시작업/_tmp/r7m2 --name r7m
    python 지시작업/tools/r7m2_build.py out
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r7m_build as M  # noqa: E402

M.WORK = M.DZ / "_tmp/r7m2"
M.DELIV = M.DZ / "납품/7번_상담모자이크_강남빌딩_v2_1021"
M.NAME = "7번_상담모자이크_강남빌딩_v2"
M.CAP_TOP = True
M.SFX_LIST = [
    (3.98, "8. 훅.mp3", None),                 # 전체 화면 상담 사진으로 바뀜
    (4.58, "SEL_高速移動.mp3", None),          # 줌아웃 · 띠 빨라짐(10-21 띠 판 4.70 → 4.58)
    (6.00, "SEL_キラッ1.mp3", None),           # 실제 건물로 번쩍(10-21 띠 판 5.68 → 6.00)
    (6.50, "맑은소리.mp3", None),              # 금빛 빛
]
BH = 1100                      # 모자이크 건물 높이(세계 좌표 = 마지막 화면 좌표)
CY = 900                       # 마지막 화면에서 건물 가운데 y
TW, TH = 66, 50
HERO = "cs_0_13.jpg"           # 처음 크게 보이는 한 장(앉아서 상담 — 10-21 확인)
STAND = {"cs_0_60.jpg", "cs_0_82.jpg", "cs_2_12.jpg"}


def cells():
    b = Image.open(M.BLD)
    bw = round(BH * b.width / b.height)
    a = np.array(b.resize((bw, BH)).split()[3]) > 128
    x0, y0 = 450 - bw / 2, CY - BH / 2
    cs = []
    for r in range(BH // TH):
        for c in range(bw // TW + 1):
            blk = a[r * TH:(r + 1) * TH, c * TW:(c + 1) * TW]
            if blk.size and blk.mean() > .6:
                cs.append([x0 + c * TW, y0 + r * TH])
    tiles = sorted(p.name for p in (M.DZ / "소재/r4s5").glob("cs_*.jpg") if p.name not in STAND and p.name != HERO)
    rng = np.random.default_rng(7)
    rng.shuffle(tiles)
    # 첫 장 자리: 건물 아래쪽 가운데 근처(줌아웃하면 위로 건물이 드러남)
    hx, hy = 450, y0 + BH * .62
    hero = min(range(len(cs)), key=lambda i: (cs[i][0] + TW / 2 - hx) ** 2 + (cs[i][1] + TH / 2 - hy) ** 2)
    out, k = [], 0
    for i, (x, y) in enumerate(cs):
        if i == hero:
            img = HERO
        else:
            img = tiles[k % len(tiles)]
            k += 1
        out.append(dict(x=x, y=y, img=img))
    (HERE / "scenes/r7m2_cells.js").write_text(
        f"// tools/r7m2_build.py cells 가 만듦 — 칸 {len(cs)}개(사진 {min(k, len(tiles)) + 1}장) · 건물 {bw}×{BH}\n"
        f"window.R7M2 = {json.dumps(dict(cells=out, hero=hero, bw=bw, bh=BH, x0=x0, y0=y0, tw=TW, th=TH))};\n", encoding="utf-8")
    print("칸", len(cs), "· 사진", min(k, len(tiles)) + 1, "장 (겹침", max(0, k - len(tiles)), ")")


# 10-21 완성도 판(사장님 «덩그러니 건물만있으니까 좀 연출이 별로 … 속도가 너무 일정하고 사진도 움직임이 별로없으니까 고급진 느낌이안나
#   … 연출방법은 좋은데 완성도가 떨어진다») — 마지막을 실제 강남 밤거리(Codex set17 소재/codex/r7m_night.png)로, 모자이크 모양 = 그 사진 속 건물 누끼
NIGHT = M.DZ / "소재/codex/r7m_night.png"
NIGHT_BLD = M.DZ / "소재/codex/r7m_night_bld.png"      # rembg birefnet-general
NTW, NTH = 80, 60


def cells_night():
    im = Image.open(NIGHT_BLD)
    sc = 1600 / im.height                                   # 화면 높이에 맞춤(가로는 양옆 잘림)
    nw = round(im.width * sc)
    ox = (900 - nw) / 2
    a = np.array(im.resize((nw, 1600)).split()[3]) > 128
    bb = Image.fromarray(a.astype(np.uint8) * 255).getbbox()
    x0, y0, x1, y1 = bb
    cs = []
    for r in range((y1 - y0) // NTH + 1):
        for c in range((x1 - x0) // NTW + 1):
            X, Y = x0 + c * NTW, y0 + r * NTH
            blk = a[Y:Y + NTH, X:X + NTW]
            if blk.size and blk.mean() > .6:
                cs.append([X + ox, Y])
    tiles = sorted(p.name for p in (M.DZ / "소재/r4s5").glob("cs_*.jpg") if p.name not in STAND and p.name != HERO)
    rng = np.random.default_rng(11)
    rng.shuffle(tiles)
    hx, hy = 450, y0 + (y1 - y0) * .62
    hero = min(range(len(cs)), key=lambda i: (cs[i][0] + NTW / 2 - hx) ** 2 + (cs[i][1] + NTH / 2 - hy) ** 2)
    out, k = [], 0
    for i, (x, y) in enumerate(cs):
        img = HERO if i == hero else tiles[k % len(tiles)]
        k += i != hero
        out.append(dict(x=x, y=y, img=img, ph=round(float(rng.uniform(0, 6.28)), 2), d=round(float(rng.uniform(0, 1)), 3)))
    (HERE / "scenes/r7m3_cells.js").write_text(
        f"// tools/r7m2_build.py night 가 만듦 — 칸 {len(cs)}개 · 밤거리 사진 {nw}×1600 (x {ox:.0f})\n"
        f"window.R7M3 = {json.dumps(dict(cells=out, hero=hero, tw=NTW, th=NTH, nw=nw, ox=ox, bx0=x0 + ox, by0=y0, bx1=x1 + ox, by1=y1))};\n", encoding="utf-8")
    print("칸", len(cs), "· 겹침", max(0, k - len(tiles)))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    M.WORK.mkdir(parents=True, exist_ok=True)
    {"cells": cells, "night": cells_night, "out": M.out}[sys.argv[1]]()
