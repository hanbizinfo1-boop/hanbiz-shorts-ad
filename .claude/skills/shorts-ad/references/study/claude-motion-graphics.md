# claude-motion-graphics — 클로드가 모션그래픽을 정복했습니다 (Jay Choi)

- URL: https://www.youtube.com/watch?v=_kc0riDpxOY · 8분 10초(490.1초) · **1920×1080 / 30fps (AV1)** — 사장님 안내의 «4K 원본»이 아니라 1080p 였다(`ffprobe` 확인, 글자 판독은 1080p 한계) · 올린 곳: YouTube, 채널 Jay Choi
- 사장님이 붙인 목적(원문): «클로드 영상강의 이거 화면까지 따서 하나하나 제대로 정독할것 모션그래픽이 결과물까지 확인 제대로 해서 학습» + «힉스필드(유료) 없이 이 수준 모션그래픽이 되는지»
- 수치(summary.md): 컷 104 · 평균 컷 4.71초 · 강한 타격 102.7/분 · LUFS −10.2 · BPM(추정) 123.1 · 맞춤 비율(봉우리↔타격 18% / 봉우리↔박 21% / 컷↔타격 17% / 컷↔박 17%) — **강의 영상 자체의 편집 수치**일 뿐 학습 대상은 강의 속 «결과 영상 4편»이다
- 근거 자료(`_tmp`, git 제외): `_tmp/study/_kc0riDpxOY/study/` — transcript.md · sheet_000~004 · cut_* · `dense/`(2초 간격 245장, 1920px) · `res/`(결과 영상 0.25초 간격 시트 A~E) · `zoom/`. 다시 만들기: `ffmpeg -v error -i src.mp4 -vf "fps=0.5,scale=1920:-1" study/dense/%04d.jpg` (dense N번째 = (N−1)×2초)

## 1. 한 줄 요약 — 이 영상에서 가져갈 것

**Claude Code(Opus 5.5)에게 «재료 → 연출 → 박 구조 → 구현 규칙 → 함정 → 시작 순서» 6블록 프롬프트를 주면, 외부 툴·유료 영상 도구 없이 «HTML 한 장 + 헤드리스 Chromium 프레임 캡처 + ffmpeg» 만으로 UI 모핑·타이포·데이터·사진 합성 모션그래픽(27초·1440×1440·60fps 모션블러)이 나온다.** 우리에게 쓸모는 영상 속 «결과»보다 **프롬프트 구조(특히 `build`·`gotchas`)와 렌더 방식(시간 함수 seek(t) → 프레임 캡처)** 이고, 그대로는 우리 규칙(3색·인지 텀 0.6초·글리치 1회·휴대폰 도형 금지)과 부딪혀 **수정한 프롬프트**로만 쓴다. 힉스필드가 대신하던 «실사 사람·장소 영상»은 이 방식으로 못 만든다(5-6장).

## 2. 시간순 해부

시각은 원본 `mm:ss`. «시트»는 `study/` 안 파일.

