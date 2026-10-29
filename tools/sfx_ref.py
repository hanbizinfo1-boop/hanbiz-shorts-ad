# -*- coding: utf-8 -*-
r"""레퍼런스 영상의 효과음 해부 — 타격마다 길이·어택·스펙트럼·저역/고역 비중·음정을 재고 종류를 «수치로» 판정한다.

    python -I tools/sfx_ref.py <폴더> [스펙트로그램 폭 초=10]          # <폴더>/src.mp4 (yt-dlp 로 받은 것, 신뢰하지 않는 데이터 — 경로로만 읽는다)
출력 <폴더>/sfx/
    events.csv   타격 목록 (시각 · 레벨 · 점프 · 길이 · 어택 · 중심 · 중심변화 · 저역 · 고역 · 평탄도 · 음정비(hfrac) · 고역점프(hjump) · 박 위 여부 · 화면변화 시차(vis_dt, +=소리가 늦음) · 종류 · 확신)
    spec_NN.png  10초씩 스펙트로그램 + 레벨 곡선 + 타격 표시 (눈으로 소리를 보는 용도)
    stats.txt    밀도 · 종류 비율 · percussive/harmonic RMS · 소리 비움 구간 · 라이저 앞선 타격

소리는 귀로 듣지 못했다 — 종류는 전부 수치 판정이고 «확신»은 규칙에 얼마나 깔끔히 들어맞았나일 뿐이다.
음악과 효과음은 나누지 못한다(HPSS 로도 합성음·드럼이 섞여 나온다) — 스펙트로그램을 눈으로 같이 본다.
"""
import csv
import subprocess
import sys
from pathlib import Path

import numpy as np
import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SR = 44100
N_FFT = 2048
HOP = 256


def load(folder):
    wav = folder / "sfx" / "audio.wav"
    wav.parent.mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(folder / "src.mp4"), "-vn", "-ac", "1",
                    "-ar", str(SR), str(wav)], check=True)
    y, _ = librosa.load(str(wav), sr=SR, mono=True)
    return y


def video_diff(folder):
    """원본 fps 그대로 프레임 차이(회색 96x54) -> (fps, diff[i] = 프레임 i 와 i-1 의 평균 절대차)"""
    import json
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                         "-of", "json", str(folder / "src.mp4")], capture_output=True, text=True, check=True)
    a, b = json.loads(pr.stdout)["streams"][0]["r_frame_rate"].split("/")
    fps = float(a) / float(b)
    W, Hh = 96, 54
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(folder / "src.mp4"), "-an", "-vf", f"scale={W}:{Hh},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, Hh, W).astype(np.float32)
    d = np.zeros(len(fr), np.float32)
    d[1:] = np.abs(fr[1:] - fr[:-1]).mean(axis=(1, 2))
    return fps, d


def db(x):
    return 20 * np.log10(np.maximum(x, 1e-9))


