"""역재생 흡입(suck-back) 효과음 만들기 — 원본에 울림 꼬리를 붙인 뒤 뒤집는다.

원본은 출처가 안전한 것만(Kenney CC0 · 직접 만든 것). 効果音ラボ(SEL_)는 가공본 재배포 금지라 쓰지 않는다(sfx.md 9장).
    python tools/sfx_make_reverse.py <원본.wav> <출력.wav> [--len 0.6] [--echo 0.8]
출력 끝 = 원본의 시작(타격 정점) → 배치할 때 `align: peak` 로 정점을 컷 시각에.
측정(--measure)만 하면: 길이 · 정점 위치(끝에서 몇 초) · 오름 단조성 · 고역 비중을 낸다.
"""
import argparse
import subprocess
import sys

import numpy as np

SR = 48000


def load(path):
    b = subprocess.run(["ffmpeg", "-v", "quiet", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True, check=True).stdout
    return np.frombuffer(b, np.float32).copy()


def measure(x):
    """흡입 소리로 쓸 만한지 보는 수치."""
    n = len(x)
    hop = int(SR * 0.02)
    env = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2) + 1e-12) for i in range(0, n - hop, hop)])
    db = 20 * np.log10(env + 1e-9)
    pk = int(np.argmax(env))
    # 오름 단조성: 정점 앞 구간에서 20ms 창이 앞 창보다 커진 비율
    rise = db[:pk + 1]
    mono = float(np.mean(np.diff(rise) > -0.5)) if len(rise) > 2 else 0.0
    # 들리는 오름 길이: 정점 −30dB 을 처음 넘는 곳부터 정점까지
    above = np.where(db[:pk + 1] > db[pk] - 30)[0]
    rise_s = (pk - above[0]) * hop / SR if len(above) else 0.0
    S = np.abs(np.fft.rfft(x)) ** 2
    fr = np.fft.rfftfreq(n, 1 / SR)
    hi = float(S[fr > 2000].sum() / S.sum())
    low = float(S[fr < 150].sum() / S.sum())
    return {"길이": n / SR, "정점_끝에서": (n - pk * hop) / SR, "들리는_오름": rise_s,
            "오름_단조": mono, "고역>2k": hi, "저역<150": low}


def make(src, length, echo):
    x = load(src)
    # 울림 꼬리: aecho 여러 겹(이 PC ffmpeg 엔 reverb 필터 없음 — sfx.md 참고)
    delays = "|".join(str(int(d)) for d in (37, 61, 97, 149, 223))
    decays = "|".join(f"{echo * k:.2f}" for k in (0.8, 0.65, 0.5, 0.38, 0.28))
    p = subprocess.run(["ffmpeg", "-v", "quiet", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-af", f"apad=pad_dur=1.5,aecho=0.9:0.9:{delays}:{decays},aecho=0.8:0.7:311|467:{echo*0.3:.2f}|{echo*0.2:.2f}",
                        "-f", "f32le", "-"], input=x.tobytes(), capture_output=True, check=True)
    y = np.frombuffer(p.stdout, np.float32).copy()
    # 앞 −60dB 아래 잘라내고 뒤집기
    mx = np.abs(y).max()
    alive = np.where(np.abs(y) > mx * 10 ** (-60 / 20))[0]
    y = y[: alive[-1] + 1][::-1]
    n = int(SR * length)
    y = y[-n:] if len(y) > n else np.concatenate([np.zeros(n - len(y), np.float32), y])
    # 앞은 제곱 페이드인(자연스러운 흡입), 끝은 5ms 로 딱 끊기
    fi = np.linspace(0, 1, n) ** 2
    y = y * fi
    fo = int(SR * 0.005)
    y[-fo:] *= np.linspace(1, 0, fo)
    y = y / (np.abs(y).max() + 1e-9) * 10 ** (-1 / 20)
    return y.astype(np.float32)


def save(y, out):
    subprocess.run(["ffmpeg", "-v", "quiet", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-c:a", "pcm_s24le", out], input=y.tobytes(), check=True)


def main():
    ap = argparse.ArgumentParser(description="역재생 흡입 효과음 만들기")
    ap.add_argument("src")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--len", type=float, default=0.6)
    ap.add_argument("--echo", type=float, default=0.8)
    ap.add_argument("--measure", action="store_true", help="만들지 않고 src 만 잰다")
    a = ap.parse_args()
    if a.measure:
        y = load(a.src)
    else:
        y = make(a.src, a.len, a.echo)
        save(y, a.out)
    m = measure(y)
    print(" · ".join(f"{k} {v:.2f}" for k, v in m.items()))


if __name__ == "__main__":
    sys.exit(main())
