"""BGM 후보 실측: BPM · 길이 · LUFS · 첫 히트/드롭 · 대역 비중 · 마디 경계(30초/15초).

사용: python -I tools/bgm_analyze.py <입력폴더> <결과.json> [동시프로세스수]
소리는 귀로 듣지 않는다 — 전부 신호 분석 값이다.
"""
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

MAXSEC = 150.0


def lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    lra = re.findall(r"LRA:\s+(-?[\d.]+) LU", r.stderr)
    return (float(m[-1]) if m else None), (float(lra[-1]) if lra else None)


def probe_dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def nearest_bar(t_target, first, bar):
    k = round((t_target - first) / bar)
    return round(first + max(k, 1) * bar, 2)


def analyze(path):
    import librosa
    out = {"file": os.path.basename(path)}
    try:
        out["duration_s"] = round(probe_dur(path), 2)
        out["lufs"], out["lra"] = lufs(path)
        y, sr = librosa.load(path, sr=22050, mono=True, duration=MAXSEC)
        hop = 512
        oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
        tempo, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=sr, hop_length=hop)
        bt = librosa.frames_to_time(beats, sr=sr, hop_length=hop)
        tempo = float(np.atleast_1d(tempo)[0])
        if len(bt) > 12:
            # 프레임 해상도 양자화를 줄이려고 8박 간격 시간차의 중앙값으로 박 간격을 구한다
            ibi = float(np.median((bt[8:] - bt[:-8]) / 8.0))
            bpm = 60.0 / ibi
        else:
            ibi, bpm = 60.0 / tempo, tempo
        out["bpm"] = round(bpm, 1)
        out["bpm_tracker"] = round(tempo, 1)
        # 첫 강한 히트: 온셋 세기가 99퍼센타일의 60% 를 처음 넘는 시각(0.3초 이후)
        times = librosa.frames_to_time(np.arange(len(oenv)), sr=sr, hop_length=hop)
        thr = 0.6 * np.percentile(oenv, 99)
        idx = np.where((oenv > thr) & (times > 0.3))[0]
        out["first_hit_s"] = round(float(times[idx[0]]), 2) if len(idx) else None
        # 드롭: 8초 이후, 1초 RMS 가 직전 4초 평균보다 가장 크게 오르는 지점(4dB 이상일 때만)
        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
        db = 20 * np.log10(rms + 1e-9)
        fps = sr / hop
        w1, w4 = int(fps), int(4 * fps)
        best, besti = 0.0, None
        for i in range(max(w4, int(8 * fps)), len(db) - w1, int(fps / 4)):
            rise = db[i:i + w1].mean() - db[i - w4:i].mean()
            if rise > best:
                best, besti = rise, i
        out["drop_s"] = round(besti / fps, 2) if besti is not None and best >= 4.0 else None
        out["drop_db"] = round(float(best), 1) if out["drop_s"] is not None else None
        # 대역 비중
        S = np.abs(librosa.stft(y, n_fft=2048, hop_length=1024)) ** 2
        f = librosa.fft_frequencies(sr=sr, n_fft=2048)
        tot = S.sum()
        out["low_pct"] = round(100 * S[f < 250].sum() / tot, 1)
        out["mid_pct"] = round(100 * S[(f >= 250) & (f < 4000)].sum() / tot, 1)
        out["high_pct"] = round(100 * S[f >= 4000].sum() / tot, 1)
        out["voice_1_4k_pct"] = round(100 * S[(f >= 1000) & (f < 4000)].sum() / tot, 1)
        # 마디 경계(4/4 가정): 첫 비트 기준 4박 격자에서 30초·15초에 가장 가까운 지점
        if len(bt):
            bar = 4 * ibi
            first = float(bt[0])
            dur = out["duration_s"]
            out["bar_s"] = round(bar, 3)
            out["first_beat_s"] = round(first, 2)
            out["loop30_s"] = nearest_bar(30, first, bar) if dur > 32 else None
            out["loop15_s"] = nearest_bar(15, first, bar) if dur > 17 else None
        out["ok"] = True
    except Exception as e:  # noqa
        out["ok"] = False
        out["error"] = str(e)[:200]
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    files = sorted(os.path.join(src, f) for f in os.listdir(src) if f.lower().endswith((".mp3", ".wav")))
    res = []
    if os.path.exists(dst):
        res = json.load(open(dst, encoding="utf-8"))
    done = {r["file"] for r in res}
    todo = [p for p in files if os.path.basename(p) not in done]
    with ProcessPoolExecutor(n) as ex:
        for i, r in enumerate(ex.map(analyze, todo), 1):
            res.append(r)
            print(i, len(todo), r["file"], r.get("bpm"), r.get("lufs"), flush=True)
            if i % 20 == 0:
                json.dump(res, open(dst, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1, default=float)
    json.dump(res, open(dst, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    main()