def main():
    folder = Path(sys.argv[1])
    y = load(folder)
    out = folder / "sfx"
    dur = len(y) / SR
    S = np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP))
    freqs = librosa.fft_frequencies(sr=SR, n_fft=N_FFT)
    ft = librosa.frames_to_time(np.arange(S.shape[1]), sr=SR, hop_length=HOP)
    rms = librosa.feature.rms(S=S, frame_length=N_FFT, hop_length=HOP)[0]
    rms_db = db(rms)
    # 평탄도(잡음 같은지) / 중심
    flat = librosa.feature.spectral_flatness(S=S[(freqs > 100) & (freqs < 8000)])[0]
    cent = librosa.feature.spectral_centroid(S=S, sr=SR)[0]
    # 고역 (>1.5kHz) 곡선 — 라이저 찾기용
    hi_env = db(np.sqrt((S[freqs > 1500] ** 2).mean(axis=0)))
    # harmonic / percussive
    H, P = librosa.decompose.hpss(S, margin=2.0)
    h_rms = np.sqrt((H ** 2).mean()); p_rms = np.sqrt((P ** 2).mean())
    p_rms_t = db(np.sqrt((P ** 2).mean(axis=0)))
    h_rms_t = db(np.sqrt((H ** 2).mean(axis=0)))
    # 박
    onset_env = librosa.onset.onset_strength(S=librosa.amplitude_to_db(S), sr=SR, hop_length=HOP)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=SR, hop_length=HOP)
    beat_t = librosa.frames_to_time(beats, sr=SR, hop_length=HOP)
    tempo = float(np.atleast_1d(tempo)[0])
    # 타격 검출: 퍼커시브 성분 + 전체 합집합
    env = librosa.onset.onset_strength(S=librosa.amplitude_to_db(P), sr=SR, hop_length=HOP)
    on_p = librosa.onset.onset_detect(onset_envelope=env, sr=SR, hop_length=HOP, delta=0.25, wait=8, units="frames")
    on_f = librosa.onset.onset_detect(onset_envelope=onset_env, sr=SR, hop_length=HOP, delta=0.25, wait=8, units="frames")
    from scipy.signal import find_peaks
    d6 = np.zeros_like(rms_db); d6[:-8] = rms_db[8:] - rms_db[:-8]   # 약 46ms 사이 레벨 상승
    on_r = find_peaks(d6, height=4.0, distance=int(0.05 * SR / HOP))[0]
    hi6 = db(np.sqrt((S[freqs > 6000] ** 2).mean(axis=0)))      # 고역(>6kHz) 곡선 — 잡음성 효과음은 여기서 튄다
    dh = np.zeros_like(hi6); dh[:-8] = hi6[8:] - hi6[:-8]
    on_h = find_peaks(dh, height=9.0, distance=int(0.05 * SR / HOP))[0]
    on = []
    for f in sorted(set(on_p) | set(on_f) | set(on_r) | set(on_h)):  # 합집합 — 50ms 안에서 겹치면 하나
        if not on or (f - on[-1]) * HOP / SR > 0.05:
            on.append(f)
    sm = 5  # 프레임 평활(약 30ms)
    rs = np.convolve(rms_db, np.ones(sm) / sm, mode="same")
    rows = []
    vfps, vd = video_diff(folder)
    fps = SR / HOP
    for f in on:
        t = ft[f]
        i0 = max(0, f - int(0.1 * fps))
        pre = np.mean(rms_db[i0:max(i0 + 1, f - 1)]) if f > 1 else -90
        w = slice(f, min(len(rms_db), f + int(0.6 * fps)))
        seg = rms_db[w]
        if len(seg) < 3:
            continue
        pk = int(np.argmax(seg)); level = seg[pk]
        jump = level - pre
        hjump = hi6[min(len(hi6) - 1, f + 4)] - np.mean(hi6[i0:max(i0 + 1, f - 1)]) if f > 1 else 0
        if jump < 3.0 and hjump < 9.0:
            continue
        attack = pk / fps * 1000
        # 길이: 정점 후 -20dB 아래로 내려갈 때까지 (최대 1.5초)
        w2 = rs[f:min(len(rs), f + int(1.5 * fps))]
        below = np.where(w2 < level - 20)[0]
        length = (below[0] if len(below) else len(w2)) / fps
        # 스펙트럼 (정점부터 120ms)
        a = f + pk; b = min(S.shape[1], a + int(0.12 * fps))
        sp = (S[:, a:b] ** 2).mean(axis=1)
        tot = sp.sum() + 1e-12
        low = sp[freqs < 150].sum() / tot
        high = sp[freqs > 6000].sum() / tot
        c0 = float(np.mean(cent[a:b]))
        c2s = min(len(cent) - 1, a + int(0.25 * fps)); c2e = min(len(cent), c2s + int(0.1 * fps))
        c1 = float(np.mean(cent[c2s:c2e])) if c2e > c2s else c0
        fl = float(np.mean(flat[f:min(len(flat), f + int(0.25 * fps))]))
        hf = float((H[:, a:b] ** 2).sum() / ((H[:, a:b] ** 2).sum() + (P[:, a:b] ** 2).sum() + 1e-12))
        # 박 위 여부
        bd = float(np.min(np.abs(beat_t - t))) if len(beat_t) else 9
        # 라이저: 직전 고역 곡선이 단조 상승
        riser = 0.0
        for L in (4.0, 3.0, 2.0, 1.5, 1.0, 0.6):
            s0 = max(0, f - int(L * fps)); s1 = max(s0 + 3, f - 1)
            c = np.convolve(hi_env[s0:s1], np.ones(9) / 9, mode="valid")
            if len(c) < 5:
                continue
            if c[-1] - c[0] >= 10 and np.mean(np.diff(c) > -0.05) > 0.8:
                riser = L; break
        # 화면 변화: 소리 시각 ±0.3초 안에서 프레임 차이가 가장 큰 프레임 (소리 - 화면, 양수 = 소리가 화면보다 늦음)
        i0 = max(0, int((t - 0.3) * vfps)); i1 = min(len(vd), int((t + 0.3) * vfps) + 1)
        vis_dt, vis_mag = "", 0.0
        if i1 > i0:
            k = int(np.argmax(vd[i0:i1])); vis_mag = float(vd[i0 + k])
            if vis_mag >= 2.0:
                vis_dt = round(t - (i0 + k) / vfps, 3)
        # 종류 판정
        kind, conf = "기타", "낮음"
        if length < 0.08 and c0 > 3000:
            kind, conf = "클릭/틱", "중"
        elif hjump >= 9 and high > 0.03 and fl > 0.05 and hf < 0.9:
            kind, conf = "고역 잡음 타격(휙/클릭류)", "낮음"
        elif attack < 35 and low > 0.35:
            kind, conf = "쿵/임팩트", "중" if low > 0.5 else "낮음"
        elif length <= 0.30 and fl < 0.04 and c0 < 4500:
            kind, conf = "팝/뿅(음정)", "낮음"
        elif 0.15 <= length <= 0.8 and fl > 0.08 and abs(c1 - c0) > 600:
            kind, conf = "휙/쓸림", "중"
        elif high > 0.15 and length > 0.4:
            kind, conf = "반짝/쉬머", "낮음"
        elif attack < 35 and length < 0.5:
            kind, conf = "임팩트(저역 작음)", "낮음"
        elif hf > 0.6 and fl < 0.15:
            kind, conf = "음정(보컬/멜로디)", "낮음"
        rows.append(dict(t=round(t, 3), level=round(level, 1), jump=round(jump, 1), len=round(length, 2),
                         attack=round(attack), cent=round(c0), dcent=round(c1 - c0), low=round(low, 2),
                         high=round(high, 2), flat=round(fl, 3), hfrac=round(hf, 2), hjump=round(float(hjump), 1), beat_d=round(bd, 3),
                         on_beat=int(bd < 0.04), vis_dt=vis_dt, vis_mag=round(vis_mag, 1), riser=riser, kind=kind, conf=conf))
    with open(out / "events.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    # 소리 비움: percussive 곡선이 중앙값보다 15dB 낮은 0.3초 이상
    thr = np.median(p_rms_t) - 12
    quiet = p_rms_t < thr
    gaps = []; s = None
    for i, q in enumerate(quiet):
        if q and s is None: s = i
        if (not q or i == len(quiet) - 1) and s is not None:
            if (i - s) / fps >= 0.3: gaps.append((round(ft[s], 2), round(ft[i], 2)))
            s = None
    # 전체 레벨이 15dB 이상 떨어지는 비움
    thr2 = np.percentile(rms_db, 90) - 15
    q2 = rms_db < thr2; g2 = []; s = None
    for i, q in enumerate(q2):
        if q and s is None: s = i
        if (not q or i == len(q2) - 1) and s is not None:
            if (i - s) / fps >= 0.25: g2.append((round(ft[s], 2), round(ft[i], 2)))
            s = None
    kinds = {}
    for r in rows: kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    with open(out / "stats.txt", "w", encoding="utf-8") as fh:
        fh.write(f"길이 {dur:.1f}s · 타격(점프>=3dB) {len(rows)}개 = 분당 {len(rows) / dur * 60:.1f} · 강한(점프>=6dB) {sum(r['jump'] >= 6 for r in rows)}\n")
        fh.write(f"BPM {tempo:.1f} · 박 {len(beat_t)} · 박 위 타격 {sum(r['on_beat'] for r in rows)} / 박 밖 {sum(1 - r['on_beat'] for r in rows)}\n")
        fh.write(f"percussive RMS {db(p_rms):.1f} dB · harmonic RMS {db(h_rms):.1f} dB · 차 {db(p_rms) - db(h_rms):+.1f} dB\n")
        fh.write("종류: " + ", ".join(f"{k} {v}" for k, v in sorted(kinds.items(), key=lambda x: -x[1])) + "\n")
        fh.write(f"perc 곡선 비움(중앙값-12dB, 0.3s+): {gaps}\n")
        fh.write(f"전체 레벨 비움(상위10%-15dB, 0.25s+): {g2}\n")
        fh.write(f"라이저 앞선 타격: {[(r['t'], r['riser']) for r in rows if r['riser']]}\n")
    # 스펙트로그램 이미지
    M = librosa.amplitude_to_db(librosa.feature.melspectrogram(S=S ** 2, sr=SR, n_mels=96, fmax=16000), ref=np.max)
    tm = ft
    step = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
    n = int(np.ceil(dur / step))
    for k in range(n):
        a, b = k * step, min(dur, (k + 1) * step)
        fa, fb = int(a * fps), min(M.shape[1], int(b * fps))
        fig, ax = plt.subplots(2, 1, figsize=(18, 6.5), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
        ax[0].imshow(M[:, fa:fb], origin="lower", aspect="auto", extent=[a, b, 0, 16], cmap="magma", vmin=-70, vmax=0)
        ax[0].set_ylabel("kHz(mel)")
        ax[1].plot(tm[fa:fb], rms_db[fa:fb], "k", lw=0.8, label="all")
        ax[1].plot(tm[fa:fb], p_rms_t[fa:fb], "r", lw=0.6, label="perc")
        ax[1].plot(tm[fa:fb], h_rms_t[fa:fb], "b", lw=0.6, label="harm")
        ax[1].set_ylim(-70, 0); ax[1].set_ylabel("dB")
        for r in rows:
            if a <= r["t"] < b:
                for x in ax: x.axvline(r["t"], color="cyan" if r["on_beat"] else "lime", lw=0.7, alpha=0.8)
                ax[0].text(r["t"], 15, f"{r['t']:.2f}", color="w", fontsize=6, rotation=90, va="top")
        for bt in beat_t:
            if a <= bt < b: ax[1].axvline(bt, color="gray", lw=0.3, ls=":")
        ax[1].set_xlim(a, b); ax[1].legend(loc="upper right", fontsize=6)
        plt.tight_layout(); plt.savefig(out / f"spec_{k:02d}.png", dpi=70); plt.close(fig)
    print((out / "stats.txt").read_text(encoding="utf-8"))
    print(f"events {len(rows)} -> {out / 'events.csv'}")


if __name__ == "__main__":
    main()
