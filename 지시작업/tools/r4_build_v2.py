# -*- coding: utf-8 -*-
r"""4번 레퍼연출 v2(10-19) — v1(r4_build.py) 반려 뒤 다시.

사장님(10-19, v1 보시고):
  «효과음도 부족하고 연출도구도 부족하고 레퍼런스의 효과음좀 재현해줬으면좋겠고 넘 연출이없는 장면들이 많은데?»
  «그리고 연출도구도 내가 원하는 그런느낌아닌데 좀더 빡빡하게 연출도구 넣어주고 연출도구좀 ai티안나게 짜치지않게 만들어줘»
  «글짜 강조하는거도 저쪽은 많은데 넌 글자 강조도없고 색깔도 딱히 강조색이없어»

v1 과 다른 점
  - 장면 `scenes/r4_ref_v2.html`: 자막 줄마다 연출 하나 이상(카드·그래프·취소선·동그라미·형광펜·도장·체크·버튼), Codex 3D 아이콘·지폐 → 이모지
  - 바탕: 컷 안에서도 천천히 당김(1→1.035) · 때리는 순간 흔들림(14.30 · 24.44 · 46.56)
  - 기본 자막: 색 역할(숫자 초록 · 강조 노랑) — 사장님 10-15 «숫자는 초록색이니까 강조할만한거 노란색»
  - 소리: 레퍼런스처럼 BGM 깔기(사장님 10-12 «bgm은 2안 5번» Miles Away) + 화면 사건마다 결이 맞는 효과음
    (레퍼런스 스펙트로그램: 흑백 전환 휙 3.2 · 말풍선 딸깍 22.0/44.8 · 돈 반짝 20.3 · 슬픈 흑백 «띠로리» 46.5 · 끝 반짝 48.2)

    python 지시작업/tools/r4_build_v2.py prep
    python tools/html_motion.py 지시작업/tools/scenes/r4_ref_v2.html --alpha --workers 2 --sub 3 --out 지시작업/_tmp/r4v2 --name r4_ref_v2
    python 지시작업/tools/r4_build_v2.py plan
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r4_build as V1  # noqa: E402

ROOT, DZ = V1.ROOT, V1.DZ
WORK = DZ / "_tmp/r4v2"
DELIV = DZ / "납품/4번_레퍼연출_v2_1019"
NAME = "4번_레퍼연출_v2"
SCENE = "r4_ref_v2"
BGM = ROOT / "납품/BGM후보_1012/2안_설명형/5_Miles Away.mp3"
BGM_DB = -18
PUSH = 0.035                                  # 컷 하나 동안 천천히 당기는 양
SHAKE = {14.30: 14, 24.44: 10, 46.56: 14}     # 때리는 순간 흔들림(px, 0.35초 감쇠)
BIG_LINES = V1.BIG_LINES | {"제가 18년동안"}
# 기본 자막 강조 — (강조 말, 색) · 숫자 g · 강조 y
EMPH = {
    "강남 빌딩보다": ("강남 빌딩", "y"), "확실한 투자가 있다?": ("확실한 투자", "y"), "진짜 그렇게": ("진짜", "y"),
    "30억으로": ("30억", "g"), "100억 만드려고 하는데": ("100억", "g"), "예금하려는 분들은 없죠?": ("예금", "y"),
    "10년전에 최저시급이": ("10년전", "g"), "6천 원이였는데": ("6천 원", "g"), "지금 만원 넘잖아요": ("만원", "g"),
    "찾는게 강남빌딩이에요": ("강남빌딩", "y"), "적어도 강남빌딩은": ("강남빌딩", "y"), "물가상승률보다": ("물가상승률", "y"),
    "더 올라가잖아요": ("더 올라가", "y"), "이건 다 알고있으시죠?": ("다 알고", "y"), "건물만 사면": ("건물만", "y"),
    "물론 시세차익은": ("시세차익", "y"), "확실한 임차인이": ("확실한 임차인", "y"), "월세를 잘 내줘야": ("월세", "y"),
    "돈이 되는거에요": ("돈이 되는", "y"), "임차인이 확실히": ("확실히", "y"), "알아냈어요": ("알아냈어요", "y"),
    "손해없이 확실한 건물을": ("손해없이", "y"), "그런 경험을 한 사람에게": ("경험", "y"), "배우고싶다": ("배우고싶다", "y"),
}
# 효과음 역할 → 후보 파일(목소리 대비 dB). 한 편 같은 파일 2번까지(5-4)·같은 파일 연속 금지(5-2) → 아래 pick() 이 전체 사용 횟수로 돌린다
ROLE_FILES = {
    "pop": [("ML_Explainer video pops whoosh light pop.wav", -10), ("KN_select_003.wav", -10), ("SEL_パッ.mp3", -11),
            ("KN_toggle_002.wav", -10), ("KN_select_004.wav", -11), ("ML_Interface option select.wav", -10), ("KN_pluck_001.wav", -11)],
    "card": [("ML_Fast small sweep transition.wav", -11), ("ML_Fast air sweep transition.wav", -11), ("ML_Fast whoosh transition.wav", -11),
             ("ML_Speeding swoosh.wav", -11), ("SEL_高速移動.mp3", -11)],
    "chime": [("SEL_キラッ1.mp3", -10), ("ML_Achievement bell.wav", -10), ("ML_Magic sparkle whoosh.wav", -11)],
    "shine": [("KN_confirmation_004.wav", -9)],
    "sad": [("KN_lowDown.wav", -6)],                 # 레퍼런스 46.5 흑백 «띠로리» — Cartoon/Fairy 계열은 17-4 금지라 내려가는 톤 하나로
    "rain": [("ML_Bag of coins touch.wav", -8)],
    "strike": [("KN_error_002.wav", -11)],
    "graph": [("ML_Paper quick movement.wav", -10), ("ML_Big paper page turn.wav", -11), ("ML_Paper slide.wav", -10)],
    "marker": [("ML_Paper slide.wav", -10), ("SEL_パパッ.mp3", -11), ("종이소리 화면전환.mp3", -11)],   # 유성 마커 2.28초는 다음 소리에 잘림(5-5)
    "bubble": [("KN_open_003.wav", -9), ("채팅 효과음.mp3", -10)],
    "stamp": [("도장.mp3", -6)],
    "tick": [("KN_click_001.wav", -11), ("KN_click_003.wav", -11), ("KN_select_001.wav", -11), ("KN_select_002.wav", -11)],
    "tap": [("KN_click_005.wav", -9)],
    "shrink": [("ML_Fast transitions swoosh.wav", -9), ("SEL_マントを翻す.mp3", -9)],
    "hit": [("ML_Impact of a blow.wav", -6), ("ML_Fast impact blow.wav", -6)],
}
DROP = set()   # 소리 안 붙일 장면 계기 (역할, id)
ROLE_ALIGN = {}   # 역할별 맞춤 기준(기본 peak) — 길게 차오르는 소리는 onset
BURST_ROLES = set()   # 사장님이 시킨 연타 — 같은 파일 횟수·0.3초 묶기를 안 본다(v3 «띵띵띵»)
EXTRA = [(1.97, "shrink"), (3.47, "card"), (5.00, "shrink"), (24.44, "hit"), (42.48, "card"), (44.34, "chime"), (46.56, "hit")]   # 3.47 컷 줌 · 42.48 «18년» · 44.34 «45번» 다 셈


def vf(zoom, fx, dur, t0):
    z = f"{zoom}*(1+{PUSH}*t/{dur:.3f})"
    sx = ""
    for ts, amp in SHAKE.items():
        if t0 - 1e-3 <= ts < t0 + dur:
            d = ts - t0
            sx = f"+{amp}*sin((t-{d:.3f})*55)*exp(-(t-{d:.3f})*9)*gte(t,{d:.3f})"
    f = [f"scale=w='trunc(1080*{z}/2)*2':h='trunc(1920*{z}/2)*2':eval=frame:flags=lanczos",
         f"crop=1080:1920:x='(iw-1080)/2{sx}':y='(ih-1920)*{V1.ANCHOR_Y}{sx.replace('sin', 'cos')}'"]
    if fx.get("bw"):
        f.append("hue=s=0,eq=contrast=1.08")
    if fx.get("shrink"):
        sw, sh = round(1080 * V1.SHRINK / 2) * 2, round(1920 * V1.SHRINK / 2) * 2
        f += [f"scale={sw}:{sh}:flags=lanczos", f"pad=1080:1920:{(1080 - sw) // 2}:{(1920 - sh) // 2}:black"]
    return ",".join(f + [f"fps={V1.FPS_N}/{V1.FPS_D}", "format=yuv420p"])


def prep():
    seg_dir = WORK / "seg"
    seg_dir.mkdir(parents=True, exist_ok=True)
    lst = []
    segs = V1.segments()
    for k, (a, b, s0, z, fx) in enumerate(segs):
        n = V1.frame(b) - V1.frame(a) + (1 if k == len(segs) - 1 else 0)    # v1 은 끝 1프레임 모자랐다(XML 끝 검정)
        p = seg_dir / f"s{k:02d}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s0:.4f}", "-i", str(V1.SRC), "-frames:v", str(n), "-an",
                        "-vf", vf(z, fx, b - a, a), "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-r", f"{V1.FPS_N}/{V1.FPS_D}", str(p)], check=True)
        lst.append(f"file '{p.as_posix()}'")
        print(f"  {k:02d} {a:6.2f}-{b:6.2f} 줌 {z} {fx or ''} {n}프레임", flush=True)
    (seg_dir / "list.txt").write_text("\n".join(lst) + "\n", encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(seg_dir / "list.txt"), "-c", "copy",
                    str(WORK / "base.mp4")], check=True)
    shutil.copy2(V1.WORK / "voice.wav", WORK / "voice.wav")
    print(f"바탕 {WORK / 'base.mp4'}")


def plan():
    v1, v2 = V1.seq()
    caps = [{"text": " ".join(c.get("text") or []).strip(), "start": round(c["t0"], 3), "end": round(c["t1"], 3)} for c in v2]
    media = DELIV / "media"
    media.mkdir(parents=True, exist_ok=True)
    base, ovl = media / "바탕_줌흑백.mp4", media / "연출층_v2.mov"
    shutil.copy2(WORK / "base.mp4", base)
    shutil.copy2(WORK / f"{SCENE}.mov", ovl)
    shutil.copy2(WORK / "voice.wav", media / "목소리_뼈대.wav")
    cuts = [{"src": str(base), "in": round(a, 6), "out": round(b, 6), "start": round(a, 6), "end": round(b, 6), "cont": k > 0}
            for k, (a, b, _, _, _) in enumerate(V1.segments())]
    ev = json.loads((WORK / f"{SCENE}_events.json").read_text(encoding="utf-8"))
    ev = (ev if isinstance(ev, list) else ev.get("events", [])) + [{"t": t, "role": r} for t, r in EXTRA]
    ev = [e for e in ev if (e["role"], e.get("id")) not in DROP]
    count, last, sfx, roles = {}, None, [], {}

    def pick(role):
        for f, db in ROLE_FILES[role]:
            if count.get(f, 0) < 2 and f != last:
                return f, db
        raise SystemExit(f"효과음 후보 모자람: {role}")
    prev_t = -9
    for e in sorted(ev, key=lambda e: e["t"]):
        burst = e["role"] in BURST_ROLES
        if e["t"] - prev_t < 0.15 and not burst:               # 같은 순간 둘(카드+이모지 등)은 앞 것 하나만 — 5-5 잘림
            continue
        if e["role"] not in ROLE_FILES:
            print("  역할 없음(소리 안 붙임):", e)
            continue
        f, db = ROLE_FILES[e["role"]][0] if burst else pick(e["role"])
        count[f] = count.get(f, 0) + 1
        last, prev_t = f, e["t"]
        rn = f"{e['role']}_{f}"
        roles[rn] = {"file": f, "align": ROLE_ALIGN.get(e["role"], "peak"), "exact_db": db}
        sfx.append({"t": round(e["t"], 3), "role": rn})
    shown = [c for c in caps if c["text"] not in BIG_LINES]
    capl = []
    for c in shown:
        x = dict(c, anim="pop")
        if c["text"] in EMPH:
            w, col = EMPH[c["text"]]
            x.update(emph=[w], emph_color=col)
        capl.append(x)
    p = {
        "name": NAME, "base_dir": str(ROOT), "seq": {"w": 1080, "h": 1920, "fps": 29.97}, "speed": 1.0, "loudness_lufs": -14,
        "voice": {"file": str(media / "목소리_뼈대.wav"), "start": 0.0},
        "bgm": {"file": str(BGM), "start": 0.0, "gain_db": BGM_DB, "fade_out": 1.0},
        "caption_style": V1.CAP_STYLE,
        "script": [c["text"] for c in shown],
        "cuts": cuts, "captions": capl, "graphics": [],
        "overlays": [{"file": str(ovl), "t0": 0.0, "t1": V1.SEQ_END, "name": "연출층_v2"}],
        "sfx_roles": roles, "sfx": sfx,
    }
    path = WORK / f"plan_{NAME}.json"
    path.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(f"배치표 {path} — 조각 {len(cuts)} · 자막 {len(capl)}/{len(caps)}(강조 {sum('emph' in c for c in capl)}) · 효과음 {len(sfx)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    {"prep": prep, "plan": plan}[sys.argv[1]]()
