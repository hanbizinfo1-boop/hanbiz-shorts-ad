# -*- coding: utf-8 -*-
r"""한 편 조립용 배치표(JSON) — 스키마 정의 · 불러오기 · 검증 · 프리미어 초안 변환.

[새로 만든 도구 — 원본 D:/영상제작/도구/광고편집/ 의 sg_render(XML 을 읽어 다시 조립) 를 «배치표 하나가 정본» 으로 뒤집은 것.
 sg_render.read_xml 의 XML 읽기는 from_premiere 로, 건 전용 값(CAPS·trig·PAL 절대경로)은 전부 배치표로 옮겼다.]

배치표 한 장이 편집의 정본이다 (workflow.md P4). 입력은 둘:
  ① 이쪽이 쓴다 (지시 + 대본)      ② 사장님 프리미어 초안 → edit_plan.from_premiere(path) (컷 순서·길이 그대로)
출력은 edit_render(미리보기 mp4 + _점검.txt) · edit_xml(프리미어 XML + media/).

시각 축 — 배치표의 모든 시각(초)은 «배속 전 타임라인» 이다 (sg_render 의 XML 시간과 같다). 최종 시각 = 배치표 시각 ÷ speed.
  컷의 원본은 1:1 로 흐른다: 원본 in..out 이 start..end 에 그대로 놓이고(out−in = end−start), 배속은 전체에 한 번만 건다.
  목소리·배경음 파일은 원속 그대로 두고, 렌더/XML 이 speed 로 만든다. 그래픽의 ‘anim’ 길이·자막 팝은 최종(배속 후) 초 기준.

스키마 (아래 키 말고는 읽지 않는다. * = 필수, 값이 없으면 PlanError)
{
  "name": "건 이름",                              # 출력 파일 이름
  "base_dir": ".",                                # 아래 모든 파일 경로의 기준. 배치표 파일 위치 기준 상대 또는 절대
  "seq": {"w": 1080, "h": 1920, "fps": 29.97},    # 없으면 config.W/H/FPS
  "speed": 1.15,            *                     # 배속. 기본값 없음 — 건마다 정한다 (원본에 1.12 / 1.15 가 섞여 있었다). 0.5~2.0
  "loudness_lufs": -14,     *                     # 마감 음량. 기본값 없음 (원본 −11 / −14 섞임)
  "voice": {"file": "목소리.wav", "start": 0.0},  *   # 원속 파일
  "bgm": {"file": "bgm.wav", "start": 0.0, "gain_db": -20, "fade_out": 1.0},    # 선택. gain_db 필수(원 파일에 거는 dB), fade_out 기본 1.0초(sg_render)
  "caption_style": {"mode": "band"|"outline", "band_fill": [52,52,56], "pad_x": 26, "pad_y": 14, "radius": 12, "y": 1150, "size": 66, "max_w": 960, "track": 3, "stroke": 9, "colors": {"y": [255,222,60], ...}},   # 선택 — 기본값은 아래 CAPTION_STYLE
  "script": ["대본 한 줄", ...],                  # 선택. 있으면 rule_check 4-1(자막 ≠ 원문) 로 대조
  "cuts": [{                                      *   빈틈·겹침 없이 0초부터 이어진다 (까만 화면 금지 1-4)
      "src": "a.mp4", "kind": "video|image",       # kind 는 확장자로 자동 (png/jpg/webp = image)
      "in": 0.0, "out": 3.0,                       # 원본 안 초 (video 필수, image 불필요)
      "start": 0.0, "end": 3.0,                    # 배치표 시각
      "scale": 1.0, "pos": [0, 0],                 # 리프레임. scale ≥ 1.0 (1.0 = 꽉 채움), pos = 화면 안에서 그림을 옮기는 px (여백 안쪽이어야 함)
      "tr": {"kind": "lensblur", "dur": 0.3, "mode": "enter"},    # 이 컷으로 «들어오는» 전환 (첫 컷은 없음). null = 그냥 컷. dur 필수
      "flash": false, "cont": false                # flash: 이 컷 첫 2프레임 흰색 · cont: 같은 자료의 이어진 샷(rule_check 1-1 예외)
  }],
  "captions": [{                                  # 선택
      "text": "한강 보이는 신축이", "start": 0.1, "end": 2.0,
      "emph": ["신축"], "emph_color": "y",          # 강조어(text 안에 있어야 함) · y 노랑 g 초록 p 보라
      "emph_from": null,                           # 강조색이 켜지는 시각. null = 처음부터 (그 전에는 흰색)
      "key": false, "anim": "pop"                  # key = 핵심 줄(1→120→100%). anim: pop(130→100 0.216초) | fade(페이드+0.94→1.0, 머무는 동안 →1.02) | none
  }],
  "graphics": [{                                  # 선택. PNG(알파) 또는 알파 MOV
      "file": "card.png", "start": 1.0, "end": 3.0,
      "pos": [540, 700], "scale": 1.0,             # pos = 그림 가운데의 화면 좌표(px). 생략 = 화면 가운데. MOV 는 전체 화면 크기여야 하고 pos/scale 무시
      "anim": "pop|fade|slide_up|none"             # 기본 none. 길이는 sg_render 값 (pop 0.25초 0.7→1.0 · fade 0.2초 · slide_up 0.25초 300px)
  }],
  "overlays": [{                                  # 선택. 알파 영상 층(html_motion --alpha 가 만든 ProRes 4444 MOV 등) — graphics 와 달리 «움직이는 장면 한 편»
      "file": "typo.mov", "t0": 1.0, "t1": 7.9,    # file = 알파 .mov/.webm · 알파 .png 한 장 · 알파 PNG 시퀀스("f_%05d.png"). t0/t1 = 배치표 시각(배속 전). 영상은 최종(배속 후) 초로 흐른다
      "x": 540, "y": 960, "scale": 1.0,            # x,y = 그림 가운데의 화면 좌표(px, 생략 = 화면 가운데) · scale = 원본 크기 대비(기본 1.0 = 원본 그대로; 1080x1920 장면이면 전체 화면)
      "name": "typo"                               # 표시 이름(생략 = 파일 이름). 영상이 (t1−t0)/speed 초보다 2프레임 넘게 짧으면 PlanError
  }],                                             #   미리보기: 그래픽 위·자막 아래에 합성 · XML: 원본 참조(PNG 시퀀스만 media/ 에 알파 MOV 로 구움) — 그래픽(V2) 다음 트랙, 겹치면 다음 트랙. 효과음은 events_to_sfx_plan()
  "sfx_roles": {"zoom": {"file": "휙２.mp3", "min_len": 0.0, "rel_db": 5, "align": "peak", "exact_db": -6, "prio": 1}},    # 선택. 역할 → 파일 (이름만 적는다 — sfx.find_file 이 라이브러리에서 찾는다. 배치표 옆 파일이 있으면 그것)
         # exact_db = 역할별 dB 예외 — FILE_DB(파일별 표)로 덮지 않고 «목소리 대비 이 dB 그대로» (sfx.exact / sfx.role(db=) 와 같다. 정수로 내림). 없으면 rel_db → FILE_DB 순
         # prio = 우선순위 1~4 (기본 1: 첫 등장 1 · 자막 2 · 내용·도장·가격·버튼 3 · 전환 4, sfx.md 15장). 3 이상이면 finish.accent, 1 이면 finish.overlap 의 대상
  "sfx": [{"t": 1.0, "role": "zoom"}, {"t": 2.0, "file": "맑은소리.mp3", "abs_db": -26}, {"t": 3.0, "file": "7. 뿅.mp3", "exact_db": 2, "prio": 3}]
         # t = 배치표 시각. abs_db 를 주면 «가장 큰 0.4초 RMS» 를 그 dB 로 맞춘다 (sg_render PAL 방식). 없으면 sfx.prep (목소리 대비 FILE_DB)
         # exact_db / prio 는 이 한 발에만 (role 항목에서도 쓸 수 있다 — 역할의 값을 이 한 발만 덮는다). exact_db 와 abs_db 는 같이 못 쓴다
         # burst: "사유" — 사장님이 시킨 연타(박수 3연타 등). rule_check 5-2·5-2b·5-4 에서 뺀다(sfx.md 결정표 ⑦)
  # "sfx_per_ep_max": 2  선택. 한 편 같은 파일 횟수 상한(5-4, 기본 2). null = 안 봄 — 말 없는 타이포(분당 130)처럼 사유가 있을 때만
  "finish": {"reverb": true, "overlap": true, "bgm_eq": true, "duck": true, "duck_db": -9, "accent": true, "accent_db": -3,
             "master_comp": true, "limiter": true, "peak_norm": true},
         # 선택 — 한 편 마감 체인(sfx.md 15장)의 단계별 스위치. 안 적은 키는 위 값(= 원본 v5_sound 대로 켬). 미리보기에만 적용되고 XML 에는 안 간다(_점검.txt 에 목록)
         #   reverb 효과음 버스 43·71·113ms · overlap 0.12초 겹침 제거 · bgm_eq BGM 필터+앞 페이드인 · duck 말 밑 BGM 덕킹(duck_db ≤ 0)
         #   accent prio≥3 효과음 순간 BGM 비킴(accent_db ≤ 0) · master_comp loudnorm 앞 컴프 · limiter loudnorm 뒤 alimiter 0.89 · peak_norm 합산 피크 0.95
}
"""
import json
import subprocess
from fractions import Fraction
from pathlib import Path

