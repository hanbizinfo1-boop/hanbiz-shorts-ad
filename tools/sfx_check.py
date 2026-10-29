# -*- coding: utf-8 -*-
r"""소리 소재 검사 — 새로 들인 효과음 파일마다 길이·크기·대역·날카로운 순간음을 재서 «찢어지는 소리» 후보를 걸러 낸다.

[이식본 — 원본 D:/영상제작/도구/소리/예능스킬/sfx_check.py (2026-10-02, 다큐 스킬에서 복사된 것). 바뀐 것: 출력 위치는 config.WORK,
 모음1~6(광고 사용 금지) 폴더는 건너뜀, 판정 기준은 그대로.]

  python sfx_check.py <소재 폴더> [출력.md]
    → 출력.md (기본 _tmp/sfx_check/<폴더이름>_검사.md). 소재 폴더는 읽기만 한다(그 폴더에 파일을 쓰지 않는다).
  librosa 필요 (pip install librosa). 이 파일을 import 하는 것만으로는 librosa 를 부르지 않는다.

판정 (references/sfx.md 6장)
  · «고역 셈»  : 2~5kHz + 5kHz 위 에너지 합이 40% 넘음 → 5kHz 셸빙 −6dB 로 쓰거나 안 씀
  · «고역 조금»: 25~40% → 셸빙 권장
  · «순간음 날카로움»: 10ms 안에 +18dB 넘게 솟음 → 앞쪽 30~80ms 페이드인
  · «피크 0dB 근처»: 피크 > −0.3dB → 낮춰 쓰기
  sfx.role() 은 등급표의 «소재상태» 칸에서 셸빙·페이드인을 자동으로 켠다 — 새 파일은 이 도구로 먼저 재서 그 칸에 반영한다.
  (배경 2~5kHz ≤2%·저음 ≥50% 는 «믹스 전체» 기준이라 소재 하나에는 적용하지 않는다. 소재 하나는 셸빙 뒤 쓸 수 있는지만 본다.)
"""
import io
import os
import sys
from pathlib import Path

import numpy as np

import config as C
import sfx as SFX

EXTS = (".mp3", ".wav", ".ogg", ".flac")
HEAD = ["# 소리 소재 검사 — {root}", "",
        "| 파일 | 길이 | RMS dB | 피크 dB | 저음<150 | 2~5k | 5k+ | 최대 순간 상승 | 판정 |",
        "|---|---|---|---|---|---|---|---|---|"]


def check_file(path):
    """파일 하나 → (길이초, RMS dB, 피크 dB, 저음비, 2~5k비, 5k+비, 최대 순간 상승 dB/10ms, 판정 글)."""
    import librosa                                     # 무거워서 쓸 때만 부른다
    y, sr = librosa.load(str(path), sr=22050, mono=True)
    if not len(y):
        return None
    dur = len(y) / sr
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512)) ** 2
    f = librosa.fft_frequencies(sr=sr, n_fft=2048)
    tot = S.sum() + 1e-12
    lo = S[f < 150].sum() / tot
    mid = S[(f >= 2000) & (f < 5000)].sum() / tot
    hi = S[f >= 5000].sum() / tot
    rms = 20 * np.log10(np.sqrt(np.mean(y ** 2)) + 1e-9)
    peak = 20 * np.log10(np.max(np.abs(y)) + 1e-9)
    hop = int(sr * 0.01)
    n = len(y) // hop
    # 무음(−∞)에서의 상승은 세지 않는다: 파일 평균보다 20dB 아래를 바닥으로
    e = np.maximum(20 * np.log10(np.sqrt(np.mean(y[:n * hop].reshape(n, hop) ** 2, 1)) + 1e-9), rms - 20)
    jump = float(np.max(np.diff(e))) if n > 2 else 0.0
    warn = []
    if mid + hi > 0.40:
        warn.append("고역 셈 → 셸빙 필수")
    elif mid + hi > 0.25:
        warn.append("고역 조금 → 셸빙 권장")
    if jump >= 18:
        warn.append(f"순간음 +{jump:.0f}dB/10ms → 페이드인")
    if peak > -0.3:
        warn.append("피크 0dB 근처 → 낮춰 쓰기")
    return dur, rms, peak, lo, mid, hi, jump, " · ".join(warn) or "통과"


def scan(root, out=None):
    root = Path(root)
    rows = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in EXTS:
            continue
        if SFX.is_banned(p.relative_to(root)):          # 모음1~6: 광고 사용 금지 — 재지 않는다
            continue
        r = check_file(p)
        if r:
            rows.append((p.relative_to(root).as_posix(),) + r)
    L = [h.format(root=root) for h in HEAD]
    for r in rows:
        L.append(f"| {r[0]} | {r[1]:.1f}초 | {r[2]:.1f} | {r[3]:.1f} | {r[4]*100:.0f}% | {r[5]*100:.0f}% | {r[6]*100:.0f}% | +{r[7]:.0f}dB | {r[8]} |")
    out = Path(out) if out else C.WORK / "sfx_check" / f"{root.name or 'root'}_검사.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    io.open(out, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    return rows, out


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    rows, out = scan(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(f"{len(rows)}개 검사 → {out}")
    for r in rows:
        print(f"  {r[0]}: {r[8]}")
