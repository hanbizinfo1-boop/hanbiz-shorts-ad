"""퓨레바 육아 쇼츠 — 컷별 설계 스토리보드 PDF (사장님 연출표 18줄 × 실촬영 21클립 × 녹음 단어 시각).

python 지시작업/tools/pureva_storyboard.py
→ 납품/퓨레바_육아_스토리보드_1026/퓨레바_육아_스토리보드.pdf

시각 = 정리 녹음(`납품/퓨레바_녹음정리_1026/퓨레바_녹음_정리.wav`) faster-whisper 단어 시각(`_tmp/pureva/vo/words.txt`).
실촬영 원본은 Downloads(읽기만). 목업 화면은 1080×1920 기준 자막·화면 글 자리를 그려 본 것(최종 렌더 아님).
"""
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\user\Downloads\drive-download-20261026T014322Z-1-001")
OUT = ROOT / "납품" / "퓨레바_육아_스토리보드_1026" / "퓨레바_육아_스토리보드.pdf"
TMP = ROOT / "_tmp" / "pureva" / "sb"
FONT = ROOT.parent / "소재" / "fonts" / "pretendard"
F = lambda w, s: ImageFont.truetype(str(FONT / f"Pretendard-{w}.otf"), s)

GREEN, INK, MUTE, RED, AMBER = (46, 125, 50), (20, 24, 22), (95, 102, 98), (198, 40, 40), (180, 110, 0)


def clip(n):
    return next(SRC.glob(f"*_{n}_D.MP4"))


