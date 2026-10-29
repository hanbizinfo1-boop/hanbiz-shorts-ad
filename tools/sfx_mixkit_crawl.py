"""Mixkit 무료 효과음 목록 수집 (공개 페이지만, 로그인 없음 · bgm_mixkit_crawl.py 와 같은 방식).

태그 페이지를 돌며 id·제목·길이·태그·미리듣기 mp3 주소를 모아 JSON 으로 저장한다.
사용: python -I tools/sfx_mixkit_crawl.py <출력.json> [태그 ...]
"""
import html
import json
import re
import sys
import time
import urllib.request

TAGS = ["whoosh", "swoosh", "swish", "transition", "rewind", "sweep", "swell", "cymbal", "crash", "cinematic",
        "intro", "high-tech", "technology", "interface", "tones", "bell", "chimes", "instrument", "piano",
        "bleep", "tap", "click", "notification", "page", "paper", "slide", "drop", "key", "office",
        "wood", "sparkle", "impact", "hit", "glitch", "movie", "spin", "zoom", "pop", "thud", "type", "write"]
UA = {"User-Agent": "Mozilla/5.0"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf8", "replace")


def parse(page):
    out = []
    for p in page.split('data-audio-player-preview-url-value="')[1:]:
        url = re.match(r"([^\"]+)\"", p).group(1)
        iid = re.search(r"/sfx/(\d+)/", url).group(1)
        title = re.search(r'item-grid-card__title">\s*(.*?)\s*</h2>', p, re.S)
        dur = re.search(r'data-test-id="duration">\s*([\d:]+)', p)
        seg = p.split("item-grid-card__title")[1].split("duration")[0] if title else ""
        tags = re.findall(r'meta-links__link"[^>]*href="/free-sound-effects/[^"]*">([^<]+)<', seg)
        out.append({"id": int(iid), "title": html.unescape(title.group(1)) if title else "",
                    "duration": dur.group(1) if dur else "", "tags": [html.unescape(t) for t in tags],
                    "mp3": url})
    return out


def main(dst, tags):
    items = {}
    for g in tags:
        for n in range(1, 30):
            try:
                got = parse(get(f"https://mixkit.co/free-sound-effects/{g}/?page={n}"))
            except Exception:
                break
            new = 0
            for it in got:
                if it["id"] not in items:
                    new += 1
                    it["tag_list"] = [g]
                    items[it["id"]] = it
                elif g not in items[it["id"]]["tag_list"]:
                    items[it["id"]]["tag_list"].append(g)
            if not got or new == 0 and n > 1:
                break
            time.sleep(0.3)
        print(g, len(items), flush=True)
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        json.dump(sorted(items.values(), key=lambda x: x["id"]), f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:] or TAGS)
