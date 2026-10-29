# -*- coding: utf-8 -*-
r"""애펙 장면 렌더 · 소리 섞기 · 납품 XML 틀 (한비즈 쇼츠).

[이식본 — 원본 D:/영상제작/도구/광고편집/bisa_web_vs_instant.py 의 «틀» 부분(조각 저장·겹침 검사·AfterFX 감시 실행·voice·sfx).
 빡이사 06 전용 상수(드롭다운 좌표·판 크기·SEGS·EVENTS)는 전부 매개변수로 바꿨다. 장면 모양은 examples/ 의 본보기를 보고 새로 짠다.]

장면 도구 한 개의 뼈대
    import ae_scene as M, sfx as SFX, words
    M.configure(work=..., out=..., sfx_dir=...)             # 필요할 때만 (기본: config 의 _tmp/ae · 납품 · _tmp/sfx)

    # ① 조각: PIL 로 레이어 PNG 를 만들며 M.save(name, im, (x, y)) — 실제 픽셀 상자가 M.BOX 에 쌓인다
    # ② 겹침 검사: M.check_boxes(panel=(x0,y0,x1,y1), keepout={"사람": (...), "자막": (...)})   ← 렌더 전에 멈춘다
    # ③ 애펙: JSX 본문을 문자열로 만들고(M.comp_open … M.comp_close) M.render(jsx, 출력.mp4)
    # ④ 소리: M.mix_sfx(...)  → 미리보기.mp4 + 효과음 wav 낱개 + 효과음 XML (규칙 점검기 rule_check.check_sfx 를 통과해야 섞는다)

시각은 «시퀀스 초» 로 받고 JSX 안에서는 s(t) = t − T0 (장면 시작 기준)로 바꿔 건다.
함정: 애펙 «충돌 복구 옵션» 창이 AfterFX -r 를 막는다 → run_ae_guarded 가 지켜보고 Enter 를 넣는다(references/motion-graphics.md).
"""
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import config as C
import lec_xml
import rf3_ae as AE
import rule_check
import sfx as SFX

W, H, FPS = C.W, C.H, C.FPS
WORK = C.WORK / "ae"
OUT = C.OUT
SFX_DIR = C.WORK / "sfx"
BOX = {}                      # 레이어 이름 → 화면에서 실제로 차지하는 픽셀 상자, 이름+"@" → (x, y, w, h) 이미지 자리


def configure(size=None, fps=None, work=None, out=None, sfx_dir=None):
    """모듈 설정을 바꾼다(장면 도구 맨 위에서 한 번)."""
    global W, H, FPS, WORK, OUT, SFX_DIR
    if size:
        W, H = size
        lec_xml.SEQ_W, lec_xml.SEQ_H = W, H
    if fps:
        FPS = fps
    if work:
        WORK = Path(work)
    if out:
        OUT = Path(out)
    if sfx_dir:
        SFX_DIR = Path(sfx_dir)


# ── PIL 조각 ──────────────────────────────────────────────────
def font(n, f=None):
    return ImageFont.truetype(str(f or C.FONTS["pretendard_bold"]), n)


def tlen(t, f):
    return ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(t, font=f)


def save(name, im, xy):
    """레이어 PNG 저장 + 실제 픽셀(알파 > 60) 상자를 BOX 에 기록."""
    WORK.mkdir(parents=True, exist_ok=True)
    xy = (int(round(xy[0])), int(round(xy[1])))
    im.save(WORK / f"{name}.png")
    a = np.array(im)[..., 3] > 60
    ys, xs = np.where(a)
    BOX[name] = (int(xy[0] + xs.min()), int(xy[1] + ys.min()), int(xy[0] + xs.max()), int(xy[1] + ys.max()))
    BOX[name + "@"] = (int(xy[0]), int(xy[1]), im.width, im.height)


def shadowed(w, h, r, fill, pad=24, alpha=70):
    """그림자 달린 둥근 카드 한 장."""
    im = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 6, pad + w, pad + h + 6), r, fill=(10, 30, 70, alpha))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(im).rounded_rectangle((pad, pad, pad + w, pad + h), r, fill=fill)
    return im


def overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def inside(a, b, m=0):
    return a[0] >= b[0] + m and a[1] >= b[1] + m and a[2] <= b[2] - m and a[3] <= b[3] - m


