"""퓨레바 설계표 연출 — 디자인 시안 5안 (10-26 사장님 «연출은 별로임 디자인시안 5개정도 내가 고를 수 있게 뽑아봐»).

python 지시작업/tools/pv_gfx_sian.py base      # 사장님 V1 컷을 모션값대로 재현한 바탕 4장(격자 포함 확인용)
python 지시작업/tools/pv_gfx_sian.py           # 5안 × 4장면 → 납품/퓨레바_육아_XML_1026/연출시안/
장면 = 44가지(23.8) · 야에야마(27.6) · 엽록소 1.5배(32.3) · 클로렐라 100%(35.0) — 사장님 자막(y≈990~1140) 줄은 비움.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pv_xml_build as P  # noqa: E402  (글꼴·컷 재현 함수 공유 — 같은 건의 짝 도구)

W, H = P.W, P.H
OUT = P.OUT / "연출시안"
TMP = P.TMP / "sian"
SCENES = [("44가지", 23.8), ("야에야마", 27.6), ("1.5배", 32.3), ("100%", 35.0)]
CREAM, LIME, GREEN, INK = (246, 241, 230), (190, 228, 110), (16, 52, 32), (22, 44, 30)
F = P.font


def base(t):
    import json
    seq = json.loads(P.SEQ.read_text(encoding="utf-8"))
    it = next(i for i in seq["items"] if i["track"] == "V1" and i["t0"] <= t < i["t1"])
    p = P.src_path(it["name"])
    ss = it.get("s0", 0) + (t - it["t0"])
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ss}", "-i", str(p), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True).stdout
    w, h = (1728, 3072) if "DJI" in it["name"] else (1080, 1916)
    src = Image.frombytes("RGB", (w, h), raw)
    mo = next((x["params"] for x in it.get("fx", []) if x["name"] == "모션"), {})
    lt = t - it["t0"]
    sc = float(P.kf(mo.get("비율 조정", "100"), lt)) / 100
    rot = float(P.kf(mo.get("회전", "0"), lt))
    px, py = map(float, str(P.kf(mo.get("위치", "0.5:0.5"), lt)).split(":"))
    im = src.resize((round(w * sc), round(h * sc)), Image.LANCZOS)
    if rot:
        im = im.rotate(-rot, expand=True)
    c = Image.new("RGB", (W, H))
    c.paste(im, (round(px * W - im.width / 2), round(py * H - im.height / 2)))
    return c


def sub_zone(im):
    """사장님 자막 자리 표시(시안에만 — 겹침 확인용)."""
    d = ImageDraw.Draw(im)
    d.rectangle([60, 1000, W - 60, 1130], outline=(255, 80, 80), width=2)
    d.text((70, 1005), "사장님 자막 자리", font=F("Medium", 22), fill=(255, 120, 120))


def shadow_text(L, xy, s, f, fill, anchor="la", blur=8, alpha=120, spacing=0):
    sh = Image.new("RGBA", L.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0] + 2, xy[1] + 3), s, font=f, fill=(0, 0, 0, alpha), anchor=anchor)
    L.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(L).text(xy, s, font=f, fill=fill, anchor=anchor)


# ───────── A 매거진 타이포 — 상자 없이 Bodoni 큰 숫자 + 헤어라인 + 작은 캡션 (이현이 화보와 같은 말투)
def A(scene, bg):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    if scene == "44가지":
        shadow_text(L, (W / 2, 70), "NUTRIENTS IN ONE STICK", F("bod_r", 30), INK + (255,), "ma", alpha=0)   # 밝은 하늘 — 진한 글자 · 상자(y≈480) 위
        shadow_text(L, (W / 2, 100), "44", F("bod_b", 250), INK + (255,), "ma", alpha=0)
        d.line([(300, 382), (600, 382)], fill=INK + (230,), width=2)
        shadow_text(L, (W / 2, 396), "한 포에 담긴 영양성분", F("Medium", 36), INK + (255,), "ma", alpha=0)
    elif scene == "야에야마":
        shadow_text(L, (W / 2, 130), "ISHIGAKI  ·  YAEYAMA", F("bod_b", 74), CREAM + (255,), "ma", blur=12)
        d.line([(250, 240), (650, 240)], fill=CREAM + (230,), width=2)
        shadow_text(L, (W / 2, 262), "일본 야에야마 · 햇빛 아래 야외 배양", F("Medium", 36), CREAM + (255,), "ma")
    elif scene == "1.5배":
        shadow_text(L, (W / 2, 96), "CHLOROPHYLL", F("bod_r", 32), INK + (255,), "ma", alpha=0)
        shadow_text(L, (W / 2, 136), "×1.5", F("bod_b", 240), INK + (255,), "ma", alpha=0)
        d.line([(250, 420), (650, 420)], fill=INK + (230,), width=2)
        shadow_text(L, (W / 2, 438), "야외 3,260mg  vs  실내 2,180mg  (100g당)", F("Medium", 32), INK + (255,), "ma", alpha=0)
    else:
        shadow_text(L, (W / 2, 40), "100%", F("bod_b", 200), CREAM + (255,), "ma", blur=14)
        shadow_text(L, (W / 2, 270), "PURE CHLORELLA  ·  NO ADDITIVES", F("bod_r", 30), CREAM + (255,), "ma")
    return L


# ───────── B 프로스트 글래스 — 뒤 화면을 흐리게 비친 유리판 + 1px 테두리 + 가벼운/굵은 글 대비
def glass(bg, box, r=28):
    x0, y0, x1, y1 = box
    g = bg.crop(box).filter(ImageFilter.GaussianBlur(26)).convert("RGBA")
    g.alpha_composite(Image.new("RGBA", g.size, (8, 24, 14, 120)))          # 어두운 유리 — 밝은 하늘 위에서도 흰 글자가 읽히게
    m = Image.new("L", g.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, g.width - 1, g.height - 1], r, fill=255)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    L.paste(g, (x0, y0), m)
    ImageDraw.Draw(L).rounded_rectangle(box, r, outline=(255, 255, 255, 150), width=2)
    return L


def B(scene, bg):
    if scene == "44가지":
        L = glass(bg, (190, 130, 710, 520))
        d = ImageDraw.Draw(L)
        d.text((W / 2, 168), "한 포에 담긴 영양성분", font=F("Light", 36), fill=(255, 255, 255), anchor="ma")
        d.text((W / 2, 220), "44", font=F("ExtraBold", 210), fill=(255, 255, 255), anchor="ma")
        d.text((W / 2, 452), "가지", font=F("Light", 40), fill=(255, 255, 255), anchor="ma")
    elif scene == "야에야마":
        L = glass(bg, (200, 120, 700, 300))
        d = ImageDraw.Draw(L)
        d.text((W / 2, 150), "ISHIGAKI, JAPAN", font=F("Light", 30), fill=(255, 255, 255), anchor="ma")
        d.text((W / 2, 194), "일본 야에야마", font=F("Bold", 66), fill=(255, 255, 255), anchor="ma")
    elif scene == "1.5배":
        L = glass(bg, (120, 90, 780, 470))
        d = ImageDraw.Draw(L)
        d.text((160, 124), "엽록소 함량 · 100g당", font=F("Light", 30), fill=(255, 255, 255))
        for k, (lab, v, col) in enumerate([("실내 배양", 2180, (220, 220, 220)), ("야외 배양", 3260, LIME)]):
            y = 190 + k * 110
            d.text((160, y), lab, font=F("Light", 30), fill=(255, 255, 255))
            d.rounded_rectangle([320, y + 4, 320 + 300 * v / 3260, y + 40], 18, fill=col + (255,))
            d.text((330 + 300 * v / 3260, y + 2), f"{v:,}", font=F("Bold", 30), fill=(255, 255, 255))
        d.text((W / 2, 418), "1.5배", font=F("ExtraBold", 40), fill=LIME, anchor="mm")
    else:
        L = glass(bg, (230, 110, 670, 280))
        d = ImageDraw.Draw(L)
        d.text((W / 2, 138), "원재료", font=F("Light", 30), fill=(255, 255, 255), anchor="ma")
        d.text((W / 2, 178), "클로렐라 100%", font=F("Bold", 64), fill=(255, 255, 255), anchor="ma")
    return L


# ───────── C 패키지 라벨 — 제품 상자 말투(딥그린 + 라임 · 굵은 대문자 · 얇은 테두리 표기 칸)
def label(L, box, lines):
    d = ImageDraw.Draw(L)
    d.rectangle(box, fill=GREEN + (255,))
    x0, y0, x1, y1 = box
    d.rectangle([x0 + 10, y0 + 10, x1 - 10, y1 - 10], outline=LIME + (255,), width=2)
    for (xy, s, f, col, an) in lines:
        d.text(xy, s, font=f, fill=col, anchor=an)


def C(scene, bg):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if scene == "44가지":
        label(L, (210, 140, 690, 500), [((W / 2, 176), "PURE CHLORELLA 100", F("Black", 34), LIME, "ma"),
                                        ((W / 2, 220), "44", F("Black", 200), LIME, "ma"),
                                        ((W / 2, 436), "영양성분 44종", F("Bold", 40), CREAM, "ma")])
    elif scene == "야에야마":
        label(L, (190, 130, 710, 310), [((W / 2, 160), "ORIGIN", F("Black", 30), LIME, "ma"),
                                        ((W / 2, 204), "일본 야에야마산", F("Black", 62), CREAM, "ma")])
    elif scene == "1.5배":
        label(L, (130, 90, 770, 450), [((170, 126), "CHLOROPHYLL / 100g", F("Black", 30), LIME, "la")])
        d = ImageDraw.Draw(L)
        for k, (lab, v, col) in enumerate([("실내", 2180, (130, 150, 135)), ("야외", 3260, LIME)]):
            y = 196 + k * 100
            d.text((170, y + 4), lab, font=F("Black", 40), fill=CREAM)
            d.rectangle([280, y, 280 + 280 * v / 3260, y + 52], fill=col + (255,))
        d.text((690, 290), "×1.5", font=F("Black", 66), fill=LIME, anchor="mm")
    else:
        label(L, (230, 110, 670, 300), [((W / 2, 140), "INGREDIENT", F("Black", 30), LIME, "ma"),
                                        ((W / 2, 184), "클로렐라 100%", F("Black", 62), CREAM, "ma")])
    return L


# ───────── D 에디토리얼 주석 — 화면 속 대상에 가는 선 + 점 + 작은 글(대상이 주인공, 글은 받쳐 줌)
def note(L, dot, elbow, end, title, sub, col=CREAM, right=True):
    d = ImageDraw.Draw(L)
    sh = Image.new("RGBA", L.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    for dd, c, w in ((ds, (0, 0, 0, 110), 5), (d, col + (255,), 2)):
        dd.line([dot, elbow, end], fill=c, width=w)
        dd.ellipse([dot[0] - 9, dot[1] - 9, dot[0] + 9, dot[1] + 9], outline=c, width=w)
    L.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)), (0, 0))
    an = "ls" if right else "rs"
    shadow_text(L, (end[0] + (12 if right else -12), end[1] - 14), title, F("bod_b", 90), col + (255,), an, blur=8)
    shadow_text(L, (end[0] + (12 if right else -12), end[1] + 30), sub, F("Medium", 30), col + (255,), an, blur=6)


def D(scene, bg):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if scene == "44가지":
        note(L, (262, 600), (262, 420), (330, 420), "44", "한 포 속 영양성분", col=INK)          # 스틱 위 끝 · 밝은 하늘이라 진한 선
    elif scene == "야에야마":
        note(L, (530, 850), (530, 360), (480, 360), "Yaeyama", "일본 야에야마 · 야외 배양지", right=False)   # 배양지 하나 · 글은 왼쪽으로
    elif scene == "1.5배":
        d = ImageDraw.Draw(L)
        x = 760
        x = 820                                                   # 플라스크(x≤690) 오른쪽 하늘 — 진한 눈금
        d.line([(x, 260), (x, 900)], fill=INK + (230,), width=2)
        for k in range(9):
            y = 900 - k * 80
            d.line([(x - 14, y), (x, y)], fill=INK + (230,), width=2)
        d.line([(x - 40, 900 - 427), (x + 6, 900 - 427)], fill=(110, 118, 112, 255), width=5)
        d.line([(x - 40, 900 - 640), (x + 6, 900 - 640)], fill=GREEN + (255,), width=7)
        shadow_text(L, (x - 54, 900 - 427), "실내 2,180", F("Medium", 28), (60, 66, 62, 255), "rm", alpha=0)
        shadow_text(L, (x - 54, 900 - 640), "야외 3,260", F("Bold", 30), GREEN + (255,), "rm", alpha=0)
        shadow_text(L, (x - 54, 900 - 760), "×1.5", F("bod_b", 96), GREEN + (255,), "rm", alpha=0)
        shadow_text(L, (x - 54, 940), "엽록소 · 100g당 mg", F("Medium", 24), INK + (255,), "rm", alpha=0)
    else:
        d = ImageDraw.Draw(L)
        bx = (280, 848, 600, 902)            # 상자 앞면 «클로렐라분말 100%» 줄
        for (a, b) in [((bx[0], bx[1]), (bx[0] + 30, bx[1])), ((bx[0], bx[1]), (bx[0], bx[1] + 30)),
                       ((bx[2], bx[3]), (bx[2] - 30, bx[3])), ((bx[2], bx[3]), (bx[2], bx[3] - 30))]:
            d.line([a, b], fill=LIME + (255,), width=5)
        note(L, (440, 846), (440, 560), (490, 560), "100%", "원재료 · 클로렐라만", col=CREAM)
    return L


# ───────── E 시네마틱 와이드 — 화면 위쪽을 가로지르는 얇은 큰 숫자 + 넓은 자간 캡션(박스 없음, 어두운 그라데이션 막)
def E(scene, bg):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gr = Image.new("L", (1, 560))
    for y in range(560):
        gr.putpixel((0, y), int(150 * (1 - y / 560) ** 1.6))
    L.paste((0, 0, 0, 255), (0, 0), gr.resize((W, 560)))
    d = ImageDraw.Draw(L)

    def spaced(y, s, f, col):
        tw = sum(d.textlength(c, font=f) for c in s) + 10 * (len(s) - 1)
        x = (W - tw) / 2
        for c in s:
            d.text((x, y), c, font=f, fill=col)
            x += d.textlength(c, font=f) + 10
    if scene == "44가지":
        d.text((W / 2, 80), "44", font=F("ExtraLight", 300), fill=(255, 255, 255), anchor="ma")
        spaced(420, "NUTRIENTS", F("Light", 30), (255, 255, 255, 230))
        d.text((W / 2, 470), "한 포에 담긴 영양성분", font=F("Regular", 34), fill=(255, 255, 255), anchor="ma")
    elif scene == "야에야마":
        spaced(120, "YAEYAMA", F("ExtraLight", 100), (255, 255, 255, 255))
        d.text((W / 2, 260), "일본 야에야마  |  ISHIGAKI, OKINAWA", font=F("Regular", 30), fill=(255, 255, 255), anchor="ma")
    elif scene == "1.5배":
        d.text((W / 2, 70), "1.5×", font=F("ExtraLight", 260), fill=LIME, anchor="ma")
        spaced(380, "CHLOROPHYLL", F("Light", 28), (255, 255, 255, 230))
        d.text((W / 2, 426), "엽록소 · 야외 3,260 / 실내 2,180mg (100g당)", font=F("Regular", 28), fill=(255, 255, 255), anchor="ma")
    else:
        d.text((W / 2, 30), "100%", font=F("ExtraLight", 210), fill=(255, 255, 255), anchor="ma")
        spaced(270, "PURE CHLORELLA", F("Light", 30), (255, 255, 255, 230))
        d.text((W / 2, 318), "첨가물 없이 클로렐라만", font=F("Regular", 34), fill=(255, 255, 255), anchor="ma")
    return L


STYLES = [("A_매거진타이포", "상자 없이 Bodoni 큰 숫자 + 얇은 선 + 작은 영문 캡션 — 이현이 화보와 같은 말투", A),
          ("B_프로스트글래스", "뒤 화면이 흐리게 비치는 유리판 + 가는 테두리 — 깨끗한 웰니스 톤", B),
          ("C_패키지라벨", "제품 상자 디자인 말투(딥그린 + 라임 · 굵은 대문자 · 표기 칸 테두리)", C),
          ("D_에디토리얼주석", "화면 속 대상(스틱·배양지·플라스크·표시사항)을 가는 선으로 짚는 주석", D),
          ("E_시네마틱와이드", "위쪽 어두운 막 + 아주 가는 큰 숫자 + 넓은 자간 — 영화 타이틀 톤", E)]


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    bases = {n: base(t) for n, t in SCENES}
    if sys.argv[1:] == ["base"]:
        for n, im in bases.items():
            g = im.copy()
            d = ImageDraw.Draw(g)
            for y in range(0, H, 100):
                d.line([(0, y), (W, y)], fill=(255, 0, 0), width=1)
                d.text((4, y), str(y), fill=(255, 0, 0))
            for x in range(0, W, 100):
                d.line([(x, 0), (x, H)], fill=(0, 120, 255), width=1)
                d.text((x + 2, 4), str(x), fill=(0, 120, 255))
            g.resize((450, 800)).save(TMP / f"base_{n}.jpg")
        return
    thumbs = []
    for code, desc, fn in STYLES:
        row = []
        for n, _ in SCENES:
            im = bases[n].convert("RGBA")
            im.alpha_composite(fn(n, bases[n]))
            im = im.convert("RGB")
            sub_zone(im)
            row.append(im)
        sheet = Image.new("RGB", (W * 4 + 60, H + 170), (250, 248, 243))
        d = ImageDraw.Draw(sheet)
        d.text((24, 30), f"시안 {code.replace('_', '  ')}", font=F("Bold", 56), fill=INK)
        d.text((24, 104), desc, font=F("Medium", 34), fill=(90, 96, 92))
        for i, im in enumerate(row):
            sheet.paste(im, (20 + i * (W + 10), 160))
        sheet.save(OUT / f"시안_{code}.jpg", quality=90)
        thumbs.append(sheet.resize((sheet.width // 3, sheet.height // 3)))
    allp = Image.new("RGB", (thumbs[0].width, sum(t.height for t in thumbs)), "white")
    y = 0
    for t in thumbs:
        allp.paste(t, (0, y))
        y += t.height
    allp.save(OUT / "시안_한눈에.jpg", quality=88)
    print(OUT)


if __name__ == "__main__":
    main()
