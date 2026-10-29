"""퓨레바 육아 쇼츠 3차 — 실촬영 컷 + 자막 + 화면 글 + 효과음 → 완성 mp4 (1080×1920 · 59.94).

python 지시작업/tools/pureva_build.py [--only-audio] [--frames 1.2,22.9,…]
설계 = 스토리보드 PDF(`pureva_storyboard.py` ROWS). 시각 = 정리 녹음 단어 시각(`_tmp/pureva/vo/words.txt`).
힉스필드 자리(12·13)는 Codex 시작프레임 정지 화면 + 느린 밀어 들어가기로 임시(발주는 사장님이 고르신 뒤).
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(REPO / "tools"))
import edit_render as ER  # noqa: E402  (자막 A2 · 팝 키프레임 — 10-08 확정값을 그대로 쓴다)
import edit_plan as EP  # noqa: E402
import rule_check  # noqa: E402
import sfx as SFX  # noqa: E402

SRC = Path(r"C:\Users\user\Downloads\drive-download-20261026T014322Z-1-001")
VOICE = ROOT / "납품" / "퓨레바_녹음정리_1026" / "퓨레바_녹음_정리.wav"
CODEX = ROOT / "소재" / "codex" / "pureva"
MODEL = ROOT / "소재" / "pureva" / "상세페이지" / "d2.jpg"      # 브랜드 공식 상세페이지(이현이 · 문구 뺀 자리만 자름)
OUT = ROOT / "납품" / "퓨레바_육아_3차_1026"
TMP = ROOT / "_tmp" / "pureva" / "build"
FONT = REPO / "소재" / "fonts" / "pretendard"
W, H = 1080, 1920
FPS = 60000 / 1001
DUR = 45.871
F = lambda w, s: ImageFont.truetype(str(FONT / f"Pretendard-{w}.otf"), s)

LIME, DARK, GREY = (163, 230, 90), (14, 40, 22), (150, 156, 152)


def clip(n):
    return next(SRC.glob(f"*_{n}_D.MP4"))


# 컷: (시작초, 끝초, 소재, 소재 안 시작초, 옵션) — 줄 시작에서 자르고 다음 줄 시작까지 끈다
CUTS = [
    (0.00, 2.16, "0010", 0.00, {"boxes": [(170, 730, 580, 1010), (450, 890, 900, 1290)], "nostab": True}),   # 10-26 사장님 추가 «맨처음» · 즉석밥 뚜껑·김 포장 상표 흐림
    (2.16, 4.00, "0011", 1.00, {}),                     # 10-26 «싹다 실촬영» — Codex 식판 컷 뺌
    (4.00, 6.80, "0012", 0.00, {}),
    (6.80, 9.66, "0014", 1.75, {}),
    (9.66, 13.58, "0016", 1.40, {}),
    (13.58, 16.54, "0031", 0.25, {}),                    # 0024 는 상자 글자와 이현이 카드가 겹쳐 지저분 → 0031(깔끔한 손+상자)
    (16.54, 18.10, "0017", 9.00, {"logo": True}),        # 0018(옆으로 찍힘) 뺌 — 10-26 «구도 망가짐»
    (18.10, 20.16, "0019", 1.80, {"rot": True}),          # 위에서 찍은 컷을 시계 방향으로 세움(사람 위 · 컵 가운데)
    (20.16, 21.68, "0020", 8.25, {}),
    (21.68, 24.44, "0021", 0.25, {"nostab": False}),   # 바탕(하늘·도시)이 대부분 — 카메라 흔들림만 보정
    (24.44, 26.26, "0026", 4.25, {"rot": True}),
    (26.26, 29.34, "hf12.mp4", 0.30, {}),                    # 힉스필드 Kling 3.0 · 12번 A(항공) 시작프레임
    (29.34, 32.88, "hf13.mp4", 0.20, {}),                    # 힉스필드 Kling 3.0 · 13번 B(플라스크) 시작프레임
    (32.88, 35.60, "0025", 0.90, {}),
    (35.60, 37.34, "0023", 2.00, {}),                    # 10-26 «구도 망가짐»(옆으로 찍힌 0019 확대) → 똑바로 선 진한 초록 병
    (37.34, 38.105, "0028", 4.00, {}),
    (38.105, 38.87, "0022", 8.50, {}),
    (38.87, 39.635, "0020", 10.50, {}),
    (39.635, 40.40, "0030", 1.00, {}),
    (40.40, 42.40, "0030", 1.75, {}),
    (42.40, DUR, "0029", 1.20, {}),                       # 가방에서 상자 꺼내 스틱 뽑음 — 06번(0031)과 같은 소스 두 번 피함(B 1-1)
]
FLASH = [9.66, 26.26]                    # 섹션 바뀜 — 흰 2프레임

# 자막 = 확정 대본 원문(글자 그대로) · 시각 = 단어 시각 − 0.05 · 강조어 하나
SUBS = [
    (0.00, 2.10, "애 키우는 엄마 밥, 다 이렇죠?", "엄마 밥", "key"),
    (2.16, 3.95, "아이 밥은 꼬박꼬박 챙기면서", "꼬박꼬박"),
    (4.00, 6.75, "정작 제 식사는 늘 뒷전이더라고요.", "뒷전"),
    (6.80, 9.60, "따로 뭘 준비해서 먹는 것도 쉽지 않고요.", ""),
    (9.66, 10.95, "그래서 요즘은 먹던 음식에", ""),
    (11.00, 13.55, "퓨레바 클로렐라 한 포를 더하고 있어요.", "퓨레바 클로렐라"),
    (13.58, 14.65, "자기관리의 끝판왕", "끝판왕"),
    (14.70, 16.50, "이현이가 모델인 제품인데요.", "이현이"),
    (16.54, 18.05, "아이 우유나 요거트 챙길 때", ""),
    (18.10, 20.10, "제 것도 같이 준비해서 한 포 넣거나,", "한 포"),
    (20.16, 21.62, "카페라떼에 넣어 먹어요.", "카페라떼"),
    (21.68, 24.40, "한 포에 영양성분이 44가지나 들어 있는데,", "44가지"),
    (24.44, 26.20, "여기 진한 초록색 보이세요?", "진한 초록색"),
    (26.26, 27.40, "일본 야에야마에서", "야에야마"),
    (27.44, 29.30, "햇빛을 받으며 야외배양해서", "야외배양"),
    (29.34, 30.80, "실내배양 클로렐라보다", ""),
    (30.84, 32.85, "엽록소 함량이 1.5배 높고", "1.5배"),
    (32.88, 35.55, "첨가물 없이 클로렐라 100%만 담아서", "100%"),
    (35.60, 37.30, "이렇게 진한 초록색이에요.", "진한 초록색"),
    (37.34, 38.85, "하루 1g, 한 포 뜯어서", "1g"),
    (38.88, 40.35, "어디든 넣으면 관리 끝!", "관리 끝!", "key"),
    (40.40, 42.35, "저처럼 내 밥은 늘 뒷전인 엄마들,", "엄마들"),
    (42.40, 44.20, "퓨레바 클로렐라가 궁금하다면", "퓨레바 클로렐라"),
    (44.24, DUR, "아래 링크에서 확인해보세요.", "아래 링크"),
]
SUB_STYLE = EP.CAPTION_STYLE            # 10-08 설명형 A2: 회색 띠(52,52,56) · Pretendard Bold 66 · 자간 3 · y 1150 · 팝 130→100
NUM_WORDS = ("44가지", "1.5배", "100%", "1g")   # 숫자 = 초록 · 나머지 강조어 = 노랑(10-15·10-20 색 역할)

# 효과음: (계기 시각, 역할) — 들리는 어택을 계기 시각에 맞춘다
SND_FIX = {
    "hook": ("도돈.mp3", 0.4, 0, "attack"),
    "tray": ("7. 뿅.mp3", 0.2, 0, "attack"),
    "tick": ("15. 마우스클릭.mp3", 0.1, 0, "attack"),
    "bubble": ("ML_Cartoon bubbles popping.wav", 0.2, 0, "attack"),
    "block": ("6. SE_블록소리.mp3", 0.2, 0, "attack"),
    "swoosh": ("휙２.mp3", 0.4, 0, "attack"),
    "chime": ("ML_Page forward single chime.wav", 0.3, 0, "attack"),
    "card": ("휙1.mp3", 0.4, 0, "attack"),
    "tag": ("KN_pepSound1.wav", 0.2, 0, "attack"),
    "pep2": ("KN_pepSound2.wav", 0.2, 0, "attack"),
    "n44": ("SEL_キラッ1.mp3", 0.3, 0, "attack"),
    "wind": ("두꺼운 바람.mp3", 0.5, 0, "attack"),
    "bar1": ("띠링.mp3", 0.3, 0, "attack"),
    "bar2": ("SEL_ゲージ回復1.mp3", 0.5, 0, "attack"),
    "x15": ("쿠궁.mp3", 0.5, 0, "attack"),
    "pct": ("2. 띠딩2.mp3", 0.3, 0, "attack"),
    "fast": ("SEL_高速移動.mp3", 0.3, 0, "attack"),
    "end": ("도장.mp3", 0.4, 0, "attack"),
    "btn": ("맑은소리.mp3", 0.3, 0, "attack"),
    "click": ("마우스 클릭.mp3", 0.1, 0, "attack"),
}
# 계기 = 화면 속 동작·그래픽 등장(컷마다 붙이지 않는다). 같은 파일 한 편 2번까지.
CUES = [
    (0.02, "hook"),        # 첫 화면
    (2.20, "tray"),        # 0011 컷 — 급히 떠먹는 숟가락
    (4.30, "tick"),        # 0012 숟가락 뜸
    (6.25, "bubble"),      # 0012 죽 한 숟갈 들어 올림
    (7.30, "block"),       # 0014 냉장고 문 열림
    (9.66, "swoosh"),      # «그래서» 섹션(흰 플래시)
    (12.20, "chime"),      # 0016 스틱 쭉 뽑힘
    (14.70, "card"),       # 이현이 카드
    (14.98, "tag"),        # «모델 이현이»
    (16.60, "bubble"),     # 0017 우유 따름
    (19.10, "pep2"),       # 0019 가루가 요거트에 떨어짐
    (20.60, "tick"),       # 0020 스푼 젓기
    (22.96, "n44"),        # «44가지»
    (24.50, "chime"),      # 0026 쏟아진 진한 초록 가루
    (26.26, "wind"),       # 야에야마 섬(흰 플래시)
    (26.90, "pep2"),       # «일본 · 야에야마» 표지
    (29.45, "bar1"),       # 실내 막대
    (30.90, "bar2"),       # 야외 막대 차오름
    (31.96, "x15"),        # «1.5배»
    (34.30, "pct"),        # «클로렐라 100%»
    (37.34, "fast"), (38.105, "swoosh"), (38.87, "card"), (39.635, "fast"),   # 빠른 4컷
    (40.16, "end"),        # «관리 끝!»
    (42.42, "block"),      # 0031 상자 든 손
    (44.30, "btn"),        # 버튼 등장
    (45.05, "click"),      # 버튼 누름
]


def ease(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


# ───────────────────────── 화면 바탕(컷) ─────────────────────────

STAB = ROOT / "_tmp" / "pureva" / "stab2"      # stab = vidstab 판(10-26 실패, 안 씀)
PAD = 0.5                                 # 보정용 앞뒤 여유(초)


def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])


ZW, ZH = 1148, 2040                      # 보정용으로 6.3% 크게 — 잘라낼 여유 가로 ±34 · 세로 ±60px
STAB_ON = False                           # 10-26 실측: 화면 전체 이동 보정은 손·얼굴 움직임까지 따라가 멀쩡한 컷을 흔듦(0031 0.15→3.06px) — 끔
SIG = 14                                  # 부드러운 길 = 이동 경로의 가우스 평균(14프레임 ≈ 0.23초) — 잔 떨림만 뺀다


def _shift(a, b):
    A, B = np.fft.fft2(a), np.fft.fft2(b)
    R = A * np.conj(B)
    r = np.fft.ifft2(R / (np.abs(R) + 1e-6)).real
    y, x = np.unravel_index(np.argmax(r), r.shape)
    h, w = r.shape
    return (x if x < w / 2 else x - w), (y if y < h / 2 else y - h)


def stab_offsets(path):
    """화면 전체 이동(위상 상관, 1/4 크기) → 누적 경로 → 가우스로 편 길과의 차 = 프레임마다 잘라낼 자리(px, ZW×ZH 기준).
    10-26: vidstab 은 흰 책상 바탕에서 움직임을 잘못 읽어 오히려 튐(76px) → 이동만 보는 단순 보정으로 바꿈."""
    w4, h4 = ZW // 4, ZH // 4
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"scale={w4}:{h4}", "-f", "rawvideo",
                          "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h4, w4).astype(np.float32)
    win = np.hanning(h4)[:, None] * np.hanning(w4)[None, :]
    fr = [(f - f.mean()) * win for f in fr]
    d = np.array([[0.0, 0.0]] + [_shift(fr[i + 1], fr[i]) for i in range(len(fr) - 1)]) * 4
    path_ = np.cumsum(d, axis=0)
    k = np.exp(-0.5 * (np.arange(-3 * SIG, 3 * SIG + 1) / SIG) ** 2)
    k /= k.sum()
    pad = np.pad(path_, ((3 * SIG, 3 * SIG), (0, 0)), mode="edge")
    smooth = np.stack([np.convolve(pad[:, j], k, "valid") for j in range(2)], 1)
    off = path_ - smooth                  # 10-26 부호 실측: smooth - path 는 흔들림을 두 배로 키움(0021 3.87→6.96px)
    off[:, 0] = off[:, 0].clip(-(ZW - W) / 2, (ZW - W) / 2)
    off[:, 1] = off[:, 1].clip(-(ZH - H) / 2, (ZH - H) / 2)
    return off


def prep_cut(src, ss, dur, opt):
    """컷 소재를 59.94 중간 파일로 미리 만든다(10-26 «영상에 잔 떨림»).
    실촬영 = ZW×ZH 로 키워 두고 stab_offsets 로 프레임마다 잘라낼 자리를 잰다(고정 카메라 «nostab» 은 1080×1920 그대로) ·
    힉스필드 24fps = minterpolate 로 59.94 보간(반복 프레임 덜컥 없앰).
    반환: (파일, 그 파일 안 시작초, 프레임별 오프셋 또는 None)."""
    STAB.mkdir(parents=True, exist_ok=True)
    opt = dict(opt, nostab=opt.get("nostab", not STAB_ON))
    big = not opt["nostab"] and not src.endswith(".mp4")
    name = f"{Path(src).stem}_{ss:.2f}_{dur:.2f}{'_r' if opt.get('rot') else ''}_{ZW if big else W}"   # 크기를 이름에 — 다른 크기 캐시를 잘못 읽지 않게
    out = STAB / f"{name}.mp4"
    if src.endswith(".mp4"):                                  # 힉스필드
        if not out.exists():
            run(["ffmpeg", "-v", "error", "-y", "-i", str(CODEX / src), "-vf",
                 f"minterpolate=fps=60000/1001:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,scale={W}:{H}:flags=lanczos",
                 "-c:v", "libx264", "-crf", "10", "-preset", "medium", "-pix_fmt", "yuv420p", str(out)])
        return out, ss, None
    a = max(0.0, ss - PAD)
    size = (W, H) if opt.get("nostab") else (ZW, ZH)
    if not out.exists():
        vf = "transpose=1,crop=ih*9/16:ih," if opt.get("rot") else ""
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-t", f"{dur + 2 * PAD}", "-i", str(clip(src)), "-an", "-vf",
             f"{vf}scale={size[0]}:{size[1]}:flags=lanczos,fps=60000/1001", "-c:v", "libx264", "-crf", "10",
             "-preset", "fast", "-pix_fmt", "yuv420p", str(out)])
    if opt.get("nostab"):
        return out, ss - a, None
    npy = STAB / f"{name}_v2.npy"          # v2 = 부호 고친 뒤
    if not npy.exists():
        np.save(npy, stab_offsets(out))
    return out, ss - a, np.load(npy)


def read_cut(src, ss, n, opt):
    """컷 하나를 n 프레임 RGB 배열로(모자라면 마지막 프레임 반복)."""
    if src.endswith(".png"):
        base = Image.open(CODEX / src).convert("RGB")
        s = max(W / base.width, H / base.height)
        base = base.resize((round(base.width * s), round(base.height * s)), Image.LANCZOS)
        z = opt.get("push", 1.05)
        for i in range(n):
            k = 1 + (z - 1) * ease(i / max(1, n - 1)) * 0.9 + (z - 1) * 0.1 * i / max(1, n - 1)
            bw, bh = round(W * k), round(H * k)
            im = base.resize((round(base.width * k), round(base.height * k)), Image.BILINEAR)
            x0, y0 = (im.width - W) // 2, (im.height - H) // 2
            yield np.asarray(im.crop((x0, y0, x0 + W, y0 + H)))
        return
    path, ss, off = prep_cut(src, ss, n / FPS, opt)     # 59.94 중간 파일(실촬영은 키워 둔 화면 + 프레임별 잘라낼 자리)
    sw, sh = (W, H) if off is None else (ZW, ZH)
    i0 = round(ss * FPS)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"select=gte(n\\,{i0})", "-vsync", "0",
                          "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    last = None
    for k in range(n):
        buf = p.stdout.read(sw * sh * 3)
        if len(buf) == sw * sh * 3:
            last = np.frombuffer(buf, np.uint8).reshape(sh, sw, 3)
        fr = last
        if off is not None:
            j = min(i0 + k, len(off) - 1)
            x0 = int(round((ZW - W) / 2 + off[j, 0]))
            y0 = int(round((ZH - H) / 2 + off[j, 1]))
            fr = np.ascontiguousarray(fr[y0:y0 + H, x0:x0 + W])
        if opt.get("logo"):
            fr = blur_logo(fr)
        if opt.get("boxes"):
            fr = blur_boxes(fr, opt["boxes"])
        yield fr
    p.stdout.close()
    p.wait()


def blur_boxes(fr, boxes):
    """고정 카메라 컷의 상표 자리 — 상자 안을 흐리고 가장자리는 부드럽게."""
    im = Image.fromarray(fr)
    bl = im.filter(ImageFilter.GaussianBlur(28))
    m = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(m)
    for b in boxes:
        d.rounded_rectangle(b, 40, fill=255)
    im.paste(bl, (0, 0), m.filter(ImageFilter.GaussianBlur(12)))
    return np.asarray(im)


def blur_logo(fr):
    """우유팩 빨간 상표 자리 흐림 — 빨강 덩어리 둘레 + 여유."""
    r, g, b = (fr[..., i].astype(int) for i in range(3))
    m = (r > 150) & (g < 90) & (b < 100)
    ys, xs = np.nonzero(m)
    if len(xs) < 150:
        return fr
    x0, x1 = np.percentile(xs, [1, 99]).astype(int)
    y0, y1 = np.percentile(ys, [1, 99]).astype(int)
    x0, y0, x1, y1 = max(0, x0 - 90), max(0, y0 - 90), min(W, x1 + 90), min(H, y1 + 90)
    im = Image.fromarray(fr)
    im.paste(im.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(26)), (x0, y0))
    return np.asarray(im)


# ───────────────────────── 화면 위 층(자막·화면 글) ─────────────────────────

def pill(text, size=54, fg=(255, 255, 255), bg=DARK, pad=(34, 18)):
    f = F("ExtraBold", size)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    b = d0.textbbox((0, 0), text, font=f)
    w, h = b[2] - b[0] + pad[0] * 2, b[3] - b[1] + pad[1] * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 14, fill=bg + (255,))
    d.text((pad[0] - b[0], pad[1] - b[1]), text, font=f, fill=fg)
    return im


def card_model():
    src = Image.open(MODEL).convert("RGB").crop((0, 0, 452, 515))       # 사람 + 상자(오른쪽 문구 뺌)
    w = 600
    src = src.resize((w, round(src.height * w / src.width)), Image.LANCZOS)
    im = Image.new("RGBA", (w + 16, src.height + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], 14, fill=(255, 255, 255, 255))
    mask = Image.new("L", src.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, src.width - 1, src.height - 1], 12, fill=255)
    im.paste(src, (8, 8), mask)
    return im


def n44_box():
    im = Image.new("RGBA", (620, 330), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 619, 329], 14, fill=DARK + (255,))
    d.text((310, 40), "한 포에 영양성분", font=F("Bold", 46), fill="white", anchor="mt")
    f = F("Black", 190)
    tw = d.textlength("44", font=f) + 18 + d.textlength("가지", font=F("Black", 84))
    x = 310 - tw / 2
    d.text((x, 118), "44", font=f, fill=LIME)
    d.text((x + d.textlength("44", font=f) + 18, 210), "가지", font=F("Black", 84), fill="white")
    return im


def bars(t):
    """13번 — 실내(회색) vs 야외(초록) 엽록소 가로 막대 + 오른쪽 «1.5배». 숫자는 상세페이지 표기(100g당 2,180 · 3,260mg,
    야에야마쇼쿠산 분석서). 힉스필드 13번(플라스크가 화면 가운데)이라 판은 위쪽에 납작하게 — 초록 액체를 가리지 않게."""
    im = Image.new("RGBA", (1000, 330), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 999, 329], 14, fill=DARK + (255,))
    d.text((40, 26), "엽록소 함량 (100g당)", font=F("Bold", 32), fill="white")
    for k, (lab, val, col, t0) in enumerate([("실내 배양", 2180, GREY, 29.40), ("야외 배양", 3260, LIME, 30.86)]):
        y = 96 + k * 92
        d.text((40, y + 8), lab, font=F("Bold", 32), fill="white")
        g = ease((t - t0) / 0.55)
        if g <= 0:
            continue
        ww = 400 * val / 3260 * g
        d.rounded_rectangle([210, y, 210 + ww, y + 60], 12, fill=col + (255,))
        if g >= 1:
            d.text((222 + ww, y + 12), f"{val:,}mg", font=F("Bold", 30), fill=col)
    if t >= 31.96:
        g = ease((t - 31.96) / (6 / FPS))
        f = F("Black", round(96 * (0.8 + 0.2 * g)))
        d.text((878, 170), "1.5배", font=f, fill=LIME, anchor="mm")
    d.text((40, 300), "출처: 야에야마쇼쿠산 분석서(상세페이지)", font=F("Medium", 20), fill=(190, 200, 194), anchor="lm")
    return im


CARD = card_model()
TAG_MODEL = pill("모델 이현이", 48)
N44 = n44_box()
TAG_PLACE = pill("일본 · 야에야마", 56)
TAG_100 = pill("클로렐라 100%", 60, fg=DARK, bg=LIME)
TAG_1G = pill("하루 1g", 52)
BTN = pill("자세히 보기  ›", 64, fg=DARK, bg=LIME, pad=(70, 30))
def sub_arr(text, emph):
    segs = [(text, None)]
    k = text.find(emph) if emph else -1
    if k >= 0:
        segs = [(x, c) for x, c in [(text[:k], None), (emph, "g" if emph in NUM_WORDS else "y"), (text[k + len(emph):], None)] if x]
    return Image.fromarray(ER.cap_img(SUB_STYLE, segs, True).clip(0, 255).astype(np.uint8), "RGBA")


SUB_IMG = [(r[0], r[1], sub_arr(r[2], r[3]), len(r) > 4) for r in SUBS]


def put(layer, im, cx, y, t, t0, t1, scale0=0.9, dy=0, fade=0.1):
    """등장: t0 부터 6프레임 감속(크기 scale0→1, 위로 dy) · 퇴장: t1 전 fade 초 흐려짐. 튕김 없음."""
    if not (t0 <= t < t1):
        return
    g = ease((t - t0) / (6 / FPS))
    a = min(g, max(0.0, (t1 - t) / fade) if fade else 1.0)
    s = scale0 + (1 - scale0) * g
    if s != 1:
        im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.BILINEAR)
    if a < 1:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    layer.alpha_composite(im, (int(cx - im.width / 2), int(y + dy * (1 - g) + (1 - s) * im.height / 2 * 0)))


def overlay(t):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    put(L, CARD, W / 2, 230, t, 14.70, 16.54, scale0=0.94, dy=-60)
    put(L, TAG_MODEL, W / 2, 230 + CARD.height + 24, t, 14.98, 16.54, scale0=0.92)
    put(L, N44, W / 2, 250, t, 22.96, 24.44, scale0=0.85)
    put(L, TAG_PLACE, W / 2, 260, t, 26.40, 29.34, scale0=0.92, dy=-30)
    if 29.34 <= t < 32.88:
        put(L, bars(t), W / 2, 110, t, 29.34, 32.88, scale0=0.96)
    put(L, TAG_100, W / 2, 260, t, 34.26, 35.60, scale0=0.88)
    put(L, TAG_1G, W / 2, 260, t, 37.48, 38.87, scale0=0.9)
    if t >= 44.30:
        k = 1.0 + 0.035 * np.sin((t - 44.6) * 2 * np.pi * 1.6) if t > 44.6 else 1.0
        if 45.05 <= t < 45.05 + 4 / FPS:
            k = 0.94
        b = BTN.resize((round(BTN.width * k), round(BTN.height * k)), Image.BILINEAR) if k != 1 else BTN
        put(L, b, W / 2, 1400, t, 44.30, DUR + 1, scale0=0.9, dy=60, fade=0)
    for a, b, im, key in SUB_IMG:          # 자막은 팝(130→100 · 핵심 줄 1→120→100) 뒤 그 자리에 가만히 — 계속 커지는 줌 없음(떨림 원인)
        a0 = max(0.0, a - 0.05)
        if a0 <= t < b + 0.04:
            s = ER.pop_key(t - a0) if key else ER.pop(t - a0)
            sim = im if s == 1.0 else im.resize((round(im.width * s), round(im.height * s)), Image.BILINEAR)
            L.alpha_composite(sim, (round((W - sim.width) / 2), round(SUB_STYLE["y"] - sim.height / 2)))
    return L


# ───────────────────────── 소리 ─────────────────────────

def build_audio(path):
    import soundfile as sf
    v, sr = sf.read(VOICE, dtype="float32")
    total = int(DUR * SFX.SR)
    mix = np.zeros((total, 2), np.float32)
    mix[: min(total, len(v))] += v[:total]
    ref = SFX.voice_ref_from(v)
    SFX.SND.update(SFX.roles_from(SND_FIX))
    items = []
    for t, r in CUES:
        x, _ = SFX.prep(r, ref)
        x = x * 10 ** ((SFX.ad_target(Path(SND_FIX[r][0]).name) - (SFX.rms_frames(x).max() - ref)) / 20)
        st = t - SFX.attack_at(x)
        items.append(dict(t=st, x=x, label=f"{t:.2f} {SND_FIX[r][0]}", file=SND_FIX[r][0], cue=t))
    warns = SFX.fit_tails(items)
    ev = [(d["cue"], d["file"], len(d["x"]) / SFX.SR) for d in items]
    n_err = rule_check.report(rule_check.check_sfx(ev, DUR) + warns, TMP / "rule_check_sfx.txt", "효과음")
    for d in items:
        s = int(round(d["t"] * SFX.SR))
        x = d["x"][: max(0, total - s)]
        mix[s:s + len(x)] += x
    raw = TMP / "mix_raw.wav"
    sf.write(raw, mix, SFX.SR, subtype="FLOAT")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    import json
    import re
    m = json.loads(re.findall(r"\{[^{}]*\}", r.stderr)[-1])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
                    f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
                    f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000",
                    "-c:a", "pcm_s24le", str(path)], check=True)
    return n_err, items


# ───────────────────────── 조립 ─────────────────────────

def frame_plan():
    plan = []
    for a, b, src, ss, opt in CUTS:
        f0, f1 = round(a * FPS), round(b * FPS)
        plan.append((f0, f1 - f0, src, ss, opt))
    return plan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only-audio", action="store_true")
    ap.add_argument("--frames", default="")
    a = ap.parse_args()
    TMP.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    rc = rule_check.report(rule_check.check_copy([r[2] for r in SUBS]), TMP / "rule_check_copy.txt", "화면 글·자막")
    wav = TMP / "mix.wav"
    n_err, _ = build_audio(wav)
    if n_err:
        raise SystemExit("효과음 규칙 ERROR — 멈춤")
    if a.only_audio:
        return
    want = [float(x) for x in a.frames.split(",") if x]
    total_f = round(DUR * FPS)
    video = TMP / "video.mp4"
    enc = None if want else subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "60000/1001",
         "-i", "-", "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", str(video)],
        stdin=subprocess.PIPE)
    fi = 0
    for f0, n, src, ss, opt in frame_plan():
        need = [w for w in want if f0 <= round(w * FPS) < f0 + n]
        if want and not need:
            fi += n
            continue
        for k, fr in enumerate(read_cut(src, ss, n, opt)):
            t = (f0 + k) / FPS
            if want and round(t * FPS) not in {round(w * FPS) for w in need}:
                continue
            im = Image.fromarray(fr).convert("RGBA")
            im.alpha_composite(overlay(t))
            out = im.convert("RGB")
            if any(abs(t - x) < 1.5 / FPS for x in FLASH):
                out = Image.new("RGB", (W, H), "white")
            if want:
                out.save(TMP / f"f_{t:06.2f}.jpg", quality=88)
            else:
                enc.stdin.write(out.tobytes())
        fi += n
    if want:
        return
    enc.stdin.close()
    enc.wait()
    final = OUT / "퓨레바_육아_3차.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-shortest", str(final)], check=True)
    print(final, total_f, "프레임")


if __name__ == "__main__":
    main()
