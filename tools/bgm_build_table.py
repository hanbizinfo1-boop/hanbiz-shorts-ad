"""BGM 후보 확정 목록을 폴더로 복사하고 후보표(CSV·MD)를 만든다.

입력: _tmp/bgm_all/<id>.mp3 + _tmp/bgm_all.json(실측) + 소재/BGM후보/mixkit_catalog.json(메타)
출력: 소재/BGM후보/<P1|P2|P3>/Mixkit_<곡명>.mp3, 후보표.csv, 후보표.md
"""
import csv
import json
import re
import shutil
import subprocess
import time
import urllib.request

ROOT = "소재/BGM후보"
PICK = {
    "P1": [85, 422, 746, 596, 1168, 1167, 439, 1023, 766, 704, 645, 834, 729, 486, 152, 34],
    "P2": [190, 836, 371, 720, 468, 470, 473, 469, 740, 933, 1119, 1029, 69, 732, 527, 1003],
    "P3": [725, 587, 988, 187, 88, 797, 1054, 1152, 1148, 696, 635, 569, 1002, 606, 33, 1042],
}
LIC = "Mixkit Stock Music Free License (크레딧 불필요)"


def slug(t):
    t = t.lower().replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def fname(t):
    return re.sub(r"[^A-Za-z0-9가-힣 ._-]+", "", t).strip().replace(" ", "_")


def head(url):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
    try:
        return urllib.request.urlopen(req, timeout=20).status
    except Exception as e:  # noqa
        return getattr(e, "code", 0)


def main():
    cat = {x["id"]: x for x in json.load(open(f"{ROOT}/mixkit_catalog.json", encoding="utf-8"))}
    an = {int(a["file"].split(".")[0]): a for a in json.load(open("_tmp/bgm_all.json", encoding="utf-8"))}
    rows = []
    for prof, ids in PICK.items():
        for i in ids:
            c, a = cat[i], an[i]
            dst = f"{ROOT}/{prof}/Mixkit_{fname(c['title'])}.mp3"
            shutil.copyfile(f"_tmp/bgm_all/{i}.mp3", dst)
            pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst],
                                capture_output=True, text=True)
            playable = "OK" if pr.returncode == 0 and pr.stdout.strip() else "FAIL"
            page = f"https://mixkit.co/free-stock-music/discover/{slug(c['title'])}-{i}/"
            st = head(page)
            time.sleep(1.0)
            rows.append({
                "프로필": prof, "라이브러리": "Mixkit", "곡명": c["title"], "작곡가": c["author"],
                "곡페이지URL": page if st == 200 else f"(페이지 확인 실패 {st}) {c['mp3']}",
                "다운로드URL": c["mp3"], "라이선스": LIC, "길이_s": a["duration_s"],
                "태그": " / ".join(c["tags"]), "BPM": a["bpm"], "BPM_트래커": a["bpm_tracker"],
                "LUFS": a["lufs"], "LRA": a["lra"], "첫히트_s": a["first_hit_s"],
                "드롭_s": a.get("drop_s"), "드롭_dB": a.get("drop_db"),
                "저_pct": a["low_pct"], "중_pct": a["mid_pct"], "고_pct": a["high_pct"],
                "음성대역_1to4k_pct": a["voice_1_4k_pct"], "마디_s": a.get("bar_s"), "첫박_s": a.get("first_beat_s"),
                "루프30_s": a.get("loop30_s"), "루프15_s": a.get("loop15_s"),
                "재생확인": playable, "파일": dst,
            })
            print(prof, i, c["title"], playable, st, flush=True)
    keys = list(rows[0].keys())
    with open(f"{ROOT}/후보표.csv", "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    json.dump(rows, open("_tmp/bgm_rows.json", "w", encoding="utf-8"), ensure_ascii=False)


if __name__ == "__main__":
    main()
