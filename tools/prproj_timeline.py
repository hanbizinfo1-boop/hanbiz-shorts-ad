"""[한비즈 쇼츠 이식본 — 원본 D:/영상제작/도구/읽기/prproj_timeline.py, 내용 그대로]
프리미어 프로젝트에서 타임라인 배치를 전수로 뽑는다.
    python prproj_timeline.py <사본.prproj> <출력.json>   (자동저장본이 가장 최신 — 사본을 떠서 읽는다)

구조 (실측으로 확인)
  AudioClipTrackItem / VideoClipTrackItem
    └ ClipTrackItem
        ├ TrackItem → Start / End   (틱, 1초 = 254016000000)
        └ SubClip ObjectRef=…  →  SubClip → Name (파일명)

읽기 전용.
"""

import gzip
import json
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

TICKS = 254016000000


def main():
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)

    root = ET.fromstring(gzip.open(src, "rb").read())
    byid = {el.get("ObjectID"): el for el in root.iter() if el.get("ObjectID")}

    def text_of(el, path):
        n = el.find(path)
        return n.text.strip() if (n is not None and n.text) else None

    items = []
    for kind in ("AudioClipTrackItem", "VideoClipTrackItem"):
        for el in root.iter(kind):
            cti = el.find("ClipTrackItem")
            if cti is None:
                continue
            ti = cti.find("TrackItem")
            if ti is None:
                continue
            s = ti.find("Start")
            e = ti.find("End")
            if e is None:
                continue
            try:
                start = int(s.text) if (s is not None and s.text) else 0
                end = int(e.text)
            except (ValueError, TypeError):
                continue

            name = None
            sc = cti.find("SubClip")
            if sc is not None and sc.get("ObjectRef"):
                sub = byid.get(sc.get("ObjectRef"))
                if sub is not None:
                    name = text_of(sub, "Name")

            items.append({
                "kind": kind,
                "name": name or "(이름없음)",
                "start": start / TICKS,
                "end": end / TICKS,
            })

    items.sort(key=lambda x: x["start"])
    out.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")

    # 요약
    grp = defaultdict(list)
    for it in items:
        grp[(it["kind"], it["name"])].append(it)

    print(f"트랙 아이템 총 {len(items):,}개")
    print()
    print("=== 소재별 사용 횟수 ===")
    for (kind, name), lst in sorted(grp.items(), key=lambda kv: -len(kv[1])):
        dur = sum(x["end"] - x["start"] for x in lst)
        tag = "오디오" if kind.startswith("Audio") else "비디오"
        print(f"  {tag}  {name[:44]:46s} {len(lst):5d}회  총 {dur:8.1f}초")
    print()
    print(f"저장: {out}")


if __name__ == "__main__":
    main()
