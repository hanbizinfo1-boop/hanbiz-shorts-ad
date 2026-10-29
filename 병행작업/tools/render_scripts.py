"""대본 3안 납품물 전부 다시 뽑기 — 장면표 PDF 3개 + 대본만 PDF + 대본만 TXT(시간 없음, 복붙용).

사용: python 병행작업/tools/render_scripts.py [판]   예) v2 → 기록/*_1012_v2.html → 납품/대본3안_제조업_v2_1012/ (판마다 새 폴더, 기존 판은 그대로)
장면표 HTML(병행작업/기록/대본{1,2,3}안_*.html)을 고친 뒤 이것 하나만 돌린다. 같은 이름 제자리 덮어쓰기.
"""
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import script_only as so  # noqa: E402

OUT = so.ROOT / "납품" / "대본3안_제조업_1012"
PAIRS = [
    ("대본1안_통보반전_1012", "한비즈_제조업_1안_통보반전"),
    ("대본2안_돈주세요_1012", "한비즈_제조업_2안_돈주세요"),
    ("대본3안_엿듣는대화_1012", "한비즈_제조업_3안_엿듣는대화"),
]


def pdf(src_html, out_pdf):
    subprocess.run([so.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--user-data-dir={so.ROOT / '_tmp' / 'chrome'}", f"--print-to-pdf={out_pdf}",
                    src_html.as_uri()], capture_output=True, timeout=120)


def plain_text(src_list, out_dir, suffix):
    out = []
    for fn, title, _cast, _top in src_list:
        out.append(f"[{title}]")
        out += [f"{so.NAMES.get(sp, sp)}: {line}" for _, sp, line in so.rows(so.REC / fn)]
        out.append("")
    txt = "\n".join(out).rstrip() + "\n"
    (out_dir / f"한비즈_제조업_대본만_3안{suffix}.txt").write_text(txt, encoding="utf-8", newline="\n")
    return txt


if __name__ == "__main__":
    ver = sys.argv[1] if len(sys.argv) > 1 else ""
    sfx = f"_{ver}" if ver else ""
    out_dir = so.ROOT / "납품" / (f"대본3안_제조업_{ver}_1012" if ver else "대본3안_제조업_1012")
    out_dir.mkdir(parents=True, exist_ok=True)
    src_list = [(fn.replace(".html", f"{sfx}.html"), *rest) for fn, *rest in so.SRC]
    for s, d in PAIRS:
        pdf(so.REC / f"{s}{sfx}.html", out_dir / f"{d}{sfx}.pdf")
    so.build(src_list, out_dir / f"한비즈_제조업_대본만_3안{sfx}.pdf", f"대본만_3안_1012{sfx}.html", f" · {ver}" if ver else "")
    print(plain_text(src_list, out_dir, sfx))
