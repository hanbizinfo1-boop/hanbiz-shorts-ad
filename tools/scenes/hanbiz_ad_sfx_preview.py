# -*- coding: utf-8 -*-
r"""한비즈 광고 «소리 미리듣기» — 효과음 큐시트(JSON) → BGM + 효과음만 든 오디오 (영상 렌더 전에 소리 설계를 먼저 듣는다).

    python tools/scenes/hanbiz_ad_sfx_preview.py --cue 기록/효과음큐_3안_1012.json \
        --out 납품/효과음준비_1012 --name 3안_소리미리듣기 --length 26 \
        --beats 기록/BGM_박자표_1012.json --beat-key 3안

큐 JSON 형식: bgm{file, start_in_track, volume_curve[{t,db}], end, logo_db} · cues[{t, role, file, db, align(onset|peak), event}]
  - BGM: start_in_track 부터 잘라 volume_curve(점마다 «그 시각에 도달하는» 0.15초 램프) 적용. logo_db 가 있으면 logo_ending 큐 시각부터 그 dB.
         끝 = 마지막 1.0초 페이드 + 0.6초 무음 (큐의 end 문구와 같은 규칙). BGM EQ·덕킹은 나레이션이 없어 끈다(sfx.md 15장 4~6단계 생략).
  - 효과음: sfx.find_file → sfx.role/prep 엔진(자연 길이·셸빙·페이드). 크기 = hanbiz_logo_sfx 와 같은 가상 기준(REF −20 dBFS + PREP_OFFSET) + 큐의 db 를 역할 상대값으로.
  - role == logo_ending: 납품/시안_로고엔딩_1008/효과음_낱개/레이저_0N_*.wav 6개를 레이저 엔딩 내부 시각(hanbiz_logo_sfx 의 laser 프리셋 + _tmp/laser/laser_events.json)대로 t 부터 배치.
  - 마감: 마스터 컴프 → −14 LUFS → 트루피크 −1.5 dBTP 이하. BGM 대 효과음 균형은 --bgm-db (효과음 기준 −30 dBFS 에 대한 BGM 중앙 RMS 상대값, 기본 −10).

만드는 것 (out)
  <name>.mp3(192k) · <name>_합본.wav · <name>_낱개/NN_<역할>.wav(마스터 게인 반영) + 00_BGM.wav · <name>_점검.txt
  영상이 없어 프리미어 XML(lec_xml 은 영상 클립을 전제)은 만들지 않는다 — 낱개 wav 와 큐 시각표(점검 txt)가 같은 일을 한다.
소리는 귀로 확인하지 못했다 — 점검 txt 에도 그렇게 적는다.
"""
import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import config as C  # noqa: E402
import rule_check as RC  # noqa: E402
import sfx as SFX  # noqa: E402
import hanbiz_logo_sfx as HL  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SR = SFX.SR
FRAME_DT = 1001 / 30000
REF_DBFS = HL.REF_DBFS
PREP_OFFSET = HL.PREP_OFFSET
TARGET_LUFS = HL.TARGET_LUFS
TP_MAX = HL.TP_MAX
RAMP = 0.15                      # 볼륨 곡선 점 사이 램프(초)
END_FADE_BGM = 1.0               # BGM 마지막 페이드
END_SILENCE = 0.6                # 그 뒤 무음
MIX_END_FADE = 0.2               # 합본 끝에서 뚝 끊기지 않게
MIN_LEN = 0.5                    # sfx.prep 의 최소 길이(초) — 큐 JSON 에 길이가 없어 한 값으로
LASER_DIR = C.ROOT / "납품" / "시안_로고엔딩_1008" / "효과음_낱개"
LASER_EVENTS = C.WORK / "laser" / "laser_events.json"


_load_orig = SFX.load


def _load_padded(path, shelf=False):
    """KN_tick 처럼 50ms 보다 짧은 파일은 sfx.prep 의 50ms RMS 창이 비어 죽는다 — 뒤에 무음을 붙여 0.1초로(소리 자체는 그대로)."""
    x = _load_orig(path, shelf)
    need = int(0.1 * SR)
    return x if len(x) >= need else np.vstack([x, np.zeros((need - len(x), 2), np.float32)])


SFX.load = _load_padded


def rp(p):
    p = Path(p)
    return p if p.is_absolute() else C.ROOT / p


def decode(path, ss, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ss}", "-t", f"{t}", "-i", str(path), "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def rms_db(x, a, b):
    seg = x[int(a * SR):int(b * SR)]
    if len(seg) == 0:
        return float("nan")
    return 20 * math.log10(math.sqrt(float((seg.mean(1) ** 2).mean())) + 1e-9)


def bed_envelope(n, knots):
    """knots [(초, dB)] → 샘플별 선형 게인."""
    t = np.arange(n) / SR
    ks = sorted(knots)
    return 10 ** (np.interp(t, [k[0] for k in ks], [k[1] for k in ks]) / 20)