| 시각 | 화면(무엇이 보이나) | 움직임·전환 | 글자(타이포) | 소리 | 시트 |
|---|---|---|---|---|---|
| 00:00–00:12 | 아이보리 둥근 사각 판 위 «Jay Choi.» → «Editing» 필 | 와이드 워드마크가 점으로 접히고 필로 커짐(이 영상 4번 결과의 훅 사용) | 굵은 와이드 산세리프 | 음악 | sheet_000 0:00·0:10 |
| 00:12–00:24 | 오렌지 «M»+3D 고리 글리치 → 검정 바탕 오렌지 «M0…» | 글리치·3D 회전(1번 쇼릴 오프닝) | 굵은 고딕, HUD 잔글씨 | 음악 | sheet_000 0:20 |
| 00:24–00:44 | 격자 노트 위 선 그림 카드: 01 한 문장 → 02 고퀄리티 프롬프트 → 03 최종 버전 계단 | 카드가 계단을 따라 오르며 줌아웃(이 강의 자체 해설 그래픽 — 제작 방법은 화면에 안 나옴) | 세리프 숫자 + 굵은 고딕 라벨 | 말 | sheet_000 0:30 |
| 00:44–01:11 | Claude Code 데스크톱 앱(Mac, 프로젝트 폴더 `motion`) — `/effort` → **Effort (Max)**, 모델 «Opus 5.5 Max», 한 문장 입력 | 프롬프트 타이핑 → «Thinking… → Forging…» | 입력창 영어 | 말 | dense 0029~0035 |
| 01:11–01:28 | **결과 1: 쇼릴 15초** — EASE 곡선 → TYPE «I MAKE THINGS MOVE.» → SHAPE 격자 → SPACE 3D 덩어리 → FLOW 파티클 → DATA 숫자·막대 → 글자 연타 → CLAUDE 엠블럼 | 장면당 0.25~1.5초, 컷 없는 연속 모핑·블러 | 굵은 고딕, 구석 HUD(`01 / EASE`, `128 BPM`, 타임코드) | 음악(코드로 합성) | res/A_01~04 |
| 01:28–01:50 | 앱 내장 비디오 미리보기 `showreel.mp4`(0:15) | 재생 확인 | — | «배경 음악도 알아서» | sheet_000 1:30·1:50 |
| 01:38–01:53 | 필름 스트립 + Remotion · Hyperframes + 스킬 카드 | «이전엔 외부 툴·스킬 설치가 필요했다» | — | 말 | m_05 |
| 01:53–02:31 | 한계 설명(돌릴 때마다 결과 다름 / «보여주기용») + **Anthropic 문서 «프론트엔드 디자인 기본값»**(디자인 방향이 없으면 기본 스타일로 돌아감 · «avoid a generic AI look» 같은 일반 지시는 소용없고 **피할 구체 패턴**을 적어야 함) | 문서 하이라이트 | 한국어 문서 | 말 | dense 0068·0069 |
| 02:31–03:10 | 2번 프롬프트 설명: 01 재료(장면?·색?·음악?) · 02 연출(느낌·화면 전환) · 03 금지목록(바운스·파티클·글로우·템플릿 느낌) · 04 구현 | 블록이 격자 노트에 하나씩 | 세리프 숫자 + 고딕 | 말 | sheet_001 2:40~3:00, dense 0078~0102 |
| 03:10–03:32 | 한 문장 프롬프트 ↔ 긴 프롬프트(스크롤) | 프롬프트 흰 카드가 앱 위에 | 모노스페이스 영어 | 말 | dense 0097·0099 |
| 03:32–04:09 | 모델 **Medium** 으로 전환(시간 때문, 강의자는 Max 권장) → 프롬프트 투입 → Claude 가 **먼저 질문**(UI 상태 12개 제안·색 A/B·음악 A/B) → 사용자 답 3줄 → **박자 그리드 표(28박·14초)** 를 보여 주고 승인 | 코드 쓰기 전 계획 단계 | 한국어 답 | 말 | dense 0113·0116·0120·0123 |
| 04:14–04:29 | **결과 2: `out/one-shape.mp4` 14초, 1440×1440** — Connect 버튼 → 로더 → ✓ → 다이내믹 아일랜드 → 음악 플레이어 → 볼륨 슬라이더 → 토글 → Day/Week 탭 → 차트 → ⌘K 팔레트 → 토스트 → 처음 버튼으로 루프 | 한 도형이 크기·반경·색을 바꾸며 이어짐, 가짜 커서가 클릭·드래그, 카메라가 상태마다 줌 | Geist UI 글꼴 | 클릭·드래그 효과음 + 음악 | res/B_01~03 |
| 04:28–04:46 | 한 문장 결과(01:12) vs 구조 프롬프트 결과 나란히 | 좌우 비교 | — | 말 | dense 0138·0139 |
| 04:46–05:12 | 3번 **Apple 키노트 스타일** 프롬프트(요구 사항 더 많음) → Claude 가 이름(Slowlife)·사진·음악 질문 → 사진·음악은 알아서 | 같은 6블록 구조 | 영어 | 말 | dense 0147~0150 |
| 05:13–05:40 | **결과 3: `slowlife.mp4` 27초, 1440×1440** — 워드마크 → 필 «Your photos, framed.» → 홍채 → 커피 사진 → 3×3 그리드 → 한 컷 확대 → 글라스 «glow» 툴바·슬라이더로 낮→황금빛 → 렌즈 → 잠금화면 폰 → Mac 창 → Safari 탭 → 랜딩 «Slow days, framed.» → 액자·사이즈 선택 → Ordered→Printing→On its way→Delivered → 벽에 걸린 액자 → 워드마크 복귀 | 컷 없이 «앞 장면이 다음 장면으로 변형» | Archivo 와이드 800 + Geist | 음악 | res/C_04~08 |
| 06:00–06:36 | 4번: 같은 구조에 **내 채널 이야기**(이름 «Jay Choi», 내 작업 사진 9~12장·채널 스크린샷·책상 영상 클립) → 입력 4칸 | 구조 유지·재료만 교체 | 한국어 입력 | 말 | dense(06:10 노트), sheet_003 |
| 06:16–06:37 | **결과 4: Jay Choi 브랜드 필름** — 워드마크 → «Indie Hacker Life» → 사진 그리드 → 카페 영상 → 터미널 타자 «build jaychoi.site» → 웹 페이지 → 폰 → YouTube 채널 → Idea→Script→Recording→Editing→Uploaded ✓ → 책상 영상 | 동일 문법 | 한글 정상 표시(도현체) + Archivo | 음악 | res/D_01~04 |
| 06:37–06:54 | `film.html`(32줄) 코드 화면 | `@font-face` 로컬 ttf 5종, 색 3개 변수, `#stage` 1440×1440, `src/film.js` 모듈 | — | 말 | dense 0200 |
| 06:45–07:41 | 정리: «모션 디자인을 대체한다기보다 **도구 문턱이 낮아진 것**» · 판단(장면·박·금지)은 사람이 내림 | 해설 그래픽 | — | 말 | sheet_003 6:50~7:30 |
| 07:41–08:10 | 프롬프트는 X 에 공개된 오픈소스 템플릿 → 설명란 링크 | 쇼케이스 몽타주 | — | 음악 | sheet_003 7:50 |

## 3. 방법 (강의 — 도구 · 프롬프트 원문 · 설정값 · 순서 · 결과 확인)

### 3-1. 도구
- **Claude Code 데스크톱 앱**(Mac, 하단 «Remote Control» 알약 · «Auto» 모드) + 모델 **Opus 5.5**. 추론 강도는 `/effort` 로 조절 — 1번은 **Max**, 2~4번은 시간 때문에 **Medium**(그러나 «가능하면 Max 권장», 03:37). 중간 화면에 «Extra high» 도 보임.
- 외부 툴(Remotion·Hyperframes 등)·스킬 **없음**(01:38~01:49, 쇼릴 DATA 장면의 «LIBRARIES USED 0 / 2428 LINES OF CODE» 는 영상 속 자기 표기 — 사실 검증 안 함).
- 프롬프트 6블록(2~4번)의 `build` 항이 렌더 방법을 지시한다: **HTML 한 장, 스타일은 전부 `seek(t)` 안에서 시간으로 계산(CSS transition·timer·프레임 간 상태 금지) → Playwright 로 프레임 캡처(프레임당 서브프레임 4장) → ffmpeg `tmix` 로 평균해 60fps 모션블러 → numpy 로 음원 박 격자 분석 → 효과음을 측정한 피크에 배치.** 결과 파일은 `out/*.mp4`(앱 안에서 바로 재생).
- 음악: Mixkit 무료 곡(예: «Swish Swed — Arulo», Tech House, Mixkit Stock Music Free License)을 Claude 가 골라 numpy 로 BPM 측정(119.99, 1박 0.500초) 후 박 격자에 맞춤. 사진: Pexels 무료 스톡(2~3번) / 본인 촬영(4번).
- 비용: Claude 구독 한도(강의에 금액 언급 없음). 유료 영상 도구 호출 없음. 소요 시간: 화면에 표시 없음.

