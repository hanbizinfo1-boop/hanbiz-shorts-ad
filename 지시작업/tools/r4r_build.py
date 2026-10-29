# -*- coding: utf-8 -*-
r"""4번 29.446~36.086 집주인·임차인 구간 — 실사판(힉스필드 Kling 3.0 pro) 화면 전체 (10-20).

사장님(10-20): «이부분은 실사화하자 힉스필드사용해서 한번 내가 화면 전체에 띄울용으로 각색해서 만들어봐»
  «강남이랑 건물 위치 및 정합성 정도만 새폴더 파일 확인해서 맞춰줘» · 시작프레임 «A로 가자» · «pro 12.25 크레딧 발주 승인»
시작프레임 = 소재/codex/r4r_start_A_916.png(실제 빌딩2.jpg 기준 Codex) · job b1c1140c-04fb-48b3-98e3-4999c8ad7c3a
바탕·자막 층은 r4t 것을 그대로 쓴다(같은 구간). XML V4 · A4~.

    python 지시작업/tools/r4r_build.py clip <받은 mp4>   # 앞에서 6.64초 · 900×1600 · 59.94 · 속도 그대로
    python 지시작업/tools/r4r_build.py out
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r4t_build as T  # noqa: E402
X = T.X

X.DELIV = X.DZ / "납품/4번_집주인_임차인_월세_실사_1020"
X.NAME = "4번_집주인_임차인_월세_실사"
T.OVL_NAME = "연출층_집주인_실사.mov"
X.SFX_LIST = [   # 실사라 만화 소리는 빼고 들어올 때 하나만
    (29.46 - T.OFFSET, "8. 훅.mp3", -8, "onset", 0),
]
CLIP = X.WORK / "r4r.mov"


def clip(src):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-t", f"{X.END:.4f}", "-an",
                    "-vf", f"scale={X.W}:{X.H}:flags=lanczos,fps={X.FN}/{X.FD},format=yuv422p10le",
                    "-c:v", "prores_ks", "-profile:v", "3", str(CLIP)], check=True)
    print("연출층", CLIP)


def out():
    shutil.copy2(CLIP, X.WORK / "r4t.mov")   # r4t_build.out 이 WORK/r4t.mov 를 연출층으로 씀
    X.DELIV.mkdir(parents=True, exist_ok=True)
    (X.DELIV / "media").mkdir(exist_ok=True)
    T.out()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    {"clip": lambda: clip(sys.argv[2]), "out": out}[sys.argv[1]]()
