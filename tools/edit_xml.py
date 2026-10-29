# -*- coding: utf-8 -*-
r"""배치표(JSON) → 프리미어 FCP7 XML + media/ 층별 소재, 그리고 XML 만으로 다시 조립해 미리보기와 대조(verify).

[이식본 — 원본 D:/영상제작/도구/광고편집/ 의 sg_xml2.py(알파 MOV · 효과음 낱개 · 전체 이득) · sg_xml_verify.py(XML 로 다시 조립해 PSNR·LUFS·싱크 대조)
 · ad_xml.py(원본 참조 클립 · Basic Motion 스케일 · 레이트 규칙). 바뀐 것: 분양1 전용 읽기(G.read_xml · plan_v1 · ovs)를 배치표로,
 V1 을 «컷마다 구운 파일» 에서 «원본 참조» 로(사장님이 컷을 밀거나 소재를 바꿔 쓰시도록). 그 대신 전환(렌즈 블러 등)은 XML 에 못 담아 마커로만 남긴다.
 시퀀스 레이트·알파 복원(검정·흰 바탕 두 번 그리기)·Audio Levels 선형 배율은 sg_xml2 그대로. lec_xml 의 url · rate_of 를 재사용.]

    python edit_xml.py 배치표.json [--out 폴더] [--미리보기 mp4]    → <폴더>/<이름>.xml + <폴더>/media/
    import edit_xml; edit_xml.verify(xml, 미리보기_mp4)

트랙: V1 배경 컷(원본 참조) · V2 그래픽(PNG 는 알파 MOV 로 구워서, MOV 는 원본 참조) · [오버레이 — 있을 때만, V2 다음 트랙부터(겹치면 다음 트랙)]
      · 자막(줄마다 알파 MOV) · 흰 플래시(있을 때만).  오버레이가 없으면 V3 자막 · V4 플래시 그대로.
      오버레이 = 배치표 overlays[] — 알파 MOV(ProRes 4444)는 원본 그대로 참조(리프레임은 Basic Motion), 알파 PNG 한 장도 원본 참조, PNG 시퀀스만 media/ 에 알파 MOV 로 굽는다.
      A1 목소리(배속 구운 wav) · A2 BGM(구운 wav, 없으면 빈 트랙) · A3~ 효과음 낱개 wav(겹치면 다음 트랙)

시험하지 못한 것(프리미어를 실제로 열어 보지 못했다): ① Time Remap 속도 효과(배속) ② Basic Motion center(pos) ③ 시퀀스 마커.
  — XML 문법은 Premiere 가 내보내는 모양을 따랐고 verify 는 «이 XML 을 이 규칙대로 읽으면» 미리보기와 같은지만 본다. 프리미어가 다르게 읽으면 verify 로는 못 잡는다.

레이트 규칙(ad_xml.py 의 코드 주석 vs 독스트링이 어긋나 있어 코드 쪽을 따랐다):
  원본이 59.94 인데 시퀀스가 30 일 때, 원본 레이트로 in/out 을 적으면 프리미어가 시퀀스 기준으로 읽어 클립이 비었다(ad_xml 코드 주석).
  → 기본(SRC_RATE="seq"): 파일 <rate> 도 in/out 도 전부 시퀀스 레이트 프레임 수. 독스트링의 «파일마다 제 레이트» 는 SRC_RATE="own" 으로 켠다(미시험).
"""
import argparse
import math
import re
import subprocess
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import config as C  # noqa: E402
import edit_plan as P  # noqa: E402
import edit_render as R  # noqa: E402
import lec_xml  # noqa: E402
import sfx as SFX  # noqa: E402

SR = R.SR
SRC_RATE = "seq"             # "seq"(기본, ad_xml 코드 따름) | "own"
LEVEL_MAX = 3.98109          # Audio Levels 최대(+12dB), sg_xml2


def xml_rate(fps_float):
    """(timebase, ntsc) — lec_xml.rate_of 가 다루는 59.94·29.97·30 은 그것을, 그 밖(24·25·23.976·50·60)은 여기서."""
    try:
        tb, ntsc, _ = lec_xml.rate_of(fps_float)
        return tb, ntsc == "TRUE"
    except ValueError:
        pass
    for v, tb, n in ((23.976, 24, True), (24.0, 24, False), (25.0, 25, False), (50.0, 50, False), (60.0, 60, False)):
        if abs(fps_float - v) < 0.01:
            return tb, n
    raise ValueError(f"fps {fps_float} 는 아직 안 다룬다")


