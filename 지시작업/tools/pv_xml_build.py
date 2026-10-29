"""퓨레바 육아 — 사장님 프리미어(퓨레바녹음.prproj 13:59 저장본) 위에 얹을 두 묶음 XML (10-26).

사장님: «이현이 이미지들이 좀 잡지매거진처럼 챱챱 나오는느낌이랑 내가 준 설계표에있는 그런 연출 그리고 좀 가볍지않고 고급스러운 효과음으로
  귀에 거슬리는 치링 이런느낌말고 좀 부드럽거 어우러지는 효과음으로 채워줘 … 이거 두개 xml로 뽑아줘 내가 조정할 수있게 · 타임라인은 지금 프리미어 클립으로 파악하고»

  1) 이현이 매거진 — V1 13.397~16.433(사장님 V1 빈자리, V3 에 임시 사진) · 화면 전체 장면이라 V1(7번 규칙)
  2) 설계표 연출 — V4 알파 MOV 4개(44가지 · 야에야마 · 엽록소 1.5배 · 클로렐라 100%)
  효과음은 둘 다 A3~ (A1 목소리 · A2 사장님 클립 소리). 종이·셔터·공기·부드러운 타격만 — 반짝·띠링·차임 금지.

    python 지시작업/tools/pv_xml_build.py            # 소재 → 렌더 → 효과음 → XML 2개 → 미리보기
시각 = 사장님 시퀀스 초(목소리 퓨레바.MP3 A1 0초 시작 = 정리 녹음 단어 시각과 같음).
"""
import json
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
DZ = HERE.parent
ROOT = DZ.parent
sys.path.insert(0, str(ROOT / "tools"))
import lec_xml  # noqa: E402
import rule_check  # noqa: E402
import sfx as SFX  # noqa: E402

W, H, FPS = 900, 1600, 60000 / 1001
SEQ = DZ / "_tmp/story/seq_pv_1359.json"
SRC = Path(r"C:\Users\user\Downloads\drive-download-20261026T014322Z-1-001")
HYUNI = DZ / "소재/pureva/이현이_공식"
VOICE = Path(r"D:\26년 10월\261026\퓨레바.MP3")      # 사장님 A1 (읽기만)
VOICE_DB = 9.0                                         # A1 레벨 0.501 = 0dB(0.17783) 대비 +9dB
OUT = DZ / "납품/퓨레바_육아_XML_1026"
TMP = DZ / "_tmp/pv_xml"
FONTD = ROOT / "소재/fonts/pretendard"
UF = Path(r"C:\Users\user\AppData\Local\Microsoft\Windows\Fonts")

PAPER, INK, GREEN, CREAM, LIME, GREY = (241, 236, 226), (22, 44, 30), (16, 52, 32), (246, 241, 230), (178, 226, 110), (150, 156, 150)


def font(name, size):
    p = {"bod_b": UF / "BOD_B.TTF", "bod_r": UF / "BOD_R.TTF", "bod_i": UF / "BOD_I.TTF", "serif_kr": UF / "NotoSerifKR-VF.ttf"}.get(name)
    if p is None:
        p = FONTD / f"Pretendard-{name}.otf"
    f = ImageFont.truetype(str(p), size)
    if name == "serif_kr":
        try:
            f.set_variation_by_name("Bold")
        except Exception:
            pass
    return f


