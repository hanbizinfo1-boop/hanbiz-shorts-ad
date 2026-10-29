# -*- coding: utf-8 -*-
r"""한비즈 DB 광고 1 — A지시판(10-14 사장님 직접 지시) 조립 도구. 지시작업 세션 전용.

정본 = 사장님 프리미어 «한비즈 DB 광고 1»(DB광고.prproj, 10-14 10:37 저장): V1 컷 21개 · 48.131초 · 자막 V4(+V5).
루트 tools/ 는 import·실행만(수정 금지 — 지시작업/README.md). 산출은 전부 지시작업/ 안.

    python 지시작업/tools/ad_build.py prep     # 목소리 wav · 자막(V4+V5) · SRT · 단어 시각 · 장면용 times.js
    python 지시작업/tools/ad_build.py plan     # 배치표(장면 렌더 뒤 — events.json 으로 효과음)
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent                 # 지시작업/tools
DZ = HERE.parent                                       # 지시작업
ROOT = DZ.parent
sys.path.insert(0, str(ROOT / "tools"))
import config as C  # noqa: E402
import words as WD  # noqa: E402

SRC = Path(r"D:\26년 10월\261013\1013.mp4")
PRJ_JSON = DZ / "_tmp/prproj/광고1_1014.json"
WORK = DZ / "_tmp/a"
SCENE_DIR = HERE / "scenes"
SEQ_END = 48.131
FPS = 30
BGM = ROOT / "납품/BGM후보_1012/2안_설명형/5_Miles Away.mp3"   # 10-12 사장님 «bgm은 2안 5번» — 이 광고 곡(읽기만)
BGM_DB = -18

# V4 자막 MOV(V3_NN) → 글. NN = 1·2판 SRT 줄 번호 − 1 (납품/한비즈_DB광고1_1013/A_레퍼1카피/한비즈_DB광고1.srt)
V3_TEXT = ["제조업 하시면", "최대 10억 받아가세요", "아직도 제조업이나", "공장 돌리면서", "비싼 이자 쓰고 계세요?",
           "같은 1억을 빌려도", "정책자금이면", "이자가 절반입니다", "제조업 아니라고", "넘기려고 하셨죠?",
           "위탁 생산도", "전부 가능합니다", "아는 사람만 받아가는", "중진공 정책자금이", "4조 7천억원이에요",
           "실시간으로 소진되고", "있는 거 알고 계신가요?", "공장 규모가 작다고요?", "걱정 마세요", "소규모 공장도",
           "신청할 수 있고", "심지어 기계 전용 대출은", "기간도 엄청 넉넉해요", "위탁 생산하는 사람은", "더더욱 좋고요",
           "추가로 한비즈에서는", "대표님 공장에 맞는", "지원금까지", "전부 찾아서", "사업 계획서까지",
           "함께 보내드립니다", "추가로 매달", "경영 분석 리포트까지", "대표님께 전달해드리는데요", "이렇게 버신 돈,",
           "비싼 이자로 다 쓰지 마시고", "아래 버튼 눌러서", "공장 한도부터 확인해보세요"]
# 강조어(노랑) — 1·2판과 같은 자리
EMPH = {"최대 10억 받아가세요": "최대 10억", "비싼 이자 쓰고 계세요?": "비싼 이자", "이자가 절반입니다": "절반",
        "전부 가능합니다": "가능", "4조 7천억원이에요": "4조 7천억원", "기간도 엄청 넉넉해요": "넉넉",
        "추가로 한비즈에서는": "한비즈", "공장 한도부터 확인해보세요": "한도"}
CAP_STYLE = {"mode": "outline", "y": 1140,           # 10-14 «얼굴가리는 문제» — 숙인 컷 턱 끝 y≈1040 → 자막 1075~1205
             "size": 72, "max_w": 800, "track": 1, "stroke": 7,   # 10-14 «안쪽 테두리안에» — 안전선 안(폭 800)
             "colors": {"white": [255, 255, 255], "y": [255, 214, 10], "g": [60, 235, 110], "p": [190, 140, 245]}}


def items(track):
    d = json.loads(PRJ_JSON.read_text(encoding="utf-8"))
    return [i for i in d["items"] if i["track"] == track]


def build_voice():
    """A1 클립을 시퀀스 자리 그대로 이어 붙인 목소리(48k 스테레오). 클립 볼륨(0dB = 0.17783)도 그대로 굽는다."""
    out = WORK / "voice.wav"
    parts = []
    for n, c in enumerate(items("A1")):
        lv = float(c["fx"][0]["params"]["레벨"])
        g = 20 * math.log10(lv / 0.177827939391)
        p = WORK / f"_v{n:02d}.wav"
        d = c["t1"] - c["t0"]
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{c['s0']}", "-t", f"{d:.6f}", "-i", str(SRC), "-vn",
                        "-af", f"volume={g:.3f}dB,apad=whole_dur={d:.6f}", "-ar", "48000", "-ac", "2", str(p)], check=True)
        parts.append(p)
    lst = WORK / "_voice_list.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "pcm_s16le", str(out)], check=True, cwd=WORK)
    for p in parts:
        p.unlink()
    lst.unlink()
    return out


def captions():
    """사장님 V4(자막 MOV — 시각만) + V5(그래픽 글, 줄 나눔). 10-14 «추가로 / 매달» — V3_31 «추가로 매달» → «추가로»."""
    out = []
    for i in items("V4"):
        k = int(i["name"].split("_")[1])
        text = "추가로" if k == 31 else V3_TEXT[k]
        out.append({"text": text, "start": round(i["t0"], 3), "end": round(i["t1"], 3), "emph": [EMPH[text]] if text in EMPH else []})
    for i in items("V5"):
        out.append({"text": " ".join(i["text"]).strip(), "start": round(i["t0"], 3), "end": round(i["t1"], 3), "emph": []})
    return sorted(out, key=lambda c: c["start"])


def srt(caps, path):
    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    path.write_text("".join(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n\n" for i, c in enumerate(caps, 1)), encoding="utf-8-sig")


def prep(skip_words=False):
    WORK.mkdir(parents=True, exist_ok=True)
    v = build_voice()
    caps = captions()
    (WORK / "captions.json").write_text(json.dumps(caps, ensure_ascii=False, indent=1), encoding="utf-8")
    srt(caps, WORK / "한비즈_DB광고1_A지시.srt")
    wpath = WORK / "words.txt"
    if not (skip_words and wpath.exists()):
        segs = [(c["t0"], c["t1"], c["s0"]) for c in items("V1")]
        ws = WD.word_times(segs, SRC)
        wpath.write_text("".join(f"{t:.2f} {w}\n" for t, w in ws), encoding="utf-8")
    ws = [(float(l.split()[0]), l.split(None, 1)[1]) for l in wpath.read_text(encoding="utf-8").split("\n") if l.strip()]
    SCENE_DIR.mkdir(parents=True, exist_ok=True)
    js = "window.WORDS=" + json.dumps([[t, w] for t, w in ws], ensure_ascii=False) + ";\nwindow.CAPS=" + json.dumps(
        [[c["start"], c["end"], c["text"]] for c in caps], ensure_ascii=False) + ";\n"
    (SCENE_DIR / "a_times.js").write_text(js, encoding="utf-8", newline="\n")
    for c in caps:
        print(f"{c['start']:6.2f}–{c['end']:6.2f} {c['text']}")
    print("목소리", v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["prep", "plan"])
    ap.add_argument("--skip-words", action="store_true")
    a = ap.parse_args()
    if a.step == "prep":
        prep(a.skip_words)
    else:
        plan()


# 효과음 역할 → 파일 · 목소리 대비 dB(exact_db). 10-14 사장님 «사람 목소리가 너무작고 효과음이 너무커» → 전부 목소리보다 작게,
# 큰 타격(10억 쾅·카드 쾅·도장)만 −3~−6. 소리 뜻 = 화면 동작(sfx.md 2장). 한 편 안 같은 소리 연달아 금지(5-2).
# 넷째 값 = 그 길이로 딱(음수) — **동작 길이에 맞추는 소리만**(카운터 굴림·마커·형광). 10-19 사장님 «하나로 통합해서 정리» → 결정표 ⑤:
#   겹침을 피하려 길이 상한으로 자르지 않는다(~~card_in·flip·swipe·zoom·shine·page·page2·button 상한~~). 겹치는 것만
#   edit_render(sfx.fit_tails)가 다음 소리 어택 앞 0.2초 감쇠로 끝내고, «들리는 중 잘림» WARN 이 나면 더 짧은 파일로 바꾼다.
ROLES = {
    "photo_in":  ("ML_Explainer video pops whoosh light pop.wav", "peak", -9),
    "photo_in2": ("종이소리.mp3", "peak", -9),
    "card_in":   ("ML_Fast small sweep transition.wav", "peak", -10),
    "slam":      ("ML_Impact of a blow.wav", "peak", -3),
    "slam2":     ("ML_Fast impact blow.wav", "peak", -4),
    "slide_in":  ("ML_Fast transitions swoosh.wav", "peak", -10),
    "tag":       ("KN_toggle_001.wav", None, -9),
    "flip":      ("ML_Big paper page turn.wav", "peak", -9),
    "good":      ("KN_confirmation_004.wav", None, -8),
    "swipe":     ("SEL_マントを翻す.mp3", "peak", -10),
    "swipe2":    ("ML_Fast transitions swoosh.wav", "peak", -11),
    "stamp":     ("도장.mp3", "peak", -6),
    "doc_in":    ("ML_Paper slide.wav", "peak", -8),
    "zoom":      ("ML_Air woosh.wav", None, -10),
    "mark":      ("SEL_油性マーカーで字を書く.mp3", None, -12, -0.30),
    "panel_in":  ("KN_open_003.wav", None, -9),
    "count":     (str(DZ / "소재/효과음/카운터_굴림_길게.wav"), "onset", -10, -2.15),   # 10-14 «줄어들고 올라가는거 … 계속 두드드드» — 카운터 굴림 A·B·A 이어 붙인 2.15초(숫자 움직이는 17.93~20.07 내내)
    "drop":      ("ML_Paper quick movement.wav", "peak", -10),
    "doc_drop":  ("종이소리.mp3", "peak", -8),
    "scan":      ("ML_Interface option select.wav", "peak", -9),
    "belt":      ("SEL_高速移動.mp3", "peak", -12),
    "ding":      ("KN_select_003.wav", None, -9),
    "shine":     ("SEL_キラッ1.mp3", None, -11),
    "chat":      ("채팅 효과음.mp3", None, -8),
    "glint":     ("ML_Achievement bell.wav", None, -12),
    "send":      ("ML_Fast transitions swoosh.wav", "peak", -10),
    "page":      ("ML_Big paper page turn.wav", "peak", -10),
    "page2":     ("종이소리 화면전환.mp3", None, -10),
    "coin":      ("ML_Bag of coins touch.wav", "peak", -6),
    "suck":      ("SEL_高速移動.mp3", "peak", -10),          # 진공 쓸림은 1.5초 차오름이라 돈·카드 소리를 덮음(10-14 점검) → 짧은 쓸림
    "button":    ("ML_Page forward single chime.wav", None, -8),
    "tap":       ("SEL_決定ボタンを押す4.mp3", None, -9),          # CTA 버튼 누름(자연 길이)
    "tap5":      ("KN_toggle_003.wav", None, -9),                 # 휴대폰 탭 — 원래 0.1초 딸깍(10-14 «10초에 효과음 살짝 끊긴다» 때 잘린 탭도 바꿈)
    "swipe_feed": ("ML_Fast small sweep transition.wav", "peak", -10),   # «넘기려고» 엄지 넘김 — 자연 길이 0.32초(망토 휙을 0.45초에서 자르니 끊겨 들림, 10-14)
    "fill":      ("SEL_ゲージ回復1.mp3", "peak", -12, -0.40),     # R5 «위탁 생산» 줄 형광
}
# R10 «걱정 마세요» — 사장님 컷 하나(21.688~22.656)를 얼굴 클로즈업(얼굴 x 450·y 920 → 화면 540·800, 턱 끝 ≈ 908 < 자막 1075)
CLOSEUP = {"t0": 21.688, "scale": 1.35, "pos": [121, -106]}
DELIV = DZ / "납품/한비즈_DB광고1_A지시_1014"
SCENE_NAME = "a_direct"

# ── 메타판(10-14 사장님 «메타광고쪽이긴한데» → «위에 살짝 자르고 위치 맞춰서 덮어씌우지말고 버전 바꿔서 새로 뽑아줘 규격에맞게»)
#   메타 릴스 안전 영역(위 14% = 270 · 아래 35% = 670 → 내용은 y 270~1250, 양옆 65) — AD_VER=meta 로 켠다
#   사람 = 원본을 410px 위로 올려 구운 사본(위 벽만 잘림, 빈 아래는 책상 거울+흐림 — 메타 문구가 덮는 자리)
if os.environ.get("AD_VER") == "meta":
    SRC = DZ / "_tmp/src/1013_meta.mp4"
    WORK = DZ / "_tmp/a_meta"
    CAP_STYLE = dict(CAP_STYLE, y=730)                       # 1140 − 410
    CLOSEUP = {"t0": 21.688, "scale": 1.35, "pos": [121, 77]}  # 얼굴(450,510) → 화면(540,≈430), 턱 ≈538
    DELIV = DZ / "납품/한비즈_DB광고1_A지시_메타_1014"
    SCENE_NAME = "a_direct_meta"
CUT_ALL = None
# ── 메타v2(10-14 «엥 이건또 너무 높은거같은데 그냥 아까 내가 준 가이드라인에서 사진만 위쪽으로올리고 위에 잘라서 만들어줘 저런 흐림처리 이런거없어»
#   + «가이드라인으로 저 사진이 들어가게끔만 만들면돼 작게할필요도없고 그냥 저 사진위치랑 인물위치만 그대로 자른만큼 올려주면돼»)
#   사장님 프리미어 안전선 캡처의 안쪽 선(아래 끝 ≈1734) 기준 — 사람·자막·판·버튼을 똑같이 124px 위로(크기 그대로, 짝수 픽셀).
#   사람 = 원본 위 124px 를 자르고 올린 사본(빈 아래 124px 는 하얀 책상 앞면 줄을 그대로 늘림, 흐림 없음)
if os.environ.get("AD_VER") == "meta2":
    SRC = DZ / "_tmp/src/1013_v2.mp4"
    WORK = DZ / "_tmp/a_meta2"
    CAP_STYLE = dict(CAP_STYLE, y=1016)                       # 1140 − 124
    CLOSEUP = {"t0": 21.688, "scale": 1.35, "pos": [121, 0]}   # 얼굴(450,796) → 화면 (540,≈739), 턱 ≈846
    DELIV = DZ / "납품/한비즈_DB광고1_A지시_메타v2_1014"
    SCENE_NAME = "a_direct_meta2"


def plan():
    caps = json.loads((WORK / "captions.json").read_text(encoding="utf-8"))
    ev = json.loads((WORK / f"{SCENE_NAME}_events.json").read_text(encoding="utf-8"))["events"]
    sfx = sorted(({"t": round(e["t"], 3), "role": e["role"]} for e in ev if e.get("role") in ROLES), key=lambda s: s["t"])
    # 10-14 낱개 실측(지시작업/tools/sfxchk.py) — 들리는 정점이 화면보다 2프레임 넘게 어긋난 곳만 큐를 옮김
    NUDGE = {4.30: -0.15, 8.06: +0.077}   # 21.72 판 빠짐 소리는 10-14 «걱정마세요 할때 효과음이 살짝 빨리나와» → 장면 EVENTS 에서 21.84 로
    for x in sfx:
        x["t"] = round(x["t"] + NUDGE.get(x["t"], 0.0), 3)
    used = {s["role"] for s in sfx}
    deliv = DELIV / "_새판/media"   # 10-14 «1로 가고» — 옆에 다 만든 뒤 tools/deliver_swap.py 로 교체
    deliv.mkdir(parents=True, exist_ok=True)
    ovl = deliv / "자료층_A지시.mov"
    shutil.copy2(WORK / f"{SCENE_NAME}.mov", ovl)      # 10-14 «파일을 찾을 수 없다» — XML 은 납품 폴더 사본을 참조
    cuts = []
    for n, c in enumerate(items("V1")):
        cut = {"src": str(SRC), "in": c["s0"], "out": round(c["s0"] + (c["t1"] - c["t0"]), 6), "start": c["t0"], "end": c["t1"], "cont": n > 0}
        if abs(c["t0"] - CLOSEUP["t0"]) < 0.01:
            cut.update(scale=CLOSEUP["scale"], pos=CLOSEUP["pos"])
        elif CUT_ALL:
            cut.update(scale=CUT_ALL["scale"], pos=CUT_ALL["pos"])
        cuts.append(cut)
    p = {
        "name": "한비즈_DB광고1_A지시",
        "base_dir": str(ROOT),
        "seq": {"w": 1080, "h": 1920, "fps": FPS},
        "speed": 1.0,
        "loudness_lufs": -14,
        "voice": {"file": str(WORK / "voice.wav"), "start": 0.0},
        "bgm": {"file": str(BGM), "start": 0.0, "gain_db": BGM_DB, "fade_out": 1.0},
        "caption_style": CAP_STYLE,
        "script": [c["text"] for c in caps],
        "cuts": cuts,
        "captions": [{"text": c["text"], "start": c["start"], "end": c["end"], "emph": c["emph"], "emph_color": "y", "anim": "none"} for c in caps],
        "graphics": [],
        "overlays": [{"file": str(ovl), "t0": 0.0, "t1": SEQ_END, "name": "자료_A지시"}],
        "sfx_roles": {r: {"file": v[0], "align": v[1] or "peak", "exact_db": v[2], **({"min_len": v[3]} if len(v) > 3 else {})} for r, v in ROLES.items() if r in used},
        "sfx": sfx,
    }
    path = WORK / "plan_A지시.json"
    path.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(f"배치표 {path} — 효과음 {len(sfx)}개")


if __name__ == "__main__":
    main()
