# 한비즈 쇼츠 광고

한비즈 **쇼츠 광고(세로 1080×1920) 전용** 작업 폴더. Claude Code 세션이 열자마자 일할 수 있게 스킬·도구·규칙을 담았다.
**10-29 사장님 결정으로 공개 저장소다(직원 공유 — 노하우 100% 공개).** 처음이면 **`직원용/README.md`** 부터. 영상·음원·프로젝트·이미지 바이너리는 커밋하지 않는다(`.gitignore`).

## 폴더

```
한비즈-쇼츠광고/
├─ CLAUDE.md                 # 이 세션 규칙(하드 규칙) + 시작할 때 읽는 순서
├─ README.md                 # 이 파일
├─ .gitignore
├─ .claude/
│  ├─ settings.json          # SessionStart(compact·resume) 훅 → python tools/resume_guide.py
│  └─ skills/shorts-ad/
│     ├─ SKILL.md            # 핵심 스킬: 작업 순서 · 사장님 상시 규칙 · 가로→세로 · 점검표
│     └─ references/
│        ├─ motion-graphics.md   # AE JSX 파이프라인 · 영상미 원칙 1~13 · 통과/반려 이력 · 함정
│        ├─ design-paths.md      # 그림 길 A(Codex) · B(클로드 디자인) · 2D 플랫 애니 · 실제 로고 · 녹화 화면 재현
│        ├─ ai-video.md          # Codex 시작프레임 → Kling/힉스필드 · 비용 규칙 · 사진풍 · 영상화 직전 점검
│        ├─ blender.md           # 블렌더 프리비즈·시네 도구
│        ├─ sfx.md               # 효과음 문법·고르기·크기·반복/빈 구간·믹스
│        ├─ editing-premiere.md  # prproj 읽기 · 컷 조각 · 납품 XML · 쇼츠 편집 문법·자막
│        ├─ feedback-log.md      # 사장님 피드백 원문
│        └─ checklist.md         # 납품 전 점검표 A·B·C + 점검기
├─ tools/                    # 재사용 도구. 경로는 전부 config.py 한 곳
│  ├─ config.py · ae_scene.py · rf3_ae.py · sfx.py · rule_check.py · lec_xml.py
│  ├─ design_layers.py · read_prproj.py · prproj_timeline.py · words.py · resume_guide.py
│  ├─ edit_plan.py · edit_render.py · edit_xml.py · edit_smoke.py   # 한 편 조립기(배치표 JSON → 미리보기 mp4 / 프리미어 XML)
│  ├─ html_motion.py · ref_study.py   # HTML seek(t) 장면 → 알파 MOV(렌더 전 겹침·3색·인지 텀 점검) · 레퍼런스 영상 해부(tools/scenes/html/ 에 장면)
│  ├─ data/                  # 예능효과음-등급.json · 예능효과음-실사용.json
│  └─ examples/              # 통과/최신 장면 도구 «본보기»(원본 경로 상수 그대로, 실행 보장 없음)
├─ 기록/작업기록.md          # 장면마다 구간 · 앞뒤 맥락 · 단어 시각 · 연출 · 피드백
├─ 소재/                     # 이 건 소재(이미지·로고) + 소재/이미지-출처.md
├─ 납품/                     # 사장님께 드리는 것(같은 이름 제자리 덮어쓰기)
└─ _tmp/                     # 임시(중간 렌더·내려받은 원본). git 제외
```

원본(읽기 전용 참조): `D:\영상제작`(길라잡이 문서·도구·빡이사DB 기록) · `D:\★에이전트`(ad-video·ae-template 스킬). 이 폴더에서 원본을 수정하지 않는다.

## 새 PC 세팅

