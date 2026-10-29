# -*- coding: utf-8 -*-
r"""4번 전체를 사장님 저장본대로 다시 짜서 «소리 고친» 확인용 MP4 를 만든다 (10-20).

사장님(10-20): «이거 니가 저대로 MP4 파일만들어봐» — mix_audit.py --fix 로 고친 소리(fix_mix.wav)를 화면에 입힘.
화면 = 저장본 읽기(read_prproj) 그대로: V1 원본(모션 비율·위치) → 연출층(V4 · V2 의 영상 · 중첩 «4번_앞부분_빌딩인형») → 자막(V2·V5) → 제목(V3).
비슷하게만 되는 것: 자막·제목 글꼴 크기·튀는 팝(뺌) · 전환(Lens Blur·Split 뺌) · 제목 뒤 그림(뺌, 43.994 뒤 제목은 글이 저장본에 없어 뺌).

    python 지시작업/tools/mix_audit.py <사본.prproj> 4번 4번_앞부분_빌딩인형 --fix
    python 지시작업/tools/r4_full_render.py <seq.json> <nest.json> <사본.prproj> <출력.mp4>
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mix_audit as M  # noqa: E402

DZ, ROOT = M.DZ, M.ROOT
W, H, FN, FD = 900, 1600, 60000, 1001
FPS = FN / FD
WORK = DZ / "_tmp/r4full"
FONT = ROOT / "소재/fonts/gmarket-sans/GmarketSansMedium.ttf"
CAP_Y, CAP_PX = 924, 62
GREEN = (0, 252, 0, 255)
PREFER = "판없음"          # 같은 이름 연출층이 두 폴더에 있을 때(달팽이경주) — 사장님이 나중에 받으신 판


def fx_of(it):
    s, px, py = 100.0, .5, .5
    for f in it.get("fx", []):
        if f.get("name") == "모션":
            p = f["params"]
            try:
                s = float(p.get("비율 조정", 100))
            except (TypeError, ValueError):
                pass
            pos = p.get("위치", "0.5:0.5")
            pos = pos["v"] if isinstance(pos, dict) else pos
            px, py = (float(v) for v in pos.split(":"))
    return s / 100, px, py


def fr(t):
    return round(t * FPS)


def src_path(name, by):
    c = by.get(name, [])
    if len(c) > 1:
        c = sorted(c, key=lambda p: PREFER not in str(p))
    return c[0] if c else None


def seg(i, it, path, out, alpha=False):
    s, px, py = fx_of(it)
    n = fr(it["t1"]) - fr(it["t0"])
    # 확대(비율 > 화면)도 되게 — 바탕 위에 가운데 기준으로 얹음(넘치는 곳은 잘림)
    bg = f"color=black@0:s={W}x{H}:r={FN}/{FD},format=rgba" if alpha else f"color=black:s={W}x{H}:r={FN}/{FD}"
    fc = (f"[0:v]fps={FN}/{FD},scale=trunc(iw*{s}/2)*2:trunc(ih*{s}/2)*2:flags=lanczos{',format=rgba' if alpha else ''}[s];{bg}[b];"
          f"[b][s]overlay=x=({W}-w)/2+{(px - .5) * W:.0f}:y=({H}-h)/2+{(py - .5) * H:.0f}:format=auto:shortest=1[v]")
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{it['s0']:.4f}", "-i", str(path), "-filter_complex", fc, "-map", "[v]",
           "-frames:v", str(n), "-an"]
    if alpha:
        cmd += ["-pix_fmt", "yuva444p10le", "-c:v", "prores_ks", "-profile:v", "4", str(out)]
    else:
        cmd += ["-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "14", "-preset", "fast", str(out)]
    subprocess.run(cmd, check=True)
    return n


def caption_png(texts, path, y=CAP_Y, px=CAP_PX, colors=None):
    font = ImageFont.truetype(str(FONT), px)
    tmp = Image.new("RGBA", (W * 3, px * 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    x = 0
    for k, t in enumerate(texts):
        c = colors[k] if colors else (255, 255, 255, 255)
        d.text((x, px), t, font=font, fill=c, stroke_width=4, stroke_fill=(0, 0, 0, 230))
        x += d.textlength(t + " ", font=font)
    tmp = tmp.crop(tmp.getbbox())
    if tmp.width > W - 60:
        tmp = tmp.resize((W - 60, int(tmp.height * (W - 60) / tmp.width)), Image.LANCZOS)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im.alpha_composite(tmp, (W // 2 - tmp.width // 2, int(y - tmp.height / 2)))
    im.save(path)


def runs_for(it, cs):
    tx = it["text"]
    key = " ".join(tx)
    if key in cs:
        rs = cs[key]
        return [r["t"] for r in rs], [tuple(r["rgb"]) + (255,) if r["rgb"] else (255, 255, 255, 255) for r in rs]
    if len(tx) > 1:                       # 글 층이 여럿 — 읽는 순서는 뒤 층부터(«제가 18년»), 숫자 층은 초록
        tx = tx[::-1]
        return tx, [GREEN if any(ch.isdigit() for ch in t) else (255, 255, 255, 255) for t in tx]
    return tx, None


def main():
    seq, nest, prproj, out = (Path(a) for a in sys.argv[1:5])
    WORK.mkdir(parents=True, exist_ok=True)
    items = json.loads(seq.read_text(encoding="utf-8"))["items"]
    nitems = json.loads(nest.read_text(encoding="utf-8"))["items"]
    by = M.paths_of(prproj)
    end = max(i["t1"] for i in items if i["track"] == "V1")
    # 1) V1 바탕 — 빈 곳은 검정
    v1 = sorted([i for i in items if i["track"] == "V1" and i["type"] == "VideoClipTrackItem"], key=lambda i: i["t0"])
    parts, cur = [], 0
    for k, it in enumerate(v1):
        it = dict(it, t0=max(it["t0"], cur / FPS))
        if fr(it["t0"]) > cur:
            g = WORK / f"gap_{k}.mp4"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=black:s={W}x{H}:r={FN}/{FD}",
                            "-frames:v", str(fr(it["t0"]) - cur), "-pix_fmt", "yuv420p", "-c:v", "libx264", str(g)], check=True)
            parts.append(g)
            cur = fr(it["t0"])
        p = src_path(it["name"], by)
        o = WORK / f"v1_{k:02d}.mp4"
        cur += seg(k, dict(it, t0=cur / FPS), p, o)
        parts.append(o)
    lst = WORK / "v1.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    base = WORK / "base.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(base)], check=True)
    # 2) 연출층
    ovl = [i for i in items if i["type"] == "VideoClipTrackItem" and i["track"] in ("V2", "V4", "V5") and i["name"] != "그래픽"]
    layers = []
    for k, it in enumerate(sorted(ovl, key=lambda i: i["t0"])):
        if it["name"] == "4번_앞부분_빌딩인형":
            sub = [n for n in nitems if n["track"].startswith("V")][0]
            it = dict(it, name=sub["name"], fx=sub.get("fx", []))
        p = src_path(it["name"], by)
        if p is None:
            print("  [없음]", it["name"])
            continue
        o = WORK / f"ov_{k:02d}.mov"
        seg(k, it, p, o, alpha=True)
        layers.append((it["t0"], o))
    # 3) 자막·제목 PNG
    cs = json.loads((DZ / "_tmp/story/caps_style_1020.json").read_text(encoding="utf-8"))
    caps = []
    for k, it in enumerate(sorted([i for i in items if i["track"] in ("V2", "V5") and i.get("text")], key=lambda i: i["t0"])):
        tx, col = runs_for(it, cs)
        pth = WORK / f"cap_{k:02d}.png"
        caption_png(tx, pth, colors=col)
        caps.append((it["t0"], it["t1"], pth))
    for it in [i for i in items if i["track"] == "V3" and i.get("text")]:
        pth = WORK / "title.png"
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for line, (y, c) in zip(it["text"], [(70, (255, 255, 255, 255)), (150, (255, 212, 59, 255))]):
            caption_png([line], WORK / "_t.png", y=y, px=58, colors=[c])
            im.alpha_composite(Image.open(WORK / "_t.png"))
        im.save(pth)
        caps.append((it["t0"], it["t1"], pth))
    # 4) 합성 + 고친 소리
    ins = ["-i", str(base)]
    fc, last = [], "0:v"
    n = 1
    for t0, o in layers:
        ins += ["-itsoffset", f"{t0:.4f}", "-i", str(o)]
        fc.append(f"[{last}][{n}:v]overlay=eof_action=pass:format=auto[o{n}]")
        last, n = f"o{n}", n + 1
    for t0, t1, pth in caps:
        ins += ["-loop", "1", "-framerate", f"{FN}/{FD}", "-t", f"{end:.3f}", "-i", str(pth)]   # 한 장 그림은 반복 입력이어야 끝까지 얹힌다
        fc.append(f"[{last}][{n}:v]overlay=enable='between(t,{t0:.3f},{t1 - .001:.3f})':eof_action=pass[o{n}]")
        last, n = f"o{n}", n + 1
    fc.append(f"[{last}]format=yuv420p[v]")
    ins += ["-i", str(DZ / "_tmp/story/fix_mix.wav")]
    script = WORK / "fc.txt"
    script.write_text(";".join(fc), encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex_script", str(script), "-map", "[v]", "-map", f"{n}:a",
                    "-t", f"{end:.3f}", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-c:a", "aac", "-b:a", "256k", str(out)], check=True)
    print("완성", out)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
