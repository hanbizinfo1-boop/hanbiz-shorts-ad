# -*- coding: utf-8 -*-
r"""4번 15.649~18.835 «그래서 결국 / 돈 있는 분들이 찾는게 / 강남빌딩이에요» — v5 상담 사진 두 줄 필름 (10-21).

클라이언트(사장님 전달): «강의 사진보다 상담사진이 좋을거같네요 · 돈 있는 분들이 찾는 내용이라서요 · 상담 수백명 온거 홈피에 있는거요»
사장님: «D:년 10월±021 여기있는 사진들로 구성해서 교체해야해 / 그대로 교체하는게좋을까? 아니면 좀 잘 보이게 자막밑에 넣는 방법이 있을까?» → «추천대로가자»(② 두 줄 필름).
장면 scenes/r4s_v5.html · 소재 tools/r4s5_assets.py · 건물은 건물교체판과 같음. 바탕·자막 층·효과음은 v4 그대로.

    python tools/html_motion.py 지시작업/tools/scenes/r4s_v5.html --alpha --fps 59.94 --workers 2 --sub 4 --out 지시작업/_tmp/r4s_v5 --name r4s_v4
    python 지시작업/tools/r4s_v5_build.py out
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r4s_v4_build as B  # noqa: E402
X = B.X

OLD = X.WORK
X.WORK = X.DZ / "_tmp/r4s_v5"
X.DELIV = X.DZ / "납품/4번_상담사진_강남빌딩_v5_1021"
X.NAME = "4번_상담사진_강남빌딩_v5"

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    X.WORK.mkdir(parents=True, exist_ok=True)
    for f in ("base_full.mov",):
        if not (X.WORK / f).exists():
            shutil.copy2(OLD / f, X.WORK / f)
    if not (X.WORK / "cap").exists():
        shutil.copytree(OLD / "cap", X.WORK / "cap")
    (X.DELIV / "media").mkdir(parents=True, exist_ok=True)
    B.out()
