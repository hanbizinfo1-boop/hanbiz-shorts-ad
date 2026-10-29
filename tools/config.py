# -*- coding: utf-8 -*-
r"""한비즈 쇼츠 광고 — 경로·규격 설정 한 곳.

다른 PC 로 옮기면 여기(또는 같은 이름의 환경변수)만 고친다. 도구는 경로를 이 파일에서만 가져온다.
  예) set HANBIZ_SFX_LIB=E:\효과음\예능효과음
환경변수가 있으면 그것이 이긴다.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # 한비즈-쇼츠광고/
TOOLS = ROOT / "tools"


def _p(env, default):
    return Path(os.environ.get(env, default))


# ── 애프터이펙트 (AE 2026 한국어판 — 출력 모듈 템플릿 이름이 «고품질» = ProRes 422 HQ)
AE_DIR = _p("HANBIZ_AE_DIR", r"C:\Program Files\Adobe\Adobe After Effects 2026\Support Files")
AE_RENDER_TEMPLATE = "고품질"                           # 알파 필요하면 «고품질(알파 포함)»

# ── 효과음
# 10-08 사장님 «응 따로 복사해» → 이 폴더 소재/효과음/ 사본이 기본이다(음원은 .gitignore 로 커밋 제외).
# SFX_LIB = Mixkit·Kenney·効果音ラボ 받은 것. 앞말 ML_ KN_ SEL_ 로 구분. 원본 D:\영상제작\소재\예능효과음
SFX_LIB = _p("HANBIZ_SFX_LIB", ROOT / "소재" / "효과음" / "받은라이브러리")
# 사장님 개인 라이브러리(앞말 없는 파일들: 휙２.mp3 · 두꺼운 바람.mp3 · 맑은소리.mp3 …). 한글 파일명이 NFD 일 수 있어 sfx.find_file 이 정규화해서 찾는다.
# 원본 C:\Users\user\Desktop\작업공간\효과음 — 모음1~6(게임·방송 음원)은 복사하지 않았다.
SFX_LIB_OWNER = _p("HANBIZ_SFX_LIB_OWNER", ROOT / "소재" / "효과음" / "사장님라이브러리")
# 장면음(드론·지하철 같은 배경 소리). 원본 C:\Users\user\Desktop\분양\효과음\오픈소스\16_장면음
SFX_LIB_SCENE = _p("HANBIZ_SFX_LIB_SCENE", ROOT / "소재" / "효과음" / "장면음")
GRADE_JSON =TOOLS / "data" / "예능효과음-등급.json"      # A★ → A → B 등급표(파일 경로 문자열 + 점수)
USED_JSON = TOOLS / "data" / "예능효과음-실사용.json"      # 사장님이 실제 편집에서 통과·반려한 소리

# ── 글꼴
# 소재/fonts/ 에 받아 둔 사본(OFL·상업 사용 가능, 출처 소재/fonts/출처.md). 윈도에는 설치하지 않는다 — 파일 경로로만 쓴다.
FONTS_DIR = _p("HANBIZ_FONTS_DIR", ROOT / "소재" / "fonts")


def _font_first(*cands):
    """이 폴더 사본이 있으면 그걸, 없으면 마지막 후보(기존 경로)를 돌려준다."""
    for c in cands:
        if Path(c).exists():
            return Path(c)
    return Path(cands[-1])


FONTS = {
    "pretendard_bold": _font_first(FONTS_DIR / "pretendard" / "Pretendard-Bold.otf",
                                   _p("HANBIZ_FONT_PRETENDARD", r"C:\Users\user\AppData\Local\Microsoft\Windows\Fonts\Pretendard-Bold.otf")),
    "noto_sans_kr": Path(r"C:\Windows\Fonts\NotoSansKR-VF.ttf"),     # 가변 폰트: 굵기 500 으로 쓴다(맑은 고딕 25px 은 받침이 뭉개짐)
    "noto_serif_kr": Path(r"C:\Windows\Fonts\NotoSerifKR-VF.ttf"),
    "gaegu_bold": ROOT / "_tmp" / "fonts" / "Gaegu-Bold.ttf",   # 손글씨(OFL). 없으면 장면 도구가 받는다
    # ── 소재/fonts/ 사본 (10-08 사장님 승인 «글꼴은 추가필요한거 다 받아도돼»)
    "pretendard_thin": FONTS_DIR / "pretendard" / "Pretendard-Thin.otf",
    "pretendard_extralight": FONTS_DIR / "pretendard" / "Pretendard-ExtraLight.otf",
    "pretendard_light": FONTS_DIR / "pretendard" / "Pretendard-Light.otf",
    "pretendard_regular": FONTS_DIR / "pretendard" / "Pretendard-Regular.otf",
    "pretendard_medium": FONTS_DIR / "pretendard" / "Pretendard-Medium.otf",
    "pretendard_semibold": FONTS_DIR / "pretendard" / "Pretendard-SemiBold.otf",
    "pretendard_extrabold": FONTS_DIR / "pretendard" / "Pretendard-ExtraBold.otf",
    "pretendard_black": FONTS_DIR / "pretendard" / "Pretendard-Black.otf",
    "pretendard_var": FONTS_DIR / "pretendard" / "PretendardVariable.ttf",   # 가변 wght 45~930
    "suit_var": FONTS_DIR / "suit" / "SUIT-Variable.ttf",                    # 가변 wght 100~900
    "black_han_sans": FONTS_DIR / "black-han-sans" / "BlackHanSans-Regular.ttf",
    "do_hyeon": FONTS_DIR / "do-hyeon" / "DoHyeon-Regular.ttf",              # 도현체
    "paperlogy_black": FONTS_DIR / "paperlogy" / "Paperlogy-9Black.ttf",     # 1Thin~9Black 9종 전부 폴더에 있다
    "paperlogy_extrabold": FONTS_DIR / "paperlogy" / "Paperlogy-8ExtraBold.ttf",
    "paperlogy_bold": FONTS_DIR / "paperlogy" / "Paperlogy-7Bold.ttf",
    "paperlogy_regular": FONTS_DIR / "paperlogy" / "Paperlogy-4Regular.ttf",
    "gmarket_sans_bold": FONTS_DIR / "gmarket-sans" / "GmarketSansBold.ttf",
    "gmarket_sans_medium": FONTS_DIR / "gmarket-sans" / "GmarketSansMedium.ttf",
    "gmarket_sans_light": FONTS_DIR / "gmarket-sans" / "GmarketSansLight.ttf",
    "archivo_var": FONTS_DIR / "archivo" / "Archivo-Variable.ttf",           # 가변 wght 100~900 · wdth 62~125 (영문 라벨)
    "mono": FONTS_DIR / "jetbrains-mono" / "JetBrainsMono-Variable.ttf",     # 가변 wght 100~800 (HUD 소형 영문·숫자)
}

# ── 작업 폴더
WORK = ROOT / "_tmp"            # 다시 만들 수 있는 것(중간 렌더·내려받은 원본). git 제외
OUT = ROOT / "납품"              # 사장님께 드리는 것. 같은 이름 제자리 덮어쓰기 — 폴더를 지우지 않는다
SRC = ROOT / "소재"              # 이 건 소재(이미지·로고). 출처는 소재/이미지-출처.md 에 한 줄씩
EDIT_WORK = WORK / "edit"       # 한 편 조립기(edit_render·edit_xml)의 기본 출력 위치. 미리보기 mp4·_점검.txt·XML media

# ── 외부 도구
CODEX_RUN = Path(r"C:/Users/user/.claude/scripts/codex-run.ps1")
CHROME = _p("HANBIZ_CHROME", r"C:\Program Files\Google\Chrome\Application\chrome.exe")   # design_layers 가 레이어 PNG 를 뜰 때

# ── 쇼츠 규격 (세로). 프레임레이트는 첫 작업 때 사장님 시퀀스에서 확인해 고친다 — 분양 쇼츠는 29.97, 강의 시퀀스는 59.94 였다.
W, H = 1080, 1920
FPS = 29.97
