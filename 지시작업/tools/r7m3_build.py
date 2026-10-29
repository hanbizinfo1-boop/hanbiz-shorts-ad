# -*- coding: utf-8 -*-
r"""7번 3.971~7.124 상담 모자이크 V3 — 상담 사진 한 장을 크게 보여 준 뒤 띠 연출로 전환 (10-21).

사장님(10-21): «약간 사진 하나가 상담하는걸 보여주는거처럼 커진상태로 시작하면서 지금 연출로 전환하는건 어떻게돼? V3로만들어볼래?»
  «이 사진속 내용이 상담이라는걸 뚜렷하게 보여주고싶어»
  → 서류를 펼치고 마주 앉은 cs_0_13 을 선명하게 키워(소재/r4s5/hd_cs_0_13.jpg, Lanczos 3배+언샤프) 폭 860 으로 자막 위에.
장면 scenes/r7m5.html(칸 자리 r7m3_cells.js 그대로). 효과음·미리보기·XML 은 r7m_build 그대로(V4 · A4~ · 3.971).

    python tools/html_motion.py 지시작업/tools/scenes/r7m5.html --alpha --fps 59.94 --workers 2 --sub 4 --settle --out 지시작업/_tmp/r7m3 --name r7m
    python 지시작업/tools/r7m3_build.py out
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r7m_build as M  # noqa: E402

M.WORK = M.DZ / "_tmp/r7m3"
M.DELIV = M.DZ / "납품/7번_상담모자이크_강남빌딩_v3_1021"
M.NAME = "7번_상담모자이크_강남빌딩_v3"
M.CAP_TOP = True
# 10-21 사장님 «효과음이 끊기는 느낌이 너무 많이들어» → 겹침 0 을 지키며 꼬리가 다 들리게 시각을 맞춤(앞 소리의 들리는 끝 ≤ 다음 소리 시작).
#   휙1 들림 0.49 · 高速移動 1.21 · キラッ 0.92 — キラッ 꼬리가 6.97 까지라 6.50 맑은소리는 뺌(번쩍 여운이 금빛 띠를 덮음)
M.SFX_LIST = [
    # 10-21 사장님 «처음에 훅 휙 이 어울ㄹ지않아» → 사진이니 카메라 셔터 · 종이(사진)가 미끄러지는 소리로
    (3.98, "SEL_カメラのシャッター1.mp3", None),  # 상담 사진 크게 — 찰칵(0.28초 → 4.26)
    (4.38, "ML_Paper slide.wav", None),        # 1단 물러남 4.40 — 사진이 미끄러짐(0.42초 → 4.80)
    (4.83, "SEL_高速移動.mp3", None),          # 2단 줌아웃 4.85 · 띠 빨라짐 → 맞물림(→ 6.04)
    (6.05, "SEL_キラッ1.mp3", None),           # 실제 건물로 번쩍 · 여운이 6.50 금빛 띠까지(→ 6.97)
]

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    M.WORK.mkdir(parents=True, exist_ok=True)
    {"out": M.out}[sys.argv[1]]()
