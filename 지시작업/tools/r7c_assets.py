# -*- coding: utf-8 -*-
r"""7번 28.145~29.997 «실제 사례로 알려드리겠습니다» — 인터넷 자료 → 카페 → 책이 물방울처럼 들어가며 성공사례가 쏟아짐: 소재 정리 (10-21).

사장님: «그다음 실제 사례로 알려드리겠습니다 까지 이어서 전환효과 부드럽게 연출 효과붙여서 넣어주면 좋을듯 / 이 부분은 인터넷상 수많은 자료중에 하나를 클릭했더니
  [카페 화면] 이 카페가 나오고 이 카페 속으로 새폴더의 책5 가 속 들어가면서(지면에 물방울 들어갈때 이는 출렁임연출) 성공사례들이 쏟아져나오는 연출로»
  카페 화면: «이름·로고 그대로 다시 그림»(사장님 선택) — 배너·카드 그림은 사장님이 보낸 카페 화면 캡처에서 잘라 쓰고 나머지 틀은 장면에서 새로 그림.
원본(읽기만): 카페 캡처 = 대화 첨부(…\images\34.png) · 사진 = Downloads\연금형부동산연구소\새 폴더(번호 = _tmp/r7p/list.json)
→ 지시작업/소재/r7c/{cafe_banner, cafe_ad, cafe_step1, cafe_step2, cafe_step4}.jpg · m00~.jpg(자료 칸) · s00~.jpg(성공사례 카드) · book5.png · last.jpg(앞 장면 마지막 프레임)

    python 지시작업/tools/r7c_assets.py
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageOps

HERE = Path(__file__).resolve().parent
DZ = HERE.parent
OUT = DZ / "소재/r7c"
SHOT = Path(r"C:\Users\user\AppData\Local\Temp\claude\C--Users-user-Desktop---------\29f039ed-13d4-43b9-ad9d-8d23c8d1b5b8\images\34.png")
SRC = Path(r"C:\Users\user\Downloads\연금형부동산연구소\새 폴더")
CROPS = {"cafe_banner": (548, 113, 1358, 368), "cafe_ad": (728, 436, 1349, 593), "cafe_step1": (1042, 621, 1349, 853),
         "cafe_step2": (728, 860, 1036, 1032), "cafe_step4": (1042, 860, 1349, 1032)}
MAT = [243, 259, 266, 232, 271, 244, 285, 203, 267, 245, 261, 235, 286, 229, 248, 268, 233, 272, 250, 287, 206, 236, 251, 269, 283, 252, 288, 239]
CASE = [243, 244, 245, 247, 249, 251, 253, 254, 255, 256, 257, 258]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    shot = Image.open(SHOT).convert("RGB")
    # 10-21 «저거 카페홍보겸해서하는거니까 제대로 따라해줘» → 카페 본문(탭 줄 뺀 가운데 칸)을 그대로 — 900 폭
    pg = shot.crop((538, 88, 1368, 1032))
    pg.resize((900, round(pg.height * 900 / pg.width)), Image.LANCZOS).save(OUT / "cafe_page.jpg", quality=95)
    for k, b in CROPS.items():
        shot.crop(b).save(OUT / f"{k}.jpg", quality=93)
    names = json.loads((DZ / "_tmp/r7p/list.json").read_text(encoding="utf-8"))
    for g, ids in (("m", MAT), ("s", CASE)):
        for k, i in enumerate(ids):
            im = ImageOps.exif_transpose(Image.open(SRC / names[i])).convert("RGB")
            im.thumbnail((700, 700), Image.LANCZOS)
            im.save(OUT / f"{g}{k:02d}.jpg", quality=90)
    b = Image.open(SRC / "책5.jpg").convert("RGB")
    b.thumbnail((700, 1000), Image.LANCZOS)
    b.save(OUT / "book5.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.05", "-i", str(DZ / "납품/7번_홀로그램_빌딩분석_1021/media/전체화면_홀로그램_빌딩분석.mov"),
                    "-frames:v", "1", "-q:v", "2", str(OUT / "last.jpg")], check=True)
    print("ok", len(MAT), len(CASE))


if __name__ == "__main__" and len(sys.argv) == 1:
    sys.stdout.reconfigure(encoding="utf-8")
    main()


# 10-21 B안(«1. b안 2. 빼자 3 실제사례위주로만 폴더에있는») — 후기 카드 4장: 위쪽(제목·작성자·첫 줄)만 · 작성자 이름·프로필 사진 가림(개인정보)
CARDS = ["s02", "s09", "s05", "s00"]
MASK = [(14, 74, 330, 124), (14, 58, 330, 110), (14, 86, 340, 136), (14, 74, 330, 124)]   # 카드마다 작성자 줄(제목은 안 덮게)


def cards():
    from PIL import ImageDraw, ImageFilter
    for k, n in enumerate(CARDS):
        # 10-21 «상담후기 본문이 블러처리 안됐으면 좋겠어» → 700 폭 축소본 대신 원본에서 바로(글씨 선명)
        names = json.loads((DZ / "_tmp/r7p/list.json").read_text(encoding="utf-8"))
        im = ImageOps.exif_transpose(Image.open(SRC / names[CASE[int(n[1:])]])).convert("RGB")
        im = im.resize((820, round(im.height * 820 / im.width)), Image.LANCZOS)
        im = im.crop((0, 0, 820, min(im.height, 520)))
        box = MASK[k]                                               # 프로필 사진 · 이름 · 날짜 줄
        im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(14)), box[:2])
        d = ImageDraw.Draw(im)
        d.rounded_rectangle(box, 10, fill=(232, 236, 240))
        d.text((box[0] + 16, box[1] + 12), "회원 후기", fill=(110, 118, 128), font=__import__("PIL.ImageFont", fromlist=["x"]).truetype("C:/Windows/Fonts/malgunbd.ttf", 26))
        im.save(OUT / f"card{k}.jpg", quality=93)
    print("cards", len(CARDS))


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "cards":
    cards()


# 10-21 «이거만 보이잖아 아니 내용이 보이게끔 뭔가 후기쓴게 내용이 초반 3줄이라도 좀 보이게해줘» → 카드 = 캡처 제목 줄만(작성자 줄 전) + 본문은 장면에서 큰 글씨로(그 글의 실제 문장 그대로)
HEAD = [68, 56, 84, 70]                                            # card0~3 에서 제목 줄 끝(작성자 줄 위)


def heads():
    for k, h in enumerate(HEAD):
        Image.open(OUT / f"card{k}.jpg").crop((0, 0, 820, h)).save(OUT / f"head{k}.jpg", quality=95)
    print("heads", len(HEAD))


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "heads":
    heads()
