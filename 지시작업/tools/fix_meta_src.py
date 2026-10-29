# -*- coding: utf-8 -*-
"""메타판 XML 의 사람 사본 경로를 _tmp → 납품 media 로(_tmp 를 지워도 프리미어에서 안 끊기게). rebuild_meta.sh 가 교체 뒤에 부른다."""
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

R = Path(__file__).resolve().parents[1]
# 인자: <납품 폴더 이름> <사본 파일 이름> — 기본은 메타판
D = R / "납품" / (sys.argv[1] if len(sys.argv) > 1 else "한비즈_DB광고1_A지시_메타_1014")
NAME = sys.argv[2] if len(sys.argv) > 2 else "1013_meta.mp4"
src, dst = R / "_tmp/src" / NAME, D / "media" / NAME
shutil.copy2(src, dst)
x = D / "한비즈_DB광고1_A지시.xml"
s = x.read_text(encoding="utf-8")
s = s.replace("file://localhost/" + quote(src.as_posix()), "file://localhost/" + quote(dst.as_posix()))
x.write_text(s, encoding="utf-8", newline="\n")
print("사람 사본 →", dst, "· _tmp 참조", s.count("_tmp"))