def curve_knots(curve, logo_t, logo_db):
    ks = []
    prev = None
    for p in sorted(curve, key=lambda p: p["t"]):
        if prev is not None:
            ks.append((max(0.0, p["t"] - p.get("ramp", RAMP)), prev))  # 점마다 "ramp" 로 바꿀 수 있다(드롭 직전 비움 = 0.01)
        ks.append((p["t"], p["db"]))
        prev = p["db"]
    if not ks:
        ks = [(0.0, 0.0)]
        prev = 0.0
    if logo_db is not None and logo_t is not None:
        ks.append((max(0.0, logo_t - RAMP), prev))
        ks.append((logo_t, logo_db))
    return ks


# ── 효과음을 «음악 위로 톡 튀어나오게» (10-12 사장님 «효과음이 너무 작고 효과음볼륨도 제각각이야 뭔가 음악에서 톡톡 툭툭 효과음이 튀어나와야하는데 그맛이없어»)
# 실측: 3판까지 효과음 순간 크기가 그 자리 BGM 보다 중앙 −2.9dB, 소리끼리 폭 26dB → 묻히고 제각각.
# 해법: ① 소리마다 «들리는 크기»(K 가중 근사 · 400ms 창 최대 RMS)를 재서 그 자리 BGM(같은 가중 · 앞 0.3초~뒤 0.7초 중앙) + 단계 값으로 맞춘다
#       ② 단계는 3개만 — 타격 +8 · 보통 +5 · 쓸림(휙·흡입·바람) +1 dB (큐 db 는 단계 안 미세 조정으로 ±2dB 까지만)
#       ③ 효과음이 날 때마다 BGM 을 순간 −4dB (10ms 내려가 0.12초 버팀 → 0.18초에 복귀) — 쓸림은 덕킹 안 함
TIER_DB = {"hit": 8.0, "mid": 5.0, "soft": 1.0}
SOFT_ROLES = {"swipe", "suck", "wipe", "stamp_move", "gather", "zoom_in", "underline2", "strike_whoosh"}
HIT_ROLES = {"hit_big_low", "stamp", "thump_light", "count", "doc_slam", "fill_in", "positive", "button"}
DUCK_DB, DUCK_HOLD, DUCK_REL = -4.0, 0.12, 0.18


def tier_of(c):
    if c.get("tier"):
        return c["tier"]
    r = c["role"]
    return "soft" if r in SOFT_ROLES else "hit" if r in HIT_ROLES else "mid"


def kw_mono(x):
    """K 가중 근사(고역 통과 60Hz + 1.5kHz 위 +4dB) — ebur128 과 같은 결의 «들리는 크기»."""
    st = x if x.ndim == 2 else np.stack([x, x], axis=1)            # ff_array 는 스테레오만 받는다
    return HL.ff_array(st.astype(np.float32), "highpass=f=60,treble=g=4:f=1500").mean(axis=1)


def mom_max(x, win=0.4):
    n = int(win * SR)
    y = np.concatenate([np.asarray(x, np.float64).ravel(), np.zeros(n)])
    c = np.cumsum(np.concatenate([[0.0], y * y]))
    r = (c[n:] - c[:-n]) / n
    return 10 * math.log10(float(r.max()) + 1e-12)


def mom_med(x, t0, t1, win=0.4):
    n = int(win * SR)
    seg = np.asarray(x[max(0, int(t0 * SR)):int(t1 * SR)], np.float64).ravel()
    if len(seg) <= n:
        return -60.0
    c = np.cumsum(np.concatenate([[0.0], seg * seg]))
    r = (c[n:] - c[:-n]) / n
    return 10 * math.log10(float(np.median(r)) + 1e-12)


def match_to_bed(items, cues_by_t, bed):
    """items 의 x 를 그 자리 BGM 대비 단계 값으로 맞춘다. 반환: 기록 줄."""
    bk = kw_mono(bed)
    glob = mom_med(bk, 0, len(bk) / SR)
    log = []
    for r in items:
        if r["role"] == "logo_ending":
            continue
        c = cues_by_t.get((round(r["t"], 3), r["file"]), {})
        tier = tier_of(c or {"role": r["role"]})
        fine = max(-2.0, min(2.0, (c.get("db", 0) + 4) * 0.25)) if c else 0.0     # 큐 db 는 미세 조정만(±2)
        local = max(mom_med(bk, max(0.0, r["start"] - 0.3), r["start"] + 0.7), glob - 6.0)
        x0 = r["x"]; st = x0 if x0.ndim == 2 else np.stack([x0, x0], axis=1)
        st = HL.ff_array((st / (np.abs(st).max() + 1e-9) * 0.5).astype(np.float32), "acompressor=threshold=0.06:ratio=8:attack=0.2:release=40:knee=2")  # 뾰족한 머리를 깎아(크레스트↓) 마스터 리미터에 짓눌리지 않게
        r["x"] = (st if x0.ndim == 2 else st.mean(axis=1)).astype(np.float32)
        have = mom_max(kw_mono(r["x"]), win=0.05)          # 효과음은 짧은 창(50ms) — 짧은 클릭이 400ms 창에서 과소평가돼 과증폭되던 것 막음
        g = local + TIER_DB[tier] + fine - have
        r["x"] = (r["x"] * 10 ** (g / 20)).astype(np.float32)
        r["tier"], r["match_db"] = tier, g
        log.append(f"  {r['start']:6.3f}s {r['role']:<12} {tier:<4} BGM {local:6.1f} → 목표 {local + TIER_DB[tier] + fine:6.1f} (소리 {have:6.1f}, 이득 {g:+5.1f} dB)")
    return log


