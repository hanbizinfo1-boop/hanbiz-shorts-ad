# -*- coding: utf-8 -*-
r"""장면 도구 공용 — 사장님 시퀀스(900×1600 · 59.94) 사람 화면·목소리 잇기 · 효과음 묶음 (10-22).

10-21 까지 7번 장면 도구가 서로를 불러 썼다(r7c·r7h·r7p → r7g → r7m → r7d). r7g 의 OFF·SEQ 를 밖에서 덮어써
build_base 를 빌리는 식이라, 한 장면 도구를 고치면 다른 장면이 조용히 바뀔 수 있었다(병목·충돌).
→ 여러 장면이 쓰는 것은 여기 한 곳에 두고 값은 인자로 받는다. **새 장면 도구는 남의 장면 도구를 import 하지 않고 이것만 쓴다.**

    import scene_kit as K
    items = K.seq_items(SEQ, OFF, END_ABS)
    voice = K.build_base(SEQ, OFF, END_ABS, WORK, K.SRCS_7)     # WORK/base_v.mp4 + 목소리 배열
    K.bundle(path, [(시각, K.head("파일", 길이), 크기), …])
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import sfx as SFX  # noqa: E402

W, H, FN, FD = 900, 1600, 60000, 1001          # 사장님 쇼츠 시퀀스 규격(4번·7번)
FPS = FN / FD
# 7번 원본(읽기만) — 이름: (경로, 가로, 세로). 멀티7 은 회전 −90 → 세로
SRCS_7 = {"7(대본즉석수정).MP4": (Path(r"D:\26년 10월\261020\7(대본즉석수정).MP4"), 1728, 3072),
          "멀티7(즉석대본수정).MOV": (Path(r"C:\Users\user\Downloads\멀티7(즉석대본수정).MOV"), 2160, 3840)}
VOICE_7 = "7(대본즉석수정).MP4"


def seq_items(seq, off, end_abs):
    """read_prproj 로 뽑은 시퀀스 JSON 에서 [off, end_abs] 에 걸치는 클립."""
    d = json.loads(Path(seq).read_text(encoding="utf-8"))
    return [i for i in d["items"] if i["t1"] > off + 1e-3 and i["t0"] < end_abs - 1e-3]


def captions(seq, off, end_abs, track="V2"):
    """자막 (시작, 끝, 글) — 미리보기에 자막을 그릴 때."""
    return [(max(i["t0"], off), min(i["t1"], end_abs), " ".join(i["text"])) for i in seq_items(seq, off, end_abs) if i["track"] == track and i.get("text")]


def build_base(seq, off, end_abs, work, srcs, voice_src=VOICE_7, voice_db=6):
    """사장님 컷 그대로(V1 사람 · A1 목소리 +voice_db) — 미리보기용. work/base_v.mp4 를 쓰고 목소리 배열을 돌려준다."""
    work = Path(work)
    items = seq_items(seq, off, end_abs)
    segs = []
    for it in sorted((i for i in items if i["track"] == "V1" and i["name"] in srcs), key=lambda i: i["t0"]):
        src, dw, dh = srcs[it["name"]]
        mo = next((f["params"] for f in it.get("fx", []) if f.get("name") == "모션"), {})
        sc = float(mo.get("비율 조정", 100)) / 100
        px, py = (float(v) for v in mo.get("위치", "0.5:0.5").split(":"))
        a, b = max(it["t0"], off), min(it["t1"], end_abs)
        sw, sh = round(dw * sc / 2) * 2, round(dh * sc / 2) * 2
        p = work / f"seg_{len(segs):02d}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{it['s0'] + a - it['t0']:.4f}", "-t", f"{b - a:.4f}", "-i", str(src), "-filter_complex",
                        f"[0:v]fps={FN}/{FD},scale={sw}:{sh},format=yuv420p[s];color=black:s={W}x{H}:r={FN}/{FD}[k];[k][s]overlay=x={round(px * W - sw / 2)}:y={round(py * H - sh / 2)}:shortest=1[v]",
                        "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "16", str(p)], check=True)
        segs.append(p)
    lst = work / "segs.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in segs), encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(work / "base_v.mp4")], check=True)
    SR = SFX.SR
    dur = end_abs - off
    voice = np.zeros((int(dur * SR) + SR, 2))
    for it in (i for i in items if i["track"] == "A1"):
        a, b = max(it["t0"], off), min(it["t1"], end_abs)
        tmp = work / "a.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{it['s0'] + a - it['t0']:.4f}", "-t", f"{b - a:.4f}", "-i", str(srcs[voice_src][0]),
                        "-vn", "-ac", "2", "-ar", str(SR), str(tmp)], check=True)
        x = SFX.load(tmp) * 10 ** (voice_db / 20)
        s = int((a - off) * SR)
        voice[s:s + len(x)] += x[: len(voice) - s]
    return voice[: int(dur * SR)]


def head(name, dur):
    """효과음 앞 무음을 걷고 dur 초만 — 끝은 짧게 페이드(묶음 재료용. 따로 깔 소리는 자르지 않는다 — sfx.md 결정표 ⑤)."""
    x = SFX.load(SFX.find_file(name))
    a = np.abs(x).max(1)
    x = x[int(np.argmax(a > a.max() * 10 ** (-40 / 20))):][: int(dur * SFX.SR)].copy()
    fo = int(min(.06, dur / 3) * SFX.SR)
    x[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return x


def bundle(path, hits):
    """여러 타격을 한 파일로 묶음 — hits = [(시각초, 배열, 크기배수), …] · 피크 0.9 로 맞춤."""
    SR = SFX.SR
    end = max(o + len(x) / SR for o, x, g in hits)
    out = np.zeros((int(end * SR) + 1, 2))
    for o, x, g in hits:
        s = int(o * SR)
        out[s:s + len(x)] += x * g
    SFX.write_wav(path, out * min(1, .9 / (np.abs(out).max() + 1e-9)))
