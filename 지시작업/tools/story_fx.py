# -*- coding: utf-8 -*-
r"""광고 초안 자막 v3 — 사장님이 프리미어에서 맞춘 자막 타임라인(«스토리 쇼츠» → «쇼츠» 시퀀스) 그대로 + «스토리»(OVWZuG1KyV0) 식 연출.

사장님 10-15 (원래 이 세션에 주실 지시를 숏폼자동화 세션에 잘못 보내셨다 — «여기부터 잘못보냈어»):
  «D:\26년 10월\261015 여기에 들어있는 영상을 자막작업을 해야하는데 https://www.youtube.com/shorts/OVWZuG1KyV0
   여기 나오는 쇼츠랑 진짜 완전 똑같이 98%이상 똑같이 할거야 / 자막 세팅해주고 이걸 내가 수정할 수 있는 형태로 XML뽑아줘»
  … «스티커 필요없어» · «v2로 그 움직임 키프레임» · «단어가 더 잘게»
  «지금 내가 프리미어에 자막 맞춰놨으니까 이 타임라인 그대로 연출 넣어서 만들어봐 스토리랑 완전 비슷하게 스티커는 넣지말되 강조선 이런건 넣어도 좋아»
  «누가 언제 무엇을 어떻게 이쪽은 다 물음표 붙여줘 뒤에»

- 자막 글·시각 = 사장님 프리미어 그래픽(시퀀스 «쇼츠» V2·V3). 모양 = 스토리(Noto Sans KR Bold 흰 + 검은 외곽선·그림자, 팝).
- 연출 그림·키프레임은 숏폼자동화 `tools/caption_fx.py` 를 import 만 해서 쓴다(그 폴더는 읽기 전용 — 바이트코드도 안 쓴다).
- 큰 숫자·계산식 동안은 자막을 숨긴다(스토리 R3·R4 «그동안 자막 없음», v2 와 같음).

    python 지시작업/tools/story_fx.py <seq_쇼츠.json> <출력 폴더>
출력: <이름>.xml(V1 영상 · V2 집중선·▶▶ · V3 자막 · V4 라벨·화살표 · V5 큰 숫자·계산식 · A1/A2) · .srt · _층/ · _미리보기.mp4 · _자막목록.txt
"""
import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, "C:/Users/user/Desktop/숏폼자동화/tools")
import caption_fx as CF  # noqa: E402
import ref_caption as RC  # noqa: E402

VIDEO = Path("D:/26년 10월/261015/광고 초안 .mp4")
NAME = "광고초안_v3"
# 사장님 그래픽 중 글자가 안 읽힌 것(프리미어 저장 형식 차이) — v2 자막 목록의 같은 시각 글
FILL = {1.37: "또", 10.03: "계속", 16.22: "문의", 22.77: "자동으로", 37.57: "80%"}
QMARK = ("누가", "언제", "무엇을", "어떻게")      # «다 물음표 붙여줘 뒤에»(25~27.5초 구간)