def rate_el(tb, ntsc):
    return f"<rate><timebase>{tb}</timebase><ntsc>{'TRUE' if ntsc else 'FALSE'}</ntsc></rate>"


# ─────────────────────────── 알파 복원 · 구워 쓰기 ───────────────────────────

def alpha_of(draw, W, H):
    """[sg_xml2.alpha_of 이식] draw(frame) 를 검정·흰 바탕에 각각 그려 알파를 되살린다 → RGBA uint8."""
    b = np.zeros((H, W, 3), np.uint8)
    w = np.full((H, W, 3), 255, np.uint8)
    draw(b)
    draw(w)
    bf, wf = b.astype(np.float32), w.astype(np.float32)
    a = np.clip(255 - (wf - bf).mean(2), 0, 255)
    rgb = np.where(a[..., None] > 0.5, bf * 255 / np.maximum(a[..., None], 1), 0)
    return np.dstack([np.clip(rgb, 0, 255), a]).astype(np.uint8)


def enc_rgba(plan, path):
    W, H = plan["seq"]["w"], plan["seq"]["h"]
    return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", R.fr_str(plan), "-i", "-",
                             "-c:v", "png", "-pix_fmt", "rgba", str(path)], stdin=subprocess.PIPE)


def bake_layers(plan, lay, media, log=print):
    """그래픽(PNG)·자막 줄을 알파 MOV 로 굽는다. → (V2 목록, V3 목록) 각 항목 = (경로, j0, j1)"""
    W, H = plan["seq"]["w"], plan["seq"]["h"]
    gfx, caps = R.Graphics(plan), R.Captions(plan)
    f = float(plan["_fps"])
    V2, V3 = [], []
    for n, (j0, j1) in enumerate(lay["gfx"]):
        g = plan["graphics"][n]
        if j1 <= j0:
            continue
        if gfx.is_mov(g):                                    # 알파 MOV 는 원본 그대로 참조
            V2.append((P.abs_path(plan, g["file"]), j0, j1))
            continue
        path = media / f"V2_{n:02d}_{re.sub(r'[^0-9A-Za-z가-힣._-]+', '_', Path(g['file']).stem)}.mov"
        e = enc_rgba(plan, path)
        for j in range(j0, j1):
            e.stdin.write(alpha_of(lambda fr, n=n, i=j - j0: gfx.draw(fr, n, i), W, H).tobytes())
        e.stdin.close()
        e.wait()
        V2.append((path, j0, j1))
        log(f"  V2 {path.name} {j0}~{j1}")
    gfx.close()
    for n, (j0, j1) in enumerate(lay["caps"]):
        if j1 <= j0:
            continue
        path = media / f"V3_{n:02d}_자막.mov"
        e = enc_rgba(plan, path)
        for j in range(j0, j1):
            e.stdin.write(alpha_of(lambda fr, n=n, j=j, a=j0, b=j1: caps.draw(fr, n, j, a, b, f), W, H).tobytes())
        e.stdin.close()
        e.wait()
        V3.append((path, j0, j1))
    log(f"  V3 자막 {len(V3)}줄")
    return V2, V3


def overlay_clips(plan, lay, media, log=print):
    """오버레이 → [dict(path, j0, j1, w, h, nfile, still, o)]. 영상 길이가 구간보다 짧으면 구간 끝을 영상 끝으로 줄인다(검증이 이미 2프레임 넘게 짧으면 막는다)."""
    f = float(plan["_fps"])
    out = []
    for n, (j0, j1) in enumerate(lay["ovl"]):
        o = plan["overlays"][n]
        if j1 <= j0:
            continue
        kind = P.overlay_kind(plan, o)
        frames = P.overlay_frames(plan, o)
        info = P.probe(frames[0])
        if kind == "seq":
            path = media / f"OV_{n:02d}_{re.sub(r'[^0-9A-Za-z가-힣._-]+', '_', o['name'])}.mov"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", R.fr_str(plan), "-i", str(P.abs_path(plan, o["file"])), "-c:v", "prores_ks", "-profile:v", "4444",
                            "-pix_fmt", "yuva444p10le", "-vendor", "apl0", str(path)], check=True)
            nfile, still = len(frames), False
            log(f"  오버레이 {path.name} (PNG 시퀀스 {nfile}장 → 알파 MOV)")
        elif kind == "still":
            path, nfile, still = frames[0], int(round(3600 * f)), True
        else:
            path, nfile, still = frames[0], int(round(info["dur"] * f)), False
        out.append(dict(path=path, j0=j0, j1=min(j1, j0 + nfile), w=info["w"], h=info["h"], nfile=nfile, still=still, o=o))
    return out