import config as C

IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
TR_KINDS = ["zoomblur", "dirblur", "push", "rays", "lensblur", "flare", "crosszoom"]    # rf5_render.TR_CYCLE (사장님 분양과오2 에서 읽은 7종)
TR_STRADDLE = ["lensblur", "flare", "dirblur", "zoomblur", "spin"]                       # sg_render.tr_fx — mode="straddle" 일 때
EMPH_KEYS = ("y", "g", "p")
CAPTION_STYLE = {                  # sg_render 09-29 (세로 1080×1920, 사장님 «자막이 너무 하단 → 중앙에서 살짝 아래»). ☐ 쇼츠 확정 수치(SKILL 6장)로 바뀌면 여기
    # 10-08 사장님 «만약에 설명하면서 진행하는건 a스타일인데 테두리색 살짝 현재보다 좀더 회색빛돌게하고 테두리크기를 좀 줄여줘» → 설명형 = A2
    #   mode "band"(기본) = 불투명 둥근 띠(band_fill) + 외곽선 없는 글자 / "outline" = 띠 없음 + 검정 외곽선 stroke px + 그림자(blur 6 · 0.5, 예전 기본)
    "mode": "band", "band_fill": [52, 52, 56], "pad_x": 26, "pad_y": 14, "radius": 12,
    "y": 1150, "size": 66, "max_w": 960, "track": 3, "stroke": 9,       # stroke 는 outline 모드에서만 쓴다
    "colors": {"white": [245, 245, 245], "y": [255, 222, 60], "g": [60, 235, 110], "p": [190, 140, 245]},
}
FLASH_FRAMES = 2                   # workflow P4 «섹션 바뀔 때만 흰 플래시 2프레임»
FINISH_DEFAULT = {                 # sfx.md 15장 / 원본 v5_sound.py mix·master — 기본은 원본대로 전부 켬
    "reverb": True, "overlap": True, "bgm_eq": True, "duck": True, "duck_db": -9.0, "accent": True, "accent_db": -3.0,
    "master_comp": True, "limiter": True, "peak_norm": True,
}
GFX_ANIMS = ("none", "pop", "fade", "slide_up")
OVL_EXT = (".mov", ".webm", ".png")
CAP_ANIMS = ("pop", "fade", "none")
CAP_MODES = ("band", "outline")


