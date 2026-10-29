# -*- coding: utf-8 -*-
r"""7번 3.971~7.124 «그렇기 때문에 / 모든 자산가가 / 강남 빌딩을 / 사고 싶어 합니다» — 상담 사진 포토 모자이크 → 강남빌딩 (10-21).

사장님(10-21): «그렇기때문에 모든 자산가가 강남빌딩을 사고싶어합니다 이부분을 어떻게 연출하면 좋을까? 약간 상담사진들 많은데 그걸 활용해서 어떻게 멋드러지게 연출해보고싶은데 좋은 아이디어 있니?»
  → A 포토 모자이크 «A로 진행» (앞 «그만큼 강남은 확실합니다»는 «내가 직접 연출할게»)
기준 = 7번.prproj 18:41: V1 3.971~7.124 원본 13.947 · 비율 61.083% · 위치 0.53:0.54875 · 자막 y 755~818.
단어 시각: 그렇기 4.24 · 때문에 4.50 · 모든 4.70 · 자산가가 5.10 · 강남 5.68 · 빌딩을 6.08 · 사고 6.50 · 싶어 6.62 · 합니다 6.86.
소재 = 상담 사진 162칸(tools/r4s5_assets.py → 소재/r4s5) · 리모델링 후 건물 누끼 소재/r4s/bldcut_uh.png. 장면 scenes/r7m.html(칸 자리는 이 도구가 scenes/r7m_cells.js 로 씀).
납품: V4 연출층 · A4~ 효과음(sfx.AD_LEVEL). 3초 규칙 밖이지만 7번 통일로 자막 밑.

    python 지시작업/tools/r7m_build.py cells
    python tools/html_motion.py 지시작업/tools/scenes/r7m.html --alpha --fps 59.94 --workers 2 --sub 4 --out 지시작업/_tmp/r7m --name r7m
    python 지시작업/tools/r7m_build.py out
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
DZ = HERE.parent
ROOT = DZ.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE))
import sfx as SFX  # noqa: E402
import r7d_build as D  # noqa: E402   — 사람 배치·XML·효과음 굽기 같은 방식

SRC = D.SRC
WORK = DZ / "_tmp/r7m"
DELIV = DZ / "납품/7번_상담모자이크_강남빌딩_1021"
NAME = "7번_상담모자이크_강남빌딩"
W, H, FN, FD, FPS = D.W, D.H, D.FN, D.FD, D.FPS
OFF, END_ABS = 3.971, 7.124
END = END_ABS - OFF
S0 = 13.947
BLD = DZ / "소재/r4s/bldcut_uh.png"
BH, BX, BASE = 600, 450, 1490          # 건물 높이 · 가운데 x · 밑선 y (자막 밑 890~1490)
TW, TH = 39, 30                        # 모자이크 칸
T = dict(fly0=4.70, fly1=5.62, flash=5.68, glow=6.50)
CAP_TOP = False                        # 미리보기에서 자막을 연출층 위에(전체 화면 판)
SFX_LIST = [   # (시퀀스 초, 파일, dB — None 이면 sfx.AD_LEVEL)
    (4.70, "휙1.mp3", None),                       # 사진들 날아듦
    (4.78, "모자이크_착착.wav", -7),               # 칸마다 박힘(한 파일)
    (5.68, "SEL_キラッ1.mp3", None),               # 실제 건물로 번쩍
    (6.50, "맑은소리.mp3", None),                  # 금빛 빛
]


def cells():
    """건물 누끼 알파로 칸 자리 계산 → scenes/r7m_cells.js (칸마다 사진·도착 시각·출발 자리)."""
    b = Image.open(BLD)
    bw = round(BH * b.width / b.height)
    a = np.array(b.resize((bw, BH)).split()[3]) > 128
    x0, y0 = BX - bw / 2, BASE - BH
    cs = []
    for r in range(BH // TH):
        for c in range(bw // TW + 1):
            blk = a[r * TH:(r + 1) * TH, c * TW:(c + 1) * TW]
            if blk.size and blk.mean() > .55:
                cs.append([x0 + c * TW, y0 + r * TH])
    STAND = {"cs_0_60.jpg", "cs_0_82.jpg", "cs_2_12.jpg"}   # 10-21 «완전 상담하는 사진들만» — 서서 찍은 기념 컷 뺌
    tiles = sorted(p.name for p in (DZ / "소재/r4s5").glob("cs_*.jpg") if p.name not in STAND)
    rng = np.random.default_rng(21)
    rng.shuffle(tiles)
    order = list(range(len(cs)))
    rng.shuffle(order)
    n = len(cs)
    out = []
    for k, idx in enumerate(order):                       # 도착 시각: 점점 빨라짐(4.70 → 5.62)
        land = T["fly0"] + .35 + (T["fly1"] - T["fly0"] - .35) * (k / max(1, n - 1)) ** .6
        side = rng.integers(3)                            # 출발: 왼쪽 · 오른쪽 · 아래(얼굴·자막 위로 지나가지 않게)
        sx, sy = ((-120, rng.uniform(950, 1550)) if side == 0 else (1020, rng.uniform(950, 1550)) if side == 1 else (rng.uniform(0, 900), 1720))
        out.append(dict(x=cs[idx][0], y=cs[idx][1], img=tiles[k % len(tiles)], land=round(land - OFF, 4), sx=round(sx), sy=round(sy), rot=round(float(rng.uniform(-40, 40)), 1)))
    (HERE / "scenes/r7m_cells.js").write_text(
        f"// tools/r7m_build.py cells 가 만듦 — 칸 {n}개 · 건물 {bw}×{BH} · 왼쪽 위 ({x0:.0f},{y0:.0f})\n"
        f"window.R7M = {json.dumps(dict(cells=out, bw=bw, bh=BH, x0=x0, y0=y0, tw=TW, th=TH))};\n", encoding="utf-8")
    # 박히는 소리 한 파일: 마우스 클릭·KN_tick 번갈아, 도착 시각마다(가까우면 건너뜀)
    SR = SFX.SR
    ks = [SFX.load(SFX.find_file(f)) for f in ("KN_tick_001.wav", "KN_tick_002.wav", "KN_tick_004.wav")]
    lands = sorted(c["land"] for c in out)
    t0 = lands[0] - (T["fly0"] + .08 - OFF)
    buf = np.zeros((int((lands[-1] - lands[0] + .5) * SR), 2))
    last, j = -1, 0
    for L in lands:
        if L - last < .035:
            continue
        x = ks[j % 3][: int(.08 * SR)] * (.7 + .3 * np.random.default_rng(j).random())
        s = int((L - lands[0] + t0) * SR)
        buf[s:s + len(x)] += x[: len(buf) - s]
        last, j = L, j + 1
    buf *= .9 / (np.abs(buf).max() + 1e-9)
    SFX.write_wav(ROOT / "소재/효과음/장면음/모자이크_착착.wav", buf)
    print("칸", n, "· 박힘 소리", j, "번")


def out():
    import shutil
    import rule_check as RC
    media = DELIV / "media"
    media.mkdir(parents=True, exist_ok=True)
    ov = media / "연출층_상담모자이크.mov"
    try:
        shutil.copy2(WORK / "r7m.mov", ov)
    except PermissionError:
        ov = media / "연출층_상담모자이크_새판.mov"
        shutil.copy2(WORK / "r7m.mov", ov)
        print("  [잠김] 새 판", ov.name)
    # 사람 바탕(미리보기용) + 목소리
    base = WORK / "base.mp4"
    sw, sh = round(1728 * D.VS / 2) * 2, round(3072 * D.VS / 2) * 2
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{S0}", "-t", f"{END:.4f}", "-i", str(SRC), "-filter_complex",
                    f"[0:v]fps={FN}/{FD},scale={sw}:{sh}[s];color=black:s={W}x{H}:r={FN}/{FD}[b];[b][s]overlay=x={round(D.VX - sw / 2)}:y={round(D.VY - sh / 2)}:shortest=1[v]",
                    "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "16", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(base.with_suffix(".mov"))], check=True)
    voice = SFX.load(base.with_suffix(".mov")) * 10 ** (6 / 20)
    ref = SFX.voice_ref_from(voice)
    SR = SFX.SR
    placed = []
    for t, name, db in SFX_LIST:
        x = SFX.load(SFX.find_file(name))
        a = np.abs(x).max(1)
        x = x[int(np.argmax(a > a.max() * 10 ** (-40 / 20))):]
        e = np.abs(x).max(1)
        loud = np.where(e > e.max() * 10 ** (-45 / 20))[0]
        x = x[: min((loud[-1] + 1) if len(loud) else len(x), int(SFX.TAIL_MAX * SR))].copy()
        fo = min(len(x) // 3, int(.25 * SR))
        x[-fo:] *= (np.linspace(1, 0, fo) ** 2)[:, None]
        db = SFX.ad_target(name) if db is None else db
        x *= 10 ** ((ref + db - SFX.rms_frames(x).max()) / 20)
        x *= min(1.0, .5 / (np.abs(x).max() + 1e-9))
        placed.append(dict(t=max(0, t - OFF - SFX.attack_at(x)), x=x, name=name, label=f"{name}@{t:.2f}"))
    for lv, rule, msg in SFX.fit_tails(placed):
        print(f"  [{lv}] {rule}: {msg}")
    RC.report(RC.check_sfx([(p["t"], p["name"], len(p["x"]) / SR) for p in placed], END), path=WORK / "점검_효과음.txt", title="r7m")
    for i, p in enumerate(placed):
        p["path"] = media / f"SFX_{i + 1:02d}_{Path(p['name']).stem[:20].replace(' ', '_')}.wav"
        SFX.write_wav(p["path"], p["x"])
    mix = voice.copy()
    for p in placed:
        s = int(p["t"] * SR)
        mix[s:s + len(p["x"])] += p["x"][: len(mix) - s]
    SFX.write_wav(WORK / "mix_pre.wav", mix * min(1, .95 / (np.abs(mix).max() + 1e-9)))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(WORK / "mix_pre.wav"), "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000", str(WORK / "mix.wav")], check=True)
    # 미리보기 자막(사장님 V2 흉내 — 흰 글 검은 상자, y 787)
    caps = [(3.971, 4.655, "그렇기 때문에"), (4.655, 5.639, "모든 자산가가"), (5.639, 6.340, "강남 빌딩을"), (6.340, 7.124, "사고 싶어 합니다")]
    font = ImageFont.truetype(str(ROOT / "소재/fonts/gmarket-sans/GmarketSansMedium.ttf"), 62)
    ins, fc, last = ["-i", str(base.with_suffix(".mov")), "-i", str(ov)], [], "0:v"
    if CAP_TOP:                                   # 전체 화면 판(V2) — 사장님이 자막을 V5 로 올리시므로 미리보기도 자막을 위에
        fc.append("[0:v][1:v]overlay=format=auto[o0]")
        last = "o0"
    for k, (a, b, s) in enumerate(caps):
        c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(c)
        bb = d.textbbox((W / 2, 787), s, font=font, anchor="mm")
        d.rectangle((bb[0] - 14, bb[1] - 12, bb[2] + 14, bb[3] + 12), fill=(0, 0, 0, 230))
        d.text((W / 2, 787), s, font=font, fill="white", anchor="mm")
        c.save(WORK / f"cap{k}.png")
        ins += ["-loop", "1", "-t", f"{END:.3f}", "-i", str(WORK / f"cap{k}.png")]
        fc.append(f"[{last}][{k + 2}:v]overlay=enable='between(t,{a - OFF:.3f},{b - OFF - .001:.3f})'[c{k}]")
        last = f"c{k}"
    n = len(caps) + 2
    ins += ["-i", str(WORK / "mix.wav")]
    fc.append(f"[{last}]format=yuv420p[v]" if CAP_TOP else f"[{last}][1:v]overlay=format=auto,format=yuv420p[v]")
    prev = DELIV / f"{NAME}_미리보기.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", f"{n}:a", "-t", f"{END:.4f}",
                    "-c:v", "libx264", "-crf", "15", "-c:a", "aac", "-b:a", "256k", str(prev)], check=True)
    write_xml(placed, ov)
    print("미리보기", prev)


def write_xml(placed, ov):
    """V1~V3 빈 트랙 · V4 연출층 · A1~A3 빈 트랙 · A4~ 효과음 — 사장님 «7번» 3.971 자리에 그대로 놓이게 시각을 민다."""
    from xml.sax.saxutils import escape
    import lec_xml
    rate = "<rate><timebase>60</timebase><ntsc>TRUE</ntsc></rate>"
    fr = lambda s: int(round(s * FPS))   # noqa: E731
    off, total = fr(OFF), fr(END)
    files = {}

    def file_el(p, dur, kind):
        if str(p) in files:
            return f'<file id="{files[str(p)]}"/>'
        fid = files[str(p)] = f"file-{len(files) + 1}"
        media = ("<media><audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics><channelcount>2</channelcount></audio></media>"
                 if kind == "a" else f"<media><video><samplecharacteristics>{rate}<width>{W}</width><height>{H}</height><pixelaspectratio>square</pixelaspectratio></samplecharacteristics></video></media>")
        return f'<file id="{fid}"><name>{escape(Path(p).name)}</name><pathurl>{escape(lec_xml.url(p))}</pathurl>{rate}<duration>{dur}</duration>{media}</file>'

    def clip(cid, p, start, end, kind, dur=None, audio=False):
        dur = dur or (end - start)
        st = ("<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack>"
              "<filter><effect><name>Audio Levels</name><effectid>audiolevels</effectid><effectcategory>audiolevels</effectcategory><effecttype>audiolevels</effecttype><mediatype>audio</mediatype>"
              '<parameter authoringApp="PremierePro"><parameterid>level</parameterid><name>Level</name><valuemin>0</valuemin><valuemax>3.98109</valuemax><value>1</value></parameter></effect></filter>') if audio else ""
        return (f'<clipitem id="{cid}"><name>{escape(Path(p).name)}</name><enabled>TRUE</enabled>{rate}'
                f"<start>{start + off}</start><end>{end + off}</end><in>0</in><out>{end - start}</out>{file_el(p, dur, kind)}{st}</clipitem>")
    vtr = ["<track></track>"] * 3 + [f"<track>{clip('v4-1', ov, 0, total, 'v')}</track>"]
    atr = ["<track></track>"] * 3
    for i, p in enumerate(placed):
        s = fr(p["t"])
        d = max(1, int(len(p["x"]) / SFX.SR * FPS + 1e-6))
        atr.append(f"<track>{clip(f'sfx-{i + 1}', p['path'], s, min(s + d, total), 'a', d, audio=True)}</track>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="5"><sequence id="seq-1">'
           f"<name>{NAME}</name><duration>{off + total}</duration>{rate}<media><video><format><samplecharacteristics>{rate}<width>{W}</width><height>{H}</height>"
           "<pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance></samplecharacteristics></format>"
           f"{''.join(vtr)}</video><audio><numOutputChannels>2</numOutputChannels>{''.join(atr)}</audio></media></sequence></xmeml>")
    (DELIV / f"{NAME}.xml").write_text(xml, encoding="utf-8")
    print("XML", DELIV / f"{NAME}.xml")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    WORK.mkdir(parents=True, exist_ok=True)
    {"cells": cells, "out": out}[sys.argv[1]]()