def check_boxes(content=None, panel=None, panel_margin=20, keepout=None, edge=15, skip=()):
    """렌더 전 겹침 자동 검사(사장님 10-02 «레이아웃 겹침 없었으면»). 하나라도 걸리면 SystemExit.
      content  검사할 레이어 이름들(기본: BOX 의 전부 − skip)
      panel    (x0,y0,x1,y1) 판 — 내용은 판 안쪽 panel_margin 이상 들어가 있어야 한다
      keepout  {이름: (x0,y0,x1,y1)} 비워 둘 곳(사람 자리·자막 자리·벽 글씨 …) — 세로 쇼츠 값은 첫 작업 때 재서 채운다
      edge     화면 가장자리 여유
    같은 자리에서 시간이 달라 겹치지 않는 것(예: 인스턴트 카드가 나온 뒤 웹사이트 칸이 흐려짐)은 skip 으로 빼거나 장면 도구에서 시각별로 따로 잰다."""
    names = [n for n in (content or BOX) if not n.endswith("@") and n not in skip]
    bad = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if overlap(BOX[a], BOX[b]):
                bad.append(f"{a} {BOX[a]} ↔ {b} {BOX[b]}")
    if panel:
        for n in names:
            if not inside(BOX[n], panel, panel_margin):
                bad.append(f"{n} {BOX[n]} 판 밖")
    for n in names:
        for zn, z in (keepout or {}).items():
            if overlap(BOX[n], z):
                bad.append(f"{n} {BOX[n]} ↔ {zn}")
        x0, y0, x1, y1 = BOX[n]
        if x0 < edge or y0 < edge or x1 > W - edge or y1 > H - edge:
            bad.append(f"{n} {BOX[n]} 화면 밖")
    if bad:
        raise SystemExit("레이아웃 겹침:\n  " + "\n  ".join(bad))
    print("겹침 없음")


# ── 애펙 JSX 조각 ─────────────────────────────────────────────
# eo: 빠르게 들어와 감속해 멈춘다(영상미 원칙 3). 위치(공간 속성)는 ease 가 1개라 n=1 로 — 안 그러면 «setTemporalEaseAtKey 배열 요소 1개» 오류.
EO_JS = ("function eo(p){ for(var k=1;k<=p.numKeys;k++){ var n=p.isSpatial?1:(p.value.length||1), o=[], i=[]; "
         "for(var j=0;j<n;j++){ o.push(new KeyframeEase(0,0.1)); i.push(new KeyframeEase(0,85)); } p.setTemporalEaseAtKey(k,i,o); } }")
HOLD_JS = "function hold(p){ for(var q=1;q<=p.numKeys;q++){ p.setInterpolationTypeAtKey(q,KeyframeInterpolationType.HOLD); } }"


def comp_open(name, dur, motion_blur=True):
    """컴프 하나를 여는 JSX 첫 줄. 본문은 변수 comp 에 레이어를 얹는다. comp_close 로 닫는다."""
    mb = " comp.motionBlur=true; comp.shutterAngle=180;" if motion_blur else ""
    return f"(function(){{ var comp=app.project.items.addComp('{name}',{W},{H},1,{dur:.3f},{FPS});{mb}"


def comp_close(out_mov=None, tag="scene"):
    """렌더 큐에 넣고 로그에 ok 를 쓴다. out_mov 를 안 주면 render() 가 읽는 WORK/a.mov."""
    out_mov = out_mov or (WORK / "a.mov")
    return (f"var rq=app.project.renderQueue.items.add(comp); var om=rq.outputModule(1); "
            f"om.applyTemplate({AE.js(C.AE_RENDER_TEMPLATE)}); om.file=new File({AE.js(str(out_mov))});\n"
            f"log('ok {tag}'); }})();")


