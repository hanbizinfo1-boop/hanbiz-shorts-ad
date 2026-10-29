# -*- coding: utf-8 -*-
r"""4번 «근데 갖고 있는 동안 돈이 되려면 / 임차인이 있어야 됩니다 / 확실한 임차인이 / 월세를 잘 내줘야 / 돈이 되는거에요» — 건물·집주인·임차인 연출 (10-20).

사장님(10-20): «근데 갖고 있는 동안 돈이 되려면 << 이 부분에 건물이 들어가고 앞에 집주인이있음
  임차인이 있어야 합니다 << 이부분에 임차인들이 꽉차서 건물안에서 활동하는 연출
  확실한 임차인이 << 이때 임차인들에게 스포트라이트효과 살짝
  월세를 잘 내줘야 << 임차인들에게서 돈이 각각 나오는 연출
  돈이 되는거에요 << 집주인에게 돈이 들어가는연출
  이 연출동안 집주인 표정은 상황에 맞게 잘 해주고»
기준 = 사장님 «4번» 저장본 14:28(자동저장 15:35): 29.446~36.086
  V1 29.446~31.181 원본 72.723 · 31.181~32.432 74.625 · 32.432~35.002 75.959 · 35.002~36.086 78.662
캐릭터 = Codex(set11_tenant) — 집주인 표정 3(걱정·기대·환호) · 임차인 6. XML V4 · A4~.

    python 지시작업/tools/r4t_build.py base / caps
    python tools/html_motion.py 지시작업/tools/scenes/r4t.html --alpha --fps 59.94 --workers 2 --sub 4 --out 지시작업/_tmp/r4t --name r4t
    python 지시작업/tools/r4t_build.py out
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r4x_build as X  # noqa: E402

OFFSET = 29.446                     # 사장님 시퀀스에서 이 구간 시작
X.WORK = X.DZ / "_tmp/r4t"
X.DELIV = X.DZ / "납품/4번_집주인_임차인_월세_1020"
X.NAME = "4번_집주인_임차인_월세"
X.END = 36.086 - OFFSET
X.CUTS = [(0.0, 31.181 - OFFSET, 72.723), (31.181 - OFFSET, 32.432 - OFFSET, 74.625), (32.432 - OFFSET, 35.002 - OFFSET, 75.959), (35.002 - OFFSET, 36.086 - OFFSET, 78.662)]
X.ZOOM = dict(t0=99, dur=0.131, s=1.0, dx=0)
X.CAPS = [(0.0, 30.397 - OFFSET, [("근데 갖고 있는 동안", 0)]), (30.397 - OFFSET, 31.181 - OFFSET, [("돈이 되려면", 0)]),
          (31.181 - OFFSET, 32.432 - OFFSET, [("임차인이 있어야 됩니다", 0)]), (32.432 - OFFSET, 33.4 - OFFSET, [("확실한 임차인이", 0)]),
          (33.4 - OFFSET, 35.002 - OFFSET, [("월세를 잘 내줘야", 0)]), (35.002 - OFFSET, 36.086 - OFFSET, [("돈이 되는거에요", 0)])]
X.SFX_LIST = [   # 사장님 통과 소리 위주
    (29.46 - OFFSET, "8. 훅.mp3", -6, "onset", 0),                  # 건물 + 집주인 등장
    (31.19 - OFFSET, "6. SE_블록소리.mp3", -8, "onset", 0),          # 방에 불 켜지며 임차인 꽉 참
    (32.44 - OFFSET, "SEL_キラッ1.mp3", -9, "onset", 0),             # 스포트라이트
    (33.41 - OFFSET, "코인획득.mp3", -7, "onset", 0),                 # 임차인마다 돈 나옴
    (35.01 - OFFSET, "14. 짜잔.wav", -7, "onset", 0),                 # 돈이 집주인에게 → 환호
]
OVL_NAME = "연출층_집주인_임차인_월세.mov"


def _scene_name():
    return X.WORK / "r4t.mov"


_out = X.out


def out():
    # r4x_build.out 은 WORK/r4x.mov 를 연출층으로 쓴다 — 이 구간 장면 파일로 바꿔 끼운다
    src = X.WORK / "r4t.mov"
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
        n = len(X.CUTS)
        ins = sum([["-i", str(X.WORK / f"V1_{k + 1}.mov")] for k in range(n)], [])
        fc = "".join(f"[{k}:v][{k}:a]" for k in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
        subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "prores_ks", "-profile:v", "1",
                        "-c:a", "pcm_s16le", str(X.WORK / "base_full.mov")], check=True)
    else:
        {"caps": X.caption_layer, "out": out}[cmd]()
