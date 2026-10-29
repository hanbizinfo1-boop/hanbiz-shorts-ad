# -*- coding: utf-8 -*-
r"""4번 세미나 사진 흐름(15.649~17.47) 효과음 후보 청음본 (10-20).
사장님 «아니야 마음에안들어»(카메라 찰칵) — 종이 착 · 합성 필름 · 찰칵 세 번 반려 → 후보를 한 영상에 이어 붙여 고르시게 함.
    python 지시작업/tools/r4s_v4_audition.py   → 납품/4번_세미나사진_강남빌딩_v4_1020/효과음후보_청음.mp4
"""
import subprocess, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
import sfx as SFX  # noqa: E402
DZ = HERE.parent
W = DZ / "_tmp/r4s_v4"; A = W / "aud"; A.mkdir(exist_ok=True)
OUT = DZ / "납품/4번_세미나사진_강남빌딩_v4_1020/효과음후보_청음.mp4"
SR = SFX.SR; DUR = 17.47 - 15.649 + .35
PH = [15.757, 16.145, 16.471, 16.799, 17.125]          # 사진이 화면 3/4 지점을 지나는 순간
P = lambda ts: [t - 15.649 for t in ts]                  # noqa: E731
OPT = [   # (이름, [(시각, 파일, 목소리 대비 dB)])
    ("A 소리 없음(말만)", []),
    ("B 긴 쓸림 한 번(Speeding swoosh)", [(0.0, "ML_Speeding swoosh.wav", -12)]),
    ("C 고속이동 한 번(SEL 高速移動)", [(0.02, "SEL_高速移動.mp3", -10)]),
    ("D 사진마다 약한 휙(휙1·휙２)", [(t, "휙1.mp3" if k % 2 else "휙２.mp3", -14) for k, t in enumerate(P(PH))]),
    ("E 사진마다 스치는 바람(Fast air sweep)", [(t, "ML_Fast air sweep transition.wav", -14) for t in P(PH)]),
    ("F 마법 쓸림 한 번(Magic sweep)", [(0.0, "ML_Magic transition sweep presentation.wav", -13)]),
]
voice = SFX.load(DZ / "_tmp/r4s_v4/V1_1.mov")
v2 = SFX.load(DZ / "_tmp/r4s_v4/V1_2.mov"); voice = np.concatenate([voice, v2])
ref = SFX.voice_ref_from(voice); n = int(DUR * SR); vseg = voice[:n]
clips = []
for i, (name, lst) in enumerate(OPT):
    mix = vseg.copy()
    for t, f, db in lst:
        x = SFX.load(SFX.find_file(f)); a = np.abs(x).max(1); x = x[int(np.argmax(a > a.max() * .01)):]
        x = x * 10 ** ((ref + db - SFX.rms_frames(x).max()) / 20); s0 = int(t * SR); seg = x[:max(0, n - s0)]; mix[s0:s0 + len(seg)] += seg
    wav = A / f"o{i}.wav"; SFX.write_wav(wav, mix * min(1, .9 / (np.abs(mix).max() + 1e-9)))
    lab = A / f"o{i}.png"
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGBA", (900, 1600), (0, 0, 0, 0)); d = ImageDraw.Draw(im); fo = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 54)
    d.rounded_rectangle([40, 120, 860, 230], 24, fill=(0, 0, 0, 200)); d.text((70, 140), name, font=fo, fill=(255, 220, 60)); im.save(lab)
    c = A / f"o{i}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(DZ / "납품/4번_세미나사진_강남빌딩_v4_1020/4번_세미나사진_강남빌딩_v4_미리보기.mp4"), "-i", str(lab), "-i", str(wav),
                    "-filter_complex", "[0:v][1:v]overlay[v]", "-map", "[v]", "-map", "2:a", "-t", f"{DUR:.3f}", "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(c)], check=True)
    clips.append(c)
lst = A / "list.txt"; lst.write_text("".join(f"file '{c.as_posix()}'\n" for c in clips), encoding="utf-8")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(OUT)], check=True)
print(OUT)
