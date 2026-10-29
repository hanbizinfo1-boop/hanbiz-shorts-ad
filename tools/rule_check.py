# -*- coding: utf-8 -*-
r"""[한비즈 쇼츠 이식본 — 원본 D:/영상제작/도구/점검/rule_check.py, 기준 문서 이름만 바꿈]
광고영상 규칙 점검기 — references/checklist.md 의 «납품 전 점검표»를 기계로 확인한다.

사장님 2026-09-28: «규칙 누락 현상 심함 → 길라잡이 만들 것», «점검기 만들어서 체크 루틴 넣어».
렌더 도구(rf3_render 등)가 렌더 전에 check_plan(), 소리 섞은 뒤 check_sfx() 를 부르고 report() 로 남긴다.
ERROR 가 하나라도 있으면 렌더 도구는 멈춘다(`--무시` 로만 통과).

화면 목록(shots) 한 칸 = dict(
    t0, t1,            초
    seg,               대본 구간 번호
    src,               소스 파일 경로(문자열) — 같은 파일이면 같은 소스
    kind,              "video" | "image" | "doc"(PDF 장표) | "black" | "grad" | "speed"
    tr,                들어올 때 전환 종류 — "cut" | "slide" | "fly" | "punch" | "move" | "push" …
    label=None,        화면에 보이는 타입명(예 "84A") — 타입을 말하는 줄이면 필수
    props=[],          얹은 소품 종류(prop/confetti/coins/x/stamp/big …)
)
직접 실행: python rule_check.py <work 폴더의 점검용 plan.json>
"""
import json
import re
import sys
from pathlib import Path

GUIDE = ".claude/skills/shorts-ad/references/checklist.md"
IMG_MIN, ANY_MIN, SCENE_MAX = 2.0, 1.0, 3.0
SFX_GAP = 2.5
SFX_REPEAT_MIN = 3.0   # 5-2b 같은 파일이 이 초 안에 다시 나오면 «짧은 주기»로 친다
SFX_ALT_MAX = 3        # 번갈아 쓰기는 짧은 주기 사슬에서 같은 파일 3번까지 허용 (사장님 10-02 «최대 3번까지는 번갈아사용가능»)
SFX_PER_EP_MAX = 2     # 5-4 쇼츠 한 편 같은 파일 2번까지 (숏폼 10-14 «효과음 그냥 너무 반복되는데?», sfx.md 결정표 ⑦). None = 안 봄(말 없는 타이포 등, 배치표에 사유)
BANNED_BG = {"black": "까만 화면", "grad": "그라데이션 카드", "speed": "집중선 검정 화면"}
BANNED_OV = {"prop": "이모티콘 소품", "confetti": "꽃가루", "coins": "금화", "x": "X 표시", "stamp": "도장", "site": "SITE·체크 표시",
             "big": "중복 자막(위에 큰 글자)", "title": "제목 띠 글자"}
TYPE_RE = re.compile(r"(\d{2,3}\s*타입|\b\d{2,3}[A-F]\b|평면|대형\s*평수|국평)")

# 모형(미니어처) 소스 — 사장님이 지정하지 않으면 쓰지 않는다 (규칙 1-2)
MODEL_DRONE = set(range(0, 7)) | set(range(232, 250))
MODEL_FILES = {"1-4.mp4", "1-5.mp4", "1-7.mp4", "1-11.mp4", "1-12.mp4"}


def is_model(src):
    p = Path(str(src))
    if p.name in MODEL_FILES:
        return True
    m = re.match(r"DJI_\d+_(\d{4})_D", p.stem)
    return bool(m) and int(m.group(1)) in _DJI_MODEL


_DJI_MODEL = set()   # DJI 파일 번호 → 드론 번호 매핑은 도구가 register_drone() 으로 넣는다


def register_drone(meta):
    """v5_render.META {드론 번호: 파일명} 를 받아 모형 드론 파일을 표시한다."""
    for i, f in meta.items():
        if i in MODEL_DRONE:
            m = re.match(r"DJI_\d+_(\d{4})_D", Path(f).stem)
            if m:
                _DJI_MODEL.add(int(m.group(1)))


