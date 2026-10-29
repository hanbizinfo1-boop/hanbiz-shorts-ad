"""3안 타이포 스토리보드 정지 화면 뜨기 — tools/scenes/html/hanbiz_3an_board.html 을 마디·단계별로 1080×1920 PNG.

    python tools/scenes/hanbiz_3an_board.py [--out _tmp/board3]
크롬은 이 스크립트가 띄운 것만 쓴다(전용 프로필 폴더) — 사용자 크롬을 건드리지 않는다.
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
HTML = Path(__file__).resolve().parent / "html" / "hanbiz_3an_board.html"
SHOTS = [(1, "in"), (1, "hold"), (2, "in"), (2, "out"), (3, "in"), (3, "hold"), (4, "in"), (4, "hold"),
         (5, "in"), (5, "hold"), (5, "out"), (7, "in"), (7, "out"), (8, "in"), (8, "hold"),
         (9, "in"), (9, "out"), (10, "in"), (10, "hold")]


def main():
    ap = argparse.ArgumentParser(description="3안 스토리보드 정지 화면")
    ap.add_argument("--out", default=str(ROOT / "_tmp" / "board3"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    prof = ROOT / "_tmp" / "chrome_board_profile"
    for bar, ph in SHOTS:
        png = out / f"bar{bar:02d}_{ph}.png"
        url = HTML.as_uri() + f"?bar={bar}&ph={ph}"
        subprocess.run([str(config.CHROME), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--user-data-dir={prof}", "--allow-file-access-from-files",
                        "--window-size=1080,1920", "--virtual-time-budget=1500",
                        f"--screenshot={png}", url], check=True, capture_output=True, timeout=60)
        print(png.name)


if __name__ == "__main__":
    main()
