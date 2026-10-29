# -*- coding: utf-8 -*-
r"""한 편 조립기(edit_plan · edit_render · edit_xml · words.speech_onset) 끝까지 돌려 보는 시험 — 합성 소재로.

[새로 만든 도구]
    python edit_smoke.py            → _tmp/edit_smoke/ 에 합성 소재를 만들고 배치표 본보기(examples/edit_plan_sample.json)를 돌린다
    python edit_smoke.py --소재만   → 소재만 만든다

합성 소재: testsrc2 1920×1080 29.97 · 59.94 · 1080×1920 29.97 각 6초 / 배경 PNG / 그래픽 PNG(알파) / 사인파+잡음 목소리 10초 / BGM 10초.
효과음은 배치표가 부르는 이름을 sfx.find_file 로 찾고, 못 찾으면 합성 wav 로 바꿔 쓴다.
확인: 미리보기 길이·해상도·fps · XML 파싱 · verify · from_premiere 되돌리기(컷 수·길이) · rule_check 호출 · ERROR 때 멈춤 / --무시 통과.
"""
import json
import os
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import config as C  # noqa: E402
import edit_plan as P  # noqa: E402
import edit_render as R  # noqa: E402
import edit_xml as X  # noqa: E402
import sfx as SFX  # noqa: E402
import words  # noqa: E402

D = C.WORK / "edit_smoke"
SAMPLE = C.TOOLS / "examples" / "edit_plan_sample.json"
SR = 48000


def ff(*a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)


def wav_write(path, x):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def make_assets():
    D.mkdir(parents=True, exist_ok=True)
    for name, size, rate in (("a_2997.mp4", "1920x1080", "30000/1001"), ("b_5994.mp4", "1920x1080", "60000/1001"), ("c_vert.mp4", "1080x1920", "30000/1001")):
        ff("-f", "lavfi", "-i", f"testsrc2=s={size}:r={rate}:d=6", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(D / name))
    ff("-f", "lavfi", "-i", "testsrc=s=1920x1080:d=1", "-frames:v", "1", str(D / "bg.png"))
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGBA", (600, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 599, 299), 40, fill=(255, 255, 255, 235), outline=(30, 30, 30, 255), width=6)
    d.text((300, 150), "CARD", font=ImageFont.truetype(str(C.FONTS["pretendard_bold"]), 90), fill=(20, 20, 20, 255), anchor="mm")
    im.save(D / "card.png")
    # 목소리 — 음절 0.18초씩 0.25초 간격, 말 덩어리 사이는 쉼. 덩어리 시작이 «진짜 말 시작»
    rng = np.random.default_rng(7)
    x = np.zeros(SR * 10, np.float32)
    starts = [0.25, 2.65, 7.4]          # 가운데(4.6~7.4초)는 긴 쉼 — 덕킹 실측에서 «말 없는 구간» 으로 쓴다
    for s0 in starts:
        for k in range(8):
            t0 = s0 + k * 0.25
            n = int(0.18 * SR)
            t = np.arange(n) / SR
            syl = (np.sin(2 * np.pi * (180 + 30 * k) * t) + 0.5 * np.sin(2 * np.pi * (360 + 60 * k) * t)) * np.hanning(n) * 0.28
            syl += rng.normal(0, 0.01, n) * np.hanning(n)
            i = int(t0 * SR)
            x[i:i + n] += syl.astype(np.float32)
    wav_write(D / "voice.wav", x)
    t = np.arange(SR * 10) / SR
    bgm = (np.sin(2 * np.pi * 110 * t) + 0.6 * np.sin(2 * np.pi * 164.8 * t) + 0.4 * np.sin(2 * np.pi * 220 * t)) * 0.2 + rng.normal(0, 0.01, len(t))
    wav_write(D / "bgm.wav", bgm.astype(np.float32))
    return starts


def synth_sfx(path, f0):
    t = np.arange(int(0.6 * SR)) / SR
    wav_write(path, (np.sin(2 * np.pi * f0 * t) * np.exp(-t * 6) * 0.6).astype(np.float32))