# 상태: 있음(실촬영) / 대체(실촬영이 연출표와 다름) / 없음(촬영 필요) / 힉스필드
ROWS = [
    dict(t=(0.00, 2.10), line="애 키우는 엄마 밥, 다 이렇죠?", ask="아이 밥은 정성스럽게 차려져 있는데 엄마 밥은 대충 차려져 있는 식탁 · 식탁 전체를 위에서",
         use=[("0011", 1.0, 3.1)], key=1.8, st="대체", graph=[],
         how="첫 3초 얼굴 규칙 — 0011(얼굴 아래쪽이 보이며 급히 떠먹음)로 연다. 아이 식판 대비 컷은 촬영본에 없음 → 추가 촬영(위에서 식탁 전체, 아이 식판 + 엄마 죽 그릇) 오면 0.0~1.0 은 대비 컷, 1.0~ 0011.",
         sfx="첫 타격(작은) 0.00 · 숟가락 달그락(현장음)"),
    dict(t=(2.16, 3.95), line="아이 밥은 꼬박꼬박 챙기면서", ask="엄마가 아이 식판에 반찬과 밥을 담아주는 장면 · 손 위주 클로즈업",
         use=[], st="없음", graph=[],
         how="촬영본에 없음. 추천 ① 추가 촬영 5초(손 + 아이 식판만, 아이 얼굴 없이). ② 안 되면 Codex 사진풍 이미지(식판에 반찬 담는 손) → 천천히 밀어 들어가기(유료 0).",
         sfx="반찬 담는 톡 소리(작은)"),
    dict(t=(4.00, 6.75), line="정작 제 식사는 늘 뒷전이더라고요.", ask="아이 밥 챙기느라 식탁에 앉지도 못하다가 뒤늦게 밥을 먹는 엄마 · 측면에서 자연스럽게",
         use=[("0012", 0.0, 2.75)], st="대체", graph=[],
         how="0012 위에서 본 죽 그릇 — 한 손으로 받치고 급히 뜨는 손. 측면 컷은 0011 이 1번에 쓰여서 여기선 위 시점(같은 클립 반복 피함).",
         sfx="—(말 위주, 빈 2.5초 안 됨)"),
    dict(t=(6.80, 9.60), line="따로 뭘 준비해서 먹는 것도 쉽지 않고요.", ask="냉장고를 열어보다가 시간이 없어 닫거나, 식탁에 앉았다가 다시 일어나는 모습 · 미디엄샷",
         use=[("0014", 1.75, 4.55)], st="있음", graph=[],
         how="0014 냉장고 문 열고 안을 들여다봄. 냉장고 속 다른 제품 상표는 작게 흐림. (0013 간편식 카트는 사무실 느낌이라 안 씀 — 필요하면 대체 컷)",
         sfx="냉장고 문 소리(현장음)"),
    dict(t=(9.66, 13.55), line="그래서 요즘은 먹던 음식에 / 퓨레바 클로렐라 한 포를 더하고 있어요.", ask="주방에 놓인 퓨레바 제품을 집어 한 포 꺼내는 모습 · 제품 클로즈업 → 손동작",
         use=[("0016", 1.4, 5.3)], st="있음", graph=[],
         how="0016 선반에서 상자를 집어 → 스틱을 쭉 뽑음. «퓨레바 클로렐라» 말에 상자 정면이 보이게 시작점 맞춤.",
         sfx="«그래서» 전환 휙(−5) · 스틱 뽑는 소리(현장음)"),
    dict(t=(13.58, 16.50), line="자기관리의 끝판왕 / 이현이가 모델인 제품인데요.", ask="퓨레바 패키지와 이현이 모델이 들어간 공식 제품 이미지 · 실물 패키지 + 공식 이미지 편집 삽입",
         use=[("0031", 0.25, 3.15)], st="있음", graph=["이현이 공식 이미지 카드(홈페이지·퓨레바 공식)", "이름표 «모델 이현이»"],
         how="바탕 0031 상자 여러 개 든 손 → «이현이가» 에 공식 이미지 카드가 위에서 내려와 손 위에 섬. 공식(브랜드) 이미지만 · 인스타 원본이면 다른 브랜드 안 보이는 것만 + 대표 확인. 효능 문구(«피부톤…») 들어간 이미지는 안 씀.",
         sfx="카드 등장 휙(−5) · 이름표 작은 탭(−7)"),
    dict(t=(16.54, 18.05), line="아이 우유나 요거트 챙길 때", ask="아이 우유를 컵에 따르고 요거트를 그릇에 담는 모습 · 상단 45도",
         use=[("0017", 9.0, 9.8), ("0018", 2.5, 3.25)], st="있음", graph=[],
         how="두 컷 0.75초씩 — 0017 머그에 우유 따르기 → 0018 유리 그릇에 담기. ★ 우유팩 상표(빨간 로고)가 크게 보임 → 상표 자리 흐림(추적) 또는 머그 쪽으로 당겨 자름.",
         sfx="따르는 소리(현장음)"),
    dict(t=(18.10, 20.10), line="제 것도 같이 준비해서 한 포 넣거나,", ask="엄마가 자신의 요거트에 클로렐라 한 포를 넣는 장면 · 가루가 떨어지는 모습 클로즈업",
         use=[("0019", 2.75, 4.75)], st="있음", graph=[],
         how="0019 위에서 — 흰 요거트 위로 스틱을 털면 진한 초록이 쌓임(3.75~). 위 시점이라 화면을 돌려도 어색하지 않음.",
         sfx="가루 사르르(작은 −7)"),
    dict(t=(20.16, 21.62), line="카페라떼에 넣어 먹어요.", ask="라떼에 클로렐라를 넣고 스푼으로 저어주는 장면 · 컵 정면 + 상단",
         use=[("0020", 8.25, 9.71)], st="있음", graph=[],
         how="0020 상자 옆 유리병 라떼를 젓는 손(얼굴은 턱 아래). 라떼 색은 촬영본에서 거의 베이지 — 초록이 잘 안 보임(색 보정으로 과장하지 않음).",
         sfx="스푼 딸깍(현장음)"),
    dict(t=(21.68, 24.40), line="한 포에 영양성분이 44가지나 들어 있는데,", ask="퓨레바 스틱 한 포를 손에 들고 보여주는 장면 · 손과 스틱 클로즈업 + '44가지 영양성분' 자막",
         use=[("0021", 0.25, 2.95)], st="있음", graph=["«영양성분 44가지» — «44» 숫자 팝(초록)"],
         how="0021 햇빛 아래 스틱 + 상자를 든 손(뒤는 도시). «44가지나» 단어 시각 22.96 에 숫자 팝 → 다음 줄 전까지 유지.",
         sfx="숫자 팝 타격(−2)"),
    dict(t=(24.44, 26.20), line="여기 진한 초록색 보이세요?", ask="흰 요거트에 진한 초록색 클로렐라 가루가 떨어지는 장면 · 초근접 촬영",
         use=[("0026", 4.25, 6.01)], st="대체", graph=[],
         how="0026 흰 바탕에 쏟은 진한 초록 가루 무더기(옆으로 찍힌 컷 → 90° 돌려 씀). 요거트 위 초근접은 0019 가 8번에 쓰여서 겹침을 피함 — 0019 끝부분으로 바꿔도 됨.",
         sfx="가루 쏟는 소리(현장음)"),
    dict(t=(26.26, 29.30), line="일본 야에야마에서 / 햇빛을 받으며 야외배양해서", ask="창가에 제품을 놓고 자연광으로 패키지를 보여주는 장면 · 제품 실사 + 야에야마 관련 텍스트",
         use=[], st="힉스필드", graph=["위치 표지 «일본 · 야에야마»(렌더러 글자)"],
         how="사장님 지시대로 힉스필드 재연. 순서: Codex 사진풍 시작프레임 2안(야에야마 바다 + 햇빛 아래 야외 배양 연못, 글자·로고 없음) → 사장님 고르심 → 유료 1건(Kling 3.0 · 4초 · 1배속 · sound off). 글자는 렌더러가 얹음.",
         sfx="바람·물결(작은)"),
    dict(t=(29.34, 32.85), line="실내배양 클로렐라보다 / 엽록소 함량이 1.5배 높고", ask="초록색 클로렐라가 섞인 음료를 클로즈업 · 제품 위에 '엽록소 함량 1.5배' 그래픽",
         use=[], st="힉스필드", graph=["«엽록소 1.5배»(숫자 하나만 크게)", "작은 근거 «100g당 야외 3,260mg · 실내 2,180mg»"],
         how="힉스필드 재연(12번과 같은 모델로 질감 통일). 시작프레임 = 햇빛 받는 초록 배양수 클로즈업. 그래픽은 실내(회색) vs 야외(초록) 막대 두 개 — 쪽마다 색 하나. 무료 대안: 실촬영 0022(햇빛 아래 물에 풀리는 초록) 12~16초.",
         sfx="막대 차오르는 소리 · «1.5배» 타격(−2)"),
    dict(t=(32.88, 35.55), line="첨가물 없이 클로렐라 100%만 담아서", ask="스틱 뒷면 원재료명 확대, 스틱에서 가루를 붓는 모습 · 제품 정보 + 원료 클로즈업",
         use=[("0025", 0.9, 3.57)], st="있음", graph=["«클로렐라 100%»(상자 표기 위 강조 테두리)"],
         how="0025 상자 표시사항(«클로렐라분말 100%»)으로 다가감. «100%만» 34.30 에 표기 자리를 초록 테두리로 짚음 — 실제 표기를 짚는 것(새 숫자 아님).",
         sfx="강조 테두리 쓱(작은)"),
    dict(t=(35.60, 37.30), line="이렇게 진한 초록색이에요.", ask="스푼으로 섞은 초록 요거트를 들어 올리는 장면 · 질감이 잘 보이도록 근접 촬영",
         use=[("0022", 15.0, 16.7)], st="대체", graph=[],
         how="스푼으로 든 초록 요거트 컷은 촬영본에 없음(0030 요거트는 흰색). 0022 햇빛 아래 물속에 진한 초록이 퍼지는 장면으로 대체. 원하시면 추가 촬영.",
         sfx="—"),
    dict(t=(37.34, 40.35), line="하루 1g, 한 포 뜯어서 / 어디든 넣으면 관리 끝!", ask="퓨레바 한 포 뜯기 → 요거트에 넣기 → 섞기 → 먹기 · 빠른 4컷 연결",
         use=[("0028", 4.0, 4.75), ("0022", 8.5, 9.25), ("0020", 10.5, 11.25), ("0030", 1.0, 1.75)], st="있음", graph=["«하루 1g»(작은 표지)"],
         how="0.75초 × 4컷 — 가방에서 스틱 뽑기(«어디든») → 물에 털기 → 라떼 젓기 → 한 입. «관리 끝!» 40.16 에 마지막 컷 착.",
         sfx="컷마다 짧은 휙 · «끝!» 타격(−2)"),
    dict(t=(40.40, 42.35), line="저처럼 내 밥은 늘 뒷전인 엄마들,", ask="식탁에서 요거트를 먹으며 카메라를 바라보는 엄마 · 상반신 정면 촬영",
         use=[("0030", 1.75, 3.70)], st="대체", graph=[],
         how="0030 요거트 먹는 상반신 — 얼굴은 코 아래까지만, 카메라를 안 봄. 정면 얼굴 컷은 촬영본에 없음 → 추가 촬영 권장.",
         sfx="—"),
    dict(t=(42.40, 45.87), line="퓨레바 클로렐라가 궁금하다면 / 아래 링크에서 확인해보세요.", ask="엄마가 퓨레바 제품을 손에 들고 카메라를 향해 보여주는 모습 · 제품과 얼굴이 함께 보이는 엔딩",
         use=[("0031", 0.25, 3.72)], st="대체", graph=["끝 카드: 제품 + «자세히 보기» 버튼 + 손가락", "[오퍼 자리 — 11월 행사]"],
         how="0031 상자를 든 손(얼굴 없음) → 44.24 «아래» 에 버튼이 올라오고 손가락이 누름. 얼굴 + 제품 컷은 촬영본에 없음 → 추가 촬영 권장.",
         sfx="버튼 등장 탭 · 누름 딸깍"),
]

