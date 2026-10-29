# -*- coding: utf-8 -*-
r"""효과음 고르기·다듬기·크기 맞추기 (한비즈 쇼츠).

[이식본 — 원본 D:/영상제작/도구/광고편집/bisa_meta_sfx.py (고르기·다듬기 공용 부분) + bisa_toc_cards.by_name.
 빠진 것: 빡이사DB 01 장면 전용 EVENTS·main(). 바뀐 것: 경로는 config, 파일을 못 찾으면 SFX_LIB 에서 이름으로 찾음.]

쓰는 법 (장면 도구에서)
    import sfx as SFX
    SND_FIX = {"zoom": ("휙２.mp3", 0.6, 1, "peak"), ...}           # 역할 → (파일 이름, 최소 길이초, 기본 상대dB, 정렬)
    SFX.SND.update({k: SFX.role(SFX.by_name(f), mx, rel, al) for k, (f, mx, rel, al) in SND_FIX.items()})
    ref = SFX.voice_ref_from(voice_array)                            # 목소리 50ms RMS 중앙(dBFS)
    x, peak_at = SFX.prep("zoom", ref)                               # 다듬고 목소리 대비 크기로 맞춘 스테레오 배열
    SFX.write_wav(path, x)

기준(references/sfx.md)
  - 크기 = 목소리 «원음» 대비 dB. 파일별 값(FILE_DB)이 있으면 그것이 계기 기본값보다 우선.
  - 효과음은 자연히 잦아드는 데까지(최대 TAIL_MAX=2.5초), 끝 0.25초 페이드. 0.4~0.6초에서 잘라 끊지 않는다.
  - 고역 셈 → 5kHz 셸빙 −6dB, 순간음 → 앞 30ms 페이드인, 짧은 클릭 과증폭 방지 피크 −6dBFS 상한.
  - 프리미어 볼륨 저장값: 0dB = 0.17783 (ZERO_DB).
  - 크기 결정 순서: SND_FIX 의 rel → FILE_DB(파일별 표)가 덮음 → 역할별 예외(exact() 또는 5번째 값)가 다시 덮음.
    예) 녹화 화면 확대·풀림 휙은 파일 표(휙２ +4)보다 작게: ("휙２.mp3", 0.6, SFX.exact(SFX.ZOOM_DB), "peak")
  - 광고 사용 금지 폴더(EXCLUDE_DIRS = 모음1~6: 게임·방송 음원)는 find_file·by_name·pick 이 건너뛴다.
"""
import json
import math
import subprocess
import unicodedata
import wave
from pathlib import Path

import numpy as np

import config as C

SR = 48000
GRADE = C.GRADE_JSON
ORDER = {"A★": 0, "A": 1, "B": 2, "C": 3}
ZERO_DB = 0.177827941           # 프리미어 볼륨 저장값에서 0dB 에 해당하는 값(+15dB 여유). 1.0 을 0dB 로 읽으면 15dB 낮게 읽는다
TAIL_MAX = 2.5                  # 효과음 최대 길이(초)

# 파일별 크기(목소리 «원음» 대비 dB, 구워 넣는 값) — 사장님이 프리미어에서 맞춘 최종값(빡이사DB 04~06, 가로 강의 시퀀스에서 실측).
# = 구운 값 + 사장님 클립 볼륨. 사장님 타임라인 목소리(A1)는 +7dB 였으므로 들리는 크기(목소리 대비) = 이 값 − 7.
# 같은 파일이 여러 장면에 나오면 가장 최근 장면 값. ★ 세로 쇼츠에서는 첫 작업 때 사장님 편집에서 다시 재서 이 표를 고친다.
FILE_DB = {
    "휙２.mp3": 4, "휙1.mp3": 8,
    "채팅 효과음.mp3": 5, "ML_Cartoon bubbles popping.wav": 5,
    "KN_pepSound1.wav": 8, "KN_pepSound2.wav": 8,
    "맑은소리.mp3": 7, "SEL_ゲージ回復1.mp3": 12, "KN_error_003.wav": 5,
    "SEL_キラッ1.mp3": -1,
    "SEL_キーボード2.mp3": 6, "키보드.mp3": 8,
    "SEL_シャーペンで字を書く.mp3": 4,
}
FILE_DB_DEFAULT = 5             # 표에 없는 파일(일반)

