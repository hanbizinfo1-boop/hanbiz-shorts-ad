# -*- coding: utf-8 -*-
r"""7번 19.136~23.774 «저는 지난 18년간 / 강남빌딩을 / 45채 사보고 / 36채를 지어봤습니다» — 자막 밑 사진 덱 → 매치 줌 → 화면 전체 (10-21).

사장님(10-21) 2판: «저는 지난 18년간할때 좀더 카드가 들어와서 펼쳐졌으면 좋겠고 / 마지막이 지어봣습니다 하는 건물이 올라가는게 그냥 사진이 올라가는느낌이라 건축을해서 지어졌다는 느낌이 안들어»
  «일단 추천대로하고 그리고 45채 사보고가 너무 빨리넘어가는데 이게 살짝 넘겨지고 이 화면이 위쪽에 작은카드로 보관되는 느낌이면 좋을것같아»
사장님(10-21): «45채 사보고 << 이부분을 빌딩보러다니는 사진위주로 36채 지어본건 공사현장위주로해서 … 세련되게 … 저는 지난 18년간 << 이부분에서
  자막아래에 사진들로 빌드업하고 강남빌딩을 할때부터 좀 전체화면에 사진쪽으로 연출구도잡고싶은데» → 추천안 «오케이 진행해봐 새폴더에 있어근데 구분 안해놨는데 네가 구분할수있어?»
사진 tools/r7p_assets.py → 소재/r7p · 장면 scenes/r7p.html.
납품 두 조각(사장님 15:05 편집: 화면 전체 장면은 V1, 사람 위 층은 V4 — editing-premiere.md 5-6):
  V4 19.136~20.254 연출층_사진덱.mov(알파) · V1 20.254~23.774 전체화면_45채36채.mov(불투명 — 첫 0.45초 매치 줌 동안 사람 화면을 미리 합침) · A4~ 효과음.

    python 지시작업/tools/r7p_assets.py
    python tools/html_motion.py 지시작업/tools/scenes/r7p.html --alpha --settle --fps 59.94 --workers 2 --sub 4 --out 지시작업/_tmp/r7p --name r7p
    python 지시작업/tools/r7p_build.py out
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
OFF, SPLIT, END_ABS = 19.002, 20.103, 23.54             # 10-21 17:39 저장본(seq_7번_save2) — 15:05 보다 0.13~0.23초 당겨짐
END = END_ABS - OFF
WORK = DZ / "_tmp/r7p"
DELIV = DZ / "납품/7번_18년_45채36채_1021"
NAME = "7번_18년_45채36채"
SCENE_SFX = ROOT / "소재/효과음/장면음"
# 2판(10-21 «좀더 카드가 들어와서 펼쳐졌으면» · «건축을해서 지어졌다는 느낌» · «45채 … 위쪽에 작은카드로 보관») — 장면 r7p.html 과 같은 값
FAN = [.44, .50, .56, .62, .68, .74]                               # 묶음 올라옴(0) 뒤 부채꼴로 펼침
TOUR = [0, .27, .54, .81]                                          # 화면이 넘겨지며 위쪽 줄에 보관
BUILD = [0, .12, .23, .34, .44, .53]                               # 공사현장 카드 쌓임(22.175 기준)
FLOORS = [22.83 + x for x in (0, .08, .16, .24, .32, .40)]         # 1층부터 한 층씩
FIN = 23.27                                                        # 완공(금빛)
SFX_LIST = [                                                       # 겹침 0 · 끊김 0
    (OFF + .04, "카드_촤르륵.wav", -7),                             # 묶음 올라옴 + 부채꼴 촤르륵(→ 20.05)
    (SPLIT, "휙２.mp3", None),                                      # 가운데 장이 뽑혀 화면 전체로(→ 20.68)
    (20.888, "사진_넘김.wav", -7),                                  # «45채» 넘겨지며 보관(→ 22.05)
    (22.005 + .02, "층_쿵쿵.wav", -6),                              # «36채» 카드 쌓임 → 층마다 쿵 → 완공 띵(→ 23.77)
]


_head, _bundle = K.head, K.bundle                                  # 10-22 scene_kit 으로 옮김


def make_bundles():
    p = _head("ML_Paper slide.wav", .2)
    _bundle(SCENE_SFX / "카드_촤르륵.wav", [(0, _head("ML_Paper slide.wav", .42), 1.0)] + [(f, p, .55) for f in FAN])
    _bundle(SCENE_SFX / "사진_넘김.wav", [(d, p, .8) for d in TOUR])
    w, k, g = _head("ML_Wood hard hit.wav", .27), _head("KN_impactSoft_heavy_000.wav", .22), _head("KN_glass_001.wav", .24)
    b0 = 22.025
    _bundle(SCENE_SFX / "층_쿵쿵.wav", [(b, w, .6) for b in BUILD] + [(f - b0, k, .9) for f in FLOORS] + [(FIN - b0, g, .8)])


def write_xml(placed, ov_a, ov_b):
    """V1 화면 전체(20.254~) · V4 사진 덱(19.136~20.254) · A4~ 효과음 — 사장님 «7번» 그 자리에 그대로 놓이게."""
    import lec_xml
    rate = "<rate><timebase>60</timebase><ntsc>TRUE</ntsc></rate>"
    fr = lambda s: int(round(s * FPS))   # noqa: E731
    files = {}

    def file_el(p, dur, kind):
        if str(p) in files:
            return f'<file id="{files[str(p)]}"/>'
        fid = files[str(p)] = f"file-{len(files) + 1}"
        media = ("<media><audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics><channelcount>2</channelcount></audio></media>"
                 if kind == "a" else f"<media><video><samplecharacteristics>{rate}<width>{W}</width><height>{H}</height><pixelaspectratio>square</pixelaspectratio></samplecharacteristics></video></media>")
        return f'<file id="{fid}"><name>{escape(Path(p).name)}</name><pathurl>{escape(lec_xml.url(p))}</pathurl>{rate}<duration>{dur}</duration>{media}</file>'

    def clip(cid, p, start, end, kind, audio=False):
        dur = end - start
        st = ("<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack>"
              "<filter><effect><name>Audio Levels</name><effectid>audiolevels</effectid><effectcategory>audiolevels</effectcategory><effecttype>audiolevels</effecttype><mediatype>audio</mediatype>"
              '<parameter authoringApp="PremierePro"><parameterid>level</parameterid><name>Level</name><valuemin>0</valuemin><valuemax>3.98109</valuemax><value>1</value></parameter></effect></filter>') if audio else ""
        return (f'<clipitem id="{cid}"><name>{escape(Path(p).name)}</name><enabled>TRUE</enabled>{rate}'
                f"<start>{start}</start><end>{end}</end><in>0</in><out>{dur}</out>{file_el(p, dur, kind)}{st}</clipitem>")
    a0, a1, b1 = fr(OFF), fr(SPLIT), fr(END_ABS)
    vtr = [f"<track>{clip('v1-1', ov_b, a1, b1, 'v')}</track>", "<track></track>", "<track></track>", f"<track>{clip('v4-1', ov_a, a0, a1, 'v')}</track>"]
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
    voice = K.build_base(SEQ, OFF, END_ABS, WORK, K.SRCS_7)                                         # WORK/base_v.mp4 = 사람 화면(이 구간 컷 그대로)
    media = DELIV / "media"
    media.mkdir(parents=True, exist_ok=True)
    src = WORK / "r7p.mov"
    cut = SPLIT - OFF
    ov_a, ov_b = media / "연출층_사진덱.mov", media / "전체화면_45채36채.mov"
    tmp_a, tmp_b = WORK / "part_a.mov", WORK / "part_b.mov"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-t", f"{cut:.4f}", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", str(tmp_a)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{cut:.4f}", "-i", str(WORK / "base_v.mp4"), "-ss", f"{cut:.4f}", "-i", str(src), "-filter_complex",
                    "[0:v][1:v]overlay=format=auto,format=yuv422p10le[v]", "-map", "[v]", "-t", f"{END - cut:.4f}", "-c:v", "prores_ks", "-profile:v", "3", str(tmp_b)], check=True)
    for t, o in ((tmp_a, ov_a), (tmp_b, ov_b)):
        try:
            shutil.copy2(t, o)
        except PermissionError:
            o2 = o.with_name(o.stem + "_새판.mov")
            shutil.copy2(t, o2)
            print("  [잠김] 새 판", o2.name)
            if o == ov_a:
                ov_a = o2
            else:
                ov_b = o2
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
    RC.report(RC.check_sfx([(p["t"], p["name"], len(p["x"]) / SR) for p in placed], END), path=WORK / "점검_효과음.txt", title="r7p")
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
    # 미리보기: 사람 + 연출(전체) + 자막(사장님 V2 흉내 — 화면 전체 구간도 자막이 위)
    caps = K.captions(SEQ, OFF, END_ABS)
    font = ImageFont.truetype(str(ROOT / "소재/fonts/gmarket-sans/GmarketSansMedium.ttf"), 62)
    ins, fc, last = ["-i", str(WORK / "base_v.mp4"), "-i", str(src)], ["[0:v][1:v]overlay=format=auto[o0]"], "o0"
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
    fc.append(f"[{last}]format=yuv420p[v]")
    prev = DELIV / f"{NAME}_미리보기.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", f"{n}:a", "-t", f"{END:.4f}",
                    "-c:v", "libx264", "-crf", "15", "-c:a", "aac", "-b:a", "256k", str(prev)], check=True)
    write_xml(placed, ov_a, ov_b)
    print("미리보기", prev)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    {"out": out}[sys.argv[1]]()
