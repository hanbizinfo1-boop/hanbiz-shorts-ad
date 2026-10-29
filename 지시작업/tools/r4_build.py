# -*- coding: utf-8 -*-
r"""4번 뼈대 × 레퍼런스 연출(10-19) — 사장님 프리미어 «4번» 컷·자막 그대로, 연출만 인스타 릴스 DeolaEOtysF 식으로.

사장님(10-19): «4번 뼈대 이 영상을 https://www.instagram.com/reels/DeolaEOtysF/ 여기 영상이랑 비슷한느낌으로 가고싶은데
위에랑 밑에 저런 규격줄이기는 진행하지않고 연출방법만 레퍼런스 삼으려고해 저 화면에서 9:16으로»
«이런 말풍선은 또 별로 좀더 말풍선 디자인이나 안의 글자체는 세련되었으면좋겠어 나머지는 여기 연출느낌을 9:16비율에 맞게 적용해서 한번 영상편집해봐»
«자막은 내가 srt뽑아놓은거니까 타임라인필요하면 프리미어프로 최근작업현황확인해»

    python 지시작업/tools/r4_build.py prep     # 원본 4.MP4 → 컷마다 줌·흑백·작아지는 화면을 구운 바탕(base.mp4) + 목소리(뼈대 소리)
    python tools/html_motion.py 지시작업/tools/scenes/r4_ref.html --alpha --workers 2 --sub 3 --out 지시작업/_tmp/r4 --name r4_ref
    python 지시작업/tools/r4_build.py plan     # 배치표 → edit_render / edit_xml

레퍼런스에서 가져온 것(0.5초 간격 전부 봄, 기록/작업기록.md 10-19):
  컷마다 앞으로 당기는 줌(5.0초 펀치인) · 혼잣말 같은 줄은 화면이 작아지고 검은 테(2.5·7.0초) · 웃기거나 슬픈 줄은 흑백(2.5·46.5초)
  · 핵심 줄은 큰 흰 자막이 흐릿→선명(9.5·13.0·40.5초) · 말 옆 3D 아이콘(15.0초) · 흰 인형 으쓱(4.5초) · 떨어지는 지폐(21.0초)
  · 말풍선(22.5·45.0초 — 디자인은 바꿈) · 끝은 작은 줄+큰 줄 두 단(48.5초)
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DZ = HERE.parent
sys.path.insert(0, str(ROOT / "tools"))

SRC = Path(r"D:\26년 10월\261020\4.MP4")            # 1728x3072 HEVC 10bit 59.94 (사장님 시퀀스 V1, 비율 52.08% = 꽉 채움)
SKEL = Path(r"D:\26년 10월\261020\4번 뼈대.mp4")     # 사장님 내보낸 뼈대 — 소리만 쓴다(컷 소리 볼륨 그대로)
SEQ = DZ / "_tmp/story/seq_4번.json"                 # tools/read_prproj.py 로 읽은 «4번» 시퀀스(10-19 16:24 저장본 사본)
WORK = DZ / "_tmp/r4"
DELIV = DZ / "납품/4번_레퍼연출_1019"
NAME = "4번_레퍼연출"
FPS_N, FPS_D = 30000, 1001
FPS = FPS_N / FPS_D
SEQ_END = 57.69

# 컷마다 줌 — 레퍼런스처럼 컷이 바뀔 때 당겼다 놓았다(1.0 ↔ 1.12). 얼굴이 위 1/3 이라 위쪽 기준으로 당긴다
ZOOM = [1.0, 1.12]
ANCHOR_Y = 0.30
# 영상 연출 구간(시퀀스 초) — 컷 안에서 나뉘면 그 시각에서 쪼갠다
FX = [
    (1.97, 2.72, {"shrink": True}),               # «아, 말도 안돼요» — 레퍼런스 7.0 «아니요 저는 싫은데요?» 작아지는 화면
    (5.00, 6.26, {"shrink": True, "bw": True}),   # «이 영상 보지마세요» — 레퍼런스 2.5 «오늘 영상 안 보셔도 됩니다» 흑백+작아짐+빨간 글
    (14.30, 15.78, {"bw": True}),                 # «급격히 떨어지고 있어요» — 레퍼런스 46.5 흑백
]
SHRINK = 0.86
# 큰 자막이 떠오르는 시각(장면 BIG 의 조각 시각) → 효과음 계기
BIG_T = {5.00: "shrink_skip", 14.30: "hit", 24.44: "big", 29.58: "big", 35.37: "big", 37.59: "big",
         43.64: "big", 46.56: "hit", 55.14: "big"}
# 큰 자막(장면 HTML)이 대신하는 사장님 자막 줄 — 아래 줄은 기본 자막에서 뺀다
BIG_LINES = {"이 영상 보지마세요", "돈의 가치는", "급격히 떨어지고 있어요", "착각하는게 있어요", "임차인이 있어야 됩니다",
             "100% 임차인을", "채우고 나서", "건물을 사는 방법!", "45번을 그걸 했습니다", "존재치 않아요", "아래링크를 눌러서", "상담신청을 남겨주세요"}
CAP_STYLE = {"mode": "outline", "y": 1150, "size": 62, "stroke": 8, "max_w": 960}
# 효과음 — 말하는 쇼츠라 전부 목소리 밑(sfx.md 결정표: 큰 것 −3~−6, 나머지 −8~−12) · 한 편 같은 파일 2번까지(5-4) → 계기마다 돌려 쓴다
ROLE_FILES = {
    "ico": [("ML_Explainer video pops whoosh light pop.wav", -10), ("KN_select_003.wav", -10), ("ML_Interface option select.wav", -10),
            ("KN_toggle_001.wav", -10), ("SEL_キラッ1.mp3", -12)],
    "fig": [("ML_Fast small sweep transition.wav", -10)],
    "bills": [("ML_Paper quick movement.wav", -9)],
    "bub": [("KN_open_003.wav", -9), ("채팅 효과음.mp3", -10)],
    "cta": [("KN_confirmation_004.wav", -8)],
    "shrink": [("ML_Fast transitions swoosh.wav", -10), ("SEL_マントを翻す.mp3", -10)],
    "hit": [("ML_Fast impact blow.wav", -6), ("ML_Impact of a blow.wav", -6)],          # 흑백 떨어짐 · «존재치 않아요»
    "big": [("ML_Achievement bell.wav", -12), ("ML_Paper slide.wav", -10), ("종이소리 화면전환.mp3", -11),
            ("SEL_パパッ.mp3", -11)],                                                # 큰 자막 떠오름
    "zoom": [("ML_Air woosh.wav", -12), ("SEL_高速移動.mp3", -12), ("ML_Fast air sweep transition.wav", -12),
             ("ML_Fast whoosh transition.wav", -12), ("ML_Speeding swoosh.wav", -12), ("ML_Fast sweep transition.wav", -12),
             ("ML_Flying fast swoosh.wav", -12), ("SEL_パッ.mp3", -12)],               # 컷 펀치인 — 빈 구간(5-3 2.5초)만 채운다
    "cap": [("KN_click_001.wav", -12), ("KN_select_001.wav", -12), ("KN_click_003.wav", -12), ("KN_select_002.wav", -12)],                  # 컷이 없는 빈 구간 — 자막 팝
}


def seq():
    d = json.loads(SEQ.read_text(encoding="utf-8"))
    v1 = [i for i in d["items"] if i["track"] == "V1"]
    v2 = [i for i in d["items"] if i["track"] == "V2"]
    return v1, v2


def frame(t):
    return round(t * FPS)


def segments():
    """V1 컷을 FX 경계에서 쪼갠 조각 [(t0, t1, 원본 시작초, 줌, fx)]."""
    v1, _ = seq()
    out = []
    for n, c in enumerate(v1):
        cuts = sorted({c["t0"], c["t1"], *[x for a, b, _ in FX for x in (a, b) if c["t0"] < x < c["t1"]]})
        for a, b in zip(cuts, cuts[1:]):
            fx = next((f for x0, x1, f in FX if x0 <= a + 1e-3 and b <= x1 + 1e-3), {})
            out.append((a, b, c["s0"] + (a - c["t0"]), ZOOM[n % 2], fx))
    return out


def vf(zoom, fx):
    w, h = round(1080 * zoom / 2) * 2, round(1920 * zoom / 2) * 2
    f = [f"scale={w}:{h}:flags=lanczos", f"crop=1080:1920:{(w - 1080) // 2}:{int((h - 1920) * ANCHOR_Y)}"]
    if fx.get("bw"):
        f.append("hue=s=0,eq=contrast=1.08")
    if fx.get("shrink"):
        sw, sh = round(1080 * SHRINK / 2) * 2, round(1920 * SHRINK / 2) * 2
        f += [f"scale={sw}:{sh}:flags=lanczos", f"pad=1080:1920:{(1080 - sw) // 2}:{(1920 - sh) // 2}:black"]
    return ",".join(f + [f"fps={FPS_N}/{FPS_D}", "format=yuv420p"])


def prep():
    WORK.mkdir(parents=True, exist_ok=True)
    seg_dir = WORK / "seg"
    seg_dir.mkdir(exist_ok=True)
    lst = []
    for k, (a, b, s0, z, fx) in enumerate(segments()):
        n = frame(b) - frame(a)
        p = seg_dir / f"s{k:02d}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s0:.4f}", "-i", str(SRC), "-frames:v", str(n), "-an",
                        "-vf", vf(z, fx), "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-r", f"{FPS_N}/{FPS_D}", str(p)], check=True)
        lst.append(f"file '{p.as_posix()}'")
        print(f"  {k:02d} {a:6.2f}-{b:6.2f} 줌 {z} {fx or ''} {n}프레임", flush=True)
    (seg_dir / "list.txt").write_text("\n".join(lst) + "\n", encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(seg_dir / "list.txt"), "-c", "copy",
                    str(WORK / "base.mp4")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SKEL), "-vn", "-ac", "2", "-ar", "48000", str(WORK / "voice.wav")], check=True)
    print(f"바탕 {WORK / 'base.mp4'} · 목소리 {WORK / 'voice.wav'}")


def plan():
    v1, v2 = seq()
    caps = [{"text": " ".join(c.get("text") or []).strip(), "start": round(c["t0"], 3), "end": round(c["t1"], 3)} for c in v2]
    DELIV.mkdir(parents=True, exist_ok=True)
    media = DELIV / "media"
    media.mkdir(exist_ok=True)
    import shutil
    base = media / "바탕_줌흑백.mp4"
    ovl = media / "연출층_r4.mov"
    shutil.copy2(WORK / "base.mp4", base)
    shutil.copy2(WORK / "r4_ref.mov", ovl)
    shutil.copy2(WORK / "voice.wav", media / "목소리_뼈대.wav")
    cuts = [{"src": str(base), "in": round(a, 6), "out": round(b, 6), "start": round(a, 6), "end": round(b, 6), "cont": k > 0}
            for k, (a, b, _, _, _) in enumerate(segments())]
    ev = json.loads((WORK / "r4_ref_events.json").read_text(encoding="utf-8"))
    ev = ev if isinstance(ev, list) else ev.get("events", [])
    ev += [{"t": a, "role": "shrink"} for a, _, f in FX if f.get("shrink")]
    ev += [{"t": t, "role": r} for t, r in BIG_T.items() if r in ROLE_FILES]
    # 5-3 빈 구간(2.5초) — 안에 있는 컷(펀치인 줌이 바뀜) 중 가운데에 가까운 것에 «zoom», 컷이 없으면 자막 팝에 «cap». 화면이 바뀌는 순간에만(5-6)
    cut_t = sorted({round(a, 3) for a, _, _, _, _ in segments()} - {0.0})
    cap_t = sorted(round(c["start"], 3) for c in caps if c["text"] not in BIG_LINES)
    while True:
        ts = sorted([0.0] + [e["t"] for e in ev if e["role"] in ROLE_FILES] + [SEQ_END])
        gap = next(((x, y) for x, y in zip(ts, ts[1:]) if y - x > 2.2 and any(x + 0.5 < c < y - 0.5 for c in cut_t + cap_t)), None)
        if not gap:
            break
        mid = sum(gap) / 2
        for pool, role in ((cut_t, "zoom"), (cap_t, "cap")):
            inside = [c for c in pool if gap[0] + 0.5 < c < gap[1] - 0.5]
            if inside:
                ev.append({"t": min(inside, key=lambda c: abs(c - mid)), "role": role})
                break
    used, sfx, roles = {}, [], {}
    for e in sorted(ev, key=lambda e: e["t"]):
        if e["role"] not in ROLE_FILES:
            continue
        files = ROLE_FILES[e["role"]]
        k = used.get(e["role"], 0)
        used[e["role"]] = k + 1
        f, db = files[k % len(files)]                       # 돌려 쓴다 — 같은 소리 연속(5-2) · 한 편 2번(5-4)
        rn = f"{e['role']}_{f}"
        roles[rn] = {"file": f, "align": "peak", "exact_db": db}
        sfx.append({"t": round(e["t"], 3), "role": rn})
    p = {
        "name": NAME,
        "base_dir": str(ROOT),
        "seq": {"w": 1080, "h": 1920, "fps": 29.97},
        "speed": 1.0,
        "loudness_lufs": -14,
        "voice": {"file": str(media / "목소리_뼈대.wav"), "start": 0.0},
        "caption_style": CAP_STYLE,
        "script": [c["text"] for c in caps if c["text"] not in BIG_LINES],   # 큰 자막 줄은 연출층(HTML)에 있다
        "cuts": cuts,
        "captions": [dict(c, anim="pop") for c in caps if c["text"] not in BIG_LINES],
        "graphics": [],
        "overlays": [{"file": str(ovl), "t0": 0.0, "t1": SEQ_END, "name": "연출층_r4"}],
        "sfx_roles": roles,
        "sfx": sfx,
    }
    path = WORK / f"plan_{NAME}.json"
    path.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(f"배치표 {path} — 조각 {len(cuts)} · 자막 {len(p['captions'])}/{len(caps)} · 효과음 {len(sfx)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    {"prep": prep, "plan": plan}[sys.argv[1]]()
