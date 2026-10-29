# -*- coding: utf-8 -*-
r"""사장님 프리미어 시퀀스의 소리 크기 점검 — 볼륨값을 그대로 적용해 다시 섞고, 클립마다 «목소리 대비 몇 dB»를 잰다 (10-20).

사장님(10-20): «지금 볼륨이 따로노는 느낌인데 한번 점검해줄래 완성은했는데 볼륨이 서로 안맞는느낌?»
볼륨 저장값 0dB = 0.17783(sfx.ZERO_DB). 클립 볼륨 «레벨» × 채널 볼륨(왼쪽) 을 곱해 적용. 중첩 시퀀스는 안까지 풀어서 잰다.
잣대: 목소리 = 말소리 50ms RMS 중앙(sfx.voice_ref_from). 효과음 = 50ms RMS 최대 − 목소리 기준.

    python 지시작업/tools/mix_audit.py <사본.prproj> <시퀀스이름> [중첩시퀀스이름 …] [--fix]
"""
import gzip
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DZ = HERE.parent
ROOT = DZ.parent
sys.path.insert(0, str(ROOT / "tools"))
import sfx as SFX  # noqa: E402

SR = SFX.SR
VOICE_TRACKS = {"A1"}


def gain_of(it):
    g = 1.0
    for f in it.get("fx", []):
        p = f.get("params", {})
        for k in ("레벨", "왼쪽"):
            if k in p:
                try:
                    g *= float(p[k]) / SFX.ZERO_DB
                except ValueError:
                    pass
    return g


def read_seq(prproj, name):
    out = DZ / "_tmp/story" / f"audit_{abs(hash(name)) % 10**6}.json"
    subprocess.run([sys.executable, str(ROOT / "tools/read_prproj.py"), str(prproj), name, str(out)], check=True, capture_output=True)
    return json.loads(out.read_text(encoding="utf-8"))["items"]


def paths_of(prproj):
    s = gzip.open(prproj).read().decode("utf-8", "ignore")
    ps = sorted(set(re.findall(r"<ActualMediaFilePath>([^<]+)</ActualMediaFilePath>", s)))
    by = {}
    for p in ps:
        by.setdefault(Path(p).name, []).append(Path(p))
    return by


def deliv_starts():
    """납품 XML 들에서 (시퀀스 초, 파일) — 같은 이름 SFX_01_… 이 여러 폴더에 있을 때 자리로 고른다."""
    res = []
    for x in (DZ / "납품").glob("*/*.xml"):
        s = x.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"<start>(\d+)</start><end>\d+</end>.*?<pathurl>([^<]+)</pathurl>", s, re.S):
            import urllib.parse
            p = urllib.parse.unquote(m.group(2).replace("file://localhost/", ""))
            res.append((int(m.group(1)) * 1001 / 60000, Path(p)))
    return res


def resolve(it, by, starts, t_abs):
    c = by.get(it["name"], [])
    if len(c) == 1:
        return c[0]
    if c:
        near = [(abs(t - t_abs), p) for t, p in starts if p.name == it["name"] and p in c]
        if near:
            return min(near)[1]
        return c[0]
    return None


def clip_audio(path, s0, dur):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{s0:.4f}", "-t", f"{dur:.4f}", "-i", str(path), "-vn",
                          "-af", "aresample=48000,aformat=sample_fmts=flt:channel_layouts=stereo", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def main():
    args = [a for a in sys.argv[1:] if a != "--fix"]
    prproj, seq, nests = Path(args[0]), args[1], args[2:]
    by, starts = paths_of(prproj), deliv_starts()
    items = [dict(it, t_off=0.0, g_par=1.0, via="") for it in read_seq(prproj, seq) if it["track"].startswith("A")]
    flat = []
    for it in items:
        if it["name"] in nests:   # 중첩 시퀀스 — 안의 클립을 바깥 시각·볼륨으로
            for sub in read_seq(prproj, it["name"]):
                if sub["track"].startswith("A") and sub["t1"] > it["s0"] and sub["t0"] < it["s1"]:
                    flat.append(dict(sub, t0=sub["t0"] - it["s0"] + it["t0"], t1=sub["t1"] - it["s0"] + it["t0"],
                                     g_par=gain_of(it), via=it["name"], track=it["track"]))
        else:
            flat.append(it)
    total = max(i["t1"] for i in flat) + 1
    voice = np.zeros((int(total * SR), 2), np.float32)
    rows = []
    for it in flat:
        p = resolve(it, by, starts, it["t0"])
        if p is None or not p.exists():
            rows.append((it, None, "파일 없음"))
            continue
        x = clip_audio(p, it["s0"], it["t1"] - it["t0"]) * gain_of(it) * it.get("g_par", 1.0)
        it["x"], it["path"] = x, p
        if it["track"] in VOICE_TRACKS:
            a = int(it["t0"] * SR)
            voice[a:a + len(x)] += x[: len(voice) - a]
    ref = SFX.voice_ref_from(voice)
    print(f"목소리 기준(말소리 50ms RMS 중앙) {ref:.1f} dBFS\n")
    print("■ 목소리 클립별(말소리 중앙, 기준 대비)")
    for it in flat:
        if it["track"] in VOICE_TRACKS and "x" in it:
            f = SFX.rms_frames(it["x"])
            v = float(np.median(f[f > f.max() - 25])) if len(f) else -99
            flag = "  ◀ 튐" if abs(v - ref) > 2.5 else ""
            print(f"  {it['t0']:6.2f}~{it['t1']:6.2f}  {v - ref:+5.1f} dB  (볼륨 {20 * np.log10(gain_of(it)):+.1f}){flag}")
    print("\n■ 효과음·기타(최대 50ms RMS − 목소리 기준)")
    out = []
    for it in sorted(flat, key=lambda i: i["t0"]):
        if it["track"] in VOICE_TRACKS:
            continue
        if "x" not in it:
            print(f"  {it['t0']:6.2f}  {it['name']}  — 파일 못 찾음")
            continue
        rel = float(SFX.rms_frames(it["x"]).max()) - ref
        pk = 20 * np.log10(np.abs(it["x"]).max() + 1e-9)
        out.append((it, rel, pk))
        vol = 20 * np.log10(gain_of(it) * it.get("g_par", 1.0))
        flag = "  ◀ 기준 " + f"{target_of(it['name']):+d}" if abs(rel - target_of(it["name"])) > 3 else ""
        print(f"  {it['t0']:6.2f} {it['track']:3} {rel:+5.1f} dB{flag}  피크 {pk:+5.1f} dBFS  볼륨 {vol:+5.1f}  {it['name']}{'  (중첩 ' + it['via'] + ')' if it['via'] else ''}")
    rels = np.array([r for _, r, _ in out])
    if len(rels):
        print(f"\n효과음 목소리 대비: 중앙 {np.median(rels):+.1f} · 최소 {rels.min():+.1f} · 최대 {rels.max():+.1f} · 폭 {rels.max() - rels.min():.1f} dB")
    mix = voice.copy()
    for it, _, _ in out:
        a = int(it["t0"] * SR)
        mix[a:a + len(it["x"])] += it["x"][: len(mix) - a]
    print(f"합친 소리 피크 {20 * np.log10(np.abs(mix).max() + 1e-9):+.1f} dBFS")
    SFX.write_wav(DZ / "_tmp/story/audit_mix.wav", mix * min(1, .99 / (np.abs(mix).max() + 1e-9)))
    if FIX:
        fix(flat, ref, total)


