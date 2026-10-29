# -*- coding: utf-8 -*-
r"""납품 폴더 «한 번에 바꿔 끼우기» — 새 판은 옆 폴더(<납품>/_새판/)에 다 만든 뒤 마지막에 교체한다.

10-14 사장님: (XML 이 «파일을 찾을 수 없다» — 다시 조립하는 동안 media 를 지웠다 만들어서) → «삭제안하면 또 파일이 쓸데없이 쌓일수도있는거아니야?» → «1로 가고»
  1) _새판/ 에 mp4 · xml · media/ 를 전부 만든다(edit_render --out _새판/x.mp4 · edit_xml --out _새판)
  2) XML 안의 경로(_새판/…)를 최종 폴더 경로로 고쳐 쓴다(원문·퍼센트 인코딩 둘 다)
  3) **파일 단위로** 같은 이름 덮어쓰기 → 새 판이 안 쓰는 옛 파일만 지운다(안 쓰는 파일이 쌓이지 않음)
     10-14 2차: 처음엔 옛 media 폴더를 통째로 지웠는데, 프리미어가 열고 있는 파일(잠김)에서 멈춰 63개가 빠졌다
     → 폴더를 통째로 지우지 않는다. 잠긴 파일은 건너뛰고 «준비완료.txt» 에 목록을 남긴다(프리미어를 닫고 다시 돌리면 마저 바뀜).
  4) «준비완료.txt»(시각 · 잠겨서 못 바꾼 파일) — 그 뒤에 XML 을 연다.

    python tools/deliver_swap.py <최종 납품 폴더>
"""
import shutil
import sys
import time
from pathlib import Path
from urllib.parse import quote


def _try(fn, *a):
    try:
        fn(*a)
        return True
    except PermissionError:
        return False


def swap(final):
    final = Path(final).resolve()
    stage = final / "_새판"
    if not stage.exists():
        raise SystemExit(f"_새판 폴더가 없다: {stage}")
    (final / "준비완료.txt").unlink(missing_ok=True)
    s_raw, f_raw = str(stage).replace("\\", "/"), str(final).replace("\\", "/")
    for x in stage.glob("*.xml"):
        t = x.read_text(encoding="utf-8")
        x.write_text(t.replace(quote(s_raw, safe="/"), quote(f_raw, safe="/")).replace(s_raw, f_raw), encoding="utf-8")
    locked = []
    sm, fm = stage / "media", final / "media"
    fm.mkdir(exist_ok=True)
    new = {p.name for p in sm.iterdir()} if sm.exists() else set()
    for p in (sm.iterdir() if sm.exists() else []):
        if not _try(shutil.copy2, p, fm / p.name):
            locked.append(f"media/{p.name} (덮어쓰기 못 함)")
    for p in fm.iterdir():
        if p.name not in new and not _try(p.unlink):
            locked.append(f"media/{p.name} (안 쓰는 옛 파일, 지우지 못 함)")
    for p in stage.iterdir():
        if p.is_file() and not _try(shutil.copy2, p, final / p.name):
            locked.append(f"{p.name} (덮어쓰기 못 함)")
    shutil.rmtree(stage, ignore_errors=True)
    msg = time.strftime("%Y-%m-%d %H:%M:%S") + " 교체 완료 — 이제 XML 을 열어도 됩니다\n"
    if locked:
        msg += "프리미어가 열고 있어 바꾸지 못한 파일(프리미어를 닫고 deliver_swap 을 다시 돌리면 바뀜):\n" + "".join(f"  - {x}\n" for x in locked)
    (final / "준비완료.txt").write_text(msg, encoding="utf-8")
    print(msg)


if __name__ == "__main__":
    swap(sys.argv[1])
