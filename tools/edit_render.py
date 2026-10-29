# -*- coding: utf-8 -*-
r"""배치표(JSON) → 미리보기 mp4 + _점검.txt  (한 편 조립기, workflow.md P4·P5)

[이식본 — 원본 D:/영상제작/도구/광고편집/ 의 sg_render.py(09-29, 사장님 통과에 가장 가까운 판) 에서 떼어 온 것:
   warp/retime(배속 시간 변환) → 배치표 시각 ÷ speed 로 일반화 · Reader(ffmpeg 로 배속·리프레임까지) · cover/comp · pop(130→100, 0.216초)
   tr_fx(컷 앞뒤에 걸치는 전환, mode="straddle") · cap_img(테두리 먼저, 글자 위) · loud_db(가장 큰 0.4초 RMS) · lufs · loudnorm 마감
 + rf5_render.py 의 apply_tr / TR_CYCLE 7종(mode="enter") · sub_anim.py 의 페이드+0.94→1.0, 머무는 동안 1.0→1.02(anim="fade")
 + ad_render.py 흰 플래시(다음 컷 첫 FLASH_FRAMES 프레임 흰색).
 바뀐 것: PKG/PAL/trig/CAPS 같은 건 전용 값은 전부 배치표로. 정지 그림의 느린 줌(1.00→1.06)은 뺐다 — 배경은 정지(workflow P4)이고 XML 이 못 담는다.
 효과음은 sfx.py(prep · FILE_DB) 를 쓰고 sg 의 PAL 절대경로는 버렸다. 그림을 프레임 사이에서 섞던 getf 도 뺐다(ffmpeg fps 필터가 맞춰 준다).]

    python edit_render.py 배치표.json [--out 미리보기.mp4] [--무시]

순서: 배치표 검증 → rule_check.check_plan(렌더 전) → 화면 → 소리 → rule_check.check_sfx(소리 섞은 뒤) → loudnorm 마감 → _점검.txt
ERROR 가 있으면 멈춘다. --무시 로만 통과하고, 그때 위반 목록을 _점검.txt 에 따로 적는다.
"""
import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import config as C  # noqa: E402
import edit_plan as P  # noqa: E402
import rule_check as RC  # noqa: E402
import sfx as SFX  # noqa: E402

SR = SFX.SR
LOUD_TP = -1.5        # workflow P5: 트루피크 −1.5dB 이하
LOUD_LRA = 9          # sg_render
STRADDLE_HALF = 0.5   # 컷 앞뒤 각각 dur 의 절반(sg_render HALF = TR_DUR/2)


def fr_str(plan):
    f = plan["_fps"]
    return f"{f.numerator}/{f.denominator}" if f.denominator != 1 else str(f.numerator)


# ─────────────────────────── 화면: 리프레임 · 읽기 ───────────────────────────

def geom(sw, sh, W, H, k_total, pos):
    """원본 sw×sh 를 배율 k_total(원본 크기 기준)로 키운 뒤 W×H 로 자르는 자리 → (cw, ch, x, y).
    pos = 화면 안에서 그림을 옮기는 px. edit_xml 의 Basic Motion scale/center 도 같은 식이다."""
    cw, ch = max(W, int(round(sw * k_total))), max(H, int(round(sh * k_total)))
    x = int(round((cw - W) / 2 - pos[0]))
    y = int(round((ch - H) / 2 - pos[1]))
    return cw, ch, min(max(0, x), cw - W), min(max(0, y), ch - H)


def k_cover(sw, sh, W, H, scale):
    return max(W / sw, H / sh) * scale


def quant_in(cut, fps):
    """in 을 «시퀀스» 프레임 격자에 맞춘다 — edit_xml 이 in/out 을 시퀀스 레이트 프레임 수로 적기 때문이다(ad_xml 에서 프리미어가
    원본 레이트로 적은 in 을 잘못 읽어 클립이 비었던 교훈). 이렇게 해야 미리보기와 XML 이 같은 자리를 읽는다."""
    return round(cut["in"] * fps) / fps


class Reader:
    """영상 컷 하나를 ffmpeg 로 읽는다 — 배속(setpts)·시퀀스 fps 맞춤·리프레임(scale+crop)까지 필터에서. next() = 다음 프레임."""

    def __init__(self, plan, cut, n):
        W, H = plan["seq"]["w"], plan["seq"]["h"]
        src = P.abs_path(plan, cut["src"])
        info = P.probe(src)
        cw, ch, x, y = geom(info["w"], info["h"], W, H, k_cover(info["w"], info["h"], W, H, cut["scale"]), cut["pos"])
        vf = (f"setpts=(PTS-STARTPTS)/{plan['speed']},fps={fr_str(plan)},scale={cw}:{ch}:flags=bicubic,"
              f"crop={W}:{H}:{x}:{y},format=rgb24")
        self.W, self.H = W, H
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{quant_in(cut, float(plan['_fps'])):.6f}", "-t", f"{(cut['end'] - cut['start']) + 1.0:.4f}",
                                   "-i", str(src), "-an", "-vf", vf, "-frames:v", str(n + 2), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)    # close() 가 읽던 도중 죽이면 ffmpeg 가 Broken pipe 를 떠든다
        self.f = None
        self.short = 0           # 원본이 모자라 마지막 프레임을 되풀이한 횟수

    def next(self):
        b = self.p.stdout.read(self.W * self.H * 3)
        if len(b) == self.W * self.H * 3:
            self.f = np.frombuffer(b, np.uint8).reshape(self.H, self.W, 3)
        else:
            self.short += 1
        return self.f

    def close(self):
        self.p.stdout.close()
        self.p.kill()


def still_frame(plan, cut):
    """그림 컷 — 리프레임 한 장(정지)."""
    W, H = plan["seq"]["w"], plan["seq"]["h"]
    im = Image.open(P.abs_path(plan, cut["src"])).convert("RGB")
    cw, ch, x, y = geom(im.width, im.height, W, H, k_cover(im.width, im.height, W, H, cut["scale"]), cut["pos"])
    return np.asarray(im.resize((cw, ch), Image.LANCZOS).crop((x, y, x + W, y + H)))


class MovRGBA:
    """투명 .mov 를 앞으로만 읽는다 → 전체 화면 RGBA float. get(n) = n 번째 프레임(끝을 넘으면 마지막)."""

    def __init__(self, path, W, H, seq_fps=None):
        """W,H = 파일 자신의 크기. seq_fps 를 주면 path 를 PNG 시퀀스 패턴("f_%05d.png")으로 읽는다."""
        self.W, self.H = W, H
        src = ["-framerate", str(seq_fps), "-i", str(path)] if seq_fps else ["-i", str(path)]
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", *src, "-f", "rawvideo", "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.n, self.f = -1, np.zeros((H, W, 4), np.float32)

    def get(self, n):
        while self.n < n:
            b = self.p.stdout.read(self.W * self.H * 4)
            if len(b) < self.W * self.H * 4:
                break
            self.f = np.frombuffer(b, np.uint8).reshape(self.H, self.W, 4).astype(np.float32)
            self.n += 1
        return self.f

    def close(self):
        self.p.stdout.close()
        self.p.kill()


