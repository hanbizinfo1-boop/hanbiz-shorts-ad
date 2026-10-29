# -*- coding: utf-8 -*-
r"""자막 스타일 A/B/C + T8(자막-타이포 한 층) 비교 시안 (10-08, 무음).

같은 배경(소재/시안/자막배경/bg_dark·bg_bright.png) · 같은 문장 3줄 · 같은 타이밍(0 / 2 / 4초, 총 7초) 으로
    A 불투명 띠 · B 띠 없음+굵은 외곽선(CAPTION_STYLE 기본, edit_render.cap_img 그대로) · C 얇은 외곽선+옅은 그림자 → PIL 프레임(edit_render.comp/pop 재사용) + ffmpeg
    T8 한 층 → HTML(seek) → tools/html_motion.py --alpha → 배경 위 ffmpeg 합성
를 만들고 2x2 비교판(mp4+PNG)까지 낸다.   python tools/scenes/subtitle_style_compare.py [--skip-t8] [--only-compare]
작업물은 _tmp/subcmp/, 결과는 납품/시안_자막스타일_1008/ (같은 이름 덮어쓰기).
"""
import argparse
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import config as C  # noqa: E402
import edit_plan as P  # noqa: E402
import edit_render as R  # noqa: E402

W, H = 1080, 1920
DT = 1001 / 30000
DUR = 7.0
N = int(round(DUR / DT))
FR = "30000/1001"
WORK = ROOT / "_tmp" / "subcmp"
OUT = ROOT / "납품" / "시안_자막스타일_1008"
BG = {"dark": ROOT / "소재/시안/자막배경/bg_dark.png", "bright": ROOT / "소재/시안/자막배경/bg_bright.png"}
KO = {"dark": "어두운", "bright": "밝은"}
LINES = [("정책자금, 아직 혼자 알아보세요?", ["정책자금"], False), ("조건만 맞으면 길이 생각보다 많습니다", ["길"], False), ("한비즈가 처음부터 같이 봅니다", ["한비즈"], True)]
START = [int(math.ceil(2 * k / DT - 1e-6)) for k in range(3)]   # 0, 60, 120 프레임
NAMES = {"A": "A_불투명띠", "B": "B_굵은외곽선", "C": "C_얇은외곽선그림자", "T8": "T8_한층"}


def cover_bg(path):
    im = Image.open(path).convert("RGB")
    k = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


# ───────────── A/B/C 자막 이미지 ─────────────

def fit(segs, max_w, pad_w, size=66, track=3):
    chars = [(ch, c) for t, c in segs for ch in t]
    while True:
        f = ImageFont.truetype(str(C.FONTS["pretendard_bold"]), size)
        adv = [f.getlength(ch) + (track if ch != " " else 0) for ch, _ in chars]
        width = sum(adv) - track
        if width <= max_w - 2 * pad_w or size <= 40:
            return f, chars, adv, width, size
        size -= 2


A_BAND = {"A": dict(px=40, py=24, radius=16, fill=(17, 17, 17)),
          # A2 = 사장님 10-08 «a스타일인데 테두리색 살짝 현재보다 좀더 회색빛돌게하고 테두리크기를 좀 줄여줘»
          "A2": dict(px=26, py=14, radius=12, fill=(52, 52, 56))}


def img_A(segs, bright, band="A"):
    """불투명 띠 + 외곽선 없는 글자."""
    b = A_BAND[band]
    f, chars, adv, width, size = fit(segs, 960, b["px"])
    px, py = b["px"], b["py"]
    w, h = int(width) + 2 * px, int(size * 1.2) + 2 * py
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=b["radius"], fill=b["fill"] + (255,))
    x = px
    for (ch, c), a in zip(chars, adv):
        if ch != " ":
            d.text((x, py), ch, font=f, fill=((255, 222, 60) if c else (245, 245, 245)) + (255,))
        x += a
    return np.asarray(im).astype(np.float32)


def img_C(segs, bright):
    """1~5px 외곽선(4px) + 옅은 그림자(x0.35, 번지지 않게 blur 2 · 오프셋 1,3). 밝은 배경은 어두운 글자 + 흰 외곽선."""
    f, chars, adv, width, size = fit(segs, 960, 12)
    st, pad = 4, 14
    fill_w = (17, 17, 17) if bright else (245, 245, 245)
    fill_e = (217, 72, 15) if bright else (255, 222, 60)
    edge = (255, 255, 255) if bright else (0, 0, 0)
    im = Image.new("RGBA", (int(width) + 2 * pad, int(size * 1.35) + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for layer in ("stroke", "fill"):
        x = pad
        for (ch, c), a in zip(chars, adv):
            if ch != " ":
                if layer == "stroke":
                    d.text((x, pad), ch, font=f, fill=edge + (255,), stroke_width=st, stroke_fill=edge + (255,))
                else:
                    d.text((x, pad), ch, font=f, fill=(fill_e if c else fill_w) + (255,))
            x += a
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(2)).point(lambda v: int(v * 0.35)))
    out = Image.new("RGBA", (im.width + 6, im.height + 6), (0, 0, 0, 0))
    out.alpha_composite(sh, (1, 3))
    out.alpha_composite(im, (0, 0))
    return np.asarray(out).astype(np.float32)