class PlanError(ValueError):
    def __init__(self, errors):
        self.errors = list(errors)
        super().__init__("배치표 오류 %d건:\n  - " % len(self.errors) + "\n  - ".join(self.errors))


# ───────────────────────── 보조 ─────────────────────────

def fps_frac(fps):
    """29.97 → 30000/1001 처럼 방송용 레이트는 정확한 분수로."""
    for v, n, d in ((29.97, 30000, 1001), (59.94, 60000, 1001), (23.976, 24000, 1001), (119.88, 120000, 1001)):
        if abs(fps - v) < 0.005:
            return Fraction(n, d)
    return Fraction(fps).limit_denominator(1000)


def is_image(path):
    return Path(str(path)).suffix.lower() in IMG_EXT


_PROBE = {}


def probe(path):
    """영상/그림 → dict(w, h, fps, dur, image). 회전 메타(세로 촬영)는 가로·세로를 맞바꿔 돌려준다."""
    key = str(path)
    if key in _PROBE:
        return _PROBE[key]
    if is_image(path):
        from PIL import Image
        with Image.open(path) as im:
            info = dict(w=im.width, h=im.height, fps=None, dur=None, image=True)
    else:
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                            "-show_entries", "stream=width,height,r_frame_rate:stream_side_data=rotation",
                            "-show_entries", "format=duration", "-of", "json", str(path)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        j = json.loads(r.stdout)
        st = j["streams"][0]
        n, d = (int(x) for x in st["r_frame_rate"].split("/"))
        w, h = st["width"], st["height"]
        if any(abs(int(sd.get("rotation", 0))) in (90, 270) for sd in st.get("side_data_list", [])):
            w, h = h, w
        info = dict(w=w, h=h, fps=n / d, dur=float(j["format"]["duration"]), image=False)
    _PROBE[key] = info
    return info


def overlay_frames(plan, o):
    """오버레이 파일의 프레임 파일 목록(시퀀스) 또는 [파일] — 없으면 []."""
    p = abs_path(plan, o["file"])
    if "%" in p.name:
        import re
        return sorted(p.parent.glob(re.sub(r"%0?\d*d", "*", p.name)))
    return [p] if p.exists() else []


def overlay_kind(plan, o):
    """"seq"(PNG 시퀀스) | "still"(PNG 한 장) | "video"(.mov/.webm)"""
    p = Path(str(o["file"]))
    if "%" in p.name:
        return "seq"
    return "still" if p.suffix.lower() == ".png" else "video"


