# -*- coding: utf-8 -*-
r"""한비즈 로고 엔딩 효과음 입히기 — 무음 mp4 + events.json + 역할표 → 소리 든 mp4 · 효과음 낱개 wav · 프리미어 XML · 점검 txt.

    python tools/scenes/hanbiz_logo_sfx.py --preset logo \
        --video _tmp/logo_end/paper.mp4 --events _tmp/logo_end/paper_events.json \
        --name 로고엔딩_크림 --out 납품/시안_로고엔딩_1008

  --preset logo   크림·남색 조립 엔딩 (events: logo_in · lock_pulse · word_in · sub_in · cta_in · cta_pulse)
  --preset laser  레이저 엔딩 «초안» (events: draw_start · draw_warm · ignite · fill_in · sweep · word_in · sub_in) — 실행은 레이저 HTML 이 확정된 뒤
  --video 는 «무음 원본»을 준다(납품 파일을 덮어쓰는 도구라, 소리 든 납품본을 다시 넣으면 소리가 두 겹이 되지 않게 영상 스트림만 쓴다).
  역할표를 바꾸려면 PRESETS 에 한 줄을 더한다 — 엔진(고르기·다듬기·크기)은 tools/sfx.py 그대로.

만드는 것 (out = --out)
  <out>/<name>.mp4                          소리 든 판 (같은 이름 제자리 덮어쓰기. 영상은 재인코딩 없이 복사)
  <out>/<name>_효과음.xml                   V1 영상 + A2~ 효과음 (lec_xml, 29.97fps, 1080x1920)
  <out>/효과음_낱개/<prefix>_NN_<역할>.wav  XML 이 가리키는 wav (마스터 게인 반영분)
  <work>/<name>_효과음_점검.txt             시각·크기·규칙 점검·LUFS/TP·ffprobe (work 기본 = _tmp/logo_end)

크기 기준 (목소리가 없는 영상 — 목소리 ref 가 없다)
  sfx.prep 은 «목소리 50ms RMS 중앙 + 상대 dB» 로 크기를 정한다. 여기엔 목소리가 없으므로 REF_DBFS = −20 dBFS(50ms RMS)를
  가상의 «목소리 크기»로 둔다. 근거: sfx.md 3-1 레퍼런스 쇼츠(분양1) 효과음이 −20~−29 dBFS(짧은 구간 최대) — 그 위쪽 끝.
  prep 의 피크 −6dBFS 상한이 −20 기준에서는 대부분의 소리에 걸려 상대 균형이 납작해진다 → 실제로는 REF+PREP_OFFSET(−10)에서 다듬고
  마스터 게인이 그만큼 되돌린다(최종 절대 크기는 −14 LUFS 가 정하므로 같다).
  이 값은 절대 크기를 정하지 않는다. 역할끼리의 균형(상대 dB: 3-2 FILE_DB · 역할표 rel)만 정하고, 곧바로 마스터가
  통합 −14 LUFS · 트루피크 −1.5 dBTP 이하로 전체를 끌어올린다(sfx.md 15장 8단계, 쇼츠 −14 LUFS).
  마스터 게인은 낱개 wav 에도 곱해 두어 XML 로 짠 소리와 mp4 소리의 크기가 같다(리미터·끝 페이드만 mp4 쪽에 따로).

소리를 귀로 확인하지 못했다 — 점검 txt 에도 그렇게 적는다(sfx.md 핵심 12줄 12번).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config as C  # noqa: E402
import lec_xml  # noqa: E402
import rule_check as RC  # noqa: E402
import sfx as SFX  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SR = SFX.SR
FPS = 29.97
FRAME_DT = 1001 / 30000
REF_DBFS = -20.0              # 가상 «목소리» 크기(위 설명)
PREP_OFFSET = -10.0           # prep 은 REF+이 값에서 돌린다 — prep 의 «피크 −6dBFS 상한»(짧은 클릭 보호)이 -20 에서는 거의 모든 소리에 걸려
                              # 상대 균형(임팩트 > 차임 > 반짝)이 납작해지기 때문. 균형만 남기고 절대 크기는 마스터(−14 LUFS)가 정하므로 결과 음량엔 영향 없음
TARGET_LUFS = -14.0           # 마감 통합 음량 (sfx.md 15장 8단계)
TP_MAX = -1.5                 # 트루피크 상한 dBTP
LUFS_TOL = 0.5                # 목표 허용 오차 LU
END_FADE = 0.2                # 영상 끝에서 소리가 뚝 끊기지 않게 마지막 0.2초 페이드

# ─────────────────────────────────────────────────────────────────────────────
# 역할표 (SND_FIX 형식, sfx.md 13·14장): 소리 역할 → (파일 이름, 최소 길이초, 기본 dB, 정렬[, 예외 dB])
#   정렬 "onset" = 소리 시작이 시각 · "peak" = 소리 정점이 시각.  dB 는 FILE_DB 가 있는 파일이면 그 값이 덮는다(exact 제외).
#   CUES = (events 의 role, 소리 역할, 시각 보정 초)  — 한 이벤트에 소리 둘을 겹칠 수 있다.
# 고른 기준: 분양4 04 로고 사장님 원문 «AI 기계음·날카로운·찢어지는·둔탁한 소리 없게» — 만화·장난감 소리(뿅·띠용·방울) 없음,
#   저음이 몰린 쿵(둔탁)·고음 순간음(찢어짐) 없음. 반짝 계열은 5kHz 셸빙(−6dB)이 걸려 부드러워진다.
# ─────────────────────────────────────────────────────────────────────────────
SND_FIX_LOGO = {
    # 두 획이 날아와 맞물리기까지 약 0.95초 동안 차오르는 부드러운 스윕(정점이 lock_pulse 1.1 초 근처, 저·고역 치우침 없음, A등급)
    "fly": ("ML_Magic transition sweep presentation.wav", 0.9, 4, "onset"),
    # 맞물림: 부드럽게 시작해 울리는 임팩트 벨(무게는 있되 저음 쿵이 아님, 중심 ~450Hz, 순간 상승 3dB/10ms)
    "lock_hit": ("KN_impactBell_heavy_000.wav", 0.8, 5, "onset"),
    # 맞물림 반짝: 정점을 맞물림 직후에 맞춰 얹는 작은 반짝(고역 셈 → 셸빙)
    "lock_spark": ("ML_Magic sparkle touch.wav", 0.8, 0, "peak"),
    # 한글 글자 와이프 → 영문 페이드까지 이어지는 가벼운 쉬머(아주 작게)
    "word": ("ML_Magic glitter or particles.wav", 1.2, -2, "onset"),
    # CTA 버튼 등장: 맑은 차임(사장님 «로고·브랜드 첫 등장» 통과 소리). 표값 +7 은 임팩트보다 커지므로 +4 로 낮춤
    "cta": ("맑은소리.mp3", 0.8, 4, "onset", 4),
    # CTA 파동: 작은 반짝(사장님 통과 «칩 반짝»). 표값 −1
    "cta_pulse": ("SEL_キラッ1.mp3", 0.7, -1, "onset"),
}
CUES_LOGO = [
    ("logo_in", "fly", 0.0),
    ("lock_pulse", "lock_hit", 0.0),
    ("lock_pulse", "lock_spark", 0.08),
    ("word_in", "word", 0.0),
    # sub_in(영문 페이드)은 소리를 새로 얹지 않는다 — word 쉬머의 꼬리가 덮는다(소리 과다 방지)
    ("cta_in", "cta", 0.0),
    ("cta_pulse", "cta_pulse", 0.0),
]

# 레이저 엔딩용 «초안» — 이벤트 이름은 hanbiz_logo_laser.html 의 EVENTS 에서 읽은 것. 레이저 HTML 이 바뀌면 시각·이름을 맞춘다.
#   그어짐 = 반짝이는 쉬머/sparkle whoosh 류 길게 · 점화 = 반짝 히트 · 사선 빛줄기 = 부드러운 휙 · 글자 = 가벼운 쉬머
SND_FIX_LASER = {
    "draw_blue": ("ML_Magic sparkle whoosh.wav", 1.5, 3, "onset"),            # 파랑 획을 그으며 번지는 쉬머(길게)
    "draw_warm": ("ML_Fairy sparkle whoosh.wav", 1.5, 0, "onset"),            # 주황 획 — 같은 소리 연속 금지(5-2)라 결이 같은 다른 파일
    "ignite": ("ML_Magic sparkle poof hit.wav", 0.8, 3, "onset"),             # 전체가 번쩍 — 반짝 히트
    "fill": ("SEL_キラッ2.mp3", 0.9, 0, "onset"),                              # 빛 → 색으로 채워짐
    "sweep": ("ML_Fast sweeping transition.wav", 0.9, 3, "peak"),             # 사선 빛줄기 — 부드러운 휙
    "word": ("ML_Magic glitter or particles.wav", 1.2, -2, "onset"),          # 글자 드러남 — 가벼운 쉬머
}
CUES_LASER = [
    ("draw_start", "draw_blue", 0.0),
    ("draw_warm", "draw_warm", 0.0),
    ("ignite", "ignite", 0.0),
    ("fill_in", "fill", 0.0),
    ("sweep", "sweep", 0.0),
    ("word_in", "word", 0.0),
]

PRESETS = {
    "logo": {"snd_fix": SND_FIX_LOGO, "cues": CUES_LOGO, "prefix": "로고"},
    "laser": {"snd_fix": SND_FIX_LASER, "cues": CUES_LASER, "prefix": "레이저"},
}


def events_plan(path):
    """events.json → {이벤트 role: [시각, …]} (html_motion.events_to_sfx_plan; 무거운 import 가 안 되면 같은 일을 직접)."""
    try:
        import html_motion
        return html_motion.events_to_sfx_plan(path)
    except Exception:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        out = {}
        for e in d.get("events", []):
            if e.get("role"):
                out.setdefault(e["role"], []).append(round(e["t"], 4))
        return {r: sorted(v) for r, v in out.items()}


def snap(t):
    """프레임 격자(29.97fps)에 맞춘다 — XML 시각과 wav 시각이 같게."""
    return max(0, round(t / FRAME_DT)) * FRAME_DT


def ff_array(x, af):
    """스테레오 float 배열에 ffmpeg 오디오 필터를 걸어 같은 꼴로 돌려준다."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", af, "-f", "f32le", "-"],
                         input=x.astype("<f4").tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def measure(path):
    """ebur128 통합 음량(LUFS)·트루피크(dBTP) — 파일(wav/mp4)."""
    p = subprocess.run(["ffmpeg", "-nostats", "-i", str(path), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = p.stderr[p.stderr.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", tail)
    tp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail)
    return (float(i.group(1)) if i else None), (float(tp.group(1)) if tp else None)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels,duration",
                          "-of", "compact", str(path)], capture_output=True, text=True, encoding="utf-8").stdout.strip()
    return out


