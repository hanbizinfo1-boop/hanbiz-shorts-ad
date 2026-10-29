"""녹음본 잡음 진단 — 숨·무음 바닥 · 파열음(«바»「퍼」 공기 터짐) · 지지직(딸깍 잡음) 위치를 숫자로.

python 지시작업/tools/vo_audit.py <wav(모노, 48k)>
정리 전후를 같은 기준으로 재서 비교한다(vo_clean.py 결과 확인용).
"""
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt


def db(v):
    return 20 * np.log10(np.maximum(v, 1e-9))


def frames(x, n, hop):
    k = 1 + (len(x) - n) // hop
    idx = np.arange(n)[None, :] + hop * np.arange(k)[:, None]
    return x[idx]


def audit(path, show=True):
    x, sr = sf.read(path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    n, hop = int(0.02 * sr), int(0.01 * sr)
    full = np.sqrt((frames(x, n, hop) ** 2).mean(axis=1))
    lo = sosfilt(butter(4, 120, "low", fs=sr, output="sos"), x)
    low = np.sqrt((frames(lo, n, hop) ** 2).mean(axis=1))
    hi = sosfilt(butter(4, 5000, "high", fs=sr, output="sos"), x)

    floor = np.percentile(db(full), 5)                       # 말 사이 바닥
    speech = np.percentile(db(full), 90)
    # 파열음: 120Hz 아래가 전체의 절반 이상을 먹는 20ms (말소리 기본음은 대개 120Hz 위)
    pl = np.where((db(low) - db(full) > -3) & (db(full) > speech - 20))[0]
    # 지지직: 5kHz 위에서 앞뒤 3ms 평균의 8배 넘게 튀는 표본
    env = np.abs(hi)
    k = int(0.003 * sr)
    ma = np.convolve(env, np.ones(2 * k) / (2 * k), "same")
    cl = np.where((env > 8 * ma) & (env > 10 ** ((floor + 6) / 20)))[0]

    def groups(idx, gap):
        out = []
        for i in idx:
            if out and i - out[-1][-1] <= gap:
                out[-1].append(i)
            else:
                out.append([i])
        return out

    plg = [g[0] * hop / sr for g in groups(pl, 5)]
    clg = [g[0] / sr for g in groups(cl, int(0.02 * sr))]
    if show:
        print(f"{path}: 길이 {len(x)/sr:.2f}s · 말 {speech:.1f} dB · 바닥 {floor:.1f} dB · 신호대잡음 {speech-floor:.1f} dB")
        print(f"  파열음 의심 {len(plg)}곳: " + " ".join(f"{t:.2f}" for t in plg[:40]))
        print(f"  딸깍·지지직 의심 {len(clg)}곳: " + " ".join(f"{t:.2f}" for t in clg[:60]))
    return dict(floor=floor, speech=speech, plosive=plg, click=clg)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        audit(p)
