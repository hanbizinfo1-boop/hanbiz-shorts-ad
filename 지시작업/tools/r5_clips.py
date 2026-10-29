# -*- coding: utf-8 -*-
r"""R5+R6(«제조업 아니라고 … 전부 가능합니다», 9.0~13.333초) 후보 A·B·C 를 사람·자막·목소리·BGM·효과음과 합친 짧은 클립 + 나란히 보기.

    python 지시작업/tools/r5_clips.py      # html_motion 으로 지시작업/_tmp/r5/r5_X.mov 를 먼저 렌더(--frames 270:400)
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DZ = HERE.parent
ROOT = DZ.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE))
import ad_build as AB  # noqa: E402

T0, T1 = 9.0, 13.333
OUT = DZ / "납품/후보_넘기려고+위탁생산_1014"
WORK = DZ / "_tmp/r5"
NAMES = {"A": "A_휴대폰피드", "B": "B_지나치다돌아봄", "C": "C_책자넘김"}
EXTRA = {"fill": ("SEL_ゲージ回復1.mp3", "peak", -12, -0.40), "mark": ("ML_Paper slide.wav", "peak", -11),
         "mark2": ("SEL_油性マーカーで字を書く.mp3", "peak", -12, -0.35), "tap": ("SEL_決定ボタンを押す4.mp3", "peak", -9)}


def seg_wav(src, out, gain=0.0):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{T0}", "-t", f"{T1 - T0:.3f}", "-i", str(src), "-af", f"volume={gain}dB",
                    "-ar", "48000", "-ac", "2", str(out)], check=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    seg_wav(AB.WORK / "voice.wav", WORK / "voice_seg.wav")
    seg_wav(AB.BGM, WORK / "bgm_seg.wav")
    caps = json.loads((AB.WORK / "captions.json").read_text(encoding="utf-8"))
    cuts = []
    for c in AB.items("V1"):
        a, b = max(c["t0"], T0), min(c["t1"], T1)
        if b - a > 1e-3:
            cuts.append({"src": str(AB.SRC), "in": round(c["s0"] + a - c["t0"], 4), "out": round(c["s0"] + b - c["t0"], 4),
                         "start": round(a - T0, 4), "end": round(b - T0, 4), "cont": bool(cuts)})
    ccaps = [{"text": c["text"], "start": round(max(c["start"], T0) - T0, 3), "end": round(min(c["end"], T1) - T0, 3),
              "emph": c["emph"], "emph_color": "y", "anim": "none"} for c in caps if c["end"] > T0 and c["start"] < T1]
    roles = dict(AB.ROLES, **EXTRA)
    outs = []
    for v, name in NAMES.items():
        ev = json.loads((WORK / f"r5_{v}_events.json").read_text(encoding="utf-8"))["events"]
        sfx = [{"t": round(e["t"] - T0, 3), "role": e["role"]} for e in ev if e["role"] in roles]
        used = {s["role"] for s in sfx}
        p = {"name": name, "base_dir": str(ROOT), "seq": {"w": 1080, "h": 1920, "fps": 30}, "speed": 1.0, "loudness_lufs": -14,
             "voice": {"file": str(WORK / "voice_seg.wav"), "start": 0.0},
             "bgm": {"file": str(WORK / "bgm_seg.wav"), "start": 0.0, "gain_db": AB.BGM_DB, "fade_out": 0.2},
             "caption_style": AB.CAP_STYLE, "cuts": cuts, "captions": ccaps, "graphics": [],
             "overlays": [{"file": str(WORK / f"r5_{v}.mov"), "t0": 0.0, "t1": round(T1 - T0, 3), "name": f"후보{v}"}],
             "sfx_roles": {r: {"file": x[0], "align": x[1] or "peak", "exact_db": x[2], **({"min_len": x[3]} if len(x) > 3 else {})}
                           for r, x in roles.items() if r in used},
             "sfx": sfx}
        pp = WORK / f"plan_{v}.json"
        pp.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
        mp4 = OUT / f"{name}.mp4"
        r = subprocess.run([sys.executable, str(ROOT / "tools/edit_render.py"), str(pp), "--out", str(mp4), "--무시"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(name, "ERROR" if r.returncode else "ok", [l for l in r.stdout.splitlines() if "규칙 점검" in l or "트루피크" in l])
        outs.append(mp4)
    # 나란히 보기(각 540 폭 + 라벨)
    font = str(ROOT / "소재/fonts/pretendard/Pretendard-Black.otf").replace("\\", "/").replace(":", "\\:")
    fl = []
    for i, v in enumerate(NAMES):
        fl.append(f"[{i}:v]scale=540:960,drawtext=fontfile='{font}':text='{v}':x=24:y=20:fontsize=70:fontcolor=yellow:borderw=5:bordercolor=black[v{i}]")
    fc = ";".join(fl) + ";[v0][v1][v2]hstack=3[v]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *sum([["-i", str(o)] for o in outs], []), "-filter_complex", fc,
                    "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    str(OUT / "후보_ABC_나란히.mp4")], check=True)
    print("→", OUT)


if __name__ == "__main__":
    main()