def run_ae_guarded(jf, logf, aep):
    """AfterFX -r 를 띄우고 지켜본다(10-07 밤 14·15 에서 두 번 멈춤).
    ① 20초 넘게 로그가 안 생기면 «충돌 복구 옵션» 창 → 애펙 창에 Enter(«계속»), 25초마다 다시
    ② 로그가 ok/ERR 이고 프로젝트가 저장됐는데 20초 넘게 안 닫히면 → 강제 종료(렌더는 aerender 로 따로 하므로 손실 없음)"""
    proc = subprocess.Popen([str(AE.AE_DIR / "AfterFX.exe"), "-r", str(jf)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0, done_at, pressed = time.time(), None, 0
    while proc.poll() is None and time.time() - t0 < 900:
        time.sleep(3)
        txt = logf.read_text(errors="ignore") if logf.exists() else ""
        if not txt and time.time() - t0 > 20 + pressed * 25 and pressed < 20:
            subprocess.run(["powershell", "-NoProfile", "-Command",
                            "$ws=New-Object -ComObject WScript.Shell; foreach($p in (Get-Process AfterFX -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 })){ if($ws.AppActivate($p.Id)){ Start-Sleep -Milliseconds 700; $ws.SendKeys('{ENTER}') } }"],
                           capture_output=True)
            pressed += 1
            print("애펙 응답 없음 → 충돌 복구 창으로 보고 Enter(계속)")
        if ("ok" in txt or "ERR" in txt) and aep.exists():
            done_at = done_at or time.time()
            if time.time() - done_at > 20:
                subprocess.run(["taskkill", "/F", "/IM", "AfterFX.exe"], capture_output=True)
                subprocess.run(["taskkill", "/F", "/IM", "AfterFX.com"], capture_output=True)
                print("애펙이 스크립트 끝난 뒤 안 닫힘 → 강제 종료(다음 실행 때 충돌 복구 창은 ①이 넘김)")
                break
    if proc.poll() is None:
        proc.kill()


def render(jsx_comp, dst_mp4, crf=14):
    """jsx_comp = comp_open … comp_close 로 만든 JSX 본문. JSX 작성 → AfterFX -r(감시) → aerender → ffmpeg mp4(소리 없음).
    렌더 중간물은 WORK 안 a.aep · a.jsx · a.mov · log.txt (다시 만들 수 있는 것)."""
    WORK.mkdir(parents=True, exist_ok=True)
    aep, jf, logf, mov = WORK / "a.aep", WORK / "a.jsx", WORK / "log.txt", WORK / "a.mov"
    for f in (logf, aep, mov):
        if f.exists():
            f.unlink()
    body = [AE.HEAD.replace("%LOG%", AE.js(str(logf))), EO_JS, HOLD_JS, "app.newProject();",
            "try{" + jsx_comp + "}catch(e){ log('ERR '+e.toString()+' line '+e.line); }",
            f"app.project.save(new File({AE.js(str(aep))})); LOG.close(); app.quit();"]
    jf.write_text("\n".join(body), encoding="ascii")        # 한글은 \uXXXX 로 — JSX 는 ASCII 로 쓴다(AE.js 가 이스케이프)
    t0 = time.time()
    run_ae_guarded(jf, logf, aep)
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
    dst = Path(dst_mp4)
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mov), "-c:v", "libx264", "-crf", str(crf), "-preset", "slow",
                    "-pix_fmt", "yuv420p", "-an", str(dst)], check=True)
    return dst


# ── 목소리 · 사람 미리보기 ───────────────────────────────────
def voice(segs, src):
    """사장님 컷 조각대로 이어 붙인 목소리(스테레오 float). segs = [(시퀀스 시작, 시퀀스 끝, src 안 시작초), …]"""
    parts = []
    for ta, tb, cs in segs:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{cs}", "-t", f"{tb - ta}", "-i", str(src), "-vn",
                              "-af", "aresample=48000,aformat=sample_fmts=flt:channel_layouts=stereo", "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.float32).reshape(-1, 2)
        n = int(round((tb - ta) * SFX.SR))
        parts.append(np.pad(x, ((0, max(0, n - len(x))), (0, 0)))[:n])
    return np.concatenate(parts).copy()


def cam_preview(segs, src, dst, size=(1152, 648)):
    """사람 PIP 미리보기용: 사장님 컷대로 이어 붙인 사람 영상(소리 없음)."""
    fc, ins = [], []
    for i, (ta, tb, cs) in enumerate(segs):
        ins += ["-ss", f"{cs}", "-t", f"{tb - ta:.3f}", "-i", str(src)]
        fc.append(f"[{i}:v]scale={size[0]}:{size[1]},fps=30,setpts=PTS-STARTPTS[v{i}]")
    fc.append("".join(f"[v{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=0[o]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[o]",
                    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(dst)], check=True)


