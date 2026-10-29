# -*- coding: utf-8 -*-
# ★ 본보기(원본 경로 상수 그대로) — 실행을 보장하지 않는다. 베껴 쓰지 말고 «이런 식으로 짠다»를 본다.
# 보여 주는 것: 분양 PDF 계획도가 지도 펼쳐지듯(3쪽 경첩, 3D) → 캐릭터가 부지를 톡 → 조감도 카드가 방사 흐림으로 빨려 듦(AE JSX)
# 원본: D:/영상제작/도구/광고편집/b4_cine.py (통과/반려 이력은 references/feedback-log.md)
# 모듈 대응: bisa_web_vs_instant → ae_scene · bisa_meta_sfx / bisa_toc_cards.by_name → sfx · rf3_ae·rule_check·lec_xml·design_layers → tools/ 같은 이름.
# 이 폴더에 없는 모듈(bisa_ab_setup 1판, bisa_toc_cards 노트 틀 등)을 import 하는 줄은 원본을 읽어 대응한다.
r"""분양4 — «혹시 지금 김포에서 사업비만 2조 넘게 투입되는 초대형 프로젝트 ○○단지 사업이» 애펙 장면 (사장님 09-30).

  python b4_cine.py            → 바탕화면\분양\완성본\분양4\02_○○단지_지도캐릭터조감도_드론.mp4 (+ 효과음 wav)

사장님 연출(09-30):
  «김포에서 ~ 투입되는» 까지 계획도가 지도 펼쳐지듯(애펙) → 캐릭터가 나와 손가락으로 찍음(애펙)
  → «초대형 프로젝트» 계획도 위 가운데에 조감도가 작게 → «○○단지 사업이» 조감도 속으로 빨려 들어가며
  → 블렌더+제미나이로 만든 조감도 실사(야경) 드론 영상 3초
시각(분양4 시퀀스 초, 자막 텍스트 그래픽 기준 — 길라잡이\분양4-자막타임라인.json) — 장면 0초 = 3.171
  3.171 «혹시 지금 김포에서»        계획도 3쪽이 펼쳐짐(가운데 → 양옆이 경첩처럼 젖혀짐)
  4.821 «2조 넘게 투입되는»         캐릭터가 오른쪽 아래서 들어와(0.3초) 단지 부지를 손끝으로 톡(5.12) → 노란 파동 2겹 + 부지 테두리
  5.873 «초대형 프로젝트»           조감도(흰 테두리 카드)가 가운데에 톡 튀어나옴
  6.673 «○○단지 사업이»     조감도가 화면을 채우며 빨려 듦(방사 흐림) → 7.02부터 드론 영상 3초로 녹아듦
소재: 부동산배포 1안 4쪽 계획도·조감도(앞 편 미사용) · Codex 캐릭터 · 드론 영상(Gemini)
효과음: 사장님이 분양과오2에 쓴 파일만(제작규칙 5-6)
"""
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import rf3_ae as AE  # noqa: E402

W, H, FPS = 1080, 1920, 29.97
T0 = 3.171
A = lambda t: round(t - T0, 3)  # noqa: E731
EV = dict(unfold=A(4.304), char=A(4.821), tap=A(4.99), bird=A(5.873), suck=A(6.673))   # v3: «김포에서»=김포 항공, «사업비만»=지도 펼침, «2조»=캐릭터
AERIAL = Path(r"D:\영상제작\_tmp\분양4\gimpo\gimpo-aerial.png")   # 시안4(Codex 김포 한강변 항공) — 사장님 10-01 «시안4로 고고»
SUCK = 0.42
VID_IN = EV["suck"] + SUCK - 0.08        # 드론 영상이 녹아들기 시작
VID_LEN = 3.0
WITH_DRONE = False                        # v2(09-30 사장님): AI 영상 전환은 사장님이 — 빨려 드는 데서 끝낸다
DUR = round(VID_IN + VID_LEN, 3) if WITH_DRONE else round(EV["suck"] + SUCK + 0.1, 3)
SRC = Path(r"D:\영상제작\_tmp\분양4")
WORK = Path(r"D:\영상제작\_tmp\분양4\ae_cine")
OUT = Path(r"C:\Users\user\Desktop\분양\완성본\분양4")
MAP = SRC / "pdf" / "crop_A4_계획도.png"
BIRD = SRC / "pdf" / "crop_A4_조감도.png"
CHAR = SRC / "cine" / "char-point.png"
DRONE = SRC / "cine" / "ai-cine-night.mp4"
PARCEL = (1091, 589)                      # 계획도(1512×979) 안 단지 부지 가운데
TIP = (1024 - 71, 66)                     # 캐릭터(1024×1536) 손끝 — v2: 좌우 뒤집어 왼쪽 아래서 오른쪽을 가리킴(얼굴이 화면 안에)
MAP_W, MAP_CX, MAP_CY = 1000, 540, 960    # 화면 위 계획도 크기·가운데 (v2: 정가운데)
CHAR_S = 0.55
BIRD_W = 620
SFXD = Path(r"C:\Users\user\Desktop\작업공간\효과음\효과음")
SFX = [(0.0, SFXD / "휙２.mp3", -3), (EV["unfold"], SFXD / "종이넘기는 소리.mp3", 0), (EV["char"], SFXD / "두꺼운 바람.mp3", -4),
       (EV["tap"], Path(r"C:\Users\user\Desktop\분양\완성본\후킹AI\효과음\03_더블역세권\c_배지_5호선_톡.wav"), 0),
       (EV["bird"], SFXD / "2. 띠딩2.mp3", -3),
       (EV["suck"], Path(r"C:\Users\user\Desktop\분양\완성본\후킹AI\효과음\04_커뮤니티\c_빨려들어감_휘익.wav"), 0),
       (VID_IN, Path(r"C:\Users\user\Desktop\분양\효과음\분양1_v4_장면음\소리\sfx-drone_a.wav"), -6)]
