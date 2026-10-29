# -*- coding: utf-8 -*-
r"""7번 7.124~19.136 «다 같은 강남빌딩은 아니에요 → 잘못 산 → 잘 산 → 시세차익» — 자막 밑 카드 한 장 4막 (10-21).

사장님(10-21): «그 화면전체다음에는 자막밑으로 가고싶거든 좋은 제안해봐» → 2안 «2안으로 가고 거기사 잘못산강남빌딩은할때 잘못산거만 포커스되고
  (잘된건 옆으로 밀려 사라지고) 공실에 대출이자에 손해만보고 << 연출하고 / 잘산 강남빌딩은할때는 밀려난 방향에서 빌딩이 다시 밀어내며 들어오면서 설명하는»
  «이거 다 자막밑으로 연출할거야» «딱지 고지서글자 달력숫자 이런거 다 넣어서 만들어줘» «+ 수천만원 이런거 4번영상이랑 너무비슷한데 … 둘이 비슷해보이지않게»
  «도장도 마찬가지고» «이거 시세차익도 수십억씩 얻을 수 있습니다 << 이부분 까지 해주는데 완전 여기까지 전환잘되고 품질높은데 4번이랑은 비슷해보이지않게 만들어줘»
기준 = 7번.prproj 15:05(지시작업/_tmp/story/seq_7번_1505.json): 7.124~14.248 옆모습 카메라 멀티7 · 14.248~ 정면 카메라 · 자막 y 755~818.
장면 scenes/r7g.html · 소재 Codex set19(소재/codex/r7g_bad.png 새로 그린 낡은 빌딩 · r7g_good.png). 납품: V4 연출층(사람 위) · A4~ 효과음.

    python tools/html_motion.py 지시작업/tools/scenes/r7g.html --alpha --settle --fps 59.94 --workers 2 --sub 4 --out 지시작업/_tmp/r7g --name r7g
    python 지시작업/tools/r7g_build.py out
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
DZ = HERE.parent
ROOT = DZ.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE))
import sfx as SFX  # noqa: E402
import r7m_build as M  # noqa: E402   — XML 쓰기는 그대로 빌림

SEQ = DZ / "_tmp/story/seq_7번_1505.json"
SRCS = {"7(대본즉석수정).MP4": (Path(r"D:\26년 10월\261020\7(대본즉석수정).MP4"), 1728, 3072),
        "멀티7(즉석대본수정).MOV": (Path(r"C:\Users\user\Downloads\멀티7(즉석대본수정).MOV"), 2160, 3840)}   # 멀티7 은 회전 −90 → 세로
W, H, FN, FD, FPS = M.W, M.H, M.FN, M.FD, M.FPS
OFF, END_ABS = 7.124, 19.136
END = END_ABS - OFF
WORK = DZ / "_tmp/r7g"
DELIV = DZ / "납품/7번_강남빌딩_잘산못산_시세차익_1021"
NAME = "7번_강남빌딩_잘산못산_시세차익"
SCENE_SFX = ROOT / "소재/효과음/장면음"
# 겹침 0 · 끊김 0(점검표 S5b): 앞 소리의 들리는 끝 ≤ 다음 소리 시작
SFX_LIST = [
    (7.50, "ML_Paper slide.wav", None),                 # 카드 올라옴(→7.92)
    (8.89, "ML_Page forward single chime.wav", None),   # «다 같은» 두 건물에 «강남» 핀(→9.75)
    (10.33, "SEL_ガラスが割れる3.mp3", None),            # «아니에요» «=» 에 빗금 → «≠» 쩍(0.5초 → 10.83)
    (10.86, "휙２.mp3", None),                           # «잘못 산» 잘 산 빌딩 밀려 나감(→11.25)
    (12.26, "ML_Newspaper falling to the floor.wav", None),  # «공실에» 딱지 착착(→12.63)
    (12.70, "ML_Paper slide.wav", None),                # «대출이자에» 연체 안내 철썩(→13.12)
    (13.347, "쿠궁_짧게.wav", None),                     # «손해만 보고» 쿠궁(0.85초로 줄여 자연 감쇠 → 14.20)
    (14.25, "휙２.mp3", None),                           # «잘 산» 다시 밀고 들어옴(→14.68)
    (15.38, "월세알림_연속.wav", -7),                    # «매달 수천만 원» 달력 넘김마다 알림(한 파일 → 16.61)
    (16.80, "SEL_ゲージ回復1.mp3", None),                # «시세차익도» 빌딩이 줄며 곡선이 오름(1.27초 → 18.07)
    (18.085, "SEL_キラッ1.mp3", None),                   # «얻을 수 있습니다» 시세차익 괄호(→19.00)
]
FLIP = [0.24, 0.44, 0.61, 0.76, 0.89]                    # 장면 r7g.html FLIP[1..] − T.cal


def make_bundles():
    SR = SFX.SR
    k = SFX.load(SFX.find_file("쿠궁.mp3"))
    a = np.abs(k).max(1)
    k = k[int(np.argmax(a > a.max() * 10 ** (-40 / 20))):][: int(.85 * SR)].copy()
    fo = int(.5 * SR)
    k[-fo:] *= (np.linspace(1, 0, fo) ** 1.6)[:, None]
    SFX.write_wav(SCENE_SFX / "쿠궁_짧게.wav", k)
    c = SFX.load(SFX.find_file("채팅 효과음.mp3"))
    a = np.abs(c).max(1)
    c = c[int(np.argmax(a > a.max() * 10 ** (-40 / 20))):]
    c = c[: int(.36 * SR)]
    out = np.zeros((int((FLIP[-1] + .4) * SR), 2))
    for f in FLIP:
        s = int(f * SR)
        out[s:s + len(c)] += c[: len(out) - s]
    SFX.write_wav(SCENE_SFX / "월세알림_연속.wav", out * min(1, .9 / (np.abs(out).max() + 1e-9)))


def seq_items():
    d = json.loads(SEQ.read_text(encoding="utf-8"))
    return [i for i in d["items"] if i["t1"] > OFF + 1e-3 and i["t0"] < END_ABS - 1e-3]


def build_base():
    """사장님 15:05 컷 그대로(V1 사람 · A1 목소리 +6dB) — 미리보기용."""
    segs = []
    for it in sorted((i for i in seq_items() if i["track"] == "V1" and i["name"] in SRCS), key=lambda i: i["t0"]):
        src, dw, dh = SRCS[it["name"]]
        mo = next((f["params"] for f in it.get("fx", []) if f.get("name") == "모션"), {})
        sc = float(mo.get("비율 조정", 100)) / 100
        px, py = (float(v) for v in mo.get("위치", "0.5:0.5").split(":"))
        a, b = max(it["t0"], OFF), min(it["t1"], END_ABS)
        sw, sh = round(dw * sc / 2) * 2, round(dh * sc / 2) * 2
        p = WORK / f"seg_{len(segs):02d}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{it['s0'] + a - it['t0']:.4f}", "-t", f"{b - a:.4f}", "-i", str(src), "-filter_complex",
                        f"[0:v]fps={FN}/{FD},scale={sw}:{sh},format=yuv420p[s];color=black:s={W}x{H}:r={FN}/{FD}[k];[k][s]overlay=x={round(px * W - sw / 2)}:y={round(py * H - sh / 2)}:shortest=1[v]",
                        "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "16", str(p)], check=True)
        segs.append(p)
    lst = WORK / "segs.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in segs), encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(WORK / "base_v.mp4")], check=True)
    SR = SFX.SR
    voice = np.zeros((int(END * SR) + SR, 2))
    for it in (i for i in seq_items() if i["track"] == "A1"):
        a, b = max(it["t0"], OFF), min(it["t1"], END_ABS)
        tmp = WORK / "a.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{it['s0'] + a - it['t0']:.4f}", "-t", f"{b - a:.4f}", "-i", str(SRCS['7(대본즉석수정).MP4'][0]),
                        "-vn", "-ac", "2", "-ar", str(SR), str(tmp)], check=True)
        x = SFX.load(tmp) * 10 ** (6 / 20)
        s = int((a - OFF) * SR)
        voice[s:s + len(x)] += x[: len(voice) - s]
    return voice[: int(END * SR)]


def out():
    import rule_check as RC
    WORK.mkdir(parents=True, exist_ok=True)
    make_bundles()
    media = DELIV / "media"
    media.mkdir(parents=True, exist_ok=True)
    ov = media / "연출층_강남빌딩_잘산못산.mov"
    try:
        shutil.copy2(WORK / "r7g.mov", ov)
    except PermissionError:
        ov = media / "연출층_강남빌딩_잘산못산_새판.mov"
        shutil.copy2(WORK / "r7g.mov", ov)
        print("  [잠김] 새 판", ov.name)
    voice = build_base()
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
        placed.append(dict(t=max(0, t - OFF - SFX.attack_at(x)), x=x, name=name, label=f"{name}@{t:.2f}"))
    for lv, rule, msg in SFX.fit_tails(placed):
        print(f"  [{lv}] {rule}: {msg}")
    RC.report(RC.check_sfx([(p["t"], p["name"], len(p["x"]) / SR) for p in placed], END), path=WORK / "점검_효과음.txt", title="r7g")
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
    # 미리보기 자막(사장님 V2 흉내 — 흰 글 검은 상자, y 787)
    caps = [(max(i["t0"], OFF), min(i["t1"], END_ABS), " ".join(i["text"])) for i in seq_items() if i["track"] == "V2" and i.get("text")]
    font = ImageFont.truetype(str(ROOT / "소재/fonts/gmarket-sans/GmarketSansMedium.ttf"), 62)
    ins, fc, last = ["-i", str(WORK / "base_v.mp4"), "-i", str(ov)], ["[0:v][1:v]overlay=format=auto[o0]"], "o0"
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
    M.OFF, M.END, M.DELIV, M.NAME = OFF, END, DELIV, NAME
    M.write_xml(placed, ov)
    print("미리보기", prev)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    {"out": out}[sys.argv[1]]()