# ── 효과음 섞기 · 미리보기 · XML ─────────────────────────────
def mix_sfx(scene, name, t0, t1, events, snd_fix, v, tracks=(1, 2), cam=None, pip=None, tag="sc", voice_db=7, seq_fps=None):
    """효과음을 목소리 대비 크기로 다듬어 놓고, 규칙 점검을 통과하면 합본·미리보기·XML 을 낸다.
      scene     장면 mp4 (render() 결과)       name  납품 이름(예: "03_가격비교") — 같은 이름 제자리 덮어쓰기
      t0, t1    장면의 시퀀스 시작·끝 초       events  [(시퀀스 초, 역할 이름), …]
      snd_fix   {역할: (파일 이름, 최소 길이초, 기본 상대dB, "onset"|"peak")}   (파일별 크기 FILE_DB 가 우선)
      v         voice() 결과                    tracks  (장면 V 트랙, 효과음 시작 A 트랙)
      cam, pip  사람 미리보기 mp4 와 (중심x, 중심y, 폭, 높이) — 없으면 장면 + 소리만
      voice_db  미리보기에서 목소리·효과음에 같이 거는 dB (사장님 타임라인 목소리가 +7dB 였다. 세로 쇼츠 값은 첫 작업 때 확인)
    돌려주는 값: 미리보기 mp4 경로. 소리는 귀로 못 들으니 «못 들었다»고 보고한다."""
    dur = t1 - t0
    snd = {k: SFX.role(SFX.by_name(f), mx, rel, al) for k, (f, mx, rel, al) in snd_fix.items()}
    SFX.SND.clear()
    SFX.SND.update(snd)
    ref = SFX.voice_ref_from(v)
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    cache, placed, mix = {}, [], np.zeros_like(v)
    for k, (t, nm) in enumerate(events):
        if nm not in cache:
            cache[nm] = SFX.prep(nm, ref)
        x, peak_at = cache[nm]
        start = t - (peak_at if snd[nm][5] == "peak" else 0.0)
        fp = SFX_DIR / f"{k + 1:02d}_{nm}.wav"                 # 같은 이름 제자리 덮어쓰기(폴더·파일을 지우지 않는다)
        SFX.write_wav(fp, x)
        placed.append((round(start, 3), fp, nm))
        i = int((start - t0) * SFX.SR)
        seg = x[: len(mix) - i]
        mix[i: i + len(seg)] += seg
        print(f"  {start:6.2f}s  {nm:6s} [{snd[nm][6]}] {snd[nm][0].name}  {snd[nm][4]:+d}dB")
    errs = [it for it in rule_check.check_sfx([(t - t0, snd[n][0], len(cache[n][0]) / SFX.SR) for t, _, n in placed], dur) if it[0] == "ERROR"]
    for it in errs:
        print(*it)
    if errs:
        raise SystemExit("효과음 규칙 위반(5-2/5-2b/5-3) — events 를 고친 뒤 다시")
    SFX.write_wav(SFX_DIR / f"00_효과음만_합본_{t0:.2f}~.wav", mix)
    g = 10 ** (voice_db / 20)
    both = v * g + mix * g
    both *= min(1.0, 0.8 / (np.abs(both).max() + 1e-9))
    tmp = SFX_DIR / "_미리듣기소리.wav"
    SFX.write_wav(tmp, both)
    pre = OUT / f"{name}_미리보기.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(scene)]
    if cam and pip:
        cx, cy, pw, ph = pip
        cmd += ["-i", str(cam), "-i", str(tmp), "-filter_complex", f"[0:v][1:v]overlay={cx - pw / 2:.0f}:{cy - ph / 2:.0f}[v]", "-map", "[v]", "-map", "2:a"]
    else:
        cmd += ["-i", str(tmp), "-map", "0:v", "-map", "1:a"]
    cmd += ["-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-af", "alimiter=limit=0.84:level=false", "-c:a", "aac", "-b:a", "256k", "-shortest", str(pre)]
    subprocess.run(cmd, check=True)
    tmp.unlink()
    lec_xml.V_TRACK, lec_xml.A_TRACK = tracks
    print(lec_xml.write(OUT / f"{name}_효과음.xml", name, scene, dur, t0, [(t, f) for t, f, _ in placed], seq_fps or FPS, tag=tag))
    return pre