### 3-2. 단계 순서
1. **한 문장 프롬프트**(Max) → 즉시 코드 → 15초 쇼릴(결과 1). 한계: 돌릴 때마다 다름, 원하는 영상이 아님, 방향을 안 주면 기본 스타일로 회귀.
2. **6블록 프롬프트 붙여넣기** → Claude 가 코드 쓰기 전에 `<start>` 지시대로 **질문**(상태 목록·색·음악) → 3줄로 답 → 코드 쓰기 전에 **계획표**(박 번호·시간·일어나는 일, 카메라·사운드 방침)를 보여 줌 → «순서를 바꾸거나 빼고 싶은 건 수정» → «이대로 진행» → 렌더 → `out/one-shape.mp4`.
3. **스타일만 바꾼 프롬프트**(Apple 키노트) → 질문 → 4 stills(open·glass·stage·wall) 먼저 보여 준 뒤 전체 필름.
4. **구조는 두고 재료만 교체**(내 이름·사진·영상) → `film.html` 하나 + `src/film.js` + `assets/fonts` + `assets/*`.
- 결과 확인: 앱 내장 비디오 미리보기에서 재생·스크러빙(강의자는 프레임 단위 검수 장면 없음. 프롬프트의 `build 7` 가 «박마다 한 프레임 렌더해 격자 밖·답답함·읽기 어려움을 고친 뒤 풀 렌더» 를 요구).

### 3-3. 프롬프트 원문 (화면에서 옮김)

**① 한 문장** (03:10, dense 0097)
```
make a dynamic 15-second motion graphics video that shows what an incredible motion designer you are, like it's your showreel for a résumé. go all out
```

**② UI 모핑 6블록** (03:20~, dense 0099·0100·0101·0078·0079·0102)
```
<inputs>
Ask me for: 8 to 12 UI states I want the shape to become (e.g. button, loader, player, slider, toggle, tabs, chart, command palette, toast), pure black and white or one accent color, and a royalty-free song around 120 BPM (e.g. Mixkit, free for commercial use).
</inputs>

<direction>
Dribbble-level UI motion. One shape, never cut: every state is the same element morphing its size, radius and color while its content swaps with a short blur. A cursor drives every change with real clicks and drags. Light warm-gray canvas, black and white components, one clean UI font (Geist). Springs everywhere, a tiny overshoot at most. The camera zooms so each state fills the frame. The last frame is the first frame, so it loops.
Banned: bouncy easing, particle bursts, glows, gradients on UI chrome, mismatched icon strokes, dead time, anything that looks like a template.
</direction>

<structure>
120 BPM, 7 bars, something happens on every beat.
Button → loader → check → dynamic island → music player with a play/pause morph → scrub the progress bar → it becomes a volume slider that stretches when dragged past max → a toggle flips on the beat → the knob becomes a liquid tab indicator → the tabs open into a chart that draws itself, with a tooltip on hover → it collapses into ⌘K → type to filter → enter → toast → back to the button.
</structure>

<build>
1. One HTML file, square 1440x1440. Every style is computed from time inside seek(t): no CSS transitions, no timers, no state carried between frames.
2. Springs are closed-form step responses. A value that changes target many times is the sum of one spring per change, so it stays a pure function of time.
3. The tab indicator's two edges ride different springs, so the leading edge stretches ahead of the trailing one. Same trick for the toggle knob.
4. Drags are direct manipulation: while the cursor is held, the value is computed from its position. On release it springs back from wherever it was.
5. Analyze the song with numpy for the beat grid and start on a downbeat. Place every UI sound by its measured peak.
6. Render with Playwright: 4 subframes per frame, blended with ffmpeg tmix for motion blur at 60fps.
7. Render one frame per beat before the full render. Fix anything off the grid, cramped or hard to read.
</build>

<gotchas>
Never put will-change on anything the camera scales or the text renders blurry. Text that swaps inside a morphing container needs its own enter and exit timing or it overlaps. Make the last frame identical to the first, cursor position and speed included, or the loop stutters.
</gotchas>

<start>
Ask me for the inputs, then show me the state list on the beat grid before you write any code.
</start>
```
사용자 답(04:00 전, dense 0116, 한국어): «화면은 예시로 든 것 그대로 써 줘 / 색은 최소한으로 미니멀하게 / 음악은 너가 알아서 아무거나 사용해줘».

