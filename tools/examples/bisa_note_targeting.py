# -*- coding: utf-8 -*-
# ★ 본보기(원본 경로 상수 그대로) — 실행을 보장하지 않는다. 베껴 쓰지 말고 «이런 식으로 짠다»를 본다.
# 보여 주는 것: 반반(사람이 커지며 왼쪽으로) + 스프링 노트 손글씨(Linear Wipe 270°) + 형광펜·동그라미 — 02 목차에서 통과한 노트 틀
# 원본: D:/영상제작/도구/광고편집/bisa_note_targeting.py (통과/반려 이력은 references/feedback-log.md)
# 모듈 대응: bisa_web_vs_instant → ae_scene · bisa_meta_sfx / bisa_toc_cards.by_name → sfx · rf3_ae·rule_check·lec_xml·design_layers → tools/ 같은 이름.
# 이 폴더에 없는 모듈(bisa_ab_setup 1판, bisa_toc_cards 노트 틀 등)을 import 하는 줄은 원본을 읽어 대응한다.
r"""빡이사DB 본편 12 «자 여기서 하나 더 ~ 알고리즘 되게 정확합니다» (시퀀스 986.085~1012.979, 사장님 컷 경계)
— 화면 반반 + 스프링 노트 손글씨(02 통과 틀). 사장님 10-07 «노트에 정리하는 연출 · 그 화면 반반해서».
본편이라 02 와 달리 시작이 «녹화 화면 + 왼쪽 아래 사람»: 사람 화면이 그대로 커지며 왼쪽 절반으로, 오른쪽에서 노트가 들어온다(끝에 거꾸로).

  python bisa_note_targeting.py [--조각만] [--소리만]
    → 빡이사DB\납품\12_상세타겟팅노트_986.09~.mp4 (녹화·사람 포함 — **V3** 에 얹음: 사장님 V2 사람 PIP 를 덮는다)
       · _효과음.xml(V3 장면 + A2~) · _미리보기.mp4(장면 + 목소리 + 효과음, 사람은 장면 안에 있음)
앞뒤 맥락(기록.md 12)
  앞 979.83 «대주제로 검색해라, 클릭하면서 하나씩 찾아가라 · 꿀팁» · 뒤 1012.43 «굳이 안 하셔도 콘텐츠만 잘 만드시면 … 논타겟팅 하셔도 많이 들어와요»
흐름(시퀀스 초, faster-whisper 단어 시각) — 줄은 그 말이 나올 때 왼쪽부터 써진다(Linear Wipe 270°, 펜 그림 없음 — 02 «연필 흔들려 분산»)
  986.09 «자» 사람 화면이 커지며 왼쪽 절반, 노트가 들어옴 · 987.17 «상세» «상세 타겟팅 할 때»
  988.57 «3개 또는 5개» «3 ~ 5개»(크게) · 993.15 «3개 이상은 해라» «3개 이상은 하고» · 994.73 «5개 이상은 넘지 마라» «5개는 넘지 않기»
  991.23 «넘지 마세요» «3 ~ 5개» 밑줄 두 줄 · 996.23 «이 법칙을» 빨간 동그라미
  999.23 «관심사» «관심사, 꼭 해야?» → 1002.39 «안 하셔도 돼요» «→ 안 해도 돼요»
  1004.57 «광고는 클릭할 사람들을 따라간다» «광고는 클릭할 사람을 따라가고» · 1007.45 «클릭할 사람 찾았으면 문의…» «→ 문의 넣을 사람을 찾아간다»
  1010.81 «알고리즘 되게 정확합니다» 마지막 두 줄에 형광펜 · 1012.43 거꾸로 닫힘 → 1012.979
자막 자리(아래 가운데 y ≥ 900)는 노트 줄을 쓰지 않는다(맨 아래 줄 기준선 820).
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # tools/
# (원본의 강의편집 경로 삽입은 tools/ 로 통합됨)
import rf3_ae as AE  # noqa: E402
import rule_check  # noqa: E402
import lec_xml  # noqa: E402
import sfx as SFX  # noqa: E402  (본보기: 원본 bisa_meta_sfx → sfx)
import bisa_toc_cards as N  # noqa: E402  (02 노트: 글꼴·색·종이·형광펜·동그라미)
import ae_scene as M  # noqa: E402  (본보기: 원본 bisa_web_vs_instant 의 틀 → ae_scene)  (렌더 틀·목소리)
from sfx import by_name  # noqa: E402  (본보기: 원본 bisa_toc_cards.by_name → sfx.by_name)

M.T0, M.T1 = 986.085, 1012.979
M.DUR = M.T1 - M.T0
M.SEGS = [(986.085, 987.136, 1707.322, 1709.124), (987.136, 988.638, 1714.263, 1716.064), (988.638, 990.623, 1715.898, 1717.699),
          (990.623, 992.074, 1718.133, 1719.935), (992.074, 992.892, 1720.085, 1721.887), (992.892, 994.744, 1721.019, 1722.821),
          (994.744, 998.297, 1722.988, 1724.79), (998.297, 998.848, 1727.459, 1729.261), (998.848, 1002.385, 1728.226, 1730.028),
          (1002.385, 1003.219, 1731.93, 1733.732), (1003.219, 1004.353, 1732.948, 1734.75), (1004.353, 1006.322, 1734.216, 1736.018),
          (1006.322, 1010.843, 1736.268, 1738.07), (1010.843, 1011.477, 1741.356, 1743.141), (1011.477, 1012.979, 1742.307, 1744.092)]
M.NAME = "12_상세타겟팅노트"
M.SFX_DIR = Path(r"D:\영상제작\빡이사DB\소재\효과음12")
M.WORK = N.WORK = Path(r"D:\영상제작\_tmp\빡이사\ae12")
W, H, FPS = M.W, M.H, M.FPS
T0, T1 = M.T0, M.T1
WORK = M.WORK
NAVY, BLUE, PENCIL, RED = N.NAVY, N.BLUE, N.PENCIL, N.RED
PX, X_TEXT = N.PX, N.X_TEXT
T_SPLIT, T_BACK = 986.09, 1012.43
PIP_POS, PIP_SCALE = (0.0734375 * W, 0.83703703 * H), 30           # 사장님 V2 사람(4K 30%)
HALF_POS, HALF_SCALE = (480, 540), 50
# (이름, 글, 크기, 색, 화면 x, 기준선 y, 쓰기 시작, 쓰기 끝)
ROWS = [("h", "상세 타겟팅 할 때", 60, NAVY, X_TEXT, 220, 987.17, 988.10),
        ("r1", "3 ~ 5개", 104, NAVY, X_TEXT, 370, 988.57, 990.70),
        ("r2", "3개 이상은 하고", 54, BLUE, X_TEXT, 460, 993.15, 993.95),
        ("r3", "5개는 넘지 않기", 54, BLUE, X_TEXT, 550, 994.73, 995.95),
        ("r4", "관심사, 꼭 해야?", 46, PENCIL, X_TEXT, 640, 999.23, 1001.10),
        ("r5", "안 해도 돼요!", 54, BLUE, X_TEXT + 360, 640, 1002.39, 1002.95),
        ("r6", "광고는 클릭할 사람을 따라가고", 54, NAVY, X_TEXT, 730, 1004.57, 1005.70),
        ("r7", "문의 넣을 사람까지 찾아간다", 54, NAVY, X_TEXT, 820, 1007.45, 1009.50)]
HL = [("hl1", "r6", 1010.81, 1011.15), ("hl2", "r7", 1011.10, 1011.45)]
T_CIRCLE = (996.23, 996.70)
T_UNDER = (991.23, 991.80)                                          # «넘지 마세요» 밑줄
POS = N.POS
PIP = (0, 580, 720, 1080)
CAPTION = (480, 900, 1440, 1080)


def circle_png():
    x0, y0, x1, y1 = POS["r1"]
    m = 26
    w, h = int(x1 - x0 + 2 * m), int(y1 - y0 + 2 * m)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.arc((4, 6, w - 4, h - 4), 200, 560, fill=RED + (255,), width=7)
    d.arc((8, 2, w - 2, h - 8), 190, 250, fill=RED + (255,), width=6)
    im.save(WORK / "circle.png")
    POS["circle"] = (x0 - m, y0 - m, x0 - m + w, y0 - m + h)


def underline_png():
    """«3 ~ 5개» 밑에 손으로 긋는 두 줄(«넘지 마세요» 991.23)."""
    x0, y0, x1, y1 = POS["r1"]
    w = int(x1 - x0 + 20)
    im = Image.new("RGBA", (w, 34), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line([(4, 10), (w * 0.5, 7), (w - 6, 11)], fill=NAVY + (255,), width=5, joint="curve")
    d.line([(14, 26), (w * 0.55, 22), (w - 16, 27)], fill=NAVY + (255,), width=4, joint="curve")
    im.save(WORK / "under.png")
    POS["under"] = (x0 - 10, y1 - 2, x0 - 10 + w, y1 + 32)


def panel_png():
    pn = Image.new("RGBA", (960 + 60, H), (0, 0, 0, 0))
    s3 = Image.new("RGBA", pn.size, (0, 0, 0, 0))
    ImageDraw.Draw(s3).rectangle((60, 0, 60 + 960, H), fill=(0, 0, 0, 110))
    pn.alpha_composite(s3.filter(ImageFilter.GaussianBlur(22)))
    body = Image.new("RGBA", (960, H), N.PAPER + (255,))
    d = ImageDraw.Draw(body)
    for y in range(N.RULE_Y0, 880, N.RULE_GAP):                  # 자막 자리 위까지만 줄
        d.line((70, y, 940, y), fill=N.RULE + (255,), width=2)
    d.line((X_TEXT - 960 - 20, 0, X_TEXT - 960 - 20, H), fill=N.MARGIN + (255,), width=2)
    for y in range(50, H - 20, 64):
        d.ellipse((24, y - 9, 42, y + 9), fill=(205, 205, 210, 255))
        d.rounded_rectangle((-6, y - 13, 36, y + 13), 12, outline=(140, 146, 158, 255), width=5)
    pn.alpha_composite(body, (60, 0))
    pn.save(WORK / "panel.png")


def check_layout():
    names = [r[0] for r in ROWS]
    bad = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            A, B = POS[a], POS[b]
            if A[0] < B[2] and B[0] < A[2] and A[1] < B[3] and B[1] < A[3]:
                bad.append(f"{a} {A} ↔ {b} {B}")
    for n in names + [h[0] for h in HL] + ["circle"]:
        x0, y0, x1, y1 = POS[n]
        if x0 < 1000 or x1 > W - 20 or y0 < 20 or y1 > H - 20:
            bad.append(f"{n} {POS[n]} 종이 밖")
        if x0 < CAPTION[2] and y1 > CAPTION[1]:
            bad.append(f"{n} {POS[n]} ↔ 자막")
    if bad:
        raise SystemExit("레이아웃 겹침:\n  " + "\n  ".join(bad))
    print("겹침 없음")


def pieces():
    WORK.mkdir(parents=True, exist_ok=True)
    panel_png()
    for name, text, size, color, x, base, *_ in ROWS:
        N.text_png(name, text, size, color, x, base)
    for name, row, *_ in HL:
        N.marker_png(name, POS[row])
    circle_png()
    underline_png()
    check_layout()


def jsx(out_mov):
    js = AE.js
    s = lambda t: round(t - T0, 4)                         # noqa: E731
    L = [f"(function(){{ var comp=app.project.items.addComp('bisa12',{W},{H},1,{M.DUR:.3f},{FPS});"]
    a = L.append
    # 녹화 화면(처음·끝에 보임)
    a(f"var iv=imp({js(str(M.REC))});")
    for i, (ta, tb, rs, _) in enumerate(M.SEGS):
        a(f"var R{i}=comp.layers.add(iv); R{i}.startTime={s(ta) - rs:.4f}; R{i}.inPoint={s(ta):.4f}; R{i}.outPoint={s(tb):.4f};")
    # 노트(오른쪽에서 들어옴)
    a(f"var PN=comp.layers.add(imp({js(str(WORK / 'panel.png'))})); PN.transform.anchorPoint.setValue([0,540]);")
    a(f"keys(PN.transform.position,[[{s(T_SPLIT)},[{W},540]],[{s(T_SPLIT) + 0.5:.3f},[{PX},540]],[{s(T_BACK)},[{PX},540]],[{s(T_BACK) + 0.4:.3f},[{W + 40},540]]]); ez(PN.transform.position);")
    # 사람(사장님 컷 조각대로): 왼쪽 아래 30% → 왼쪽 절반 50% → 끝에 거꾸로
    a(f"var cv=imp({js(str(M.CAM))});")
    for i, (ta, tb, _, cs) in enumerate(M.SEGS):
        v = f"C{i}"
        a(f"var {v}=comp.layers.add(cv); {v}.startTime={s(ta) - cs:.4f}; {v}.inPoint={s(ta):.4f}; {v}.outPoint={s(tb):.4f}; {v}.audioEnabled=false;")
        a(f"keys({v}.transform.position,[[{s(T_SPLIT)},[{PIP_POS[0]:.1f},{PIP_POS[1]:.1f}]],[{s(T_SPLIT) + 0.5:.3f},[{HALF_POS[0]},{HALF_POS[1]}]],[{s(T_BACK)},[{HALF_POS[0]},{HALF_POS[1]}]],[{s(T_BACK) + 0.4:.3f},[{PIP_POS[0]:.1f},{PIP_POS[1]:.1f}]]]); ez({v}.transform.position);")
        a(f"keys({v}.transform.scale,[[{s(T_SPLIT)},[{PIP_SCALE},{PIP_SCALE}]],[{s(T_SPLIT) + 0.5:.3f},[{HALF_SCALE},{HALF_SCALE}]],[{s(T_BACK)},[{HALF_SCALE},{HALF_SCALE}]],[{s(T_BACK) + 0.4:.3f},[{PIP_SCALE},{PIP_SCALE}]]]); ez({v}.transform.scale);")
    # 노트는 사람 위(사람 오른쪽 절반이 종이 밑으로) — 노트를 맨 위로
    a("PN.moveToBeginning();")

    def wipe(var, png, box, t0, t1, radial=False, blend=None):
        x0, y0, x1, y1 = box
        a(f"var {var}=comp.layers.add(imp({js(str(WORK / png))})); {var}.parent=PN; {var}.transform.position.setValue([{(x0 + x1) / 2 - PX:.1f},{(y0 + y1) / 2:.1f}]); {var}.moveToBeginning();")
        if blend:
            a(f"{var}.blendingMode=BlendingMode.{blend};")
        if radial:
            a(f"var e{var}={var}.Effects.addProperty('ADBE Radial Wipe'); e{var}.property(2).setValue(200); keys(e{var}.property(1),[[{s(t0)},100],[{s(t1)},0]]);")
        else:
            a(f"var e{var}={var}.Effects.addProperty('ADBE Linear Wipe'); e{var}.property(2).setValue(270); e{var}.property(3).setValue(12); keys(e{var}.property(1),[[{s(t0)},100],[{s(t1)},0]]);")

    for name, row, t0, t1 in HL:
        wipe(name.upper(), f"{name}.png", POS[name], t0, t1, blend="MULTIPLY")
    for name, _, _, _, _, _, t0, t1 in ROWS:
        wipe(name.upper(), f"{name}.png", POS[name], t0, t1)
    wipe("UND", "under.png", POS["under"], *T_UNDER)
    wipe("CIR", "circle.png", POS["circle"], *T_CIRCLE, radial=True)
    # 쌓인 순서(아래→위): 녹화 · 사람 · 종이 · 형광펜 · 글 · 동그라미
    a(f"var rq=app.project.renderQueue.items.add(comp); var om=rq.outputModule(1); om.applyTemplate({js('고품질')}); om.file=new File({js(str(out_mov))});")
    a("log('ok bisa12'); })();")
    return "\n".join(L)


# 효과음 — 펜은 쓰는 동안만(음수 길이 = 딱 그 길이), 샤프·연필 번갈아(02 통과). 크기는 FILE_DB 우선.
def pen(k, t0, t1):
    return ("SEL_シャーペンで字を書く.mp3" if k % 2 == 0 else "24. 연필.mp3", -(t1 - t0), 4 if k % 2 == 0 else 3, "onset")


SND_FIX = {"split": ("휙２.mp3", 0.6, 4, "peak"), "circle": ("14. 짜잔.wav", 1.0, 5, "onset"),
           "gauge": ("SEL_ゲージ回復1.mp3", 0.6, 12, "onset"), "back": ("휙1.mp3", 0.7, 8, "peak")}
EVENTS = [(T_SPLIT + 0.25, "split")]
for k, (name, _, _, _, _, _, t0, t1) in enumerate(ROWS):
    SND_FIX[f"pen_{name}"] = pen(k, t0, t1)
    EVENTS.append((t0, f"pen_{name}"))
SND_FIX["under"] = ("SEL_油性マーカーで字を書く.mp3", -(T_UNDER[1] - T_UNDER[0]), 3, "onset")   # 밑줄 = 마커(연필·샤프와 안 겹치게)
EVENTS += [(T_UNDER[0], "under"), (T_CIRCLE[0], "circle"), (HL[0][2], "gauge"), (T_BACK + 0.2, "back")]
EVENTS.sort()


def sfx(scene):
    snd = {k: SFX.role(by_name(f), mx, rel, al) for k, (f, mx, rel, al) in SND_FIX.items()}
    SFX.SND.clear()
    SFX.SND.update(snd)
    v = M.voice()
    f = SFX.rms_frames(v)
    ref = float(np.median(f[f > f.max() - 25]))
    M.SFX_DIR.mkdir(parents=True, exist_ok=True)
    cache, placed, mix = {}, [], np.zeros_like(v)
    for k, (t, name) in enumerate(EVENTS):
        if name not in cache:
            cache[name] = SFX.prep(name, ref)
        x, peak_at = cache[name]
        start = t - (peak_at if snd[name][5] == "peak" else 0.0)
        fp = M.SFX_DIR / f"{k + 1:02d}_{name}.wav"
        SFX.write_wav(fp, x)
        placed.append((round(start, 3), fp, name))
        i = int((start - T0) * SFX.SR)
        seg = x[: len(mix) - i]
        mix[i: i + len(seg)] += seg
        print(f"  {start:7.2f}s  {name:7s} {snd[name][0].name}  {snd[name][4]:+d}dB  {len(x) / SFX.SR:.2f}s")
    bad = [it for it in rule_check.check_sfx([(t - T0, snd[n][0], len(cache[n][0]) / SFX.SR) for t, _, n in placed], T1 - T0) if it[0] == "ERROR"]
    for it in bad:
        print(*it)
    if bad:
        sys.exit(1)
    tmp = M.SFX_DIR / "_미리듣기소리.wav"
    both = v * 10 ** (7 / 20) + mix * 10 ** (7 / 20)
    both *= min(1.0, 0.8 / (np.abs(both).max() + 1e-9))
    SFX.write_wav(tmp, both)
    pre = M.OUT / f"{M.NAME}_미리보기.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(scene), "-i", str(tmp), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "alimiter=limit=0.84:level=false", "-c:a", "aac", "-b:a", "256k", "-shortest", str(pre)], check=True)
    tmp.unlink()
    lec_xml.V_TRACK, lec_xml.A_TRACK = 3, 2                 # 장면 = 녹화·사람 다 들어 있음 → V3(사장님 V2 사람 PIP 를 덮음)
    print(lec_xml.write(M.OUT / f"{M.NAME}_효과음.xml", f"빡이사DB_{M.NAME}", scene, M.DUR, T0,
                        [(t, f) for t, f, _ in placed], 59.94, tag="bs12"))
    return pre


if __name__ == "__main__":
    M.pieces = pieces
    M.jsx = jsx
    WORK.mkdir(parents=True, exist_ok=True)
    scene = M.OUT / f"{M.NAME}_{T0:.2f}~.mp4"
    if "--조각만" in sys.argv:
        pieces()
        sys.exit()
    if "--소리만" not in sys.argv:
        scene = M.build()
    print(scene)
    print(sfx(scene))