def audio_dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:              # 10-13 길이 0 효과음 wav(0초 큐가 앞으로 잘림)는 ffprobe 가 N/A — 샘플 수로 센다
        import soundfile as sf
        info = sf.info(str(path))
        return info.frames / info.samplerate


def abs_path(plan, rel):
    p = Path(str(rel))
    return p if p.is_absolute() else (plan["_base"] / p)


def out_time(plan, t):
    """배치표 시각 → 최종(배속 후) 초."""
    return t / plan["speed"]


def frame_range(plan, t0, t1, n_out=None):
    """배치표 시각 구간 → 출력 프레임 [j0, j1). 한 프레임의 시각이 구간 시작 이상이면 들어간다(sg_xml2 와 같은 규칙)."""
    import math
    f = float(plan["_fps"])
    j0 = int(math.ceil(t0 / plan["speed"] * f - 1e-6))
    j1 = int(math.ceil(t1 / plan["speed"] * f - 1e-6))
    if n_out is not None:
        j1 = min(j1, n_out)
    return j0, j1


def n_frames(plan):
    return frame_range(plan, 0, plan["cuts"][-1]["end"])[1]


# ───────────────────────── 불러오기 · 검증 ─────────────────────────

def _fill(plan, base):
    plan["_base"] = base
    seq = plan.setdefault("seq", {})
    seq.setdefault("w", C.W)
    seq.setdefault("h", C.H)
    seq.setdefault("fps", C.FPS)
    plan["_fps"] = fps_frac(float(seq["fps"]))
    st = json.loads(json.dumps(CAPTION_STYLE))
    st.update({k: v for k, v in (plan.get("caption_style") or {}).items() if k != "colors"})
    st["colors"].update((plan.get("caption_style") or {}).get("colors", {}))
    plan["caption_style"] = st
    if st["mode"] not in CAP_MODES:
        raise PlanError([f"caption_style.mode {st['mode']} — {CAP_MODES}"])
    bf = st["band_fill"]
    if not (isinstance(bf, (list, tuple)) and len(bf) == 3 and all(isinstance(v, int) and 0 <= v <= 255 for v in bf)):
        raise PlanError([f"caption_style.band_fill {bf} — [r,g,b] 0~255 정수"])
    for k in ("pad_x", "pad_y", "radius", "stroke"):
        if not isinstance(st[k], (int, float)) or st[k] < 0:
            raise PlanError([f"caption_style.{k} {st[k]} — 0 이상 숫자"])
    for c in plan.get("cuts", []):
        c.setdefault("kind", "image" if is_image(c.get("src", "")) else "video")
        c.setdefault("scale", 1.0)
        c.setdefault("pos", [0, 0])
        c.setdefault("tr", None)
        c.setdefault("flash", False)
        c.setdefault("cont", False)
        if c.get("tr"):
            c["tr"].setdefault("mode", "enter")
    for c in plan.get("captions", []):
        c.setdefault("emph", [])
        c.setdefault("emph_color", "y")
        c.setdefault("emph_from", None)
        c.setdefault("key", False)
        c.setdefault("anim", "pop")
    for g in plan.get("graphics", []):
        g.setdefault("anim", "none")
        g.setdefault("scale", 1.0)
    plan.setdefault("overlays", [])
    for o in plan["overlays"]:
        o.setdefault("scale", 1.0)
        o.setdefault("x", None)
        o.setdefault("y", None)
        if o.get("file"):
            o.setdefault("name", Path(str(o["file"])).stem)
    plan.setdefault("sfx_roles", {})
    plan.setdefault("sfx", [])
    plan["finish"] = {**FINISH_DEFAULT, **(plan.get("finish") or {})}
    return plan