def bake_flash(plan, media):
    W, H = plan["seq"]["w"], plan["seq"]["h"]
    path = media / "FX_flash_white.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=white:s={W}x{H}:r={R.fr_str(plan)}", "-frames:v", str(P.FLASH_FRAMES),
                    "-c:v", "libx264", "-crf", "10", "-pix_fmt", "yuv420p", str(path)], check=True)
    return path


# ─────────────────────────── XML 조각 ───────────────────────────

class Files:
    """FCP7 규칙 — 같은 파일은 첫 번째만 전체를 적고 다음부터 id 만."""

    def __init__(self):
        self.ids = {}

    def el(self, path, rate, dur, kind, w=None, h=None):
        key = str(path)
        if key in self.ids:
            return f'<file id="{self.ids[key]}"/>'
        fid = f"file-{len(self.ids) + 1}"
        self.ids[key] = fid
        if kind == "audio":
            media = "<media><audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics><channelcount>2</channelcount></audio></media>"
        else:
            media = (f"<media><video><samplecharacteristics>{rate}<width>{w}</width><height>{h}</height>"
                     "<pixelaspectratio>square</pixelaspectratio></samplecharacteristics></video></media>")
        return (f'<file id="{fid}"><name>{escape(Path(path).name)}</name><pathurl>{escape(lec_xml.url(path))}</pathurl>'
                f"{rate}<duration>{dur}</duration>{media}</file>")


def basic_motion(pct, pos, W, H):
    c = ""
    if abs(pos[0]) > 0.01 or abs(pos[1]) > 0.01:
        c = ('<parameter authoringApp="PremierePro"><parameterid>center</parameterid><name>Center</name>'
             f"<value><horiz>{pos[0] / W:.6f}</horiz><vert>{pos[1] / H:.6f}</vert></value></parameter>")
    return ("<filter><effect><name>Basic Motion</name><effectid>basic</effectid><effectcategory>motion</effectcategory>"
            "<effecttype>motion</effecttype><mediatype>video</mediatype><pproBypass>false</pproBypass>"
            '<parameter authoringApp="PremierePro"><parameterid>scale</parameterid><name>Scale</name><valuemin>0</valuemin><valuemax>1000</valuemax>'
            f"<value>{pct:.4f}</value></parameter>{c}</effect></filter>")


def time_remap(speed):
    return ("<filter><effect><name>Time Remap</name><effectid>timeremap</effectid><effectcategory>motion</effectcategory>"
            "<effecttype>motion</effecttype><mediatype>video</mediatype>"
            '<parameter authoringApp="PremierePro"><parameterid>variablespeed</parameterid><name>variablespeed</name><value>0</value></parameter>'
            f'<parameter authoringApp="PremierePro"><parameterid>speed</parameterid><name>speed</name><valuemin>-100000</valuemin><valuemax>100000</valuemax><value>{speed * 100:.4f}</value></parameter>'
            '<parameter authoringApp="PremierePro"><parameterid>reverse</parameterid><name>reverse</name><value>FALSE</value></parameter>'
            '<parameter authoringApp="PremierePro"><parameterid>frameblending</parameterid><name>frameblending</name><value>FALSE</value></parameter>'
            "</effect></filter>")


def audio_levels(v):
    return ("<filter><effect><name>Audio Levels</name><effectid>audiolevels</effectid><effectcategory>audiolevels</effectcategory>"
            "<effecttype>audiolevels</effecttype><mediatype>audio</mediatype>"
            f'<parameter authoringApp="PremierePro"><parameterid>level</parameterid><name>Level</name><valuemin>0</valuemin><valuemax>{LEVEL_MAX}</valuemax>'
            f"<value>{min(v, LEVEL_MAX):.4f}</value></parameter></effect></filter>")


def wav_frames(path, f):
    return max(1, int(math.floor(P.audio_dur(path) * f + 1e-6)))


# ─────────────────────────── 내보내기 ───────────────────────────