def check_plan(shots, segs_text=(), model_ok=(), ref_lines=None):
    """화면 목록 점검 → [(수준, 규칙, 메시지)]."""
    out = []
    E = lambda r, m: out.append(("ERROR", r, m))   # noqa: E731
    Wn = lambda r, m: out.append(("WARN", r, m))   # noqa: E731
    at = lambda s: f"{s['t0']:5.2f}~{s['t1']:5.2f}s"  # noqa: E731
    # 1-1 같은 소스 두 번
    seen = {}
    for s in shots:
        if s["kind"] in ("video", "image", "doc"):
            seen.setdefault(str(s["src"]), []).append(s)
    for src, ss in seen.items():
        if len(ss) > 1:
            where = ", ".join(at(s) for s in ss)
            # 같은 장표 안에서 이어 옮겨 가는 샷(tr=move)은 한 번으로 본다
            real = [s for s in ss if not s.get("cont")]
            if len(real) > 1:
                E("1-1 같은 소스 중복", f"{Path(src).name} 가 {len(real)}번 — {where}")
    # 1-2 모형
    ok = {str(x) for x in model_ok}
    for s in shots:
        if s["kind"] in ("video", "image") and is_model(s["src"]) and str(s["src"]) not in ok and Path(str(s["src"])).name not in ok:
            E("1-2 모형 소재(지정 안 됨)", f"{at(s)} {Path(str(s['src'])).name}")
    # 1-4·1-5 금지 배경·소품, 4-2 중복 자막
    for s in shots:
        if s["kind"] in BANNED_BG:
            E("1-4 금지 화면", f"{at(s)} {BANNED_BG[s['kind']]}")
        for p in s.get("props", []):
            if p in BANNED_OV:
                E("1-5/4-2 금지 소품·글자", f"{at(s)} {BANNED_OV[p]}")
    # 1-8 타입명 표시
    for i, txt in enumerate(segs_text):
        if TYPE_RE.search(txt.replace("{", "").replace("}", "")):
            if not any(s.get("label") for s in shots if s["seg"] == i):
                E("1-8 타입명 표시 없음", f"구간 {i} «{txt.replace('|', ' ')}» — 화면에 84A 같은 타입명이 없다")
    # 1-9 첫 화면은 영상
    if shots and shots[0]["kind"] != "video":
        E("1-9 오프닝", f"첫 화면이 영상이 아니다 ({shots[0]['kind']})")
    # 2-1 시간 — 같은 자료 안에서 카메라만 옮겨 가는 이어진 샷(cont, 같은 src)은 한 번 보여 준 것으로 합쳐 잰다
    #   (2026-09-28 rf5: 84A·180A 한 장을 2.87초 보여 주며 84A → 180A 로 옮겨 가는 걸 1.3초 두 개로 잘못 셌다)
    runs = []
    for s in shots:
        if runs and s.get("cont") and str(s["src"]) == str(runs[-1]["src"]) and abs(s["t0"] - runs[-1]["t1"]) < 1e-3:
            runs[-1] = dict(runs[-1], t1=s["t1"])
        elif s.get("cont") and s.get("tr") is None:
            continue          # 위아래 분할의 소스별 칸(중복 검사용) — 길이는 본 칸에서 잰다
        else:
            runs.append(dict(s))
    for s in runs:
        d = s["t1"] - s["t0"]
        if s["kind"] in ("image", "doc") and d < IMG_MIN - 1e-6:
            E("2-1 자료 2초 미만", f"{at(s)} {d:.2f}초 {Path(str(s['src'])).name}")
        elif d < ANY_MIN - 1e-6:
            E("2-1 1초 미만 화면", f"{at(s)} {d:.2f}초 {Path(str(s['src'])).name}")
        elif s["kind"] == "video" and d > SCENE_MAX + 0.3:
            Wn("2-2 한 장면 3초 초과", f"{at(s)} {d:.2f}초 {Path(str(s['src'])).name}")
    # 3-1 같은 전환 연속
    for a, b in zip(shots, shots[1:]):
        if a.get("tr") and a.get("tr") == b.get("tr") and b["t0"] > 0:
            E("3-1 같은 전환 연속", f"{at(a)} → {at(b)} 둘 다 «{b['tr']}»")
    # 4-1 자막 원문 대조
    if ref_lines is not None:
        norm = lambda x: re.sub(r"[\s|{}.,!?~·…]", "", x)  # noqa: E731
        ref = norm("".join(ref_lines))
        got = norm("".join(segs_text))
        if ref != got:
            k = next((i for i, (x, y) in enumerate(zip(ref, got)) if x != y), min(len(ref), len(got)))
            E("4-1 자막 ≠ 원문", f"원문 «…{ref[max(0, k - 8):k + 8]}…» / 자막 «…{got[max(0, k - 8):k + 8]}…»")
    return out