def validate(plan, check_files=True):
    """→ 오류 문자열 목록 (비면 통과)."""
    E = []
    sp = plan.get("speed")
    if sp is None:
        E.append("speed 없음 — 배속은 건마다 정한다 (기본값 없음; 원본에 1.12 / 1.15 가 섞여 있었다)")
    elif not (0.5 <= float(sp) <= 2.0):
        E.append(f"speed {sp} — 0.5~2.0 만 (atempo 한 단)")
    if plan.get("loudness_lufs") is None:
        E.append("loudness_lufs 없음 — 마감 음량은 건마다 정한다 (기본값 없음; 원본에 −11 / −14 가 섞여 있었다)")
    if not plan.get("name"):
        E.append("name 없음")
    base = plan["_base"]
    chk = lambda rel, what: E.append(f"{what} 파일 없음: {rel}") if check_files and not abs_path(plan, rel).exists() else None   # noqa: E731

    v = plan.get("voice")
    if not v or not v.get("file"):
        E.append("voice.file 없음")
    else:
        chk(v["file"], "voice")
        v.setdefault("start", 0.0)
    b = plan.get("bgm")
    if b:
        if not b.get("file"):
            E.append("bgm.file 없음")
        else:
            chk(b["file"], "bgm")
        if b.get("gain_db") is None:
            E.append("bgm.gain_db 없음 — 배경음 크기는 건마다 정한다")
        b.setdefault("start", 0.0)
        b.setdefault("fade_out", 1.0)

    cuts = plan.get("cuts") or []
    if not cuts:
        E.append("cuts 가 비었다")
    f = float(plan["_fps"]) if "_fps" in plan else 30.0
    one_frame = float(sp or 1) / f
    prev_end = 0.0
    for i, c in enumerate(cuts):
        at = f"cuts[{i}]"
        for k in ("src", "start", "end"):
            if c.get(k) is None:
                E.append(f"{at}.{k} 없음")
        if c.get("start") is None or c.get("end") is None or not c.get("src"):
            continue
        if c["end"] <= c["start"]:
            E.append(f"{at} end ≤ start")
        if abs(c["start"] - prev_end) > 1e-3:
            E.append(f"{at} 시작 {c['start']} ≠ 앞 컷 끝 {prev_end} — 빈틈/겹침 (까만 화면 금지)")
        prev_end = c["end"]
        s = c["scale"]
        if s < 1.0:
            E.append(f"{at}.scale {s} < 1.0 — 여백(까만 띠)이 생긴다")
        if len(c["pos"]) != 2:
            E.append(f"{at}.pos 는 [x, y]")
        if c["kind"] not in ("video", "image"):
            E.append(f"{at}.kind {c['kind']}")
        if c["tr"]:
            if i == 0:
                E.append(f"{at} 첫 컷에는 전환이 없다")
            t = c["tr"]
            if not t.get("dur") or t["dur"] <= 0:
                E.append(f"{at}.tr.dur 없음 — 전환 길이(최종 초)는 적는다")
            allowed = TR_STRADDLE if t["mode"] == "straddle" else TR_KINDS
            if t.get("kind") not in allowed:
                E.append(f"{at}.tr.kind {t.get('kind')} — {t['mode']} 모드는 {allowed} 중에서")
            if t["mode"] not in ("enter", "straddle"):
                E.append(f"{at}.tr.mode {t['mode']}")
        if check_files:
            p = abs_path(plan, c["src"])
            if not p.exists():
                E.append(f"{at} 원본 없음: {c['src']}")
                continue
            info = probe(p)
            if c["kind"] == "video":
                if c.get("in") is None or c.get("out") is None:
                    E.append(f"{at} video 컷은 in/out 필수")
                    continue
                if abs((c["out"] - c["in"]) - (c["end"] - c["start"])) > one_frame + 1e-6:
                    E.append(f"{at} out−in {c['out'] - c['in']:.3f} ≠ end−start {c['end'] - c['start']:.3f} (원본은 1:1 로 흐른다; 배속은 plan.speed 한 곳)")
                if c["in"] < 0 or c["out"] > info["dur"] + one_frame:
                    E.append(f"{at} 원본 {Path(c['src']).name} 길이 {info['dur']:.2f}초를 벗어남 (in {c['in']}, out {c['out']})")
            # 리프레임 여백 — pos 는 확대된 그림의 남는 폭 안이어야 한다
            W, H = plan["seq"]["w"], plan["seq"]["h"]
            k = max(W / info["w"], H / info["h"]) * s
            mx, my = (info["w"] * k - W) / 2, (info["h"] * k - H) / 2
            if abs(c["pos"][0]) > mx + 0.5 or abs(c["pos"][1]) > my + 0.5:
                E.append(f"{at}.pos {c['pos']} — 옮길 수 있는 폭은 ±({mx:.0f}, {my:.0f})px (넘으면 까만 띠)")

    for i, c in enumerate(plan.get("captions", [])):
        at = f"captions[{i}]"
        if not c.get("text") or c.get("start") is None or c.get("end") is None:
            E.append(f"{at} text/start/end 필수")
            continue
        if c["end"] <= c["start"]:
            E.append(f"{at} end ≤ start")
        for w in c["emph"]:
            if w not in c["text"]:
                E.append(f"{at} 강조어 «{w}» 가 text 에 없다")
        if c["emph"] and c["emph_color"] not in EMPH_KEYS:
            E.append(f"{at}.emph_color {c['emph_color']} — {EMPH_KEYS}")
        if c["anim"] not in CAP_ANIMS:
            E.append(f"{at}.anim {c['anim']}")
    for i, g in enumerate(plan.get("graphics", [])):
        at = f"graphics[{i}]"
        if not g.get("file") or g.get("start") is None or g.get("end") is None:
            E.append(f"{at} file/start/end 필수")
            continue
        chk(g["file"], at)
        if g["anim"] not in GFX_ANIMS:
            E.append(f"{at}.anim {g['anim']}")
    for i, o in enumerate(plan.get("overlays", [])):
        at = f"overlays[{i}]"
        if not o.get("file") or o.get("t0") is None or o.get("t1") is None:
            E.append(f"{at} file/t0/t1 필수")
            continue
        if o["t1"] <= o["t0"] or o["t0"] < 0:
            E.append(f"{at} t0/t1 — 0 ≤ t0 < t1 이어야 한다")
        if Path(str(o["file"])).suffix.lower() not in OVL_EXT:
            E.append(f"{at}.file {o['file']} — 알파가 있는 {OVL_EXT} (또는 %05d.png 시퀀스)만. mp4 는 알파가 없다")
        if not isinstance(o["scale"], (int, float)) or isinstance(o["scale"], bool) or o["scale"] <= 0:
            E.append(f"{at}.scale {o['scale']!r} — 0 보다 큰 숫자")
        for k in ("x", "y"):
            if o[k] is not None and (isinstance(o[k], bool) or not isinstance(o[k], (int, float))):
                E.append(f"{at}.{k} {o[k]!r} — 숫자(px) 이거나 생략")
        if check_files and Path(str(o["file"])).suffix.lower() in OVL_EXT:
            fr = overlay_frames(plan, o)
            if not fr:
                E.append(f"{at} 파일 없음: {o['file']}")
                continue
            kind = overlay_kind(plan, o)
            need = (o["t1"] - o["t0"]) / float(sp or 1)
            have = len(fr) / float(plan["_fps"]) if kind == "seq" else (probe(fr[0])["dur"] if kind == "video" else None)
            if have is not None and have < need - 2 / float(plan["_fps"]):
                E.append(f"{at} {Path(str(o['file'])).name} 길이 {have:.2f}초 < 구간 (t1−t0)/speed = {need:.2f}초 — 영상이 끝난 뒤 붙잡아 주지 않는다. 구간을 줄이거나 더 긴 영상으로")
    for i, e in enumerate(plan.get("sfx", [])):
        at = f"sfx[{i}]"
        if e.get("t") is None:
            E.append(f"{at}.t 없음")
        if not (e.get("role") or e.get("file")):
            E.append(f"{at} role 또는 file 필요")
        if e.get("role") and e["role"] not in plan["sfx_roles"]:
            E.append(f"{at}.role {e['role']} 가 sfx_roles 에 없다")
        E += _sfx_num_errors(at, e)
        if e.get("exact_db") is not None and e.get("abs_db") is not None:
            E.append(f"{at} exact_db 와 abs_db 는 같이 못 쓴다 (exact_db = 목소리 대비 dB, abs_db = 절대 RMS dB)")
    for name, r in plan["sfx_roles"].items():
        E += _sfx_num_errors(f"sfx_roles.{name}", r)
    fin = plan["finish"]
    for k, v in fin.items():
        if k not in FINISH_DEFAULT:
            E.append(f"finish.{k} — 모르는 키 {list(FINISH_DEFAULT)}")
        elif isinstance(FINISH_DEFAULT[k], bool) != isinstance(v, bool):
            E.append(f"finish.{k} {v!r} — {'true/false' if isinstance(FINISH_DEFAULT[k], bool) else '숫자(dB)'} 여야 한다")
    for k in ("duck_db", "accent_db"):
        if isinstance(fin.get(k), (int, float)) and not isinstance(fin.get(k), bool) and fin[k] > 0:
            E.append(f"finish.{k} {fin[k]} — 비키는 양이라 0 이하여야 한다")
    return E