def export(plan_path, out_dir=None, log=print):
    """→ dict(xml, media, master, files...) . 배치표 → XML + media/."""
    plan = P.load(plan_path)
    out_dir = Path(out_dir) if out_dir else C.EDIT_WORK / plan["name"] / "xml"
    media = out_dir / "media"
    media.mkdir(parents=True, exist_ok=True)
    W, H = plan["seq"]["w"], plan["seq"]["h"]
    f = float(plan["_fps"])
    tb, ntsc = xml_rate(f)
    RATE = rate_el(tb, ntsc)
    lay = R.layout(plan)
    n_out, jr = lay["n_out"], lay["cuts"]
    sp = plan["speed"]
    files = Files()

    # ── 소리 재료 · 전체 이득 (마감 loudnorm 이 XML 에 없으니 클립 볼륨에 미리 곱한다 — sg_xml2)
    log("소리 …")
    au = R.build_audio(plan, media)
    pre = out_dir / "_premix.wav"
    SFX.write_wav(pre, au["mix"])
    lu = R.lufs(pre)
    master = 10 ** ((plan["loudness_lufs"] - lu) / 20)
    peak_db = 20 * np.log10(np.abs(au["mix"]).max() + 1e-9)
    capped = 0.0
    if peak_db + 20 * np.log10(master) > R.LOUD_TP:        # XML 에는 리미터(loudnorm)가 없다 — 겹친 봉우리가 0dB 를 넘지 않게 이득을 깎고 모자란 만큼 알린다
        capped = peak_db + 20 * np.log10(master) - R.LOUD_TP
        master *= 10 ** (-capped / 20)
    pre.unlink()
    log(f"  믹스 {lu:.1f} LUFS(최고 {peak_db:.1f} dBFS) → 목표 {plan['loudness_lufs']} 전체 이득 x{master:.3f}"
        + (f" — 최고음이 {R.LOUD_TP} dBFS 를 넘어 {capped:.1f}dB 깎음: XML 은 목표보다 약 {capped:.1f}dB 작게 나온다(미리보기는 loudnorm 이 눌러 맞춤)" if capped else ""))

    log("층 …")
    V2, V3 = bake_layers(plan, lay, media, log)
    ovls = overlay_clips(plan, lay, media, log)
    flashes = R.flash_ranges(plan, lay)
    flash_path = bake_flash(plan, media) if flashes else None

    # ── V1
    v1 = []
    for k, c in enumerate(plan["cuts"]):
        j0, j1 = jr[k]
        if j1 <= j0:
            continue
        src = P.abs_path(plan, c["src"])
        info = P.probe(src)
        pct = R.k_cover(info["w"], info["h"], W, H, c["scale"]) * 100.0
        fx = basic_motion(pct, c["pos"], W, H)
        if c["kind"] == "image":
            dur = int(round(3600 * f))
            fil = files.el(src, RATE, dur, "video", info["w"], info["h"])
            cin, cout, rate_el_ = 0, j1 - j0, RATE
        else:
            if SRC_RATE == "own":
                stb, sntsc = xml_rate(info["fps"])
                srate, sf = rate_el(stb, sntsc), info["fps"]
            else:
                srate, sf = RATE, f
            cin = int(round(R.quant_in(c, f) * sf)) if SRC_RATE == "seq" else int(round(c["in"] * sf))
            cout = cin + int(round((c["end"] - c["start"]) * sf))
            fil = files.el(src, srate, int(round(info["dur"] * sf)), "video", info["w"], info["h"])
            rate_el_ = srate
            if abs(sp - 1.0) > 1e-9:
                fx += time_remap(sp)
        v1.append((f'<clipitem id="V1_{k}"><name>{escape(src.name)}</name><enabled>TRUE</enabled>{rate_el_}'
                   f"<start>{j0}</start><end>{j1}</end><in>{cin}</in><out>{cout}</out>{fil}{fx}</clipitem>"))

    def alpha_clip(cid, path, j0, j1):
        n = int(round(P.audio_dur(path) * f))
        return (f'<clipitem id="{cid}"><name>{escape(Path(path).name)}</name><enabled>TRUE</enabled>{RATE}'
                f"<start>{j0}</start><end>{j1}</end><in>0</in><out>{j1 - j0}</out>{files.el(path, RATE, max(n, j1 - j0), 'video', W, H)}</clipitem>")

    v2 = [alpha_clip(f"V2_{i}", p, a, b) for i, (p, a, b) in enumerate(V2)]
    v3 = [alpha_clip(f"V3_{i}", p, a, b) for i, (p, a, b) in enumerate(V3)]

    def ovl_clip(cid, d):
        o = d["o"]
        s, pos = o["scale"], ((o["x"] - W / 2) if o["x"] is not None else 0.0, (o["y"] - H / 2) if o["y"] is not None else 0.0)
        fx = basic_motion(s * 100.0, pos, W, H) if (abs(s - 1.0) > 1e-9 or abs(pos[0]) > 0.01 or abs(pos[1]) > 0.01) else ""
        return (f'<clipitem id="{cid}"><name>{escape(o["name"])}</name><enabled>TRUE</enabled>{RATE}'
                f"<start>{d['j0']}</start><end>{d['j1']}</end><in>0</in><out>{d['j1'] - d['j0']}</out>"
                f"{files.el(d['path'], RATE, d['nfile'], 'video', d['w'], d['h'])}{fx}</clipitem>")
    ov_lanes, ov_ends = [], []                       # 시간이 겹치는 오버레이는 다음 트랙으로 (효과음과 같은 방식)
    for i, d in enumerate(sorted(ovls, key=lambda d: d["j0"])):
        for li, last in enumerate(ov_ends):
            if last <= d["j0"]:
                ov_lanes[li].append(ovl_clip(f"OV_{i}", d))
                ov_ends[li] = d["j1"]
                break
        else:
            ov_lanes.append([ovl_clip(f"OV_{i}", d)])
            ov_ends.append(d["j1"])
    v4 = [alpha_clip(f"V4_{i}", flash_path, a, b) for i, (a, b) in enumerate(flashes)]

    # ── 오디오
    def aclip(cid, path, start_s, level, limit_n=None):
        s = int(round(start_s * f))
        n = wav_frames(path, f)
        if limit_n is not None:
            n = min(n, max(1, limit_n - s))
        return s, s + n, (f'<clipitem id="{cid}"><name>{escape(Path(path).name)}</name><enabled>TRUE</enabled>{RATE}'
                          f"<start>{s}</start><end>{s + n}</end><in>0</in><out>{n}</out>{files.el(path, RATE, wav_frames(path, f), 'audio')}"
                          '<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack>' + audio_levels(level) + "</clipitem>")

    a1 = [aclip("A1_0", au["voice"][0], au["voice"][1], master, n_out)[2]]
    a2 = [aclip("A2_0", au["bgm"][0], au["bgm"][1], master, n_out)[2]] if au["bgm"] else []
    lanes, ends = [], []
    for i, s in enumerate(sorted(au["sfx"], key=lambda s: s["t"])):
        a, b, it = aclip(f"SFX_{i}", s["path"], s["t"], master, n_out)
        for li, last in enumerate(ends):
            if last <= a:
                lanes[li].append(it)
                ends[li] = b
                break
        else:
            lanes.append([it])
            ends.append(b)

    # ── 마커(전환) — XML 이 못 담는 전환은 여기 남긴다
    markers = []
    for k in range(1, len(plan["cuts"])):
        w = R.tr_window(plan, k, jr)
        if w:
            t = plan["cuts"][k]["tr"]
            markers.append(f"<marker><name>전환 {t['kind']} ({t['mode']})</name><comment>{t['dur']}초</comment><in>{max(0, w[0])}</in><out>{w[1]}</out></marker>")

    trk = lambda items: "<track>" + "".join(items) + "<enabled>TRUE</enabled></track>"   # noqa: E731
    vtracks = trk(v1) + trk(v2) + "".join(trk(ln) for ln in ov_lanes) + trk(v3) + (trk(v4) if v4 else "")
    atracks = trk(a1) + trk(a2) + "".join(trk(ln) for ln in lanes)
    fmt = (f"<format><samplecharacteristics>{RATE}<width>{W}</width><height>{H}</height><pixelaspectratio>square</pixelaspectratio>"
           "</samplecharacteristics></format>")
    x = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="4"><sequence id="seq-1">'
         f"<name>{escape(plan['name'])}</name><duration>{n_out}</duration>{RATE}"
         f"<media><video>{fmt}{vtracks}</video><audio><numOutputChannels>2</numOutputChannels>{atracks}</audio></media>"
         f"{''.join(markers)}</sequence></xmeml>\n")
    xml = out_dir / f"{plan['name']}.xml"
    xml.write_text(x, encoding="utf-8", newline="\n")
    (out_dir / "README.txt").write_text(
        f"{plan['name']} — 프리미어용 (배치표에서 생성)\n\n[파일 > 가져오기] 로 {plan['name']}.xml 을 엽니다. 미디어는 media 폴더 + 원본(배치표 경로).\n\n"
        "V1 배경 컷: 원본 참조(리프레임 = Basic Motion). 배속은 Time Remap 속도 효과 — 프리미어에서 적용이 안 되어 있으면 클립 속도를 직접 맞출 것.\n"
        "V2 그래픽 · 자막: 움직임이 든 투명 영상(.mov). 흰 플래시(있을 때만).\n"
        + (f"V3~V{2 + len(ov_lanes)} 오버레이(원본 알파 영상 참조 — 크기·위치는 Basic Motion), 그 위로 자막{' · 플래시' if v4 else ''}.\n" if ov_lanes else "") +
        "A1 목소리(배속 구움) · A2 BGM · A3~ 효과음 낱개. 볼륨은 마감 음량 기준으로 클립 Audio Levels 에 들어 있음.\n"
        "전환(렌즈 블러·줌 블러 등)은 XML 에 못 담아 시퀀스 마커로만 표시했다 — 미리보기 mp4 에는 들어 있다.\n", encoding="utf-8", newline="\n")
    log(f"→ {xml}")
    return dict(xml=xml, media=media, master=master, capped_db=capped, premix_lufs=lu, n_out=n_out, plan=plan, n_v1=len(v1), n_v2=len(v2), n_v3=len(v3),
                n_ovl=len(ovls), ovl_tracks=len(ov_lanes), n_sfx=len(au["sfx"]), sfx_tracks=len(lanes), n_flash=len(flashes), n_markers=len(markers))