**③ Apple 키노트 스타일** (04:46~, dense 0147·0148·0149·0150)
```
<inputs>
Ask me for: a one-word brand name for the wordmark (a verb works best), 9 to 12 high-res photos, a royalty-free song around 120 BPM with a drop and a quiet breakdown (Mixkit, free for commercial use), and a free stock clip of a plain wall with moving plant shadows (Pexels).
</inputs>

<direction>
An Apple-keynote launch film, 2D only, one continuous take. Every scene is made out of the previous one: nothing fades, blurs or cuts. Objects change shape instead: text rises out of a mask line, icons pop from zero on a spring, bars draw across, pages push, and a black shape floods the whole frame and contracts into the next scene. Warm off-white canvas, black UI, iOS 26 liquid glass over the photos. Archivo (wdth 125, weight 800) for the wordmark, Geist for UI. A cursor drives every change with real clicks, drags and long-presses. The camera zooms screen-studio style so each moment fills the square, and the cursor scales with it.
Banned: crossfades, blur-ins, brightness "developing", 3D flips, particles, glows, holds longer than 1s, anything that looks like a template.
</direction>

<structure>
120 BPM, 54 beats, something happens on every beat.
Open: the wordmark squeezes into its own period like an accordion, the dot grows into a black pill, a label rises inside it. Click: six iris blades close over the label and snap open onto a photo. The circle becomes a square, shrinks, the grid unfolds from behind it like a paper map (center, plus, corners), reflows into a bento, and a click zooms into one tile, landing exactly on the drop.
Glass: a glass word pops in letter by letter, melts into a droplet that stretches into a glass toolbar. The adjust icon turns it into a slider. Dragging relights the photo from day to golden hour (two aligned shots), and the knob turns into a glass lens while held. It lifts into a glass orb, the next photo opens inside it as a circle, and the orb expands into a lock screen: glass clock digits, date, and a home bar that stretches into a glass music player.
Stage: the lock screen pulls back into a phone (the bezel grows out of the screen edge). The Dynamic Island stretches like liquid, pinches off, flies over and grows into a Mac window that rolls up like a blind. Long-press the wallpaper, drag it onto a Safari tab, the page pushes in, drop it and it becomes the hero of a landing page. Scroll: the hero morphs into a framed print on a product card, with the mat and molding growing out of the photo's edge. Pick a frame color (it paints across) and a size, then the nav button flies down into "Order print".
Order: one black shape keeps morphing: Ordered ✓ → Printing % → On its way (a van on a route) → Delivered ✓.
Wall: the delivered circle floods the frame edge to edge, holds black for a beat, and contracts into the framed print hanging on the real wall footage. The same iris opens onto the print, closes again, the frame floods the screen and contracts into the pill → the dot → the letters spring back out, landing on the beat return. Last frame = first frame.
</structure>

<build>
1. One HTML file, square 1440x1440. Every style is computed from time inside an async seek(t): no CSS transitions, no timers, no state between frames.
2. Springs are closed-form step responses. A value with many targets is the sum of one spring per change, so it stays a pure function of time.
3. Liquid glass: each glass element holds its own clone of the scene behind it, filtered with an SVG feImage displacement map (a rounded-rect distance field) through three feDisplacementMaps at slightly different scales for chromatic edges, plus a rim light.
4. Iris: 6 blades around a hexagonal aperture. Each blade is its two vertices, both edge extensions and the SHORT arc between them.
5. Wordmark squeeze: every letter moves toward the dot by the same factor and its drawn width follows (narrow the wdth axis, scale the rest), so the letters stay touching.
6. Footage: re-encode all-intra (ffmpeg -g 1), load it as a blob URL, await 'seeked' before drawing each frame.
7. Sound: the song starts on a downbeat: the zoom lands on the drop, the desk clip sits in the breakdown, the wordmark returns with the beat. Add a short UI sound for clicks and typing, each …  (※ 문장 끝은 화면에서 잘림; Apple 판 build 1~3 은 dense 0149 로 같음을 확인 — 4~7항은 Jay 판(dense 0183) 원문이며 Apple 판도 같은 구조로 보임)
</build>

<gotchas>
backdrop-filter: url() misreads displacement maps in Chromium, so clone the scene instead. A flood must overscale past the corners and take about 0.3s, or half the screen changes in one frame. A child with visibility: visible shows through a hidden parent, so use inherit. Text that swaps inside a morphing shape needs its own mask. python http.server can't range-seek video, so use the blob URL.
</gotchas>

<start>
Ask me for the inputs, then show me the beat map and 4 stills (open, glass, stage, wall) before you write the full film.
</start>
```
(※ 위 Apple 판 `structure` 는 dense 0148, `direction`·`inputs` 는 dense 0147, `gotchas`·`start` 는 dense 0150 에서 글자 그대로. build 4~7항은 Jay 판 화면에서 읽은 같은 문장.)

**④ Jay Choi 판**(06:00~, dense 0181·0182·0183 — 글자 그대로, 나머지 블록은 ③ 과 동일)
```
<inputs>
Ask me for: 9 to 12 high-res photos of my work as a YouTuber and indie hacker (desk setup, filming, screen captures, thumbnails), a screenshot of my YouTube channel page, a short clip of me working at my desk, and a royalty-free song around 120 BPM with a drop and a quiet breakdown (Mixkit, free for commercial use). The wordmark is "Jay Choi".
</inputs>

<direction>
A personal channel branding film in the style of an Apple keynote, 2D only, one continuous take. Every scene is made out of the previous one: nothing fades, blurs or cuts. Objects change shape instead: text rises out of a mask line, icons pop from zero on a spring, bars draw across, pages push, and a black shape floods the whole frame and contracts into the next scene. Warm off-white canvas, black UI, iOS 26 liquid glass over the photos. Archivo (wdth 125, weight 800) for the wordmark, Geist for UI and code. A cursor drives every change with real clicks, drags and typing. The camera zooms screen-studio style so each moment fills the square, and the cursor scales with it.
Banned: crossfades, blur-ins, brightness "developing", 3D flips, particles, glows, holds longer than 1s, anything that looks like a template.
</direction>

<structure>
120 BPM, 40 beats, something happens on every beat.
Open: the wordmark squeezes into its own period like an accordion, the dot grows into a black pill, the label "Indie Hacker Life" rises inside it. Click: six iris blades close over the label and snap open onto a photo. The circle becomes a square, shrinks, the grid of my photos unfolds from behind it like a paper map (center, plus, corners), reflows into a bento, and a click zooms into one tile, landing exactly on the drop.
Build: the tile turns into a liquid glass terminal window. One prompt line types itself in. Lines of code pour down, then collapse and morph into a finished app screen.
Stage: the app pulls back into a Mac window, which shrinks into a phone (the bezel grows out of the screen edge). The phone screen becomes my YouTube channel page from the screenshot. The cursor clicks Subscribe: the button morphs into "Subscribed ✓", the bell rings, and a notification drops out of the Dynamic Island.
Upload: one black shape keeps morphing: Idea → Script → Recording % → Editing → Uploaded ✓.
Desk: the uploaded circle floods the frame edge to edge, holds black for a beat, and contracts into the clip of me working at my desk, sitting in the breakdown. The same iris opens onto the clip, closes again, the frame floods the screen and contracts into the pill → the dot → the letters spring back out, landing on the beat return. Last frame = first frame.
</structure>
```
→ 즉 **구조(블록·`build`·`gotchas`·`start`)는 그대로 두고 `inputs` 와 `structure` 의 장면 이름·소재만 바꾼다**(06:00 «프롬프트 구조는 그대로 두고 내용만 제 채널 이야기로»). `film.html` 은 `@font-face` 5종(Archivo·Geist·Geist Mono·Orbitron·Do Hyeon — **한글용 도현체**)과 `:root` 색 변수 3개(paper `#f3f1ec` · ink `#0e0f11`(+ink-2 `#17181a`) · signal red `#ff2a1f`; 주석 «Three colours, each with a job: paper = the brand canvas, ink = every UI shape, signal red = recording / YouTube only.», dense 0200).