def ease(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


# ───────────────────────── 1) 이현이 매거진 ─────────────────────────
MAG_T0, MAG_T1 = 13.397, 16.433
# 원본 crop (x0,y0,x1,y1) — 문구·행사가 피해서 사람(+상자)만. 효과문구(«피부톤», «DETOX»)는 잘라낸 영역 밖
CROPS = {
    "c06": ("인스타_06_2026-09-28_Dd2YyU5kzZk_01.jpg", (300, 0, 1900, 1250)),     # 병 마시는 얼굴 — «피부톤» 문구(y≈1370) 위만
    "c01": ("인스타_01_2026-07-23_DbJ4bn4E7ld_01.jpg", (330, 120, 1400, 1480)),   # 초록 상의 — CHLORELLA·SUPERFOOD·DETOX 글자 밖
    "c02": ("인스타_02_2026-08-11_Db4QoVGk1lr_01.jpg", (1000, 320, 2050, 1900)),  # 정장 전신 — 왼쪽 큰 글자(«끝!») 밖
    "c05": ("인스타_05_2026-09-10_DdICVGJE65v_01.jpg", (0, 330, 880, 1880)),      # 초록 셔츠 + 스틱 — 오른쪽 문구 밖
    "c07": ("인스타_07_2026-10-10_DeTy14-mlnA_01.jpg", (300, 760, 1500, 2350)),   # 초록 블라우스 — 위 문구(«최애 건강관리템» 아래 끝 y≈700)·아래 문구 밖
    "c03": ("인스타_03_2026-08-21_DcTFW1mGuWl_01.jpg", (0, 1800, 830, 2520)),     # 행사 글자(«67%» 아래 끝 y≈1760) 아래 인물만
    "d1": ("상세페이지_d1_하루1포.jpg", (0, 150, 215, 470)),                       # 턱 괸 얼굴 — 오른쪽 문구·가격 밖
    "d2": ("상세페이지_d2_그린루틴.jpg", (0, 0, 452, 515)),                        # 정장 + 상자 — 오른쪽 문구 밖
    "d3": ("../상세페이지/d3.jpg", (60, 620, 620, 1250)),                          # 초록 상의 전신
    "s05": ("../상세페이지/s05.jpg", (150, 1330, 848, 1800)),                      # 스틱 든 미소 — 위 문구 밖
    "cover": ("인스타_04_2026-08-28_DckOnTUGiSC_01.jpg", (150, 0, 1450, 1680)),  # 상자 든 모습 — «2박스+1박스»·아래 문구 밖
}
# 10-26 «사진 4장이 꽉채워진 느낌이 아니라 좀더 사진들이 다양하게 많이 들어갔으면» — 10장 무드보드, 크기·기울기 제각각, 0.13초 간격으로 착착.
#   놓인 장은 사라지지 않고 남아 쌓임(7번 «넘긴 장은 작은 카드로 보관»). (키, 시각, 가운데 x, 위 y, 폭, 기울기°)
# 10-26 «사진 6개만 넣자 지금 너무 렉걸린다 렌더해도 6개정도만 좀 크게해서 꽉차보이게» — 원본이 큰 6장만(d1·d2·d3 는 작은 원본이라 뺌) 크게
_T = [13.45 + 0.2 * i for i in range(6)]
TILES = [("c06", _T[0], 300, 250, 560, -2.5), ("c01", _T[1], 690, 270, 380, 3.0), ("c02", _T[2], 210, 640, 360, -2.0),
         ("s05", _T[3], 560, 720, 560, 2.0), ("c05", _T[4], 720, 1010, 330, -2.5), ("c07", _T[5], 320, 1080, 420, 2.0)]
COVER_T = 14.70


def load_crop(k):
    f, box = CROPS[k]
    return Image.open(HYUNI / f).convert("RGB").crop(box)


def paper_bg():
    rng = np.random.default_rng(7)
    g = rng.normal(0, 4.0, (H, W, 1))
    base = np.array(PAPER, float)[None, None, :] + g
    yy = np.linspace(-1, 1, H)[:, None]
    xx = np.linspace(-1, 1, W)[None, :]
    vig = 1 - 0.06 * (xx ** 2 + yy ** 2)
    return Image.fromarray(np.clip(base * vig[..., None], 0, 255).astype(np.uint8))


def framed(im, w, border=12):
    h = round(im.height * w / im.width)
    ph = im.resize((w, h), Image.LANCZOS)
    card = Image.new("RGBA", (w + 2 * border, h + 2 * border + 26), (252, 250, 245, 255))
    card.paste(ph, (border, border))
    return card


def shadowed(card, rot):
    pad = 40
    sh = Image.new("RGBA", (card.width + 2 * pad, card.height + 2 * pad), (0, 0, 0, 0))
    a = Image.new("L", card.size, 70)
    sh.paste((20, 20, 20, 255), (pad + 8, pad + 14), a)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    sh.alpha_composite(card, (pad, pad))
    return sh.rotate(rot, resample=Image.BICUBIC, expand=True)


def mag_assets():
    tiles = {k: shadowed(framed(load_crop(k), w), r) for k, _, _, _, w, r in TILES}
    cov = load_crop("cover")
    return paper_bg(), tiles, cov


def masthead(alpha=1.0, dy=0):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    a = int(255 * alpha)
    f = font("bod_b", 150)
    s = "PUREVA"
    tw = sum(d.textlength(c, font=f) for c in s) + 14 * (len(s) - 1)
    x = (W - tw) / 2
    for c in s:
        d.text((x, 54 + dy), c, font=f, fill=INK + (a,))
        x += d.textlength(c, font=f) + 14
    d.line([(70, 222 + dy), (W - 70, 222 + dy)], fill=INK + (a,), width=2)
    d.text((70, 230 + dy), "THE GREEN ROUTINE ISSUE", font=font("bod_r", 26), fill=INK + (a,))
    d.text((W - 70, 230 + dy), "NO. 10", font=font("bod_r", 26), fill=INK + (a,), anchor="ra")
    return L


def mag_frame(t, bg, tiles, cov):
    im = bg.copy().convert("RGBA")
    g = ease((t - 13.40) / (8 / FPS))
    im.alpha_composite(masthead(g, dy=-24 * (1 - g)))
    for k, t0, cx, y, w, r in TILES:
        if t < t0:
            continue
        g = ease((t - t0) / (7 / FPS))
        tl = tiles[k]
        s = 1.08 - 0.08 * g
        tt = tl.resize((round(tl.width * s), round(tl.height * s)), Image.BILINEAR)
        if g < 1:
            tt.putalpha(tt.getchannel("A").point(lambda v: int(v * g)))
        im.alpha_composite(tt, (int(cx - tt.width / 2), int(y - 40 - 30 * (1 - g))))
    if t >= COVER_T:                                     # 표지 — 오른쪽에서 페이지 넘기듯
        g = ease((t - COVER_T) / (9 / FPS))
        dim = Image.new("RGBA", (W, H), (10, 20, 14, int(110 * g)))
        im.alpha_composite(dim)
        cw, ch = 860, 1330                               # 화면을 거의 채우는 표지(10-26 «꽉차보이게»)
        # 10-26 «마지막 사진이 확대 느낌이면좋겠고» — 표지가 자리 잡은 뒤(9프레임) 얼굴 쪽으로 1.0 → 1.35 천천히 당겨 들어감
        u = min(1.0, max(0.0, (t - COVER_T - 9 / FPS) / (MAG_T1 - COVER_T - 9 / FPS)))
        k = 1.0 + 0.35 * (u * u * (3 - 2 * u))
        sc = max(cw / cov.width, ch / cov.height) * k     # 가로·세로 둘 다 덮게(세로로 긴 표지에서 위가 비지 않게)
        ph = cov.resize((round(cov.width * sc), round(cov.height * sc)), Image.LANCZOS)
        fx, fy = 0.60, 0.36                              # 얼굴 자리(표지 사진 안 가로 60% · 세로 36%)
        x0 = int(min(max(0, ph.width * fx - cw * fx), ph.width - cw))
        y0 = int(min(max(0, ph.height * fy - ch * fy), ph.height - ch))
        ph = ph.crop((x0, y0, x0 + cw, y0 + ch))
        page = Image.new("RGBA", (cw, ch))
        page.paste(ph, (0, 0))
        d = ImageDraw.Draw(page)
        # 표지 글(말 따라 쓰기 아님 — 잡지 표지 말): 표제 · 호수 · 작은 크레딧
        # 표지 안 표제는 빼고 바깥 표제를 표지 위에 그대로 둔다(«PUREVA» 두 줄 겹침 · 머리에 닿음 — 10-26 미리보기)
        sh = Image.new("RGBA", (cw, 220), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle([0, 0, cw, 220], fill=(0, 0, 0, 160))   # 확대 뒤 상자 글자가 띠로 올라와도 크레딧이 읽히게
        page.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30)), (0, ch - 200))
        if t >= 15.18:                                    # «모델인» — 크레딧 한 줄
            ga = ease((t - 15.18) / (6 / FPS))
            d.text((44, ch - 120), "COVER MODEL", font=font("bod_r", 30), fill=CREAM + (int(255 * ga),))
            d.text((44, ch - 84), "LEE HYUN-YI", font=font("bod_i", 54), fill=CREAM + (int(255 * ga),))
            d.text((cw - 44, ch - 74), "PURE CHLORELLA 100", font=font("bod_r", 28), fill=CREAM + (int(255 * ga),), anchor="ra")
        x = int(20 + (W + 40) * (1 - g))
        pad = Image.new("RGBA", (cw + 60, ch + 60), (0, 0, 0, 0))
        ImageDraw.Draw(pad).rectangle([30, 30, cw + 30, ch + 30], fill=(0, 0, 0, 120))
        pad = pad.filter(ImageFilter.GaussianBlur(18))
        im.alpha_composite(pad, (x - 30 + 10, 226 - 30 + 14))
        im.alpha_composite(page, (x, 226))
        im.alpha_composite(masthead(1.0))               # 어둡게 한 막 위로 표제를 다시 — 표지의 머리글이 된다
    return im.convert("RGB")


