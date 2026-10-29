# -*- coding: utf-8 -*-
r"""7번 28.145~29.997 «실제 사례로 알려드리겠습니다» — 인터넷 자료 → 카페 → 책5 가 물방울처럼 들어가며 성공사례가 쏟아짐, 화면 전체 V1 (10-21).

사장님: «그다음 실제 사례로 알려드리겠습니다 까지 이어서 전환효과 부드럽게 연출 효과붙여서 넣어주면 좋을듯 / 이 부분은 인터넷상 수많은 자료중에 하나를 클릭했더니
  [카페 화면] 이 카페가 나오고 이 카페 속으로 새폴더의 책5 가 속 들어가면서(지면에 물방울 들어갈때 이는 출렁임연출) 성공사례들이 쏟아져나오는 연출로»
  «이름·로고 그대로 다시 그림» «저거 카페홍보겸해서하는거니까 제대로 따라해줘»
기준 = 7번.prproj 17:39 저장본. 소재 tools/r7c_assets.py → 소재/r7c · 장면 scenes/r7c.html. r7h_build 의 효과음·미리보기·XML 을 그대로 씀.

    python 지시작업/tools/r7c_assets.py
    python 지시작업/tools/r7c_assets.py cards
    python tools/html_motion.py 지시작업/tools/scenes/r7c2.html --settle --fps 59.94 --workers 2 --sub 4 --out 지시작업/_tmp/r7c --name r7c2
    python 지시작업/tools/r7c_build.py out
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
OFF, END_ABS = 28.145, 29.997
END = END_ABS - OFF
WORK = DZ / "_tmp/r7c"
DELIV = DZ / "납품/7번_실제사례_카페_1021"
NAME = "7번_실제사례_카페"
SCENE_SFX = ROOT / "소재/효과음/장면음"
GRADE = "eq=brightness=-0.06:saturation=0.65,colorbalance=bs=.12:bm=.08:rs=-.06,vignette=PI/5"
# 2판 «1. b안 2. 빼자 3 실제사례위주로만 폴더에있는» — 장면 scenes/r7c2.html(책 퐁당 뺌 · 실제 후기 4장 형광펜)
SFX_LIST = [                                                       # 겹침 0 · 끊김 0
    (OFF, "ML_Fast small sweep transition.wav", None),              # 앞 화면 물러나고 카페 화면(→ 28.78)
    (28.745, "마우스 클릭.mp3", None),                              # «황소장님 상담 후기» 딸깍(→ 28.89)
    (28.805, "후기_착착.wav", -7),                                  # 후기 4장 착착(→ 29.62)
]


def make_bundles():
    p = K.head("ML_Paper slide.wav", .2)
    K.bundle(SCENE_SFX / "후기_착착.wav", [(i * .22, p, .85) for i in range(4)])


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
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(WORK / "r7c2.mp4"), "-t", f"{END:.4f}", "-r", f"{FN}/{FD}", "-pix_fmt", "yuv422p10le",
                    "-c:v", "prores_ks", "-profile:v", "3", str(full)], check=True)
    ov = media / "전체화면_실제사례_카페.mov"
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
    RC.report(RC.check_sfx([(p["t"], p["name"], len(p["x"]) / SR) for p in placed], END), path=WORK / "점검_효과음.txt", title="r7c")
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
