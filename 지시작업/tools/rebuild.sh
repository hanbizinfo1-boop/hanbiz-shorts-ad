#!/usr/bin/env bash
# A지시판 전체 다시 만들기: 장면 렌더 → 배치표 → 미리보기 → XML(+대조) → 효과음 점검 → 납품 교체
set -e
cd "$(dirname "$0")/../.."
export PYTHONIOENCODING=utf-8
D=지시작업/납품/한비즈_DB광고1_A지시_1014
N=$D/_새판
python tools/html_motion.py 지시작업/tools/scenes/a_direct.html --alpha --fps 30 --workers 2 --sub 3 --out 지시작업/_tmp/a --name a_direct 2>&1 | grep -E "ERROR|완료"
python 지시작업/tools/ad_build.py plan
python tools/edit_render.py 지시작업/_tmp/a/plan_A지시.json --out $N/한비즈_DB광고1_A지시.mp4 2>&1 | grep -E "마감 후|트루피크|규칙 점검|\[ERROR"
python tools/edit_xml.py 지시작업/_tmp/a/plan_A지시.json --out $N --미리보기 $N/한비즈_DB광고1_A지시.mp4 2>&1 | grep -E "파일 |화면:|소리:"
cp 지시작업/_tmp/a/한비즈_DB광고1_A지시.srt $D/읽어보기.md $N/
python tools/deliver_swap.py $D
python 지시작업/tools/sfxchk.py | tail -12
echo REBUILD_DONE