def duck_env(n, items):
    env = np.ones(n, np.float32)
    t = np.arange(n) / SR
    for r in items:
        if r["role"] == "logo_ending" or r.get("tier") == "soft":
            continue
        s0 = r["start"]
        a = np.clip((t - s0) / 0.01, 0, 1)
        rel = np.clip((t - s0 - DUCK_HOLD) / DUCK_REL, 0, 1)
        d = 1 - (1 - 10 ** (DUCK_DB / 20)) * a * (1 - rel)
        d[t < s0] = 1.0
        env = np.minimum(env, d.astype(np.float32))
    return env


def build_bed(cue, length, bgm_db):
    b = cue["bgm"]
    src = rp(b["file"])
    raw = decode(src, b.get("start_in_track", 0.0), length + 0.5)
    n = int(round(length * SR))
    raw = raw[:n] if len(raw) >= n else np.vstack([raw, np.zeros((n - len(raw), 2), np.float32)])
    f = SFX.rms_frames(raw)
    mid = float(np.median(f[f > f.max() - 25]))
    target = REF_DBFS + PREP_OFFSET + bgm_db
    raw_n = raw * 10 ** ((target - mid) / 20)
    logo = next((c for c in cue["cues"] if c["role"] == "logo_ending"), None)
    knots = curve_knots(b.get("volume_curve", []), logo["t"] if logo else None, b.get("logo_db"))
    env = bed_envelope(n, knots)
    t = np.arange(n) / SR
    f0, f1 = length - END_SILENCE - END_FADE_BGM, length - END_SILENCE
    fade = np.clip(1 - (t - f0) / END_FADE_BGM, 0, 1) ** 2
    fade[t >= f1] = 0.0
    bed = raw_n * (env * fade)[:, None]
    return raw_n, bed.astype(np.float32), knots, (mid, target, src)


def onset_times(x):
    """모노 에너지 상승(5ms 격자)의 시각열 — 박 위치 측정용. 반환 (시각 배열, 상승량 배열)."""
    m = x.mean(1)
    hop = int(0.005 * SR)
    k = len(m) // hop
    e = np.sqrt((m[: k * hop].reshape(k, hop) ** 2).mean(1)) + 1e-7
    le = 20 * np.log10(e)
    d = np.diff(le, prepend=le[0])
    d[d < 0] = 0
    d = d[:-2] + d[1:-1] + d[2:] if len(d) > 3 else d             # 15ms 합
    return (np.arange(len(d)) + 1) * 0.005, d


def onset_peaks(raw, min_rise=6.0):
    """에너지 상승 국소 최댓값(±60ms 안에서 최대, 상승 min_rise dB 이상) → [(시각, 상승 dB)]."""
    ts, d = onset_times(raw)
    w = 12
    pk = []
    for i in range(len(d)):
        if d[i] >= min_rise and d[i] >= d[max(0, i - w):i + w + 1].max():
            if pk and ts[i] - pk[-1][0] < 0.03:                      # 같은 상승이 두 칸에 걸친 경우
                continue
            pk.append((float(ts[i]), float(d[i])))
    return pk


def beat_report(cues, raw, start_in_track, beats):
    """큐 시각마다 ±0.2초 안에서 가장 가까운 실제 onset(상승 6dB 이상)과 그 근처 가장 센 onset 을 잰다. ±1프레임 판정은 «가장 가까운 것» 기준.
    곡이 16분음표까지 촘촘해 격자 박 기준 매칭은 의미가 없다 — 큐 시각 기준으로 본다. 박자표의 마디 시작(downbeats)도 따로 대조."""
    pk = onset_peaks(raw)
    L = []
    n_ok = n_all = 0
    for c in cues:
        t = c["t"]
        near = [(abs(o - t), o, v) for o, v in pk if abs(o - t) <= 0.2]
        if not near:
            L.append(f"  {t:7.3f}s {c['role']:12s} | ±0.2초 안에 상승 6dB 이상 onset 없음 | 판정 불가")
            continue
        _, o, v = min(near)
        big = max(((v2, o2) for _, o2, v2 in near if abs(o2 - t) <= 0.1), default=None)
        dfr = (o - t) / FRAME_DT
        n_all += 1
        ok = abs(dfr) <= 1.0
        n_ok += ok
        L.append(f"  {t:7.3f}s {c['role']:12s} | 가장 가까운 onset {o:7.3f}s (상승 {v:.1f}dB) → onset−큐 {dfr:+.1f}f | {'±1f 안' if ok else '±1f 밖'}"
                 + (f" | ±0.1초 안 최강 {big[1]:.3f}s ({big[0]:.1f}dB)" if big else ""))
    L.append("  박자표 마디 시작(downbeats)의 광고 시각 대 실제 onset (박자표 값이 실제 곡과 얼마나 맞는지):")
    for d0 in beats.get("downbeats", []):
        t = d0 - start_in_track
        if t < -0.2 or t > raw.shape[0] / SR - 0.2:
            continue
        near = [(abs(o - t), o, v) for o, v in pk if abs(o - t) <= 0.2]
        if near:
            _, o, v = min(near)
            L.append(f"    마디 시작 {t:7.3f}s | 가장 가까운 onset {o:7.3f}s ({v:.1f}dB) → {(o - t) / FRAME_DT:+.1f}f")
        else:
            L.append(f"    마디 시작 {t:7.3f}s | ±0.2초 안 onset 없음")
    return L, n_ok, n_all