# v2 연출 계획에서 스티커만 뺀 것(«스티커는 넣지말되 강조선 이런건 넣어도 좋아»)
FX = [
    {"type": "speed", "from": "매일", "to": "겁니다"},
    {"type": "bignum_gap", "text": "100,000", "after": "광고비", "after_t": 11.0},   # 사장님이 비워 둔 «10만원씩» 자리(12.21~12.85)
    {"type": "arrow", "on": "알림톡까지", "tip": [610, 780], "angle": 140},
    {"type": "ff", "from": "자동으로", "to": "나갑니다", "after": "알림톡까지"},
    {"type": "speed", "from": "자동으로", "to": "나갑니다", "after": "알림톡까지"},   # 스토리 25.3~27.3: ▶▶ 와 집중선이 함께
    {"type": "calc", "from": "실수나", "to": "있습니다",
     # 스토리 7.0~9.8: «1,000,000» → 흰 «-» 먼저 → 초록 숫자가 붙음 → 밑줄 그어짐 → 빨강 결과
     "lines": [["실수 · 누락", "white", "실수나", 0], ["-", "white", "누락을", 0], ["- 80%", "green", "80%", 0],
               ["__line__", None, "80%", 0.35], ["싹 잡힘!", "red", "잡을 수", 0]]},
    {"type": "big", "on": "하루만에", "scale": 1.4},          # 스토리 «5시간 동안»·«지난 90일 동안»·«무려 1,249만 명이» — 시간·숫자 말을 키움
    {"type": "bignum_gap", "text": "1,000,000", "after": "10곳"},     # «100만원» 자리(44.56~44.96)
    {"type": "color", "on": "신청해", "color": "red"},
    # 10-15 사장님 «선착순 라벨 뺴고는 다 괜찮았어 그리고 색깔 처리 조금 아쉽 숫자는 초록색이니까 강조할만한거 노란색으로 했으면 좋았을텐데»
    #   → 라벨 뺌 · 핵심 말 노랑(숫자 초록 · 결론 빨강과 겹치지 않게)
    *[{"type": "color", "on": w, "color": "yellow"} for w in
      ("짜증 나시죠?", "DB관리", "자동으로", "한번이면", "편하게", "한 눈에", "하루만에", "선착순", "10곳 만")],
]


def calc_lines(W, H, lines):
    """caption_fx.calc_lines + «-» 를 먼저 띄우는 줄: ["-", 색, …] 다음 줄이 ["- 80%", …] 이면 같은 줄(y)에서
    «-» 만(흰) → 숫자만(초록, «-» 부분은 지움) 두 층으로 나눈다."""
    from PIL import ImageFont
    k = W / 1080
    rows, out = [], []
    for txt, col, frag, d in lines:
        if txt == "-":
            continue
        rows.append([txt, col, frag, d])
    base = CF.calc_lines(W, H, rows)
    f = CF.noto(int(140 * k))
    ri = 0
    for txt, col, frag, d in lines:
        if txt == "-":
            nxt = next(r for r in rows[ri:] if r[0].startswith("- "))
            full_w = f.getlength(nxt[0])
            cut = int(W / 2 - full_w / 2 + f.getlength("-") + 14 * k)
            ys = [575, 740, 855, 960]
            im = CF.text_layer(W, H, nxt[0], 540, ys[min(rows.index(nxt), 3)], 140, CF.COL["white"], 4)
            im.paste((0, 0, 0, 0), (cut, 0, W, H))
            out.append(im)
            continue
        im = base[ri]
        if txt.startswith("- "):
            full_w = f.getlength(txt)
            cut = int(W / 2 - full_w / 2 + f.getlength("-") + 14 * k)
            im = im.copy()
            im.paste((0, 0, 0, 0), (0, 0, cut, H))
        out.append(im)
        ri += 1
    return out


