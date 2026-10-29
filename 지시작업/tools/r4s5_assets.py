# -*- coding: utf-8 -*-
r"""4번 15.649~18.835 상담 사진 두 줄 필름 소재 — 클라이언트 상담 사진 모음판 3장을 칸마다 잘라냄 (10-21).

클라이언트(10-20 메신저, 사장님 전달): «강의 사진보다 상담사진이 좋을거같네요 · 돈 있는 분들이 찾는 내용이라서요 · 상담 수백명 온거 홈피에 있는거요»
사장님: «D:\26년 10월\261021 여기있는 사진들로 구성해서 교체해야해» → ② 자막 밑 두 줄 필름 «추천대로가자».
원본(읽기만) = D:\26년 10월\261021\KakaoTalk_20200626_151550823(_01·_02).png — 한 장에 6×9 칸, 상담받은 분 얼굴은 원본에서 이미 모자이크.
흰 여백으로 칸을 찾아 자름 → 지시작업/소재/r4s5/cs_{장}_{줄}{칸}.jpg · 확인 모음 _tmp/r4s5/all.jpg

    python -I 지시작업/tools/r4s5_assets.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path(r"D:\26년 10월\261021")
SHEETS = ["KakaoTalk_20200626_151550823.png", "KakaoTalk_20200626_151550823_01.png", "KakaoTalk_20200626_151550823_02.png"]
DZ = Path(__file__).resolve().parent.parent
OUT = DZ / "소재/r4s5"
CHK = DZ / "_tmp/r4s5"


def runs(v, th=.05, min_len=100):
    on = v > th
    r, s = [], None
    for i, x in enumerate(on):
        if x and s is None:
            s = i
        if not x and s is not None:
            r.append((s, i))
            s = None
    if s is not None:
        r.append((s, len(on)))
    return [x for x in r if x[1] - x[0] > min_len]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    CHK.mkdir(parents=True, exist_ok=True)
    tiles = []
    for k, name in enumerate(SHEETS):
        im = Image.open(SRC / name).convert("RGB")
        g = np.array(im.convert("L")).astype(int)
        cols, rows = runs((g < 235).mean(0)), runs((g < 235).mean(1))
        for r, (y0, y1) in enumerate(rows):
            for c, (x0, x1) in enumerate(cols):
                t = im.crop((x0 + 2, y0 + 2, x1 - 2, y1 - 2))
                p = OUT / f"cs_{k}_{r}{c}.jpg"
                t.save(p, quality=92)
                tiles.append(t)
        print(name, len(rows), "×", len(cols))
    n = len(tiles)
    cw, ch = 180, 135
    per = 18
    sheet = Image.new("RGB", (per * cw, (n + per - 1) // per * ch), "white")
    for i, t in enumerate(tiles):
        sheet.paste(t.resize((cw - 4, ch - 4)), ((i % per) * cw, (i // per) * ch))
    sheet.save(CHK / "all.jpg", quality=85)
    print("칸", n)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
