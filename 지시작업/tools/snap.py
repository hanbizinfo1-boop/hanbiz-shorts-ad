# -*- coding: utf-8 -*-
r"""장면 HTML 을 정한 시각에 찍어 «사람 화면 + 자막 자리» 위에 합성한 접촉 시트(스토리보드·검수용).

    python 지시작업/tools/snap.py --times 0.5,1.3,2.8 --out 지시작업/_tmp/look/snap.jpg [--cols 6] [--w 270]
"""
import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
DZ = HERE.parent
ROOT = DZ.parent
sys.path.insert(0, str(ROOT / "tools"))
import html_motion as HM  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402
import config as C  # noqa: E402

import os
VER = os.environ.get("AD_VER", "")
# 판별 사람 영상 · 자막 · 자막 y(텍스트 위 끝) — 지금 판은 meta2(10-14). 옛 판(기본·meta)의 _tmp 는 D:\폐기 로 옮겼다
SRC = {"meta2": str(DZ / "_tmp/src/1013_v2.mp4")}.get(VER, "D:/26년 10월/261013/1013.mp4")
CAPS = DZ / {"meta2": "_tmp/a_meta2"}.get(VER, "_tmp/a") / "captions.json"
CAP_Y = {"meta2": 986}.get(VER, 1110)
SCENE = HERE / "scenes" / "a_direct.html"


def person(t):
    d = json.loads((DZ / "_tmp/prproj/광고1_1014.json").read_text(encoding="utf-8"))
    v1 = [i for i in d["items"] if i["track"] == "V1"]
    c = next((c for c in v1 if c["t0"] <= t < c["t1"]), v1[-1])
    s = c["s0"] + (t - c["t0"])
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{s:.3f}", "-i", SRC, "-frames:v", "1", "-vf", "scale=1080:1920",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(1920, 1080, 3)


def caption(t):
    caps = json.loads(CAPS.read_text(encoding="utf-8"))
    return next((c["text"] for c in caps if c["start"] <= t < c["end"]), "")


async def run(times, scene=SCENE):
    w = HM.Worker(0, scene, 1080, 1920, True, 9361)
    await w.start()
    out = []
    try:
        for t in times:
            out.append(await w.grab(t))
    finally:
        await w.close()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--times", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cols", type=int, default=6)
    ap.add_argument("--w", type=int, default=270)
    ap.add_argument("--scene", default=str(SCENE))
    a = ap.parse_args()
    times = [float(x) for x in a.times.split(",")]
    shots = asyncio.run(run(times, Path(a.scene)))
    f = ImageFont.truetype(str(C.FONTS["pretendard_bold"]), 60)
    tiles = []
    for t, s in zip(times, shots):
        bg = Image.fromarray(person(t)).convert("RGBA")
        bg.alpha_composite(Image.fromarray(s))
        d = ImageDraw.Draw(bg)
        cap = caption(t)
        if cap:
            tw = d.textlength(cap, font=f)
            d.text(((1080 - tw) / 2, CAP_Y), cap, font=f, fill=(255, 255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0, 255))
        d.rectangle((0, 0, 330, 90), fill=(0, 0, 0, 200))
        d.text((16, 10), f"{t:.2f}s", font=f, fill=(255, 220, 60, 255))
        h = int(1920 * a.w / 1080)
        tiles.append(bg.convert("RGB").resize((a.w, h)))
    cols = min(a.cols, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (a.w + 4), rows * (tiles[0].height + 4)), "white")
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * (a.w + 4), (i // cols) * (im.height + 4)))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(a.out, quality=85)
    print(a.out, sheet.size)


if __name__ == "__main__":
    main()