def img_B(segs, bright):
    return R.cap_img(P.CAPTION_STYLE, segs, True)       # CAPTION_STYLE 기본 그대로(y 1150 · 66px · stroke 9)


def motion(mode, key, j, nfr):
    t = j * DT
    if mode in ("A", "A2", "B"):
        return (R.pop_key(t) if key else R.pop(t)), 1.0
    nin = min(4, max(1, nfr - 1))                        # C: 페이드 + 0.94→1.0, 머무는 동안 1.0→1.02
    if j < nin:
        p = 1 - (1 - (j + 1) / nin) ** 2
        return 0.94 + 0.06 * p, 0.58 + 0.42 * p
    return 1.0 + 0.02 * (j / max(1, nfr - 1)), 1.0


def start_ff(path):
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-framerate", FR, "-i", "-", "-an",
           "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", "-r", FR, str(path)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def render_abc(mode, tone):
    bright = tone == "bright"
    bg = np.asarray(cover_bg(BG[tone]))
    mk = {"A": img_A, "A2": lambda s, b: img_A(s, b, "A2"), "B": img_B, "C": img_C}[mode]
    imgs = []
    for text, emph, key in LINES:
        segs = R.caption_segs({"text": text, "emph": emph, "emph_color": "y"})
        imgs.append(mk(segs, bright))
    path = WORK / f"{mode}_{tone}.mp4"
    ff = start_ff(path)
    for i in range(N):
        k = max(j for j in range(3) if i >= START[j])
        end = START[k + 1] if k < 2 else N
        s, a = motion(mode, LINES[k][2], i - START[k], end - START[k])
        fr = bg.copy()
        R.comp(fr, imgs[k], cy=P.CAPTION_STYLE["y"], s=s, a=a)
        ff.stdin.write(fr.tobytes())
    ff.stdin.close()
    ff.wait()
    return path


# ───────────── T8 (HTML) ─────────────

T8_HTML = r"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><title>T8 자막-타이포 한 층 (__MODE__)</title>
<style>
  html, body { margin:0; padding:0; width:1080px; height:1920px; overflow:hidden; background:transparent; }
  .ln { position:absolute; left:540px; top:0; white-space:pre; text-align:center; word-break:keep-all;
        font-family:"HM NotoSansKR","Noto Sans KR",sans-serif; color:__INK__; text-shadow:__SHADOW__; }
  .row { display:block; line-height:1.22; }
  .row.big { line-height:1.0; }
  .w { display:inline-block; font-weight:600; }
</style></head><body>
<script>
window.W = 1080; window.H = 1920; window.FPS = 29.97; window.DURATION = 7.0;
const INK = '__INK__', ACC = '__ACC__';
window.PALETTE = ['__INK__', '__ACC__', '__EDGE__'];
const F = 1001 / 30000, EASE_IN = 6 * F, RAMP = 8 * F;
const CY = __CY__, GAP = 40, BASE = 80, KEY_FILL = 0.74;
const LINES = [
  { t: 0, rows: [[{s:'정책자금', e:1}, {s:', 아직'}], [{s:'혼자 알아보세요?'}]] },
  { t: 2, rows: [[{s:'조건만 맞으면'}], [{s:'길', e:1}, {s:'이 생각보다 많습니다'}]] },
  { t: 4, key: 1, rows: [[{s:'한비즈', e:1, big:1}, {s:'가'}], [{s:'처음부터 같이 봅니다'}]] },
];
window.EVENTS = LINES.map((l, i) => ({ t: l.t, role: 'text_in', id: 'line' + i }));
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const eo = x => { x = clamp(x); return 1 - Math.pow(1 - x, 3); };   // 감속, 오버슈트 0
const hex = h => [1,3,5].map(i => parseInt(h.substr(i,2),16));
const mix = (a, b, p) => { const A = hex(a), B = hex(b); return 'rgb(' + A.map((v,i) => Math.round(v + (B[i]-v)*p)).join(',') + ')'; };

