# -*- coding: utf-8 -*-
r"""4번 «적어도 강남빌딩은 물가상승률보다 더 올라가잖아요» — 연도별 상승률 비교, 굴곡진 점선 그래프 (10-20).

사장님(10-20): «적어도 강남빌딩은 물가상승률보다 더 올라가잖아요 << 이부분 년도그래프로 물가상승률이랑 비교그래프 %로 실질데이터로 표현해봐 굴곡진 점선 그래프로»
실질 데이터(2006 = 0%, 누적 상승률)
  강남 꼬마빌딩: 연금형부동산연구소 «빌딩거래량.png» 토지금액(꼬마빌딩 기준, 평당 만원)
     06 987 · 07 1068 · 08 1441 · 09 1195 · 10 1510 · 11 1381 · 12 1547 · 13 1491 · 14 1522 · 15 1626 · 16 1805 · 17 2213 · 18 2184 · 19 2450 · 20 2971 · 21 3854 · 22 4285 · 23 4523 → +358%
  소비자물가: 통계청 소비자물가지수 연간 상승률(%) 07 2.5 · 08 4.7 · 09 2.8 · 10 2.9 · 11 4.0 · 12 2.2 · 13 1.3 · 14 1.3 · 15 0.7 · 16 1.0 · 17 1.9 · 18 1.5 · 19 0.4 · 20 0.5 · 21 2.5 · 22 5.1 · 23 3.6 → 누적 +47%
     (이 값은 내가 아는 공표치로 넣음 — 사장님 확인 필요)
기준 = 사장님 «4번» 자동저장 14:12: 18.835~22.222 (V1 18.835~21.188 원본 57.741 · 21.188~22.222 원본 60.177). XML V4 · A4~.

    python 지시작업/tools/r4g_build.py base / caps
    python tools/html_motion.py 지시작업/tools/scenes/r4g.html --alpha --fps 59.94 --workers 2 --sub 4 --out 지시작업/_tmp/r4g --name r4g
    python 지시작업/tools/r4g_build.py out
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r4x_build as X  # noqa: E402

OFFSET = 18.835                     # 사장님 시퀀스에서 이 구간 시작
X.WORK = X.DZ / "_tmp/r4g"
X.DELIV = X.DZ / "납품/4번_강남빌딩_물가비교그래프_1020"
X.NAME = "4번_강남빌딩_물가비교그래프"
X.END = 22.222 - OFFSET
X.CUTS = [(0.0, 21.188 - OFFSET, 57.741), (21.188 - OFFSET, 22.222 - OFFSET, 60.177)]
X.ZOOM = dict(t0=99, dur=0.131, s=1.0, dx=0)
X.CAPS = [(0.0, 19.987 - OFFSET, [("적어도 강남빌딩은", 0)]), (19.987 - OFFSET, 21.188 - OFFSET, [("물가상승률보다", 0)]),
          (21.188 - OFFSET, 22.222 - OFFSET, [("더 올라가잖아요", 0)])]
X.SFX_LIST = [   # 통과 목록 소리 위주
    (18.84 - OFFSET, "휙２.mp3", -10, "onset", 0),                    # 그래프 판 올라옴
    (19.99 - OFFSET, "SEL_シャーペンで字を書く.mp3", -12, "onset", 0),  # 물가 선 그려짐(펜)
    (21.19 - OFFSET, "SEL_高速移動.mp3", -9, "onset", 0),             # 빌딩 선 쭉 치솟음
    (21.91 - OFFSET, "띠링.mp3", -8, "onset", 0),                     # +358% 뜸
]
OVL_NAME = "연출층_강남빌딩_물가비교그래프.mov"


def _scene_name():
    return X.WORK / "r4g.mov"


_out = X.out


def out():
    # r4x_build.out 은 WORK/r4x.mov 를 연출층으로 쓴다 — 이 구간 장면 파일로 바꿔 끼운다
    src = X.WORK / "r4g.mov"
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