def check_sfx(events, total, bed_intervals=None, per_ep_max=SFX_PER_EP_MAX):
    """events = [(초, 파일, 길이초[, 연타 사유])] — 3-튜플 이상(2-튜플은 ERROR, sfx.md 16장 ⑤). 5-2 같은 효과음 연속, 5-2b 짧은 주기 반복, 5-3 빈 구간,
    5-4 한 편 같은 파일 per_ep_max 번 초과. 넷째 값(사유 글)이 있는 발은 사장님이 시킨 연타(박수 3연타 등)로 보고 5-2·5-2b·5-4 에서 뺀다(결정표 ⑦).
    길이가 있으면 5-3 은 «소리가 실제로 안 나는 시간»(앞 소리 끝 → 다음 소리 시작)으로 잰다(10-07 — 시작 간격만 세면
    빈칸 메우려 요소를 끼워 넣어 장면이 급해진다, 사장님 «연출이 전체적으로 급해서 정신없는 느낌»).
    bed_intervals = [(시작, 끝), …] 선택 — BGM 처럼 계속 깔리는 소리의 구간. 이 안의 빈 시간은 5-3 에서 «소리 있음»으로 쳐서 뺀다
    (BGM 이 깔린 모션그래픽·타이포는 효과음 사이를 채우지 않는다, sfx.md 17장). 안 주면 예전과 같다."""
    out = []
    two = [e for e in events if len(e) < 3]
    if two:                                   # sfx.md 16장 ⑤ — 시작 간격만 세면 빈칸을 요소로 메우려 해 장면이 급해진다(10-07)
        out.append(("ERROR", "5-3 효과음 2-튜플", f"3-튜플(시작·파일·길이)만 — sfx.md 16장 ⑤ (2-튜플 {len(two)}개, 처음 {two[0][0]:.2f}s {Path(str(two[0][1])).name})"))
    events = [e for e in events if len(e) >= 3] or events
    dur = {(e[0], str(e[1])): e[2] for e in events if len(e) > 2}
    burst = {(e[0], str(e[1])) for e in events if len(e) > 3 and e[3]}
    ev = sorted((e[0], e[1]) for e in events)
    if per_ep_max:
        cnt = {}
        for t, f in ev:
            if (t, str(f)) not in burst:
                cnt.setdefault(Path(str(f)).name, []).append(t)
        for f, ts in cnt.items():
            if len(ts) > per_ep_max:
                out.append(("ERROR", "5-4 한 편 같은 효과음 반복", f"{f} {len(ts)}번({', '.join(f'{x:.2f}s' for x in ts)}) — 한 편 {per_ep_max}번까지, 결이 비슷한 다른 파일로"))
    for (t1, f1), (t2, f2) in zip(ev, ev[1:]):
        if f1 == f2 and (t2, str(f2)) not in burst:
            out.append(("ERROR", "5-2 같은 효과음 연속", f"{t1:5.2f}s · {t2:5.2f}s {Path(str(f1)).name}"))
    last, chain = {}, {}
    for t, f in ev:                           # 5-2b 번갈아 쓰기는 같은 파일이 짧은 주기로 3번까지만 (사장님 10-02)
        if (t, str(f)) in burst:
            continue
        chain[f] = chain.get(f, 0) + 1 if f in last and 0 < t - last[f] < SFX_REPEAT_MIN else 1
        if chain[f] > SFX_ALT_MAX:
            out.append(("ERROR", "5-2b 같은 효과음 짧은 주기 반복", f"{t:5.2f}s {Path(str(f)).name} — {SFX_REPEAT_MIN:.0f}초 간격 안에 {chain[f]}번째"))
        last[f] = t
    end = 0.0
    beds = sorted((a, b) for a, b in (bed_intervals or []) if b > a)
    for t, f in ev + [(total, None)]:
        if t - end > SFX_GAP:
            if not beds:
                out.append(("ERROR", "5-3 효과음 빈 구간", f"{end:5.2f}~{t:5.2f}s ({t - end:.1f}초)"))
            else:                                 # 깔린 소리(BGM) 구간을 뺀 «실제 무음» 토막마다 잰다
                cur = end
                holes = []
                for a, b in beds:
                    if b <= cur:
                        continue
                    if a >= t:
                        break
                    if a > cur:
                        holes.append((cur, min(a, t)))
                    cur = max(cur, b)
                if cur < t:
                    holes.append((cur, t))
                for h0, h1 in holes:
                    if h1 - h0 > SFX_GAP:
                        out.append(("ERROR", "5-3 효과음 빈 구간", f"{h0:5.2f}~{h1:5.2f}s ({h1 - h0:.1f}초, BGM 구간 제외)"))
        if f is not None:
            end = max(end, t + dur.get((t, str(f)), 0.0))
    return out