### 3-4. 필요 설치물 (강의 환경)
Claude Code(Opus 5.5) · Node(`film.js` 모듈) · Playwright(헤드리스 Chromium) · ffmpeg · Python numpy(박 분석) · 무료 음원(Mixkit) · 스톡 사진·영상(Pexels) · 로컬 글꼴 ttf. 아무 것도 «스킬·MCP» 로 설치하지 않는다.

### 3-5. 결과물 판정표 (프레임으로 본 것 — 0.25초 간격 `res/`)

판정 기준: 우리 **납품 수준**인가(SKILL 4장 상시 규칙 + 영상미 원칙 6장). ○ 쓸 수 있음(손질 후) / △ 기법만 참고 / ✕ 못 씀.

| 시각 | 무엇 | 품질 판정 | 결함(프레임 근거) |
|---|---|---|---|
| 01:12–01:27 | 1번 쇼릴 15초(한 문장 프롬프트) | **△ 기법만 참고.** 질감·모션블러·글자 번짐은 상업 수준이나 **우리 규칙 대부분과 충돌** | ① 장면 길이 0.25~1.5초 — 말·인지 텀 0.6초에 못 맞음(RHYTHM 01:23~01:25 는 장면당 0.3초) ② 색 5가지 이상(주황·파랑·노랑·보라·흰) ③ 글리치 3회+(01:19 FLOW, 01:21 DATA 숫자, 00:12 M) ④ HUD 구석 글씨 약 14px@1080 — 폰에서 안 읽힘 ⑤ 3D 덩어리·파티클 가장자리 판독은 AV1 압축으로 보류 ⑥ «돌릴 때마다 결과가 다름»(강의 자인) |
| 04:14–04:29 | 2번 UI 모핑 14초(Connect→플레이어→슬라이더→토글→탭→차트→⌘K→토스트) | **○ 조건부.** UI 부품이 «실제 설정 화면에서 값을 넣는 느낌»(사장님 08 통과 구도)에 가장 가까움. 1440 정사각 → 세로 재배치 필요 | ① 변형 중간에 **회색 덩어리 판** 3~4프레임(04:19.5, 04:25.5–04:26.0) — 우리 «구멍·반투명» 반려 결과와 닮음 ② ⌘K 팔레트 «Settings» 흐린 줄이 «Share track» 에 겹침(04:25) ③ 숫자 «14h 02m» 글자 떨림(04:24) ④ 가짜 커서(광고에선 불필요) ⑤ 박마다 상태가 바뀜 = 0.5초 간격(인지 텀 0.6초 위반) |
| 05:13–05:40 | 3번 Slowlife 27초(사진·글라스·폰·웹·주문 흐름) | **○ 가장 높음.** 컷 없이 «앞 장면이 다음 장면으로» 이어지는 문법과 사진 합성이 고급. 브랜드·분양 «소개» 장면 후보 | ① 작은 UI 글(≈11px)이 1080p 압축에서 뭉개짐(05:31 이후 제품 카드 «Free returns…») ② 폰 베젤·다이내믹 아일랜드를 **CSS 도형으로 그림** — 우리 «도형으로 휴대폰 흉내 금지»와 충돌, 핀치 변형이 이상한 덩어리(05:27) ③ 사진은 **외부 소재(Pexels)** 가 있어야 함 ④ 검은 판이 화면을 덮고 0.5초 홀드(05:36) |
| 06:16–06:37 | 4번 Jay Choi 브랜드 필름 | **○.** 실사진 + UI + **한글 정상**(도현체 + 와이드 영문). 유튜버·업체 브랜딩 소개 틀로 바로 | ① 검정 판 플러드 후 어두운 빈 프레임 2~3회(06:30–06:34) = 프롬프트가 금지한 «dead time» 위반 ② YouTube 목업 소글씨(≈10px) ③ 홍채·플러드 전환 4회 반복(시그니처 모티프로는 OK, 우리 «같은 전환 연속 금지»(분양)와는 범위 다름) |
| 00:24–00:44 외 | 강의 자체 해설 그래픽(격자 위 선 그림 카드·필름 스트립·계단) | **○ 스타일 참고** — 우리 B 경로(클로드 디자인) 격자·선 카드 톤과 같은 결 | 제작 방법이 화면에 안 나옴 → 이 강의로 배운 방법이 아니다 |

## 4. 기법 카드

- **시간 함수 렌더(seek(t)) + 서브프레임 모션블러**
  - 무엇: 모든 스타일을 `t` 의 순수 함수로 계산하고, 프레임마다 `seek(t)` 를 부른 뒤 캡처. 프레임당 4 서브프레임을 평균해 셔터 블러.
  - 왜 먹히나: 같은 코드가 항상 같은 영상(재현성) + 블러 덕에 «CSS 애니 느낌» 이 빠짐.
  - 시각(근거): 03:20 `build 1·2·6`(dense 0078·0079).
  - **우리 도구로 하는 법**: 신규 `tools/html_motion.py`(5장 설계) · 난이도 중 · 한비즈 적용: 설정·버튼·표 장면, 브랜드 오프닝.
- **한 도형이 모양을 바꾸며 이어 가기(모핑, 컷 없음)**
  - 무엇: Connect 버튼 → 로더 → 체크 → 플레이어 → 슬라이더 …를 한 요소의 크기·반경·색 변경으로. 내용만 짧은 블러로 교체.
  - 왜 먹히나: 장면이 «끊기지 않아» 한 문장 안에 상태 변화를 한 무대에서(우리 원칙 8 «모핑»과 같은 말).
  - 시각: 04:14–04:29.
  - **우리 도구로 하는 법**: 클로드 디자인 B(정지 아트보드) 대신 HTML 직접 · 난이도 중상(모핑 중간 판 처리) · 한비즈 적용: 광고 설정 단계(예산→기간→노출), 문의 폼 단계.
