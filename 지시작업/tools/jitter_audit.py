"""영상 잔 떨림 검사 — 프레임 사이 화면 이동(위상 상관)에서 부드러운 움직임을 빼고 남은 «잔 흔들림»과
«같은 프레임 반복 박자»(24fps→59.94 처럼 중복 프레임이 고르지 않게 끼는 덜컥임)를 구간마다 잰다.

python 지시작업/tools/jitter_audit.py <영상.mp4> [--cuts 0,2.16,4.0,…] [--roi 0,0,1,0.55]
--roi = 잴 영역(가로·세로 비율, x0,y0,x1,y1) — 자막·그래픽이 없는 화면 위쪽을 기본으로 본다.
결과: 구간마다 잔 흔들림 RMS(px, 1080 폭 기준) · 반복 프레임 비율. 0.6px 넘으면 «떨림» · 반복 10% 넘고 고르지 않으면 «덜컥».
"""
import argparse
import subprocess

import numpy as np


def frames(path, w=270, h=480):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={w}:{h}", "-f", "rawvideo",
                          "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)


def shift(a, b):
    A, B = np.fft.fft2(a - a.mean()), np.fft.fft2(b - b.mean())
    R = A * np.conj(B)
    r = np.fft.ifft2(R / (np.abs(R) + 1e-6)).real
    y, x = np.unravel_index(np.argmax(r), r.shape)
    h, w = r.shape
    # 부분 화소 — 이웃 세 점 포물선
    def sub(v, i, n):
        l, c, rr = v[(i - 1) % n], v[i], v[(i + 1) % n]
        d = l - 2 * c + rr
        return i + (0.5 * (l - rr) / d if d else 0)
    xs, ys = sub(r[y], x, w), sub(r[:, x], y, h)
    return (xs if xs < w / 2 else xs - w), (ys if ys < h / 2 else ys - h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--cuts", default="")
    ap.add_argument("--roi", default="0.05,0.02,0.95,0.55")
    ap.add_argument("--fps", type=float, default=60000 / 1001)
    a = ap.parse_args()
    F = frames(a.video)
    n, H, W = F.shape
    x0, y0, x1, y1 = [float(v) for v in a.roi.split(",")]
    roi = F[:, int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)]
    win = np.hanning(roi.shape[1])[:, None] * np.hanning(roi.shape[2])[None, :]
    d = np.array([shift(roi[i] * win, roi[i + 1] * win) for i in range(n - 1)])
    same = np.array([np.abs(roi[i + 1] - roi[i]).mean() < 0.35 for i in range(n - 1)])
    cuts = [float(v) for v in a.cuts.split(",") if v] or [0, n / a.fps]
    scale = 1080 / W
    print(f"{a.video}: {n} 프레임")
    for t0, t1 in zip(cuts, cuts[1:]):
        i0, i1 = int(t0 * a.fps) + 2, int(t1 * a.fps) - 2
        if i1 - i0 < 8:
            continue
        seg = d[i0:i1] * scale
        k = 9
        sm = np.stack([np.convolve(seg[:, j], np.ones(k) / k, "same") for j in range(2)], 1)
        jit = np.sqrt(((seg - sm)[k:-k] ** 2).sum(1).mean()) if len(seg) > 2 * k else 0
        rep = same[i0:i1].mean()
        flag = ("떨림" if jit > 0.6 else "") + (" 덜컥(반복 프레임)" if 0.1 < rep < 0.9 else "")
        print(f"  {t0:6.2f}~{t1:6.2f}  잔 흔들림 {jit:4.2f}px  반복 {rep * 100:4.0f}%  {flag}")


if __name__ == "__main__":
    main()