let built = false; const els = [], hs = [], emph = [];
function build() {
  if (built) return; built = true;
  LINES.forEach((l, li) => {
    const ln = document.createElement('div'); ln.className = 'ln'; ln.dataset.box = 'line' + li;
    emph[li] = [];
    l.rows.forEach(row => {
      const r = document.createElement('div'); r.className = 'row';
      row.forEach(sp => {
        const w = document.createElement('span'); w.className = 'w'; w.textContent = sp.s; w.style.fontSize = BASE + 'px';
        if (sp.big) { w.dataset.big = 1; r.className = 'row big'; }
        if (sp.e) { emph[li].push(w); }
        r.appendChild(w);
      });
      ln.appendChild(r);
    });
    document.body.appendChild(ln); els.push(ln);
  });
  // 핵심 줄: «한비즈» 폭 맞춤(화면 폭의 KEY_FILL) — 100px 로 재서 계산(한글 전각이라 굵기가 바뀌어도 폭 불변)
  els.forEach((ln, li) => {
    const big = ln.querySelector('[data-big]'); if (!big) return;
    emph[li].forEach(w => w.style.fontWeight = 900);
    big.style.fontSize = '100px';
    const row = big.parentElement; const rowW = row.getBoundingClientRect().width, bigW = big.getBoundingClientRect().width;
    const S = Math.round((1080 * KEY_FILL - (rowW - bigW)) / (bigW / 100));
    big.style.fontSize = S + 'px';
  });
  els.forEach((ln, li) => { hs[li] = ln.getBoundingClientRect().height; });
}

