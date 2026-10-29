# -*- coding: utf-8 -*-
r"""7번 23.54~28.145 «어떤 빌딩이 손해를 보는 빌딩이고 어떤 빌딩이 돈을 벌 수 있는 빌딩인지» — 빌딩숲(2배속) 위 홀로그램 분석, 화면 전체 V1 (10-21).

사장님: «D:\26년 10월\261021 여기 있는 빌딩숲 영상을 활용해서 (원본 영상 한 2배속정도걸어줘) 각각 건물을 홀로그램 데이터처럼 가격지표 확인하는 듯한 연출 …
  준공년도, 현재가치, 미래예상가치, 임차인정보 … 미래시대에 존재할법한 홀로그램같은 그런느낌»
기준 = 7번.prproj 17:39 저장본(_tmp/story/seq_7번_save2.json). 배경 = 빌딩숲.MP4 2.0~11.3초 2배속(_tmp/r7h/bg2x.mp4) 청록 톤.
업체 간판(왼쪽 탑 꼭대기 · 외벽 세로 병원 간판)·얼굴 광고판은 추적(tools/r7h_track.py)으로 홀로그램 표지를 덮어 가림.

    ffmpeg -ss 2.0 -t 9.3 -i "D:\26년 10월\261021\빌딩숲.MP4" -vf "setpts=0.5*PTS,fps=60000/1001,scale=900:1600" -an 지시작업/_tmp/r7h/bg2x.mp4
    python 지시작업/tools/r7h_track.py
    python tools/html_motion.py 지시작업/tools/scenes/r7h2.html --alpha --settle --fps 59.94 --workers 2 --sub 4 --out 지시작업/_tmp/r7h --name r7h
    python 지시작업/tools/r7h_build.py out
"""
import shutil
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
DZ = HERE.parent
ROOT = DZ.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE))
import sfx as SFX  # noqa: E402
import scene_kit as K  # noqa: E402   — 사람 화면·목소리 잇기·효과음 묶음(10-22 공용으로 뗌)

W, H, FN, FD, FPS = K.W, K.H, K.FN, K.FD, K.FPS
SEQ = DZ / "_tmp/story/seq_7번_save2.json"            # 7번.prproj 17:39 저장본
OFF, END_ABS = 23.54, 28.145
END = END_ABS - OFF
WORK = DZ / "_tmp/r7h"
DELIV = DZ / "납품/7번_홀로그램_빌딩분석_1021"
NAME = "7번_홀로그램_빌딩분석"
SCENE_SFX = ROOT / "소재/효과음/장면음"
# 2판 «내가 말한 홀로그램은 이런느낌이야 … 연출색감이나 느낌은 저런걸로» → 짙은 파랑(스마트시티 참고) · 장면 scenes/r7h2.html
GRADE = "curves=all='0/0 0.5/0.30 1/0.82',colorbalance=rs=-.22:gs=-.02:bs=.32:rm=-.18:bm=.24:rh=-.1:bh=.1,eq=saturation=0.95,vignette=PI/4"
SFX_LIST = [                                                       # 겹침 0 · 끊김 0
    (OFF, "홀로_스캔.wav", -7),                                     # HUD 켜짐 + 조준 3번(→ 24.16)
    (24.341, "ML_Wrong electricity buzz.wav", None),                # «손해를 보는» 빨강 경고(→ 24.66)
    (25.709, "ML_Electronic lock success beeps.wav", None),         # 오른쪽 잠김(→ 25.82)
    (26.476, "SEL_電子ルーレットの出目が点滅.mp3", None),            # «돈을 벌 수 있는» 금빛 분석 창(→ 27.32)
    (27.344, "ML_Positive interface beep.wav", None),               # «빌딩인지» 금빛 맥박(→ 27.74)
]


def make_bundles():
    b = K.head("ML_Positive interface beep.wav", .4)
    p = K.head("SEL_ピコッ.mp3", .12)
    K.bundle(SCENE_SFX / "홀로_스캔.wav", [(0, b, 1.0)] + [(x, p, .7) for x in (.30, .40, .50)])


def write_xml(placed, ov):
    import lec_xml
    rate = "<rate><timebase>60</timebase><ntsc>TRUE</ntsc></rate>"
    fr = lambda s: int(round(s * FPS))   # noqa: E731
    files = {}

    def clip(cid, p, start, end, kind, audio=False):
        dur = end - start
        if str(p) in files:
            fe = f'<file id="{files[str(p)]}"/>'
        else:
            fid = files[str(p)] = f"file-{len(files) + 1}"
            media = ("<media><audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics><channelcount>2</channelcount></audio></media>"
                     if kind == "a" else f"<media><video><samplecharacteristics>{rate}<width>{W}</width><height>{H}</height><pixelaspectratio>square</pixelaspectratio></samplecharacteristics></video></media>")
            fe = f'<file id="{fid}"><name>{escape(Path(p).name)}</name><pathurl>{escape(lec_xml.url(p))}</pathurl>{rate}<duration>{dur}</duration>{media}</file>'
        st = ("<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack>"
              "<filter><effect><name>Audio Levels</name><effectid>audiolevels</effectid><effectcategory>audiolevels</effectcategory><effecttype>audiolevels</effecttype><mediatype>audio</mediatype>"
              '<parameter authoringApp="PremierePro"><parameterid>level</parameterid><name>Level</name><valuemin>0</valuemin><valuemax>3.98109</valuemax><value>1</value></parameter></effect></filter>') if audio else ""
        return (f'<clipitem id="{cid}"><name>{escape(Path(p).name)}</name><enabled>TRUE</enabled>{rate}'
                f"<start>{start}</start><end>{end}</end><in>0</in><out>{dur}</out>{fe}{st}</clipitem>")
    a0, b1 = fr(OFF), fr(END_ABS)
    vtr = [f"<track>{clip('v1-1', ov, a0, b1, 'v')}</track>"]
    atr = ["<track></track>"] * 3
    for i, p in enumerate(placed):
        s = a0 + fr(p["t"])
        d = max(1, int(len(p["x"]) / SFX.SR * FPS + 1e-6))
        atr.append(f"<track>{clip(f'sfx-{i + 1}', p['path'], s, min(s + d, b1), 'a', audio=True)}</track>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="5"><sequence id="seq-1">'
           f"<name>{NAME}</name><duration>{b1}</duration>{rate}<media><video><format><samplecharacteristics>{rate}<width>{W}</width><height>{H}</height>"
           "<pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance></samplecharacteristics></format>"
           f"{''.join(vtr)}</video><audio><numOutputChannels>2</numOutputChannels>{''.join(atr)}</audio></media></sequence></xmeml>")
    (DELIV / f"{NAME}.xml").write_text(xml, encoding="utf-8")
    print("XML", DELIV / f"{NAME}.xml")


