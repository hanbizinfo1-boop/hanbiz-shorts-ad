# -*- coding: utf-8 -*-
"""SessionStart 훅(startup·compact·resume) — 자동 압축·세션 재개 뒤에도 규칙을 빠뜨리지 않게, 상시 규칙과 지금 진행 상황을 대화에 넣는다.

[이식본 — 원본 D:/영상제작/도구/점검/resume_guide.py. 사장님 10-07 «오토컴팩트 진행되더라도 길라잡이 누락되지 않게끔 장치 만들어서 적용»]
.claude/settings.json → hooks.SessionStart(matcher compact|resume) → python tools/resume_guide.py
출력(표준 출력)이 그대로 대화 맥락에 들어간다. 발췌만 믿지 말고 SKILL.md 와 references/ 를 다시 연다.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".claude" / "skills" / "shorts-ad"


def section(text, heading_keyword):
    """'## ... 키워드 ...' 로 시작하는 절을 다음 '## ' 직전까지 잘라 온다."""
    m = re.search(rf"^## [^\n]*{re.escape(heading_keyword)}[^\n]*\n[\s\S]*?(?=\n## |\Z)", text, re.M)
    return m.group(0) if m else ""


LIMIT = 9000          # Claude Code 훅 출력이 1만 자를 넘으면 파일로 빠지고 앞 2KB 만 대화에 들어간다(10-22 실측 52KB → 사실상 안 읽힘)


def rule_heads(sec):
    """4장 — 규칙마다 머리글(굵은 글씨)만 한 줄씩. 전문은 SKILL.md 를 연다."""
    out = []
    for ln in sec.splitlines():
        s = ln.lstrip()
        if not s.startswith("- "):
            continue
        m = re.search(r"\*\*(.+?)\*\*", s)
        head = m.group(1) if m else re.split(r"[(—«]", s[2:])[0]
        out.append(("  - " if ln.startswith("  ") else "- ") + head.strip()[:90])
    return "\n".join(out)


def clip(text, n):
    return text if len(text) <= n else text[:n].rsplit("\n", 1)[0] + "\n…(이하 생략 — 파일을 연다)"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = ["# 한비즈 쇼츠 광고 — 세션 재개 자동 안내 (발췌다. 장면을 만들기 전에 파일을 다시 연다)", "",
           "읽을 순서: `지시작업/길라잡이.md` → `지시작업/기록/작업기록.md` «지금 상태» → `CLAUDE.md` → `.claude/skills/shorts-ad/SKILL.md`(1장 표에서 지금 일에 맞는 references/) → 납품 직전 `references/checklist.md`."]
    sk = SKILL / "SKILL.md"
    if sk.exists():
        t = sk.read_text(encoding="utf-8")
        s = section(t, "상시 규칙")
        if s:
            out.append("\n## SKILL 4장 사장님 상시 규칙 — 머리글만(전문은 SKILL.md)\n" + rule_heads(s))
        s = section(t, "납품 전 점검표")
        if s:
            out.append("\n" + s.strip())
    # 정본 = 지시작업 세션(10-14 사장님 «여기 세션을 정본으로 … 앞으로 이 세션으로 작업하게»)
    dz = ROOT / "지시작업" / "기록" / "작업기록.md"
    if dz.exists():
        s = section(dz.read_text(encoding="utf-8"), "지금 상태")
        if s:
            used = sum(len(x) for x in out)
            out.append("\n---\n# ★ 정본 세션 = 지시작업 — `지시작업/기록/작업기록.md` «지금 상태»(이게 내 기록이다)\n" + clip(s, max(1500, LIMIT - used - 400)))
    out.append("\n(루트 `기록/`(10-14 끝난 자율 세션, 결과물 폐기)·`병행작업/`(10-12~13 대본 세션)은 넣지 않는다 — 필요하면 그 파일을 연다.)")
    print(clip("\n".join(out), LIMIT))


if __name__ == "__main__":
    main()
