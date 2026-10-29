# -*- coding: utf-8 -*-
r"""레퍼런스 영상의 효과음 후보 분석 — 소리를 귀로 못 듣는다는 전제에서 수치로 판정한다.

    python -I tools/sfx_ref_analyze.py <폴더>          # <폴더>/src.mp4 (yt-dlp 로 받은 것, 신뢰하지 않는 데이터)

출력 <폴더>/sfx/
    onsets.csv       타격마다: 시각 · 박격자와의 거리 · 레벨 · 점프 · 길이 · 어택 · 중심주파수 · 저역/고역 비율 · 음정 · 종류(수치 판정)
    ramps.csv        라이저(상승)/다운스윕(하강) 후보 구간
    spec_NN.png      멜 스펙트로그램 8초 창 (타격 표시 · 박 표시 · 말 구간 음영)
    report.txt       요약 수치

«종류»는 수치 규칙 판정이다(귀로 들은 것이 아님). 초벌 분류기일 뿐이라 스펙트로그램을 눈으로 보고 고친다.
주의: ramps.csv(라이저/하강 후보)와 onsets.csv 의 att 열은 신뢰하지 않는다(시험 결과 쓸모 없음). 말 구간은 src.en-orig.json3 / src.ko-orig.json3 의 단어 시각에서 얻는다.
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SR = 44100
HOP = 256
FONT = None
try:
    from matplotlib import font_manager
    font_manager.fontManager.addfont(r"C:\Windows\Fonts\malgun.ttf")
    plt.rcParams["font.family"] = "Malgun Gothic"
except Exception:
    pass


def load_audio(folder, out):
    wav = out / "audio.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(folder / "src.mp4"), "-vn", "-ac", "1",
                    "-ar", str(SR), str(wav)], check=True)
    y, _ = librosa.load(str(wav), sr=SR, mono=True)
    return y


def voice_spans(folder):
    spans = []
    for name in ("src.ko-orig.json3", "src.en-orig.json3"):
        p = folder / name
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for e in d.get("events", []):
            segs = e.get("segs")
            if not segs or "tStartMs" not in e:
                continue
            ws = [(e["tStartMs"] + s.get("tOffsetMs", 0)) / 1000 for s in segs if s.get("utf8", "").strip()]
            for i, t in enumerate(ws):
                nxt = ws[i + 1] if i + 1 < len(ws) else t + 0.45
                spans.append((t, min(nxt, t + 0.6)))
        break
    spans.sort()
    merged = []
    for a, b in spans:
        if merged and a - merged[-1][1] < 0.5:
            merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
        else:
            merged.append((a, b))
    return merged


def in_spans(t, spans):
    return any(a - 0.05 <= t <= b + 0.05 for a, b in spans)


def db(x):
    return 20 * np.log10(np.maximum(x, 1e-9))


def main():
    folder = Path(sys.argv[1])
    out = folder / "sfx"
    out.mkdir(exist_ok=True)
    y = load_audio(folder, out)
    dur = len(y) / SR
    spans = voice_spans(folder)

    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=HOP)) ** 2
    freqs = librosa.fft_frequencies(sr=SR, n_fft=2048)
    ft = librosa.frames_to_time(np.arange(S.shape[1]), sr=SR, hop_length=HOP)
    tot = S.sum(axis=0) + 1e-12
    rms_db = 10 * np.log10(tot / S.shape[0])  # 상대 레벨

    # 박
    tempo, beats = librosa.beat.beat_track(y=y, sr=SR, hop_length=HOP)
    bt = librosa.frames_to_time(beats, sr=SR, hop_length=HOP)
    tempo = float(np.atleast_1d(tempo)[0])

    # 타격: 전체와 percussive 둘 다
    yh, yp = librosa.effects.hpss(y)
    oenv = librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP, aggregate=np.median, fmax=16000)
    on = librosa.onset.onset_detect(onset_envelope=oenv, sr=SR, hop_length=HOP, backtrack=False,
                                    delta=0.12, wait=int(0.06 * SR / HOP))
    ot = librosa.frames_to_time(on, sr=SR, hop_length=HOP)
    # percussive 에도 있는지
    penv = librosa.onset.onset_strength(y=yp, sr=SR, hop_length=HOP)
    hpr = (yh ** 2).sum() / ((yh ** 2).sum() + (yp ** 2).sum())

    lo_m = freqs < 150
    hi_m = freqs > 6000
    rows = []
    for t in ot:
        f0 = int(t * SR / HOP)
        a, b = f0, min(S.shape[1], f0 + int(0.8 * SR / HOP))
        if b - a < 4:
            continue
        env = rms_db[a:b]
        pk_i = int(np.argmax(env[: int(0.15 * SR / HOP)]))
        pk = env[pk_i]
        pk_t = ft[a + pk_i]
        # 길이: 피크에서 -20dB 아래로 내려갈 때까지(상한 0.8)
        below = np.where(env[pk_i:] < pk - 20)[0]
        dlen = (below[0] * HOP / SR) if len(below) else 0.8
        # 어택
        pre = rms_db[max(0, f0 - int(0.08 * SR / HOP)):a + pk_i + 1]
        thr = pk - 20
        idx = np.where(pre >= thr)[0]
        att = (len(pre) - idx[0]) * HOP / SR if len(idx) else 0.0
        # 직전 100ms 대비 점프
        pre_lvl = np.median(rms_db[max(0, f0 - int(0.12 * SR / HOP)):max(1, f0 - 1)]) if f0 > 3 else pk
        jump = pk - pre_lvl
        # 스펙트럼 (피크 직후 0~100ms)
        w0, w1 = a + max(0, pk_i - 1), min(S.shape[1], a + pk_i + int(0.1 * SR / HOP))
        sp = S[:, w0:w1].mean(axis=1)
        sp_tot = sp.sum() + 1e-12
        lo = sp[lo_m].sum() / sp_tot
        hi = sp[hi_m].sum() / sp_tot
        cen0 = float((sp * freqs).sum() / sp_tot)
        # 꼬리 중심 (150~300ms)
        e0, e1 = a + int(0.15 * SR / HOP), min(S.shape[1], a + int(0.3 * SR / HOP))
        cen1 = np.nan
        if e1 - e0 > 2:
            sp2 = S[:, e0:e1].mean(axis=1)
            cen1 = float((sp2 * freqs).sum() / (sp2.sum() + 1e-12))
        # 음정: 100~8000 대역에서 최대 봉우리와 중앙값 대비
        band = (freqs > 100) & (freqs < 8000)
        spb = 10 * np.log10(sp[band] + 1e-12)
        pi = int(np.argmax(spb))
        tonal = float(spb[pi] - np.median(spb))
        pitch = float(freqs[band][pi])
        # 음정 궤적 (피크 직후 3지점)
        tr = []
        for off in (0.02, 0.08, 0.16):
            k = min(S.shape[1] - 1, a + pk_i + int(off * SR / HOP))
            col = 10 * np.log10(S[band, k] + 1e-12)
            tr.append(float(freqs[band][int(np.argmax(col))]))
        # 박 거리
        bd = float(np.min(np.abs(bt - pk_t))) if len(bt) else np.nan
        # percussive 비중
        pe = float(penv[min(len(penv) - 1, f0 + 1)])
        # 같은 시각 말 위?
        vo = in_spans(pk_t, spans)
        rows.append(dict(t=round(float(pk_t), 3), onset=round(float(t), 3), beat_d=round(bd, 3), lvl=round(float(pk), 1),
                         jump=round(float(jump), 1), dur=round(float(dlen), 2), att=round(float(att), 3),
                         cen0=int(cen0), cen1=(int(cen1) if cen1 == cen1 else -1), lo=round(float(lo), 2),
                         hi=round(float(hi), 2), pitch=int(pitch), tonal=round(tonal, 1),
                         tr=",".join(str(int(x)) for x in tr), perc=round(pe, 1), voice=int(vo)))
    # 레벨을 음악 평균 대비로
    med = float(np.median(rms_db))
    for r in rows:
        r["rel_med"] = round(r["lvl"] - med, 1)
        r["kind"], r["conf"] = classify(r)

    # 램프(라이저 / 다운스윕): 고역(3~12k) 대역 에너지 dB 의 0.4초 선형 추세
    hb = (freqs > 3000) & (freqs < 12000)
    hdb = 10 * np.log10(S[hb].sum(axis=0) + 1e-12)
    ramps = []
    fps = SR / HOP
    win = int(0.45 * fps)
    sl = []
    for i in range(0, len(hdb) - win, 2):
        seg = hdb[i:i + win]
        x = np.arange(win) / fps
        k, c = np.polyfit(x, seg, 1)
        r2 = np.corrcoef(x, seg)[0, 1] ** 2
        sl.append((ft[i], k, r2, seg[-1] - seg[0]))
    cur = None
    for t, k, r2, dd in sl:
        kind = "상승" if (k > 18 and r2 > 0.7 and dd > 8) else ("하강" if (k < -22 and r2 > 0.7 and dd < -10) else None)
        if kind and cur and cur["kind"] == kind and t - cur["end"] < 0.12:
            cur["end"] = t + 0.45
            cur["gain"] = max(cur["gain"], abs(dd))
        elif kind:
            if cur:
                ramps.append(cur)
            cur = dict(kind=kind, start=t, end=t + 0.45, gain=abs(dd))
        else:
            if cur and t - cur["end"] > 0.12:
                ramps.append(cur)
                cur = None
    if cur:
        ramps.append(cur)

    with (out / "onsets.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with (out / "ramps.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kind", "start", "end", "gain_db"])
        for r in ramps:
            w.writerow([r["kind"], round(r["start"], 2), round(r["end"], 2), round(r["gain"], 1)])

    # 스펙트로그램
    M = librosa.feature.melspectrogram(y=y, sr=SR, n_fft=2048, hop_length=HOP, n_mels=128, fmax=16000)
    Md = librosa.power_to_db(M, ref=np.max)
    mf = librosa.mel_frequencies(n_mels=128, fmax=16000)
    WIN = 8.0
    n = int(np.ceil(dur / WIN))
    for k in range(n):
        a, b = k * WIN, min(dur, (k + 1) * WIN)
        fa, fb = int(a * fps), int(b * fps)
        fig, ax = plt.subplots(figsize=(16, 4.6), dpi=80)
        ax.imshow(Md[:, fa:fb], origin="lower", aspect="auto", cmap="magma", vmin=-70, vmax=0,
                  extent=[a, b, 0, 128])
        ticks = [10, 25, 45, 64, 84, 100, 118]
        ax.set_yticks(ticks)
        ax.set_yticklabels([f"{int(mf[i])}" for i in ticks], fontsize=7)
        for va, vb in spans:
            if vb > a and va < b:
                ax.axvspan(max(va, a), min(vb, b), ymin=0.0, ymax=0.04, color="cyan")
        for bb in bt:
            if a <= bb <= b:
                ax.axvline(bb, ymin=0.96, ymax=1.0, color="white", lw=1)
        for r in rows:
            if a <= r["t"] <= b:
                col = {"쿵/임팩트": "red", "킥(음악)": "orange", "클릭/틱": "lime", "팝/뿅": "yellow", "휙/쓸림": "deepskyblue",
                       "반짝/쉬머": "magenta", "타자/UI": "springgreen"}.get(r["kind"], "white")
                ax.axvline(r["t"], ymin=0.08, ymax=0.2, color=col, lw=1.5)
                ax.text(r["t"], 6, f'{r["t"]:.2f}\n{r["kind"][:2]}', color=col, fontsize=6, ha="center", va="bottom")
        for r in ramps:
            if r["end"] > a and r["start"] < b:
                ax.axvspan(max(r["start"], a), min(r["end"], b), ymin=0.9, ymax=0.96,
                           color="deepskyblue" if r["kind"] == "상승" else "salmon")
        ax.set_xlim(a, b)
        ax.set_xticks(np.arange(np.ceil(a), b + 0.01, 0.5))
        ax.tick_params(axis="x", labelsize=7)
        fig.tight_layout()
        fig.savefig(out / f"spec_{k:02d}_{a:.0f}-{b:.0f}.png")
        plt.close(fig)

    nvo = [r for r in rows if r["voice"]]
    kinds = {}
    for r in rows:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    with (out / "report.txt").open("w", encoding="utf-8") as f:
        f.write(f"길이 {dur:.2f}s · BPM(librosa) {tempo:.1f} · 박 {len(bt)} · HPSS 하모닉 비중 {hpr:.2f}\n")
        f.write(f"onset {len(rows)} (분당 {len(rows) / dur * 60:.0f}) · 말 위 {len(nvo)} · 말 구간 {len(spans)}개 {sum(b - a for a, b in spans):.1f}s\n")
        f.write(f"종류별 {kinds}\n")
        f.write(f"램프 {len(ramps)} 개\n")
    print((out / "report.txt").read_text(encoding="utf-8"))


def classify(r):
    lo, hi, dur, att, cen0, cen1, tonal, jump = r["lo"], r["hi"], r["dur"], r["att"], r["cen0"], r["cen1"], r["tonal"], r["jump"]
    tr = [int(x) for x in r["tr"].split(",")]
    glide = (tr[2] - tr[0]) / max(tr[0], 1)
    if lo > 0.55 and dur < 0.18:
        return "킥(음악)", "중"
    if lo > 0.45 and dur >= 0.18:
        return "쿵/임팩트", "중" if lo > 0.6 else "하"
    if hi > 0.4 and dur < 0.12:
        return "클릭/틱", "중"
    if tonal > 28 and 0.08 <= dur <= 0.9 and cen0 > 1200:
        if cen0 > 3500 and dur > 0.2:
            return "반짝/쉬머", "중"
        return "팝/뿅", "중" if abs(glide) > 0.25 or dur < 0.4 else "하"
    if hi > 0.25 and dur >= 0.12:
        if cen1 > 0 and cen1 < cen0:
            return "휙/쓸림", "중"
        return "휙/쓸림", "하"
    if hi > 0.2 and dur < 0.25:
        return "클릭/틱", "하"
    return "기타", "하"


if __name__ == "__main__":
    main()