ZOOM_DB = -6                    # 녹화 화면 확대·풀림 휙의 역할별 예외값(빡이사DB 05 — 사장님이 확대 휙２ 를 0dB 로 내리심 = 원음 −6)

# 말 있는 세로 쇼츠 광고 — 효과음 «들리는 크기»(50ms RMS 최대 − 목소리 말소리 50ms RMS 중앙, dB).
# 10-20 4번 볼륨 정리본에서 사장님 «지금 효과음 넣은거 이거 학습해 이 데시벨». 지시작업/tools/mix_audit.py --fix 가 이 값으로 맞춘다.
AD_LEVEL = {"impact": -2, "whoosh": -5, "small": -7}
AD_KIND_KEYS = {"impact": ("impact", "도장", "Glass", "둥", "쿠궁", "punch", "Boing", "쾅", "쿵"),
                "whoosh": ("휙", "sweep", "swoosh", "高速移動", "바람", "훅", "날아가는", "マント", "슉", "lowDown")}


def ad_kind(name):
    """파일 이름 → impact · whoosh · small(반짝·틱·종이·가위·클릭·코인 등)."""
    for k, keys in AD_KIND_KEYS.items():
        if any(s in name for s in keys):
            return k
    return "small"


def ad_target(name):
    return AD_LEVEL[ad_kind(name)]

# 사장님 라이브러리(다운효과음/모음N)에는 포켓몬·마리오·메이플·롤 같은 게임·방송 음원이 섞여 있다 — 광고 사용 금지(references/sfx.md 9장).
EXCLUDE_DIRS = tuple(f"모음{n}" for n in range(1, 7))

SND = {}                        # 역할 이름 → role() 튜플. 장면 도구가 채운다


def db(v):
    """프리미어 볼륨 저장값 → dB (0dB = 0.17783)."""
    return round(20 * math.log10(float(v) / ZERO_DB), 1)


class Exact(int):
    """«이 dB 그대로» 표시 — role() 이 FILE_DB(파일별 표)로 덮지 않는다. exact(-6) 으로 만든다."""


def exact(db_value):
    """역할별 dB 예외: SND_FIX 의 rel 자리에 exact(-6) 을 쓰면 FILE_DB 가 있는 파일이어도 -6 그대로."""
    return Exact(db_value)


def is_banned(path):
    """경로에 광고 사용 금지 폴더(모음1~6)가 들어 있으면 True. 한글 NFC/NFD 둘 다."""
    banned = {_nfc(d) for d in EXCLUDE_DIRS}
    return any(_nfc(part) in banned for part in Path(str(path)).parts)


def pick(cat, n, skip=(), new=None):
    """등급표에서 분류 cat 의 상위 n개(서로 다른 파일). A★ → A → B 순.
    skip = 뜻이 안 맞아 뺄 파일 이름 일부. new=True 면 SFX_LIB(받은 라이브러리)만, False 면 사장님 라이브러리만."""
    rs = [r for r in json.loads(GRADE.read_text(encoding="utf-8")) if r["분류"] == cat
          and not any(k in Path(r["파일"]).name for k in skip)
          and r.get("계열근거") != "소리추정(약함)"
          and not is_banned(r["파일"])
          and (new is None or ("예능효과음" in r["파일"]) == new)]
    rs.sort(key=lambda r: (ORDER[r["등급"]], -r["점수"]))
    return rs[:n]


def _nfc(s):
    return unicodedata.normalize("NFC", str(s))


def find_file(path_or_name):
    """등급표의 경로가 이 PC 에 없으면 이름으로 SFX_LIB · SFX_LIB_OWNER 에서 찾는다(한글 NFC/NFD 둘 다).
    EXCLUDE_DIRS(모음1~6) 아래 파일은 있어도 «없는 것»으로 친다 — 게임·방송 음원, 광고 사용 금지."""
    p = Path(str(path_or_name))
    if is_banned(p):
        raise FileNotFoundError(f"광고 사용 금지 폴더(모음1~6)의 파일: {p}")
    # 이 폴더 사본(소재/효과음)을 먼저 — 등급표의 절대경로는 원본 PC 경로라 독립 운영(10-08)에선 마지막 대안
    want = _nfc(p.name)
    for root in (C.SFX_LIB, C.SFX_LIB_OWNER, C.SFX_LIB_SCENE):
        if root.exists():
            for f in root.rglob("*"):
                if f.is_file() and _nfc(f.name) == want and not is_banned(f.relative_to(root)):
                    return f
    if p.exists():
        return p
    raise FileNotFoundError(f"효과음 파일을 못 찾음: {p.name} (SFX_LIB={C.SFX_LIB}, SFX_LIB_OWNER={C.SFX_LIB_OWNER}; 모음1~6 제외)")


