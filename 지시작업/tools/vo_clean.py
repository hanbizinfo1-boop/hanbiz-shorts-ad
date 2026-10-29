"""녹음본 잡음 정리 — 파열음(«바» 공기 터짐) · 지지직(딸깍) · 바닥 쉬익 · 음량 맞춤.

python 지시작업/tools/vo_clean.py <원본> <출력.wav> [--lufs -14]
원본은 읽기만 한다. 결과는 48k · 24bit · 스테레오(같은 소리 두 채널 — 프리미어에 그대로 얹게).

순서와 이유 (10-26 퓨레바 녹음 실측: 말 −18dB · 바닥 −48dB · 파열음 자리는 200Hz 아래만 평소보다 15~20dB 튐)
1. highpass 70Hz   — 목소리 아래 웅웅·책상 울림.
2. 파열음 누르기    — 180Hz 아래만 떼어(zero-phase 저역 + 원음−저역 = 합치면 원래대로) 그 대역에 «미리 보는»
                      리미터를 건다. 기준 = 평소 말의 저음 최고치(97번째 백분위) + 2dB → 튀는 순간만 눌리고
                      평소 목소리 몸통은 그대로. 압축기(acompressor)로는 −8dB 밖에 안 줄어서 바꿈.
3. 딸깍 지우기      — 5kHz 위에서 1.5ms 안에 끝나는 외톨이 바늘(주변 3ms 평균의 6배)만 골라 그 고역을 깎는다.
                      ㅋ·ㅌ·ㅊ 같은 자음은 수 ms 이어지는 쉬익이라 안 걸린다. 그 뒤 adeclick 로 한 번 더.
4. afftdn          — 바닥 쉬익을 약하게(10dB). 세게 걸면 물속 같은 소리가 난다.
                      ★ afftdn 은 소리를 1200표본(48k 에서 25ms) 늦춘다 — 뒤에 같은 만큼 붙이고 앞을 잘라 원본과 맞춤.
                      끝에 원본 대비 어긋남을 상호상관으로 재서 0 이 아니면 멈춘다(프리미어에서 원본 자리에 바꿔 끼우게).
5. loudnorm 2회    — 스테레오 기준 통합 −14 LUFS · 트루피크 −1.5dB.
"""
import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.ndimage import maximum_filter1d, uniform_filter1d
from scipy.signal import butter, sosfiltfilt

SPLIT = 180
FFTDN_DELAY = 1200  # afftdn 지연(48k) — 실측 10-26, 아래 check_offset 이 매번 다시 잰다
FFCHAIN = (f"adeclick=w=10:o=50:t=3,apad=pad_len={FFTDN_DELAY},afftdn=nr=10:nf=-50:tn=1,"
           f"atrim=start_sample={FFTDN_DELAY},asetpts=PTS-STARTPTS")


def declick(x, sr):
    hp = x - sosfiltfilt(butter(4, 5000, "low", fs=sr, output="sos"), x)
    env = np.abs(hp)
    local = uniform_filter1d(env, int(0.003 * sr))
    floor = np.percentile(env, 50)
    spike = (env > 6 * local) & (env > 8 * floor)
    idx = np.flatnonzero(spike)
    g = np.ones_like(x)
    span, pad, hits = int(0.0015 * sr), int(0.001 * sr), 0
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and idx[j + 1] - idx[j] < pad:
            j += 1
        a, b = idx[i], idx[j]
        if b - a <= span:
            s, e = max(0, a - pad), min(len(x), b + pad)
            w = np.hanning(e - s)
            g[s:e] = np.minimum(g[s:e], 1 - 0.9 * w)
            hits += 1
        i = j + 1
    return x - hp * (1 - g), hits


def check_offset(src, out, sr):
    s = int(min(10, len(src) / sr / 3) * sr)
    a, b = src[s:s + 5 * sr], out[s:s + 5 * sr]
    m = 3000
    c = np.correlate(b, a[m:-m], "valid")
    return int(np.argmax(c)) - m


def deplosive(x, sr):
    x = sosfiltfilt(butter(2, 70, "high", fs=sr, output="sos"), x)
    low = sosfiltfilt(butter(4, SPLIT, "low", fs=sr, output="sos"), x)
    high = x - low
    # 저역 포락선: 6ms 창 최대값 → 앞뒤로 퍼진(미리 보는) 값
    env = maximum_filter1d(np.abs(low), int(0.006 * sr))
    speech = maximum_filter1d(np.abs(x), int(0.02 * sr)) > 10 ** (-30 / 20)
    thr = np.percentile(env[speech], 97) * 10 ** (2 / 20)
    gain = np.minimum(1.0, thr / np.maximum(env, 1e-9))
    # 바로 떨어지고(앞 5ms 미리) 천천히 돌아오게: 최소값 퍼뜨린 뒤 30ms 평균
    gain = -maximum_filter1d(-gain, int(0.01 * sr))
    gain = uniform_filter1d(gain, int(0.03 * sr))
    n_hit = int((gain < 0.7).sum() / (0.01 * sr))
    return high + low * gain, thr, n_hit


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--lufs", type=float, default=-14.0)
    a = ap.parse_args()

    with tempfile.TemporaryDirectory() as td:
        mono = Path(td) / "mono.wav"
        run(["ffmpeg", "-v", "error", "-y", "-i", a.src, "-ac", "1", "-ar", "48000", "-c:a", "pcm_f32le", str(mono)])
        x, sr = sf.read(mono)
        y, thr, n_hit = deplosive(x, sr)
        y, n_click = declick(y, sr)
        stage = Path(td) / "dep.wav"
        sf.write(stage, y, sr, subtype="FLOAT")

        pre = f"[0:a]{FFCHAIN},pan=stereo|c0=c0|c1=c0"
        r = run(["ffmpeg", "-hide_banner", "-i", str(stage), "-filter_complex",
                 f"{pre},loudnorm=I={a.lufs}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"])
        m = json.loads(re.findall(r"\{[^{}]*\}", r.stderr)[-1])
        ln = (f"loudnorm=I={a.lufs}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
              f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}"
              ":linear=true")
        run(["ffmpeg", "-hide_banner", "-y", "-i", str(stage), "-filter_complex",
             f"{pre},{ln},aresample=48000[o]", "-map", "[o]", "-c:a", "pcm_s24le", a.out])
        o, _ = sf.read(a.out)
        off = check_offset(x, o.mean(axis=1), sr)
        if off or len(o) != len(x):
            raise SystemExit(f"원본과 어긋남 {off}표본 · 길이 차 {len(o) - len(x)}표본 — 납품 금지")
    print(f"파열음 리미터 기준 {20*np.log10(thr):.1f} dBFS · 눌린 구간 약 {n_hit}×10ms · 딸깍 {n_click}곳 지움")
    print("원본 대비 어긋남 0표본 · 길이 같음")
    print("정리 후 · 음량 맞추기 전:", m["input_i"], "LUFS · TP", m["input_tp"])
    print(a.out)


if __name__ == "__main__":
    main()