def _sfx_num_errors(at, e):
    """효과음 항목·역할의 숫자 키(exact_db · rel_db · abs_db · prio) 검사."""
    E = []
    for k in ("exact_db", "rel_db", "abs_db"):
        v = e.get(k)
        if v is not None and (isinstance(v, bool) or not isinstance(v, (int, float))):
            E.append(f"{at}.{k} {v!r} — 숫자(dB)여야 한다")
    pr = e.get("prio")
    if pr is not None and (isinstance(pr, bool) or pr not in (1, 2, 3, 4)):
        E.append(f"{at}.prio {pr!r} — 1~4 (sfx.md 15장: 첫 등장 1 · 자막 2 · 내용·도장 3 · 전환 4)")
    return E


def load(path, check_files=True):
    path = Path(path)
    plan = json.loads(path.read_text(encoding="utf-8"))
    base = Path(plan.get("base_dir", "."))
    base = base if base.is_absolute() else (path.parent / base).resolve()
    _fill(plan, base)
    errs = validate(plan, check_files)
    if errs:
        raise PlanError(errs)
    return plan


def save(plan, path):
    d = {k: v for k, v in plan.items() if not k.startswith("_")}
    Path(path).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


# ───────────────────────── rule_check 용 화면 목록 ─────────────────────────

