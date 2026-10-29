# -*- coding: utf-8 -*-
r"""화면 사건(프레임 차이 봉우리) ↔ 소리 타격(sfx/onsets.csv) 대조 — 원본 fps 프레임 단위.

    python -I tools/sfx_ref_sync.py <폴더> [문턱배수=2.5]

<폴더>/sfx/vis_events.csv : 화면 사건 시각(초)·프레임 번호·변화량 · 가장 가까운 소리 타격 시각 · 시차(화면-소리, 초, 프레임)
사전 조건: tools/sfx_ref_analyze.py 를 먼저 돌려 onsets.csv 가 있어야 한다.
"""
import csv
import subprocess
import sys
from pathlib import Path

import numpy as np


def main():
    folder = Path(sys.argv[1])
    mult = float(sys.argv[2]) if len(sys.argv) > 2 else 2.5
    out = folder / "sfx"
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=avg_frame_rate,width,height",
                         "-of", "csv=p=0", str(folder / "src.mp4")], capture_output=True, text=True).stdout.strip().split(",")
    w0, h0 = int(pr[0]), int(pr[1])
    n, d = pr[2].split("/")
    fps = float(n) / float(d)
    W, H = 160, 90
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(folder / "src.mp4"), "-an", "-vf", f"scale={W}:{H},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    arr = np.frombuffer(raw, dtype=np.uint8).reshape(-1, H, W).astype(np.float32)
    diff = np.abs(np.diff(arr, axis=0)).mean(axis=(1, 2))   # diff[i] = 프레임 i -> i+1
    # 사건 = 국소 최대이면서 문턱(중앙값 배수 + 절대 하한) 이상
    med = float(np.median(diff))
    thr = max(mult * med, 1.0)
    ev = []
    for i in range(len(diff)):
        lo, hi = max(0, i - 2), min(len(diff), i + 3)
        if diff[i] >= thr and diff[i] == diff[lo:hi].max():
            ev.append((i + 1, diff[i]))
    on = [float(r["onset"]) for r in csv.DictReader((out / "onsets.csv").open(encoding="utf-8"))]
    on = np.array(on)
    rows = []
    for fr, v in ev:
        t = fr / fps
        j = int(np.argmin(np.abs(on - t))) if len(on) else -1
        dt = t - on[j] if j >= 0 else float("nan")
        rows.append([round(t, 3), fr, round(float(v), 1), round(float(on[j]), 3), round(dt, 3), round(dt * fps, 1)])
    with (out / "vis_events.csv").open("w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["vis_t", "frame", "diff", "nearest_onset_t", "dt_s(vis-snd)", "dt_frames"])
        wr.writerows(rows)
    print(f"fps {fps:.3f} 프레임 {len(arr)} 중앙값 {med:.2f} 문턱 {thr:.2f} 사건 {len(ev)}")


if __name__ == "__main__":
    main()