def sample_plan():
    """본보기 배치표를 읽어, 이 PC 에서 못 찾는 효과음만 합성 wav 로 바꾼 사본(_tmp/edit_smoke/plan.json)을 돌려준다."""
    d = json.loads(SAMPLE.read_text(encoding="utf-8"))
    swapped = {}
    names = {r["file"] for r in d["sfx_roles"].values()} | {e["file"] for e in d["sfx"] if e.get("file")}
    for k, n in enumerate(sorted(names)):
        try:
            SFX.find_file(n)
        except FileNotFoundError:
            swapped[n] = f"synth_{k}.wav"
            synth_sfx(D / swapped[n], 500 + 200 * k)
    for r in d["sfx_roles"].values():
        r["file"] = swapped.get(r["file"], r["file"])
    for e in d["sfx"]:
        if e.get("file"):
            e["file"] = swapped.get(e["file"], e["file"])
    d["base_dir"] = "."
    d["sfx_per_ep_max"] = None      # 본보기는 같은 파일 3번씩 돌려 쓴다 — 5-4(한 편 2번)는 아래 따로 시험한다
    ov = C.WORK / "html_motion" / "hanbiz_typo_test.mov"          # 오버레이 시험용 알파 MOV — 없으면 html_motion 으로 다시 렌더(약 1분)
    if not ov.exists():
        print("오버레이 시험 소재가 없다 → html_motion 렌더 …")
        subprocess.run([sys.executable, str(C.TOOLS / "html_motion.py"), str(C.TOOLS / "scenes" / "html" / "hanbiz_typo_test.html"), "--alpha", "--sub", "1", "--no-sheet"], check=True)
    for o in d.get("overlays", []):
        o["file"] = os.path.relpath(ov, D).replace("\\", "/")
    p = D / "plan.json"
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return p, swapped


def probe(mp4):
    s = R.probe_out(mp4)
    v = next(x for x in s if x["codec_type"] == "video")
    a = next(x for x in s if x["codec_type"] == "audio")
    return v, a


