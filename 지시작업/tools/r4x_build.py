# -*- coding: utf-8 -*-
r"""4번 앞 3.47초 «강남빌딩 vs 예금·주식 인형» 연출 → 사장님 시퀀스(900×1600 · 59.94)에 얹는 XML (10-20).

사장님(10-20):
  «이제 부터 내가 원하는 연출을 xml로 만들어줘 자막밑에 들어갈 그림설계로
   강남빌딩보다 확실한투자가있다? 이거할때 강남빌딩이 오른쪽 위에서 약간 사선으로 굴곡지게 자막밑으로 박히는연출로 시작해서
   확실한투자가 있다 할때 오른쪽에서 [흰 인형] 이런 사람인데 예금,주식 이런게 적혀있는 사람모형 나와서 강남빌딩을 옆으로 밀어내고 약간 근육자랑하는연출을 하고
   아 말도안돼요 할때 화면이 확대되면서 대표님 손 짓에 맞춰 그 사람이 손에 치여날라가고(약간 피융~ 하는 애니메이션 날아가는 효과음)
   강남빌딩이 가운데로오면서 좀 커지면서 빵빠레 연출(따딴~~ 하는 연출음)»
  «대표님 확대되고 손짓위치랑 사람 위치가 잘맞아야지 이 연출이산다» «아 말도안돼요 그거는 << 까지 xml로 만들어주면 돼»
  «이거를 이제 좀 상호작용을 잘해야한다 부드럽게 퀄리티낮게하면안돼»

기준 = 사장님 프리미어 «4번»(10-20 10:30 저장) — 900×1600 · 59.94 · V1 4.MP4 비율 52.083% 위치 0.5:0.562 · 자막 900~950px.
손 궤적(확대 구운 바탕에서 60fps 직접 잼, 시퀀스 초 · 화면 좌표): 2.069 (340,1480) → 2.135 (360,1280) → 2.202 (300,1170) → 2.236 (180,1040) → 2.302 (10,1150) — 맞는 순간 2.125
확대: 1.969 부터 0.13초 동안 52.083% → 65.104%(1.25배), 가운데 x 450 → 562 (손이 화면 안에서 인형 자리를 지나가게). 바탕에 구워 V1 에 넣는다(XML 키프레임은 시험 못 함).

    python 지시작업/tools/r4x_build.py base       # V1 두 조각(확대 구움) · 미리보기용 자막 층
    python tools/html_motion.py 지시작업/tools/scenes/r4x.html --alpha --fps 59.94 --workers 2 --sub 4 --out 지시작업/_tmp/r4x --name r4x
    python 지시작업/tools/r4x_build.py out        # 효과음 · 미리보기 mp4 · XML
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DZ = HERE.parent
ROOT = DZ.parent
sys.path.insert(0, str(ROOT / "tools"))
import sfx as SFX  # noqa: E402

SRC = Path(r"D:\26년 10월\261020\4.MP4")
WORK = DZ / "_tmp/r4x"
DELIV = DZ / "납품/4번_앞부분_빌딩인형_1020"
NAME = "4번_앞부분_빌딩인형"
W, H = 900, 1600
FN, FD = 60000, 1001
FPS = FN / FD
END = 3.47
CUTS = [(0.0, 1.969, 14.381), (1.969, 3.47, 16.5)]     # 사장님 V1 (시퀀스 시작, 끝, 원본 시작)
POS_Y = 0.562 * H                                      # 사장님 V1 위치(가운데 y)
ZOOM = dict(t0=1.969, dur=0.131, s=1.0, dx=0)          # 10-20 사장님 «말도안돼요 그거는 이쪽은 원본이 낫겠다» → 확대 없음(예전 1.25배 · x+112)

# 자막(사장님 V2 — 미리보기에만 그린다, XML 에는 안 넣음): (시작, 끝, [(글, 초록?)])
CAPS = [(0.0, 0.884, [("강남 빌딩보다", 0)]), (0.884, 1.969, [("확실한 투자가 있다?", 1)]),
        (1.969, 2.719, [("아, 말도 안돼요", 0)]), (2.719, 3.47, [("그거는", 0)])]
CAP_Y = 924

# 효과음(시퀀스 초, 파일, 목소리 대비 dB) — 말 있는 쇼츠라 목소리 밑. 사장님이 콕 집은 «피융»·«따단» 은 조금 크게
SFX_LIST = [
    (0.00, "ML_Flying fast swoosh.wav", -9, "peak", 0.36),      # 빌딩이 사선으로 날아옴(들리는 정점 = 박히기 직전)
    (0.42, "KN_impactPunch_heavy_000.wav", -5, "onset", 0),      # 박힘
    (0.90, "ML_Fast small sweep transition.wav", -10, "onset", 0),   # 인형 등장
    (1.12, "KN_impactSoft_heavy_000.wav", -8, "onset", 0),       # 밀어냄
    (1.45, "ML_Boing hit sound.wav", -10, "onset", 0),           # 근육 자랑
    (2.09, "ML_Cartoon punch.wav", -6, "onset", 0),             # 손에 맞음
    (2.236, "날아가는소리1.mp3", -4, "onset", 0),                 # 피융~(손을 떠나는 순간)
    # 10-20 사장님 «손에 사람 팅겨져 나가는거까지만 연출하고 그냥 말도안돼요 그거는 이쪽은 원본이 낫겠다» → 확대·빌딩 복귀·빵빠레 뺌
]


def zoom_expr():
    k = f"min(max((t)/{ZOOM['dur']}\\,0)\\,1)"
    e = f"(1-pow(1-{k}\\,3))"
    s = f"(1+{ZOOM['s'] - 1}*{e})"
    return s, e


def base():
    """V1 두 조각: ① 0~1.969 사장님 배치 그대로 ② 1.969~3.47 확대 구움. 둘 다 900×1600 59.94."""
    WORK.mkdir(parents=True, exist_ok=True)
    DELIV.mkdir(parents=True, exist_ok=True)
    (DELIV / "media").mkdir(exist_ok=True)
    for i, (t0, t1, s0) in enumerate(CUTS):
        n = round(t1 * FPS) - round(t0 * FPS)
        out = WORK / f"V1_{i + 1}.mov"   # 미리보기 바탕만(XML 은 사장님 V1 원본 그대로)
        if i == 0:
            s, e = "1", "0"
        else:
            s, e = zoom_expr()
        fc = (f"color=c=black:s={W}x{H}:r={FN}/{FD}[bg];"
              f"[0:v]setpts=PTS-STARTPTS,scale=w='trunc({W}*{s}/2)*2':h='trunc({H}*{s}/2)*2':eval=frame:flags=lanczos[v];"
              f"[bg][v]overlay=x='{W / 2}+{ZOOM['dx']}*{e}-overlay_w/2':y='{POS_Y}-overlay_h/2':eval=frame:shortest=1,format=yuv422p10le[o]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s0:.4f}", "-i", str(SRC), "-frames:v", str(n), "-filter_complex", fc,
                        "-map", "[o]", "-map", "0:a:0", "-t", f"{n / FPS:.4f}", "-c:v", "prores_ks", "-profile:v", "3",
                        "-c:a", "pcm_s16le", "-ar", "48000", str(out)], check=True)
        print("V1", out.name, n, "프레임")


def caption_layer():
    """미리보기용 자막(지마켓 Medium, 흰/초록 0,252,0, 팝 130→100 0.216초) PNG 시퀀스."""
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(str(ROOT / "소재/fonts/gmarket-sans/GmarketSansMedium.ttf"), 62)
    d = WORK / "cap"
    d.mkdir(exist_ok=True)
    n = round(END * FPS)
    for f in range(n):
        t = f / FPS
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for c0, c1, runs in CAPS:
            if not (c0 <= t < c1):
                continue
            k = min(1, (t - c0) / 0.216)
            sc = 1.3 - 0.3 * k
            txt = "".join(r for r, _ in runs)
            tmp = Image.new("RGBA", (W * 2, 200), (0, 0, 0, 0))
            dr = ImageDraw.Draw(tmp)
            x = 0
            for r, g in runs:
                dr.text((x, 40), r, font=font, fill=(0, 252, 0, 255) if g else (255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 200))
                x += dr.textlength(r, font=font)
            box = tmp.getbbox()
            tmp = tmp.crop(box)
            tmp = tmp.resize((max(1, int(tmp.width * sc)), max(1, int(tmp.height * sc))), Image.LANCZOS)
            im.alpha_composite(tmp, (int(W / 2 - tmp.width / 2), int(CAP_Y - tmp.height / 2)))
        im.save(d / f"c_{f:05d}.png")
    print("자막 층", n)


def out():
    media = DELIV / "media"
    ovl = media / "연출층_빌딩인형.mov"
    shutil.copy2(WORK / "r4x.mov", ovl)
    # 효과음 낱개(목소리 대비 크기는 sfx.prep 기준) → media/SFX_*.wav
    vo = WORK / "voice.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(WORK / "base_full.mov"), "-vn",   # 10-20 V1 조각이 둘보다 많을 수 있어 이어 붙인 바탕에서 소리를 뽑음
                    "-ar", "48000", "-ac", "2", str(vo)], check=True)
    voice = SFX.load(vo)
    ref = SFX.voice_ref_from(voice)
    SR = SFX.SR
    placed = []
    for i, (t, name, db, align, peak_off) in enumerate(SFX_LIST):
        x = SFX.load(SFX.find_file(name))
        a = np.abs(x).max(1)
        x = x[int(np.argmax(a > a.max() * 10 ** (-40 / 20))):]                     # 앞 무음 제거(sfx.prep 와 같음)
        e = np.abs(x).max(1)
        loud = np.where(e > e.max() * 10 ** (-45 / 20))[0]
        x = x[: min((loud[-1] + 1) if len(loud) else len(x), int(SFX.TAIL_MAX * SR))].copy()   # 자연히 잦아드는 곳까지
        fo = min(len(x) // 3, int(0.25 * SR))
        x[-fo:] *= (np.linspace(1, 0, fo) ** 2)[:, None]
        if db is None:                                                               # 10-20 기준 — 타격 −2 · 휙 −5 · 작은 소리 −7(sfx.AD_LEVEL)
            db = SFX.ad_target(name)
        x *= 10 ** ((ref + db - SFX.rms_frames(x).max()) / 20)                       # 목소리 대비 db(50ms RMS)
        x *= min(1.0, 0.5 / (np.abs(x).max() + 1e-9))                                  # 피크 −6dBFS 상한
        off = SFX.attack_at(x) if align == "onset" else peak_off
        placed.append(dict(t=max(0.0, t - off), x=x, name=name, label=f"{name}@{t:.2f}s"))
    for lv, rule, msg in SFX.fit_tails(placed):                                       # 겹치면 다음 소리 직전 0.2초 감쇠(sfx.md 결정표)
        print(f"  [{lv}] {rule}: {msg}")
    for i, p in enumerate(placed):
        p["path"] = media / f"SFX_{i + 1:02d}_{Path(p['name']).stem[:22].replace(' ', '_')}.wav"
        try:
            SFX.write_wav(p["path"], p["x"])
        except Exception as e:   # 프리미어가 열어 둔 파일(잠김) — 사장님 규칙 9: 남기고 알린다
            print(f"  [잠김] {p['path'].name} — 덮어쓰지 못해 기존 파일 그대로 ({type(e).__name__})")
    # 미리보기 소리: 목소리 + 효과음 → −14 LUFS
    n = len(voice)
    mix = voice.copy()
    for p in placed:
        s0 = int(p["t"] * SR)
        seg = p["x"][: max(0, n - s0)]
        mix[s0:s0 + len(seg)] += seg
    pre = WORK / "mix_pre.wav"
    SFX.write_wav(pre, mix * min(1.0, 0.95 / (np.abs(mix).max() + 1e-9)))
    mixf = WORK / "mix.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(pre), "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000", str(mixf)], check=True)
    prev = DELIV / f"{NAME}_미리보기.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(WORK / "base_full.mov"), "-i", str(ovl), "-framerate", f"{FN}/{FD}", "-i", str(WORK / "cap/c_%05d.png"),
                    "-i", str(mixf), "-filter_complex", "[0:v][1:v]overlay=format=auto[a];[a][2:v]overlay=format=auto,format=yuv420p[v]",
                    "-map", "[v]", "-map", "3:a", "-c:v", "libx264", "-crf", "15", "-preset", "slow", "-c:a", "aac", "-b:a", "256k", "-shortest", str(prev)], check=True)
    write_xml(placed, ovl)
    print("효과음", len(placed), "· 미리보기", prev.name)


def write_xml(placed, ovl):
    """FCP7 XML(사장님 시퀀스와 같은 900×1600 · 59.94) — V1 두 조각(원래 배치 · 확대 구움) · V2 연출층 · A1 목소리(V1 소리) · A2~ 효과음.
    프리미어에서 «가져오기» 한 뒤 V2·A2~ 를 사장님 «4번» 0초에 얹으면 된다(V1_2 는 1.969 에 V1 위에 덮어씀)."""
    from xml.sax.saxutils import escape
    import urllib.parse

    import lec_xml

    def url(p):   # 10-20 사장님 «xml에 이렇게뜨는데?»(영상 빨강=오프라인) → 검증된 lec_xml.url(C%3A 모양)
        return lec_xml.url(p)
    rate = "<rate><timebase>60</timebase><ntsc>TRUE</ntsc></rate>"
    fr = lambda s: int(round(s * FPS))   # noqa: E731
    total = fr(END)
    files = {}

    def file_el(p, dur, kind):
        k = str(p)
        if k in files:
            return f'<file id="{files[k]}"/>'
        fid = f"file-{len(files) + 1}"
        files[k] = fid
        media = ("<media><audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics><channelcount>2</channelcount></audio></media>"
                 if kind == "a" else f"<media><video><samplecharacteristics>{rate}<width>{W}</width><height>{H}</height><pixelaspectratio>square</pixelaspectratio></samplecharacteristics></video></media>")   # 연출층 MOV 는 소리 없음 — 소리까지 적으면 프리미어가 오프라인으로 봄
        return f'<file id="{fid}"><name>{escape(Path(p).name)}</name><pathurl>{escape(url(p))}</pathurl>{rate}<duration>{dur}</duration>{media}</file>'

    def clip(cid, p, start, end, kind, src_in=0, dur=None, audio=False):
        dur = dur or (end - start)
        st = ("<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack>"
              "<filter><effect><name>Audio Levels</name><effectid>audiolevels</effectid><effectcategory>audiolevels</effectcategory><effecttype>audiolevels</effecttype><mediatype>audio</mediatype>"
              '<parameter authoringApp="PremierePro"><parameterid>level</parameterid><name>Level</name><valuemin>0</valuemin><valuemax>3.98109</valuemax><value>1</value></parameter></effect></filter>') if audio else ""   # 10-20 검증본(edit_xml) 모양
        return (f'<clipitem id="{cid}"><name>{escape(Path(p).name)}</name><enabled>TRUE</enabled>{rate}'
                f"<start>{start}</start><end>{end}</end><in>{src_in}</in><out>{src_in + end - start}</out>{file_el(p, dur, kind)}{st}</clipitem>")
    media = DELIV / "media"
    c0, c1 = fr(CUTS[0][1]), total
    v2 = clip("v2-1", ovl, 0, total, "v")
    atr = []   # 사장님 V1·목소리는 원본 그대로 — 연출층(V1 자리)과 효과음만 얹는다
    for i, p in enumerate(placed):
        s = fr(p["t"])
        d = max(1, int(len(p["x"]) / SFX.SR * FPS + 1e-6))   # 내림 — 반올림하면 파일보다 1프레임 길어 빗금(10-20)
        atr.append(f"<track>{clip(f'sfx-{i + 1}', p['path'], s, min(s + d, total), 'a', 0, d, audio=True)}</track>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="5"><sequence id="seq-1">'
           f"<name>{NAME}</name><duration>{total}</duration>{rate}<media><video><format><samplecharacteristics>{rate}<width>{W}</width><height>{H}</height>"
           "<pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance></samplecharacteristics></format>"
           f"<track>{v2}</track></video><audio><numOutputChannels>2</numOutputChannels>{''.join(atr)}</audio></media></sequence></xmeml>")
    path = DELIV / f"{NAME}.xml"
    path.write_text(xml, encoding="utf-8")
    print("XML", path)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    {"base": base, "caps": caption_layer, "out": out}[sys.argv[1]]()
