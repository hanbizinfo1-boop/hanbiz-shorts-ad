# -*- coding: utf-8 -*-
r"""4번 29.446~36.086 집주인 실사판 — 건물 교체판(리모델링 후) (10-20).

사장님(10-20): «이 세장면 이 건물로 바꿔달래» · «모두 이건물이아니라 리모델링 전 건물이야 우리가쓴게» · «pro 12.25 크레딧 발주 승인»
시작프레임 = 소재/codex/r4r_uh_start_916.png(Codex set16, r4r_start_A 구도) · Kling 3.0 pro 7초 job ecbeb51a-ad25-4bdb-90e1-4ae968446290.
자르기·효과음·XML 은 r4r_build 그대로.

    python 지시작업/tools/r4r_uh_build.py clip <받은 mp4>
    python 지시작업/tools/r4r_uh_build.py out
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r4r_build as R  # noqa: E402
X = R.X

X.DELIV = X.DZ / "납품/4번_집주인_임차인_월세_실사_건물교체_1020"
X.NAME = "4번_집주인_임차인_월세_실사_건물교체"
R.CLIP = X.WORK / "r4r_uh.mov"

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    {"clip": lambda: R.clip(sys.argv[2]), "out": R.out}[sys.argv[1]]()