# ─────────────────────────── verify : XML 만으로 다시 조립 ───────────────────────────

def _fps_of(rate):
    tb = int(rate.findtext("timebase"))
    return tb * 1000 / 1001 if (rate.findtext("ntsc") or "").upper() == "TRUE" else float(tb)


def _path(f, files):
    if f.find("pathurl") is not None:
        files[f.get("id")] = dict(path=urllib.parse.unquote(f.findtext("pathurl")).replace("file://localhost/", ""),
                                  fps=_fps_of(f.find("rate")), w=f.findtext(".//width"), h=f.findtext(".//height"))
    return files[f.get("id")]


def read_xml(xml):
    """XML → dict(fps, W, H, n, v=[[clip…]…], a=[[clip…]…], markers=[(in,out,name)])"""
    seq = ET.parse(xml).getroot().find("sequence")
    fps = _fps_of(seq.find("rate"))
    fmt = seq.find("media/video/format/samplecharacteristics")
    files = {}

    def clip(c):
        fi = _path(c.find("file"), files)
        d = dict(path=fi["path"], frate=fi["fps"], sw=int(fi["w"]) if fi["w"] else None, sh=int(fi["h"]) if fi["h"] else None,
                 s=int(c.findtext("start")), e=int(c.findtext("end")), i=int(c.findtext("in")), o=int(c.findtext("out")),
                 scale=100.0, center=(0.0, 0.0), speed=1.0, level=1.0)
        for eff in c.iter("effect"):
            eid = eff.findtext("effectid")
            for p in eff.iter("parameter"):
                pid = p.findtext("parameterid")
                if eid == "basic" and pid == "scale":
                    d["scale"] = float(p.findtext("value"))
                elif eid == "basic" and pid == "center":
                    d["center"] = (float(p.findtext("value/horiz")), float(p.findtext("value/vert")))
                elif eid == "timeremap" and pid == "speed":
                    d["speed"] = float(p.findtext("value")) / 100.0
                elif eid == "audiolevels" and pid == "level":
                    d["level"] = float(p.findtext("value"))
        return d
    rt = seq.find("rate")
    tb = int(rt.findtext("timebase"))
    out = dict(fps=fps, frs=(f"{tb * 1000}/1001" if (rt.findtext("ntsc") or "").upper() == "TRUE" else str(tb)), W=int(fmt.findtext("width")), H=int(fmt.findtext("height")), n=int(seq.findtext("duration")),
               v=[[clip(c) for c in t.findall("clipitem")] for t in seq.find("media/video").findall("track")],
               a=[[clip(c) for c in t.findall("clipitem")] for t in seq.find("media/audio").findall("track")],
               markers=[(int(m.findtext("in")), int(m.findtext("out")), m.findtext("name")) for m in seq.findall("marker")])
    return out


