"""퓨레바 육아 3차 위에 BGM 후보를 깔아 본 판 — 곡마다 한 편(mp4) + 원곡 mp3 사본.

python 지시작업/tools/pureva_bgm_preview.py
BGM 레벨 = 분양2 실측(sfx.md 13장): 나레이션보다 12 LU 아래로 고르게(펌핑 덕킹 없음) · 앞 0.5초 페이드인 · 끝 1.8초 페이드아웃 ·
마감 −14 LUFS · 트루피크 −1.5dB. 곡 시작 = 첫 히트(후보표 «첫히트» — 도입부 허전한 데 건너뜀).
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
VIDEO = ROOT / "납품" / "퓨레바_육아_3차_1026" / "퓨레바_육아_3차.mp4"
OUT = ROOT / "납품" / "퓨레바_육아_BGM후보_1026"
LIB = REPO / "소재" / "BGM후보"
DUR = 45.871
UNDER = 12          # 나레이션(완성 믹스) 대비 BGM 을 이만큼 아래 LU
PICKS = [            # (번호, 파일, 시작초, 한 줄)
    ("1", "P1/Mixkit_Dreamy_Jazz.mp3", 2.21, "Dreamy Jazz · 110 BPM · 라운지·편안·웰니스 · 말 대역 겹침 3%"),
    ("2", "P3/Mixkit_My_Father_Tells_Me.mp3", 0.30, "My Father Tells Me · 110 BPM · 어쿠스틱 기타·다정·라이프스타일 · 5%"),
    ("3", "P3/Mixkit_Adone.mp3", 0.77, "Adone · 116 BPM · 가볍고 밝음·라이프스타일 · 4%"),
    ("4", "P3/Mixkit_Im_Fine.mp3", 1.53, "I'm Fine · 120 BPM · 자신감·긍정·라이프스타일 · 6%"),
]


def lufs(path, af="anull"):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", f"{af},ebur128", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ref = lufs(VIDEO)
    for n, f, ss, note in PICKS:
        src = LIB / f
        shutil.copy2(src, OUT / f"BGM{n}_{src.stem.replace('Mixkit_', '')}_원곡.mp3")
        seg = f"atrim={ss}:{ss + DUR},asetpts=PTS-STARTPTS"
        g = (ref - UNDER) - lufs(src, seg)
        fc = (f"[1:a]{seg},volume={g:.2f}dB,afade=t=in:d=0.5,afade=t=out:st={DUR - 1.8}:d=1.8[b];"
              f"[0:a][b]amix=inputs=2:normalize=0:duration=first[m]")
        r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(VIDEO), "-i", str(src), "-filter_complex",
                            fc + ";[m]loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json[o]", "-map", "[o]", "-f", "null", "-"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        m = json.loads(re.findall(r"\{[^{}]*\}", r.stderr)[-1])
        ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
              f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000")
        out = OUT / f"퓨레바_육아_3차_BGM{n}_{src.stem.replace('Mixkit_', '')}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(VIDEO), "-i", str(src), "-filter_complex",
                        fc + f";[m]{ln}[o]", "-map", "0:v", "-map", "[o]", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
                        str(out)], check=True)
        print(f"BGM{n} {note} · 곡 {g:+.1f}dB → {out.name} · 마감 {lufs(out):.1f} LUFS")


if __name__ == "__main__":
    main()
