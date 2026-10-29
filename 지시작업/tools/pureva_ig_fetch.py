"""퓨레바 공식 인스타(@pureva_chlorella) 게시물 이미지·영상 내려받기 — Apify instagram-scraper 결과(JSON) → 소재 폴더.

python 지시작업/tools/pureva_ig_fetch.py <apify 결과 json> <저장 폴더>
파일 이름 = 날짜_shortCode_순번.jpg|mp4 · 목록 `_목록.csv`(날짜·shortCode·종류·원본 게시물 주소).
브랜드 공식 계정 콘텐츠만(10-22 대표 «퓨레바 브랜드 콘텐츠는 초상권·저작권 문제없이 쓸 수 있다»).
"""
import csv
import json
import sys
import urllib.request
from pathlib import Path


def get(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        path.write_bytes(r.read())


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    data = json.loads(src.read_text(encoding="utf-8"))
    items = data["items"] if isinstance(data, dict) else data
    rows, n = [], 0
    for it in items:
        sc = it.get("shortCode")
        if not sc:
            continue
        day = (it.get("timestamp") or "")[:10]
        urls = list(dict.fromkeys(it.get("images") or [])) or [it.get("displayUrl")]
        media = [(u, "jpg") for u in urls if u]
        if it.get("videoUrl"):
            media.append((it["videoUrl"], "mp4"))
        for k, (u, ext) in enumerate(media, 1):
            p = out / f"{day}_{sc}_{k:02d}.{ext}"
            if not p.exists():
                try:
                    get(u, p)
                    n += 1
                except Exception as e:  # 만료 등 — 목록에 표시
                    print("실패", p.name, e)
                    continue
            rows.append([day, sc, it.get("type"), p.name, f"https://www.instagram.com/p/{sc}/"])
    with open(out / "_목록.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["날짜", "shortCode", "종류", "파일", "원본 게시물"])
        w.writerows(rows)
    print(f"새로 받은 파일 {n} · 목록 {len(rows)}줄 → {out}")


if __name__ == "__main__":
    main()