def by_name(n):
    """파일 이름으로 등급표 행(없으면 라이브러리에서 찾아 임시 행)."""
    rs = json.loads(GRADE.read_text(encoding="utf-8"))
    r = next((r for r in rs if Path(r["파일"]).name == n), None)
    if r is None:                                          # 등급표 다시 돌리기 전 새로 받은 파일
        r = {"파일": str(find_file(n)), "소재상태": "통과", "등급": "-"}
    return r


def role(r, mx, rel, align, db=None):
    """등급표 행 → (파일, 최소길이초, 셸빙?, 페이드인ms, 상대dB, 정렬, 등급).
    크기 순서: rel(SND_FIX 값) → FILE_DB(파일별 표)가 덮음 → 역할별 예외가 다시 덮음.
      역할별 예외 = db 인자 또는 rel 자리에 exact(dB). (예: 녹화 화면 확대 휙 exact(ZOOM_DB))
    mx < 0 이면 «그 길이로 딱»(펜 소리처럼 동작 길이에 맞춰야 하는 소리)."""
    st = r["소재상태"]
    if db is not None:
        rel = int(db)
    elif isinstance(rel, Exact):
        rel = int(rel)
    else:
        rel = FILE_DB.get(Path(r["파일"]).name, rel)
    return (find_file(r["파일"]), mx, ("셸빙" in st) or ("고역 조금" in st), 30 if "페이드" in st else 0, rel, align, r["등급"])


def roles_from(snd_fix):
    """SND_FIX {역할: (파일 이름, 최소길이, 기본dB, 정렬[, 예외dB])} → {역할: role() 튜플}.
    5번째 값(예외dB)이 있으면 FILE_DB 를 무시하고 그 dB 그대로. 4-튜플은 기존과 같다."""
    out = {}
    for k, v in snd_fix.items():
        f, mx, rel, al = v[:4]
        out[k] = role(by_name(f), mx, rel, al, db=(v[4] if len(v) > 4 else None))
    return out


