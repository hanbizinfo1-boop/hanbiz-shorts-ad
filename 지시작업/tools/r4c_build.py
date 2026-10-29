# -*- coding: utf-8 -*-
r"""4번 «그런 경험을 한 사람에게 / 배우고싶다 / 들어보고 싶다 / 하는 분이라면» — 수강생 세미나 그리드 채움 (10-20).

사장님(10-20): «그런경험을 한  ~ 분이라면 이부분 수강생 세미나 부분으로 그리드형식으로 채우는 느낌으로 하는
  하나씩채워지다가 점점점 빨라지면서 슉슉슉슉 채워지는 느낌으로 연출해줘»
기준 = 사장님 «4번» 자동저장 17:00: 52.986~56.707
  V1 52.419~55.239 원본 104.638(→ 이 구간 시작 105.205) · 55.239~56.707 109.376
소재 = tools/r4c_assets.py(세미나 사진 32장 · 얼굴 자동 모자이크). 장면 scenes/r4c.html. XML V4 · A4~.
효과음 = 칸마다 휙1·휙２ 번갈아 한 파일로 묶음(연타는 한 파일 — sfx.md 5-2) → 느림/빠름 두 파일(TAIL_MAX 2.5초) + 꽉 찰 때 반짝.

    python 지시작업/tools/r4c_build.py base / caps / sfx
    python tools/html_motion.py 지시작업/tools/scenes/r4c.html --alpha --fps 59.94 --workers 2 --sub 4 --out 지시작업/_tmp/r4c --name r4c
    python 지시작업/tools/r4c_build.py out
"""
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r4t_build as T  # noqa: E402
X = T.X
SFX = X.SFX

OFFSET = 52.986
T.OFFSET = OFFSET                   # r4t_build.write_xml 이 이 값만큼 뒤로 민다
X.WORK = X.DZ / "_tmp/r4c"
X.DELIV = X.DZ / "납품/4번_수강생_세미나_그리드_1020"
X.NAME = "4번_수강생_세미나_그리드"
X.END = 56.707 - OFFSET
X.CUTS = [(0.0, 55.239 - OFFSET, 105.205), (55.239 - OFFSET, 56.707 - OFFSET, 109.376)]
X.CAPS = [(0.0, 54.438 - OFFSET, [("그런 경험을 한 사람에게", 0)]), (54.438 - OFFSET, 55.239 - OFFSET, [("배우고싶다", 1)]),
          (55.239 - OFFSET, 55.806 - OFFSET, [("들어보고 싶다", 1)]), (55.806 - OFFSET, 56.707 - OFFSET, [("하는 분이라면", 0)])]
T.OVL_NAME = "연출층_수강생_그리드.mov"

# 칸이 들어오는 시각 — scenes/r4c.html 의 TT 와 같은 식
N, FULL = 32, 55.70 - OFFSET
TT = [0.02 + (FULL - 0.02) * (k / (N - 1)) ** 0.55 for k in range(N)]
SPLIT = 8                           # 앞 8칸 = 느림(한 장씩), 나머지 = 빠름(슉슉슉)
RUN = X.ROOT / "소재/효과음/장면음"
X.SFX_LIST = [
    (TT[0] + .0, "그리드_슉_느림.wav", -7, "onset", 0),
    (TT[SPLIT], "그리드_슉_빠름.wav", -7, "onset", 0),
    (FULL, "SEL_キラッ1.mp3", -9, "onset", 0),          # 꽉 찬 순간
]


def make_runs():
    """휙1·휙２ 를 칸 시각마다 번갈아 깐 연타 파일 두 개(느림·빠름). 칸 사이가 짧으면 소리도 그만큼 짧게."""
    SR = SFX.SR
    srcs = []
    for n in ("휙1.mp3", "휙２.mp3"):
        x = SFX.load(SFX.find_file(n))
        a = np.abs(x).max(1)
        x = x[int(np.argmax(a > a.max() * 10 ** (-40 / 20))):]
        srcs.append(x / (np.abs(x).max() + 1e-9))
    for name, ks in (("그리드_슉_느림.wav", range(0, SPLIT)), ("그리드_슉_빠름.wav", range(SPLIT, N))):
        ks = list(ks)
        t0 = TT[ks[0]]
        buf = np.zeros((int((TT[ks[-1]] - t0 + .6) * SR), 2))
        for j, k in enumerate(ks):
            gap = (TT[k + 1] - TT[k]) if k + 1 < N else .5
            x = srcs[j % 2][: int(min(.45, gap * 1.6) * SR)].copy()
            fo = max(1, len(x) // 3)
            x[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
            g = 1.0 if name.endswith("느림.wav") else .75 + .25 * (j / max(1, len(ks) - 1))   # 빠름은 끝으로 갈수록 살짝 커짐
            s0 = int((TT[k] - t0) * SR)
            buf[s0:s0 + len(x)] += x * g
        buf *= .9 / (np.abs(buf).max() + 1e-9)
        SFX.write_wav(RUN / name, buf)
        print("효과음 묶음", name, len(ks), "칸")


def out():
    shutil.copy2(X.WORK / "r4c.mov", X.WORK / "r4t.mov")   # r4t_build.out 이 WORK/r4t.mov 를 연출층으로 씀
    (X.DELIV / "media").mkdir(parents=True, exist_ok=True)
    T.out()
    import rule_check as RC
    lens = [TT[SPLIT] - TT[0] + .5, FULL - TT[SPLIT] + .5, .8]   # 묶음 파일은 칸 시각만큼 길다
    items = RC.check_sfx([(t, n, ln) for (t, n, *_), ln in zip(X.SFX_LIST, lens)], X.END)
    if RC.report(items, path=X.WORK / "점검_효과음.txt", title="r4c"):
        raise SystemExit("효과음 규칙 ERROR — 점검_효과음.txt")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    X.WORK.mkdir(parents=True, exist_ok=True)
    cmd = sys.argv[1]
    if cmd == "base":
        X.base()
        n = len(X.CUTS)
        ins = sum([["-i", str(X.WORK / f"V1_{k + 1}.mov")] for k in range(n)], [])
        fc = "".join(f"[{k}:v][{k}:a]" for k in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
        subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "prores_ks", "-profile:v", "1",
                        "-c:a", "pcm_s16le", str(X.WORK / "base_full.mov")], check=True)
    else:
        {"caps": X.caption_layer, "sfx": make_runs, "out": out}[cmd]()