- **«앞 장면이 다음 장면이 되는» 플러드·홍채 전환**
  - 무엇: 검정/아이보리 도형이 화면을 덮고 줄어들며 다음 장면이 됨. 6날 홍채가 닫혔다 열려 사진으로.
  - 시각: 05:16–05:17, 05:36, 06:19–06:20.
  - **우리 도구로 하는 법**: 코드(SVG clip-path) · 난이도 중 · 주의: 홀드 0.3초 이하(어두운 빈 프레임 방지).
- **글라스(liquid glass) 요소**
  - 무엇: 글라스 요소마다 뒤 장면 복제본을 SVG `feDisplacementMap` 3겹(색수차)으로 굴절.
  - 근거: `build 3`(dense 0149) · `gotchas`(`backdrop-filter: url()` 는 Chromium 에서 틀리니 복제).
  - **우리 규칙 충돌**: «유리 효과 남발 금지»(motion-graphics.md 6장 금지목록) → **한 편 한 곳**으로만.
- **프롬프트 6블록: inputs / direction(+Banned) / structure(박 단위 시나리오) / build(구현 규칙) / gotchas / start(먼저 질문·계획 보여 줘)**
  - 왜 먹히나: 판단(장면·박·금지)은 사람이, 구현은 Claude 가. `start` 가 «코드 전에 계획표»를 강제해 사장님식 «물어보지 말고 보여 줘» 대신 **우리는 계획표를 설계자가 검수**하는 단계로 쓴다.
  - **우리 도구로 하는 법**: 우리 프롬프트 뼈대로 5-2장.

## 5. 설계자 관점 변형 — 영상이 «하라는 방식» → 우리 파이프라인에서는 이렇게

### 5-1. 큰 그림
```
[설계자] 단어 시각(words.py)·앞뒤 맥락 → 6블록 프롬프트(5-2) 
 → [Claude Code/실행자] 계획표(박 → 우리는 «단어 시각표»)와 스틸 3~4장 먼저 보고 → [설계자 검수]
 → scene.html (window.seek / DURATION / EVENTS) 작성
 → tools/html_motion.py : 헤드리스 Chrome 프레임 캡처(CDP) → 서브프레임 평균 → ffmpeg
 → 알파 MOV(ProRes 4444) + 확인용 mp4 + 0.25초 프레임 시트
 → 규칙 점검(EVENTS → rule_check) → 효과음(sfx.py) → 납품 3종(lec_xml / edit_xml V2)
```
- 강의와 가장 크게 다른 점: **강의는 «박»(BPM) 에 맞추고, 우리는 «말의 단어 시각»에 건다**(SKILL 3장 2·`motion-graphics.md` 6장 «우리 장면에 맞게 바꾼 점»). 박 격자표 자리에 단어 시각표(초)를 넣는다. 말이 없는 구간(인트로·엔딩)만 박 사용.

### 5-2. 우리 프롬프트로 바꿀 곳 (영어 유지, 강의 뼈대 + 규칙 반영)
- `inputs`: 분양/광고 건은 «Ask me for» 대신 **설계자가 값을 모두 채워 준다**(사장님 «물어보지 말고 만들어서 보여 준다»). 넣을 값: 세로 **1080×1920**, FPS **29.97**, 길이(초), **단어 시각표**, **비워 둘 박스 좌표**(사람·자막 자리 — 세로 값은 SKILL 6장 ☐ 재서 채울 칸), 쓸 글꼴 경로, 사진·로고 파일 경로(Codex 이미지·실제 로고).
- `direction`: «One accent colour + paper + ink» **3색**(비교 장면은 쪽마다 색 하나), «critically damped springs, **no overshoot**»(강의의 «tiny overshoot at most» 를 바운스 금지로 강화), «no glitch except once per film», «Banned: …, text that copies the spoken words».
- `structure`: 박 대신 **«t=1.20s 이 단어에 요소 A 등장; 요소 사이 간격 ≥ 0.6s»**.
- `build`: 강의 1·2·4·6·7항 유지, 크기 1080×1920, `window.FPS=29.97`, **`window.EVENTS=[{t,id,text}]` 를 `seek` 가 기록하게 할 것**(규칙 점검 입력), **`getBoundingClientRect` 로 요소·사람·자막 박스 겹침 검사 결과를 콘솔에 출력**(겹침 검사 = `ae_scene.check_boxes` 대응). 글꼴은 `@font-face url(file:///…)` 로컬 + `await document.fonts.ready`.
- `gotchas`: 강의 문장 그대로 + 한글 글꼴 줄바꿈(`word-break: keep-all`) + 사진 `<img>` 는 `decode()` 완료 후 캡처.
- `start`: «show me the word-time table with elements and 3 stills before you write any code» — 스틸 3장은 설계자가 본다(우리 스토리보드 단계).
- 박 구조를 쓸 때 **BPM 100** 이면 1박 = 0.6초 → «every beat» 가 곧 인지 텀 0.6초가 된다(120BPM 은 0.5초라 위반).