def shots(plan):
    """check_plan 이 받는 화면 목록 — 시각은 최종(배속 후) 초."""
    out = []
    for i, c in enumerate(plan["cuts"]):
        t0, t1 = out_time(plan, c["start"]), out_time(plan, c["end"])
        seg = next((k for k, cp in enumerate(plan["captions"]) if cp["start"] < c["end"] and cp["end"] > c["start"]), 0)
        out.append(dict(t0=t0, t1=t1, seg=seg, src=str(abs_path(plan, c["src"])), kind=c["kind"],
                        tr=(c["tr"] or {}).get("kind"), cont=c["cont"], props=[]))
    return out


# ───────────────────────── 프리미어 초안 → 배치표 ─────────────────────────

def _xml_fps(rate):
    tb = int(rate.findtext("timebase"))
    return tb * 1000 / 1001 if (rate.findtext("ntsc") or "").upper() == "TRUE" else float(tb)


def _url_path(u):
    import urllib.parse
    s = urllib.parse.unquote(u or "")
    for pre in ("file://localhost/", "file:///", "file://"):
        if s.startswith(pre):
            return s[len(pre):]
    return s


def _remap_speed(clip):
    """Time Remap 효과의 속도(%) → 배수. 없으면 None."""
    for eff in clip.iter("effect"):
        if (eff.findtext("effectid") or "").lower() == "timeremap":
            for p in eff.iter("parameter"):
                if (p.findtext("parameterid") or "") == "speed":
                    try:
                        return float(p.findtext("value")) / 100.0
                    except (TypeError, ValueError):
                        return None
    return None


def from_premiere(path, speed=None, loudness_lufs=None, sequence=None, media_dir=None, name=None):
    """사장님 프리미어 초안(FCP7 XML 또는 .prproj) → 배치표 dict. 컷 순서·길이를 그대로 옮긴다.

    · 초안의 시각은 «배속 전 타임라인» 으로 본다(sg_render 와 같다). 단 Time Remap(속도 효과)이 모든 V1 클립에 같은 값으로 있으면
      (edit_xml 이 내보낸 XML) 그 값이 speed 이고, 시퀀스 시각 × speed 로 되돌려 같은 배치표를 얻는다.
    · speed·loudness_lufs 는 초안에 없으니 인자로 받는다. 없으면 None 으로 두고 검증(validate)이 «채울 것» 으로 알려 준다.
    · V1 컷만 읽는다. V2 이상(그래픽·자막)·효과음은 건너뛰고 plan["_notes"] 에 적는다 — 초안은 «컷만 잡은 것».
    · .prproj 는 read_prproj 의 트랙 읽기를 쓴다. ☐ 실제 사장님 초안으로는 아직 시험하지 못했다(합성 XML 만 시험).
    """
    path = Path(path)
    if path.suffix.lower() == ".prproj":
        return _from_prproj(path, speed, loudness_lufs, sequence, media_dir, name)
    import xml.etree.ElementTree as ET
    root = ET.parse(path).getroot()
    seq = root.find("sequence") if root.tag != "sequence" else root
    if seq is None:
        raise PlanError([f"{path.name}: sequence 요소가 없다"])
    sfps = _xml_fps(seq.find("rate"))
    fmt = seq.find("media/video/format/samplecharacteristics")
    w = int(fmt.findtext("width")) if fmt is not None else C.W
    h = int(fmt.findtext("height")) if fmt is not None else C.H
    notes = []
    vt = seq.find("media/video").findall("track")
    clips = []
    files = {}
    for ci in vt[0].findall("clipitem"):
        if (ci.findtext("enabled") or "TRUE").upper() == "FALSE":
            continue
        f = ci.find("file")
        if f is not None and f.find("pathurl") is not None:
            files[f.get("id")] = (_url_path(f.findtext("pathurl")), _xml_fps(f.find("rate")) if f.find("rate") is not None else sfps)
        fp, ffps = files.get(f.get("id"), (ci.findtext("name"), sfps)) if f is not None else (ci.findtext("name"), sfps)
        clips.append(dict(src=fp, ffps=ffps, s=int(ci.findtext("start")), e=int(ci.findtext("end")),
                          i=int(ci.findtext("in")), o=int(ci.findtext("out")), sp=_remap_speed(ci)))
    clips.sort(key=lambda c: c["s"])
    sps = {round(c["sp"], 4) for c in clips if c["sp"]}
    if sps:
        if len(sps) > 1 or any(not c["sp"] for c in clips if Path(c["src"]).suffix.lower() not in IMG_EXT):   # 그림 컷은 속도 효과가 없다
            raise PlanError([f"V1 클립 속도가 제각각이다 {sorted(sps)} — 컷별 배속은 배치표에 없다"])
        speed = sps.pop()
    k = speed if any(c["sp"] for c in clips) else 1.0       # 시퀀스 시각 → 배치표 시각 (초안은 배속 전 타임라인이라 1)
    cuts = []
    for c in clips:
        cut = dict(src=c["src"], start=round(c["s"] / sfps * k, 4), end=round(c["e"] / sfps * k, 4))
        if not Path(c["src"]).suffix.lower() in IMG_EXT:
            cut["in"] = round(c["i"] / c["ffps"], 4)
            cut["out"] = round(c["o"] / c["ffps"], 4)
        cuts.append(cut)
    if len(vt) > 1 and any(t.findall("clipitem") for t in vt[1:]):
        notes.append("V2 이상(그래픽·자막)은 읽지 않았다 — 초안의 컷만 옮김")
    at = seq.find("media/audio")
    voice = bgm = None
    if at is not None:
        for n, t in enumerate(at.findall("track")):
            ci = t.find("clipitem")
            if ci is None:
                continue
            f = ci.find("file")
            p = _url_path(f.findtext("pathurl")) if f is not None and f.find("pathurl") is not None else ci.findtext("name")
            if n == 0 and voice is None:
                voice = dict(file=p, start=round(int(ci.findtext("start")) / sfps * k, 4))
            elif n == 1 and bgm is None:
                bgm = dict(file=p, start=round(int(ci.findtext("start")) / sfps * k, 4), gain_db=None)
        if any(t.findall("clipitem") for t in at.findall("track")[2:]):
            notes.append("A3 이상(효과음)은 읽지 않았다")
    if any(c["sp"] for c in clips):
        notes.append("Time Remap 속도가 있어 시퀀스 시각 × speed 로 되돌렸다. A1/A2 는 이미 배속이 구워진 파일일 수 있다 — 원속 파일로 바꿔 넣을 것")
    plan = dict(name=name or seq.findtext("name") or path.stem, base_dir=".", seq=dict(w=w, h=h, fps=round(sfps, 3)),
                speed=speed, loudness_lufs=loudness_lufs, voice=voice or dict(file=None), cuts=cuts, captions=[], graphics=[], sfx=[])
    if bgm:
        plan["bgm"] = bgm
    plan["_notes"] = notes
    return plan


