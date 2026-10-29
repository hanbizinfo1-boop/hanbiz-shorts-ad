# -*- coding: utf-8 -*-
"""hanbiz_logo_laser.html 안의 PATHS 를 소재/브랜드/logo_paths.json 으로 갱신한다.
(HTML 은 file:// 에서 JSON 을 못 읽으므로 경로 문자열을 HTML 안에 박아 둔다. 경로를 다시 뽑았으면 이 스크립트를 한 번 돌린다.)
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "tools" / "scenes" / "html" / "hanbiz_logo_laser.html"
J = ROOT / "소재" / "브랜드" / "logo_paths.json"

j = json.loads(J.read_text(encoding="utf-8"))
js = json.dumps({"paths": [{"id": p["id"], "d": p["d"], "length": p["length"]} for p in j["paths"]]}, ensure_ascii=False)
s = HTML.read_text(encoding="utf-8")
s2, n = re.subn(r"/\*PATHS_JSON\*/.*?/\*END\*/", lambda m: "/*PATHS_JSON*/" + js + "/*END*/", s, count=1, flags=re.S)
assert n == 1, "PATHS_JSON 표시를 못 찾았다"
HTML.write_text(s2, encoding="utf-8", newline="\n")
print("PATHS 갱신:", [p["id"] for p in j["paths"]])