# ───────────────────────── 2) 설계표 연출(알파) ─────────────────────────

def card(w, h, fill=GREEN):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w - 1, h - 1], 14, fill=fill + (255,))
    return im


def g44(t, t0):
    im = card(560, 300)
    d = ImageDraw.Draw(im)
    d.text((280, 34), "한 포에 담긴 영양성분", font=font("Bold", 34), fill=CREAM, anchor="mt")
    f = font("bod_b", 170)
    w1 = d.textlength("44", font=f)
    f2 = font("Bold", 64)
    w2 = d.textlength("가지", font=f2)
    x = 280 - (w1 + 16 + w2) / 2
    d.text((x, 78), "44", font=f, fill=LIME)
    d.text((x + w1 + 16, 166), "가지", font=f2, fill=CREAM)
    return im, (W / 2, 150)


def gyae(t, t0):
    im = card(520, 150)
    d = ImageDraw.Draw(im)
    d.text((260, 26), "ISHIGAKI · YAEYAMA, JAPAN", font=font("bod_r", 26), fill=LIME, anchor="mt")
    d.text((260, 64), "일본 야에야마", font=font("Bold", 54), fill=CREAM, anchor="mt")
    return im, (W / 2, 140)


def gbar(t, t0):
    im = card(820, 330)
    d = ImageDraw.Draw(im)
    d.text((36, 26), "엽록소 함량 (100g당)", font=font("Bold", 30), fill=CREAM)
    for k, (lab, val, col, ta) in enumerate([("실내 배양", 2180, GREY, 29.36), ("야외 배양", 3260, LIME, 30.86)]):
        y = 92 + k * 90
        d.text((36, y + 10), lab, font=font("Bold", 30), fill=CREAM)
        g = ease((t - ta) / 0.55)
        if g <= 0:
            continue
        ww = 330 * val / 3260 * g
        d.rounded_rectangle([190, y, 190 + ww, y + 58], 12, fill=col + (255,))
        if g >= 1:
            d.text((202 + ww, y + 14), f"{val:,}mg", font=font("bod_r", 30), fill=col)
    if t >= 31.96:
        g = ease((t - 31.96) / (6 / FPS))
        d.text((716, 150), "1.5", font=font("bod_b", round(110 * (0.85 + 0.15 * g))), fill=LIME + (int(255 * g),), anchor="mm")
        d.text((716, 228), "배", font=font("Bold", 44), fill=CREAM + (int(255 * g),), anchor="mm")
    d.text((36, 300), "출처: 야에야마쇼쿠산 분석서(제품 상세페이지)", font=font("Medium", 20), fill=(190, 200, 194), anchor="lm")
    return im, (W / 2, 96)