STATE = {"있음": (GREEN, "실촬영 있음"), "대체": (AMBER, "대체 컷"), "없음": (RED, "촬영 없음"), "힉스필드": ((40, 90, 200), "힉스필드")}


def grab(n, t, rot=False):
    TMP.mkdir(parents=True, exist_ok=True)
    p = TMP / f"{n}_{t:.2f}.png"
    if not p.exists():
        vf = "transpose=1," if rot else ""
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t}", "-i", str(clip(n)), "-frames:v", "1",
                        "-vf", f"{vf}scale=1080:-2", str(p)], check=True)
    im = Image.open(p).convert("RGB")
    if rot:  # 가로가 된 화면 → 가운데 9:16
        w = im.height * 9 // 16
        im = im.crop(((im.width - w) // 2, 0, (im.width - w) // 2 + w, im.height)).resize((1080, 1920))
    return im


def text_box(d, xy, s, f, fill=(255, 255, 255), pad=18, bg=(0, 0, 0, 170)):
    x, y = xy
    b = d.textbbox((0, 0), s, font=f)
    w, h = b[2] - b[0], b[3] - b[1]
    d.rounded_rectangle([x - w // 2 - pad, y - pad, x + w // 2 + pad, y + h + pad], 14, fill=bg)
    d.text((x - w // 2, y - b[1]), s, font=f, fill=fill)


def mock(r):
    """1080×1920 목업 — 첫 클립 가운데 프레임 + 자막 + 화면 글."""
    if r["use"]:
        n, a, b = r["use"][0]
        im = grab(n, r.get("key", (a + b) / 2), rot=(n == "0026"))
    else:
        im = Image.new("RGB", (1080, 1920), (214, 218, 215))
        dd = ImageDraw.Draw(im)
        lab = "힉스필드 재연\n(Codex 시작프레임 → 확인 → 1건)" if r["st"] == "힉스필드" else "촬영 없음\n추가 촬영 또는 Codex"
        dd.multiline_text((540, 820), lab, font=F("Bold", 64), fill=(70, 76, 72), anchor="mm", align="center", spacing=20)
    im = im.convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # 자막(가운데 아래 0.62H) — 흰 글자 + 검은 외곽
    sub = r["line"].split(" / ")[0]
    f = F("ExtraBold", 66)
    lines = [sub]
    if d.textlength(sub, font=f) > 960:  # 한 줄에 안 들어가면 가운데 띄어쓰기에서 두 줄
        sp = [i for i, c in enumerate(sub) if c == " "]
        cut = min(sp, key=lambda i: abs(i - len(sub) / 2))
        lines = [sub[:cut], sub[cut + 1:]]
    for j, ln in enumerate(lines):
        bb = d.textbbox((0, 0), ln, font=f, stroke_width=7)
        d.text((540 - (bb[2] - bb[0]) // 2, 1190 + j * 86), ln, font=f, fill="white", stroke_width=7, stroke_fill="black")
    # 화면 글(첫 항목만 그려 봄)
    for g in r["graph"][:1]:
        s = g.split("«")[1].split("»")[0] if "«" in g else g
        text_box(d, (540, 330), s, F("Black", 76), fill=(170, 240, 120))
    if r["st"] in ("대체",) and r["use"] and r["use"][0][0] in ("0017",):
        pass
    im = Image.alpha_composite(im, ov).convert("RGB")
    # 안전선(아래 UI 가림 y 1560)
    d2 = ImageDraw.Draw(im)
    d2.line([(0, 1560), (1080, 1560)], fill=(255, 60, 60), width=4)
    return im


def wrap(d, s, f, w):
    out, cur = [], ""
    for ch in s:
        if d.textlength(cur + ch, font=f) > w:
            out.append(cur)
            cur = ch
        else:
            cur += ch
    out.append(cur)
    return out


def para(d, xy, s, f, w, fill=INK, gap=8):
    x, y = xy
    for line in wrap(d, s, f, w):
        d.text((x, y), line, font=f, fill=fill)
        y += f.size + gap
    return y


PW, PH = 2480, 1754  # A4 가로 300dpi


def page_brief():
    pg = Image.new("RGB", (PW, PH), "white")
    d = ImageDraw.Draw(pg)
    d.text((120, 100), "퓨레바 육아 쇼츠 — 컷별 설계 스토리보드", font=F("Black", 72), fill=INK)
    d.text((120, 200), "10-26 · 확정 대본(육아) · 사장님 연출표 18줄 · 실촬영 21클립 · 정리 녹음 45.87초", font=F("Medium", 36), fill=MUTE)
    L = [
        ("어떻게 만들까 — 지난 피드백에서 가져온 방향", [
            "첫 3초는 사람 얼굴(7번 «초반 3초는 무조건 사람얼굴») — 촬영본에 정면 얼굴이 없어 1번은 0011(얼굴 아래쪽 + 먹는 모습)로 연다.",
            "바닥은 항상 실제 영상(«초반은 영상 · 바닥은 항상 실제 영상») — 이미지·까만 화면 오프닝 없음. 정지 이미지는 이현이 공식 카드 한 장만.",
            "말의 결과를 보여 준다 — 줄마다 «그 말이 실제로 일어나는 자리»(연출표 그대로) · 움직임은 녹음 단어 시각에 건다.",
            "인지할 텀 0.6초 · 빠른 4컷(16번)도 0.75초씩 · 덩그러니·일정 속도 금지 — 실촬영 자체 움직임 + 컷 리듬 1.5~3초.",
            "화면 글은 렌더러(Pretendard)가 그린다 — 44가지 · 야에야마 · 엽록소 1.5배 · 클로렐라 100% · 버튼. AI 영상에 글자를 맡기지 않는다.",
            "숫자는 대본·상세페이지에 있는 것만 — 1.5배 근거(100g당 3,260 vs 2,180mg)는 작은 글씨로. 한 화면 큰 숫자 하나.",
            "비교(13번)는 쪽마다 색 하나: 실내 회색 / 야외 초록. 그 외 3색(바탕 · 흰 글 · 강조 초록).",
            "유료는 힉스필드 2컷(12·13번)만, 장면당 1건 — Codex 시작프레임 후보를 먼저 보여 드리고 고르신 것만 발주.",
            "효과음은 AD_LEVEL(타격 −2 · 휙 −5 · 작은 −7), 자연 길이 · 겹침 0 · 들리는 중 잘림 0. 가루·따르기·스틱은 실촬영 현장음을 살림.",
            "다른 상표 금지 — 우유팩(7번)·냉장고 속 제품 상표는 흐림. 이현이는 공식 브랜드 이미지만, 효능 문구 이미지 안 씀.",
        ]),
        ("규격", [
            "1080×1920 · 59.94fps(촬영본 1728×3072 · 59.94 그대로 축소, 확대 여유 1.6배) · 목소리 = 정리 녹음 · −14 LUFS · 트루피크 −1.5dB.",
            "자막: 한 줄 · 흰 글자 + 검은 외곽 · 핵심어만 초록 · 가운데 아래(y≈1190) · 읽힐 글자는 y 1560(쇼츠 아래 UI) 위.",
            "납품: 완성 mp4 + 프리미어 XML(실촬영 원본 참조 · 그래픽 알파 MOV · 자막 · 효과음 낱개).",
        ]),
    ]
    y = 300
    for title, items in L:
        d.text((120, y), title, font=F("Bold", 44), fill=GREEN)
        y += 70
        for it in items:
            d.text((140, y), "·", font=F("Bold", 34), fill=INK)
            y = para(d, (175, y), it, F("Regular", 33), PW - 320) + 10
        y += 30
    return pg


def page_ask():
    pg = Image.new("RGB", (PW, PH), "white")
    d = ImageDraw.Draw(pg)
    d.text((120, 100), "만들기 전에 정해 주실 것", font=F("Black", 64), fill=INK)
    qs = [
        ("1. 촬영본에 없는 컷 4곳", "2번 아이 식판에 담는 손 · 1번 아이 vs 엄마 식탁 대비 · 15번 초록 요거트 스푼 · 17·18번 정면 얼굴(+제품). "
                              "추천: 추가 촬영 한 번(아이 얼굴 없이 식판·손, 엄마 정면 2컷, 초록 요거트 스푼 — 합 30초 분량). 어려우면 2번은 Codex 사진풍 이미지, 나머지는 이 안의 대체 컷으로."),
        ("2. 이현이 공식 이미지", "홈페이지·공식 인스타 중 쓸 이미지를 주시거나, 제가 공식 홈페이지에서 브랜드 이미지를 골라 올리겠습니다(인스타 원본은 다른 브랜드가 안 보이는 것만 + 대표 확인)."),
        ("3. 힉스필드 2컷(12·13번)", "Codex 시작프레임 후보를 컷당 2안 만들어 보여 드린 뒤 고르신 것만 1건씩 발주(Kling 3.0 · 4초 · 발주 전 비용 확인). 13번은 실촬영 0022(햇빛 아래 퍼지는 초록)로 대신하면 유료 1건이 줄어듭니다."),
        ("4. 배경음악", "넣을지(넣는다면 밝은 일상 톤 한 곡 −20dB 아래) / 목소리 + 효과음만 갈지."),
        ("5. 오퍼·버튼 문구", "18번 끝 카드 — 11월 행사가 정해지면 넣습니다(지금은 «자세히 보기» 버튼만)."),
        ("6. 규격", "1080×1920 · 59.94 로 갑니다(사장님 7번 시퀀스는 900×1600). 다르게 원하시면 말씀 주세요."),
    ]
    y = 220
    for t, s in qs:
        d.text((120, y), t, font=F("Bold", 42), fill=GREEN)
        y = para(d, (140, y + 62), s, F("Regular", 34), PW - 300) + 40
    d.text((120, PH - 180), "※ 시각은 정리 녹음 받아쓰기 단어 시각. 목업 화면은 자막·화면 글 자리를 그려 본 것(최종 아님). 빨간 선 = 쇼츠 아래 UI 가림선.",
           font=F("Medium", 30), fill=MUTE)
    return pg


def page_rows(rows, first):
    pg = Image.new("RGB", (PW, PH), "white")
    d = ImageDraw.Draw(pg)
    rh = (PH - 120) // 2
    for k, r in enumerate(rows):
        y0 = 60 + k * rh
        n = first + k
        d.line([(60, y0), (PW - 60, y0)], fill=(220, 224, 221), width=3)
        # 목업
        m = mock(r).resize((int((rh - 40) * 9 / 16), rh - 40))
        pg.paste(m, (90, y0 + 20))
        x = 90 + m.width + 50
        col, lab = STATE[r["st"]]
        d.text((x, y0 + 22), f"{n:02d}", font=F("Black", 64), fill=INK)
        d.text((x + 110, y0 + 30), f"{r['t'][0]:.2f} ~ {r['t'][1]:.2f}초  ({r['t'][1]-r['t'][0]:.1f}초)", font=F("Bold", 34), fill=MUTE)
        bw = d.textlength(lab, font=F("Bold", 30)) + 40
        d.rounded_rectangle([PW - 120 - bw, y0 + 26, PW - 120, y0 + 76], 12, fill=col)
        d.text((PW - 120 - bw + 20, y0 + 32), lab, font=F("Bold", 30), fill="white")
        yy = para(d, (x, y0 + 100), r["line"].replace(" / ", " "), F("ExtraBold", 46), PW - x - 120)
        W = PW - x - 120
        yy = para(d, (x, yy + 6), "연출표 · " + r["ask"], F("Regular", 32), W, fill=MUTE) + 8
        # 쓸 소재 썸네일
        tx = x
        for (c, a, b) in r["use"]:
            th = grab(c, (a + b) / 2, rot=(c == "0026")).resize((135, 240))
            pg.paste(th, (tx, yy))
            d.text((tx, yy + 246), f"{c} {a:.2f}~{b:.2f}", font=F("Medium", 24), fill=INK)
            tx += 230
        if r["use"]:
            yy += 290
        yy = para(d, (x, yy), "만드는 법 · " + r["how"], F("Medium", 33), W) + 6
        if r["graph"]:
            yy = para(d, (x, yy), "화면 글 · " + " / ".join(r["graph"]), F("Medium", 33), W, fill=GREEN) + 6
        para(d, (x, yy), "효과음 · " + r["sfx"], F("Medium", 33), W, fill=MUTE)
    return pg


def main():
    pages = [page_brief(), page_ask()]
    for i in range(0, len(ROWS), 2):
        pages.append(page_rows(ROWS[i:i + 2], i + 1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pages[0].save(OUT, save_all=True, append_images=pages[1:], resolution=300)
    for k, p in enumerate(pages):
        p.resize((PW // 3, PH // 3)).save(TMP / f"page{k + 1}.jpg", quality=80)
    print(OUT, len(pages), "쪽")


if __name__ == "__main__":
    main()