def video_duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "csv=p=0", str(path)],
                                capture_output=True, text=True).stdout.strip())


def build_cues(preset, events_path, dur):
    """이벤트 × 역할표 → 큐 목록(시작 초 · 역할 · 배열 · 정점 초 …). 크기는 prep 이 REF_DBFS 기준으로 맞춘다."""
    SFX.SND.update(SFX.roles_from(preset["snd_fix"]))
    plan = events_plan(events_path)
    cues = []
    for ev_role, snd, off in preset["cues"]:
        for t in plan.get(ev_role, []):
            x, peak_at = SFX.prep(snd, REF_DBFS + PREP_OFFSET)
            fn, mx, shelf, fin, rel, align, grade = SFX.SND[snd]
            want = t + off                                              # 소리 기준점(onset 이면 시작, peak 이면 정점)이 올 시각
            start = snap(want - (peak_at if align == "peak" else 0.0))
            note = ""
            if want - (peak_at if align == "peak" else 0.0) < 0:
                note = "시작이 0초 앞이라 0초로 당김"
            cues.append({"event": ev_role, "t": t, "off": off, "snd": snd, "file": Path(fn).name, "x": x, "peak_at": peak_at, "align": align,
                         "rel": rel, "grade": grade, "shelf": shelf, "fin": fin, "start": start, "want": want, "note": note,
                         "len": len(x) / SR})
    cues.sort(key=lambda c: (c["start"], c["snd"]))
    return cues