def user_caps(seq_json):
    d = json.loads(Path(seq_json).read_text(encoding="utf-8"))
    caps = []
    for i in d["items"]:
        if i["track"] not in ("V2", "V3") or i["name"] not in ("그래픽", "계산 - 80%"):   # 37.57 «80%» 자리에 v2 그림을 쓰셨다
            continue
        t = " ".join(i.get("text") or []).strip() or FILL.get(round(i["t0"], 2), "")
        if t in QMARK and 25.0 < i["t0"] < 27.5:
            t += "?"
        if t:
            caps.append([i["t0"], i["t1"], t])
    caps.sort()
    for a, b in zip(caps, caps[1:]):          # 겹침(7.12 «이거 전화했어?» V3 ↔ 7.99 «문자 보냈어?») → 앞 자막을 뒷 자막 시작에서 끊는다
        if a[1] > b[0]:
            a[1] = b[0]
    return [tuple(c) for c in caps]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    seq, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    W, H, fps, dur = RC.probe(VIDEO)
    caps = user_caps(seq)
    find = CF.find_cap
    style, hidden, layers = {}, set(), []
    hidden.add(find(caps, "80%"))             # 그 자리는 계산식 «- 80%» 줄이 대신한다
    for fx in FX:
        ty = fx["type"]
        if ty in ("big", "color"):
            i = find(caps, fx["on"])
            sc, co = style.get(i, (1.0, "white"))
            style[i] = (fx.get("scale", sc), fx.get("color", co))
            continue
        after = caps[find(caps, fx["after"], fx.get("after_t", -1.0))][0] if fx.get("after") else -1.0
        if ty == "bignum_gap":
            i = find(caps, fx["after"], fx.get("after_t", -1.0))
            t0, t1 = caps[i][1], caps[i + 1][0]
            layers.append((5, t0, t1, f"큰숫자 {fx['text']}", CF.bignum_layer(W, H, fx["text"])))
            continue
        if "on" in fx:
            i0 = i1 = find(caps, fx["on"], after)
        else:
            i0 = find(caps, fx["from"], after)
            i1 = find(caps, fx["to"], caps[i0][0])
        t0, t1 = caps[i0][0], caps[i1][1]
        if ty == "arrow":
            a_ = math.radians(fx["angle"])
            far = [fx["tip"][0] - 28 * math.cos(a_), fx["tip"][1] - 28 * math.sin(a_)]
            ims = [CF.arrow_layer(W, H, far, fx["angle"]), CF.arrow_layer(W, H, fx["tip"], fx["angle"])]
            t, n = t0, 0
            while t < t1 - 1e-3:
                layers.append((4, t, min(t + 0.15, t1), f"화살표{n % 2}", ims[n % 2]))
                t += 0.15
                n += 1
        elif ty == "ff":
            layers.append((2, t0, t1, "빨리감기", CF.ff_layer(W, H)))
        elif ty == "speed":
            t, n = t0, 0
            while t < t1 - 1e-3:
                layers.append((2, t, min(t + 0.1, t1), f"집중선{n % 4}", CF.speed_layer(W, H, n % 4)))
                t += 0.1
                n += 1
        elif ty == "label":
            layers.append((4, t0, t1, f"라벨 {fx['text']}", CF.label_layer(W, H, fx["text"])))
        elif ty == "calc":
            ims = calc_lines(W, H, fx["lines"])
            for (txt, col, frag, delay), im in zip(fx["lines"], ims):
                s0 = caps[find(caps, frag, t0)][0] + (delay or 0)
                layers.append((5, s0, t1, f"계산 {txt}", im))
            hidden.update(range(i0, i1 + 1))

    pd = out / f"{NAME}_층"
    pd.mkdir(exist_ok=True)
    for f in pd.glob("*.png"):
        f.unlink()
    clips = []
    for i, (s, e, t) in enumerate(caps):
        if i in hidden:
            continue
        sc, co = style.get(i, (1.0, "white"))
        p = pd / f"V3_{i + 1:03d}.png"
        CF.caption_layer(W, H, t, sc, co).save(p)
        clips.append((3, s, e, f"{i + 1:03d} {t}", p))
    cache = {}
    for j, (tr, s, e, nm, im) in enumerate(layers):
        key = nm if nm.startswith(("집중선", "화살표")) else None
        if key and key in cache:
            p = cache[key]
        else:
            p = pd / f"V{tr}_{j:03d}.png"
            im.save(p)
            if key:
                cache[key] = p
        clips.append((tr, s, e, nm, p))
    (out / f"{NAME}.srt").write_text("".join(f"{i}\n{RC.ts(s)} --> {RC.ts(e)}\n{t}\n\n" for i, (s, e, t) in enumerate(caps, 1)),
                                     encoding="utf-8")
    (out / f"{NAME}_자막목록.txt").write_text(
        "\n".join(f"{s:6.2f}~{e:6.2f}  {t}{'  (숨김: 큰 숫자·계산식)' if i in hidden else ''}" for i, (s, e, t) in enumerate(caps)) + "\n",
        encoding="utf-8")
    CF.write_xml(out / f"{NAME}.xml", f"{NAME}_자막연출", VIDEO, clips, W, H, fps, dur, motion=True)
    CF.preview(out / f"{NAME}_미리보기.mp4", VIDEO, clips, motion=True)
    print(f"자막 {len(caps)}줄(숨김 {len(hidden)}) · 연출 층 {len(layers)}개 · {out}")


if __name__ == "__main__":
    main()
