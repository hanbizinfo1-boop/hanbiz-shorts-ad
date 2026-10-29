"""효과음 라이브러리를 등급별(A★/A/B/C) 폴더로 묶어 zip 하나로 만든다 — 직원 배포용(10-29).

등급은 tools/data/예능효과음-등급.json. 등급표에 없는 파일은 «미등급», 장면음 폴더는 «장면음» 으로.
zip 안 경로: <등급>/<분류>/<파일>. 같은 이름이 겹치면 출처 폴더 이름을 앞에 붙인다.
사용: python -X utf8 tools/sfx_pack.py <출력.zip>
"""
import json
import sys
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "소재" / "효과음"
GRADE = ROOT / "tools" / "data" / "예능효과음-등급.json"
AUDIO = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}
GRADE_DIR = {"A★": "1_A★_사장님사용", "A": "2_A", "B": "3_B", "C": "4_C"}


def nfc(s):
    return unicodedata.normalize("NFC", s)


def main(out):
    rows = json.loads(GRADE.read_text(encoding="utf-8"))
    by_name = {}
    for r in rows:
        by_name.setdefault(nfc(Path(r["파일"].replace("\\", "/")).name), r)

    used, cnt = set(), Counter()
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as z:   # 음원은 이미 압축돼 있어 저장만
        for f in sorted(LIB.rglob("*")):
            if not f.is_file() or f.suffix.lower() not in AUDIO:
                continue
            rel = f.relative_to(LIB)
            r = by_name.get(nfc(f.name))
            if rel.parts[0] == "장면음":
                arc = Path("5_장면음") / Path(*rel.parts[1:])
                cnt["장면음"] += 1
            elif r:
                arc = Path(GRADE_DIR[r["등급"]]) / r["분류"] / f.name
                cnt[r["등급"]] += 1
            else:
                arc = Path("6_미등급") / Path(*rel.parts)
                cnt["미등급"] += 1
            key = nfc(arc.as_posix())
            if key in used:
                arc = arc.with_name(f"{rel.parts[0]}_{f.name}")
                key = nfc(arc.as_posix())
            used.add(key)
            z.write(f, key)
        z.write(GRADE, "예능효과음-등급.json")
        z.writestr("읽어보기.txt", README)
    print(dict(cnt), "합계", sum(cnt.values()), "→", out, f"{out.stat().st_size / 1e6:.0f}MB")


README = """한비즈 효과음 라이브러리 — 등급별 (직원 전용, 외부 공유·재배포 금지)

1_A★_사장님사용 : 사장님이 실제 편집에 쓰신 소리
2_A / 3_B / 4_C  : 분류(쿵쾅·뿅·휙·종이 …)마다 점수순 등급. A부터 고르고, 맞는 게 없을 때만 다음 등급
5_장면음         : 장면용으로 묶거나 가공한 소리
6_미등급         : 등급표에 없는 파일
예능효과음-등급.json : 파일별 분류·점수·소재상태(셸빙/페이드인 필요 여부)

라이선스: Mixkit(ML_)·効果音ラボ(SEL_)는 소재 단독 재배포 금지 — 영상에 넣어 쓰는 건 되고, 파일을 외부에 올리거나 넘기면 안 된다.
Kenney(KN_)는 CC0. 쓰는 법·크기·겹침 규칙은 GitHub 저장소 .claude/skills/shorts-ad/references/sfx.md
설치: 아무 폴더에 풀고 환경변수 HANBIZ_SFX_LIB 를 그 폴더로 지정하면 도구(sfx.find_file)가 하위 폴더까지 파일 이름으로 찾는다.
"""

if __name__ == "__main__":
    main(sys.argv[1])