if not WITH_DRONE:
    SFX = SFX[:-1]


def pieces():
    WORK.mkdir(parents=True, exist_ok=True)
    m = Image.open(MAP).convert("RGB")
    k = MAP_W / m.width
    mh = round(m.height * k)
    ms = m.resize((MAP_W, mh), Image.LANCZOS)
    out = {"map_h": mh}
    # 3쪽(가운데·왼쪽·오른쪽) — 지도 펼치기
    third = MAP_W // 3
    for i, nm in enumerate(("L", "C", "R")):
        x0, x1 = i * third, (MAP_W if i == 2 else (i + 1) * third)
        p = WORK / f"map_{nm}.png"
        ms.crop((x0, 0, x1, mh)).save(p)
        out[f"map_{nm}"] = (p, x1 - x0)
    # 바탕: 계획도를 크게 흐리게(까만 화면 금지 — 제작규칙 1-4)
    bg = m.resize((round(m.width * H / m.height), H), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, 0, (bg.width - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(28))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (20, 32, 40)), 0.45)
    bg.save(WORK / "bg.png")
    ae = Image.open(AERIAL).convert("RGB")
    ae = ae.resize((W, round(ae.height * W / ae.width)), Image.LANCZOS)
    if ae.height < H:
        ae = ae.resize((round(ae.width * H / ae.height), H), Image.LANCZOS)
    ae = ae.crop(((ae.width - W) // 2, (ae.height - H) // 2, (ae.width - W) // 2 + W, (ae.height - H) // 2 + H))
    ae.save(WORK / "aerial.png")
    # 단지 부지 테두리(노랑) — 계획도 크기 캔버스
    a = np.array(m).astype(int)
    mask = (a[..., 1] > 55) & (a[..., 1] < 110) & (a[..., 0] < 40) & (a[..., 2] > 45) & (a[..., 2] < 100)
    mask[:520, :] = False                  # 위쪽 라벨 상자는 뺀다
    mi = Image.fromarray((mask * 255).astype("uint8")).resize((MAP_W, mh), Image.NEAREST)
    edge = mi.filter(ImageFilter.MaxFilter(9))
    ring = Image.eval(edge, lambda v: v) .point(lambda v: 255 if v > 0 else 0)
    inner = mi.filter(ImageFilter.MaxFilter(3))
    outline = Image.fromarray(np.clip(np.array(ring).astype(int) - np.array(inner).astype(int), 0, 255).astype("uint8"))
    ol = Image.new("RGBA", (MAP_W, mh), (0, 0, 0, 0))
    ol.paste((255, 222, 40, 255), mask=outline)
    ol.save(WORK / "parcel_ol.png")
    # 파동 고리
    s = 4
    rg = Image.new("RGBA", (200 * s, 200 * s), (0, 0, 0, 0))
    ImageDraw.Draw(rg).ellipse((6 * s, 6 * s, 194 * s, 194 * s), outline=(255, 222, 40, 255), width=7 * s)
    rg.resize((200, 200), Image.LANCZOS).save(WORK / "ring.png")
    # 조감도 카드(흰 테두리 + 그림자)
    b = Image.open(BIRD).convert("RGB")
    bh = round(b.height * BIRD_W / b.width)
    b = b.resize((BIRD_W, bh), Image.LANCZOS)
    pad, bd = 40, 10
    card = Image.new("RGBA", (BIRD_W + 2 * bd + 2 * pad, bh + 2 * bd + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 10, pad + BIRD_W + 2 * bd, pad + bh + 2 * bd + 10), 14, fill=(0, 0, 0, 150))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    ImageDraw.Draw(card).rounded_rectangle((pad, pad, pad + BIRD_W + 2 * bd, pad + bh + 2 * bd), 14, fill=(255, 255, 255, 255))
    card.paste(b, (pad + bd, pad + bd))
    card.save(WORK / "bird_card.png")
    out["bird"] = (WORK / "bird_card.png", card.size)
    # 캐릭터 축소
    c = Image.open(CHAR).convert("RGBA")
    c = c.resize((round(c.width * CHAR_S), round(c.height * CHAR_S)), Image.LANCZOS).transpose(Image.FLIP_LEFT_RIGHT)
    c.save(WORK / "char.png")
    out["char"] = c.size
    return out


def jsx(pc, out_mov):
    js = AE.js
    L = []
    a = L.append
    mh = pc["map_h"]
    mx0, my0 = MAP_CX - MAP_W / 2, MAP_CY - mh / 2
    px, py = mx0 + PARCEL[0] * MAP_W / 1512, my0 + PARCEL[1] * mh / 979
    a(f"(function(){{ var comp=app.project.items.addComp('b4_cine',{W},{H},1,{DUR:.3f},{FPS}); comp.motionBlur=true;")
    # 드론 영상(맨 아래) — 녹아듦
    if WITH_DRONE:
        a(f"var iv=imp({js(str(DRONE))}); var Lv=comp.layers.add(iv); Lv.startTime={VID_IN:.3f}; Lv.transform.scale.setValue([{W / 720 * 100:.2f},{W / 720 * 100:.2f}]);")
        a(f"keys(Lv.transform.opacity,[[{VID_IN:.3f},0],[{VID_IN + 0.3:.3f},100]]);")
        a(f"keys(Lv.transform.scale,[[{VID_IN:.3f},[{W / 720 * 130:.1f},{W / 720 * 130:.1f}]],[{VID_IN + 0.6:.3f},[{W / 720 * 100:.1f},{W / 720 * 100:.1f}]]]); ez(Lv.transform.scale);")
    # 바탕
    u = EV["unfold"]
    a(f"var ib=imp({js(str(WORK / 'aerial.png'))}); var Lb=comp.layers.add(ib); Lb.outPoint={(VID_IN + 0.3) if WITH_DRONE else DUR:.3f};")
    a(f"keys(Lb.transform.scale,[[0,[100,100]],[{u:.3f},[108,108]],[{DUR:.3f},[114,114]]]);")
    a(f"var gb=Lb.Effects.addProperty('ADBE Gaussian Blur 2'); keys(gb.property(1),[[{u:.3f},0],[{u + 0.35:.3f},28]]);")
    a(f"var bc=Lb.Effects.addProperty('ADBE Brightness & Contrast 2'); keys(bc.property(1),[[{u:.3f},0],[{u + 0.35:.3f},-45]]);")
    # 바탕은 첫 프레임부터 보인다(까만 화면 금지 — 제작규칙 1-4)
    # 계획도 3쪽 — 가운데가 먼저 펴지고 양옆이 경첩처럼 젖혀짐(3D)
    third = MAP_W // 3
    for nm, (x0, hinge) in (("C", (third, None)), ("L", (0, "R")), ("R", (2 * third, "L"))):
        p, w = pc[f"map_{nm}"]
        a(f"var i{nm}=imp({js(str(p))}); var M{nm}=comp.layers.add(i{nm}); M{nm}.threeDLayer=true; M{nm}.outPoint={EV['suck'] + SUCK:.3f};")
        if nm == "C":
            a(f"M{nm}.transform.anchorPoint.setValue([{w / 2},{mh / 2}]); M{nm}.transform.position.setValue([{mx0 + x0 + w / 2:.1f},{MAP_CY},0]);")
            a(f"keys(M{nm}.transform.scale,[[{u:.3f},[0,100,100]],[{u + 0.22:.3f},[100,100,100]]]); ez(M{nm}.transform.scale);")
            a(f"keys(M{nm}.transform.opacity,[[{u:.3f},0],[{u + 0.08:.3f},100]]);")
        else:
            ax = w if hinge == "R" else 0              # 가운데 쪽 가장자리가 경첩
            a(f"M{nm}.transform.anchorPoint.setValue([{ax},{mh / 2}]); M{nm}.transform.position.setValue([{mx0 + x0 + ax:.1f},{MAP_CY},0]);")
            r0 = 178 if nm == "L" else -178
            a(f"keys(M{nm}.transform.yRotation,[[{u + 0.16:.3f},{r0}],[{u + 0.55:.3f},-6*{1 if nm == 'L' else -1}],[{u + 0.68:.3f},0]]); ez(M{nm}.transform.yRotation);")
            a(f"keys(M{nm}.transform.opacity,[[{u + 0.16:.3f},0],[{u + 0.2:.3f},100]]);")
    # 부지 테두리(톡 순간 켜지고 깜빡)
    t = EV["tap"]
    a(f"var io=imp({js(str(WORK / 'parcel_ol.png'))}); var Lo=comp.layers.add(io); Lo.transform.position.setValue([{MAP_CX},{MAP_CY}]); Lo.inPoint={t:.3f}; Lo.outPoint={EV['suck'] + SUCK:.3f};")
    a(f"keys(Lo.transform.opacity,[[{t:.3f},0],[{t + 0.06:.3f},100],[{t + 0.25:.3f},30],[{t + 0.4:.3f},100]]);")
    # 파동 2겹
    for k, d in enumerate((0.0, 0.18)):
        a(f"var ir{k}=imp({js(str(WORK / 'ring.png'))}); var R{k}=comp.layers.add(ir{k}); R{k}.transform.position.setValue([{px:.1f},{py:.1f}]); R{k}.inPoint={t + d:.3f}; R{k}.outPoint={t + d + 0.6:.3f};")
        a(f"keys(R{k}.transform.scale,[[{t + d:.3f},[15,15]],[{t + d + 0.55:.3f},[140,140]]]); keys(R{k}.transform.opacity,[[{t + d:.3f},100],[{t + d + 0.55:.3f},0]]);")
    # 캐릭터 — 오른쪽 아래서 들어와 손끝이 부지에 닿음, 톡 순간 살짝 튕김
    cw, chh = pc["char"]
    tx, ty = TIP[0] * CHAR_S, TIP[1] * CHAR_S
    fx, fy = px - tx - 8, py - ty + 10                  # 이미지 왼쪽 위 위치
    cx, cy = fx + cw / 2, fy + chh / 2
    tc = EV["char"]
    a(f"var ic=imp({js(str(WORK / 'char.png'))}); var Lc=comp.layers.add(ic); Lc.inPoint={tc - 0.02:.3f}; Lc.motionBlur=true;")
    a(f"keys(Lc.transform.position,[[{tc - 0.02:.3f},[{cx - 420:.1f},{cy + 300:.1f}]],[{tc + 0.13:.3f},[{cx:.1f},{cy:.1f}]],[{t - 0.04:.3f},[{cx - 10:.1f},{cy + 10:.1f}]],[{t:.3f},[{cx + 6:.1f},{cy - 6:.1f}]],[{t + 0.12:.3f},[{cx:.1f},{cy:.1f}]],"
      f"[{EV['suck']:.3f},[{cx:.1f},{cy:.1f}]],[{EV['suck'] + 0.25:.3f},[{cx - 700:.1f},{cy + 300:.1f}]]]); ez(Lc.transform.position);")
    # 조감도 카드 — 가운데 톡 → 빨려 듦(화면을 채우며 방사 흐림)
    bp, (bw, bh) = pc["bird"]
    tb, ts = EV["bird"], EV["suck"]
    big = round(max(W / (bw - 120), H / (bh - 120)) * 100 * 1.25)
    a(f"var ik=imp({js(str(bp))}); var Lk=comp.layers.add(ik); Lk.inPoint={tb:.3f}; Lk.outPoint={(VID_IN + 0.32) if WITH_DRONE else DUR:.3f}; Lk.transform.position.setValue([{W / 2},{MAP_CY - 60}]); Lk.motionBlur=true;")
    a(f"keys(Lk.transform.scale,[[{tb:.3f},[40,40]],[{tb + 0.14:.3f},[112,112]],[{tb + 0.24:.3f},[100,100]],[{ts:.3f},[100,100]],[{ts + SUCK:.3f},[{big},{big}]]]);")
    a(f"keys(Lk.transform.position,[[{ts:.3f},[{W / 2},{MAP_CY - 60}]],[{ts + SUCK:.3f},[{W / 2 + 160},{H / 2 + 60}]]]);")
    a(f"keys(Lk.transform.opacity,[[{tb:.3f},0],[{tb + 0.06:.3f},100],[{VID_IN + 0.05:.3f},100],[{VID_IN + 0.32:.3f},0]]);") if WITH_DRONE else a(f"keys(Lk.transform.opacity,[[{tb:.3f},0],[{tb + 0.06:.3f},100]]);")
    a(f"var rb=Lk.Effects.addProperty('ADBE Radial Blur'); try{{rb.property('ADBE Radial Blur-0003').setValue(2);}}catch(e){{}} keys(rb.property('ADBE Radial Blur-0001'),[[{ts:.3f},0],[{ts + SUCK:.3f},60]]);")
    # 빨려 들 때 계획도·바탕도 같이 커지며 흐려짐
    for v in ("ML", "MC", "MR", "Lo", "Lb"):
        a(f"keys({v}.transform.opacity,[[{ts:.3f},100],[{ts + SUCK:.3f},0]]);") if v != "Lb" else None
    a(f"var rq=app.project.renderQueue.items.add(comp); var om=rq.outputModule(1); om.applyTemplate({js('고품질')}); om.file=new File({js(str(out_mov))});")
    a("log('ok b4_cine'); })();")
    return "\n".join(L)


def build():
    pc = pieces()
    aep, jf, logf, mov = WORK / "cine.aep", WORK / "cine.jsx", WORK / "log.txt", WORK / "cine.mov"
    for f in (logf, aep):
        if f.exists():
            f.unlink()
    for f in WORK.glob("cine*.mov"):
        f.unlink()
    body = [AE.HEAD.replace("%LOG%", AE.js(str(logf))), "app.newProject();",
            "try{" + jsx(pc, mov) + "}catch(e){ log('ERR '+e.toString()+' line '+e.line); }",
            f"app.project.save(new File({AE.js(str(aep))})); LOG.close(); app.quit();"]
    jf.write_text("\n".join(body), encoding="ascii")
    t0 = time.time()
    subprocess.run([str(AE.AE_DIR / "AfterFX.exe"), "-r", str(jf)], capture_output=True, timeout=900)
    while time.time() - t0 < 900:
        txt = logf.read_text(errors="ignore") if logf.exists() else ""
        if aep.exists() and ("ok" in txt or "ERR" in txt) and not AE._ae_running():
            break
        time.sleep(3)
    txt = logf.read_text(errors="ignore") if logf.exists() else "(로그 없음)"
    print("AE:", txt.strip())
    if "ERR" in txt:
        raise SystemExit(txt)
    subprocess.run([str(AE.AE_DIR / "aerender.exe"), "-project", str(aep)], capture_output=True, timeout=1800)
    rendered = sorted(WORK.glob("cine*.*"), key=lambda p: p.stat().st_mtime)
    rendered = [p for p in rendered if p.suffix.lower() in (".mov", ".avi", ".mp4")]
    return rendered[-1]


def mix(video):
    """효과음을 얹어 mp4 로(소리는 효과음만 — 목소리·배경음은 프리미어에서)."""
    OUT.mkdir(parents=True, exist_ok=True)
    ins, flt = [], []
    for k, (t, f, db) in enumerate(SFX):
        ins += ["-i", str(f)]
        flt.append(f"[{k + 1}:a]volume={db}dB,adelay={int(t * 1000)}|{int(t * 1000)},aformat=channel_layouts=stereo[s{k}]")
    flt.append("".join(f"[s{k}]" for k in range(len(SFX))) + f"amix=inputs={len(SFX)}:normalize=0,apad,atrim=0:{DUR}[a]")
    dst = OUT / ("02_○○단지_지도캐릭터조감도_드론.mp4" if WITH_DRONE else "02_v3_김포항공_지도_캐릭터_조감도_빨려듦까지.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), *ins, "-filter_complex", ";".join(flt),
                    "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-r", "29.97",
                    "-c:a", "aac", "-b:a", "192k", "-t", f"{DUR}", str(dst)], check=True)
    wdir = OUT / ("02_효과음" if WITH_DRONE else "02_v3_효과음")
    wdir.mkdir(exist_ok=True)
    for t, f, db in SFX:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-af", f"volume={db}dB", "-ar", "48000", "-ac", "2",
                        str(wdir / f"{t + T0:06.2f}s_{f.stem.replace(' ', '')}.wav")], check=True)
    return dst


if __name__ == "__main__":
    v = build()
    print("→", mix(v))