def out():
    import rule_check as RC
    WORK.mkdir(parents=True, exist_ok=True)
    make_bundles()
    voice = K.build_base(SEQ, OFF, END_ABS, WORK, K.SRCS_7)
    media = DELIV / "media"
    media.mkdir(parents=True, exist_ok=True)
    full = WORK / "full.mov"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(WORK / "bg2x.mp4"), "-i", str(WORK / "r7h.mov"), "-filter_complex",
                    f"[0:v]{GRADE}[b];[b][1:v]overlay=format=auto,format=yuv422p10le[v]", "-map", "[v]", "-t", f"{END:.4f}", "-r", f"{FN}/{FD}",
                    "-c:v", "prores_ks", "-profile:v", "3", str(full)], check=True)
    ov = media / "전체화면_홀로그램_빌딩분석.mov"
    try:
        shutil.copy2(full, ov)
    except PermissionError:
        ov = ov.with_name(ov.stem + "_새판.mov")
        shutil.copy2(full, ov)
        print("  [잠김] 새 판", ov.name)
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
        fo = min(len(x) // 3, int(.12 * SR))
        x[-fo:] *= (np.linspace(1, 0, fo) ** 2)[:, None]
        db = SFX.ad_target(name) if db is None else db
        x *= 10 ** ((ref + db - SFX.rms_frames(x).max()) / 20)
        x *= min(1.0, .5 / (np.abs(x).max() + 1e-9))
        placed.append(dict(t=max(0, t - OFF - SFX.attack_at(x)), x=x, name=name, label=f"{name}@{t:.2f}"))
    for lv, rule, msg in SFX.fit_tails(placed):
        print(f"  [{lv}] {rule}: {msg}")
    RC.report(RC.check_sfx([(p["t"], p["name"], len(p["x"]) / SR) for p in placed], END), path=WORK / "점검_효과음.txt", title="r7h")
    for old in media.glob("SFX_*.wav"):
        old.unlink()
    for i, p in enumerate(placed):
        p["path"] = media / f"SFX_{i + 1:02d}_{Path(p['name']).stem[:20].replace(' ', '_')}.wav"
        SFX.write_wav(p["path"], p["x"])
    mix = voice.copy()
    for p in placed:
        s = int(p["t"] * SR)
        mix[s:s + len(p["x"])] += p["x"][: len(mix) - s]
    SFX.write_wav(WORK / "mix_pre.wav", mix * min(1, .95 / (np.abs(mix).max() + 1e-9)))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(WORK / "mix_pre.wav"), "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000", str(WORK / "mix.wav")], check=True)
    caps = K.captions(SEQ, OFF, END_ABS)
    font = ImageFont.truetype(str(ROOT / "소재/fonts/gmarket-sans/GmarketSansMedium.ttf"), 62)
    ins, fc, last = ["-i", str(full)], [], "0:v"
    for k, (a, b, s) in enumerate(caps):
        c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(c)
        bb = d.textbbox((W / 2, 787), s, font=font, anchor="mm")
        d.rectangle((bb[0] - 14, bb[1] - 12, bb[2] + 14, bb[3] + 12), fill=(0, 0, 0, 230))
        d.text((W / 2, 787), s, font=font, fill="white", anchor="mm")
        c.save(WORK / f"cap{k}.png")
        ins += ["-loop", "1", "-t", f"{END:.3f}", "-i", str(WORK / f"cap{k}.png")]
        fc.append(f"[{last}][{k + 1}:v]overlay=enable='between(t,{a - OFF:.3f},{b - OFF - .001:.3f})'[c{k}]")
        last = f"c{k}"
    n = len(caps) + 1
    ins += ["-i", str(WORK / "mix.wav")]
    fc.append(f"[{last}]format=yuv420p[v]")
    prev = DELIV / f"{NAME}_미리보기.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", f"{n}:a", "-t", f"{END:.4f}",
                    "-c:v", "libx264", "-crf", "15", "-c:a", "aac", "-b:a", "256k", str(prev)], check=True)
    write_xml(placed, ov)
    print("미리보기", prev)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    {"out": out}[sys.argv[1]]()