### 5-3. 설치·환경 확인 (설치하지 않고 확인만 — 2026-10-08, 이 PC)
| 항목 | 결과 |
|---|---|
| `node -v` | **v24.20.0** ✓ |
| `npx -v` | **11.19.0** ✓ |
| 크롬 `tools/config.py CHROME` | `C:\Program Files\Google\Chrome\Application\chrome.exe` **존재**, 버전 **154.0.8037.98** ✓ (`design_layers.shoot` 이 이미 `--headless=new --screenshot` 로 사용 중) |
| ffmpeg | 8.1.1 essentials, **`tmix`·`tblend`·`minterpolate` 있음** ✓ |
| Python | 3.11 · **aiohttp OK**(→ CDP WebSocket 직접 가능) · numpy OK · Pillow OK · opencv OK · `playwright`/`websocket(s)`/`selenium` **없음** |
| npm 전역 | `@anthropic-ai/claude-code@2.1.293` · `@openai/codex@0.149.1` 뿐 — **Remotion·Playwright 미설치**(설치하지 않음) |
| GPU | NVIDIA GeForce RTX 3050(WebGL·3D 장면 가능성 — **헤드리스 캡처 속도·WebGL 동작은 검증 안 함**) |
| 글꼴 | `C:\Windows\Fonts\NotoSansKR-VF.ttf` · `NotoSerifKR-VF.ttf`(config.FONTS) · Pretendard-Bold(사용자 폰트 폴더) 있음. 강의의 Archivo·Geist·Do Hyeon(도현체)은 **없음** — 받으려면 OFL 로 받아 `소재/fonts/`(출처 기록, 사장님 확인) |

### 5-4. 렌더 도구 설계 — `tools/html_motion.py` (신규 제안, **아직 만들지 않음**)
- **Playwright·Remotion 설치 없이** 크롬 CDP + aiohttp 로 한다(위 5-3). 강의의 Playwright 단계를 같은 뜻으로 대체:
  1. `chrome --headless=new --remote-debugging-port=<p> --user-data-dir=_tmp/chrome-hm --window-size=1080,1920 --force-device-scale-factor=1 --hide-scrollbars --allow-file-access-from-files` (WebGL 장면은 `--use-angle=d3d11`/GPU 기본).
  2. aiohttp `ws_connect` → `Page.navigate(scene.html)` → `Runtime.evaluate("seek(t)", awaitPromise)` → `Page.captureScreenshot(format=png)`. **알파**: `Emulation.setDefaultBackgroundColorOverride{color:{r:0,g:0,b:0,a:0}}` + `html,body{background:transparent}`(`design_layers` 함정과 같음).
  3. 프레임 n 의 시각 `t = n·1001/30000`(29.97). 서브프레임 4장은 `t + (k/4)·(0.5/fps)` 처럼 **셔터 180°** 구간에서 → numpy 로 **premultiplied 알파 평균**(ffmpeg `tmix` 는 알파가 있으면 가장자리 번짐 우려 — 알파 장면은 numpy, 불투명 장면은 `tmix=frames=4`).
  4. 인코딩: 알파 `ffmpeg -framerate 30000/1001 -i f_%05d.png -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le out.mov`, 확인용 `libx264 -pix_fmt yuv420p -crf 14`. 불투명 풀화면은 mp4 만.
  5. 병렬 Chrome 2~3개로 프레임 나눔. **예상 시간은 측정 전**(15초=450프레임×4=1800캡처) — 먼저 10프레임으로 장당 시간을 잰 뒤 정한다.
  6. 부산물: 0.25초 간격 시트(`ffmpeg … fps=4,tile`) 자동 생성 → 설계자가 «단어 시각마다 프레임을 눈으로» 점검(SKILL 3장 8).
- 장면 HTML 계약(`tools/scenes_html/<장면>/scene.html` 제안 위치): `window.W/H/FPS/DURATION`, `async window.seek(t)`, `window.EVENTS`, `window.BOXES`(겹침 검사용), `Math.random`·`Date.now`·CSS transition/animation·타이머 **금지**(시드 고정).
- 비디오 클립을 장면에 넣을 때는 **강의 `build 5` 처럼 all-intra 재인코딩(`ffmpeg -g 1`) + blob URL + `await 'seeked'`**, 더 간단히는 **ffmpeg 로 JPEG 시퀀스를 미리 뽑아 `<img>` 교체**(권장 — 헤드리스 비디오 seek 불안정 회피).

### 5-5. 우리 파이프라인에 붙이는 자리
- **글·숫자·UI·표·차트·단계 도식 장면** = 지금 B 경로(`클로드 디자인 → design_layers → AE`)의 **대안 한 칸**. 움직임까지 HTML 안에서 끝나므로 AE 불요. 정지 레이어가 필요하면 기존 B 경로 그대로.
- **납품**: 알파 mov → `lec_xml`(«얹을 것만» 프리미어 XML, V 트랙) 또는 `edit_xml` V2. 단 **`edit_plan` 스키마의 컷은 V1(video|image)만**(edit_plan.py 253~254행 kind 검증) — HTML 알파 오버레이 층은 아직 없다. **설계자 결정 필요**: ① `edit_plan` 에 `overlays[]` 추가 ② 당분간 `lec_xml` 로 별도 납품.
- **규칙 점검**: `EVENTS` → `rule_check.check_plan` 입력(요소별 등장 시각·글 길이·색 수)으로 변환하는 어댑터 필요(미작성). 새 렌더 도구는 `rule_check` 를 반드시 끼운다(CLAUDE.md 10장).
- **효과음**: 강의의 «측정 피크에 소리»는 우리 `sfx.py`/`rule_check.check_sfx` 로 — `EVENTS` 의 등장 프레임에 붙임(게이지·타자에는 차오르는/타자 소리).
- **플랫폼**: Remotion 은 설치·라이선스(회사 규모별 유료 조항 있음 — **확인 안 함**)가 걸려 채택하지 않는다. 필요해지면 설치 전에 사장님께 묻는다.

### 5-6. 힉스필드(유료) 없이 가능한 범위 / 불가능한 범위

**가능 (영상 속 근거가 있는 것)**
- 글자·키네틱 타이포(01:13 «I MAKE THINGS MOVE.», 05:13 워드마크 squeeze), 숫자 카운트·막대·도넛(01:21 DATA), UI 부품 상태 변화(04:14–04:29), 도형 격자·패턴·모핑(01:15), 파티클·3D 추상·글로우(01:17–01:21 — 우리 규칙상 쓸지는 별개), 사진+글라스 합성·사진 그리드·확대(05:16–05:25), 장면 전환(홍채·플러드), 한글 브랜드 카드(06:17, 도현체).
- 사진·영상 **소재가 이미 있는** 합성(05:36 벽 영상 위 액자, 06:32 책상 영상) — 코드는 «얹기·마스크·전환»만.
- **우리가 가설로 추가(강의엔 없음)**: 알파 오버레이로 말하는 사람 위에 얹기 · Codex 이미지(무료)를 `<img>` 로 쓰는 카드·마스코트 모핑.