def load(path, shelf=False):
    af = ["aresample=48000", "aformat=sample_fmts=flt:channel_layouts=stereo"]
    if shelf:
        af.insert(0, "treble=g=-6:f=5000")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-af", ",".join(af), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def rms_frames(x, win=0.05):
    n = int(SR * win)
    m = x.mean(1)
    if len(m) < n:                       # 10-13 KN_tick(20~55ms)처럼 창보다 짧은 소리 — 빈 배열 오류 대신 무음을 덧대 한 창으로 잰다
        m = np.pad(m, (0, n - len(m)))
    m = m[: len(m) // n * n].reshape(-1, n)
    return 20 * np.log10(np.sqrt((m ** 2).mean(1)) + 1e-9)


def voice_ref_from(v):
    """목소리 배열(스테레오 float) → 말소리 50ms RMS 중앙(dBFS). 효과음 크기의 기준."""
    f = rms_frames(v)
    return float(np.median(f[f > f.max() - 25]))


def prep(name, ref):
    """SND[name] 을 다듬어 (스테레오 배열, 최대 크기 시각 초) 로. ref = voice_ref_from() 값."""
    fn, mx, shelf, fin, rel, _, _ = SND[name]
    x = load(fn, shelf)
    a = np.abs(x).max(1)
    st = int(np.argmax(a > a.max() * 10 ** (-40 / 20)))          # 앞 무음 제거
    x = x[st:]
    # 길이: 소리가 자연히 잦아드는 곳(최고점 −45dB)까지, 최대 TAIL_MAX초 · 최소 mx초.
    # 10-07 사장님 «효과음 또 짧게 끊기고» — 예전엔 mx(0.4~0.6초)에서 자르고 0.08초에 꺼서 뚝 끊겼다.
    e = np.abs(x).max(1)
    loud = np.where(e > e.max() * 10 ** (-45 / 20))[0]
    end = (loud[-1] + 1) if len(loud) else len(x)
    if mx < 0:                                                     # 음수 = 그 길이로 딱
        x = x[: int(-mx * SR)]
    else:
        x = x[: max(int(mx * SR), min(end, int(TAIL_MAX * SR)))]
    fo = min(len(x) // 3, int(0.25 * SR))                          # 꼬리 페이드아웃(부드럽게)
    x[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
    if fin:
        n = int(fin / 1000 * SR)
        x[:n] *= np.linspace(0, 1, n)[:, None]
    f = rms_frames(x)
    x *= 10 ** ((ref + rel - f.max()) / 20)
    x *= min(1.0, 0.5 / (np.abs(x).max() + 1e-9))   # 짧은 클릭은 50ms RMS 가 작게 잡혀 과증폭 → 피크 −6dBFS 상한
    peak_at = (int(np.argmax(f)) + 0.5) * 0.05
    return x, peak_at


CUT_LEAD = 0.010                # 다음 소리 들리는 어택 이만큼 전에 앞 소리를 끝낸다
CUT_FADE = 0.20                 # 끝내기 전 감쇠 길이(10-19 결정표 ④ — 60ms 는 촘촘하면 «들리는 중 잘림», 롱폼 10-15)
CUT_AUDIBLE = 0.12              # 들리는 끝(피크 −15dB)보다 이만큼 넘게 앞에서 끊기면 WARN
CUT_MIN = 0.15                  # 이보다 짧게 남으면 WARN — 큐를 옮긴다


def attack_at(x, db=-20):
    """들리는 시작(초) — 20ms RMS 가 최고점 −20dB 에 처음 닿는 곳(sfx.md 17-6)."""
    f = rms_frames(x, 0.02)
    return int(np.argmax(f >= f.max() + db)) * 0.02


def audible_end(x, db=-15):
    """들리는 끝(초) — 20ms RMS 가 최고점 −15dB 위인 마지막 곳."""
    f = rms_frames(x, 0.02)
    return (int(np.where(f >= f.max() + db)[0][-1]) + 1) * 0.02


def fit_tails(items):
    """겹침 0(10-19 «사장님 의도» 5) — items = [dict(t=시작초, x=배열, label=…)] 를 시각 순으로 보고,
    앞 소리가 다음 소리의 들리는 어택(−CUT_LEAD)까지 이어지면 거기서 끝나게 CUT_FADE 감쇠로 줄인다(x 를 바꿈).
    파일을 길이 상한으로 미리 자르지 않는다(결정표 ⑤) — 이 함수가 실제로 걸치는 것만 다듬는다.
    → [(수준, 규칙, 메시지)] (rule_check.report 형식). «들리는 중 잘림»·«0.15초 안 잘림»은 더 짧은 파일로 바꾸거나 큐를 옮길 곳."""
    out = []
    its = sorted(items, key=lambda d: d["t"])
    for a, b in zip(its, its[1:]):
        cut = b["t"] + attack_at(b["x"]) - CUT_LEAD - a["t"]
        if len(a["x"]) / SR <= cut:
            continue
        keep = max(0, int(cut * SR))
        ae = audible_end(a["x"])
        if keep / SR < ae - CUT_AUDIBLE:
            out.append(("WARN", "5-5 들리는 중 잘림", f"{a['label']} — {keep / SR:.2f}초에서 끊김(들리는 끝 {ae:.2f}초) · 다음 {b['label']} → 짧은 파일로 바꾸거나 큐를 옮긴다"))
        if keep / SR < CUT_MIN:
            out.append(("WARN", "5-5 0.15초 안 잘림", f"{a['label']} — {keep / SR:.2f}초만 남음 · 큐 배치 확인"))
        a["x"] = a["x"][:keep].copy()
        fo = min(len(a["x"]) // 2, int(CUT_FADE * SR))
        if fo:
            a["x"][-fo:] *= (np.linspace(1, 0, fo) ** 2)[:, None]
    return out


def write_wav(path, x):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