def comp(frame, arr, cx=None, cy=None, s=1.0, a=1.0, dx=0, dy=0):
    """RGBA(float, 비-premultiplied) 를 가운데 (cx,cy) 기준 배율 s, 이동 dx·dy, 불투명도 a 로 얹는다. frame 을 제자리에서 바꾼다."""
    H, W = frame.shape[:2]
    cx = W / 2 if cx is None else cx
    cy = H / 2 if cy is None else cy
    if s != 1.0:
        im = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")
        im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.BILINEAR)
        arr = np.asarray(im).astype(np.float32)
    h, w = arr.shape[:2]
    x0, y0 = int(round(cx - w / 2 + dx)), int(round(cy - h / 2 + dy))
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if X1 <= X0 or Y1 <= Y0:
        return
    src = arr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    al = src[..., 3:4] / 255.0 * a
    dst = frame[Y0:Y1, X0:X1].astype(np.float32)
    frame[Y0:Y1, X0:X1] = (dst * (1 - al) + src[..., :3] * al).astype(np.uint8)


def pop(t, d=0.216, k0=1.3):
    """사장님 텍스트 그래픽 키프레임 — k0 → 100% (기본 130→100, 0.216초). sg_render.pop."""
    if t >= d:
        return 1.0
    u = t / d
    return k0 - (k0 - 1) * (1 - (1 - u) ** 3)


def pop_key(t):
    """핵심 줄 — 1 → 120 → 100% (0.2 + 0.05초). editing-premiere.md 5장."""
    if t < 0.2:
        u = t / 0.2
        return 1.0 + 0.2 * (1 - (1 - u) ** 3)
    if t < 0.25:
        return 1.2 - 0.2 * ((t - 0.2) / 0.05)
    return 1.0


# ─────────────────────────── 전환 · 플래시 ───────────────────────────

def _zoom(img, k, W, H):
    im = Image.fromarray(img)
    w, h = int(W * k), int(H * k)
    im = im.resize((w, h), Image.BILINEAR)
    x, y = (w - W) // 2, (h - H) // 2
    return np.asarray(im.crop((x, y, x + W, y + H))).astype(np.float32)


def _shift(img, dx, W):
    out = np.zeros_like(img)
    dx = int(dx)
    if dx >= 0:
        out[:, dx:] = img[:, :W - dx] if dx < W else 0
    else:
        out[:, :W + dx] = img[:, -dx:]
    return out


