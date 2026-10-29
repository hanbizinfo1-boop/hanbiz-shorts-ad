"""대본 장면표 HTML 에서 대사만 뽑아 «대본만» 문서(HTML → PDF)를 만든다.

사용: python 병행작업/tools/script_only.py
입력: 병행작업/기록/대본{1,2,3}안_*.html 의 대본 표(td.na = 대사 칸, 첫 칸 = 초)
출력: 병행작업/기록/대본만_3안_1012.html → 병행작업/납품/대본3안_제조업_1012/한비즈_제조업_대본만_3안.pdf
"""
import html
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
REC = ROOT / "기록"
OUT_PDF = ROOT / "납품" / "대본3안_제조업_1012" / "한비즈_제조업_대본만_3안.pdf"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

SRC = [
    ("대본1안_통보반전_1012.html", "1안 · 통보 반전", "A 컨설턴트 · B 제조업 대표", "제조업 대표님 / 정책자금, 받고 끝이 아닙니다"),
    ("대본2안_돈주세요_1012.html", "2안 · «기계 한 대만 사 주세요»", "A 컨설턴트 · B1 금속가공 대표 · B2 식품 제조 대표 · B3 청년 창업 대표", "제조업 정책자금 / 공장 사정마다 따로 있습니다"),
    ("대본3안_엿듣는대화_1012.html", "3안 · 엿듣는 대화", "C 대표 · D 대표 · A 컨설턴트", "1억 빌리면 1년 이자 1,150만원 차이 / 제조업 정책자금 확인하세요"),
]
NAMES = {"A": "컨설턴트", "B": "대표", "B1": "금속가공 대표", "B2": "식품 제조 대표", "B3": "청년 창업 대표", "C": "C 대표", "D": "D 대표"}
EXTRA = {2: " 이자 비교는 1억원 1년 예시입니다."}
FINE = "※ 승인 여부·한도는 기관 심사에 따라 달라집니다. 수임료·용역비는 상담 때 안내드립니다."


def rows(path):
    """(초, 화자, 대사) 목록. 화자 표시가 없는 대사는 직전 화자."""
    s = path.read_text(encoding="utf-8")
    table = s.split('<table class="scene">', 1)[1].split("</table>", 1)[0]
    out = []
    for tr in re.findall(r"<tr>(.*?)</tr>", table, re.S):
        t = re.search(r'<td class="t">(.*?)</td>', tr)
        na = re.search(r'<td class="na">(.*?)</td>', tr, re.S)
        if not (t and na):
            continue
        speaker = out[-1][1] if out else "A"
        for part in re.split(r"<br\s*/?>", na.group(1)):
            # 한 칸 안에 화자가 여러 번 바뀌면 화자 표시마다 끊는다
            for seg in re.split(r'(?=<span class="who-[ab]">)', part):
                m = re.match(r'<span class="who-[ab]">(\w+)</span>\s*', seg)
                if m:
                    speaker, seg = m.group(1), seg[m.end():]
                line = html.unescape(re.sub(r"<[^>]+>", "", seg)).strip()
                if line:
                    out.append((t.group(1), speaker, line))
    return out


def build(src_list=None, out_pdf=None, html_name="대본만_3안_1012.html", tag=""):
    src_list = src_list or SRC
    out_pdf = out_pdf or OUT_PDF
    body = []
    for i, (fn, title, cast, top) in enumerate(src_list):
        rs = rows(REC / fn)
        lines = []
        for sec, sp, line in rs:
            who = NAMES.get(sp, sp)
            lines.append(f'<tr><td class="t">{sec}</td><td class="sp">{who}</td><td class="ln">{html.escape(line)}</td></tr>')
        body.append(f"""<section{' class="sec"' if i else ''}>
<div class="kicker">HANBIZ · 제조업 · 대본만 · 2026-10-12{tag}</div>
<h1>{title}</h1>
<p class="q">출연: {cast}</p>
<p class="q">화면 위 고정 제목: «{top}»</p>
<table class="sc">{''.join(lines)}</table>
<p class="src">끝 화면 작은 고지: {FINE}{EXTRA.get(i, "")}</p>
</section>""")
    doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>대본만 3안</title>
<link rel="stylesheet" href="문서스타일.css">
<style>
.sc td{{border:none;border-bottom:.5pt solid var(--line);padding:3.5pt 4pt}}
.sc .sp{{width:22%;font-weight:700;color:var(--royal);white-space:nowrap}}
.sc .ln{{font-size:11.6pt;font-weight:600;line-height:1.45}}
</style></head><body>{''.join(body)}</body></html>"""
    src = REC / html_name
    src.write_text(doc, encoding="utf-8", newline="\n")
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--user-data-dir={ROOT / '_tmp' / 'chrome'}", f"--print-to-pdf={out_pdf}", src.as_uri()],
                   capture_output=True, timeout=120)
    return src, out_pdf


if __name__ == "__main__":
    print(*build(), sep="\n")
