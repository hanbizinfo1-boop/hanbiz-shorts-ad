# -*- coding: utf-8 -*-
r"""7번 0~2.186 «강남이 망하면 / 우리나라 망한겁니다» — 자막 밑 실사 도미노 + 인물 펀치 (10-20).

사장님(10-20): «초반 3초는 무조건 사람얼굴나와야해서 자막밑으로 후킹줘야해» · «B로가는데 자막밑에 나오는거 인지하고 작업해»
  · «C로 만들어봐» · «C1로 하는데 저게 강남빌딩이라는건 에펙같은걸로 표시할거야?» · «진행»
기준 = 7번.prproj 18:41 «7번»: V1 7(대본즉석수정).MP4 0~2.186 원본 5.806 · 비율 61.083% · 위치 0.53:0.54875 · 자막 y 755~818.
단어 시각: 강남이 0.00 · 망하면 0.60 · 우리나라 1.12 · 망한 1.54 · 겁니다 1.88.
판 = 자막 밑 900×640 · y 860~1500(얼굴 y 400~680 · 자막 가림 0). 도미노 영상 = Kling 3.0 pro 3초(시작프레임 소재/codex/r7d_start_C1_169.png).
납품: V1 자리 인물 조각(0~2.186, 당김·흑백·흔들림 구움) · V4 도미노 판(알파) · A4~ 효과음(sfx.AD_LEVEL 기준).

    python 지시작업/tools/r7d_build.py clip <kling.mp4> <첫 도미노가 넘어지기 시작하는 영상 초>
    python 지시작업/tools/r7d_build.py person
    python 지시작업/tools/r7d_build.py panel
    python 지시작업/tools/r7d_build.py out
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
DZ = HERE.parent
ROOT = DZ.parent
sys.path.insert(0, str(ROOT / "tools"))
import sfx as SFX  # noqa: E402

SRC = Path(r"D:\26년 10월\261020\7(대본즉석수정).MP4")
WORK = DZ / "_tmp/r7d"
DELIV = DZ / "납품/7번_도미노_후킹_1020"
NAME = "7번_도미노_후킹"
W, H, FN, FD = 900, 1600, 60000, 1001
FPS = FN / FD
END = 2.186
S0, VS, VX, VY = 5.806, 0.6108333, 0.53 * W, 0.54875 * H        # 사장님 V1
FACE = (470, 560)
T_FALL, T_KOREA, T_DOWN = 0.60, 1.12, 1.54
PY, PH = 900, 450                                                  # 카드 자리(y 900~1350, 10-21 여백판)
CROP = (1536, 864)                                                 # 시작프레임(16:9) 크기 — 영상도 같은 그림
DOM = (415, 62)                                                    # 영상 첫 프레임의 첫 도미노 지붕 가운데(1536×864 좌표, 받은 영상에서 잼)
FONT = ROOT / "소재/fonts/gmarket-sans/GmarketSansBold.ttf"
SFX_LIST = [   # (시퀀스 초, 파일, 목소리 대비 dB — None 이면 sfx.AD_LEVEL)
    (0.00, "휙２.mp3", None),                       # 판 올라옴
    (0.82, "ML_Wood hard hit.wav", -4),             # 첫(강남) 도미노가 바닥에 닿음(기울기 시작 = «망하면» 0.60)
    (0.92, "도미노_연쇄.wav", -7),                  # 연쇄(clip 때 만든 한 파일 — 판이 빠질 때까지)
    (1.54, "쿠궁.mp3", None),                       # 마지막 쿵 + 인물 흑백
]
T_CRUMPLE = 1.36                                    # 10-21 구김 연출(«저런느낌이아닌데» 로 안 씀 — crumple() 은 남겨 둠)


def crumple(img, k, seed=3):
    """카드를 종이처럼 구김 — 격자 꼭짓점을 비틀고(MESH) 구김 선 명암 · 살짝 오그라듦. k 0~1."""
    if k <= 0:
        return img
    w, h = img.size
    nx, ny = 6, 4
    rng = np.random.default_rng(seed)
    jit = rng.uniform(-1, 1, (ny + 1, nx + 1, 2))
    pts = np.zeros((ny + 1, nx + 1, 2))
    for j in range(ny + 1):
        for i in range(nx + 1):
            x, y = i * w / nx, j * h / ny
            cx, cy = (x - w / 2), (y - h / 2)
            pull = .07 * k                                          # 가운데로 오그라듦
            pts[j, i] = (x - cx * pull + jit[j, i, 0] * 18 * k, y - cy * pull + jit[j, i, 1] * 14 * k)
    # MESH: 목표(구겨진 자리) 사각형마다 원본 사각형을 대응 — 목표 = 원래 격자, 원본 = 역변위
    mesh = []
    for j in range(ny):
        for i in range(nx):
            box = (int(i * w / nx), int(j * h / ny), int((i + 1) * w / nx), int((j + 1) * h / ny))
            q = []
            for (jj, ii) in ((j, i), (j + 1, i), (j + 1, i + 1), (j, i + 1)):
                gx, gy = ii * w / nx, jj * h / ny
                dx_, dy_ = pts[jj, ii] - (gx, gy)
                q += [gx - dx_, gy - dy_]
            mesh.append((box, q))
    out = img.transform((w, h), Image.MESH, mesh, Image.BICUBIC)
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    for j in range(ny + 1):                                         # 구김 선 — 밝은 선·어두운 선 번갈아
        for i in range(nx):
            a, b = pts[j, i], pts[j, i + 1]
            d.line((a[0], a[1], b[0], b[1]), fill=(255, 255, 255, int(110 * k)) if (i + j) % 2 else (0, 0, 0, int(140 * k)), width=4)
    for i in range(nx + 1):
        for j in range(ny):
            a, b = pts[j, i], pts[j + 1, i]
            d.line((a[0], a[1], b[0], b[1]), fill=(0, 0, 0, int(130 * k)) if (i + j) % 2 else (255, 255, 255, int(100 * k)), width=4)
    sh = sh.filter(ImageFilter.GaussianBlur(2.5))
    al = out.split()[3]
    out = Image.alpha_composite(out, sh)
    out.putalpha(al)
    return out


def ease(x):
    x = min(1, max(0, x))
    return 1 - (1 - x) ** 3


def frames(src, ss, n, scale=None):
    vf = f"fps={FN}/{FD}" + (f",scale={scale}" if scale else "")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ss:.4f}", "-i", str(src), "-frames:v", str(n), "-vf", vf,
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return raw


def clip(src, t_fall):
    """Kling 영상 → 첫 도미노가 넘어지는 순간을 0.60 에 맞춰 앞을 자름(속도 그대로) + 연쇄 소리 한 파일."""
    WORK.mkdir(parents=True, exist_ok=True)
    off = float(t_fall) - T_FALL
    json.dump({"src": str(src), "off": off}, open(WORK / "clip.json", "w"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, off):.4f}", "-i", str(src), "-t", f"{END + .2:.3f}", "-an",
                    "-vf", f"scale={CROP[0]}:{CROP[1]}:flags=lanczos,fps={FN}/{FD}", "-c:v", "libx264", "-crf", "12", str(WORK / "dom.mp4")], check=True)
    # 연쇄 소리: 나무토막 높음·중간·낮음 번갈아 — 0.92 부터 판이 빠지는 2.19 까지(영상 연쇄가 거의 고른 속도라 간격 0.07 → 0.05)
    SR = SFX.SR
    ks = [SFX.load(SFX.find_file(f"나무토막_{n}.wav")) for n in ("높음", "중간", "낮음")]
    ts = [0.0]
    g = .07
    while ts[-1] < END - 0.92 - .05:
        ts.append(ts[-1] + g)
        g = max(.05, g * .97)
    buf = np.zeros((int(1.5 * SR), 2))
    for j, t in enumerate(ts):
        x = ks[j % 3][: int(.12 * SR)] * (0.6 + 0.4 * np.random.default_rng(j).random()) * (1 - .5 * t / 1.3)   # 멀어질수록 작게
        s = int(t * SR)
        buf[s:s + len(x)] += x[: len(buf) - s]
    buf *= .9 / (np.abs(buf).max() + 1e-9)
    SFX.write_wav(ROOT / "소재/효과음/장면음/도미노_연쇄.wav", buf)
    print("자름", off, "· 연쇄 소리", len(ts), "번")


def person():
    """V1 자리 조각 — 사장님 배치 그대로 + 0~1.54 얼굴 쪽으로 천천히 당김 → 1.54 펀치·흑백·흔들림."""
    n = round(END * FPS)
    sw, sh = round(1728 * VS / 2) * 2, round(3072 * VS / 2) * 2
    raw = frames(SRC, S0, n, f"{sw}:{sh}")
    out = WORK / "person"
    out.mkdir(parents=True, exist_ok=True)
    for f in range(n):
        t = f / FPS
        im = Image.frombytes("RGB", (sw, sh), raw[f * sw * sh * 3:(f + 1) * sw * sh * 3])
        z = 1 + .05 * ease(t / T_DOWN) + (.08 * ease((t - T_DOWN) / .08) if t >= T_DOWN else 0)
        sx = sy = 0
        if t >= T_DOWN:
            d = t - T_DOWN
            a = 16 * np.exp(-d * 9)
            sx, sy = a * np.sin(d * 70), a * np.cos(d * 55)
        canvas = Image.new("RGB", (W, H))
        canvas.paste(im, (round(VX - sw / 2), round(VY - sh / 2)))
        cw, ch = W / z, H / z
        x0, y0 = FACE[0] - (FACE[0]) / z + sx, FACE[1] - FACE[1] / z + sy
        canvas = canvas.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS)
        if t >= T_DOWN:
            k = ease((t - T_DOWN) / .06)
            canvas = Image.blend(canvas, canvas.convert("L").convert("RGB"), k)
        canvas.save(out / f"p_{f:04d}.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", f"{FN}/{FD}", "-i", str(out / "p_%04d.png"), "-c:v", "prores_ks", "-profile:v", "3",
                    "-pix_fmt", "yuv422p10le", str(WORK / "인물_흑백펀치.mov")], check=True)
    print("인물 조각", n)


def panel():
    """V4 — 자막 밑 도미노 판(0~0.15 올라옴 · 2.03~ 떨어지며 빠짐) + 0~0.6 핀·«강남» 꼬리표."""
    n = round(END * FPS)
    raw = frames(WORK / "dom.mp4", 0, n + 2)
    # 10-21 사장님 «지도가 너무 크게들어가 조금 테두리 보이게 적용하자» «좌우 여백좀 남게» → 영상을 자르지 않고 통째로 카드(800×450)에 · 좌우 여백 50 · 흰 테두리 · 둥근 모서리 · 그림자
    CW, CH, CX = 800, 450, 50
    sc = CW / CROP[0]
    font = ImageFont.truetype(str(FONT), 36)
    dx, dy = DOM[0] * sc, DOM[1] * sc                             # 카드 안 좌표
    out = WORK / "panel"
    out.mkdir(parents=True, exist_ok=True)
    fb = CROP[0] * CROP[1] * 3
    mask = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, CW - 1, CH - 1), 22, fill=255)
    shadow = Image.new("RGBA", (W, CH + 120), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((CX + 6, 40 + 14, CX + CW + 6, 40 + CH + 14), 22, fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    for f in range(n):
        t = f / FPS
        fr = Image.frombytes("RGB", CROP, raw[min(f, len(raw) // fb - 1) * fb:(min(f, len(raw) // fb - 1) + 1) * fb])
        p = fr.resize((CW, CH), Image.LANCZOS).convert("RGBA")
        # 꼬리표: 0.05~0.60 꽂혀 있다가 0.60~0.80 기울며 떨어져 사라짐
        u = (t - .05) / .18
        if u > 0 and t < .82:
            tag = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
            d = ImageDraw.Draw(tag)
            k = ease(u)
            fall = ease((t - T_FALL) / .2) if t > T_FALL else 0
            ox, oy = dx + 85 + 40 * fall, dy + 72 - 30 * (1 - k) + 120 * fall
            al = int(255 * min(1, u * 2) * (1 - fall))
            d.ellipse((dx - 9, dy - 9 + 10, dx + 9, dy + 9 + 10), fill=(255, 212, 59, al), outline=(0, 0, 0, al), width=3)   # 지붕 위 금빛 점
            d.line((dx + 8, dy + 14, ox - 6, oy + 6), fill=(255, 255, 255, al), width=4)
            d.rounded_rectangle((ox - 8, oy - 30, ox + 110, oy + 34), 12, fill=(0, 0, 0, int(al * .78)), outline=(255, 212, 59, al), width=3)
            d.text((ox + 51, oy + 2), "강남", font=font, fill=(255, 255, 255, al), anchor="mm")
            p = Image.alpha_composite(p, tag)
            # 금빛 빛무리(0~0.6 한 번 숨 쉬듯)
            if t < T_FALL:
                gl = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
                r = 60 + 30 * np.sin(t / T_FALL * np.pi)
                ImageDraw.Draw(gl).ellipse((dx - r, dy + 60 - r * 1.6, dx + r, dy + 60 + r * 1.6), fill=(255, 200, 80, int(70 * np.sin(t / T_FALL * np.pi))))
                p = Image.alpha_composite(p, gl.filter(ImageFilter.GaussianBlur(30)))
        a_in = ease(t / .15)
        a_out = ease((t - 2.03) / .15) if t > 2.03 else 0
        y = PY + 90 * (1 - a_in) + 70 * a_out
        op = a_in * (1 - a_out)
        p.putalpha(mask)
        ImageDraw.Draw(p).rounded_rectangle((1, 1, CW - 2, CH - 2), 22, outline=(255, 255, 255, 255), width=5)   # 흰 테두리
        # 10-21 «흑백일때 얘만 멀쩡해서 좀 어색해 흑백일떄 얘도 무슨 비슷한종류의 효과를 줘야할거같아» → 인물과 같이 1.54 흑백 + 같은 흔들림 + 살짝 어둡게(구김은 «저런느낌이아닌데»로 뺌)
        sx = sy = 0
        if t >= T_DOWN:
            kk = ease((t - T_DOWN) / .06)
            rgb = p.convert("RGB")
            g = rgb.convert("L").convert("RGB").point(lambda v: int(v * .85))
            p = Image.merge("RGBA", (*Image.blend(rgb, g, kk).split(), p.split()[3]))
            d_ = t - T_DOWN
            a_ = 16 * np.exp(-d_ * 9)
            sx, sy = a_ * np.sin(d_ * 70), a_ * np.cos(d_ * 55)            # 인물 조각과 같은 식
        layer = shadow.copy()
        layer.alpha_composite(p, (CX + round(sx), 40 + round(sy)))
        pa = np.array(layer)
        pa[..., 3] = (pa[..., 3] * op).astype(np.uint8)
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        canvas.alpha_composite(Image.fromarray(pa), (0, round(y) - 40))
        canvas.save(out / f"d_{f:04d}.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", f"{FN}/{FD}", "-i", str(out / "d_%04d.png"), "-c:v", "prores_ks", "-profile:v", "4",
                    "-pix_fmt", "yuva444p10le", str(WORK / "도미노판.mov")], check=True)
    print("도미노 판", n)


def out():
    import shutil
    import rule_check as RC
    media = DELIV / "media"
    media.mkdir(parents=True, exist_ok=True)
    pv, dv = media / "인물_흑백펀치.mov", media / "도미노판.mov"
    for a, b in ((WORK / "인물_흑백펀치.mov", pv), (WORK / "도미노판.mov", dv)):
        try:
            shutil.copy2(a, b)
        except PermissionError:
            print("  [잠김]", b.name)
    # 효과음 — 목소리 대비(50ms RMS) 기준값으로 구워 낱개 wav
    voice = SFX.load(WORK / "voice.wav") if (WORK / "voice.wav").exists() else None
    if voice is None:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{S0}", "-t", f"{END}", "-i", str(SRC), "-vn", "-ar", "48000", "-ac", "2",
                        str(WORK / "voice.wav")], check=True)
        voice = SFX.load(WORK / "voice.wav")
    voice *= 10 ** (6 / 20)                                       # 사장님 A1 +6dB
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
        placed.append(dict(t=max(0, t - SFX.attack_at(x)), x=x, name=name, label=f"{name}@{t:.2f}"))
    for lv, rule, msg in SFX.fit_tails(placed):
        print(f"  [{lv}] {rule}: {msg}")
    items = RC.check_sfx([(p["t"], p["name"], len(p["x"]) / SR) for p in placed], END)
    RC.report(items, path=WORK / "점검_효과음.txt", title="r7d")
    for i, p in enumerate(placed):
        p["path"] = media / f"SFX_{i + 1:02d}_{Path(p['name']).stem[:20].replace(' ', '_')}.wav"
        try:
            SFX.write_wav(p["path"], p["x"])
        except Exception:
            print("  [잠김]", p["path"].name)
    mix = voice.copy()
    for p in placed:
        s = int(p["t"] * SR)
        mix[s:s + len(p["x"])] += p["x"][: len(mix) - s]
    SFX.write_wav(WORK / "mix_pre.wav", mix * min(1, .95 / (np.abs(mix).max() + 1e-9)))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(WORK / "mix_pre.wav"), "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000", str(WORK / "mix.wav")], check=True)
    # 미리보기: 인물 조각 + 사장님 자막 흉내(흰 글, 자리 y 787) + 도미노 판
    cap = WORK / "cap.png"
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    font = ImageFont.truetype(str(ROOT / "소재/fonts/gmarket-sans/GmarketSansMedium.ttf"), 62)
    caps = [(0, .6 + .484, "강남이 망하면"), (1.084, END, "우리나라 망한겁니다")]
    for k, (a, b, s) in enumerate(caps):
        c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(c)
        bb = d.textbbox((W / 2, 787), s, font=font, anchor="mm")
        d.rectangle((bb[0] - 14, bb[1] - 12, bb[2] + 14, bb[3] + 12), fill=(0, 0, 0, 230))
        d.text((W / 2, 787), s, font=font, fill="white", anchor="mm")
        c.save(WORK / f"cap{k}.png")
    prev = DELIV / f"{NAME}_미리보기.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(pv), "-loop", "1", "-i", str(WORK / "cap0.png"), "-loop", "1", "-i", str(WORK / "cap1.png"),
                    "-i", str(dv), "-i", str(WORK / "mix.wav"), "-filter_complex",
                    "[0:v][1:v]overlay=enable='lt(t,1.084)'[a];[a][2:v]overlay=enable='gte(t,1.084)'[b];[b][3:v]overlay=format=auto,format=yuv420p[v]",
                    "-map", "[v]", "-map", "4:a", "-t", f"{END}", "-c:v", "libx264", "-crf", "15", "-c:a", "aac", "-b:a", "256k", str(prev)], check=True)
    write_xml(placed, pv, dv)
    print("미리보기", prev)


def write_xml(placed, pv, dv):
    from xml.sax.saxutils import escape
    import lec_xml
    rate = "<rate><timebase>60</timebase><ntsc>TRUE</ntsc></rate>"
    fr = lambda s: int(round(s * FPS))   # noqa: E731
    total = fr(END)
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
                f"<start>{start}</start><end>{end}</end><in>0</in><out>{end - start}</out>{file_el(p, dur, kind)}{st}</clipitem>")
    vtr = [f"<track>{clip('v1-1', pv, 0, total, 'v')}</track>", "<track></track>", "<track></track>", f"<track>{clip('v4-1', dv, 0, total, 'v')}</track>"]
    atr = ["<track></track>"] * 3
    for i, p in enumerate(placed):
        s = fr(p["t"])
        d = max(1, int(len(p["x"]) / SFX.SR * FPS + 1e-6))
        atr.append(f"<track>{clip(f'sfx-{i + 1}', p['path'], s, min(s + d, total), 'a', d, audio=True)}</track>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="5"><sequence id="seq-1">'
           f"<name>{NAME}</name><duration>{total}</duration>{rate}<media><video><format><samplecharacteristics>{rate}<width>{W}</width><height>{H}</height>"
           "<pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance></samplecharacteristics></format>"
           f"{''.join(vtr)}</video><audio><numOutputChannels>2</numOutputChannels>{''.join(atr)}</audio></media></sequence></xmeml>")
    (DELIV / f"{NAME}.xml").write_text(xml, encoding="utf-8")
    print("XML", DELIV / f"{NAME}.xml")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    WORK.mkdir(parents=True, exist_ok=True)
    c = sys.argv[1]
    if c == "clip":
        clip(sys.argv[2], sys.argv[3])
    else:
        {"person": person, "panel": panel, "out": out}[c]()
