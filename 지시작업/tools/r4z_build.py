# -*- coding: utf-8 -*-
r"""4번 «10년전에 최저시급이 6천 원이였는데 지금 만 원 넘잖아요 / 그렇기 때문에 돈의 가치는 급격히 떨어지고 있어요» — 막대그래프가 뒤집히는 연출 (10-20).

사장님(10-20): «시급 6천원에서 만원 --> 막대그래프로 연출
  그렇기때문에 돈의 가치는 급격히떨어지고있어요 --> 막대그래프가 좌우로 뒤집히면서 돈의가치는 역으로 하락하는 연출
  이 두개가 자연스럽고 부드럽게 이어지게끔 연출해줘»
기준 = 사장님 «4번» 11:34 저장본: 9.543~15.649 (V1 9.543~12.896 원본 42.659 · 12.896~15.649 원본 46.263).
r4y_build.py 와 같은 틀(r4x_build 재사용) — 장면 0초 = 시퀀스 9.543초, XML 은 V4 · A4 부터.

    python 지시작업/tools/r4z_build.py base
    python 지시작업/tools/r4z_build.py caps
    python tools/html_motion.py 지시작업/tools/scenes/r4z.html --alpha --fps 59.94 --workers 2 --sub 4 --out 지시작업/_tmp/r4z --name r4z
    python 지시작업/tools/r4z_build.py out
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r4x_build as X  # noqa: E402

OFFSET = 9.543                      # 사장님 시퀀스에서 이 구간 시작
X.WORK = X.DZ / "_tmp/r4z"
X.DELIV = X.DZ / "납품/4번_최저시급_돈의가치_1020"
X.NAME = "4번_최저시급_돈의가치"
X.END = 15.649 - OFFSET
X.CUTS = [(0.0, 12.896 - OFFSET, 42.659), (12.896 - OFFSET, 15.649 - OFFSET, 46.263)]
X.ZOOM = dict(t0=99, dur=0.131, s=1.0, dx=0)
X.CAPS = [(0.0, 10.844 - OFFSET, [("10년전에 최저시급이", 0)]), (10.844 - OFFSET, 11.628 - OFFSET, [("6천 원", 1), ("이였는데", 0)]),
          (11.628 - OFFSET, 12.896 - OFFSET, [("지금 ", 0), ("만 원", 1), (" 넘잖아요", 0)]), (12.896 - OFFSET, 13.363 - OFFSET, [("그렇기 때문에", 0)]),
          (13.363 - OFFSET, 14.164 - OFFSET, [("돈의 가치는", 0)]), (14.164 - OFFSET, 15.649 - OFFSET, [("급격히 떨어지고 있어요", 0)])]
X.SFX_LIST = [   # (구간 시각, 파일, 목소리 대비 dB, 맞춤, -)
    (0.03, "ML_Fast small sweep transition.wav", -10, "onset", 0),   # 그래프 판 들어옴
    (1.33, "KN_select_003.wav", -9, "onset", 0),                     # 10년 전 막대 6천 원
    (2.12, "SEL_キラッ1.mp3", -9, "onset", 0),                        # 지금 막대 1만 원(쭉)
    (3.36, "SEL_マントを翻す.mp3", -7, "onset", 0),                   # 판이 좌우로 뒤집힘
    (4.65, "KN_lowDown.wav", -8, "onset", 0),                        # 지금 막대가 툭 꺼짐(급격히 떨어지고)
]
OVL_NAME = "연출층_최저시급_돈의가치.mov"


def _scene_name():
    return X.WORK / "r4z.mov"


_out = X.out


def out():
    # r4x_build.out 은 WORK/r4x.mov 를 연출층으로 쓴다 — 이 구간 장면 파일로 바꿔 끼운다
    src = X.WORK / "r4z.mov"
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
