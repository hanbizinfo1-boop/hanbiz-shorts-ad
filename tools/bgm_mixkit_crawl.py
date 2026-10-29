"""Mixkit 무료 음악 목록 수집 (공개 페이지만, 로그인 없음).

장르 페이지를 돌며 곡 id·제목·작곡가·길이·태그·mp3 주소를 모아 JSON 으로 저장한다.
사용: python -I tools/bgm_mixkit_crawl.py 소재/BGM후보/mixkit_catalog.json
"""
import html
import json
import re
import sys
import time
import urllib.request

GENRES = [
    "corporate-music", "electronic", "electronica", "tech-house", "house", "deep-house",
    "synthpop", "lo-fi-beats", "chillout", "downtempo", "minimalism", "rhythmic-underscore",
    "underscore", "funk", "edm", "electro-house", "cinematic", "orchestral-pop", "film-score",
    "pop", "indie-pop", "dance-pop", "hip-hop", "jazz-funk", "acid-jazz", "nu-jazz",
    "electropop", "breakbeat", "trailer-music", "easy-listening", "lounge", "future-bass",
    "trap", "disco", "soul", "neo-soul", "synthwave", "percussion-trailer", "orchestral-hybrid",
]
UA = {"User-Agent": "Mozilla/5.0"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf8", "replace")


def parse(page):
    out = []
    parts = page.split('data-audio-player-preview-url-value="')[1:]
    for p in parts:
        m = re.match(r"([^\"]+)\"", p)
        url = m.group(1)
        iid = re.search(r"/music/(\d+)/", url).group(1)
        title = re.search(r'item-grid-card__title">\s*(.*?)\s*</h2>', p, re.S)
        author = re.search(r"by ([^<\n]+)", p)
        dur = re.search(r'data-test-id="duration">\s*([\d:]+)', p)
        tags = re.findall(r'meta-links__link"[^>]*href="/free-stock-music/[^"]*">([^<]+)<', p.split("item-grid-card__title")[1].split("duration")[0]) if title else []
        page_url = re.search(r'href="(/free-stock-music/[^"]*-' + iid + r'/)"', p)
        out.append({
            "id": int(iid), "title": html.unescape(title.group(1)) if title else "",
            "author": html.unescape(author.group(1).strip()) if author else "",
            "duration": dur.group(1) if dur else "", "tags": [html.unescape(t) for t in tags],
            "mp3": url, "page": "https://mixkit.co" + page_url.group(1) if page_url else "",
        })
    return out


def main(dst):
    items = {}
    for g in GENRES:
        for n in range(1, 30):
            try:
                page = get(f"https://mixkit.co/free-stock-music/{g}/?page={n}")
            except Exception as e:
                break
            got = parse(page)
            new = 0
            for it in got:
                if it["id"] not in items:
                    new += 1
                    it["genre_list"] = [g]
                    items[it["id"]] = it
                elif g not in items[it["id"]]["genre_list"]:
                    items[it["id"]]["genre_list"].append(g)
            if not got or new == 0 and n > 1:
                break
            time.sleep(0.3)
        print(g, len(items), flush=True)
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        json.dump(sorted(items.values(), key=lambda x: x["id"]), f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
