#!/usr/bin/env bash
# A지시 메타판 전체 만들기(메타 릴스 안전 영역 y 270~1250) — 장면 → 배치표 → 미리보기 → XML(+대조) → _새판 교체 → 효과음 점검
set -e
cd "$(dirname "$0")/../.."
export PYTHONIOENCODING=utf-8 AD_VER=meta
D=지시작업/납품/한비즈_DB광고1_A지시_메타_1014
N=$D/_새판
mkdir -p $N
python tools/html_motion.py 지시작업/tools/scenes/a_direct_meta.html --alpha --fps 30 --workers 2 --sub 3 --out 지시작업/_tmp/a_meta --name a_direct_meta 2>&1 | grep -E "ERROR|완료"
python 지시작업/tools/ad_build.py plan
python tools/edit_render.py 지시작업/_tmp/a_meta/plan_A지시.json --out $N/한비즈_DB광고1_A지시.mp4 2>&1 | grep -E "마감 후|트루피크|규칙 점검|\[ERROR"
python tools/edit_xml.py 지시작업/_tmp/a_meta/plan_A지시.json --out $N --미리보기 $N/한비즈_DB광고1_A지시.mp4 2>&1 | grep -E "파일 |화면:|소리:"
cp 지시작업/_tmp/a_meta/한비즈_DB광고1_A지시.srt $N/
python tools/deliver_swap.py $D
python 지시작업/tools/fix_meta_src.py
python 지시작업/tools/sfxchk.py $D 지시작업/_tmp/a_meta/plan_A지시.json | tail -14
echo REBUILD_DONE
