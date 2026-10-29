# -*- coding: utf-8 -*-
r"""4번_건물만사면_돈다발 — 건물 교체판(리모델링 후) (10-20).

사장님(10-20): «이 세장면 이 건물로 바꿔달래» · «모두 이건물이아니라 리모델링 전 건물이야 우리가쓴게» · «자세히보면 조금 달라» · «XML 만들어줘 내가 넣을게»
bldcut_1(리모델링 전) → 소재/r4s/bldcut_uh.png(리모델링 후 — 받은 사진을 Codex set16 으로 글자·로고 없이 다시 그림 → 초록 키). 장면 scenes/r4m_uh.html.
바탕·자막 층은 원래 판(_tmp/r4m) 것을 복사해 쓴다. 타이밍·효과음은 원래 판 그대로.

    python tools/html_motion.py 지시작업/tools/scenes/r4m_uh.html --alpha --fps 59.94 --workers 2 --sub 4 --out 지시작업/_tmp/r4m_uh --name r4m
    python 지시작업/tools/r4m_uh_build.py out
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r4m_build as B  # noqa: E402
X = B.X

OLD = X.WORK
X.WORK = X.DZ / "_tmp/r4m_uh"
X.DELIV = X.DZ / "납품/4번_건물만사면_돈다발_건물교체_1020"
X.NAME = "4번_건물만사면_돈다발_건물교체"

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