def _from_prproj(path, speed, loudness_lufs, sequence, media_dir, name):
    import read_prproj as RP
    root = RP.load(path)
    pj = RP.Proj(root)
    seqs = [el for el in root.iter("Sequence") if (sequence is None or (el.findtext("Name") or "") == sequence)]
    if not seqs:
        raise PlanError([f"{path.name}: 시퀀스 «{sequence}» 를 못 찾았다"])

    def rows_of(seq):
        rows = []
        tg_root = seq.find("TrackGroups")
        if tg_root is None:
            return rows
        for tg in tg_root.iter("TrackGroup"):
            g = pj.d(tg.find("Second"))
            if g is None or g.find(".//Tracks") is None or g.tag != "VideoTrackGroup":
                continue
            for tr in g.find(".//Tracks"):
                t = pj.d(tr)
                if t is not None and int(tr.get("Index")) == 0:
                    rows += RP.read_track(pj, t, "V", 1)
        return rows
    seq = max(seqs, key=lambda s: len(rows_of(s)))
    rows = [r for r in sorted(rows_of(seq), key=lambda r: r["t0"]) if r.get("name") and not r["type"].endswith("TransitionTrackItem")]
    md = Path(media_dir) if media_dir else None
    cuts = []
    for r in rows:
        src = r["name"]
        if md:
            hit = next(iter(md.rglob(src)), None)
            src = str(hit) if hit else src
        cut = dict(src=src, start=round(r["t0"], 4), end=round(r["t1"], 4))
        if not Path(src).suffix.lower() in IMG_EXT:
            cut["in"] = round(r.get("s0") or 0.0, 4)
            cut["out"] = round(cut["in"] + (cut["end"] - cut["start"]), 4)
        cuts.append(cut)
    return dict(name=name or (seq.findtext("Name") or path.stem), base_dir=".", seq=dict(w=C.W, h=C.H, fps=C.FPS), speed=speed,
                loudness_lufs=loudness_lufs, voice=dict(file=None), cuts=cuts, captions=[], graphics=[], sfx=[],
                _notes=["prproj 는 클립 단위 InPoint 만 읽어 in 이 틀릴 수 있다(트랙 아이템의 실제 in 은 읽지 않음) — XML 로 내보낸 초안이 정확하다",
                        "voice 는 비어 있다 — 채울 것"])


if __name__ == "__main__":
    import sys
    try:
        p = load(sys.argv[1])
        print(f"통과: 컷 {len(p['cuts'])} · 자막 {len(p['captions'])} · 그래픽 {len(p['graphics'])} · 오버레이 {len(p['overlays'])} · 효과음 {len(p['sfx'])} · 최종 {out_time(p, p['cuts'][-1]['end']):.2f}초")
    except PlanError as e:
        print(e)
        sys.exit(1)