# 17-4 소리 가족: 정책자금(정보·신뢰) 모션그래픽·타이포에 게임·마법·코믹 소리 금지 (10-12)
# 단 사장님 실사용 통과 파일(10-02 02 목차 «좋아»)은 이름이 걸려도 뺀다 — 10-19 결정표: 통과 이력이 계열 금지보다 먼저
TONE_OK = {"SEL_キラッ1.mp3", "ML_Cartoon bubbles popping.wav"}
TONE_BAN = ("魔法", "キラ", "Magic", "Fairy", "Cartoon", "arcade", "Arcade", "game", "Game", "funny", "Funny",
            "SYN_", "marimba", "Marimba", "xylo", "Xylo", "glock")   # 10-12 «실리폰소리 되게 듣기싫» — 음정 톤(합성 마림바·벨 포함) 금지


def check_tone(files):
    """files: 파일 이름 목록 → 17-4 금지 계열이면 ERROR."""
    out = []
    for f in sorted(set(map(str, files))):
        if Path(f).name in TONE_OK:
            continue
        hit = [k for k in TONE_BAN if k in f]
        if hit:
            out.append(("ERROR", "17-4 소리 가족", f"{f} — {hit[0]} 계열(게임·마법·코믹·실로폰/마림바 음정 톤)은 한비즈 모션그래픽·타이포에 쓰지 않는다"))
    return out


# 광고 문구(references/copy.md) — 계약·표시광고 위험 말과 «시청자에게 계산 시키기»를 찾는다. 사장님 확정 문구일 수 있어 WARN 만(보고에 적고 사장님께 여쭌다)
COPY_BAN = [
    (r"무조건|100\s*%|보장|확정(?!된\s*대본)|\d[\d,.]*\s*(?:억|만\s*원|만원)\s*이상\s*(?:받|나와|드|가능)", "승인·금액 보장으로 들림(계약 조건)"),
    (r"받아\s*드|받아드|대출\s*(해|받아)\s*(드|줘)|연결해\s*드", "대출 중개·대행처럼 들림(계약 조건 · 붙임2)"),
    (r"오늘만|마감\s*임박|소진이?\s*(엄청|빠르|곧)|서두르", "조급하게 만드는 말(근거 없으면 공고 원문 «예산 소진 시까지»)"),
    (r"(수수료|돈|비용)\s*(를|을)?\s*안\s*받", "«돈 안 받는다» 그대로 금지 → «대출 나왔다고 바로 성공보수를 받지 않습니다»(10-08 확정)"),
]
NUM_RE = re.compile(r"\d[\d,.]*\s*(?:%|조|억|천|만|원|년|개월|배|곳|명)")


def check_copy(lines):
    """lines: 대사·화면 글 줄 목록 → [(WARN, 규칙, 메시지)]. 10-12 «너무 어렵대 … 시청자가 계산하게 시키는거자체가 안읽히는 광고»."""
    out = []
    for i, ln in enumerate(lines, 1):
        for pat, why in COPY_BAN:
            m = re.search(pat, ln)
            if m:
                out.append(("WARN", "copy 금지어", f"{i}행 «{m.group(0)}» — {why}: {ln.strip()[:60]}"))
        n = len(NUM_RE.findall(ln))
        if n >= 2:
            out.append(("WARN", "copy 숫자 하나", f"{i}행 숫자 {n}개 — 한 문장에 결과 숫자 하나, 비교·계산을 시청자에게 시키지 않는다: {ln.strip()[:60]}"))
    return out


def report(items, path=None, title=""):
    err = [x for x in items if x[0] == "ERROR"]
    lines = [f"규칙 점검 {title} — ERROR {len(err)} · WARN {len(items) - len(err)}  (기준: {GUIDE})"]
    lines += [f"  [{lv}] {r}: {m}" for lv, r, m in items] or ["  통과"]
    txt = "\n".join(lines)
    print(txt, flush=True)
    if path:
        Path(path).write_text(txt + "\n", encoding="utf-8")
    return len(err)


if __name__ == "__main__":
    if sys.argv[1] == "--copy":   # python tools/rule_check.py --copy 대본.txt  (한 줄 = 대사·화면 글 하나)
        report(check_copy(Path(sys.argv[2]).read_text(encoding="utf-8").splitlines()), title="광고 문구")
        sys.exit(0)
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    n = report(check_plan(d["shots"], d.get("segs_text", []), d.get("model_ok", []), d.get("ref_lines")))
    sys.exit(1 if n else 0)
