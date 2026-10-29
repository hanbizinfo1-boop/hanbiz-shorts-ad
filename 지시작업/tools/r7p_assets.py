# -*- coding: utf-8 -*-
r"""7번 19.136~23.774 «저는 지난 18년간 강남빌딩을 45채 사보고 36채를 지어봤습니다» — 사진 고르기·정리 (10-21).

원본(읽기만) = C:\Users\user\Downloads\연금형부동산연구소\새 폴더 (305장, 사장님 «새폴더에 있어근데 구분 안해놨는데 네가 구분할수있어?»)
번호 = 파일 이름 정렬 순(지시작업/_tmp/r7p/list.json · sheet_*.jpg). 다른 사람 얼굴이 정면으로 크게 나온 컷(94·151·87)은 뺌.
  빌드업(자막 밑 덱): 91 117 133 144 168 172 + 맨 위 d6 = 리모델링 후 건물(소재/codex/r7m_night.png — 10-21 사장님 «얘 말고 다른 건물써달라고 4번영상에서 요청받은거 기억하지 그건물로바꿔줘», 237 은 리모델링 전 건물이라 안 씀)
  45채(건물 사진 — 10-21 «여기서 산 느낌을 주는건 첫번째 사진밖에없는데.. 건물사진으로 바꾸던지 …» → «a안고고»): 232(«22차» 잘라 냄) 236 239 233(«24차» 잘라 냄) · 238 은 리모델링 후 건물과 닮아 뺌 · (앞 판 임장 97 109 155 171 189 119 은 안 씀)
  36채(공사현장 → 완성): 296(터파기) 123(흙막이) 75(거푸집) 147(비계) 163(골조) 302(눈 온 현장) → 234(완성, 오른쪽 아래 «26차» 글씨 잘라 냄)
→ 지시작업/소재/r7p/{d0..d6, t0..t5, b0..b6}.jpg · grain.png

    python 지시작업/tools/r7p_assets.py
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

HERE = Path(__file__).resolve().parent
DZ = HERE.parent
SRC = Path(r"C:\Users\user\Downloads\연금형부동산연구소\새 폴더")
OUT = DZ / "소재/r7p"
PICK = {"d": [91, 117, 133, 144, 168, 172, "codex/r7m_night.png"], "t": [232, 236, 239, 233], "b": [296, 123, 75, 147, 163, 302, 234]}
CROP_BOTTOM = {232: .07, 233: .07, 234: .07}   # 사진 속 «22차·24차·26차» 표기


def main():
    names = json.loads((DZ / "_tmp/r7p/list.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    for g, ids in PICK.items():
        for k, i in enumerate(ids):
            im = ImageOps.exif_transpose(Image.open(DZ / "소재" / i if isinstance(i, str) else SRC / names[i])).convert("RGB")
            if i in CROP_BOTTOM:
                c = CROP_BOTTOM[i]
                im = im.crop((0, 0, im.width, round(im.height * (1 - c))))
            im.thumbnail((1600, 1600), Image.LANCZOS)
            im.save(OUT / f"{g}{k}.jpg", quality=92)
            print(f"{g}{k} ← {i} {i if isinstance(i, str) else names[i]} {im.size}")
    rng = np.random.default_rng(3)
    g = (128 + rng.normal(0, 38, (256, 256))).clip(0, 255).astype(np.uint8)
    Image.fromarray(g, "L").save(OUT / "grain.png")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