def mix_cues(cues, dur, gain_db=0.0):
    n = int(round(dur * SR))
    m = np.zeros((n, 2), np.float32)
    g = 10 ** (gain_db / 20)
    for c in cues:
        i = int(round(c["start"] * SR))
        seg = (c["x"] * g)[: max(0, n - i)]
        m[i:i + len(seg)] += seg
    k = int(END_FADE * SR)
    m[-k:] *= np.linspace(1, 0, k)[:, None] ** 2          # 영상 끝에서 뚝 끊기지 않게
    return m


def master(cues, dur, work):
    """통합 −14 LUFS · 트루피크 −1.5 이하로 맞추는 게인(dB)을 찾는다. 반환 (게인, 마스터된 믹스, 실측 I, TP)."""
    tmp = work / "_mix_tmp.wav"
    raw = mix_cues(cues, dur, 0.0)
    SFX.write_wav(tmp, raw)
    I0, _ = measure(tmp)
    gain = TARGET_LUFS - I0
    ceil = 10 ** (TP_MAX / 20) * 0.99                       # 샘플 피크 상한(트루피크 여유)
    for _ in range(5):
        mixed = mix_cues(cues, dur, gain)
        lim = ff_array(mixed, f"alimiter=limit={ceil:.4f}:attack=3:release=40:level=disabled")[: len(mixed)]
        SFX.write_wav(tmp, lim)
        I, tp = measure(tmp)
        if abs(I - TARGET_LUFS) <= 0.2 and tp <= TP_MAX:
            break
        gain += TARGET_LUFS - I
    tmp.unlink(missing_ok=True)
    return gain, lim, I, tp, I0