def run(a):
    cue = json.loads(rp(a.cue).read_text(encoding="utf-8"))
    out = rp(a.out)
    out.mkdir(parents=True, exist_ok=True)
    nick = out / f"{a.name}_낱개"
    nick.mkdir(parents=True, exist_ok=True)
    cues = sorted(cue["cues"], key=lambda c: c["t"])
    length = a.length if a.length else math.ceil(max(c["t"] for c in cues) + 2.3)
    n = int(round(length * SR))

    raw_bed, bed, knots, (bed_mid, bed_target, bed_src) = build_bed(cue, length, a.bgm_db)

    # 효과음 다듬기 ----------------------------------------------------------------
    items = []                      # 믹스에 얹을 것: dict(t, start, role, file, x, len, db, align, note, ref)
    sounds = {}
    for i, c in enumerate(cues):
        if c["role"] == "logo_ending":
            continue
        name = f"c{i}"
        sounds[name] = SFX.role(SFX.by_name(c["file"]), c.get("mx", MIN_LEN), c["db"], c["align"], db=int(c["db"]))  # 큐에 "mx": -초 면 그 길이로 딱(타자처럼 동작 길이에 맞출 소리)
    SFX.SND.update(sounds)
    for i, c in enumerate(cues):
        if c["role"] == "logo_ending":
            continue
        name = f"c{i}"
        x, peak_at = SFX.prep(name, REF_DBFS + PREP_OFFSET)
        start = c["t"] - (peak_at if c["align"] == "peak" else 0.0)
        note = "시작이 0초 앞이라 0초로 당김" if start < 0 else ""
        start = max(0.0, start)
        items.append({"t": c["t"], "start": start, "role": c["role"], "file": Path(c["file"]).name, "x": x, "len": len(x) / SR,
                      "db": c["db"], "align": c["align"], "peak_at": peak_at, "event": c.get("event", ""), "note": note})

    laser_note = []
    for c in cues:
        if c["role"] != "logo_ending":
            continue
        if not LASER_EVENTS.exists():
            raise SystemExit(f"레이저 엔딩 내부 시각을 못 찾음: {LASER_EVENTS}")
        lc = HL.build_cues(HL.PRESETS["laser"], LASER_EVENTS, 5.0)        # 엔딩을 만들 때 쓴 큐(내부 시각 · 정렬 포함)
        for k, q in enumerate(lc, 1):
            wavp = LASER_DIR / f"레이저_{k:02d}_{q['snd']}.wav"
            if not wavp.exists():
                raise SystemExit(f"레이저 낱개 wav 없음: {wavp}")
            w = SFX.load(wavp)
            g = math.sqrt(float((w ** 2).mean()) / (float((q["x"] ** 2).mean()) + 1e-12))     # 그 엔딩 마스터 게인(선형) 추정
            x = (w / g) * 10 ** (c.get("db", 0) / 20)
            laser_note.append(f"레이저_{k:02d}_{q['snd']}: 낱개 wav 에서 마스터 게인 약 {20 * math.log10(g):+.1f} dB 를 되돌려 가상 기준으로 환산")
            items.append({"t": c["t"] + q["want"], "start": c["t"] + q["start"], "role": "logo_ending", "file": wavp.name, "x": x.astype(np.float32),
                          "len": len(x) / SR, "db": c.get("db", 0), "align": q["align"], "peak_at": q["peak_at"],
                          "event": f"{c.get('event', '')} / 엔딩 내부 {q['event']} {q['t']:.2f}s", "note": ""})
    items.sort(key=lambda r: (r["start"], r["file"]))

    # 음악 대비 크기 맞춤 + 순간 덕킹 (a.match) ----------------------------------------
    match_log = []
    sync_log = []
    if a.match:
        cues_by_t = {(round(c["t"], 3), Path(c["file"]).name): c for c in cues if c["role"] != "logo_ending"}
        match_log = match_to_bed(items, cues_by_t, bed)
        # 들리는 시각 맞춤 (10-13 사장님 «효과음이 겹치거나 밀려서 나오는거 조정해서 깔끔하고 자연스럽게») ----------
        # 파일 앞쪽에 서서히 올라오는 부분이 있으면 귀에 «때리는» 순간이 큐보다 늦다 → 실제 엔벨로프로 다시 잼:
        # onset = 피크 대비 −20dB 첫 도달, peak = 엔벨로프 최대. 그 순간이 큐 시각에 오도록 시작을 옮긴다(tools/sfx_audit.py 와 같은 기준).
        sync_log = []
        for r in items:
            if r["role"] == "logo_ending":
                continue
            ref = audible_ref(r["x"], r["align"])
            want = r["t"] - ref
            # 여러 번 치는 소리(타자·연타)는 첫 타를 큐에 — 앞당김은 최대 80ms, 피크 보정은 ±120ms 안에서만
            lo, hi = (r["start"] - 0.08, r["start"]) if r["align"] != "peak" else (r["start"] - 0.12, r["start"] + 0.12)
            new = max(0.0, min(hi, max(lo, want)))
            if abs(new - r["start"]) > 0.004:
                sync_log.append(f"  {r['t']:6.3f}s {r['role']:<12} {r['align']:<5} 시작 {r['start']:.3f} → {new:.3f} ({(new - r['start']) * 1000:+.0f}ms) {r['file']}")
            r["start"] = new
        items.sort(key=lambda r: (r["start"], r["file"]))
        bed = (bed * duck_env(len(bed), items)[:, None]).astype(np.float32)

    # 겹침 끊기 (10-12 사장님 «효과음 겹치는부분때문에 듣기싫어 … 겹치는 부분 꽤많음») -------------------------
    # 다음 효과음이 들리기 10ms 전에 앞 효과음이 끝나게 0.2초 감쇠(10-19 sfx.md 결정표 ④ — ~~25ms·60ms~~ 는 촘촘하면 «들리는 중 잘림»).
    # 들리는 끝보다 0.12초 넘게 앞에서 끊기거나 0.15초도 안 남으면 경고 → 짧은 파일로 바꾸거나 큐를 옮긴다. 레이저 엔딩 낱개끼리는 엔딩 원본 설계 그대로 둔다.
    cut_log, chk_fit = [], []
    seq = sorted(items, key=lambda r: r["start"])
    for k, cur in enumerate(seq):
        nxt = next((q for q in seq[k + 1:] if not (cur["role"] == "logo_ending" and q["role"] == "logo_ending")), None)
        if nxt is None:
            continue
        room = nxt["start"] + audible_ref(nxt["x"], "onset") - cur["start"] - 0.010   # 다음 소리가 들리기 시작하기 10ms 전까지
        if cur["len"] > room:
            n_keep = max(int(0.05 * SR), int(room * SR))
            xs = cur["x"] if cur["x"].ndim == 2 else cur["x"][:, None]
            ae = SFX.audible_end(xs)
            if n_keep / SR < ae - SFX.CUT_AUDIBLE:
                chk_fit.append(("WARN", "5-5 들리는 중 잘림", f"{cur['start']:.3f}s {cur['file']} — {n_keep / SR:.2f}초에서 끊김(들리는 끝 {ae:.2f}초)"))
            if n_keep / SR < SFX.CUT_MIN:
                chk_fit.append(("WARN", "5-5 0.15초 안 잘림", f"{cur['start']:.3f}s {cur['file']} — {n_keep / SR:.2f}초만 남음"))
            x = cur["x"][:n_keep].copy(); fo = min(int(SFX.CUT_FADE * SR), len(x) // 2)
            ramp = np.linspace(1, 0, fo, dtype=np.float32)
            x[-fo:] *= ramp[:, None] if x.ndim == 2 else ramp
            cut_log.append(f"  {cur['start']:6.3f}s {cur['role']:<12} {cur['len']:.2f}s → {len(x) / SR:.2f}s (다음 {nxt['role']} {nxt['start']:.3f}s)")
            cur["x"], cur["len"] = x, len(x) / SR

    # 규칙 점검 (3-튜플) -----------------------------------------------------------
    trip = [(r["start"], r["file"], r["len"]) for r in items]
    bed_iv = [(0.0, length - END_SILENCE)]
    # 말 없는 타이포(분당 약 130)는 «한 편 2번»(5-4) 대신 3초 사슬 규칙만 — sfx.md 결정표 ⑦
    plain = RC.check_sfx(trip, length, per_ep_max=None)
    chk = RC.check_sfx(trip, length, bed_intervals=bed_iv, per_ep_max=None) + chk_fit
    chk += RC.check_tone(r["file"] for r in items)
    errs = [x for x in chk if x[0] == "ERROR"]

    # 믹스 · 마스터 ----------------------------------------------------------------
    def sfx_sum(gain_db=0.0):
        m = np.zeros((n, 2), np.float32)
        g = 10 ** (gain_db / 20)
        for r in items:
            i = int(round(r["start"] * SR))
            seg = (r["x"] * g)[: max(0, n - i)]
            m[i:i + len(seg)] += seg
        return m

    def endfade(m):
        k = int(MIX_END_FADE * SR)
        m[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
        return m

    pre = endfade(sfx_sum() + bed)
    comp = HL.ff_array(pre, "acompressor=threshold=-18dB:ratio=2:attack=15:release=200:makeup=1")[: len(pre)]
    tmp = out / "_tmp_master.wav"
    SFX.write_wav(tmp, comp)
    I0, _ = HL.measure(tmp)
    tmp.unlink(missing_ok=True)
    gain = TARGET_LUFS - I0
    ceil_db = TP_MAX - 0.3                                   # 리미터 천장(dBFS) — 인코딩 뒤 트루피크를 보고 내린다
    final_wav = out / f"{a.name}_합본.wav"
    mp3 = out / f"{a.name}.mp3"
    for _ in range(14):
        ceil = 10 ** (ceil_db / 20)
        lim = HL.ff_array(comp * 10 ** (gain / 20), f"alimiter=limit={ceil:.4f}:attack=3:release=40:level=disabled")[: len(comp)]
        SFX.write_wav(final_wav, lim)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(final_wav), "-c:a", "libmp3lame", "-b:a", "192k", "-ar", str(SR), str(mp3)], check=True)
        I_mp3, tp_mp3 = HL.measure(mp3)
        if abs(I_mp3 - TARGET_LUFS) <= 0.25 and tp_mp3 <= TP_MAX:
            break
        if tp_mp3 > TP_MAX:
            ceil_db -= tp_mp3 - TP_MAX + 0.1
        if abs(I_mp3 - TARGET_LUFS) > 0.25:
            gain += TARGET_LUFS - I_mp3
    ceil = 10 ** (ceil_db / 20)

    # 낱개 wav (마스터 게인 반영) --------------------------------------------------
    g_lin = 10 ** (gain / 20)
    for old in nick.glob("*.wav"):
        old.unlink()
    SFX.write_wav(nick / "00_BGM.wav", HL.ff_array(bed * g_lin, f"alimiter=limit={ceil:.4f}:attack=3:release=40:level=disabled")[: len(bed)])
    for k, r in enumerate(items, 1):
        y = HL.ff_array(r["x"] * g_lin, f"alimiter=limit={ceil:.4f}:attack=3:release=40:level=disabled")[: len(r["x"])]
        r["wav"] = nick / f"{k:02d}_{r['role']}.wav"
        SFX.write_wav(r["wav"], y)
        r["wav_peak"] = 20 * math.log10(float(np.abs(y).max()) + 1e-9)
    # 낱개 배치표(프리미어 XML 을 만들 때 시각을 읽는다)
    json.dump({"length": length, "bgm": "00_BGM.wav", "sfx": [{"file": r["wav"].name, "start": round(r["start"], 4), "role": r["role"], "t": round(r["t"], 4), "align": r["align"]} for r in items]},
              open(nick / "_배치.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # 점검 txt ---------------------------------------------------------------------
    L = [f"소리 미리듣기 점검 — {a.name}  (큐 {Path(a.cue).name}, 길이 {length:.1f}초)",
         "도구: tools/scenes/hanbiz_ad_sfx_preview.py · 엔진 tools/sfx.py(role/prep) · 규칙 rule_check.check_sfx(3-튜플)",
         "", "[BGM]",
         f"  {Path(bed_src).name} / 곡 {cue['bgm'].get('start_in_track', 0.0)}초부터 {length:.1f}초 / 처리: 크기 맞춤·볼륨 곡선·끝 페이드만 (EQ·덕킹·큰 소리 비킴 끔 — 나레이션 없음)",
         f"  크기: 곡 구간 50ms RMS 중앙 {bed_mid:.1f} dBFS → {bed_target:.1f} dBFS (가상 효과음 기준 {REF_DBFS + PREP_OFFSET:.0f} 에 대한 {a.bgm_db:+.0f} dB; --bgm-db)",
         "  볼륨 곡선(점 시각에 도달하는 0.15초 램프): " + ", ".join(f"{t:.3f}s→{d:+.0f}dB" for t, d in knots),
         f"  끝: {length - END_SILENCE - END_FADE_BGM:.2f}~{length - END_SILENCE:.2f}s 페이드 → {length - END_SILENCE:.2f}~{length:.2f}s 무음",
         "", f"[크기 기준] 가상 REF = {REF_DBFS:.0f} dBFS(50ms RMS) + 큐의 db(역할 상대값), prep 은 {PREP_OFFSET:+.0f}dB 낮춰 돌림(hanbiz_logo_sfx 와 같음).",
         f"  마감: 마스터 컴프(−18dB, 2:1) → 게인 {gain:+.1f} dB (컴프 뒤 {I0:.1f} LUFS) → 리미터. 낱개 wav 에는 이 게인만 곱함(컴프·끝 페이드 제외).",
         "", "[큐] 큐 시각 · 소리 · 시작 · 프레임(29.97fps)", "  t | 역할 → 파일 | 시작 | 정렬/기준점 | 길이 | db | 낱개 wav(피크) | 이벤트"]
    for r in items:
        ref_t = r["start"] + (r["peak_at"] if r["align"] == "peak" else 0.0)
        L.append(f"  {r['t']:7.3f}s f{round(r['t'] / FRAME_DT):4d} | {r['role']} → {r['file']} | {r['start']:.3f}s f{round(r['start'] / FRAME_DT):4d} | "
                 f"{r['align']} {ref_t:.3f}s ({round((ref_t - r['t']) / FRAME_DT):+d}f) | {r['len']:.2f}s | {r['db']:+d} | {r['wav'].name} ({r['wav_peak']:.1f}dBFS)"
                 f"{' | ' + r['event'] if r['event'] else ''}{' | ' + r['note'] if r['note'] else ''}")
    if laser_note:
        L += ["  (레이저 엔딩: " + "; ".join(laser_note) + ")"]
    L += ["", "[규칙 점검 — rule_check.check_sfx 3-튜플]"]
    L += [f"  [{lv}] {r}: {m}" for lv, r, m in chk] or ["  통과 (5-2 연속 · 5-2b 짧은 주기 3번 · 5-3 빈 구간 — BGM 깔린 구간 제외)"]
    L.append(f"  참고: BGM 을 빼고(bed_intervals 없이) 효과음만으로 재면 5-3 {len([x for x in plain if x[1].startswith('5-3')])}건 — BGM 이 깔린 형식이라 sfx.md 17장대로 빈 시간을 메우지 않음")
    if errs and a.ignore_reason:
        L.append(f"  --ignore-reason 로 넘김: {a.ignore_reason}")
    if errs and not a.ignore_reason:
        print("\n".join(L))
        raise SystemExit("규칙 ERROR — 큐를 고치거나 --ignore-reason")

    # 박 정렬 ---------------------------------------------------------------------
    n_ok = n_all = 0
    if a.beats:
        bt = json.loads(rp(a.beats).read_text(encoding="utf-8"))[a.beat_key]
        rows, n_ok, n_all = beat_report([c for c in cues if c["role"] != "logo_ending"], raw_bed, cue["bgm"].get("start_in_track", 0.0), bt)
        L += ["", f"[마디 경계 확인 — BGM 실제 onset 대 큐 시각 (박자표 {a.beat_key}: {bt['bpm']}BPM, 박 {bt['beat_s']}s, 마디 {bt['bar_s']}s)]",
              "  큐 시각 | 역할 | BGM 실제 onset(에너지 상승, 10ms 격자) | 판정(±1프레임 = ±0.033s)"] + rows
        L.append(f"  → onset 이 잡힌 {n_all}개 중 ±1프레임 안 {n_ok}개. (BGM 은 곡 원본 — 볼륨 곡선 적용 전 신호로 잼. 상승이 «약함»이면 그 박에 뚜렷한 타악이 없다는 뜻)")

    # 드롭 자리 ---------------------------------------------------------------------
    drop = next((c for c in cues if c["role"] == "hit_big_low"), None)
    if drop:
        td = drop["t"]
        bed_c = bed * g_lin
        mix_c = lim
        sfx_only = sfx_sum() * g_lin
        L += ["", f"[마디3 드롭 {td:.3f}s 전후 0.5초 RMS (dBFS, 마감 후 믹스 기준)]"]
        for lab, sig in (("합본", mix_c), ("BGM만", bed_c), ("효과음만", sfx_only)):
            a0, a1, a2 = rms_db(sig, td - 1.0, td - 0.5), rms_db(sig, td - 0.5, td), rms_db(sig, td, td + 0.5)
            L.append(f"  {lab:6s}: 앞 1.0~0.5초 {a0:6.1f} | 앞 0.5초 {a1:6.1f} | 뒤 0.5초 {a2:6.1f}  → 뒤−앞 {a2 - a1:+.1f} dB, 앞0.5초−그 앞0.5초 {a1 - a0:+.1f} dB")
        gap = rms_db(bed_c, td - 0.5, td)
        pre = rms_db(bed_c, td - 1.0, td - 0.5)
        post = rms_db(bed_c, td, td + 0.5)
        L.append(f"  BGM 만 0.5초 창 평균: 드롭 앞 0.5초는 그 앞 0.5초보다 {gap - pre:+.1f} dB, 드롭 뒤는 앞 0.5초보다 {post - gap:+.1f} dB (앞 0.5초 창의 끝 0.15초가 드롭으로 올라가는 램프라 평균이 덜 내려감 — 평탄부 값을 볼 것)")
        raw_c = raw_bed
        L.append(f"  곡 원본(곡선 전, 상대값) {td - 1.0:.3f}~{td - 0.5:.3f}s {rms_db(raw_c, td - 1.0, td - 0.5):.1f} → 앞 0.5초 {rms_db(raw_c, td - 0.5, td):.1f} → 뒤 0.5초 {rms_db(raw_c, td, td + 0.5):.1f} (곡 자체의 변화)")
        L.append(f"  −14 평탄부 {td - 0.5:.3f}~{td - 0.01:.3f}s BGM 만 {rms_db(bed_c, td - 0.5, td - 0.01):.1f} dBFS (그 앞 {td - 1.0:.3f}~{td - 0.65:.3f}s {rms_db(bed_c, td - 1.0, td - 0.65):.1f}) — 드롭 점의 ramp 가 짧으면(0.01) 평탄부가 0.5초 가까이 된다. 실제값은 아래 줄")
        # 곡선 값 직접 확인
        env = bed_envelope(n, knots)
        L.append("  볼륨 곡선 실제값: " + ", ".join(f"{tt:.3f}s {20 * math.log10(env[min(n - 1, int(tt * SR))]):+.1f}dB" for tt in (td - 0.6, td - 0.5, td - 0.3, td - 0.1, td, td + 0.1, td + 0.2)))
        sfx_in_gap = [r for r in items if r["start"] < td and r["start"] + r["len"] > td - 0.5]
        L.append("  앞 0.5초에 걸린 효과음 꼬리: " + (", ".join(f"{r['file']}({r['start']:.2f}~{r['start'] + r['len']:.2f}s)" for r in sfx_in_gap) or "없음"))

    # 나레이션 예상 구간 -----------------------------------------------------------
    if any("word" in c for c in cues):
        L += ["", "[나레이션 예상 구간 — 대본 예상 초(5.5음절/초) 기준, 미리듣기에는 자리 표시음 없음]", "  시각 | 대본 단어 | 소리 | 다음 큐까지"]
        for i, c in enumerate(cues):
            nxt = (cues[i + 1]["t"] - c["t"]) if i + 1 < len(cues) else length - c["t"]
            L.append(f"  {c['t']:6.1f}s | {c.get('word', '')} | {c['role']} {c.get('db', 0):+d}dB {Path(c['file']).name} | {nxt:.1f}초")

    # 실측 ---------------------------------------------------------------------------
    I_wav, tp_wav = HL.measure(final_wav)
    dur_mp3 = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)], capture_output=True, text=True).stdout.strip())
    L += ["", "[실측 ebur128]",
          f"  합본 wav: I {I_wav:.1f} LUFS · TP {tp_wav:.1f} dBTP",
          f"  mp3 192k: I {I_mp3:.1f} LUFS · TP {tp_mp3:.1f} dBTP · 길이 {dur_mp3:.2f}s → 목표 {TARGET_LUFS:.0f}±{HL.LUFS_TOL} / TP ≤ {TP_MAX}: "
          + ("통과" if abs(I_mp3 - TARGET_LUFS) <= HL.LUFS_TOL and tp_mp3 <= TP_MAX else "미달"),
          "", "[걸린 것]",
          "  - 소리는 귀로 듣지 못했다(파형·RMS·박 측정만).",
          "  - 프리미어 XML 은 만들지 않았다(lec_xml 은 영상 클립을 전제) — 낱개 wav + 위 시각표로 대신.",
          "  - BGM 대 효과음 균형(--bgm-db)은 추정값 — 들어 보고 조정.",
          "  - 합본 wav 는 컴프·리미터·끝 페이드가 든 최종, 낱개 wav 는 게인만 반영."]
    if cut_log:
        L += ["", "[겹침 끊기 — 다음 효과음의 들리는 어택 10ms 전에 앞 효과음을 끊음 · 60ms 페이드]"] + cut_log
    if sync_log:
        L += ["", "[들리는 시각 맞춤 — 어택(−12dB)/피크가 큐 시각에 오게 시작을 옮김]"] + sync_log
    if match_log:
        L += ["", "[음악 대비 크기 맞춤 — 단계 타격 +8 · 보통 +5 · 쓸림 +1 dB, 효과음마다 BGM 순간 −4dB 덕킹]"] + match_log
    chkp = out / f"{a.name}_점검.txt"
    chkp.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(L))
    print(f"→ {mp3}\n→ {chkp}")


