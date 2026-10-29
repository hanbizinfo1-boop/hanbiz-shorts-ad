#!/usr/bin/env bash
# 메타v2 소리만 다시(장면 MOV 그대로) — 배치표 → 미리보기 → XML(+대조) → 교체 → 효과음 점검
set -e
cd "$(dirname "$0")/../.."
export PYTHONIOENCODING=utf-8 AD_VER=meta2
D=지시작업/납품/한비즈_DB광고1_A지시_메타v2_1014
N=$D/_새판
mkdir -p $N
python 지시작업/tools/ad_build.py plan
python tools/edit_render.py 지시작업/_tmp/a_meta2/plan_A지시.json --out $N/한비즈_DB광고1_A지시.mp4 2>&1 | grep -E "마감 후|트루피크|규칙 점검|\[ERROR"
python tools/edit_xml.py 지시작업/_tmp/a_meta2/plan_A지시.json --out $N --미리보기 $N/한비즈_DB광고1_A지시.mp4 2>&1 | grep -E "파일 |화면:|소리:"
cp 지시작업/_tmp/a_meta2/한비즈_DB광고1_A지시.srt $N/
python tools/deliver_swap.py $D
python 지시작업/tools/fix_meta_src.py 한비즈_DB광고1_A지시_메타v2_1014 1013_v2.mp4
python 지시작업/tools/sfxchk.py $D 지시작업/_tmp/a_meta2/plan_A지시.json | tail -14
echo REBUILD_DONE