async function seek(t) {
  await document.fonts.ready; build();
  const e = LINES.map(l => eo((t - l.t) / EASE_IN));           // T1: 줄 등장 6프레임 감속, 새 줄이 들어오면 블록 재중앙
  let total = -GAP; e.forEach((v, i) => total += v * (hs[i] + GAP));
  let cum = 0;
  els.forEach((ln, i) => {
    const y = CY - total / 2 + cum; cum += e[i] * (hs[i] + GAP);
    ln.style.opacity = e[i]; ln.style.display = e[i] <= 0.001 ? 'none' : 'block';
    ln.style.transform = 'translate(-50%,0) translateY(' + y.toFixed(2) + 'px) scale(' + (0.94 + 0.06 * e[i]).toFixed(4) + ')';
    const p = eo((t - LINES[i].t) / RAMP);                      // T3: 강조어 굵기 300→900 + 색 켜짐 8프레임
    emph[i].forEach(w => { w.style.fontWeight = Math.round(300 + 600 * p); w.style.color = mix(INK, ACC, p); });
  });
  return true;
}
window.seek = seek;
</script></body></html>
"""
T8_MODE = {
    "dark": dict(INK="#ffffff", ACC="#ffd60a", EDGE="#000000", SHADOW="0 3px 16px rgba(0,0,0,.6), 0 1px 3px rgba(0,0,0,.5)", CY=1250),
    "bright": dict(INK="#111111", ACC="#d9480f", EDGE="#ffffff", SHADOW="0 2px 12px rgba(255,255,255,.75)", CY=1250),
}


def write_html():
    outs = {}
    for tone, v in T8_MODE.items():
        s = T8_HTML.replace("__MODE__", tone)
        for k, val in v.items():
            s = s.replace(f"__{k}__", str(val))
        p = ROOT / "tools/scenes/html" / f"hanbiz_t8_caption_{tone}.html"
        p.write_text(s, encoding="utf-8", newline="\n")
        outs[tone] = p
    return outs


def render_t8(tone, html):
    name = f"t8_{tone}"
    r = subprocess.run([sys.executable, str(ROOT / "tools/html_motion.py"), str(html), "--alpha", "--workers", "2", "--out", str(WORK), "--name", name],
                       cwd=str(ROOT), env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if r.returncode != 0:
        raise SystemExit(f"html_motion 실패({tone}) — {WORK / (name + '_점검.txt')} 확인")
    bgp = WORK / f"bg_{tone}.png"
    cover_bg(BG[tone]).save(bgp)
    out = WORK / f"T8_{tone}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", FR, "-i", str(bgp), "-i", str(WORK / f"{name}.mov"),
                    "-filter_complex", "[0:v][1:v]overlay=format=auto,format=yuv420p[o]", "-map", "[o]", "-frames:v", str(N), "-an",
                    "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", "-r", FR, str(out)], check=True)
    return out


# ───────────── 비교판 ─────────────

def label_png():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(str(C.FONTS["pretendard_bold"]), 26)
    for (x, y), t in zip([(0, 0), (540, 0), (0, 960), (540, 960)], ["A 불투명 띠", "B 굵은 외곽선", "C 얇은 외곽선+그림자", "T8 한 층"]):
        w = d.textlength(t, font=f)
        d.rounded_rectangle((x + 10, y + 10, x + 10 + w + 24, y + 10 + 42), radius=8, fill=(0, 0, 0, 215))
        d.text((x + 22, y + 15), t, font=f, fill=(255, 255, 255, 255))
    p = WORK / "labels.png"
    im.save(p)
    return p


def compare(tone, vids):
    lab = label_png()
    out = WORK / f"비교_{KO[tone]}배경.mp4"
    ins = []
    for v in vids:
        ins += ["-i", str(v)]
    fc = "".join(f"[{i}:v]scale=540:960[s{i}];" for i in range(4)) + "[s0][s1][s2][s3]xstack=inputs=4:layout=0_0|540_0|0_960|540_960[g];[g][4:v]overlay=0:0,format=yuv420p[o]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-i", str(lab), "-filter_complex", fc, "-map", "[o]", "-an", "-c:v", "libx264", "-crf", "16", "-r", FR, str(out)], check=True)
    png = WORK / f"비교_{KO[tone]}배경.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "4.5", "-i", str(out), "-frames:v", "1", str(png)], check=True)
    return out, png


def compare_a2():
    """A(원래) vs A2(수정) — 위 어두운 배경 · 아래 밝은 배경, 2×2."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(str(C.FONTS["pretendard_bold"]), 26)
    for (x, y), t in zip([(0, 0), (540, 0), (0, 960), (540, 960)], ["A 원래", "A2 수정(회색·작게)", "A 원래", "A2 수정(회색·작게)"]):
        w = d.textlength(t, font=f)
        d.rounded_rectangle((x + 10, y + 10, x + 10 + w + 24, y + 10 + 42), radius=8, fill=(0, 0, 0, 215))
        d.text((x + 22, y + 15), t, font=f, fill=(255, 255, 255, 255))
    lab = WORK / "labels_a2.png"
    im.save(lab)
    vids = [WORK / f"{m}_{tone}.mp4" for tone in ("dark", "bright") for m in ("A", "A2")]
    out = WORK / "A_수정비교.mp4"
    ins = []
    for v in vids:
        ins += ["-i", str(v)]
    fc = "".join(f"[{i}:v]scale=540:960[s{i}];" for i in range(4)) + "[s0][s1][s2][s3]xstack=inputs=4:layout=0_0|540_0|0_960|540_960[g];[g][4:v]overlay=0:0,format=yuv420p[o]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-i", str(lab), "-filter_complex", fc, "-map", "[o]", "-an", "-c:v", "libx264", "-crf", "16", "-r", FR, str(out)], check=True)
    png = WORK / "A_수정비교.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "4.5", "-i", str(out), "-frames:v", "1", str(png)], check=True)
    for p in (out, png):
        shutil.copyfile(p, OUT / p.name)
    for tone in ("dark", "bright"):
        shutil.copyfile(WORK / f"A2_{tone}.mp4", OUT / f"A2_회색띠_{KO[tone]}.mp4")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-t8", action="store_true")
    ap.add_argument("--only-compare", action="store_true", help="이미 만든 _tmp/subcmp/*.mp4 로 복사·비교판만")
    ap.add_argument("--a2", action="store_true", help="A2(회색·작은 띠) 만 렌더하고 A 와 비교판")
    a = ap.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    if a.a2:
        for tone in ("dark", "bright"):
            render_abc("A2", tone)
        compare_a2()
        return
    htmls = write_html()
    res = {}
    for tone in ("dark", "bright"):
        for m in ("A", "B", "C"):
            res[(m, tone)] = (WORK / f"{m}_{tone}.mp4") if a.only_compare else render_abc(m, tone)
            print("done", m, tone, flush=True)
        if not a.skip_t8:
            res[("T8", tone)] = (WORK / f"T8_{tone}.mp4") if a.only_compare else render_t8(tone, htmls[tone])
    for tone in ("dark", "bright"):
        for m in ("A", "B", "C", "T8"):
            if res.get((m, tone)):
                shutil.copyfile(res[(m, tone)], OUT / f"{NAMES[m]}_{KO[tone]}.mp4")
        if not a.skip_t8:
            mp4, png = compare(tone, [res[(m, tone)] for m in ("A", "B", "C", "T8")])
            shutil.copyfile(mp4, OUT / mp4.name)
            shutil.copyfile(png, OUT / png.name)


if __name__ == "__main__":
    main()