def gpct(t, t0):
    im = card(420, 120, fill=GREEN)
    d = ImageDraw.Draw(im)
    d.text((210, 60), "클로렐라 100%", font=font("ExtraBold", 54), fill=LIME, anchor="mm")
    return im, (W / 2, 150)


# ── 10-26 사장님 «A로 진행» — 시안 A 매거진 타이포(상자 없음 · Bodoni 큰 숫자 · 얇은 선 · 작은 영문 캡션). 시안 `pv_gfx_sian.py` A 와 같은 자리.
#    요소마다 등장(감속 7프레임 · 아래로 살짝 내려앉음 · 튕김 없음) · 선은 가운데서 양옆으로 · 밝은 하늘 위는 진한 글자(INK), 어두운 상자 위는 크림
def _shadow_text(L, xy, s, f, fill, anchor="la", blur=8, alpha=120):
    if alpha:
        sh = Image.new("RGBA", L.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((xy[0] + 2, xy[1] + 3), s, font=f, fill=(0, 0, 0, int(alpha * fill[3] / 255)), anchor=anchor)
        L.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(L).text(xy, s, font=f, fill=fill, anchor=anchor)


def _el(L, t, ta, draw, drop=22):
    """ta 부터 7프레임 감속으로 나타나는 요소 하나(투명 층에 그려 위에서 내려앉힘)."""
    g = ease((t - ta) / (7 / FPS))
    if g <= 0:
        return
    E = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw(E, g)
    if g < 1:
        E.putalpha(E.getchannel("A").point(lambda v: int(v * g)))
        E = E.transform(E.size, Image.AFFINE, (1, 0, 0, 0, 1, drop * (1 - g)), resample=Image.BILINEAR)
    L.alpha_composite(E)


def _rule(L, t, ta, y, x0, x1, col, dur=10):
    u = ease((t - ta) / (dur / FPS))
    if u <= 0:
        return
    cx, half = (x0 + x1) / 2, (x1 - x0) / 2 * u
    ImageDraw.Draw(L).line([(cx - half, y), (cx + half, y)], fill=col, width=2)


def a44(t, t0):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    k = INK + (255,)
    _el(L, t, t0, lambda E, g: _shadow_text(E, (W / 2, 100), "44", font("bod_b", 250), k, "ma", alpha=0))
    _el(L, t, t0 + 0.10, lambda E, g: _shadow_text(E, (W / 2, 70), "NUTRIENTS IN ONE STICK", font("bod_r", 30), k, "ma", alpha=0), drop=10)
    _rule(L, t, t0 + 0.14, 382, 300, 600, INK + (230,))
    _el(L, t, t0 + 0.22, lambda E, g: _shadow_text(E, (W / 2, 396), "한 포에 담긴 영양성분", font("Medium", 36), k, "ma", alpha=0), drop=10)
    return L


def ayae(t, t0):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    c = CREAM + (255,)
    _el(L, t, t0, lambda E, g: _shadow_text(E, (W / 2, 130), "ISHIGAKI  ·  YAEYAMA", font("bod_b", 74), c, "ma", blur=12))
    _rule(L, t, t0 + 0.12, 240, 250, 650, CREAM + (230,))
    _el(L, t, t0 + 0.20, lambda E, g: _shadow_text(E, (W / 2, 262), "일본 야에야마 · 햇빛 아래 야외 배양", font("Medium", 36), c, "ma"), drop=10)
    return L


def a15(t, t0):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    k = INK + (255,)
    _el(L, t, t0, lambda E, g: _shadow_text(E, (W / 2, 96), "CHLOROPHYLL", font("bod_r", 32), k, "ma", alpha=0), drop=10)
    _rule(L, t, t0 + 0.08, 420, 250, 650, INK + (230,))
    _el(L, t, t0 + 0.16, lambda E, g: _shadow_text(E, (W / 2, 438), "야외 3,260mg  vs  실내 2,180mg  (100g당)", font("Medium", 32), k, "ma", alpha=0), drop=10)
    _el(L, t, 31.96, lambda E, g: _shadow_text(E, (W / 2, 136), "×1.5", font("bod_b", 240), k, "ma", alpha=0))   # «1.5배» 단어 시각
    _el(L, t, t0 + 0.30, lambda E, g: _shadow_text(E, (W - 70, 492), "출처: 야에야마쇼쿠산 분석서(제품 상세페이지)", font("Medium", 20), INK + (200,), "ra", alpha=0), drop=0)
    return L


def a100(t, t0):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    c = CREAM + (255,)
    _el(L, t, t0, lambda E, g: _shadow_text(E, (W / 2, 40), "100%", font("bod_b", 200), c, "ma", blur=14))
    _el(L, t, t0 + 0.14, lambda E, g: _shadow_text(E, (W / 2, 270), "PURE CHLORELLA  ·  NO ADDITIVES", font("bod_r", 30), c, "ma"), drop=10)
    return L


# (이름, 시작, 끝, 그리기 함수) — 시작 = 그 말의 단어 시각(정리 녹음 words.txt) · 끝 = 사장님 컷 끝
GFX = [("44가지", 22.96, 24.424, a44), ("야에야마", 26.40, 29.296, ayae),
       ("엽록소1.5배", 29.36, 32.816, a15), ("클로렐라100", 34.26, 35.552, a100)]


def gfx_frame(fn, t, t0, t1):
    L = fn(t, t0)
    fo = min(1.0, max(0.0, (t1 - t) / 0.12))            # 컷 끝 0.12초 흐려짐
    if fo < 1:
        L.putalpha(L.getchannel("A").point(lambda v: int(v * fo)))
    return L


# ───────────────────────── 효과음 ─────────────────────────
# 부드럽고 고급스러운 결만: 종이·셔터·공기·부드러운 타격 (10-26 «귀에 거슬리는 치링 이런느낌말고»)
SND_FIX = {
    "air": ("ML_Air woosh.wav", 0.5, 0, "attack"),
    "shutter": ("nice-camera-click.mp3", 0.2, 0, "attack"),
    "paper": ("ML_Paper slide.wav", 0.3, 0, "attack"),
    "paperq": ("ML_Paper quick movement.wav", 0.3, 0, "attack"),
    "page": ("ML_Big paper page turn.wav", 0.6, 0, "attack"),
    "soft0": ("KN_impactSoft_heavy_000.wav", 0.3, 0, "attack"),
    "soft1": ("KN_impactSoft_heavy_001.wav", 0.3, 0, "attack"),
    "soft2": ("KN_impactSoft_heavy_002.wav", 0.3, 0, "attack"),
    "sweep": ("ML_Fast small sweep transition.wav", 0.3, 0, "attack"),
    "rise": ("Cinematic SFX - Riser (Short).wav", 0.8, 0, "attack"),
    "chak": ("매거진_착착.wav", 0.3, 0, "attack"),
}
SCENE_SFX = ROOT / "소재/효과음/장면음"


def make_chak():
    """사진 10장 착착 — 종이 미끄러짐·셔터를 번갈아 0.13초 간격으로 한 파일에(scene_kit.bundle 과 같은 방식)."""
    def head(name, dur):
        x = SFX.load(SFX.find_file(name))
        a = np.abs(x).max(1)
        x = x[int(np.argmax(a > a.max() * 10 ** (-40 / 20))):][: int(dur * SFX.SR)].copy()
        fo = int(min(.05, dur / 3) * SFX.SR)
        x[-fo:] *= np.linspace(1, 0, fo)[:, None]
        return x
    pa, sh = head("ML_Paper slide.wav", .16), head("nice-camera-click.mp3", .14)
    hits = [((_T[i] - _T[0]), (sh if i % 2 == 0 else pa), (0.8 if i % 2 == 0 else 0.9)) for i in range(len(_T))]
    end = max(o + len(x) / SFX.SR for o, x, _ in hits)
    out = np.zeros((int(end * SFX.SR) + 1, 2))
    for o, x, g in hits:
        i = int(o * SFX.SR)
        out[i:i + len(x)] += x * g
    SCENE_SFX.mkdir(parents=True, exist_ok=True)
    SFX.write_wav(SCENE_SFX / "매거진_착착.wav", out * min(1, .9 / (np.abs(out).max() + 1e-9)))
# 표제(13.40)와 첫 사진(13.58)이 0.18초 차 — 공기 소리는 들리는 중 잘려(S5b) 빼고 사진 셔터가 맡음 · 사진 넷은 짧은 셔터/종이 번갈아
CUES_MAG = [(13.45, "chak"), (14.70, "page"), (15.18, "soft0")]       # chak = 10장 착착 묶음(아래 make_chak)
CUES_GFX = [(22.96, "soft1"), (26.40, "air"), (29.36, "paper"), (30.86, "sweep"), (31.96, "soft2"), (34.26, "paperq")]


def voice_ref():
    v = SFX.load(VOICE)
    return SFX.voice_ref_from(v) + VOICE_DB


def bake(cues, ref, media, tag):
    make_chak()
    SFX.SND.update(SFX.roles_from(SND_FIX))
    items = []
    for t, r in cues:
        x, _ = SFX.prep(r, ref)
        x = x * 10 ** ((SFX.ad_target(Path(SND_FIX[r][0]).name) - (SFX.rms_frames(x).max() - ref)) / 20)
        x *= min(1.0, 0.89 / (np.abs(x).max() + 1e-9))
        items.append(dict(t=t - SFX.attack_at(x), x=x, cue=t, label=f"{t:.2f} {SND_FIX[r][0]}", file=SND_FIX[r][0]))
    warns = SFX.fit_tails(items)
    for i, d in enumerate(items):
        d["path"] = media / f"{tag}_{i + 1:02d}_{Path(d['file']).stem[:24].replace(' ', '_')}.wav"
        SFX.write_wav(d["path"], d["x"])
    return items, warns


# ───────────────────────── 렌더 · XML ─────────────────────────

def enc_mp4(path):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "60000/1001",
                             "-i", "-", "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", str(path)],
                            stdin=subprocess.PIPE)