def apply_tr(kind, frame, prev, u):
    """[rf5_render.apply_tr 이식] 들어오는 컷에 건다. u: 0→1(전환 진행). prev = 앞 컷 마지막 프레임. Film Impact 계열 흉내 7종."""
    H, W = frame.shape[:2]
    e = 1 - (1 - u) ** 3
    f = frame.astype(np.float32)
    if kind in ("zoomblur", "crosszoom"):
        k0 = 1.35 if kind == "crosszoom" else 1.22
        k = k0 - (k0 - 1) * e
        amt = (1 - e) * 0.18
        acc = sum(_zoom(frame, k * (1 + amt * i / 4), W, H) for i in range(5)) / 5
        if kind == "crosszoom" and u < 0.3:
            acc = acc + 140 * (1 - u / 0.3)
        return np.clip(acc, 0, 255).astype(np.uint8)
    if kind == "dirblur":
        k = 1.30
        big = Image.fromarray(frame).resize((int(W * k), int(H * k)), Image.BILINEAR)
        ox = int((big.width - W) * (1 - e))
        oy = (big.height - H) // 2
        g = np.asarray(big.crop((ox, oy, ox + W, oy + H))).copy()
        r = int(40 * (1 - u))
        if r > 1:
            g = np.asarray(Image.fromarray(g).filter(ImageFilter.BoxBlur(r))).copy()
        return g
    if kind == "push" and prev is not None:
        dx = W * (1 - e)
        return np.where(np.arange(W)[None, :, None] >= dx, _shift(frame, dx, W), _shift(prev, dx - W, W)).astype(np.uint8)
    if kind in ("rays", "flare"):
        a = 1 - e
        glow = np.asarray(Image.fromarray(frame).resize((W // 8, H // 8)).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BICUBIC)).astype(np.float32)
        out = f + glow * 1.4 * a
        if kind == "flare":
            xx = np.linspace(0, 1, W)[None, :, None]
            band = np.exp(-((xx - (0.1 + 0.8 * u)) ** 2) / 0.02) * np.array([255, 190, 120], np.float32)[None, None, :]
            out = out + band * a * 0.9
        return np.clip(out, 0, 255).astype(np.uint8)
    if kind == "lensblur":
        r = 22 * (1 - e)
        g = Image.fromarray(frame)
        if r > 0.8:
            g = g.filter(ImageFilter.GaussianBlur(r))
        return np.clip(_zoom(np.asarray(g), 1.06 - 0.06 * e, W, H), 0, 255).astype(np.uint8)
    return frame


def _hblur(a, r):
    r = int(r)
    if r < 2:
        return a
    c = np.cumsum(np.pad(a.astype(np.float32), ((0, 0), (r + 1, r), (0, 0)), mode="edge"), axis=1)
    return (c[:, 2 * r + 1:] - c[:, :-2 * r - 1]) / (2 * r + 1)


def tr_fx(kind, frame, a):
    """[sg_render.tr_fx 이식] 컷 앞뒤에 걸치는 전환(mode="straddle"). a = 0(효과 없음)~1(컷 순간). 가운데 기준 변형만 — 흔들림·이동 없음."""
    if a < 0.02:
        return frame
    H, W = frame.shape[:2]
    f = frame.astype(np.float32)
    if kind == "zoomblur":
        out = sum(_zoom(frame, 1 + 0.10 * a * i / 5, W, H) for i in range(6)) / 6
    elif kind == "dirblur":
        out = _hblur(f, 70 * a)
    elif kind == "lensblur":
        out = np.asarray(Image.fromarray(frame).filter(ImageFilter.GaussianBlur(24 * a))).astype(np.float32)
    elif kind == "flare":
        glow = np.asarray(Image.fromarray(frame).resize((W // 8, H // 8)).filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BICUBIC)).astype(np.float32)
        out = np.asarray(Image.fromarray(frame).filter(ImageFilter.GaussianBlur(10 * a))).astype(np.float32) * (1 - 0.3 * a) + glow * 0.9 * a
    elif kind == "spin":
        out = sum(_zoom(frame, 1.04 * a + 1 + 0.06 * a * i / 4, W, H) for i in range(5)) / 5 + 50 * a
    else:
        out = f
    return np.clip(out, 0, 255).astype(np.uint8)


def tr_window(plan, k, jr):
    """k 번 컷으로 들어오는 전환이 건드리는 출력 프레임 범위 [a, b) — edit_xml 이 마커로 쓰고 verify 가 건너뛴다."""
    t = plan["cuts"][k].get("tr")
    if not t:
        return None
    f = float(plan["_fps"])
    n = int(math.ceil(t["dur"] * f))
    if t["mode"] == "straddle":
        h = int(math.ceil(t["dur"] * STRADDLE_HALF * f))
        return jr[k][0] - h, jr[k][0] + h
    return jr[k][0], jr[k][0] + n


# ─────────────────────────── 자막 ───────────────────────────

_FONT_CACHE = {}


def caption_segs(cp):
    """[(글, 색키 또는 None)] — 강조어는 text 안에서 앞에서부터 찾는다."""
    text = cp["text"]
    spans = []
    for w in cp["emph"]:
        i = text.find(w)
        if i >= 0 and all(i >= e or i + len(w) <= s for s, e in spans):
            spans.append((i, i + len(w)))
    spans.sort()
    out, pos = [], 0
    for s, e in spans:
        if s > pos:
            out.append((text[pos:s], None))
        out.append((text[s:e], cp["emph_color"]))
        pos = e
    if pos < len(text):
        out.append((text[pos:], None))
    return out


def cap_img(style, segs, on):
    """[sg_render.cap_img 이식] 자막 한 줄 → RGBA float. mode "band"(기본, A2) = 둥근 불투명 띠 + 글자, "outline" = 아래 설명.
    outline: 테두리를 먼저 모든 글자에 그리고 그 위에 글자색을 칠해
    겹쳐도 글자를 먹지 않게, 자간 +track px. on = 강조색을 켤지(꺼져 있으면 흰색)."""
    key = (str(C.FONTS["pretendard_bold"]),)
    size = style["size"]
    band = style.get("mode", "band") == "band"
    stroke, track, max_w = (0 if band else style["stroke"]), style["track"], style["max_w"]
    col = {k: tuple(v) for k, v in style["colors"].items()}
    if band:        # 10-08 A2: 불투명 둥근 띠 + 외곽선·그림자 없는 글자 (밝은 배경에서도 그대로 — 띠가 가독성을 맡는다)
        px, py = style["pad_x"], style["pad_y"]
        while True:
            f = _FONT_CACHE.get(key + (size,)) or _FONT_CACHE.setdefault(key + (size,), ImageFont.truetype(key[0], size))
            chars = [(ch, c) for t, c in segs for ch in t]
            adv = [f.getlength(ch) + (track if ch != " " else 0) for ch, _ in chars]
            width = sum(adv) - track
            if width <= max_w - 2 * px or size <= 40:
                break
            size -= 2
        w, h = int(width) + 2 * px, int(size * 1.2) + 2 * py
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=style["radius"], fill=tuple(style["band_fill"]) + (255,))
        x = px
        for (ch, c), a_ in zip(chars, adv):
            if ch != " ":
                d.text((x, py), ch, font=f, fill=(col[c] if (c and on) else col["white"]) + (255,))
            x += a_
        return np.asarray(img).astype(np.float32)
    while True:
        f = _FONT_CACHE.get(key + (size,)) or _FONT_CACHE.setdefault(key + (size,), ImageFont.truetype(key[0], size))
        chars = [(ch, i, c) for i, (t, c) in enumerate(segs) for ch in t]
        adv = [f.getlength(ch) + (track if ch != " " else 0) for ch, _, _ in chars]
        width = sum(adv) - track
        if width <= max_w - 2 * stroke or size <= 40:
            break
        size -= 2
    pad = stroke + 8
    img = Image.new("RGBA", (int(width) + 2 * pad, int(size * 1.35) + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for layer in ("stroke", "fill"):
        x = pad
        for (ch, i, c), a_ in zip(chars, adv):
            if ch != " ":
                if layer == "stroke":
                    d.text((x, pad), ch, font=f, fill=(0, 0, 0, 255), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
                else:
                    d.text((x, pad), ch, font=f, fill=(col[c] if (c and on) else col["white"]) + (255,))
            x += a_
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.putalpha(img.getchannel("A").filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.5)))
    out = Image.new("RGBA", (img.width + 8, img.height + 10), (0, 0, 0, 0))
    out.alpha_composite(sh, (6, 8))
    out.alpha_composite(img, (0, 0))
    return np.asarray(out).astype(np.float32)


class Captions:
    """줄마다 이미지(강조 꺼짐/켜짐)를 캐시하고 프레임 i 의 (이미지, 배율, 불투명도) 를 준다."""

    def __init__(self, plan):
        self.plan, self.cache = plan, {}

    def image(self, n, on):
        if (n, on) not in self.cache:
            cp = self.plan["captions"][n]
            self.cache[(n, on)] = cap_img(self.plan["caption_style"], caption_segs(cp), on and bool(cp["emph"]))
        return self.cache[(n, on)]

    def motion(self, cp, i, nfr, fps):
        """프레임 i(줄이 뜬 뒤) → (배율, 불투명도)."""
        if cp["anim"] == "pop":
            return (pop_key(i / fps) if cp["key"] else pop(i / fps)), 1.0
        if cp["anim"] == "fade":                      # sub_anim.render 의 rise — 페이드 + 0.94→1.0 (3~4프레임), 머무는 동안 1.0→1.02
            nin = min(4, max(1, nfr - 1))
            if i < nin:
                p = 1 - (1 - (i + 1) / nin) ** 2
                return 0.94 + 0.06 * p, 0.58 + 0.42 * p
            return 1.0 + 0.02 * (i / max(1, nfr - 1)), 1.0
        return 1.0, 1.0

    def draw(self, frame, n, j, j0, j1, fps):
        cp = self.plan["captions"][n]
        t_plan = j / fps * self.plan["speed"]
        on = cp["emph_from"] is None or t_plan >= cp["emph_from"]
        s, a = self.motion(cp, j - j0, j1 - j0, fps)
        comp(frame, self.image(n, on), cy=self.plan["caption_style"]["y"], s=s, a=a)


# ─────────────────────────── 그래픽 ───────────────────────────

class Graphics:
    def __init__(self, plan):
        self.plan = plan
        self.W, self.H = plan["seq"]["w"], plan["seq"]["h"]
        self.arr, self.mov = {}, {}

    def is_mov(self, g):
        return Path(g["file"]).suffix.lower() in (".mov", ".mp4", ".webm", ".avi")

    def draw(self, frame, n, i):
        """n 번 그래픽의 i 번째 프레임(켜진 뒤)을 얹는다."""
        g = self.plan["graphics"][n]
        f = float(self.plan["_fps"])
        path = P.abs_path(self.plan, g["file"])
        if self.is_mov(g):
            if n not in self.mov:
                self.mov[n] = MovRGBA(path, self.W, self.H)
            comp(frame, self.mov[n].get(i))
            return
        if n not in self.arr:
            self.arr[n] = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32)
        tt = i / f
        cx, cy = g.get("pos") or (self.W / 2, self.H / 2)
        s, a, dy = g["scale"], 1.0, 0
        if g["anim"] == "pop":
            s *= pop(tt, 0.25, 0.7)
        elif g["anim"] == "fade":
            a = min(1.0, tt / 0.2)
        elif g["anim"] == "slide_up":
            dy = 300 * (1 - min(1.0, tt / 0.25)) ** 3
        comp(frame, self.arr[n], cx=cx, cy=cy, s=s, a=a, dy=dy)

    def close(self):
        for m in self.mov.values():
            m.close()


# ─────────────────────────── 오버레이 (알파 영상 층) ───────────────────────────

class Overlays:
    """overlays[] — 알파 MOV/PNG(시퀀스)를 그래픽 위·자막 아래에 얹는다. 영상은 최종(출력) 프레임 속도로 흐른다."""

    def __init__(self, plan):
        self.plan = plan
        self.W, self.H = plan["seq"]["w"], plan["seq"]["h"]
        self.src = {}

    def size(self, n):
        o = self.plan["overlays"][n]
        info = P.probe(P.overlay_frames(self.plan, o)[0])
        return info["w"], info["h"]

    def draw(self, frame, n, i):
        o = self.plan["overlays"][n]
        kind = P.overlay_kind(self.plan, o)
        if n not in self.src:
            w, h = self.size(n)
            if kind == "still":
                self.src[n] = np.asarray(Image.open(P.overlay_frames(self.plan, o)[0]).convert("RGBA")).astype(np.float32)
            else:
                self.src[n] = MovRGBA(P.abs_path(self.plan, o["file"]), w, h, float(self.plan["_fps"]) if kind == "seq" else None)
        s = self.src[n]
        arr = s if kind == "still" else s.get(i)
        cx = self.W / 2 if o["x"] is None else o["x"]
        cy = self.H / 2 if o["y"] is None else o["y"]
        comp(frame, arr, cx=cx, cy=cy, s=o["scale"])

    def close(self):
        for m in self.src.values():
            if isinstance(m, MovRGBA):
                m.close()


# ─────────────────────────── 장면 틀 (렌더와 XML 이 같이 쓴다) ───────────────────────────

def layout(plan):
    """출력 프레임 범위들. → dict(n_out, cuts=[(j0,j1)], caps=[(j0,j1)], gfx=[(j0,j1)], ovl=[(j0,j1)])"""
    n_out = P.n_frames(plan)
    return dict(n_out=n_out,
                cuts=[P.frame_range(plan, c["start"], c["end"], n_out) for c in plan["cuts"]],
                caps=[P.frame_range(plan, c["start"], c["end"], n_out) for c in plan["captions"]],
                gfx=[P.frame_range(plan, g["start"], g["end"], n_out) for g in plan["graphics"]],
                ovl=[P.frame_range(plan, o["t0"], o["t1"], n_out) for o in plan["overlays"]])


def flash_ranges(plan, lay):
    return [(lay["cuts"][k][0], min(lay["cuts"][k][0] + P.FLASH_FRAMES, lay["cuts"][k][1])) for k, c in enumerate(plan["cuts"]) if c["flash"]]


def render_video(plan, lay, out_mp4, log=print):
    W, H, f = plan["seq"]["w"], plan["seq"]["h"], float(plan["_fps"])
    n_out, jr = lay["n_out"], lay["cuts"]
    caps, gfx, ovl = Captions(plan), Graphics(plan), Overlays(plan)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", fr_str(plan), "-i", "-",
                            "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", str(out_mp4)], stdin=subprocess.PIPE)
    flashes = flash_ranges(plan, lay)
    cur, src, last, black, short = -1, None, None, 0, 0
    still = None
    for j in range(n_out):
        k = max(i for i, (a, b) in enumerate(jr) if a <= j)
        c = plan["cuts"][k]
        if k != cur:
            if isinstance(src, Reader):
                short += src.short
                src.close()
            if c["kind"] == "image":
                src, still = None, still_frame(plan, c)
            else:
                src, still = Reader(plan, c, jr[k][1] - jr[k][0]), None
            cur = k
        frame = np.array(still if still is not None else src.next(), dtype=np.uint8)
        # 전환 — 들어오는 컷(enter) 또는 컷 앞뒤 걸침(straddle)
        t = c.get("tr")
        if t and t["mode"] == "enter":
            n = int(math.ceil(t["dur"] * f))
            if j - jr[k][0] < n:
                frame = apply_tr(t["kind"], frame, last, (j - jr[k][0]) / (t["dur"] * f))
        elif t and t["mode"] == "straddle":
            h = t["dur"] * STRADDLE_HALF
            tt = (j - jr[k][0]) / f
            if tt < h:
                frame = tr_fx(t["kind"], frame, (1 - tt / h) ** 2)
        if k + 1 < len(plan["cuts"]):
            nt = plan["cuts"][k + 1].get("tr")
            if nt and nt["mode"] == "straddle":
                h = nt["dur"] * STRADDLE_HALF
                tt = (jr[k + 1][0] - j) / f
                if tt <= h:
                    frame = tr_fx(nt["kind"], frame, (1 - tt / h) ** 2)
        last = frame.copy()
        frame = np.ascontiguousarray(frame)
        for n, (a, b) in enumerate(lay["gfx"]):
            if a <= j < b:
                gfx.draw(frame, n, j - a)
        for n, (a, b) in enumerate(lay["ovl"]):
            if a <= j < b:
                ovl.draw(frame, n, j - a)
        for n, (a, b) in enumerate(lay["caps"]):
            if a <= j < b:
                caps.draw(frame, n, j, a, b, f)
                break
        if any(a <= j < b for a, b in flashes):
            frame[:] = 255
        if frame.mean() < 12:
            black += 1
        enc.stdin.write(frame.tobytes())
        if j % 150 == 0:
            log(f"  … {j / f:5.1f}s / {n_out / f:.1f}s")
    if isinstance(src, Reader):
        short += src.short
        src.close()
    gfx.close()
    ovl.close()
    enc.stdin.close()
    enc.wait()
    return dict(black=black, short=short)


# ─────────────────────────── 소리 ───────────────────────────

def _ff_load(path, af):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-af", af, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).reshape(-1, 2).copy()


def lufs(p):
    """[sg_render.lufs 이식] ebur128 통합 음량."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True, errors="ignore")
    for ln in reversed(r.stderr.splitlines()):
        if ln.strip().startswith("I:"):
            return float(ln.split()[1])
    return -70.0


def loud_db(x):
    """[sg_render.loud_db 이식] 가장 큰 0.4초 구간의 RMS(dB). «뿅» 처럼 짧은 소리는 ebur128 이 −70 으로 재서 크게 키워 버려서 이걸로 잰다."""
    m = x.mean(axis=1)
    n = int(0.4 * SR)
    if len(m) <= n:
        r = np.sqrt((m ** 2).mean())
    else:
        c = np.concatenate([[0.0], np.cumsum(m.astype(np.float64) ** 2)])
        r = np.sqrt(((c[n:] - c[:-n]) / n).max())
    return 20 * np.log10(max(r, 1e-6)) - 0.7


def _sfx_row(plan, file):
    """효과음 이름 → 등급표 행 모양. 배치표 옆에 그 파일이 있으면 그것을, 없으면 이름으로 등급표·SFX_LIB 에서 찾는다."""
    p = P.abs_path(plan, file)
    if p.exists():
        return {"파일": str(p), "소재상태": "통과", "등급": "-"}
    return SFX.by_name(Path(str(file)).name)


# ─────────────────────────── 한 편 마감 체인 (sfx.md 15장 · 원본 v5_sound.py 189-295행) ───────────────────────────
# 숫자는 전부 원본 그대로: 리버브 mix() 250행 (0.043,0.16)(0.071,0.11)(0.113,0.07) · 겹침 181행 0.12초 · BGM 필터 198행 ·
# 페이드 205-208행(앞 0.8초 제곱·끝 0.6초) · 덕킹 262행 smooth_gain(act,-9.0) 기본 attack 0.12/release 0.45/hold 0.35 (212행) ·
# 큰 효과음 271행 −3dB attack 0.05/release 0.6/hold 0.1, 구간 0.6초(269행) · 합산 276행 피크 0.95 · master() 283-289행.
# 이 체인은 «미리보기에만» 적용된다 — XML(media/)에는 목소리·BGM·효과음 낱개와 클립 볼륨만 간다(edit_xml 은 plain 합 au["mix"] 기준).

REVERB = ((0.043, 0.16), (0.071, 0.11), (0.113, 0.07))     # v5_sound.mix 250행
OVERLAP_S = 0.12                                           # v5_sound.plan_sfx 181행
BGM_EQ = "highpass=f=50,equalizer=f=2500:t=o:w=1.3:g=-5,highshelf=f=9000:g=-2.5,acompressor=threshold=-20dB:ratio=2:attack=20:release=250"   # bgm_segment 198행(목소리 있음 = −5)
BGM_FADE_IN = 0.8                                          # bgm_segment 205행 (제곱 곡선). 끝 페이드는 배치표 bgm.fade_out
DUCK_THRESH = 10 ** (-40 / 20)                             # mix 259행 — 말하는 구간 = 목소리 절대값이 −40dBFS 초과 (정규화 전 값)
ACCENT_S = 0.6                                             # mix 269행
MASTER_COMP = "acompressor=threshold=-18dB:ratio=2:attack=15:release=200:makeup=1"    # master 283행
# master 289행은 0.89(−1dB)였다 — 10-13 한비즈 DB광고1 A: 샘플 피크만 잡아 AAC 인코딩 뒤 트루피크 −0.7dBFS(기준 −1.5 초과)
# → 4배 오버샘플 + 0.76(−2.4dB) 로 트루피크까지 잡는다(실측: 같은 믹스 −14.2 LUFS · TP −2.0)
# 10-13 B: 마스터 TP −2.0 인데 AAC 인코딩에서 +0.3 으로 2.3dB 튐(틱·팝 효과음 고역) → 16.5kHz 로우패스를 앞에(실측 AAC 뒤 TP −2.1 · −14.1 LUFS)
MASTER_LIMIT = "lowpass=f=16500:p=2,aresample=192000,alimiter=limit=0.76:attack=1:release=60:level=false,aresample=48000"


def smooth_gain(active, down_db, attack=0.12, release=0.45, hold=0.35):
    """[v5_sound.smooth_gain 이식] active(0/1, 샘플) → 부드러운 게인(샘플). hold 초보다 짧은 빈틈은 메워 문장 사이 숨에 음악이 튀어 오르지 않게.
    attack = 내려갈 때, release = 올라올 때의 시정수(초) — 원본 의미 그대로(x < cur 이면 attack)."""
    hop = SR // 100
    act = active[::hop].astype(np.float32)
    h = int(hold * 100)
    idx = np.where(act > 0)[0]
    for a_, b_ in zip(idx[:-1], idx[1:]):
        if 1 < b_ - a_ <= h:
            act[a_:b_] = 1
    g = np.ones_like(act)
    tgt = np.where(act > 0, 10 ** (down_db / 20), 1.0)
    ka, kr = 1 - np.exp(-1 / (attack * 100)), 1 - np.exp(-1 / (release * 100))
    cur = 1.0
    for i, x in enumerate(tgt):
        cur += (x - cur) * (ka if x < cur else kr)
        g[i] = cur
    out = np.repeat(g, hop)[:len(active)]
    return np.pad(out, (0, len(active) - len(out)), mode="edge") if len(out) < len(active) and len(out) else out


def voice_active(vbus):
    """말하는 구간 마스크(샘플) — 목소리 절대값이 −40dBFS 를 넘는 곳."""
    return np.abs(vbus).max(1) > DUCK_THRESH


def finish_mix(plan, vbus, bbus, fxl, N):
    """한 편 마감 체인 — plan['finish'] 의 켜진 단계만. fxl = [(t, x, prio, 이름)] (효과음 낱개 시각순). → dict(mix, bgm_fin, dropped, applied)
    합산은 BGM + 효과음 버스 + 목소리, 피크 0.95 로 정규화(peak_norm)."""
    fin = plan["finish"]
    applied, dropped = [], []
    items = sorted(fxl, key=lambda z: z[0])
    if fin["overlap"]:
        keep = []
        for it in items:
            if keep and it[0] - keep[-1][0] < OVERLAP_S and it[2] <= 1 and len(it[1]) < SR:
                dropped.append(it[3])
                continue
            keep.append(it)
        items = keep
        applied.append(f"효과음 겹침 제거 — {OVERLAP_S}초 안에 겹친 우선순위 1·1초 미만 효과음을 뺌" + (f" ({len(dropped)}발: {', '.join(dropped)})" if dropped else " (이번 건은 뺀 것 없음)") + " — XML 에는 낱개가 그대로 있다")
    fx = np.zeros((N, 2), np.float32)
    for t, x, _, _ in items:
        i = int(round(t * SR))
        if i < N:
            n = min(len(x), N - i)
            fx[i:i + n] += x[:n]
    if fin["reverb"]:
        wet = np.zeros_like(fx)
        for d, g in REVERB:
            k = int(d * SR)
            wet[k:] += fx[:-k] * g
        fx = fx + wet
        applied.append("효과음 리버브 버스 43·71·113ms (0.16·0.11·0.07)")
    bgm = bbus.copy()
    if bgm.any() and fin["duck"]:
        bgm *= smooth_gain(voice_active(vbus), fin["duck_db"])[:, None]
        applied.append(f"말 밑 BGM 덕킹 {fin['duck_db']:g}dB (어택 0.12 / 유지 0.35 / 릴리즈 0.45초 — 원본 smooth_gain 기본값: 내려갈 땐 attack, 올라올 땐 release, hold 이하의 숨은 메움)")
    if bgm.any() and fin["accent"]:
        acc = np.zeros(N, bool)
        for t, x, pr, _ in items:
            if pr >= 3:
                acc[int(t * SR):int(t * SR) + int(ACCENT_S * SR)] = True
        if acc.any():
            bgm *= smooth_gain(acc, fin["accent_db"], attack=0.05, release=0.6, hold=0.1)[:, None]
            applied.append(f"큰 효과음(prio≥3) 순간 BGM {fin['accent_db']:g}dB (0.6초, 어택 0.05 / 릴리즈 0.6 / 유지 0.1)")
    out = bgm + fx + vbus
    if fin["peak_norm"]:
        out = out / max(1.0, float(np.abs(out).max()) / 0.95)
    return dict(mix=out.astype(np.float32), bgm_fin=bgm, dropped=dropped, applied=applied)


def duck_stat(vbus, bgm_fin):
    """덕킹이 실제로 걸렸는지 — 말 «한가운데»(말 구간에서 앞뒤 0.6초씩 깎은 곳)의 BGM RMS 와 말에서 1초 이상 떨어진 곳의 BGM RMS. → (말 dB, 쉼 dB, 차 dB) 또는 None.
    첫 1초(페이드인)와 끝 1.5초(페이드아웃)는 뺀다."""
    def dil(m, k):                      # 앞뒤 k 칸씩 넓힘 (0.01초 단위)
        c = np.concatenate([[0], np.cumsum(np.pad(m.astype(int), k))])
        return (c[2 * k + 1:] - c[:-2 * k - 1]) > 0

    act = voice_active(vbus)
    hop = SR // 100
    a = act[::hop]
    a = ~dil(~dil(a, 18), 18)           # 0.18초 이하 빈틈은 메움 = 닫기 (smooth_gain hold 0.35초와 같은 폭)
    talk = ~dil(~a, 60)                 # 앞뒤 0.6초 깎음
    rest = ~dil(a, 100)                 # 말에서 1초 이상
    ok = np.zeros(len(a), bool)
    ok[100:max(100, len(a) - 150)] = True
    m = bgm_fin.mean(axis=1)

    def rms(mask):
        mask = mask & ok
        if not mask.any():
            return None
        sel = np.repeat(mask, hop)[:len(m)]
        s = m[:len(sel)][sel]
        return float(20 * np.log10(np.sqrt((s.astype(np.float64) ** 2).mean()) + 1e-9)) if len(s) else None
    t, r = rms(talk), rms(rest)
    return (t, r, t - r) if t is not None and r is not None else None


def build_audio(plan, outdir):
    """소리 재료를 만든다 — 렌더(미리보기)와 XML(media/)이 같은 재료를 쓴다.
    outdir 에 A1_목소리.wav(배속 구움) · A2_BGM.wav · SFX_NN_이름.wav(목소리 대비 크기까지 구움)를 쓰고
    dict(dur, ref, voice=(경로, 시작초), bgm=(경로, 시작초)|None, sfx=[dict(t, path, name, dur, db, prio, dropped)], mix=plain 합 — XML 이 쓴다,
    mix_finish=마감 체인을 건 합 — 미리보기가 쓴다, preview_only=[XML 에 없는 처리], vbus=목소리, bgm_fin=덕킹까지 한 BGM) 를 돌려준다. 시각은 최종 초."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    sp = plan["speed"]
    dur = P.n_frames(plan) / float(plan["_fps"])
    N = int(round(dur * SR))
    mix = np.zeros((N, 2), np.float32)
    vbus = np.zeros((N, 2), np.float32)         # 마감 체인용 — 목소리·BGM 따로
    bbus = np.zeros((N, 2), np.float32)
    fxl = []                                    # (시각, 배열, 우선순위, 이름) — 마감 체인이 효과음 버스를 다시 만든다

    def put(buf, x, t):
        i = int(round(t * SR))
        if i >= len(buf):
            return
        n = min(len(x), len(buf) - i)
        buf[i:i + n] += x[:n]

    fq = float(plan["_fps"])

    def snap(x, t):
        """시작을 시퀀스 프레임 격자 위로 — XML 클립은 프레임 단위로만 놓이므로, 남는 부분은 소리 앞에 무음으로 붙여 구워 둔다."""
        tq = math.floor(t * fq + 1e-6) / fq
        pad = int(round((t - tq) * SR))
        return (np.concatenate([np.zeros((pad, 2), np.float32), x]) if pad else x), tq

    v = plan["voice"]
    vx = _ff_load(P.abs_path(plan, v["file"]), f"atempo={sp}")
    ref = SFX.voice_ref_from(vx)
    vx, vt = snap(vx, v["start"] / sp)
    vpath = outdir / "A1_목소리.wav"
    SFX.write_wav(vpath, vx)
    put(mix, vx, vt)
    put(vbus, vx, vt)
    out = dict(dur=dur, ref=ref, voice=(vpath, vt), bgm=None, sfx=[])
    fin = plan["finish"]

    b = plan.get("bgm")
    if b:
        def bgm_shape(bx, proc):
            bx = bx * (10 ** (b["gain_db"] / 20))
            if proc:                                   # 앞 0.8초 제곱 페이드인 (bgm_segment 205행) — 미리보기 전용
                fi = min(int(BGM_FADE_IN * SR), len(bx))
                bx[:fi] *= np.linspace(0, 1, fi)[:, None] ** 2
            bx, bt_ = snap(bx, b["start"] / sp)        # 배경음은 원속
            bx = bx[:max(0, N - int(round(bt_ * SR)))]
            fade = int(b["fade_out"] * SR)
            if 0 < fade < len(bx):
                bx[-fade:] *= np.linspace(1, 0, fade)[:, None]
            return bx, bt_
        bx, bt = bgm_shape(_ff_load(P.abs_path(plan, b["file"]), "anull"), False)     # XML 용 — 가공 없음
        bpath = outdir / "A2_BGM.wav"
        SFX.write_wav(bpath, bx)
        put(mix, bx, bt)
        if fin["bgm_eq"]:                              # 미리보기 용 — 필터 체인을 건 BGM
            px, pt = bgm_shape(_ff_load(P.abs_path(plan, b["file"]), BGM_EQ), True)
            put(bbus, px, pt)
        else:
            put(bbus, bx, bt)
        out["bgm"] = (bpath, bt)

    SFX.SND.clear()
    for role, r in plan["sfx_roles"].items():
        SFX.SND[role] = SFX.role(_sfx_row(plan, r["file"]), r.get("min_len", 0.0), r.get("rel_db", SFX.FILE_DB_DEFAULT), r.get("align", "peak"), db=r.get("exact_db"))
    placed = []
    for n, e in enumerate(sorted(plan["sfx"], key=lambda e: e["t"])):
        prio = e.get("prio", plan["sfx_roles"].get(e.get("role"), {}).get("prio", 1))
        if e.get("role"):
            r = plan["sfx_roles"][e["role"]]
            name, align = Path(_sfx_row(plan, r["file"])["파일"]).name, r.get("align", "peak")
            if e.get("exact_db") is not None:         # 이 한 발만 역할 크기를 덮는다
                key = f"_f{n}"
                SFX.SND[key] = SFX.role(_sfx_row(plan, r["file"]), r.get("min_len", 0.0), r.get("rel_db", SFX.FILE_DB_DEFAULT), "peak", db=e["exact_db"])
                x, peak_at = SFX.prep(key, ref)
            else:
                x, peak_at = SFX.prep(e["role"], ref)
        else:
            row = _sfx_row(plan, e["file"])
            path = SFX.find_file(row["파일"])
            name = path.name
            if e.get("abs_db") is not None:           # sg_render PAL 방식 — 가장 큰 0.4초 RMS 를 그 dB 로
                x = SFX.load(path)[:int(SFX.TAIL_MAX * SR)]
                fo = min(len(x) // 3, int(0.25 * SR))
                x[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
                x *= 10 ** ((e["abs_db"] - loud_db(x)) / 20)
                x *= min(1.0, 0.89 / (np.abs(x).max() + 1e-9))
                peak_at = (int(np.argmax(SFX.rms_frames(x))) + 0.5) * 0.05
            else:
                key = f"_f{n}"
                SFX.SND[key] = SFX.role(row, e.get("min_len", 0.0), e.get("rel_db", SFX.FILE_DB_DEFAULT), "peak", db=e.get("exact_db"))
                x, peak_at = SFX.prep(key, ref)
            align = e.get("align", "start" if e.get("abs_db") is not None else "peak")
        t = e["t"] / sp
        if align == "peak":
            t -= peak_at
        if t < 0:
            x, t = x[int(round(-t * SR)):], 0.0
        x, t = snap(x, t)
        placed.append(dict(t=t, x=x, n=n, name=name, prio=prio, burst=e.get("burst"), label=f"{name}@{t:.2f}s"))
    # 10-19 겹침 0 — 길이 상한으로 미리 자르지 않고, 다음 소리 들리는 어택 앞에서 0.2초 감쇠로 끝낸다(sfx.md 결정표 ④⑤)
    out["fit"] = SFX.fit_tails(placed)
    for d in sorted(placed, key=lambda d: d["t"]):
        x, t, name, prio = d["x"], d["t"], d["name"], d["prio"]
        wav = outdir / f"SFX_{d['n']:02d}_{re.sub(r'[^0-9A-Za-z가-힣._-]+', '_', Path(name).stem)}.wav"
        SFX.write_wav(wav, x)
        put(mix, x, t)
        fxl.append((t, x, prio, d["label"]))
        out["sfx"].append(dict(t=t, path=wav, name=name, dur=len(x) / SR, db=loud_db(x), prio=prio, dropped=False, burst=d["burst"]))
    out["mix"] = mix                                   # plain 합 — edit_xml 이 마스터 게인을 재는 기준 (건드리지 않는다)
    fm = finish_mix(plan, vbus, bbus, fxl, N)
    for s, (_, _, _, label) in zip(out["sfx"], fxl):
        s["dropped"] = label in fm["dropped"]
    out.update(mix_finish=fm["mix"], vbus=vbus, bgm_fin=fm["bgm_fin"], preview_only=list(fm["applied"]))
    if fin["bgm_eq"] and b:
        out["preview_only"].insert(0, "BGM 필터 — 50Hz 하이패스 · 2.5kHz −5dB · 9kHz 하이셸프 −2.5dB · 컴프(−20dB, 2:1) · 앞 0.8초 제곱 페이드인")
    if fin["master_comp"]:
        out["preview_only"].append("마스터 컴프 (−18dB, 2:1, 어택 15 / 릴리즈 200ms) → loudnorm")
    if fin["limiter"]:
        out["preview_only"].append("alimiter 0.89 (loudnorm 뒤)")
    return out


def true_peak(p):
    """ebur128 트루피크(dBTP). 못 읽으면 None."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True, errors="ignore")
    m = re.findall(r"Peak:\s+(-?inf|-?[\d.]+)\s+dBFS", r.stderr)
    return float(m[-1]) if m else None


def loudnorm_wav(src, dst, target, comp=False, limiter=False):
    """2패스 loudnorm(측정 → linear) — sg_render 는 한 패스였다. 통합 음량이 목표에 가장 가깝게 맞는다.
    comp = 앞에 마스터 컴프(master 283행), limiter = 뒤에 alimiter 0.89(289행) — 측정 패스도 같은 체인으로 잰다."""
    pre = MASTER_COMP + "," if comp else ""
    post = "," + MASTER_LIMIT if limiter else ""
    base = f"loudnorm=I={target}:TP={LOUD_TP}:LRA={LOUD_LRA}"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", pre + base + ":print_format=json", "-f", "null", "-"], capture_output=True, text=True, errors="ignore")
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    if m:
        j = json.loads(m.group(0))
        af = (base + f":measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
              f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    else:
        af = base
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", pre + af + post + f",aresample={SR}", "-ar", str(SR), str(dst)], check=True)


# ─────────────────────────── 한 편 ───────────────────────────

def probe_out(mp4):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate,duration", "-of", "json", str(mp4)],
                       capture_output=True, text=True)
    return json.loads(r.stdout)["streams"]


def run(plan_path, out=None, ignore=False, log=print):
    """배치표 → 미리보기. → (mp4 경로, 점검 파일 경로, ERROR 수 — ignore 로 통과했으면 무시한 위반 수). ERROR 가 있고 ignore 가 아니면 mp4 를 만들지 않는다."""
    plan = P.load(plan_path)
    out = Path(out) if out else C.EDIT_WORK / plan["name"] / f"{plan['name']}_미리보기.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    rpt = out.with_name(out.stem + "_점검.txt")
    work = out.parent / "_work"
    work.mkdir(exist_ok=True)
    lay = layout(plan)
    f = float(plan["_fps"])

    items = RC.check_plan(P.shots(plan), [c["text"] for c in plan["captions"]], (), plan.get("script"))
    n_err = sum(1 for x in items if x[0] == "ERROR")
    rows = [f"배치표: {Path(plan_path).name} · 컷 {len(plan['cuts'])} · 자막 {len(plan['captions'])} · 그래픽 {len(plan['graphics'])} · 오버레이 {len(plan['overlays'])} · 효과음 {len(plan['sfx'])}",
            f"시퀀스 {plan['seq']['w']}x{plan['seq']['h']} {plan['_fps']} ({f:.3f}fps) · 배속 {plan['speed']}배(배경음 원속) · 마감 {plan['loudness_lufs']} LUFS / TP {LOUD_TP}"]
    ignored = []
    if n_err and not ignore:
        _write_report(rpt, rows, items, "렌더 전 규칙 점검에서 ERROR — 멈춤 (--무시 로만 통과)", ignored)
        return None, rpt, n_err
    if n_err:
        ignored += [x for x in items if x[0] == "ERROR"]

    vid, au_wav, au_norm = work / "video.mp4", work / "premix.wav", work / "master.wav"
    log("소리 …")
    au = build_audio(plan, work / "audio")
    SFX.write_wav(au_wav, au["mix_finish"])        # 마감 체인을 건 합 (XML 은 plain au["mix"] 를 쓴다)
    ev = [(s["t"], s["name"], s["dur"], s.get("burst")) for s in au["sfx"]]
    sitems = RC.check_sfx(ev, au["dur"], per_ep_max=plan.get("sfx_per_ep_max", RC.SFX_PER_EP_MAX)) + au["fit"]   # 소리를 섞은 뒤 — 화면을 그리기 전에 막는 편이 싸다
    sitems += RC.check_tone(s["name"] for s in au["sfx"])
    items = items + sitems
    s_err = [x for x in sitems if x[0] == "ERROR"]
    if s_err and not ignore:
        _write_report(rpt, rows, items, "소리 점검에서 ERROR — 멈춤 (--무시 로만 통과)", ignored)
        return None, rpt, n_err + len(s_err)
    ignored += s_err
    log("화면 …")
    vinfo = render_video(plan, lay, vid, log)
    fin = plan["finish"]
    loudnorm_wav(au_wav, au_norm, plan["loudness_lufs"], comp=fin["master_comp"], limiter=fin["limiter"])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(au_norm), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "256k", "-shortest", str(out)], check=True)

    st = probe_out(out)
    v = next(s for s in st if s["codec_type"] == "video")
    a_ = next(s for s in st if s["codec_type"] == "audio")
    tp = true_peak(out)
    tp_txt = "?" if tp is None else f"{tp:.1f}"
    rows += [f"길이: 영상 {float(v['duration']):.3f}초 · 소리 {float(a_['duration']):.3f}초 · {v['width']}x{v['height']} {v['r_frame_rate']}",
             f"어두운 프레임(평균 밝기 12 미만): {vinfo['black']}개 · 원본이 모자라 마지막 프레임을 되풀이한 횟수: {vinfo['short']}",
             "전환: " + (" · ".join(f"컷{k}:{c['tr']['kind']}({c['tr']['mode']},{c['tr']['dur']}s)" for k, c in enumerate(plan["cuts"]) if c.get("tr")) or "없음(전부 그냥 컷)"),
             "흰 플래시: " + (", ".join(f"{a}~{b - 1}프레임" for a, b in flash_ranges(plan, lay)) or "없음"),
             f"목소리 기준 크기(50ms RMS 중앙): {au['ref']:.1f} dBFS · 마감 전 {lufs(au_wav):.1f} LUFS → 마감 후 {lufs(out):.1f} LUFS (목표 {plan['loudness_lufs']})",
             f"효과음 {len(au['sfx'])}개 — 가장 큰 0.4초 RMS(loud_db): " + ", ".join(f"{s['name']}@{s['t']:.2f}s {s['db']:.1f}dB" for s in au["sfx"]),
             f"마감 트루피크: {tp_txt} dBTP (기준 ≤ {LOUD_TP}, aac 인코딩 뒤)"]
    ds = duck_stat(au["vbus"], au["bgm_fin"]) if plan.get("bgm") else None
    if ds:
        rows.append(f"덕킹 실측: 말 한가운데 BGM {ds[0]:.1f} dBFS · 말 없는 곳 BGM {ds[1]:.1f} dBFS · 차 {ds[2]:.1f} dB (finish.duck {'켬 ' + format(fin['duck_db'], 'g') + 'dB' if fin['duck'] else '끔'})")
    rows.append("XML 에는 없는 처리 (미리보기에만 적용 — 프리미어에서 들리는 소리와 다르다):")
    rows += [f"  - {x}" for x in au["preview_only"]] or ["  - 없음 (finish 가 전부 꺼짐)"]
    _write_report(rpt, rows, items, None, ignored)
    return out, rpt, len(ignored)


def _write_report(rpt, rows, items, stop, ignored):
    err = [x for x in items if x[0] == "ERROR"]
    lines = list(rows)
    if stop:
        lines.append("★ " + stop)
    if ignored:
        lines.append(f"★ --무시 로 통과한 위반 {len(ignored)}건:")
        lines += [f"    [{lv}] {r}: {m}" for lv, r, m in ignored]
    lines += ["", f"규칙 점검 — ERROR {len(err)} · WARN {len(items) - len(err)}  (기준: {RC.GUIDE})"]
    lines += [f"  [{lv}] {r}: {m}" for lv, r, m in items] or ["  통과"]
    Path(rpt).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines), flush=True)


def main():
    ap = argparse.ArgumentParser(description="배치표 → 미리보기 mp4 + _점검.txt")
    ap.add_argument("plan")
    ap.add_argument("--out")
    ap.add_argument("--무시", dest="ignore", action="store_true", help="rule_check ERROR 를 무시하고 통과(위반 목록은 점검 파일에)")
    a = ap.parse_args()
    try:
        out, rpt, n = run(a.plan, a.out, a.ignore)
    except P.PlanError as e:
        print(e)
        sys.exit(2)
    print("→", out or "(만들지 않음)", "|", rpt)
    sys.exit(1 if out is None else 0)


if __name__ == "__main__":
    main()