def mux(video, audio_wav, out_mp4, ceil_db=0.0):
    tmp = out_mp4.with_name(out_mp4.stem + "_tmp_mux.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(audio_wav), "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", str(SR), "-shortest", "-movflags", "+faststart", str(tmp)], check=True)
    shutil.move(str(tmp), str(out_mp4))


def run(args):
    preset = PRESETS[args.preset]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    work = Path(args.work) if args.work else C.WORK / "logo_end"
    work.mkdir(parents=True, exist_ok=True)
    nick = out / "효과음_낱개"
    nick.mkdir(parents=True, exist_ok=True)
    dur = video_duration(args.video)
    cues = build_cues(preset, args.events, dur)
    if not cues:
        raise SystemExit("큐가 하나도 없다 — events.json 의 role 이름이 역할표(CUES)와 맞는지 확인")
    used = {c["event"] for c in cues}
    missing = [e for e, _, _ in preset["cues"] if e not in used]

    # 규칙 점검(3-튜플) — ERROR 면 멈춘다
    items = RC.check_sfx([(c["start"], c["file"], c["len"]) for c in cues], dur)
    err = [x for x in items if x[0] == "ERROR"]
    if err and not args.ignore_reason:
        RC.report(items, title=args.name)
        raise SystemExit("규칙 ERROR — 고치거나 --ignore-reason \"이유\" 로 넘기고 점검 txt 에 적는다")

    gain, mixed, I_wav, tp_wav, I_raw = master(cues, dur, work)

    # 낱개 wav (마스터 게인 반영 — XML 로 짠 소리가 mp4 와 같은 크기)
    sfx_xml = []
    ceil = 10 ** (TP_MAX / 20) * 0.99
    for k, c in enumerate(cues, 1):
        y = ff_array(c["x"] * (10 ** (gain / 20)), f"alimiter=limit={ceil:.4f}:attack=3:release=40:level=disabled")[: len(c["x"])]
        c["wav"] = nick / f"{preset['prefix']}_{k:02d}_{c['snd']}.wav"
        SFX.write_wav(c["wav"], y)
        c["wav_peak_db"] = 20 * np.log10(np.abs(y).max() + 1e-9)
        sfx_xml.append((c["start"], c["wav"]))

    # mp4: 같은 이름 제자리 덮어쓰기 — 소리 든 판. AAC 뒤 트루피크가 넘으면 상한을 내려 다시.
    final = out / f"{args.name}.mp4"
    mix_wav = work / f"{args.name}_믹스.wav"
    cur = mixed
    adj = 0.0
    for _ in range(3):
        SFX.write_wav(mix_wav, cur)
        mux(args.video, mix_wav, final)
        I_mp4, tp_mp4 = measure(final)
        if tp_mp4 <= TP_MAX:
            break
        adj += tp_mp4 - TP_MAX + 0.1
        cur = ff_array(mixed * 10 ** (-adj / 20), f"alimiter=limit={ceil * 10 ** (-adj / 20):.4f}:attack=3:release=40:level=disabled")[: len(mixed)]

    xml_path = out / f"{args.name}_효과음.xml"
    lec_xml.SEQ_W, lec_xml.SEQ_H = C.W, C.H
    lec_xml.V_TRACK, lec_xml.A_TRACK = 1, 2
    _, tracks = lec_xml.write(xml_path, f"{args.name}_효과음", final, dur, 0.0, sfx_xml, fps=FPS, tag="l")

    # 점검 txt
    L = [f"효과음 점검 — {args.name}  (preset {args.preset}, {Path(args.video).name} + {Path(args.events).name})",
         f"도구: tools/scenes/hanbiz_logo_sfx.py · 엔진 tools/sfx.py(role/prep) · 규칙 rule_check.check_sfx(3-튜플)", ""]
    L.append(f"[크기 기준] 목소리 없음 → 가상 기준 REF = {REF_DBFS:.0f} dBFS(50ms RMS) + 역할 상대 dB (prep 은 {PREP_OFFSET:+.0f}dB 낮춰 돌림 — 피크 −6dBFS 상한이 균형을 납작하게 해서). 마감 목표 통합 {TARGET_LUFS:.0f} LUFS · 트루피크 {TP_MAX} dBTP 이하.")
    L.append(f"  마스터 게인 {gain:+.1f} dB (게인 전 통합 {I_raw:.1f} LUFS) — 낱개 wav 에도 곱함. 리미터 alimiter limit {ceil:.3f}, 끝 {END_FADE}s 페이드.")
    L += ["", "[큐] 이벤트 시각 → 소리 (프레임 = 29.97fps)",
          "  이벤트(t)            프레임 | 소리 역할 → 파일 | 시작 | 기준점 | 기준점−이벤트(프레임) | 길이 | 상대dB | 등급 | 셸빙 | 낱개 wav(피크)"]
    for c in cues:
        ref_t = c["start"] + (c["peak_at"] if c["align"] == "peak" else 0.0)
        d_fr = round((ref_t - c["want"]) / FRAME_DT)
        ev_fr = round(c["t"] / FRAME_DT)
        c["d_fr"] = d_fr
        L.append(f"  {c['event']:11s} {c['t']:5.2f}s f{ev_fr:3d} | {c['snd']:10s} → {c['file']} | {c['start']:.3f}s f{round(c['start'] / FRAME_DT):3d} | "
                 f"{c['align']} {ref_t:.3f}s | {d_fr:+d}f(보정 {c['off']:+.2f}s) | {c['len']:.2f}s | {c['rel']:+d} | {c['grade']} | "
                 f"{'셸빙' if c['shelf'] else '-'}{' 페이드인' if c['fin'] else ''} | {c['wav'].name} ({c['wav_peak_db']:.1f}dBFS){' ' + c['note'] if c['note'] else ''}")
    if missing:
        L.append(f"  (이벤트에 없어 건너뜀: {', '.join(missing)})")
    L += ["", "[규칙 점검 — rule_check.check_sfx 3-튜플]"]
    L += [f"  [{lv}] {r}: {m}" for lv, r, m in items] or ["  통과 (5-2 연속 · 5-2b 짧은 주기 · 5-3 소리 없는 시간 2.5초)"]
    if err:
        L.append(f"  --ignore-reason 로 넘김: {args.ignore_reason}")
    end_t = max(c["start"] + c["len"] for c in cues)
    L.append(f"  마지막 소리 끝 {end_t:.2f}s / 영상 {dur:.3f}s" + (" — 마지막 소리가 영상 끝을 덮음(자연 잔향 + 끝 페이드)" if end_t >= dur else ""))
    L += ["", "[실측 ebur128]",
          f"  믹스 wav(리미터 후): I {I_wav:.1f} LUFS · TP {tp_wav:.1f} dBTP",
          f"  최종 mp4(AAC 256k 뒤): I {I_mp4:.1f} LUFS · TP {tp_mp4:.1f} dBTP  → 목표 {TARGET_LUFS:.0f}±{LUFS_TOL} / TP ≤ {TP_MAX}: "
          + ("통과" if abs(I_mp4 - TARGET_LUFS) <= LUFS_TOL and tp_mp4 <= TP_MAX else "미달 — 아래 걸린 것 참고"),
          "", "[ffprobe]", "  " + probe(final).replace("\n", "\n  "),
          f"  XML: {xml_path.name} (V1 영상 + {', '.join(tracks)} 효과음 {len(cues)}개)",
          "", "[걸린 것]",
          "  - 소리는 귀로 듣지 못했다(파형·대역·길이만 확인).",
          "  - XML 에는 끝 페이드·리미터가 없다(낱개 wav 는 게인·개별 리미터만 반영).",
          "  - 영상은 재인코딩 없이 복사했다(영상 스트림 그대로)."]
    chk = work / f"{args.name}_효과음_점검.txt"
    chk.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    mix_wav.unlink(missing_ok=True)
    print("\n".join(L))
    print(f"→ {final}\n→ {xml_path}\n→ {chk}")
    return cues


def main():
    ap = argparse.ArgumentParser(description="한비즈 로고 엔딩 효과음 입히기")
    ap.add_argument("--preset", choices=sorted(PRESETS), default="logo")
    ap.add_argument("--video", required=True, help="무음 원본 mp4")
    ap.add_argument("--events", required=True, help="<name>_events.json")
    ap.add_argument("--name", required=True, help="납품 파일 이름(확장자 없이). 같은 이름으로 덮어쓴다")
    ap.add_argument("--out", required=True, help="납품 폴더")
    ap.add_argument("--work", help="점검 txt 폴더(기본 _tmp/logo_end)")
    ap.add_argument("--ignore-reason", help="규칙 ERROR 를 넘길 때 이유(점검 txt 에 적는다)")
    run(ap.parse_args())


if __name__ == "__main__":
    main()