def enc_alpha(path):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", "60000/1001",
                             "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", str(path)],
                            stdin=subprocess.PIPE)


def frames(t0, t1):
    f0, f1 = round(t0 * FPS), round(t1 * FPS)
    return [(f, f / FPS) for f in range(f0, f1)]


def xml(path, name, vclips, aitems, v_track):
    rate = "<rate><timebase>60</timebase><ntsc>TRUE</ntsc></rate>"
    fr = lambda s: int(round(s * FPS))   # noqa: E731
    files = {}

    def clip(cid, p, start, end, kind):
        dur = end - start
        if str(p) in files:
            fe = f'<file id="{files[str(p)]}"/>'
        else:
            fid = files[str(p)] = f"file-{len(files) + 1}"
            media = ("<media><audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics><channelcount>2</channelcount></audio></media>"
                     if kind == "a" else f"<media><video><samplecharacteristics>{rate}<width>{W}</width><height>{H}</height><pixelaspectratio>square</pixelaspectratio></samplecharacteristics></video></media>")
            fe = f'<file id="{fid}"><name>{escape(Path(p).name)}</name><pathurl>{escape(lec_xml.url(p))}</pathurl>{rate}<duration>{dur}</duration>{media}</file>'
        st = ("<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack>"
              "<filter><effect><name>Audio Levels</name><effectid>audiolevels</effectid><effectcategory>audiolevels</effectcategory><effecttype>audiolevels</effecttype><mediatype>audio</mediatype>"
              '<parameter authoringApp="PremierePro"><parameterid>level</parameterid><name>Level</name><valuemin>0</valuemin><valuemax>3.98109</valuemax><value>1</value></parameter></effect></filter>') if kind == "a" else ""
        return (f'<clipitem id="{cid}"><name>{escape(Path(p).name)}</name><enabled>TRUE</enabled>{rate}'
                f"<start>{start}</start><end>{end}</end><in>0</in><out>{dur}</out>{fe}{st}</clipitem>")
    vc = "".join(clip(f"v-{i}", p, fr(a), fr(b), "v") for i, (p, a, b) in enumerate(vclips))
    vtr = ["<track></track>"] * (v_track - 1) + [f"<track>{vc}</track>"]
    lanes, ends = [], []                                     # 겹치면 다음 트랙
    for i, d in enumerate(sorted(aitems, key=lambda d: d["t"])):
        s = fr(d["t"])
        e = s + max(1, int(len(d["x"]) / SFX.SR * FPS + 1e-6))
        c = clip(f"a-{i}", d["path"], s, e, "a")
        for j, last in enumerate(ends):
            if last <= s:
                lanes[j].append(c)
                ends[j] = e
                break
        else:
            lanes.append([c])
            ends.append(e)
    atr = ["<track></track>"] * 2 + [f"<track>{''.join(l)}</track>" for l in lanes]     # A1 목소리 · A2 클립 소리 비워 둠
    end = max([fr(b) for _, _, b in vclips] + ends) + 120
    x = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="5"><sequence id="seq-1">'
         f"<name>{name}</name><duration>{end}</duration>{rate}<media><video><format><samplecharacteristics>{rate}<width>{W}</width><height>{H}</height>"
         "<pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance></samplecharacteristics></format>"
         f"{''.join(vtr)}</video><audio><numOutputChannels>2</numOutputChannels>{''.join(atr)}</audio></media></sequence></xmeml>")
    path.write_text(x, encoding="utf-8")
    return [f"A{3 + i}" for i in range(len(lanes))]