def _grab(cmd_in, vf, W, H, pix):
    r = subprocess.run(["ffmpeg", "-v", "error", *cmd_in, "-vf", vf, "-frames:v", "1", "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", pix, "-"],
                       capture_output=True).stdout
    ch = 4 if pix == "rgba" else 3
    return np.frombuffer(r, np.uint8).reshape(H, W, ch).astype(np.float32) if len(r) == W * H * ch else None


def _v1_frame(sq, c, j):
    """V1 클립 c 의 시퀀스 프레임 j — 렌더와 같은 필터를, XML 에 적힌 숫자로 다시 짠다."""
    from PIL import Image
    W, H, F = sq["W"], sq["H"], sq["fps"]
    k = c["scale"] / 100.0
    pos = (c["center"][0] * W, c["center"][1] * H)
    cw, ch, x, y = R.geom(c["sw"], c["sh"], W, H, k, pos)
    if Path(c["path"]).suffix.lower() in P.IMG_EXT:
        im = Image.open(c["path"]).convert("RGB")
        return np.asarray(im.resize((cw, ch), Image.LANCZOS).crop((x, y, x + W, y + H))).astype(np.float32)
    fr = sq["frs"]
    m = j - c["s"]
    vf = (f"setpts=(PTS-STARTPTS)/{c['speed']},fps={fr},select=eq(n\\,{m}),scale={cw}:{ch}:flags=bicubic,crop={W}:{H}:{x}:{y},format=rgb24")
    return _grab(["-ss", f"{c['i'] / c['frate']:.6f}", "-i", c["path"], "-an"], vf, W, H, "rgb24")