# --fix: 점검 결과대로 고쳐 다시 섞음 — 목소리 클립은 LUFS 를 가운데 값에 맞추고(±8dB 까지),
# 효과음은 종류별 목소리 대비(타격 −2 · 휙 −5 · 반짝·틱 −7)로. 효과음 묶음엔 로우컷·고음 −3dB·작은 방 울림(목소리와 같은 공간),
# 마스터는 가벼운 컴프 → −14 LUFS · 트루피크 −1.5dB.
FIX = "--fix" in sys.argv


def target_of(name):
    return SFX.ad_target(name)   # 타격 −2 · 휙 −5 · 작은 소리 −7 (sfx.AD_LEVEL — 10-20 사장님 «이 데시벨» 학습)


def fix(flat, ref, total):
    import pyloudnorm as pyln
    meter = pyln.Meter(SR)
    vs = [i for i in flat if i["track"] in VOICE_TRACKS and "x" in i and len(i["x"]) > SR * .5]
    for i in vs:
        i["lufs"] = meter.integrated_loudness(i["x"].astype(np.float64))
    mid = float(np.median([i["lufs"] for i in vs]))
    voice = np.zeros((int(total * SR), 2), np.float32)
    bus = np.zeros_like(voice)
    print(f"\n■ 고친 값 (목소리 가운데 {mid:.1f} LUFS)")
    for i in sorted(flat, key=lambda i: i["t0"]):
        if "x" not in i:
            continue
        a = int(i["t0"] * SR)
        if i["track"] in VOICE_TRACKS:
            d = float(np.clip(mid - i["lufs"], -8, 8)) if "lufs" in i else 0.0
            voice[a:a + len(i["x"])] += i["x"][: len(voice) - a] * 10 ** (d / 20)
            if abs(d) >= 1.5:
                print(f"  목소리 {i['t0']:6.2f}  {d:+.1f} dB")
        else:
            rel = float(SFX.rms_frames(i["x"]).max()) - ref
            d = target_of(i["name"]) - rel
            bus[a:a + len(i["x"])] += i["x"][: len(bus) - a] * 10 ** (d / 20)
            print(f"  효과음 {i['t0']:6.2f}  {d:+5.1f} dB  {i['name']}")
    tmp = DZ / "_tmp/story"
    SFX.write_wav(tmp / "fix_bus_raw.wav", bus)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "fix_bus_raw.wav"), "-af",
                    "highpass=f=120,treble=g=-3:f=8000,aecho=0.9:0.7:23|37:0.10|0.06", str(tmp / "fix_bus.wav")], check=True)
    bus = SFX.load(tmp / "fix_bus.wav")[: len(voice)]
    mix = voice.copy()
    mix[: len(bus)] += bus
    SFX.write_wav(tmp / "fix_pre.wav", mix * min(1, .99 / (np.abs(mix).max() + 1e-9)))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "fix_pre.wav"), "-af",
                    "acompressor=threshold=-20dB:ratio=2.5:attack=10:release=150", "-ar", "48000", str(tmp / "fix_comp.wav")], check=True)
    c = SFX.load(tmp / "fix_comp.wav").astype(np.float64)
    g = 10 ** ((-14 - meter.integrated_loudness(c)) / 20)          # −14 LUFS 로 게인 → 마지막에 리미터(−1.5dB, 4배 오버샘플)
    SFX.write_wav(tmp / "fix_gain.wav", (c * g / 4).astype(np.float32))   # 넘침 없게 −12dB 로 써 두고 리미터 앞에서 되돌림
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "fix_gain.wav"), "-af",
                    "volume=12dB,aresample=192000,alimiter=limit=0.80:level=false:attack=2:release=60,aresample=48000",
                    str(tmp / "fix_mix.wav")], check=True)
    print("고친 소리", tmp / "fix_mix.wav")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
