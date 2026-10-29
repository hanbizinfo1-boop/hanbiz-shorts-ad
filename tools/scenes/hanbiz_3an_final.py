"""3안 타이포 완성본 조립 — 타이포 렌더 + 레이저 로고 엔딩 + 소리(BGM·효과음 마감본) → mp4 · 프리미어 XML · 층별 소재.

    python tools/scenes/hanbiz_3an_final.py [--render _tmp/typo3/3안_타이포_본.mp4] [--out 납품/3안_타이포_완성_1012]

화면: 렌더 0~28.119초(마디 1~15) → 레이저 엔딩(라벨·괄호 없음, 5.005초) → 렌더 33.124~35.39초(버튼·고지).
소리: 납품/효과음준비_1012/3안_소리미리듣기_합본.wav(−14 LUFS · TP ≤ −1.5 마감본, 큐 기록/효과음큐_3안_1012.json).
XML: V1 화면(영상만) · A1 BGM · A2~ 효과음 낱개(겹치면 다음 트랙) — lec_xml.write 재사용(1080×1920 으로 바꿔 부름).
점검: 길이 · ebur128 · rule_check.check_sfx(BGM 구간 제외) 결과를 <out>/_점검.txt 에.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config as C  # noqa: E402
import lec_xml  # noqa: E402
import rule_check as RC  # noqa: E402

ROOT = C.ROOT
F = 1001 / 30000
N_A, N_LASER, N_TOTAL = 1236, 150, 1454        # 9판(10-12, 뒷부분 재기획): 0~1235 렌더(~41.239) · 레이저 150프레임 · 1386~1453 렌더(버튼)
LASER = ROOT / "_tmp" / "typo3" / "레이저엔딩_라벨없음.mp4"   # 10-12 «위에 한비즈 … 없애줘» — tools/scenes/html/hanbiz_logo_laser_nolabel.html 을 html_motion 으로 렌더
SND = ROOT / "납품" / "효과음준비_1012"
NICK = SND / "3안_소리미리듣기_낱개"


def run(cmd):
    subprocess.run(cmd, check=True)


def probe_dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout)


def ebur(p):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    tail = r[r.rfind("Summary:"):]
    get = lambda key: next((ln.split(":",1)[1].strip() for ln in tail.splitlines() if ln.strip().startswith(key)), "?")
    return get("I:"), get("Peak:")


def main():
    ap = argparse.ArgumentParser(description="3안 완성본 조립")
    ap.add_argument("--render", default=str(ROOT / "_tmp" / "typo3" / "3안_타이포_본.mp4"))
    ap.add_argument("--out", default=str(ROOT / "납품" / "3안_타이포_완성_1012"))
    a = ap.parse_args()
    out = Path(a.out).resolve()   # XML pathurl 은 절대 경로여야 프리미어가 찾는다
    media = out / "media"
    (media / "효과음_낱개").mkdir(parents=True, exist_ok=True)

    # 화면만 (무음) — 프레임 단위로 잘라 잇는다
    pic = media / "한비즈_3안_화면만.mp4"
    fc = (f"[0:v]trim=start_frame=0:end_frame={N_A},setpts=PTS-STARTPTS[a];"
          f"[1:v]trim=start_frame=0:end_frame={N_LASER},setpts=PTS-STARTPTS,fps=30000/1001[b];"
          f"[0:v]trim=start_frame={N_A + N_LASER}:end_frame={N_TOTAL},setpts=PTS-STARTPTS[c];"
          f"[a][b][c]concat=n=3:v=1:a=0,format=yuv420p[v]")
    run(["ffmpeg", "-v", "error", "-y", "-i", a.render, "-i", str(LASER), "-filter_complex", fc, "-map", "[v]",
         "-r", "30000/1001", "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-profile:v", "high", "-movflags", "+faststart", str(pic)])

    # 소리 (마감본 그대로)
    mix = SND / "3안_소리미리듣기_합본.wav"
    final = out / "한비즈_3안_타이포.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(pic), "-i", str(mix), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-af", "alimiter=limit=0.6:attack=1:release=50:level=disabled",   # 합본 wav 트루피크가 −0.5 라(미리듣기 도구는 mp3 만 쟀다) −4.4dBFS 리미터 → AAC 뒤 −2.1 dBTP
         "-c:a", "aac", "-b:a", "320k", "-shortest", "-movflags", "+faststart", str(final)])

    # 층별 소재 + XML
    plan = json.loads((NICK / "_배치.json").read_text(encoding="utf-8"))
    shutil.copy2(NICK / plan["bgm"], media / "BGM_I'm Under The Radar_마감.wav")
    sfx = [(0.0, media / "BGM_I'm Under The Radar_마감.wav")]
    for s in plan["sfx"]:
        dst = media / "효과음_낱개" / s["file"]
        shutil.copy2(NICK / s["file"], dst)
        sfx.append((s["start"], dst))
    # 이번 배치에 없는 낱개(번호가 밀려 남은 이전 판 파일)는 프리미어에 잘못 끌려가지 않게 _tmp 로 옮긴다(지우지 않음)
    keep = {s["file"] for s in plan["sfx"]}
    stale = [p for p in (media / "효과음_낱개").glob("*.wav") if p.name not in keep]
    if stale:
        bak = ROOT / "_tmp" / "typo3" / f"낱개_이전_{out.name}"
        bak.mkdir(parents=True, exist_ok=True)
        for p in stale:
            shutil.move(str(p), str(bak / p.name))
        print(f"  이전 판 낱개 {len(stale)}개 → {bak}")
    lec_xml.SEQ_W, lec_xml.SEQ_H, lec_xml.V_TRACK, lec_xml.A_TRACK = 1080, 1920, 1, 1
    xml = out / "한비즈_3안_타이포.xml"
    lec_xml.write(xml, "한비즈_3안_타이포", pic, N_TOTAL * F, 0.0, sfx, 29.97, tag="h3")

    # 점검
    trip = [(s["start"], s["file"], probe_dur(NICK / s["file"])) for s in plan["sfx"]]
    chk = RC.check_sfx(trip, plan["length"], bed_intervals=[(0.0, plan["length"] - 0.6)], per_ep_max=None)   # 말 없는 타이포 — 5-4 대신 3초 사슬만(sfx.md 결정표 ⑦)
    chk += RC.check_tone(s["file"] for s in plan["sfx"])
    I, TP = ebur(final)
    L = ["3안 타이포 완성본 점검 (tools/scenes/hanbiz_3an_final.py)",
         f"  길이: 완성 {probe_dur(final):.3f}초 · 화면 {probe_dur(pic):.3f}초 (목표 {N_TOTAL * F:.3f}초)",
         f"  소리: I {I} · True Peak {TP} (목표 −14 LUFS · ≤ −1.5 dBTP)",
         f"  효과음 {len(plan['sfx'])}개 · rule_check: " + ("통과" if not chk else "; ".join(f"[{lv}] {r}: {m}" for lv, r, m in chk)),
         "  화면 점검: _tmp/typo3/3안_타이포_본_점검.txt (html_motion 렌더 전 점검 — --무시 로 넘긴 것: 마디 4 끝 «요» 속으로 확대 전환에서 글이 화면 밖으로 나감(연출), 인지 텀 0.46초 줄 쌓기·몽타주(motion-typo J 카드 예외))",
         "  소리는 귀로 듣지 못했다."]
    (out / "_점검.txt").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