def audible_ref(x, align, win=0.005):
    """귀에 들리는 기준 시각(초, 파일 안): onset = 피크 대비 −20dB 첫 도달, peak = 엔벨로프 최대."""
    m = np.abs(x).max(axis=1) if x.ndim == 2 else np.abs(x)
    n = max(1, int(SR * win)); k = len(m) // n
    if k == 0:
        return 0.0
    e = 20 * np.log10(m[:k * n].reshape(k, n).max(axis=1) + 1e-9)
    if align == "peak":      # 넓게 퍼진 쓸림 소리는 리미터가 꼭대기를 깎아 최대점이 흔들림 → 20ms RMS 로 잰다
        n2 = int(SR * 0.02); k2 = len(m) // n2
        if k2:
            r2 = np.sqrt((m[:k2 * n2].reshape(k2, n2) ** 2).mean(axis=1))
            return (float(r2.argmax()) + 0.5) * 0.02
        return float(e.argmax()) * win
    return float(np.argmax(e >= e.max() - 20)) * win


def main():
    ap = argparse.ArgumentParser(description="한비즈 광고 소리 미리듣기(BGM + 효과음)")
    ap.add_argument("--cue", required=True, help="효과음 큐 JSON")
    ap.add_argument("--out", required=True, help="출력 폴더")
    ap.add_argument("--name", required=True, help="파일 이름(확장자 없이)")
    ap.add_argument("--length", type=float, help="총 길이(초). 기본 = 마지막 큐 + 2.3초")
    ap.add_argument("--bgm-db", type=float, default=-10.0, help="BGM 중앙 RMS 를 효과음 기준(−30 dBFS)에 대해 몇 dB 로 둘지")
    ap.add_argument("--beats", help="BGM 박자표 JSON(마디 경계 확인)")
    ap.add_argument("--beat-key", default="3안")
    ap.add_argument("--ignore-reason", help="규칙 ERROR 를 넘길 때 이유")
    ap.add_argument("--no-match", dest="match", action="store_false", help="효과음을 음악 대비 단계로 맞추지 않음(3판까지의 방식)")
    run(ap.parse_args())


if __name__ == "__main__":
    main()
