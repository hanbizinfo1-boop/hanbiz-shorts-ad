"""분양 대본 6편 → PDF 2개(3편씩, 한 쪽에 대본 하나) — 10-29.

사장님이 저장한 txt 두 개를 글자 그대로 읽는다(줄·빈 줄 그대로, 줄 끝 공백만 버림).
쪽마다 «번호. 제목»(A·H·I·J·K·L → 1~6) + 대본. 가장 긴 대본이 한 쪽에 들어가는 글자 크기를 골라 모든 쪽에 같이 쓴다.
렌더는 Edge headless(맑은 고딕), 검산은 pymupdf(쪽 수 · 쪽마다 글자 대조).
사용: python -X utf8 지시작업/tools/bunyang_script_pdf.py  (6편 → 2개)
      python -X utf8 지시작업/tools/bunyang_script_pdf.py <대본.txt> <이름.pdf>  (txt 하나 → PDF 하나)
"""
import html
import re
import subprocess
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
DLV = ROOT / "납품"
SRC = [DLV / "분양_청량대본_8안_1029" / "분양_청량대본_8안_대본만.txt",
       DLV / "분양_청량대본_추가4안_1029" / "분양_청량대본_추가4안_대본만.txt"]
OUT = DLV / "분양_대본_PDF_1029"
GROUPS = {"분양_대본_1편.pdf": ["A", "H", "I"], "분양_대본_2편.pdf": ["J", "K", "L"]}
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# A4 297mm − 위아래 여백 18mm×2 = 261mm 에 제목(약 2줄) + 대본 줄
PAGE_MM, LINE_H = 261, 1.55


def scripts():
    out = {}
    for p in SRC:
        t = p.read_text(encoding="utf-8")
        for m in re.finditer(r"^\[(([A-Z])\..+?)\]\n(.*?)(?=^\[|\Z)", t, re.S | re.M):
            lines = [ln.rstrip() for ln in m.group(3).strip("\n").split("\n")]
            out[m.group(2)] = (m.group(1).split(". ", 1)[1], lines)   # 알파벳 떼고 제목만
    for n, k in enumerate("AHIJKL", 1):                              # 10-29 «알파벳빼고 1~6»
        out[k] = (f"{n}. {out[k][0]}", out[k][1])
    return out


def page_html(title, lines, pt):
    body = "\n".join(html.escape(ln) if ln else "&nbsp;" for ln in lines)
    return f'<section><h1>{html.escape(title)}</h1><pre>{body}</pre></section>'


def build(name, keys, sc, pt):
    css = f"""@page {{ size: A4; margin: 18mm 22mm; }}
body {{ margin: 0; font-family: 'Malgun Gothic'; color: #111; }}
section {{ page-break-after: always; break-inside: avoid; }}
section:last-child {{ page-break-after: auto; }}
h1 {{ font-size: {pt + 3}pt; margin: 0 0 {pt * 0.9:.1f}pt; font-weight: 700; }}
pre {{ font-family: inherit; font-size: {pt}pt; line-height: {LINE_H}; margin: 0;
      white-space: pre-wrap; letter-spacing: -0.01em; }}"""
    doc = f"<!doctype html><meta charset=utf-8><style>{css}</style>" + \
        "".join(page_html(*sc[k], pt) for k in keys)
    tmp = OUT / f"_{name}.html"
    tmp.write_text(doc, encoding="utf-8")
    pdf = OUT / name
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", tmp.as_uri()], check=True, capture_output=True)
    tmp.unlink()
    return pdf


def check(pdf, keys, sc):
    d = pymupdf.open(pdf)
    assert d.page_count == len(keys), f"{pdf.name}: {d.page_count}쪽 (기대 {len(keys)})"
    for i, k in enumerate(keys):
        got = re.sub(r"\s", "", d[i].get_text())
        want = re.sub(r"\s", "", sc[k][0] + "".join(sc[k][1]))
        assert got == want, f"{pdf.name} {i + 1}쪽 글자 불일치"
    d.close()


def one(txt, pdf_name):
    """«[번호. 제목]» 블록 txt 하나 → 같은 폴더에 PDF 하나(쪽당 대본 하나). 10-29 수정안 3·4·5."""
    global OUT
    txt = Path(txt).resolve()
    OUT = txt.parent
    t = txt.read_text(encoding="utf-8")
    sc = {}
    for m in re.finditer(r"^\[(.+?)\]\n(.*?)(?=^\[|\Z)", t, re.S | re.M):
        sc[str(len(sc))] = (m.group(1), [ln.rstrip() for ln in m.group(2).strip("\n").split("\n")])
    keys = list(sc)
    longest = max(len(v[1]) for v in sc.values())
    pt = 13.0
    while (longest * pt * LINE_H + (pt + 3) * 2.2) * 0.3528 > PAGE_MM:
        pt -= 0.5
    pdf = build(pdf_name, keys, sc, pt)
    check(pdf, keys, sc)
    print(pdf_name, len(keys), "쪽", f"{pt}pt", "쪽 수·글자 대조 통과")


def main():
    OUT.mkdir(exist_ok=True)
    sc = scripts()
    assert set(sc) == {"A", "H", "I", "J", "K", "L"}, sorted(sc)
    longest = max(len(v[1]) for v in sc.values())
    pt = 13.0
    while (longest * pt * LINE_H + (pt + 3) * 2.2) * 0.3528 > PAGE_MM:   # pt → mm
        pt -= 0.5
    for name, keys in GROUPS.items():
        pdf = build(name, keys, sc, pt)
        check(pdf, keys, sc)
        print(name, keys, f"{pt}pt", "쪽 수·글자 대조 통과")


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:      # python … <대본.txt> <출력.pdf 이름>
        one(sys.argv[1], sys.argv[2])
    else:
        main()