1. **Python 3.11** + 패키지: `pip install numpy pillow faster-whisper` (단어 시각용 faster-whisper 는 이 PC 에서 `device="cpu", compute_type="int8", medium` 으로 돌렸다 — GPU 에 cublas 가 없었다).
2. **ffmpeg / ffprobe** 를 PATH 에(이 PC: 8.1.1 essentials). 효과음 다듬기·미리보기·XML 길이 계산에 쓴다.
3. **After Effects 2026(한국어판)** — 기본 경로 `C:\Program Files\Adobe\Adobe After Effects 2026\Support Files\` (`AfterFX.exe`, `aerender.exe`). 출력 모듈 템플릿 이름이 «고품질». 앞 실행이 비정상 종료되면 «충돌 복구 옵션» 창이 스크립트를 막는다 → `ae_scene.run_ae_guarded` 가 지켜본다.
4. **Google Chrome** — 클로드 디자인 아트보드를 레이어 PNG 로 뜰 때(`design_layers.py`).
5. **글꼴** — `소재/fonts/` 에 받아 둔 사본(Pretendard 전체·SUIT·Black Han Sans·도현체·Paperlogy·Gmarket Sans·Archivo·JetBrains Mono, OFL, 윈도 설치 없음; 출처 `소재/fonts/출처.md`, 글꼴 파일은 커밋 제외라 새 PC 에서는 출처 표의 URL 에서 다시 받는다) · Noto Sans KR VF · Noto Serif KR VF(`C:\Windows\Fonts\`) · 손글씨 개구 굵게(Gaegu Bold, OFL; `_tmp/fonts/Gaegu-Bold.ttf`, 없으면 장면 도구가 받는다). 경로는 `tools/config.py` `FONTS`.
6. **효과음 라이브러리** — 10-08 부터 **이 폴더 `소재/효과음/` 사본**을 쓴다(음원은 git 제외 — 새 PC 에는 이 폴더째 복사해 온다). `sfx.find_file` 이 파일 이름으로 아래 세 폴더를 먼저 찾고(등급표 798건 전부 사본에서 찾힘 확인), 등급표의 원본 절대경로는 마지막 대안이다.
   - `SFX_LIB` = `소재/효과음/받은라이브러리` — Mixkit `ML_` · Kenney `KN_` · 効果音ラボ `SEL_`(원본 `D:\영상제작\소재\예능효과음`).
   - `SFX_LIB_OWNER` = `소재/효과음/사장님라이브러리` — 앞말 없는 `휙２.mp3` · `두꺼운 바람.mp3` · `맑은소리.mp3` …(원본 `C:\Users\user\Desktop\작업공간\효과음`). **`모음1~6`(게임·방송 음원)은 복사하지 않았고 도구도 막는다.** 한글 파일명이 NFD 일 수 있어 NFC 로 정규화해 찾는다.
   - `SFX_LIB_SCENE` = `소재/효과음/장면음`(원본 분양 폴더 `16_장면음`).
   - 재배포 금지 라이선스 소재(効果音ラボ 등)는 저장소에 올리지 않는다.
7. **Codex CLI** — 이미지는 Codex 내장 `image_gen` 으로(추가 과금 없음). 호출 스크립트 `C:\Users\user\.claude\scripts\codex-run.ps1` 은 이 폴더 밖(사용자 홈)에 있다. 인증이 풀리면(401) 터미널에서 `codex login`.
8. **유료 생성 MCP** — Kling · 힉스필드(claude.ai 커넥터). 호출마다 과금. Kling 은 세션에서 `who_am_i` 를 먼저 부른다.
9. **Premiere Pro** — 사장님 편집본(`.prproj`)은 gzip XML 이라 `read_prproj.py` 로 읽는다(Premiere 설치 불필요). 열려 있는 프로젝트는 사본을 떠서 읽는다. 자동저장본이 가장 최신.
10. **블렌더(선택)** — 원본 기록은 힉스필드 클라우드 블렌더(3D Jutsu)였다. 로컬 블렌더는 확인 안 함.

### 경로를 바꾸려면

`tools/config.py` 를 고치거나 환경변수로 덮어쓴다:

| 환경변수 | 뜻 |
|---|---|
| `HANBIZ_AE_DIR` | After Effects `Support Files` 폴더 |
| `HANBIZ_SFX_LIB` | 받은 효과음 라이브러리 |
| `HANBIZ_SFX_LIB_OWNER` | 사장님 개인 효과음 라이브러리 |
| `HANBIZ_FONT_PRETENDARD` | Pretendard-Bold.otf |
| `HANBIZ_CHROME` | chrome.exe |

### 설치 확인

```powershell
cd tools
python -c "import config, rf3_ae, rule_check, lec_xml, design_layers, read_prproj, prproj_timeline, sfx, ae_scene, words, resume_guide, edit_plan, edit_render, edit_xml, html_motion, ref_study; print('ok')"
```
`examples/` 는 본보기라 import 확인 대상이 아니다.

## 쓰는 법 한눈에

- 세션을 열면 `CLAUDE.md` → `.claude/skills/shorts-ad/SKILL.md` 순으로 읽는다(자동 압축·재개 때는 훅이 상시 규칙을 다시 넣는다).
- 장면 하나: 앞뒤 맥락 → 단어 시각(`tools/words.py`) → 구도 → 그림(`design-paths.md`) → 조각·겹침 검사·애펙(`tools/ae_scene.py`) → 효과음(`sfx.md`) → 점검(`checklist.md`) → 납품 3종 → 폴더 열기.
- 새 장면 도구는 `tools/scenes/` 에 `examples/` 의 가장 가까운 본보기를 복사해 시작한다(원본 경로 상수를 `config` 로 바꾼다).
- 첫 작업에서 세로 쇼츠의 확정 수치(사람 자리·자막 자리·fps·효과음 크기)를 재서 `SKILL.md` 6장 «재서 채울 칸»을 채운다.

## 커밋

자동으로 하지 않는다. 사용자가 요청할 때만 커밋·푸시한다. 저장소는 공개(10-29).