**불가능 / 부적합 (근거)**
- **새 사람·장소·제품·분위기 영상 생성** — 강의의 모든 «실사»는 본인 촬영·Pexels 스톡·사진 파일이었다(06:21 «사진은 제가 작업하는 모습», 05:12 «사진·음악은 알아서» = 스톡). 코드가 영상 속 사실적 사람·공간을 만든 장면은 **없다**. 분양 T3(AI 영상 중심)의 «현실 공간·사람» 시작프레임→영상화는 여전히 Kling/힉스필드 영역(CLAUDE.md 3장 «Codex 로 대체할 수 없는 것»).
- 포토리얼 카메라 무빙·인체 동작·물/연기 시뮬레이션 — 이 방식의 3D 는 추상 덩어리(01:17)까지만 확인.
- 실존 얼굴·실제 건물 닮게 그리기 — 코드로 시도할 이유 없음.
- **중간 영역(가능성 있지만 이 강의에선 증명 안 됨)**: Codex 이미지 한 장 + 코드 패럴랙스·켄번스·마스크 분리로 «정지 사진을 살아 있게» — 유료 영상화 한 건을 줄일 수 있는지는 **시험 필요**.

## 6. 우리 규칙과 부딪히는 것 (SKILL 4장 · checklist) — 그대로 쓰면 반려될 것

| 강의가 하는 것 | 우리 규칙 | 고치는 법 |
|---|---|---|
| 박마다 새 요소(120BPM = 0.5초) | **인지 텀 0.6초**(4장·원칙 13) | BPM 100 또는 2박마다. 단어 시각에 건다 |
| 쇼릴 5색+·사진 합성 | **3색**(바탕·글·강조 하나, 비교는 쪽마다 한 색) | `direction` 에 3색 고정 |
| «tiny overshoot at most» 스프링 | **바운스 금지**(원칙 3) | critically damped, 오버슈트 0 |
| 글리치·흔들기 여러 번 | **한 편 한 번**(원칙 11) | 프롬프트에서 삭제, 센 단어에 1회만 |
| 폰 베젤·다이내믹 아일랜드를 CSS 도형으로 그림(Slowlife 05:25) | **도형으로 휴대폰·사물 흉내 금지**(4장 도형 짜깁기, 06 반려) | 폰·액자·인물은 Codex 이미지·실제 사진 `<img>`. 버튼·슬라이더·토글·탭·차트 같은 **UI 그 자체**는 «녹화 화면 재현»(04·08·19 통과 이력)이라 CSS 로 그려도 됨 |
| 화면 글이 시나리오(Ordered·Printing…) | **말 따라 쓰기 금지**, 읽히는 예시 글 | 말을 받치는 개념어로. 업체명 ○○, 번호 010-0000-0000 |
| 가짜 커서가 클릭·드래그 | 사장님 통과(04 확대+타자)와 같은 결, 단 휴대폰 광고 맥락 | 설정 장면에서만. 커서 크기도 줌에 따라 |
| HUD 구석 글씨(원칙 10) | 쇼츠 폰 시청 — 최소 크기 ☐ 재서 채울 칸 | 세로 최소 글자 크기를 재기 전에는 HUD 미사용 |
| 정지 홀드 ≤1초(Banned: holds longer than 1s) | 원칙 7 «그림이면 멈춰 두고» | 삭제 — 보여 줄 그림은 멈춰 둔다 |
| 검은 판 플러드 후 빈 프레임 | 규칙에 직접은 없으나 «dead time» 금지 | 홀드 0.3초 이하 |
| 박 격자 중심 | **단어 시각 중심**(SKILL 3장 2) | 5-1 |
| 정사각 1440, 60fps | 세로 1080×1920 · 29.97 | `W/H/FPS` |
| 음악이 코드·스톡 | 효과음은 `sfx.md` 규칙·등급표, 음원 사용 범위는 작업기록 «사용 허락 범위» | 영상에 음악 안 구움(알파 mov 는 무음) |

## 7. 못 본 것 · 불확실

- **1번 쇼릴(한 문장)의 렌더 방식**: 한 문장 프롬프트가 Playwright 였는지·WebGL/canvas 였는지는 코드가 화면에 안 나와 **모름**. «LIBRARIES USED 0» 은 영상 속 표기일 뿐.
- **Apple 판 `build` 4~7항**: Apple 판 화면은 3항에서 끊겨 있고(dense 0149), 4~7항은 Jay 판(dense 0183)에서 읽은 문장 — Apple 판과 동일한지는 **추정**. 7항 끝(«Add a short UI sound for clicks and typing, each …»)은 화면에서 잘려 **끝 문장 미확보**. 설명란 X 템플릿 링크로 원문 필요 — 우리는 링크를 받지 못함(받은 폴더는 읽기만).
- **소요 시간·토큰·구독 요금**: 화면에 없음(앱 하단 «60m/59m» 표시는 의미 확인 못 함).
- **렌더 속도·WebGL 헤드리스 동작·알파 premultiplied 합성 결과**: 이 PC 에서 아직 실행해 보지 않음(검증 안 함). `html_motion.py` 도 아직 없다.
- **영상 판정 정밀도**: 원본이 1080p AV1 이고 결과 영상이 그 안 녹화본(재압축)이라 가는 선·작은 글의 «깨짐» 판독에 한계. 결함 시각은 ±0.5초.
- **Remotion 라이선스 조건**: 확인하지 않음.
- 강의 해설 그래픽(00:24~)이 무엇으로 만들어졌는지(AE? 코드?) — 안 나옴.
- 결과 4번 이후 구간(06:37~06:54 `film.html`)·엔딩 달리는 사람 영상(07:50 이후)은 학습 대상 아님.
