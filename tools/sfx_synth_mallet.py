"""음정 톤(마림바·벨) 효과음 합성 — BGM 조에 맞춘 단음. 라이선스 걱정 없는 자체 소리.

받은 라이브러리에 마림바·실로폰이 없어서(Mixkit 에도 없음, 10-12) 직접 만든다.
    python tools/sfx_synth_mallet.py --notes C5 Eb5 G5 C6 --kind marimba --out 소재/효과음/받은라이브러리/19_음정톤_마림바
    → SYN_marimba_C5.wav …  (48k 24bit, 정점 −1 dBFS)
조 추정: 3안 «I'm Under The Radar» C단조(상관 0.82) · 2안 «Miles Away» D장조(0.96) — 크로마 + Krumhansl 프로파일, 기록/작업기록.md 10-12.
"""
import argparse
import os
import subprocess

import numpy as np

SR = 48000
NAMES = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6,
         "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
# (배음 비, 세기, 감쇠 초) — 마림바는 1:4 배음(나무 막대), 벨은 비정수 배음으로 오래 울림
KINDS = {
    "marimba": [(1.0, 1.0, 0.38), (3.93, 0.32, 0.09), (9.2, 0.08, 0.03)],
    "bell": [(1.0, 1.0, 1.1), (2.76, 0.45, 0.55), (5.40, 0.22, 0.25), (8.93, 0.08, 0.12)],
    "pluck": [(1.0, 1.0, 0.22), (2.0, 0.5, 0.12), (3.0, 0.25, 0.07), (4.0, 0.12, 0.05)],
}


def freq(note):
    name, octv = note[:-1].replace("s", "#") if note[1:2] == "s" else note[:-1], int(note[-1])
    midi = 12 * (octv + 1) + NAMES[name]
    return 440.0 * 2 ** ((midi - 69) / 12)


def synth(f0, kind):
    parts = KINDS[kind]
    length = max(d for _, _, d in parts) * 4.5
    t = np.arange(int(SR * length)) / SR
    y = np.zeros_like(t)
    for ratio, amp, dec in parts:
        if f0 * ratio > SR / 2.2:
            continue
        y += amp * np.exp(-t / dec) * np.sin(2 * np.pi * f0 * ratio * t)
    # 채(말렛) 닿는 소리: 3ms 짧은 잡음
    rng = np.random.default_rng(int(f0))
    click = rng.standard_normal(int(SR * 0.003)) * np.linspace(1, 0, int(SR * 0.003)) * 0.15
    y[: len(click)] += click
    att = int(SR * 0.002)
    y[:att] *= np.linspace(0, 1, att)
    fo = int(SR * 0.05)
    y[-fo:] *= np.linspace(1, 0, fo)
    return (y / np.abs(y).max() * 10 ** (-1 / 20)).astype(np.float32)


def main():
    ap = argparse.ArgumentParser(description="음정 톤 효과음 합성")
    ap.add_argument("--notes", nargs="+", required=True, help="예: C5 Eb5 G5")
    ap.add_argument("--kind", choices=list(KINDS), default="marimba")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for n in a.notes:
        y = synth(freq(n), a.kind)
        p = os.path.join(a.out, f"SYN_{a.kind}_{n.replace('#', 's')}.wav")
        subprocess.run(["ffmpeg", "-v", "quiet", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-c:a", "pcm_s24le", p], input=y.tobytes(), check=True)
        print(f"{p}  {freq(n):.1f}Hz  {len(y) / SR:.2f}s")


if __name__ == "__main__":
    main()
