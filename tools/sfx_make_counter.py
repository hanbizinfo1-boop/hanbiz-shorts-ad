"""숫자 «세는» 효과음 만들기 — 짧은 클릭 두 개를 번갈아, 빠르게 시작해 점점 느려지며 멈춘다(숫자 굴림과 같은 감속).

10-12 사장님 «다음 연출은 효과음이 좀더 숫자 세는느낌으로 했으면좋겠고». 한 줄 굴림 = 파일 하나(효과음 규칙 5-2·5-2b 는 파일 단위라
틱 하나하나를 큐로 넣으면 같은 파일 반복에 걸린다 — 묶어서 소리 하나로 만든다).
    python tools/sfx_make_counter.py <출력.wav> [--dur 0.62] [--a KN_click_001.wav] [--b KN_click_003.wav] [--seed 0]
원본은 Kenney(CC0). 마지막 틱은 조금 크게(멈춤 확인).
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import sfx  # noqa: E402

SR = 48000


def load(name):
    p = sfx.find_file(name)
    b = subprocess.run(["ffmpeg", "-v", "quiet", "-i", str(p), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True, check=True).stdout
    x = np.frombuffer(b, np.float32).copy()
    return x / (np.abs(x).max() + 1e-9)


def main():
    ap = argparse.ArgumentParser(description="숫자 세는 틱 연속 효과음")
    ap.add_argument("out")
    ap.add_argument("--dur", type=float, default=0.62, help="굴림 길이(초) — 화면 숫자가 멈추는 시각")
    ap.add_argument("--a", default="KN_click_001.wav")
    ap.add_argument("--b", default="KN_click_003.wav")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    ta, tb = load(a.a), load(a.b)
    times, t, i = [], 0.0, 0
    while t <= a.dur:                       # 간격 28ms → 약 120ms 로 늘어난다(감속)
        times.append(t)
        k = t / a.dur
        t += 0.028 + 0.092 * k * k
        i += 1
    times[-1] = a.dur
    rng = np.random.default_rng(a.seed)
    y = np.zeros(int(SR * (a.dur + 0.25)), np.float32)
    for j, tt in enumerate(times):
        s = ta if j % 2 == 0 else tb
        g = 0.55 + 0.1 * rng.random()
        if j == len(times) - 1:
            g = 1.0
        n0 = int(tt * SR)
        seg = s[: len(y) - n0] * g
        y[n0:n0 + len(seg)] += seg
    y = y / (np.abs(y).max() + 1e-9) * 10 ** (-1 / 20)
    subprocess.run(["ffmpeg", "-v", "quiet", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le", a.out],
                   input=y.tobytes(), check=True)
    print(f"{a.out}  틱 {len(times)}개 · {a.dur:.2f}초")


if __name__ == "__main__":
    main()