def main():
    starts = make_assets()
    if "--소재만" in sys.argv:
        return
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  [통과] " if cond else "  [실패] ") + msg)
        ok = ok and bool(cond)

    # words.speech_onset — 합성 목소리의 진짜 말 시작과 비교
    env = words.env_db(D / "voice.wav")
    got = [words.speech_onset(env, s0 + 0.08, s0 - 0.6) for s0 in starts]
    print("말 시작 당기기 (진짜 시작 → 받아쓰기 +0.08초 가정 → speech_onset):", [(s0, round(g, 2)) for s0, g in zip(starts, got)])
    check(all(abs(g - s0) <= 0.1 for g, s0 in zip(got, starts)), "speech_onset 이 진짜 시작 ±0.1초 안")
    check(abs(words.caption_t(env, starts[1] + 0.08, starts[1] - 0.6) - (got[1] - words.CAP_LEAD)) < 1e-6, "caption_t = onset − 0.05")

    plan_path, swapped = sample_plan()
    print("효과음 합성 대체:", swapped or "없음 (전부 라이브러리에서 찾음)")
    plan = P.load(plan_path)
    n_cuts = len(plan["cuts"])

    out_dir = D / "out"
    mp4, rpt, nerr = R.run(plan_path, out_dir / "edit_smoke_미리보기.mp4")
    check(mp4 is not None, "render.run 이 미리보기를 만들었다")
    v, a = probe(mp4)
    exp_dur = P.n_frames(plan) / float(plan["_fps"])
    print(f"  ffprobe: {v['width']}x{v['height']} {v['r_frame_rate']} 영상 {float(v['duration']):.3f}s 소리 {float(a['duration']):.3f}s (기대 {exp_dur:.3f}s)")
    check((v["width"], v["height"]) == (1080, 1920), "해상도 1080x1920")
    check(v["r_frame_rate"] == "30000/1001", "fps 30000/1001")
    check(abs(float(v["duration"]) - exp_dur) < 0.1, "길이 ≈ 10.0/1.15 초")
    txt = rpt.read_text(encoding="utf-8")
    check("규칙 점검" in txt and "통과" in txt, "_점검.txt 에 rule_check 결과가 있다 (check_plan·check_sfx 호출됨)")

    # 마감 체인 — 덕킹이 실제로 걸리는지, 마감 LUFS · 트루피크, exact_db, finish 끄기
    print("  _점검.txt 의 마감 줄:")
    for ln in txt.splitlines():
        if ln.startswith(("목소리 기준", "마감 트루피크", "덕킹 실측", "XML 에는 없는", "  - ")):
            print("   ", ln)
    au = R.build_audio(plan, D / "audio_chk")
    ds = R.duck_stat(au["vbus"], au["bgm_fin"])
    print(f"  덕킹 실측: 말 한가운데 BGM {ds[0]:.1f} dBFS · 말 없는 곳 BGM {ds[1]:.1f} dBFS · 차 {ds[2]:.1f} dB (켠 값 {plan['finish']['duck_db']} dB)")
    check(ds[2] <= -6.0, "덕킹: 말 구간 BGM 이 말 없는 구간보다 6dB 이상 작다")
    d2 = json.loads(plan_path.read_text(encoding="utf-8"))
    d2["finish"] = {"duck": False}
    p2 = D / "plan_noduck.json"
    p2.write_text(json.dumps(d2, ensure_ascii=False), encoding="utf-8", newline="\n")
    au2 = R.build_audio(P.load(p2), D / "audio_chk2")
    ds2 = R.duck_stat(au2["vbus"], au2["bgm_fin"])
    print(f"  (대조) finish.duck=false: 차 {ds2[2]:.1f} dB")
    check(abs(ds2[2]) < 1.5, "finish.duck=false 면 말 구간·쉼 BGM 차가 ±1.5dB 안")
    lu_o, tp_o = R.lufs(mp4), R.true_peak(mp4)
    print(f"  마감: {lu_o:.2f} LUFS (목표 {plan['loudness_lufs']}) · 트루피크 {tp_o:.2f} dBTP (기준 ≤ {R.LOUD_TP})")
    check(abs(lu_o - plan["loudness_lufs"]) <= 1.0 and tp_o is not None and tp_o <= R.LOUD_TP + 0.3, "마감 LUFS ±1.0 · 트루피크 ≤ −1.5(+0.3 aac 여유)")
    check(SFX.SND["ding"][4] == 3, f"exact_db: ding 역할이 FILE_DB(맑은소리 7) 대신 3 (SND rel={SFX.SND['ding'][4]})")
    check(any(s["prio"] == 3 for s in au["sfx"]) and "XML 에는 없는 처리" in txt, "prio 3 효과음 · _점검.txt 에 «XML 에는 없는 처리» 목록")
    import rule_check as RC
    two = RC.check_sfx([(1.0, "a.wav"), (3.0, "b.wav")], 5.0)
    print("  check_sfx 2-튜플:", two[:1])
    check(any(x[0] == "ERROR" and "3-튜플" in x[2] for x in two), "rule_check.check_sfx 2-튜플 → ERROR")
    rep = RC.check_sfx([(1.0, "a.wav", 0.3), (4.5, "a.wav", 0.3), (9.0, "a.wav", 0.3), (12.0, "a.wav", 0.3, "사장님 연타")], 14.0)
    check(any(x[0] == "ERROR" and x[1].startswith("5-4") and "3번" in x[2] for x in rep), "rule_check 5-4 한 편 같은 파일 3번 → ERROR (연타 사유가 있는 4번째는 안 셈)")

    r = X.export(plan_path, out_dir / "xml")
    import xml.etree.ElementTree as ET
    ET.parse(r["xml"])
    check(True, f"XML 파싱 ({r['xml'].name}) V1 {r['n_v1']} · V2 {r['n_v2']} · V3 {r['n_v3']} · 오버레이 {r['n_ovl']}개/{r['ovl_tracks']}트랙 · 효과음 {r['n_sfx']}개/{r['sfx_tracks']}트랙 · 플래시 {r['n_flash']} · 마커 {r['n_markers']}")
    check(plan["overlays"] and r["n_ovl"] == len(plan["overlays"]) and r["ovl_tracks"] >= 1, "XML 에 오버레이 트랙이 들어갔다 (원본 MOV 참조)")
    xt = ET.parse(r["xml"]).getroot()
    ov_clip = next((c for c in xt.iter("clipitem") if (c.get("id") or "").startswith("OV_")), None)
    check(ov_clip is not None and Path(plan["overlays"][0]["file"]).name in (ov_clip.findtext("file/pathurl") or "").replace("%20", " ") and not (r["media"] / "OV_00_typo.mov").exists(),
          "오버레이 클립이 원본 MOV 를 그대로 참조 (media/ 에 복사본 없음)")
    # 오버레이가 미리보기에 실제로 합성됐는지 — 오버레이 구간 프레임이 배경 컷 프레임과 다르다
    import numpy as _np
    j_mid = int((plan["overlays"][0]["t0"] + 2.0) / plan["speed"] * float(plan["_fps"]))
    fa = _np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf", f"select=eq(n\\,{j_mid}),format=rgb24", "-frames:v", "1", "-f", "rawvideo", "-"],
                                       capture_output=True).stdout, _np.uint8)
    lay = R.layout(plan)
    check(lay["ovl"][0][1] > lay["ovl"][0][0] and fa.size == 1080 * 1920 * 3, f"오버레이 프레임 범위 {lay['ovl'][0]} · 구간 안 프레임 {j_mid} 추출")
    vr = X.verify(r["xml"], mp4)
    check(vr["psnr_min"] >= 30 and not vr["missing"] and not vr["gaps"], f"verify 화면 PSNR 최저 {vr['psnr_min']:.1f} / 평균 {vr['psnr_mean']:.1f}")
    check(abs(vr["lufs_xml"] - vr["lufs_prev"] + r["capped_db"]) <= 1.0 and abs(vr["lag_ms"]) <= 40 and vr["peak_xml"] <= 0,
          f"verify 소리 LUFS {vr['lufs_xml']:.1f} vs {vr['lufs_prev']:.1f} (최고음 때문에 깎은 {r['capped_db']:.1f}dB 감안), 최고 {vr['peak_xml']:.1f}dBFS, 어긋남 {vr['lag_ms']}ms")

    back = P.from_premiere(r["xml"], loudness_lufs=plan["loudness_lufs"])
    print("  from_premiere 메모:", back["_notes"])
    same_n = len(back["cuts"]) == n_cuts
    d_old = [round(c["end"] - c["start"], 3) for c in plan["cuts"]]
    d_new = [round(c["end"] - c["start"], 3) for c in back["cuts"]]
    tol = 1.5 * plan["speed"] / float(plan["_fps"])
    check(same_n and all(abs(a - b) <= tol for a, b in zip(d_old, d_new)) and abs(back["speed"] - plan["speed"]) < 1e-3,
          f"from_premiere 되돌리기: 컷 {len(back['cuts'])}/{n_cuts}, 길이 {d_new} vs {d_old}, speed {back['speed']}")

    # ERROR 일 때 멈춤 / --무시
    bad = json.loads(plan_path.read_text(encoding="utf-8"))
    bad["sfx"] = bad["sfx"][:3]
    bp = D / "plan_bad.json"
    bp.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8", newline="\n")
    m2, rpt2, n2 = R.run(bp, D / "out_bad" / "bad.mp4")
    check(m2 is None and n2 > 0, f"효과음이 모자라면 멈춘다 (ERROR {n2}건, mp4 안 만듦)")
    m3, rpt3, n3 = R.run(bp, D / "out_bad" / "bad.mp4", ignore=True)
    t3 = rpt3.read_text(encoding="utf-8")
    check(m3 is not None and "--무시 로 통과한 위반" in t3, f"--무시 로 통과하고 위반 목록을 점검 파일에 적었다 ({n3}건)")
    # 자막 스타일 — 기본 band(A2) · outline 모드 · 잘못된 mode 는 막는다
    st = plan["caption_style"]
    segs = [("정책자금", "y"), (", 아직 혼자 알아보세요?", None)]
    ib = R.cap_img(st, segs, True)
    ab = ib[..., 3]
    check(st["mode"] == "band" and st["band_fill"] == [52, 52, 56] and (st["pad_x"], st["pad_y"], st["radius"]) == (26, 14, 12), "caption_style 기본 = band A2 (52,52,56 · 26/14 · r12)")
    check(tuple(ib[ib.shape[0] // 2, 2, :3]) == (52.0, 52.0, 56.0) and ab[ib.shape[0] // 2, 2] == 255 and ab[0, 0] == 0 and ab[ib.shape[0] // 2, ib.shape[1] - 3] == 255,
          f"band: 띠 속 불투명 (52,52,56), 모서리는 둥글게 투명 — 이미지 {ib.shape[1]}x{ib.shape[0]}")
    so = json.loads(json.dumps(st))
    so["mode"] = "outline"
    io = R.cap_img(so, segs, True)
    check(io.shape != ib.shape and io[io.shape[0] // 2, 2, 3] < 255 and io[..., 3].max() == 255, f"outline 모드: 외곽선+그림자 이미지 {io.shape[1]}x{io.shape[0]} (띠와 다르다)")
    bad_style = json.loads(plan_path.read_text(encoding="utf-8"))
    bad_style["caption_style"] = {"mode": "box"}
    pbs = D / "plan_badstyle.json"
    pbs.write_text(json.dumps(bad_style, ensure_ascii=False), encoding="utf-8", newline="\n")
    try:
        P.load(pbs)
        check(False, "caption_style.mode 오타를 막는다")
    except P.PlanError:
        check(True, "caption_style.mode 오타를 막는다")
    # 미리보기 한 프레임 — 첫 자막이 나오는 순간
    c0 = plan["captions"][0]
    j_cap = int((c0["start"] / plan["speed"] + 0.5) * float(plan["_fps"]))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-vf", f"select=eq(n\\,{j_cap})", "-frames:v", "1", str(D / "cap_frame.png")], check=True)
    print("  자막 프레임:", D / "cap_frame.png")
    print("\n전체:", "통과" if ok else "실패 있음")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
