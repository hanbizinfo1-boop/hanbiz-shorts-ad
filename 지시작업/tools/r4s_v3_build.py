# -*- coding: utf-8 -*-
r"""4번 «그래서 결국 돈 있는 분들이 찾는 게 강남빌딩이에요» — 세미나 사진 박기 → 가루로 흩어져 강남빌딩 3장으로 모임 (10-20).

사장님(10-20): «그래서 결국 돈있는 분들이 찾는 게 할때 D:년 10월±020\세미나 여기에 있는 이미지들 정면으로 얼굴나오는거(황소장제외) 모자이크하고 사진처럼 디자인처리해서
  하나씩 자막밑으로 박아줘 … 살짝씩 겹쳐도좋으니까 저 하얀테두리안으로 들어가게끔 위를향하지만 살짝 틀어지는 각도는 자유롭게 위치순서도 자유롭게해서 박아주면되고
  강남빌딩이에요 할때 --> 사진들이 살짝 가루처럼 깨지며 흩어지면서 이게 모이면서 D:년 10월±020\강남빌딩 여기있는 강남빌딩도 사진처럼 이건 각도 및 정렬자간 딱딱 절도있게끔 왼 중 오 이런식으로 자막밑 하얀 테두리안쪽으로 합쳐지게끔»
기준 = 사장님 «4번» 11:34 저장본 15.649~18.835 (V1 원본 50.5). 사진 카드(모자이크·흰 테두리) = 지시작업/소재/r4s/ · 장면 0초 = 시퀀스 15.649 · XML V4 · A4~.

    python 지시작업/tools/r4s_build.py base / caps
    python tools/html_motion.py 지시작업/tools/scenes/r4s.html --alpha --fps 59.94 --workers 2 --sub 4 --out 지시작업/_tmp/r4s --name r4s
    python 지시작업/tools/r4s_build.py out
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r4x_build as X  # noqa: E402

OFFSET = 15.649                     # 사장님 시퀀스에서 이 구간 시작
X.WORK = X.DZ / "_tmp/r4s_v3"
X.DELIV = X.DZ / "납품/4번_세미나사진_강남빌딩_v3필름_1020"   # 10-20 «필름처럼 … 왼쪽으로 쭉가다가 한번 접히고 펼쳐지면서 … 건물만 세개 딱딱딱» — 장면 scenes/r4s_v3.html
X.NAME = "4번_세미나사진_강남빌딩_v3필름"
X.END = 18.835 - OFFSET
X.CUTS = [(0.0, 17.0 - OFFSET, 50.5), (17.0 - OFFSET, 18.835 - OFFSET, 50.5 + 17.0 - OFFSET)]
X.ZOOM = dict(t0=99, dur=0.131, s=1.0, dx=0)
X.CAPS = [(0.0, 16.45 - OFFSET, [("그래서 결국", 0)]), (16.45 - OFFSET, 17.768 - OFFSET, [("돈 있는 분들이 찾는게", 0)]),
          (17.768 - OFFSET, 18.835 - OFFSET, [("강남빌딩이에요", 0)])]   # 10-20 13:49 자동저장본 — 자막을 «…찾는게 / 강남빌딩이에요»로 나누심
X.SFX_LIST = [   # 10-20 필름 판(사장님 «처음부터 필름처럼 왼쪽으로» · «필름이 접히면서» · «누끼따서 하나씩 좀 크게»)
    (15.66 - OFFSET, "SEL_高速移動.mp3", -11, "onset", 0),                # 필름이 들어옴
    (17.47 - OFFSET, "ML_Big paper page turn.wav", -8, "onset", 0),      # 병풍처럼 접힘
    (17.768 - OFFSET, "KN_impactPunch_heavy_001.wav", -5, "onset", 0),     # 딱
    (17.88 - OFFSET, "KN_impactPunch_heavy_002.wav", -5, "onset", 0),     # 딱
    (17.99 - OFFSET, "KN_impactPunch_heavy_000.wav", -4, "onset", 0),     # 딱(가운데·제일 큼)
]
OVL_NAME = "연출층_세미나사진_강남빌딩.mov"


def _scene_name():
    return X.WORK / "r4s.mov"


_out = X.out


def out():
    # r4x_build.out 은 WORK/r4x.mov 를 연출층으로 쓴다 — 이 구간 장면 파일로 바꿔 끼운다
    src = X.WORK / "r4s_v3.mov"
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
