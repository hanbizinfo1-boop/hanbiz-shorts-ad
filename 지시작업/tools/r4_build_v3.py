# -*- coding: utf-8 -*-
r"""4번 레퍼연출 v3(10-20) — v2 에 사장님 앞부분 수정 6가지.

사장님(10-20):
  «일단 강남빌딩할떄 자막 밑에 크게 강남빌딩이 레이저쏘듯이와서 펑 박히면 좋겠고
   확실한투자가 있다 할때 물음표를 약간 띵띵띵 이렇게 3개 띄워주면 좋을거같아
   아 말도 안돼요 그거는 << 연출이 너무 부족함
   이 영상보지마세요 할때 x자 하잖아 이때 짧게 흔들리는 연출 (효과음동반)
   30억으로 100억만드려고하는데 --> 통장에 30억이 찍혀있고 이게 대표머리위에서 실시간으로 계좌잔액이 100억으로 바뀌는 연출
   예금하려는 분들없죠? --> 밑에 사람이 예금? 하면서 의문을 품는듯한 연출
   일단 여기까지 수정해봐»

v2(r4_build_v2.py) 그대로 + 아래만 다름
  - 장면 `scenes/r4_ref_v3.html`(= v2 + `_v3_open.js` 레이저·물음표·말도 안 돼·집중선 · `_v3_bank.js` 통장 · `_v3_fig.js` 갸웃 인형)
  - 바탕: 흔들림 0.30(펑) · 5.18(X자, 4.MP4 5.10~5.50 팔 교차) 추가 · 1.97~2.72 절레절레(좌우) · 2.72 «그거는» 1.12→1.24 당김

    python 지시작업/tools/r4_build_v3.py prep
    python tools/html_motion.py 지시작업/tools/scenes/r4_ref_v3.html --alpha --workers 2 --sub 3 --out 지시작업/_tmp/r4v3 --name r4_ref_v3
    python 지시작업/tools/r4_build_v3.py plan
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r4_build as V1  # noqa: E402
import r4_build_v2 as V2  # noqa: E402

V2.WORK = V1.DZ / "_tmp/r4v3"
V2.DELIV = V1.DZ / "납품/4번_레퍼연출_v3_1020"
V2.NAME = "4번_레퍼연출_v3"
V2.SCENE = "r4_ref_v3"
V2.SHAKE = {0.30: 14, 5.18: 18, **V2.SHAKE}

# ── 촬영 자료 컷어웨이(10-20) ──
# 사장님 «C:\Users\user\Downloads\연금형부동산연구소\새 폴더 여기에 촬영자료들이많은데 영상 정합성 맞는곳에 좀 적재적소에 넣어주면 좋을거같거든?
#   일단 니가한번 만들어봐 이건 전체화면전환 왔다갔다 하면서 만들어보면되고 자막은 노란색, 초록색 , 흰색으로만 구성»
# 사진 306장 전부 봄(지시작업/_tmp/broll/sheet_00~12.jpg · index.json). 카드·말풍선이 뜨는 구간은 피하고, 말과 맞는 사진만 전체 화면으로.
# 안 쓴 것: 카페 후기 캡처(닉네임) · 철거 사진(631px 저해상) · PDF 6개(글 문서)
BROLL_DIR = Path(r"C:\Users\user\Downloads\연금형부동산연구소\새 폴더")
CUTAWAY = [   # (시작, 끝, 파일, 가로 초점 0~1, 세로 초점 0~1)
    (0.00, 0.88, "KakaoTalk_20250418_153806194.jpg", .5, .45),       # «강남 빌딩보다» — 완공 건물(레이저 «강남빌딩»이 위에 박힘)
    (16.58, 17.42, "20150228_153555★.jpg", .55, .5),                  # «돈 있는 분들이» — 세미나 청중
    (17.42, 18.97, "KakaoTalk_20250418_152133579.jpg", .5, .45),     # «찾는게 강남빌딩이에요» — 22차 건물
    (27.13, 28.78, "KakaoTalk_20250418_152133579_03.jpg", .5, .45),  # «물론 시세차익은 얻을 수 있어요» — 26차 건물
    (28.78, 29.58, "KakaoTalk_20240825_140517528_02.jpg", .5, .5),   # «좋은데 사면» — 입지 분석 지도
    (33.43, 34.52, "KakaoTalk_20250418_152133579_06.jpg", .5, .5),   # «돈이 되는거에요» — 1층 가게 불 켜진 건물
    (38.76, 40.42, "KakaoTalk_20240825_140517528_01.jpg", .5, .5),   # «임차인이 확실히 들어있는 건물을» — 매물 분석 서류 더미
    (40.42, 41.44, "KakaoTalk_20210926_164040081_02.jpg", .62, .5),  # «사는 방법을» — 지도 펴 놓은 책상
    (42.48, 43.64, "KakaoTalk_20160626_191202694.jpg", .5, .5),      # «제가 18년동안» — 현장 점검
    (43.64, 44.07, "KakaoTalk_20250418_152133579_02.jpg", .5, .45),  # «45번을 그걸 했습니다» — 완공 건물 빠르게 넘김
    (44.07, 44.49, "KakaoTalk_20250418_152133579_05.jpg", .5, .45),
    (44.49, 44.92, "KakaoTalk_20250418_152133579_04.jpg", .5, .5),
    (44.92, 45.34, "KakaoTalk_20250418_152133579.jpg", .5, .45),
    (45.34, 46.56, "20150228_153638.jpg", .55, .5),                   # «저보다 많이 한 사람은» — 대형 세미나
    (51.42, 52.87, "KakaoTalk_20160626_191154377.jpg", .5, .5),      # «그런 경험을 한 사람에게» — 도면 보며 현장 점검
    (52.87, 54.25, "IMG_8539.JPG", .62, .45),                         # «배우고싶다 · 들어보고 싶다» — 강연
]
_seg = V1.segments


def segments():
    out = []
    tol = 0.02   # 사진 경계(대사 시각 반올림)와 프리미어 컷 경계(52.866 등)가 0.02초 안이면 같은 점 — 길이 0 조각 방지
    for a, b, s0, z, fx in _seg():
        cuts = sorted({a, b, *[x for c0, c1, *_ in CUTAWAY for x in (c0, c1) if a + tol < x < b - tol]})
        for x0, x1 in zip(cuts, cuts[1:]):
            ca = next((c for c in CUTAWAY if c[0] <= x0 + tol and x1 <= c[1] + tol), None)
            out.append((x0, x1, s0 + (x0 - a), z, dict(fx, broll=ca) if ca else fx))
    return out


V1.segments = segments


def broll_still(c, path):
    """사진 → 1080x1920 꽉 채우기(흐림 채우기 금지 — 초점 기준 잘라냄)."""
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(BROLL_DIR / c[2])).convert("RGB")
    w, h = im.size
    s = max(1080 / w, 1920 / h)
    im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    x = min(max(0, round(im.width * c[3] - 540)), im.width - 1080)
    y = min(max(0, round(im.height * c[4] - 960)), im.height - 1920)
    im.crop((x, y, x + 1080, y + 1920)).save(path, quality=95)


def prep():
    import subprocess
    seg_dir = V2.WORK / "seg"
    seg_dir.mkdir(parents=True, exist_ok=True)
    lst, segs = [], segments()
    for k, (a, b, s0, z, fx) in enumerate(segs):
        n = V1.frame(b) - V1.frame(a) + (1 if k == len(segs) - 1 else 0)
        p = seg_dir / f"s{k:02d}.mp4"
        if n <= 0:                       # 프리미어 컷 경계와 연출 경계가 1프레임 안 — 조각 없음
            continue
        if fx.get("broll"):
            still = seg_dir / f"s{k:02d}_still.jpg"
            broll_still(fx["broll"], still)
            f = {kk: v for kk, v in fx.items() if kk != "broll"}
            src = ["-loop", "1", "-framerate", f"{V1.FPS_N}/{V1.FPS_D}", "-i", str(still)]
            vfx = vf(1.0, f, b - a, a).replace(f"*(1+{V2.PUSH}*t/", "*(1+0.07*t/")    # 사진은 조금 더 당김(켄 번스)
        else:
            src = ["-ss", f"{s0:.4f}", "-i", str(V1.SRC)]
            vfx = vf(z, fx, b - a, a)
        subprocess.run(["ffmpeg", "-v", "error", "-y", *src, "-frames:v", str(n), "-an", "-vf", vfx,
                        "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-r", f"{V1.FPS_N}/{V1.FPS_D}", str(p)], check=True)
        lst.append(f"file '{p.as_posix()}'")
        print(f"  {k:02d} {a:6.2f}-{b:6.2f} {'사진 ' + fx['broll'][2] if fx.get('broll') else '줌 ' + str(z)} {n}프레임", flush=True)
    (seg_dir / "list.txt").write_text("\n".join(lst) + "\n", encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(seg_dir / "list.txt"), "-c", "copy",
                    str(V2.WORK / "base.mp4")], check=True)
    import shutil
    shutil.copy2(V1.WORK / "voice.wav", V2.WORK / "voice.wav")
    print(f"바탕 {V2.WORK / 'base.mp4'}")
WOBBLE = (1.97, 2.72)          # 절레절레 — 작아진 화면이 좌우로
PUNCH = (2.72, 1.24)           # «그거는» 순간 당김(줌 배수 목표)

V2.ROLE_FILES.update({
    "laser": [("ML_Electric whoosh.wav", -8)],
    "boom": [("Cinematic SFX - Massive Impact v1.wav", -4)],
    "ding": [("03_띵_딩.mp3", -9)],                               # 사장님이 시킨 «띵띵띵» 3연타 — burst
    "buzz": [("KN_error_001.wav", -9)],
    "focus": [("ML_Metal hit woosh.wav", -9)],
    "roll": [(str(V1.DZ / "소재/효과음/카운터_굴림_길게.wav"), -10)],
    "hit": [("KN_impactPunch_medium_000.wav", -5), *V2.ROLE_FILES["hit"]],
})
V2.EXTRA = [e for e in V2.EXTRA if e[0] != 3.47] + [(5.18, "hit")]   # 3.47 휙은 2.72 집중선이 대신 · 5.18 X자 흔들림
BURST = {"ding": "사장님 10-20 «물음표를 약간 띵띵띵 이렇게 3개»"}
V2.BURST_ROLES = set(BURST)
V2.ROLE_ALIGN = {"laser": "onset", "ding": "onset", "roll": "onset"}   # 10-20 점검: peak 맞춤이면 레이저가 0초 앞에서 시작해 잘림 · 굴림이 0.6초 먼저 남
V2.DROP = {("pop", "e_bag1"), ("marker", "ring")}   # 통장 카드·«착각» 타격과 겹쳐 잘림(5-5)

_vf = V2.vf


def vf(zoom, fx, dur, t0):
    f = _vf(zoom, fx, dur, t0)
    if abs(t0 - WOBBLE[0]) < 1e-3:   # 작아진 화면 통째로 좌우 흔들기 — pad 뒤에 한 번 더 crop/pad
        f = f.replace(f",fps={V1.FPS_N}", f",pad=1240:1920:80:0:black,crop=1080:1920:x='80+60*sin(t*26)*exp(-t*2.2)*gte(t,0.12)':y=0,fps={V1.FPS_N}", 1)
    if abs(t0 - PUNCH[0]) < 1e-3:
        z = f"{zoom}*(1+({PUNCH[1] / zoom - 1:.4f})*min(t/0.18,1))"
        f = f.replace(f"{zoom}*(1+{V2.PUSH}*t/{dur:.3f})", z)
    return f


V2.vf = vf

_plan = V2.plan


def plan():
    _plan()
    import json
    p = V2.WORK / f"plan_{V2.NAME}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    for s in d["sfx"]:
        for role, why in BURST.items():
            if s["role"].startswith(role + "_"):
                s["burst"] = why
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    {"prep": prep, "plan": plan}[sys.argv[1]]()