def _alpha_frame(sq, c, j):
    """알파 층 클립 c 의 시퀀스 프레임 j → RGBA(float, 그 파일 원본 크기)"""
    sw, sh = c["sw"] or sq["W"], c["sh"] or sq["H"]
    n = 0 if Path(c["path"]).suffix.lower() == ".png" else c["i"] + j - c["s"]       # 알파 PNG 한 장은 프레임 0 만 있다
    return _grab(["-i", c["path"]], f"select=eq(n\\,{n}),format=rgba", sw, sh, "rgba")


def verify(xml, preview, log=print):
    """XML 만 읽어 프레임·소리를 다시 조립하고 미리보기 mp4 와 대조한다 (sg_xml_verify 이식).
    화면: 컷/그래픽/자막 경계 근처 포함 여러 프레임의 PSNR (전환 마커 구간은 XML 에 전환이 없으니 건너뜀).
    소리: XML 클립(in/out/start/Audio Levels)대로 섞은 LUFS·최고음 vs 미리보기, 그리고 소리 모양 상관으로 싱크 어긋남(ms).
    → dict(psnr_min, psnr_mean, n_probe, bad, lufs_xml, lufs_prev, peak_xml, lag_ms, corr, missing)"""
    sq = read_xml(xml)
    W, H, F, n = sq["W"], sq["H"], sq["fps"], sq["n"]
    allc = [c for t in sq["v"] for c in t] + [c for t in sq["a"] for c in t]
    missing = sorted({c["path"] for c in allc if not Path(c["path"]).exists()})
    v1 = sorted(sq["v"][0], key=lambda c: c["s"])
    gaps = [(a["e"], b["s"]) for a, b in zip(v1, v1[1:]) if b["s"] != a["e"]]
    log(f"파일 {len({c['path'] for c in allc})}개, 없는 파일 {len(missing)}개, V1 빈틈 {gaps}, 처음 {v1[0]['s']} 끝 {v1[-1]['e']} / 시퀀스 {n}")

    def in_tr(j):
        return any(a - 1 <= j <= b + 1 for a, b, _ in sq["markers"])
    probe = set(int(x) for x in np.linspace(0, n - 1, 12))
    for c in v1:
        probe |= {c["s"] + 3, c["e"] - 3}
    for t in sq["v"][1:]:
        for c in t:
            probe |= {c["s"] + 2, c["s"] + 5}
    probe = sorted(j for j in probe if 0 <= j < n and not in_tr(j))
    ref = {}
    for j in probe:
        ref[j] = _grab(["-i", str(preview)], f"select=eq(n\\,{j})", W, H, "rgb24")
    psn, bad = [], 0
    for j in probe:
        fr = np.zeros((H, W, 3), np.float32)
        for ti, t in enumerate(sq["v"]):
            for c in t:
                if not (c["s"] <= j < c["e"]):
                    continue
                if ti == 0:
                    a = _v1_frame(sq, c, j)
                    if a is not None:
                        fr = a
                else:
                    a = _alpha_frame(sq, c, j)
                    if a is not None and (a.shape[:2] != (H, W) or abs(c["scale"] - 100.0) > 1e-6 or any(abs(v) > 1e-9 for v in c["center"])):
                        u8 = np.clip(fr, 0, 255).astype(np.uint8)            # 크기·위치가 다른 층(오버레이) — 렌더와 같은 comp
                        R.comp(u8, a, cx=W / 2 + c["center"][0] * W, cy=H / 2 + c["center"][1] * H, s=c["scale"] / 100.0)
                        fr = u8.astype(np.float32)
                    elif a is not None:
                        al = a[..., 3:4] / 255
                        fr = fr * (1 - al) + a[..., :3] * al
        if ref[j] is None:
            continue
        mse = ((fr - ref[j]) ** 2).mean()
        p_ = 99.0 if mse < 1e-6 else 10 * np.log10(255 ** 2 / mse)
        psn.append(p_)
        if p_ < 30:
            bad += 1
            log(f"  프레임 {j} ({j / F:.2f}s) PSNR {p_:.1f} dB — 차이 큼")
    log(f"화면: {len(psn)}장 비교(전환 구간 {len(sq['markers'])}곳 제외), PSNR 최저 {min(psn):.1f} dB · 평균 {np.mean(psn):.1f} dB, 30 dB 미만 {bad}장")

    N = int(n / F * SR)
    mix = np.zeros((N + SR, 2), np.float32)
    for t in sq["a"]:
        for c in t:
            r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{c['i'] / F:.6f}", "-t", f"{(c['e'] - c['s']) / F:.6f}", "-i", c["path"], "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                               capture_output=True).stdout
            x = np.frombuffer(r, np.float32).reshape(-1, 2) * c["level"]
            a0 = int(round(c["s"] / F * SR))
            m = min(len(x), len(mix) - a0)
            mix[a0:a0 + m] += x[:m]
    mix = mix[:N]
    tmp = Path(xml).parent / "_xml_verify.wav"
    SFX.write_wav(tmp, mix)
    lu_x, lu_p = R.lufs(tmp), R.lufs(preview)
    peak = 20 * np.log10(np.abs(mix).max() + 1e-9)

    def env(p):
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", "8000", "-f", "f32le", "-"], capture_output=True).stdout
        x = np.frombuffer(r, np.float32)
        k = len(x) // 80
        return 20 * np.log10(np.sqrt((x[:k * 80].reshape(k, 80) ** 2).mean(1)) + 1e-6)
    ea, eb = env(tmp), env(preview)
    m = min(len(ea), len(eb))
    lags = range(-30, 31)
    cc = [np.corrcoef(ea[max(0, l):m + min(0, l)], eb[max(0, -l):m - max(0, l)])[0, 1] for l in lags]
    lag = list(lags)[int(np.argmax(cc))] * 10
    tmp.unlink()
    log(f"소리: XML 조립 {lu_x:.1f} LUFS / 미리보기 {lu_p:.1f} LUFS, XML 최고 {peak:.1f} dBFS · 소리 모양 상관 {max(cc):.3f}, 어긋남 {lag} ms")
    return dict(psnr_min=float(min(psn)), psnr_mean=float(np.mean(psn)), n_probe=len(psn), bad=bad, lufs_xml=lu_x, lufs_prev=lu_p,
               peak_xml=float(peak), lag_ms=lag, corr=float(max(cc)), missing=missing, gaps=gaps)


def main():
    ap = argparse.ArgumentParser(description="배치표 → 프리미어 XML + media/ (선택: 미리보기와 대조)")
    ap.add_argument("plan")
    ap.add_argument("--out")
    ap.add_argument("--미리보기", dest="preview", help="있으면 verify 까지")
    a = ap.parse_args()
    try:
        r = export(a.plan, a.out)
    except P.PlanError as e:
        print(e)
        sys.exit(2)
    if a.preview:
        verify(r["xml"], a.preview)


if __name__ == "__main__":
    main()
