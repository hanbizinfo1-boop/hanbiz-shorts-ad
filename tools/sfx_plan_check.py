# -*- coding: utf-8 -*-
r"""효과음 점검 — 배치표의 소리만 다시 만들어(edit_render.build_audio) 규칙을 보고, 완성 영상이 있으면 «소리만»까지 본다.

10-19 사장님 «내 의도를 먼저 파악하고 길라잡이 충돌없게끔 하나로 통합해서 정리해봐» → «응 확인하고 개편진행해».
기준 = references/sfx.md 맨 위 «사장님 의도»·결정표. 렌더(화면)를 하지 않아 몇십 초면 끝난다.

    python tools/sfx_plan_check.py <배치표.json> [--layer 자료층.mov | --video 완성본.mp4] [--out _tmp/sfxcheck]

보는 것
  - 5-2·5-2b·5-3·5-4(한 편 같은 파일 2번) — rule_check.check_sfx · 17-4 소리 가족 — check_tone
  - 5-5 들리는 중 잘림 · 0.15초 안 잘림 — sfx.fit_tails(겹침을 0.2초 감쇠로 끝낼 때)
  - 5-6 소리만: 효과음마다 들리는 순간 앞 0.1초 ↔ 뒤 0.4초 화면을 12×9 칸으로 비교,
        **--layer(자료층 MOV, 알파 곱한 밝기)** 를 쓴다 — 말하는 사람이 늘 움직여 완성본(--video)으로는 0.5초마다 10 이상 바뀐다
        (10-19 메타v2 실측: 효과음 없는 구간 14곳 중 12곳이 10 넘음 → 완성본 비교는 화면녹화처럼 사람이 없는 편에만, 자막 띠는 뺌).
        가장 많이 바뀐 칸이 1.0 미만 ERROR · 4.0 미만 WARN(숏폼자동화 s6_check E2 문턱 4.0 — 10-19 메타v2 실측에서 CTA 버튼 눌림이 3.2라 4.0 밑은 눈 확인으로)
        (10-13 «14초에 효과음만 나오고 아무런 연출이없잖아» · 10-14 «화면은정지인데 효과음은 띠링?»)
소리는 귀로 듣지 않았다 — 수치 점검이다.
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import edit_plan as P  # noqa: E402
import edit_render as ER  # noqa: E402
import rule_check as RC  # noqa: E402
import sfx as SFX  # noqa: E402

PAIR_THR = 4.0          # 칸 평균 밝기 차(0~255) — 이 밑이면 WARN(작은 변화: 버튼 눌림 3.2 같은 것, 눈으로 확인)
PAIR_NONE = 1.0         # 이 밑이면 ERROR(화면이 사실상 그대로)
GRID = (9, 12)          # 세로 9 × 가로 12 칸
W, H = 270, 480         # 비교용으로 줄인 크기


def frame(video, t):
    """밝기(0~255). 알파가 있는 층이면 밝기 × 알파 — 투명한 곳은 0."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0.0, t):.3f}", "-i", str(video), "-frames:v", "1",
                          "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgba", "-"], capture_output=True, check=True).stdout
    if len(raw) != W * H * 4:
        return None
    a = np.frombuffer(raw, np.uint8).reshape(H, W, 4).astype(np.float32)
    return (a[..., :3].mean(2) * a[..., 3] / 255.0)


def change(a, b, band):
    d = np.abs(a - b)
    if band:
        d[band[0]:band[1]] = 0
    gy, gx = GRID
    d = d[: H // gy * gy, : W // gx * gx].reshape(gy, H // gy, gx, W // gx).mean((1, 3))
    return float(d.max())


def sound_only(plan, sfx, video, is_layer=False):
    """효과음마다 화면 변화 짝 → [(수준, 규칙, 메시지)]."""
    cs = plan.get("caption_style") or {}
    k = H / plan["seq"]["h"]
    band = None
    if "y" in cs and not is_layer:                               # 자막 띠(글 위 끝 y ~ 두 줄 높이)는 빼고 잰다 — 자막이 바뀐 것은 «연출»이 아니다
        y0 = cs["y"] - 20
        band = (int(y0 * k), int((y0 + 2.4 * cs.get("size", 72) + 40) * k))
    out = []
    for s in sfx:
        x = SFX.load(s["path"])
        t = s["t"] + SFX.attack_at(x)
        a, b = frame(video, t - 0.1), frame(video, t + 0.4)
        if a is None or b is None:
            continue
        c = change(a, b, band)
        if c < PAIR_NONE:
            out.append(("ERROR", "5-6 소리만(화면 변화 없음)", f"{t:6.2f}s {s['name']} — 앞뒤 화면 변화 {c:.1f} < {PAIR_NONE}"))
        elif c < PAIR_THR:
            out.append(("WARN", "5-6 화면 변화 작음", f"{t:6.2f}s {s['name']} — 앞뒤 화면 변화 {c:.1f} < {PAIR_THR} · 그 순간 보이는 변화가 있는지 눈으로 확인"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--video")
    ap.add_argument("--layer")
    ap.add_argument("--out", default=str(HERE.parent / "_tmp" / "sfxcheck"))
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    import json
    raw = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    raw["overlays"], raw["graphics"] = [], []         # 소리만 본다 — 납품 교체 뒤 옮겨진 화면 층 경로는 상관없다
    Path(a.out).mkdir(parents=True, exist_ok=True)
    tmp = Path(a.out) / "_plan_sound.json"
    tmp.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    plan = P.load(tmp)
    au = ER.build_audio(plan, Path(a.out) / "audio")
    ev = [(s["t"], s["name"], s["dur"], s.get("burst")) for s in au["sfx"]]
    items = RC.check_sfx(ev, au["dur"], per_ep_max=plan.get("sfx_per_ep_max", RC.SFX_PER_EP_MAX))
    items += RC.check_tone(s["name"] for s in au["sfx"]) + au["fit"]
    if a.layer:
        items += sound_only(plan, au["sfx"], a.layer, True)
    elif a.video:
        items += sound_only(plan, au["sfx"], a.video)
    n = RC.report(items, Path(a.out) / "점검.txt", f"{Path(a.plan).name} — 효과음 {len(au['sfx'])}개" + (" · 자료층 대조" if a.layer else " · 완성본 대조" if a.video else ""))
    sys.exit(1 if n else 0)


if __name__ == "__main__":
    main()
