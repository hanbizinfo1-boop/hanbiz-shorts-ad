# -*- coding: utf-8 -*-
r"""4번 «건물만 사면 돈을 벌 수 있어요» — 건물 한 채 박힘 → 돈다발 3개 짤랑 떠오르며 디졸브 (10-20).

사장님(10-20): «건물만 사면 돈을 벌수 있어요 부분에 건물만 사면 << 건물이 딱 한채 살짝 왼쪽부분에 박혀주고 거기서 코인획득 효과음이랑 같이 돈다발 한 3개가 짤랑 하면서 위로살짝 올라가면서 디졸브되는 느낌으로 돈벌수있는걸 표현해줘»
기준 = 사장님 «4번» 자동저장 14:12: 25.359~26.994 (V1 원본 66.667). XML V4 · A4~.

    python 지시작업/tools/r4m_build.py base / caps
    python tools/html_motion.py 지시작업/tools/scenes/r4m.html --alpha --fps 59.94 --workers 2 --sub 4 --out 지시작업/_tmp/r4m --name r4m
    python 지시작업/tools/r4m_build.py out
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r4x_build as X  # noqa: E402

OFFSET = 25.359                     # 사장님 시퀀스에서 이 구간 시작
X.WORK = X.DZ / "_tmp/r4m"
X.DELIV = X.DZ / "납품/4번_건물만사면_돈다발_1020"
X.NAME = "4번_건물만사면_돈다발"
X.END = 26.994 - OFFSET
X.CUTS = [(0.0, 26.226 - OFFSET, 66.667), (26.226 - OFFSET, 26.994 - OFFSET, 66.667 + 26.226 - OFFSET)]
X.ZOOM = dict(t0=99, dur=0.131, s=1.0, dx=0)
X.CAPS = [(0.0, 26.226 - OFFSET, [("건물만 사면", 0)]), (26.226 - OFFSET, 26.994 - OFFSET, [("돈을 벌 수 있어요", 0)])]
X.SFX_LIST = [
    (25.37 - OFFSET, "8. 훅.mp3", -6, "onset", 0),   # 건물 박힘 — 10-20 «건물떄 쿵이아니라 훅» → «휙1 말고 훅으로»
    (26.23 - OFFSET, "코인획득.mp3", -7, "onset", 0),   # 10-20 «내 효과음중에 코인획득이있어» — 사장님라이브러리/효과음/코인획득.mp3
]
OVL_NAME = "연출층_건물만사면_돈다발.mov"


def _scene_name():
    return X.WORK / "r4m.mov"


_out = X.out


def out():
    # r4x_build.out 은 WORK/r4x.mov 를 연출층으로 쓴다 — 이 구간 장면 파일로 바꿔 끼운다
    src = X.WORK / "r4m.mov"
    shutil.copy2(src, X.WORK / "r4x.mov")
    _out()
    media = X.DELIV / "media"
    old = media / "연출층_빌딩인형.mov"
    if old.exists():
        name = OVL_NAME
        try:
            old.replace(media / name)   # 다시 만들 때 덮어씀
        except PermissionError:         # 프리미어가 열어 둔 파일 — 규칙 9: 남기고 새 이름(_새판)으로 알린다
            name = OVL_NAME.replace(".mov", "_새판.mov")
            old.replace(media / name)
            print("  [잠김]", OVL_NAME, "— 새 판은", name)
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
