# -*- coding: utf-8 -*-
r"""4번 «30억으로 100억 만드려고 하는데 예금하려는 분들은 없죠?» — 달팽이 경주(C안) → 사장님 시퀀스에 얹는 XML (10-20).

사장님(10-20): «오케이 다음작업 할건데 30억으로 100억만드려고하는데 예금하려는분 없죠<< 이부분에 들어갈 연출 추천해볼래?»
  → 추천 A·B·C → «손짓으로 뭘 할 수 있는 구간은 아닌듯» → «c안으로 가자»
기준 = 사장님 «4번» 11:34 저장본(_tmp/story/seq_4번_1020d.json): 30억으로 6.123~6.807 · 100억 만드려고 하는데 6.807~7.858 · 예금하려는 분들은 없죠? 7.858~9.543
      V1 6.123~6.807(원본 37.17) · 6.807~9.543(원본 37.854). «연 3%면 41년» 같은 숫자는 사장님 확인 전이라 넣지 않음.
r4x_build.py 를 그대로 쓰고 구간·장면·효과음만 바꾼다. 장면·효과음 시각은 이 구간 시작(6.123)을 0 으로 잰다 — XML 에는 6.123 에 놓인다.

    python 지시작업/tools/r4y_build.py base
    python 지시작업/tools/r4y_build.py caps
    python tools/html_motion.py 지시작업/tools/scenes/r4y.html --alpha --fps 59.94 --workers 2 --sub 4 --out 지시작업/_tmp/r4y --name r4y
    python 지시작업/tools/r4y_build.py out
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r4x_build as X  # noqa: E402

OFFSET = 6.123                      # 사장님 시퀀스에서 이 구간 시작
X.WORK = X.DZ / "_tmp/r4y"
X.DELIV = X.DZ / "납품/4번_30억_달팽이경주_1020"
X.NAME = "4번_30억_달팽이경주"
X.END = 9.543 - OFFSET
X.CUTS = [(0.0, 6.807 - OFFSET, 37.17), (6.807 - OFFSET, 9.543 - OFFSET, 37.854)]
X.ZOOM = dict(t0=99, dur=0.131, s=1.0, dx=0)
X.CAPS = [(0.0, 6.807 - OFFSET, [("30억", 1), ("으로", 0)]), (6.807 - OFFSET, 7.858 - OFFSET, [("100억", 1), (" 만드려고 하는데", 0)]),
          (7.858 - OFFSET, 9.543 - OFFSET, [("예금하려는 분들은 없죠?", 0)])]
X.SFX_LIST = [   # (구간 시각, 파일, 목소리 대비 dB, 맞춤, -)
    (0.02, "ML_Fast small sweep transition.wav", -10, "onset", 0),   # 트랙이 들어옴
    (0.72, "SEL_キラッ1.mp3", -9, "onset", 0),                        # 도착 깃발 «100억» 반짝
    (1.78, "KN_select_003.wav", -9, "onset", 0),                     # 달팽이 등장
    (2.72, "KN_impactSoft_heavy_001.wav", -8, "onset", 0),          # 돌로 굳음(10-20 «돌이되서 깨지는느낌»)
    (2.96, "ML_Glass break with hammer thud.wav", -6, "onset", 0),  # 깨지며 디졸브
]


def _scene_name():
    return X.WORK / "r4y.mov"


_out = X.out


def out():
    # r4x_build.out 은 WORK/r4x.mov 를 연출층으로 쓴다 — 이 구간 장면 파일로 바꿔 끼운다
    src = X.WORK / "r4y.mov"
    shutil.copy2(src, X.WORK / "r4x.mov")
    _out()
    media = X.DELIV / "media"
    old = media / "연출층_빌딩인형.mov"
    if old.exists():
        name = "연출층_달팽이경주.mov"
        try:
            old.replace(media / name)   # 다시 만들 때 덮어씀
        except PermissionError:         # 프리미어가 열어 둔 파일 — 규칙 9: 남기고 새 이름(_새판)으로 알린다
            name = "연출층_달팽이경주_새판.mov"
            old.replace(media / name)
            print("  [잠김] 연출층_달팽이경주.mov — 새 판은", name)
        x = (X.DELIV / f"{X.NAME}.xml")
        import urllib.parse
        x.write_text(x.read_text(encoding="utf-8").replace("연출층_빌딩인형.mov", name)
                     .replace(urllib.parse.quote("연출층_빌딩인형.mov"), urllib.parse.quote(name)), encoding="utf-8")


_xml = X.write_xml


def write_xml(placed, ovl):
    """r4x 와 같은 모양 + 모든 클립을 OFFSET(6.123초) 뒤로 — 사장님 «4번»과 같은 시각에 놓인다."""
    _xml(placed, ovl)
    import re
    p = X.DELIV / f"{X.NAME}.xml"
    s = p.read_text(encoding="utf-8")
    off = int(round(OFFSET * X.FPS))
    s = re.sub(r"<start>(\d+)</start><end>(\d+)</end>", lambda m: f"<start>{int(m.group(1)) + off}</start><end>{int(m.group(2)) + off}</end>", s)
    s = re.sub(r"(<sequence id=\"seq-1\"><name>[^<]*</name><duration>)(\d+)(</duration>)", lambda m: f"{m.group(1)}{int(m.group(2)) + off}{m.group(3)}", s)
    # 10-20 사장님 «이거 장면 트랙 v4 효과음트랙 v4부터 나오게해줘» — 앞에 빈 트랙 셋(V1~V3 · A1~A3)
    s = s.replace("</format><track>", "</format>" + "<track></track>" * 3 + "<track>", 1)
    s = s.replace("<numOutputChannels>2</numOutputChannels><track>", "<numOutputChannels>2</numOutputChannels>" + "<track></track>" * 3 + "<track>", 1)
    p.write_text(s, encoding="utf-8")


X.write_xml = write_xml

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    X.WORK.mkdir(parents=True, exist_ok=True)
    cmd = sys.argv[1]
    if cmd == "base":
        X.base()
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(X.WORK / "V1_1.mov"), "-i", str(X.WORK / "V1_2.mov"), "-filter_complex",
                        "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]", "-c:v", "prores_ks", "-profile:v", "1",
                        "-c:a", "pcm_s16le", str(X.WORK / "base_full.mov")], check=True)
    else:
        {"caps": X.caption_layer, "out": out}[cmd]()