# ───────────────────────── 미리보기(사장님 V1 컷 재현 + 두 묶음 + 소리) ─────────────────────────

def kf(v, lt):
    if not isinstance(v, dict):
        return v
    ks = v.get("keys") or []
    if not ks:
        return v["v"]
    if lt <= ks[0][0]:
        return ks[0][1]
    if lt >= ks[-1][0]:
        return ks[-1][1]
    for (a, va), (b, vb) in zip(ks, ks[1:]):
        if a <= lt <= b:
            u = (lt - a) / (b - a)
            if ":" in str(va):
                pa, pb = [list(map(float, s.split(":"))) for s in (va, vb)]
                return ":".join(str(x + (y - x) * u) for x, y in zip(pa, pb))
            return float(va) + (float(vb) - float(va)) * u
    return ks[-1][1]


def src_path(name):
    p = SRC / name
    if p.exists():
        return p
    for q in (OUT.parent / "퓨레바_육아_3차_1026/힉스필드").glob("*"):
        if q.name == name:
            return q
    return SRC / name.replace(" (1)", "")


def preview(mag_mp4, gmovs, sfx_items, out):
    seq = json.loads(SEQ.read_text(encoding="utf-8"))
    v1 = sorted([i for i in seq["items"] if i["track"] == "V1"], key=lambda i: i["t0"])
    dur = max(i["t1"] for i in seq["items"])
    enc = enc_mp4(TMP / "pv_preview_video.mp4")
    readers = {}

    def frame_of(it, t):
        key = id(it)
        if key not in readers:
            p = src_path(it["name"])
            pr = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{it.get('s0', 0)}", "-i", str(p), "-f", "rawvideo", "-pix_fmt", "rgb24", "-vf", "fps=60000/1001", "-"],
                                  stdout=subprocess.PIPE)
            wh = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                 "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip().split(",")
            w, h = int(wh[0]), int(wh[1])                   # 10-26: 보간판은 1080×1920 — 1916 으로 읽으면 화면이 갈라짐
            readers[key] = (pr, w, h, [None])
        pr, w, h, last = readers[key]
        buf = pr.stdout.read(w * h * 3)
        if len(buf) == w * h * 3:
            last[0] = Image.frombytes("RGB", (w, h), buf)
        return last[0]
    mag = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(mag_mp4), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    gr = {}
    for f, t in frames(0, dur):
        canvas = Image.new("RGB", (W, H), (0, 0, 0))
        if MAG_T0 <= t < MAG_T1:
            buf = mag.stdout.read(W * H * 3)
            if len(buf) == W * H * 3:
                canvas = Image.frombytes("RGB", (W, H), buf)
        else:
            it = next((i for i in v1 if i["t0"] <= t < i["t1"]), None)
            if it:
                src = frame_of(it, t)
                mo = next((x["params"] for x in it.get("fx", []) if x["name"] == "모션"), {})
                lt = t - it["t0"]
                sc = float(kf(mo.get("비율 조정", "100"), lt)) / 100 if mo else (W / src.width)
                rot = float(kf(mo.get("회전", "0"), lt)) if mo else 0
                px, py = map(float, str(kf(mo.get("위치", "0.5:0.5"), lt)).split(":")) if mo else (0.5, 0.5)
                im = src.resize((max(1, round(src.width * sc)), max(1, round(src.height * sc))), Image.BILINEAR)
                if rot:
                    im = im.rotate(-rot, expand=True)
                canvas.paste(im, (round(px * W - im.width / 2), round(py * H - im.height / 2)))
        cv = canvas.convert("RGBA")
        for name, a, b, p in gmovs:
            if a <= t < b:
                if name not in gr:
                    gr[name] = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(p), "-f", "rawvideo", "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE)
                buf = gr[name].stdout.read(W * H * 4)
                if len(buf) == W * H * 4:
                    cv.alpha_composite(Image.frombytes("RGBA", (W, H), buf))
        enc.stdin.write(cv.convert("RGB").tobytes())
    enc.stdin.close()
    enc.wait()
    # 소리: A1 목소리(+9dB) + A2 사장님 클립 소리 + 효과음
    import soundfile as sf
    total = int(dur * SFX.SR)
    mix = np.zeros((total, 2), np.float32)
    v = SFX.load(VOICE) * 10 ** (VOICE_DB / 20)
    mix[:min(total, len(v))] += v[:total]
    for it in [i for i in seq["items"] if i["track"] == "A2"]:
        a = SFX.load(src_path(it["name"]))[int(it.get("s0", 0) * SFX.SR):]
        s = int(it["t0"] * SFX.SR)
        n = min(len(a), int((it["t1"] - it["t0"]) * SFX.SR), total - s)
        mix[s:s + n] += a[:n]
    for d in sfx_items:
        s = int(round(d["t"] * SFX.SR))
        x = d["x"][:max(0, total - s)]
        mix[s:s + len(x)] += x
    sf.write(TMP / "pv_preview.wav", mix, SFX.SR, subtype="FLOAT")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(TMP / "pv_preview_video.mp4"), "-i", str(TMP / "pv_preview.wav"),
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-shortest", str(out)], check=True)


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    d1, d2 = OUT / "1_이현이_매거진", OUT / "2_설계표_연출"
    for d in (d1, d2):
        (d / "media").mkdir(parents=True, exist_ok=True)
    # 1) 매거진
    bg, tiles, cov = mag_assets()
    mag = d1 / "media" / "퓨레바_이현이_매거진.mp4"
    e = enc_mp4(mag)
    for _, t in frames(MAG_T0, MAG_T1):
        e.stdin.write(mag_frame(t, bg, tiles, cov).tobytes())
    e.stdin.close()
    e.wait()
    # 2) 설계표 연출
    gmovs = []
    for name, a, b, fn in GFX:
        p = d2 / "media" / f"퓨레바_{name}.mov"
        e = enc_alpha(p)
        for _, t in frames(a, b):
            e.stdin.write(gfx_frame(fn, t, a, b).tobytes())
        e.stdin.close()
        e.wait()
        gmovs.append((name, a, b, p))
    # 효과음
    ref = voice_ref()
    s1, w1 = bake(CUES_MAG, ref, d1 / "media", "매거진")
    s2, w2 = bake(CUES_GFX, ref, d2 / "media", "연출")
    chk = []
    for items, warns, title in ((s1, w1, "매거진"), (s2, w2, "설계표 연출")):
        ev = [(d["cue"], d["file"], len(d["x"]) / SFX.SR) for d in items]
        res = [r for r in rule_check.check_sfx(ev, 46.0) + warns if "5-3" not in r[1]]   # 빈 구간(5-3)은 사장님 전체 편집에서 — 여기선 얹을 것만
        chk.append(rule_check.report(res, TMP / f"rule_check_{title}.txt", f"효과음 {title}"))
    if any(chk):
        raise SystemExit("효과음 규칙 ERROR")
    a1 = xml(d1 / "1_이현이_매거진.xml", "퓨레바_이현이_매거진", [(mag, MAG_T0, MAG_T1)], s1, v_track=1)
    a2 = xml(d2 / "2_설계표_연출.xml", "퓨레바_설계표_연출", [(p, a, b) for _, a, b, p in gmovs], s2, v_track=4)
    print("XML 1 V1 ·", a1, "/ XML 2 V4 ·", a2)
    preview(mag, gmovs, s1 + s2, OUT / "퓨레바_XML_미리보기.mp4")
    print(OUT)


if __name__ == "__main__":
    main()
