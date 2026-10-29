# 2d-mg-newtake — 이런 2D 모션그래픽, 이제 AI로 직접 만드세요 (feat. Newtake)

- URL https://www.youtube.com/watch?v=9uQVYIaYIeg · 15분 10초(909.8초) · 1920×1080 · 30fps(av1) · 올린 곳 «디자인하는AI»(한국어 AI 디자인 채널) · 2026-09-25 업로드 · 조회 약 8.3만 · 해시태그에 `#MadeWithNewtake` — **Newtake 협찬/제휴형 강의**로 읽힘(설명란에 제휴 링크 있음, 여기엔 옮기지 않음)
- 사장님이 붙인 목적(원문): «위는 강의영상 참고에서 여기서 우리에게 하라는 방식을 설계자의 입장으로 네가 설계내린다는 가정으로 변형 학습정리할것» · «대충하지말고 확실하게 하나하나 정독하면서 제대로 학습»
- 수치(summary.md): 컷 114 · 평균 컷 7.98초(설명 카드가 길어서 의미 작음) · 강한 타격 139.5/분(나레이션 음절 포함이라 의미 없음) · LUFS −23.7 · 트루피크 −7.5dBFS · BPM 117.5 · 맞춤 비율 봉우리-타격 28% / 컷-박 22% → **소리와 화면을 맞춘 영상이 아니라 나레이션 + 약한 BGM**
- 해부 폴더: `_tmp/study/9uQVYIaYIeg/study/`(다시 만들기: `yt-dlp` 로 받아 `python tools/ref_study.py _tmp/study/9uQVYIaYIeg`). 원본 해상도 추출본 `study/extra/`(프롬프트 화면 `137~245.jpg`, 설정 화면 `272~341.jpg`, 결과 0.25초 시트 `q_A~q_H.jpg`).
- **소리는 귀로 못 들었다.** «소리» 칸은 자막의 [음악] 표기와 수치만 적는다.
- 영상 챕터(설명란 원문): 00:00 인트로 · 00:54 Kinetic Typography란? · 01:35 프롬프트 설계법 · 02:07 방법① 가이드로 프롬프트 만들기 · 04:15 Newtake 에서 생성 · 05:42 결과 확인·스타일 바꾸기 · 06:16 방법② 레퍼런스 영상으로 프롬프트 · 08:39 스마트 분석 · 10:17 Character Animation · 12:29 Product promotion · 13:14 스토리보드 · 14:07 제품 이미지 한 장으로 스토리 있는 영상

## 1. 한 줄 요약 — 이 영상에서 가져갈 것

1. **이 강의는 «모션그래픽을 영상 생성 모델(MiniMax H3)에 통째로 맡기는» 방법이다.** 사람의 일은 프롬프트를 «촬영 지시서»처럼 쓰는 것(길이 · 샷별 타임코드 · 정확한 문구 · 카메라/모션 규칙 · 사운드 · 금지 목록). 도구 Newtake 는 영상·이미지·텍스트 생성 모델을 한 캔버스에 노드로 잇는 플랫폼이고, 쓸 때마다 **크레딧**이 든다(10초 영상 140~220, 4K 이미지 1장 124).
2. **프레임으로 본 품질: 구조·리듬은 지시서대로 잘 나오지만 «글자»가 새고 «캐릭터·제품»이 녹는다.** 지시한 `“AI, 그냥 쓰고 있나요?”` 가 화면엔 `나요,`(물음표 → 쉼표)로, 제품 영상엔 `에터민B MIX`·`Corxplex` 같은 없는 글자가 나온다(3-5장 표). 그래서 **우리 모션그래픽 컷(글자·UI·타이포)은 이 방식으로 만들지 않는다** — 글자는 렌더러가 폰트로 그린다(`design-paths.md` 핵심 2).
3. **그런데 가져올 것이 네 가지 있다 — 영상 모델과 무관하게 무료로 쓸 수 있는 것들이다.** ① 지시서 **형식**(샷 표 + 정확한 문구 목록 + 모션 문법 + 금지 목록) → 우리 «장면 스펙»(5-4) ② **레퍼런스 영상 → 샷·모션 표 → 스펙** 변환 순서(우리는 `ref_study.py` 가 이미 있음) ③ **스토리보드 그리드 한 장**으로 구성 먼저 확인 → 확인②에 맞음, Codex 이미지로 무료(5-2) ④ **스타일 변주 = 스펙의 한두 단락 교체**(강의: 네오브루탈리즘) → 스틸 3안 시안에 맞음.
4. **영상 모델은 «현실 공간·사람»(T3)에만** — 기존 규칙(장면당 유료 1건) 그대로. 이 강의 때문에 모션그래픽 컷에 유료 영상화를 쓰게 되는 일은 없다.

## 2. 시간순 해부

| 시각 | 화면(무엇이 보이나) | 움직임·전환 | 글자(타이포) | 소리 | 시트 |
|---|---|---|---|---|---|
| 00:00–00:14 | 샘플 몽타주: 달리는 플랫 캐릭터 카드(베이지 바탕) → 시네마틱 실사 썸네일 3장 위에 흰 카드 «2D 모션그래픽 · 타이포그래피 / 상대적으로 어려웠던 영역»(AI 영상 모델의 약점 설명) | 카드 페이드 + 썸네일 흐림 | 하단 자막(흰 외곽선 굵은 한글) · 영어 보조 자막 | 나레이션 + [음악] | sheet_000 |
| 00:14–00:50 | 결과 샘플 2종(캐릭터 달리기 / 단백질 제품 정지샷) → 3유형 라벨 «02 캐릭터 애니메이션»(오픈런 일러스트 군중) → 노드 캔버스 화면(프롬프트 노드·캐릭터 카드) → «레퍼런스 + AI» 도식 | 일러스트가 달림(좌→우), 카드 3개 나란히 | «이제, 디자인이 중요한 모션그래픽도.»(검정 + 연두 강조) | 나레이션 | sheet_000 |
| 00:55–01:35 | 키네틱 타이포 정의: 큰 글자 `don't enjoy`(흐림→선명) → `I'M` 글자에서 곡선 선이 그려져 나감 → 항공 영상 한 컷(일관성 유지 요소가 없는 예) → «짧은 영상, 10초» 스톱워치 카드 | 흐림 해제, 선 draw-on | 영문 큰 글자 + 하단 자막 | 나레이션 | sheet_000 |
| 01:35–02:07 | 설명 카드 3연속: 제작 지시서 UI(번호 01~04 줄 + 커서 타자) → 카메라 든 사람 일러스트 + 파란 선택 박스 → «머릿속에는 있지만…» 일러스트 | 카드 슬라이드 인, 커서 이동 | «어떤 문구를 보여줄지» · «장면의 구도까지 구체적으로» · «아이디어를 구성과 용어로 옮기는 일» | 나레이션 | sheet_000~001 |
| 02:07–02:37 | «01 준비된 가이드 → 프롬프트 입력 → 복사 완료» 카드 → ChatGPT 데스크톱 화면: 가이드 프롬프트 붙임 → «이 가이드에 따라 …» 요청 → «4m 8s 동안 처리함 / 웹사이트 10개 검색함» → 결과 문서 | 화면 녹화(맥) + 마우스 | UI 글자 | 나레이션 | sheet_001 |
| 02:37–04:12 | **프롬프트 결과 해설**: 영문 원문 카드(좌) + 한글 번역 카드(좌) + 우측 라벨(길이·분위기·목적 / 비주얼 스타일 / 01~05 샷 / 움직임의 공통 규칙 / 소리까지 설계 / 마지막으로 생성 제어), 하단 5분할 진행 바 | 원문 스크롤, 해당 문장 형광 하이라이트 | 영문 원문 + 한글 번역(3장에 옮김) | 나레이션 | sheet_001~002 |
| 04:15–05:42 | Newtake 로고 → 빈 캔버스 → 텍스트 노드(프롬프트 붙임) → 비디오 노드 추가 → 모델 목록 → 비율/해상도/길이/개수 패널 → «생성 중 1%…» | 화면 녹화, 마우스 클릭 | UI 글자 | 나레이션 + [음악] | sheet_002 |
| 05:42–05:55 | **결과 1 — 키네틱 타이포 10초**: 검정 바탕 커서 타자 → 원형 와이프 → 아이보리 바탕 «아이디어 / 이미지 / 브랜딩 / UI / 영상» 블록 연결 → 정사각형 → 검정 캔버스 «툴보다 중요한 건 / 만드는 흐름.» → 5단어 몽타주 → «디자인하는AI» 엔드 카드 | 샷 5개가 지시서 타임코드대로 | 한글 굵은 산세리프 + 영문 대문자(3-5장) | 생성 영상 소리는 못 들음 | sheet_002~003 · 프레임 `q_A.jpg` |
| 05:55–06:16 | **결과 2 — 같은 구성, 네오브루탈리즘**: 아이보리 종이 질감 위 `DESIGN` 큰 글자(프레임 밖으로 잘림) → FORM · TYPE · MOTION · SPACE · EXPLORE · CREATE · VIBE · MAKE · SHIFT → 검은 종이 접힘 3D → 흑백 «AI DESIGN» → «디자인하는AI» | 하프톤·번짐·잔상 + 글자 쌓임 | 영문 대문자 위주, 한글은 마지막 한 줄 | — | sheet_003 · 프레임 `q_B.jpg` |
| 06:16–06:56 | «02 레퍼런스 영상 프롬프트 만들기» 도식: 레퍼런스 → AI 분석(샷 구성·곡선 이동·오른쪽 전환) → 영상 생성 프롬프트(점선 → 카드) | 도식 카드가 흐려지며 교체 | «분석한 내용을, 영상 생성 프롬프트로» | 나레이션 | sheet_003 |
| 06:56–08:15 | Pinterest 에서 찾은 `Hello` 레퍼런스 → ChatGPT «Work» 모드(모델 GPT-6 Astra Medium)에 URL + «컴퓨터 유즈로 …» 요청 + 가이드 → 컴퓨터 유즈가 링크를 열고 **스크린샷을 찍으며** 색감·구성·타이포 움직임·전환을 하나씩 봄 → 프롬프트 문서 | 화면 녹화(맥) | 영문 프롬프트 | 나레이션 + [음악] | sheet_003~004 |
| 08:15–08:39 | **결과 3 — 13초**: 아이보리 바탕에 파란 `Hello!` 가 획 단위로 쓰여짐 → 같은 획이 손 모양 + 웃는 입 엠블럼으로 재배열 → 좌우로 흔듦 → 해체 → 같은 사이클 한 번 더 | 한 카메라 고정, 6.7초 사이클 2회 | 파랑 `Hello!` | — | sheet_004 · 프레임 `q_C.jpg` |
| 08:39–10:17 | **Newtake 스마트 분석**: 업로드한 레퍼런스(`FROM CENTER` 반복 타일) 선택 → 창에서 «샷 / 모션 / 음악» 중 샷·모션만 → «분석 시작» → 샷별 영상 조각 S01~S09 + 줄마다 한 줄 라벨 → 조각 전체를 그룹 해제해 비디오 노드에 연결 + 앞의 키네틱 프롬프트 연결 → 결과(반복 텍스트 효과 반영) | 캔버스 줌아웃 → 카드 격자 | 라벨 예: `S04 ／ 전체화면·고정 ／ C-체인 대각선 회전 패턴·리듬 전환` | — | sheet_004~005 · 프레임 `q_D.jpg` |
| 10:17–12:00 | **캐릭터 애니메이션**: 참조 이미지 2장(플랫 캐릭터) + 가이드 → 텍스트 생성 노드(Gemini 3.1) → 요청 «… 쇼핑몰 할인 오픈런이야» → 영상 프롬프트 → 비디오 노드 생성 → 결과(달리는 군중 · «오픈런» 핑크 큰 글자 · «UP TO 70%» · «지금 시작») | 오른쪽 달리기, 글자 뒤로 캐릭터가 지나감, 쇼핑백 뛰어듦 | 한글 굵은 글자 + 영문 `UP TO 70%` | — | sheet_005 · 프레임 `q_E.jpg` |
| 12:00–12:29 | «지금 시작» 정지 → 두 번째 생성: 영상 노드에 **참조 이미지 3장을 다시 연결** → 결과(출입문 앞 군중 → 달려감 → «지금 바로 달리세요» → 쇼핑백 → «단 하루의 쇼핑 찬스, MEGA SALE») | 가로 카메라 팔로우, 글자 슬라이드 | 한글 + 영문 `MEGA SALE` | — | sheet_006 · 프레임 `q_F.jpg` |
| 12:29–13:14 | **제품 홍보**: 제품 이미지(실제 단백질 통 사진) + 프롬프트 → 결과(«오늘의 프로틴 / CLEAR하게.» → 제품 등장 → «프로틴 루틴을 산뜻하게.» → `20g PROTEIN`·`LOW SUGAR`·`4.5g BCAAs` → 원형 와이프 → `LEMON ICED TEA` → 제품 정지) | 제품이 글자 사이로 들어옴 | 한글 + 영문 | — | sheet_006 · 프레임 `q_G.jpg` |
| 13:14–14:07 | **25그리드 스토리보드**: 제품 이미지 선택 → 위 툴바 «그리드 분할» → «25그리드 연속 스토리보드» 선택 + 모션 프롬프트 연결 → 모델 GPT Image 2 → 4K 한 장 안에 번호 붙은 25칸 | 화면 녹화 | 칸 안 글자(한글 카피) | 나레이션 + [음악] | sheet_006~007 |
| 14:07–14:42 | **제품 이미지 한 장만으로**: 스토리보드를 «이 비타민 제품을 홍보하는 프로모션 영상 스토리보드를 만들어줘.» 한 줄로 생성 → 그 그리드를 영상 노드에 연결 → 결과(어두운 책상의 손 → 빛 → 제품 박스가 돌 받침에 떨어짐 → 알약 → `B` 로고 → 번개·물 튐 → 분자 → 점프 실루엣 → 박스 낙하 → 정지) | 시네마틱 컷 20초대 | `하루 1알 에너지 에터민B MIX` 등 (3-5장) | — | sheet_007 · 프레임 `q_H.jpg` |
| 14:42–15:09 | 같은 스토리보드를 ChatGPT 이미지로 만든 4칸(오픈런 / UP TO 70% / 지금 시작) 보여 줌 → «원하는 주제와 스타일로» 3종 요약 카드(Kinetic Typography / Character Animation / 제품 설명·홍보) | 카드 정지 | 요약 라벨 | 나레이션 | sheet_007 |

## 3. 방법 (강의 — 도구 · 프롬프트 원문 · 설정값 · 순서 · 결과 확인)

### 3-1. 도구
| 도구 | 쓴 곳 | 근거 |
|---|---|---|
| **Newtake**(뉴테이크) | 영상·이미지·텍스트를 한 캔버스에서 노드로 이어 만드는 «AI 영상 생성 플랫폼». 노드 종류 = 텍스트 · 이미지 · 비디오. 우측 패널 «Agent» + «Skill로 오늘의 이야기를 시작하세요»(POP MV 등 프리셋). 상단 툴바(이미지 노드): 인물 질감 조정 · 파노라마 · 다각도 · 조명 · 9분할 그리드 · 고화질 · 요소 편집 · 레이어 분리 · 그리드 분할 — **강의는 «그리드 분할» 하나만 씀**. 요금제 배지 + 크레딧 숫자(⚡) 상시 표시 | 04:15–05:42 · 13:30 · 화면 `272.jpg`·`862.jpg`. 웹 검색으로는 Newtake 가 LiblibAI 의 해외판 LibTV 계열이라는 **제3자 한 곳 설명**뿐(공식 확인 못 함 — 7장) |
| 영상 모델(Newtake 안) | 이번 강의는 **MiniMax H3**(목록에 Wan 3.0 · Minimax H3 Max(예상 30s) · MiniMax H3(2min) · Happy Horse 1.1/1.0 · Kling O3 · Kling 3.0 · Kling O1 · 일부 💎표시(상위 요금제로 읽힘)). 말: «H3 는 모션 그래픽 전용은 아니고 범용에 가깝지만 텍스트와 그래픽 표현, 복잡한 지시 반영, 레퍼런스를 활용한 모션 제어에 강점, 생성 비용 대비 품질 경쟁력» | 04:52–05:10 · `300.jpg` |
| 텍스트 모델(Newtake 안) | Gemini 3.1 선택(목록: Gemini 3.1 · GPT-6 Astra · ChatGPT 5.6 Sol/Luna/Terra · ChatGPT 5.5 · Gemini 3.1 Flash). 말: «비용 부담이 적은 Gemini 3.1» | 11:09–11:18 |
| 이미지 모델(Newtake 안) | 스토리보드는 **GPT Image 2**(목록에 Nano Banana Pro/2 · Newtake Director Engine · GPT Image 2.5 Pro/Fast · Seedream 5.0 Pro). 말: «GPT 이미지 모델로도 충분히 만들 수 있으니 Newtake 안 쓰는 분은 크레딧을 추가로 구매하지 않아도» | 13:45 · 14:42 |
| ChatGPT(데스크톱) | ① 가이드 + 리서치 → 영상 프롬프트(02:20, 처리 4분 8초) ② **«Work» 모드 + 컴퓨터 유즈**로 Pinterest 링크를 직접 열어 영상 분석(07:09–07:50, 처리 4분 59초). 모델 표시 GPT-6 Astra Medium | `140.jpg` · `437.jpg` · `478.jpg` |
| Pinterest | 레퍼런스 영상 찾기(`Hello` 모션) | 06:51 |
| 가이드 프롬프트 파일 | 설명란: 구글 드라이브 파일(`영상에서 사용한 모션 그래픽 프롬프트 작성 가이드`). **내용 전체는 영상에 안 나옴** — 앞 6문단만(아래) | 7장 |

### 3-2. 단계 순서 (방법 ① 가이드 → 영상)
1. 가이드 프롬프트(«Master Version»)를 ChatGPT 에 붙임 → ChatGPT 가 «확인했습니다… 기본적으로 영어 연출문, 정확한 원문 화면 카피, 타임코드, 모션·카메라·트랜지션, Text Fidelity, 제품/브랜드 일관성, End Card 를 포함하고, 별도 길이 지정이 없으면 공백 포함 6,000~6,500자, 최대 7,000자 이내로» 라고 답함.
2. 같은 채팅에 주제 요청(아래 «요청 원문 ①») → 웹 검색 10건 → 영문 프롬프트 한 편.
3. 프롬프트 전체 복사 → Newtake «제작 시작» → 캔버스에 붙여넣기(텍스트 노드) → 노드 끌어와 **비디오 생성 노드** 추가.
4. 모델 MiniMax H3 → 비율·해상도·길이·개수(3-4장) → 생성 버튼(⚡ 크레딧 숫자가 버튼에 표시).
5. «대략 5분에서 10분이면 완성» → 결과 확인 → 프롬프트의 스타일 단락만 바꿔(네오브루탈리즘) 같은 구성의 다른 스타일 생성.

방법 ②(레퍼런스): 레퍼런스 영상 URL + «컴퓨터 유즈로 접속해 분석 → 가이드 프롬프트를 참고해 최대한 동일한 스타일의 영상 생성 프롬프트 작성» → 프롬프트의 길이(13초)에 맞춰 영상 길이도 13초로 → 생성.
스마트 분석: 업로드한 레퍼런스 영상 → 샷·모션만 분석 → 조각 전체를 레퍼런스로 비디오 노드에 연결(+ 앞의 프롬프트).
캐릭터: 캐릭터 이미지 + 가이드 → **텍스트 생성 노드**(Gemini 3.1)가 프롬프트 작성 → 영상 노드 생성 단계에서 **캐릭터 이미지를 한 번 더 참조**.
제품: 영상 프롬프트 + 제품 이미지 참조 → 영상. 사전 확인은 스토리보드(25그리드).

### 3-3. 프롬프트 원문 (화면에서 옮김 — 영상에 나온 것만)

**가이드 프롬프트 «AI 영상 생성 모델용 상업 모션그래픽 프롬프트 작성 가이드 — Master Version»**(영상에 보인 앞부분, `137.jpg`; 이후는 «더 보기» 접힘):
> 너는 AI 영상 생성 모델용 상업 모션그래픽 프롬프트를 전문적으로 작성하는 광고 크리에이티브 디렉터다.
> 사용자가 주제, 제품, 브랜드, 영상 스타일, 레퍼런스 이미지, 분위기, 광고 목적 또는 간단한 아이디어를 제공하면 이를 분석하여 실제 영상 생성 모델에 바로 입력할 수 있는 완성형 상업 영상 프롬프트 하나를 작성한다.
> 결과물은 단순히 보기 좋은 영상 설명이 아니라 다음 목적을 만족해야 한다.
> **시선을 잡고 → 메시지를 이해시키고 → 제품·브랜드를 기억하게 만드는 상업 영상**
> 사용자가 구체적인 연출을 제공하지 않았더라도 광고 목적에 맞는 영상 구조, 카피, 모션, 장면 흐름, 타이포그래피, 카메라, 사운드를 적극적으로 설계한다.
> 단, 확인되지 않은 제품 효능, 기능, 성능, 수치 또는 사실은 임의로 만들어내지 않는다.

**요청 원문 ①(키네틱, ChatGPT)**: «이 가이드에 따라 유튜브 채널 디자인하는AI에 대해서 리서치한 후 키네틱 모션 그래픽 영상 생성 프롬프트를 작성해줘. 6000자 내외로 작성해야해.» (`144.jpg`)

**생성된 영상 프롬프트 ①(영문 원문 일부 + 영상 속 한글 번역; `152.jpg`·`156.jpg`·`160~245.jpg`)** — 구조는 아래 순서다:

- 맨 윗줄 `10.000 seconds.`
- `Creative Mode: Kinetic Typography + Editorial Graphic + UI / Tech Product Motion. Structure: Multi-shot. Brand voice: confident, curious, practical, modern, design-literate. Create a premium brand film for “디자인하는AI” around one idea: AI is a practical creative workflow that turns an idea into visible design. Capture attention immediately and leave the exact channel name strongly in memory.`
- `OVERALL VISUAL STYLE` — `High-end editorial motion design with near-black and warm-white backgrounds, accented by acid lime, vivid cyan, and small violet details. Swiss-inspired grid, oversized Korean typography, thin lines, modular cards, selection boxes, keyframe dots, prompt brackets, and restrained generative textures. Crisp 2D vectors with subtle 2.5D layering. Typography is the hero. Use clean Korean sans-serif with strong weight contrast. Motion: graphic …`(한글 번역: 즉각적인 그래픽 정착 · 마스크 와이프 · 크롭을 통한 등장 · 자간 변화 · 모듈 조립 · 자석처럼 맞물리는 정렬 · 강한 크기 변화 · 정교한 매치 컷. **카메라는 대부분 고정. 로봇·빛나는 뇌·상투적인 회로·사이버펑크 풍경·홀로그램·쏟아지는 코드·일반적인 SF 볼거리는 피하세요.**)
- **샷 5개(타임코드는 소수 셋째 자리까지)**
  - 샷 1 — 0.000–1.600초 — 시선 끌기: 검정에 가까운 배경. 짧고 건조한 클릭 소리와 함께 깜빡이는 커서가 나타나 흰색으로 `“AI, 그냥 쓰고 있나요?”` 를 정확히 입력. 라임색 선택 박스가 `“쓰고”` 를 둘러싸고 한 번 늘어났다가 축소. **0.900초에** 매우 큰 흰색 문구 `“디자인하세요.”` 가 강하게 튀어나옴. 마침표는 따로 등장하며 날카로운 충격감. 카메라가 아주 조금 다가감. **1.350초에** 마침표가 커지며 원형 와이프 전환.
  - 샷 2 — 1.600–3.700초 — 아이디어에서 결과물로: 따뜻한 흰색 배경, 왼쪽→오른쪽 작업 흐름. 가는 프롬프트 입력란에 `“아이디어”`. 기하학적 선이 나와 굵은 블록 `“이미지” → “브랜딩” → “UI” → “영상”` 을 끌어옴. «이미지» 는 잘린 픽셀에서 깔끔한 프레임으로, «브랜딩» 은 세 가지 변형 반복 뒤 하나로 정렬, «UI» 는 모듈형 그리드에 딱 맞춰짐, «영상» 은 세 개의 키프레임 점이 있는 짧은 타임라인으로 펼쳐짐. **가짜 인터페이스 문구는 사용하지 마세요.** **3.350초에** 모든 모듈이 디자인 도구에서 그룹화하듯 중앙으로 모여 하나의 정사각형이 되고, 크기를 맞춘 매치 컷으로 그 정사각형 안으로 전환.
  - 샷 3 — 3.700–6.000초 — 작업 흐름의 메시지: 정사각형이 검은 캔버스로 바뀜. 왼쪽 위 `“툴보다 중요한 건”`, 아래 훨씬 큰 시안색 `“만드는 흐름.”`. `“만드는”` 은 완성된 한글 음절 블록들이 하나의 기준선에 맞물려 조립, `“흐름.”` 은 왼→오른 마스크로 드러남. 아래 가는 라임색 과정 선을 그리고 선을 따라 프롬프트 괄호 · 이미지 프레임 · 레이아웃 그리드 · 재생 삼각형 네 개의 중립적인 기호가 약간의 탄성 지연을 두고 나타남(타사 로고 없이). **5.650초에** 선이 오른쪽으로 가속하며 화면 구성을 끌고 나가는 오브젝트 와이프 전환.
  - 샷 4 — 6.000–8.300초 — 채널이 다루는 영역(영문 원문): `Fast editorial montage on warm white, organized by a strict grid. Oversized words hit different zones: “AI DESIGN”, “BRANDING”, “UI / WEB”, “MOTION”, “WORKFLOW”. AI DESIGN assembles from two halves; BRANDING appears as three outline echoes then resolves solid; UI / WEB snaps into a clean grid; MOTION enters with brief directional smear then becomes sharp; WORKFLOW magnetizes every prior module into one ordered system. Between type hits, flash abstract outputs: a generative editorial image panel, geometric brand-mark studies, web-layout wireframe, and a three-frame motion timeline. No real software UI, branded logos, or pseudo-text. Pacing feels like an expert tutorial compressed into visual rhythm. Use percussion-synced hard cuts and rectangle match cuts.`
  - 샷 5 — 8.300–10.000초 — 브랜드 강조 / 엔드 카드(영문 원문): `All modules shrink into small rectangles around center, then snap onto one baseline and merge into the exact title: “디자인하는AI”. Render “디자인하는” in black and “AI” in acid lime if reliable; text accuracy takes priority. Below, reveal exactly: “AI 디자인을 실전으로.” in smaller black type. A thin cyan line draws beneath once and stops. From 9.150s to exactly 10.000s, hold the final composition steadily. No new elements, morphing, or camera movement. The final frame must feel like a confident editorial channel identity lockup.`
- `TYPOGRAPHY / TEXT FIDELITY` — `Treat every text string inside quotation marks as an immutable graphic asset. Render it exactly as provided, preserving every Hangul character, spacing, punctuation, capitalization, numeral, slash, and English spelling. Never translate, paraphrase, autocorrect, substitute similar Hangul, split syllable blocks into jamo, omit characters, add characters, or create pseudo-text. Required strings are exactly: “AI, 그냥 쓰고 있나요?”, “디자인하세요.”, “아이디어”, “이미지”, “브랜딩”, “UI”, “영상”, “툴보다 중요한 건”, “만드는 흐름.”, “AI DESIGN”, “BRANDING”, “UI / WEB”, “MOTION”, “WORKFLOW”, “디자인하는AI”, “AI 디자인을 실전으로.” Use completed Hangul syllable blocks, clean Korean sans-serif glyphs, front-facing text, high contrast, sufficient size, minimal perspective distortion and motion blur. Text may crop or mask during entrance, but once settled it must resolve into the exact full string and hold long enough to read.`
- `MOTION / CAMERA CONTROL` — `Use one coherent grammar: select → transform → align → output. Fast entrances settle with precise ease-out. Major type hits may overshoot only 2–3%. Use tracking expansion for curiosity, collapse for decisiveness, masks for progression, and magnetic snapping for workflow. Preserve spatial continuity when elements transform. Mostly orthographic poster-like framing. No uncontrolled spinning, excessive bounce, liquid morphs, particle explosions, heavy blur, or camera shake.`
- `overall_soundscape`(번역): 정교한 모션 디자인 사운드 — 키보드 클릭, 커서의 짧은 틱, 종이를 넘기는 듯한 스와이프, 또렷한 UI 정착음, 타이포 강조 시 짧고 낮은 충격음, 마스크 와이프의 은은한 휙 소리, «디자인하는AI» 가 조립될 때 한 번의 자석 결합음. `배경 음악`: 약 120 BPM 현대적 전자음악 비트(절제된 킥 · 또렷한 타악기 · 과하지 않은 베이스). 처음엔 간결하게 시작, 몽타주에서 고조, 마지막 제목 직전 타악기를 줄임, 짧고 자신감 있는 종지.
- `생성 제어`(번역): 모든 화면 구성을 미니멀하고 의도적이며 디자인 중심으로 유지. 영상 전체에서 팔레트·그리드·타이포·그래픽 모티프의 일관성. **관련 없는 텍스트·로고·워터마크·브라우저 테두리·앱 아이콘·인물·스티커·추가 사물은 넣지 않는다.** 특정 타사 소프트웨어 인터페이스 모방 금지. 추상적인 결과물 카드에는 도형과 이미지를 넣을 수 있지만 읽을 수 없는 문자는 넣지 않는다. 마지막에 가장 강하게 기억에 남아야 하는 것은 정확한 채널명 «디자인하는AI».
- 강의 말: «문구를 바꾸려면 각 샷 따옴표 안의 문구를 수정하고 **필수 문구 목록도 함께 맞춰 줘야 합니다. 띄어쓰기와 문장 부호도 중요합니다.**»(03:33–03:41)

**스타일 변주 프롬프트(네오브루탈리즘, `359.jpg`·`365.jpg` — 전체 문서에서 바뀐 부분)**: `Create a 10-second kinetic typography identity film for the Korean YouTube channel “디자인하는AI”. CONCEPT: DESIGN SIGNAL. Visualize AI DESIGN as a creative signal moving through different forms of design. Do not show software, interfaces, tools, or literal workflows. Typography itself is the design material: it prints, stretches, tears, echoes, pulses, folds, distorts, overlaps, gains depth, and rebuilds. The channel spans graphic design, UI/UX, branding, motion, image, video, 3D, AI tools, Vibe Design, and new workflows. Suggest this range with only a few strong words. Use mostly English during fast motion. Keep Korean minimal. The only major Korean title is: “디자인하는AI”. STYLE: Neo-Brutalist editorial design + experimental magazine typography + analog print texture + digital kinetic type + minimal 3D. Use condensed and grotesk type, oversized cropped words, black-and-white contrast, paper texture, halftone dots, ink bleed, misregistration, photocopy grain, repetition, and controlled digital distortion. Add one accent color such as signal red or cobalt blue. Keep it tactile and art-directed. Typography is the hero. SHOT 01 — 0.00–1.30 SEC Hard cut to oversized black typography: “DESIGN” on warm off-white paper texture. The word is larger than the frame and cropped at the edges. On each beat, it reprints slightly offset, creating a bold registration effect. A smaller: “AI” hits the center like a stamp. Lock both into: “AI DESIGN” A halftone texture passes through the letters. No extra copy. Music begins immediately with a continuous …`
→ **눈여겨볼 점: 이 변주는 «한글을 최소로, 영문 위주»로 바꿨다(Use mostly English during fast motion. Keep Korean minimal).** 한글 글자 깨짐을 피하는 쪽으로 지시서를 쓴 셈이다.

**방법 ② 요청 원문(ChatGPT Work 모드, `437.jpg`)**: `https://co.pinterest.com/pin/281543726561703/ 컴퓨터 유즈로 이 링크에 접속해서 영상을 분석한 뒤 가이드 프롬프트를 참고하여 최대한 동일한 스타일의 모션 그래픽 영상을 생성할 수 있도록 프롬프트를 작성해줘`(말 07:17–07:29에서 옮김, 입력창엔 앞부분만 보임) + 가이드 프롬프트 첨부.
**생성된 프롬프트 ②(`478.jpg`·`488.jpg`) — 눈여겨볼 점은 «수치로 못박았다»**:
> `13.400 seconds. Creative Mode: Kinetic Typography + playful 2D graphic identity motion. Structure: one continuous, locked-camera composition containing two identical 6.700-second animation cycles. Build Hello! stroke by stroke, transform it into a smiling waving-hand emblem, then clear the background. Repeat once. The lettering is the subject; add no product, invented brand, slogan, CTA, or end card.`
> `VISUAL STYLE: Use flat, clean vector animation on a perfectly uniform warm ivory background, approximately #FFF3DD. The main lettering and final emblem are saturated ultramarine blue, approximately #2524C9. Restrict secondary colors to soft apricot orange #F6AC69, bright mint turquoise #5EE0C0, and a thin coral-red accent #EA6558. Use solid colors, crisp edges, and subtle antialiasing, without gradients, shadows, texture, or dimensional shading. The mood is warm and witty.`
> `Keep generous ivory space around a compact central composition. The readable word occupies approximately 44 percent of the canvas width; keep the hand similarly compact. … Use consistent medium blue strokes, broad soft-ended orange bands, short mint caps, and thin coral curves.`
> `LETTERING AND EMBLEM DESIGN: Display exactly: "Hello!". Use custom geometric, monoline sans-serif lettering: a tall narrow capital H, a small circular lowercase e with a clear internal crossbar, two long straight lowercase l stems, a circular lowercase o, and a tall exclamation stem with a separate compact dot. … The central transformation rearranges those same blue components into an abstract smiling raised hand. The tall letter stems become a fan of four upright finger-like bars. The H contributes the bent outward thumb … Add no filled glove silhouette, anatomy, body, pupils, or extra fingers.`
> `MOTION LANGUAGE: Animate with controlled path reveals, stroke extension, small rotations, squash-and-stretch of individual bars, quick overshoots, and soft settling. Accelerate decisively and ease into position. … Restrict fleeting blur to the fastest wave; reading moments stay sharp.`
> `FIRST CYCLE — 0.000s–6.700s` 아래 **0.000–0.250 / 0.250–1.150 / 1.150–2.250 / 2.250–3.350 / 3.350–4.150 / 4.150–4.800 / 4.800–5.950 / 5.950–6.700** 8구간에 «무엇이 어디서 어떻게» 한 문단씩. `SECOND CYCLE — 6.700s–13.400s: Repeat all seven first-cycle intervals exactly, adding 6.700 seconds to every start and end time. … The greeting completes at 10.050s; the hand transformation begins at 10.850s; waving runs from 11.500 to 12.650; disassembly ends at 13.400s. Finish on the opening ivory …` · `CAMERA, TEXT FIDELITY, AND FINISH` 단락.
→ **레퍼런스 영상 1개 → 색상 hex · 비율(글자가 화면 폭의 44%) · 구간별 동작을 «측정값처럼» 적은 스펙**이 나왔다. 이것이 우리가 가져올 부분(5-4).

**캐릭터 요청 원문(Newtake 텍스트 노드, Gemini 3.1, `691.jpg`·`700.jpg`)**: «참조한 가이드와 캐릭터 레퍼런스에 따라 플랫한 캐릭터가 등장하는 모션 그래픽 애니메이션 영상을 만들고 싶어. 영상의 주제는 쇼핑몰 할인 오픈런이야. 영상 생성 프롬프트를 작성해 줘.` (첨부: 가이드 텍스트 노드 + 캐릭터 이미지 2장, 버튼 ⚡96)
**생성된 프롬프트(`700.jpg`, 앞부분)**: `10.000 seconds. Creative Mode: Character-led Commercial + Kinetic Typography + 2D Motion Graphics. Visual Style: High-energy 2D flat vector illustration style, heavily inspired by "Corporate Memphis" aesthetics. Exaggerated character proportions: unusually small heads, oversized, thick, and elongated limbs, with distinctly large hands and feet. Vibrant, high-contrast, and solid color palette: emerald green, electric blue, hot pink, vivid orange, bright yellow, and solid black. Clean edges, zero outlines, and absolutely flat colors with no gradients, 3D shading, or realistic textures. Minimalist warm beige/light yellow background scattered with abstract geometric decorations (floating four-point stars, squiggly lines, confetti dots, small circles). Typography is bold, modern Korean sans-serif, acting as a graphic element with high impact. The overall mood is playful, urgent, highly energetic, and strictly 2D flat graphic motion. Text Fidelity Instructions: Treat every text string inside quotation marks as an immutable graphic asset. Render it exactly as provided, preserving every Hangul character, spacing, punctuation, capitalization, numeral, and English spelling. Use correct Hangul glyph construction in a clean, bold Korean sans-serif font. Ensure high contrast against the background. Do not auto-translate, add …`(이하 접힘)

**제품 프롬프트(작은 글씨, `826.jpg` 에서 옮김 — 일부 글자는 확대해도 흐릿한 곳 있음)**: `Create a premium 2.5D motion-graphic commercial for 바로채움 and the product in the reference image. Use the reference only as a product identity/design guide; never show the source image, screenshot, browser frame, thumbnail, or source watermark. VISUAL STYLE: Clean 2.5D product commercial + bold kinetic Hangul typography + minimal editorial graphics. Palette: vivid warm yellow, saturated cobalt blue, ivory stone, white highlights. Use flat yellow backgrounds, controlled diagonal sunlight bands, crisp shadows, restrained paper grain, sharp graphic edges, and polished studio lighting. Typography is bold modern Korean sans-serif, geometric, front-facing, high contrast. Keep graphic density low-to-medium. Camera motion is limited to micro push-ins and subtle parallax. PRODUCT IDENTITY: Reconstruct one upright rectangular yellow box from the reference. Preserve its proportions, 바로채움 mark at upper left, cobalt-blue front typography, large “하루 1알 에너지 비타민B MIX” hierarchy, circular B symbol with blue dots, badge placement, lower blue information blocks, and overall label structure. Keep the front panel dominant and undistorted. Do not redesign the package or invent claims/logos. Do not reproduce the lower-right “Newtake” watermark.`
다른 제품 건(단백질 통, `760.jpg`)의 프롬프트 머리: `MYPROTEIN CLEAR WHEY — Motion Graphic Ad Prompt / 10.000 seconds, vertical 9:16, 1080x1920, 30fps. … Use the provided product image only as a product identity reference, not as a screenshot or flat image inside the video. Reconstruct the product as a clean hero object while preserving the original cylindrical white tub, ribbed white lid, package proportions, MYPROTEIN logo, cream/beige label, lemon-yellow and muted orange shapes, charcoal typography … Keep only verified package information: MYPROTEIN / CLEAR Whey Protein / LEMON ICED TEA FLAVOUR / 20g PROTEIN / LOW SUGAR / 4.5g BCAAs* … Do not redesign the package or invent claims. VISUAL STYLE … SHOT 01 — HOOK | 0.000s–1.500s Background: pale lemon field with a soft cream gradient. Oversized Korean text fills the frame …`
→ **«확인된 정보만 남기고 지어내지 말라»(Keep only verified package information)** 는 우리 «숫자를 지어내지 않는다»와 같은 방향.

**스토리보드 요청(`862.jpg`)**: 이미지 노드에 `25그리드 연속 스토리보드` 칩을 붙이고 입력 «이 비타민 제품을 홍보하는 프로모션 영상 스토리보드를 만들어줘.» (참조: 제품 이미지 1장, 모델 GPT Image 2). 앞 단계(제품 영상 프롬프트 연결)에서는 모션 프롬프트도 함께 연결(`826.jpg`).

### 3-4. 설정값 · 비용 (화면에 나온 것만)
| 항목 | 값 | 근거 |
|---|---|---|
| 영상 노드 설정 항목 | **비율** 21:9 · 16:9 · 4:3 · 1:1 · 3:4 · 9:16 / **선명도** 768P · 2K / **영상 길이** 슬라이더(10s 에서 확인, 범위는 안 보임) / **생성 수량** 1개 · 2개 · 4개 / 텍스트→비디오 모드 · 위쪽 칩: 참고 · 특수효과 · 캐릭터 라이브러리 · 카메라 무빙 · 디렉터 스튜디오 | `322.jpg` · `330.jpg` |
| 크레딧 | MiniMax H3 **16:9 · 768P · 5초 · 1개 = 70** / **768P · 10초 · 1개 = 140** / **2K · 10초 · 1개 = 220** | `300.jpg` · `330.jpg` · `336.jpg` |
| 실제 차감 | 강의 시연은 16:9 · 2K · 10초 · 1개로 생성 → 잔액 **29,223 → 29,003**(= 220) | `272.jpg` · `341.jpg` |
| 해상도 환산 | 768P 16:9 의 결과 노드 표기 **1344×768** | `365.jpg` |
| 텍스트 생성 | Gemini 3.1 · 텍스트 노드 한 번 = ⚡**96**(가이드 + 이미지 2장 참조) | `691.jpg` |
| 이미지 생성 | GPT Image 2 · 16:9 · 고화질 · 4K · 1장 = ⚡**124**(출력 3840×2160). 화질 표준/고화질 · 선명도 1K/2K/4K · 수량 1·2·4장 | `832.jpg` · `826.jpg` |
| 모델 예상 시간 표시 | Minimax H3 Max 30s · MiniMax H3 2min · Happy Horse/Kling/Wan 3min(말로는 «5~10분») | `300.jpg` · 05:39 |
| 원화·구독료 | **언급 없음**(요금제 배지만 보임) | — |
| 쇼츠/릴스 | «9대 16 으로 바꿔 주시면 됩니다»(05:25) — 9:16 은 드롭다운에 존재, **세로로 만든 결과는 영상에 안 나옴** | `330.jpg` |

### 3-5. 결과물 판정표 (0.25초 간격 시트 `q_A~q_H.jpg` 로 본 것 — «잘 된다» 말을 믿지 않고)
| 결과 | 지시와 맞은 것 | 틀어진 것(프레임 근거) | 판정 |
|---|---|---|---|
| ① 키네틱 10초(`q_A`) | 샷 경계가 지시 타임코드와 거의 일치: 커서 타자 → `쓰고` 라임 박스 → `디자인하세요.` 확대 → 원형 와이프(약 3.3~3.5초), 블록 연결 `이미지·브랜딩·UI·영상` → 정사각형 → 검정 캔버스 `툴보다 중요한 건 / 만드는 흐름.`(시안색, 음절 단위로 쌓임) → `AI DESIGN` 몽타주 → `디자인하는AI` + `AI 디자인을 실전으로.` 마지막 약 1초 정지. 문구 대부분 정확, 입장 중 잘림은 지시 허용 | **물음표 → 쉼표**(`있나요,` — 지시는 `있나요?`, 샷 시작부터 끝까지 `,`). 샷 2 의 `아이디어` 입력란은 아주 작은 칸(약 0.5초)으로만 보이고 블록이 곧바로 이어짐(지시: 선이 블록을 «끌어옴» — 선 표현은 약함). `BRANDING` 이 8.0초에 글리치성 겹침(지시: 외곽선 잔상 3겹 → 채움). 샷 4 의 `UI / WEB` 가 `UI/WEB`(공백 없음) | **구조 B+ · 문구 정확도 B−**. 광고 문구에 쓰려면 글자만 렌더러 교체가 필요 |
| ② 네오브루탈 10초(`q_B`) | 스타일이 확 바뀌고(종이 질감·검정 대형 글자·접힌 검은 종이 3D) 샷 구성 유지. 마지막 `AI DESIGN` → `디자인하는AI` 한글 정확 | 지시에 없는 영단어 몽타주 `FORM·TYPE·MOTION·SPACE·EXPLORE·CREATE·VIBE·MAKE·SHIFT` 가 많음(프롬프트 뒷부분 미확인이라 지시일 수도 있음). 마지막 한글 `디자인하는A N` 로 한 프레임 깨졌다 복구(약 0.25초) | **스타일 전환 속도는 장점**(지시 두 단락 교체로 완전히 다른 룩). 한글은 마지막 한 줄뿐이라 위험 노출이 적음 |
| ③ `Hello!` 13초(`q_C`) | **레퍼런스 대비 유사**: 획 단위로 쓰여짐 → 손 엠블럼 → 흔들기 → 해체 → 한 사이클 더(약 6.7초 주기 2회로 확인). 색(군청 파랑·살구·민트·코랄)·아이보리 바탕 일치 | 해체 직전 프레임이 약간 지글거림 | **B+** — hex 와 구간 수치를 적은 지시서의 효과 |
| ④ 스마트 분석 반영(`q_D`) | 레퍼런스의 반복 타일·`ROTATING`·`EXPLORE`·`VIBE`·3D 쇠 글자 회전 등이 들어오고 마지막 `디자인하는AI` 정확 | 앞의 프롬프트 의도(5샷 구성)가 레퍼런스 샷 영향으로 **다른 구성**(`AI` 대형 → 회전 3D 금속 글자). 마지막 한글 엔드 카드 위에 **강의 자막(«반복되는 텍스트 효과들이 …»)이 얹힘** — 강의 편집물 | **레퍼런스를 강하게 넣으면 지시서 구성이 덮인다** |
| ⑤ 캐릭터 10초(`q_E`) | 플랫 벡터 질감 유지, 출렁이는 달리기(왼발·오른발 교차), `오픈런` 핑크 대형 글자, `UP TO 70%` 정확, 마지막 `지금 시작` 정확 | **캐릭터 몸이 글자를 가림**(`오픈런` 위로 몸이 지나가 `오픈` 이 읽히지 않는 프레임이 다수). 4~5초 군중 장면에서 **팔다리가 녹아 번짐**(`715.jpg`: 쇼핑백 든 인물의 다리·치마가 붙고 파란 옷 인물 얼굴이 뭉개짐). 인물 수가 1 → 3 → 4 로 바뀌며 얼굴·옷이 장면마다 달라짐 | **분위기 B+ · 일관성 C+ · 가독성 C** |
| ⑥ 캐릭터 참조 재연결(`q_F`) | 같은 캐릭터 룩(초록 재킷 · 파란 바지 · 핑크 치마)이 처음 영상보다 더 유지, 배경(출입문)·글자 `오픈런, 준비되셨나요,` `지금 바로 달리세요` `단 하루의 쇼핑 찬스, MEGA SALE` 읽힘 | **`오픈런, 준비되셨나요,` — 물음표 없이 쉼표**(지시 문구를 모름), 6.5~7.75초에 `지금 바로 달리세요` 가 캐릭터 뒤·앞으로 겹쳐 흐르며 글자 일부가 가려짐 | **참조를 영상 단계에서 다시 물리면 일관성이 오른다**(강의 주장 확인). 문장부호는 여전히 흔들림 |
| ⑦ 제품 10초(`q_G`) | 제품(통)이 프레임 내내 같은 모양 유지, 글자 `오늘의 프로틴, / CLEAR하게. / 프로틴 루틴을 산뜻하게. / 20g PROTEIN / LOW SUGAR / 4.5g BCAAs*` 정확 | **제품이 글자를 가림**: `LEMON ICED TEA` 의 가운데가 통에 가려 `LEMON IC… TEA`, 마지막 10초 정지 장면도 `LEMON IC… FLAVOUR`. 통 라벨의 작은 글자는 원본과 같은지 확인 불가(해상도) | **제품 일관성 A− · 가독성 B−** |
| ⑧ 스토리보드 → 영상 20초(`q_H`) | 그리드 칸 순서(어두운 책상 손 → 빛 → 박스 낙하 → 개봉 → 알약 번개 → 분자 → 점프 실루엣 → 박스 낙하 → 정지)대로 영상이 흐름 | **글자 오류**: 박스 앞면 `하루 1알 에너지 비타민B MIX` 가 영상에서 `에터민B MIX` 로, 분자 `Complex` 가 `Corxplex`, 상단 로고 `하루지발` 등 **없는 글자**. 책상의 인물은 실사풍 시네마틱이라 앞 영상들(2D 플랫)과 **질감이 다름**(제품 박스 컷은 사실적) | **스토리 흐름은 확실히 따라가나 한글·로고 글자가 깨진다** |

**이 표가 강의의 가장 중요한 «정직한» 근거다.** 강의는 «결과가 잘 나온다»고 하지만, 프레임으로 보면 **글자(문장부호·한글 음절·영문 철자)와 캐릭터 일관성**이 한계다 — 우리 광고는 정확한 글자가 생명이다.

## 4. 기법 카드

### K1. 촬영 지시서형 프롬프트(샷 표 + 정확한 문구 + 모션 문법 + 금지 목록)
- 무엇: 프롬프트를 `길이 → 창작 모드/브랜드 톤 → 비주얼 스타일(팔레트·그리드·질감) → 샷 N개(타임코드·무엇이 어디서 어떻게·전환) → 타이포 정확성(필수 문구 목록) → 모션/카메라 규칙 → 사운드 → 생성 제어(금지)` 순서로 쓴다. 샷마다 «정확한 문구는 따옴표», «전환은 시각으로(1.350초에 원형 와이프)», «마지막 0.85초 정지».
- 왜 먹히나: 결과 ①이 지시 타임코드와 ±0.2초로 맞았다(프레임 근거). 모델이 «무엇을 할지»보다 «언제 무엇이 어디서»에 잘 반응한다.
- 시각(근거): 02:37–04:12 · `152~245.jpg`.
- 우리 도구로 하는 법: **모델에게 주는 프롬프트가 아니라 «실행자 스펙»** — AE JSX(`ae_scene`) 또는 HTML 렌더 스펙 / Codex 이미지 프롬프트 / 편집 배치표(`edit_plan`). 5-4 의 장면 스펙 틀.
- 난이도: 쉬움(형식 변경). 한비즈 적용: 모든 장면 스펙 첫 장.

### K2. 정확한 문구 목록(Required strings) + 문구 수정 시 목록도 같이 수정
- 무엇: 화면에 나올 모든 문자열을 한 목록으로 못박고(따옴표 + 띄어쓰기·문장부호 포함) 샷 본문과 일치시킨다. 강의 말 «필수 문구 목록도 함께 맞춰 줘야 합니다».
- 왜 먹히나: 모델이 문구를 «고쳐 쓰는» 성향을 차단하려는 시도 — 그러나 결과 ①에서 `?` → `,` 가 났다(3-5장) → **부탁으로는 부족**.
- 시각: 03:33–03:41 · `215.jpg`.
- 우리 도구로 하는 법: **구조로 강제** — 문자열은 렌더러(PIL/HTML 폰트)가 그리므로 틀릴 수 없고, 목록은 `EVENTS.text` / `edit_plan` 자막과 자동 대조(`rule_check` 어댑터는 `claude-motion-graphics.md` 5-5 에 이미 제안된 미구현 항목). 한글은 AI 에 맡기지 않는다(`design-paths.md` 핵심 2).
- 난이도: 쉬움(목록) · 중(대조 어댑터). 한비즈 적용: 정책자금 이름·자격 문구·CTA 가 목록의 «고정 문자열».

### K3. 모션 문법 한 줄: «선택 → 변형 → 정렬 → 출력»
- 무엇: 한 편 안의 모든 움직임을 같은 4동사로 통일(선택 박스가 단어를 둘러쌈 → 크기·모양 변형 → 기준선에 정렬 → 결과로 출력). 과장된 튕김·회전·액체 변형·파티클·강한 블러·카메라 흔들림 금지, 정착은 감속, 오버슈트는 **2~3%만**.
- 왜 먹히나: 결과 ①의 블록 연결·정사각형 수렴·기준선 합류가 모두 같은 어휘라 «한 편 같다».
- 시각: `q_A.jpg` 3.3~11.7초 · `245.jpg`.
- 우리 도구로 하는 법: 영상미 원칙(`motion-graphics.md` 6장 «시그니처 모티프 하나·등장 4~8프레임 감속·바운스 금지»)과 **거의 같다** → 오버슈트는 우리가 0(강의 2~3% 허용을 줄임). 모티프 하나를 «선택 박스(강조색 한 개)»로 정하는 식.
- 난이도: 쉬움. 한비즈 적용: 핵심 단어를 선택 박스가 둘러싸는 한 가지 모티프로 한 편 통일.

### K4. 키네틱 타이포 어휘 — 이 결과에서 실제로 본 것
- ① **커서 타자 + 선택 박스**(`q_A` 2.0~2.75초): 커서가 깜빡이며 문장이 타자되고 강조 단어에 연두 박스가 한 번 늘었다 줄어듦 ② **원형 와이프 전환**(점 → 원이 커져 다음 장면, 3.0~3.5초) ③ **음절 블록 조립**: `만드는` 이 음절 블록 단위로 한 기준선에 맞물려 쌓임(5.5~6.5초) ④ **마스크 와이프 드러남**: `흐름.` 이 왼→오 ⑤ **하프톤·번짐·잔상**(네오브루탈, `q_B`) ⑥ **획 draw-on → 형태 변환**(`Hello!` → 손, `q_C`) ⑦ **글자 폭 맞춤 몽타주**(`AI`/`DESIGN` 두 줄, `BRANDING / UI/WEB / MOTION / WORKFLOW` 네 줄 쌓기 — 줄마다 폭이 비슷).
- 우리 도구로 하는 법: ①③④ AE 텍스트 애니메이터 + 마스크 / HTML 렌더(`claude-motion-graphics.md` 5-4 제안) — `typography-remotion.md` T1~T8 과 겹침(T4 음절 캐스케이드 = ③). ②는 AE 쉐이프 원 스케일 + 트랙 매트. ⑥은 AE 패스 트림(획) — 손 엠블럼 변환은 난이도 상(획 재배열). ⑤는 쓰지 않음(한 편 한 문법).
- 난이도: ①②④ 쉬움~중 · ⑥ 상. 한비즈 적용: ① 훅 질문, ④ 핵심 문구, ② 섹션 전환 1회.

### K5. 레퍼런스 영상 → 샷·모션 표 → 스펙
- 무엇: ChatGPT 컴퓨터 유즈가 링크를 열어 스크린샷을 찍으며 색감·화면 구성·타이포 움직임·전환을 하나씩 분석해 가이드 형식으로 정리 → **hex 코드·글자 폭 비율·구간 타임코드로 환원**(3-3 ②). Newtake 의 스마트 분석은 샷별 영상 조각 + 한 줄 라벨(`S04 ／ 전체화면·고정 ／ C-체인 대각선 회전 패턴·리듬 전환`)을 자동으로 만들고, 그 조각을 영상 모델의 레퍼런스로 직접 연결한다.
- 왜 먹히나: 결과 ③이 레퍼런스와 구조·색까지 닮음. 용어를 모르는 사람이 «움직임 어휘»를 얻는 방법.
- 시각: 06:49–08:39 · 08:39–10:17 · `478.jpg` · `562.jpg` · `576.jpg`.
- 우리 도구로 하는 법: **`tools/ref_study.py` 가 이미 같은 일을 한다**(컷 · 움직임 곡선 · 소리 · 접촉 시트) + 설계자가 시트를 정독해 노트로. 강의의 «샷 라벨 한 줄 형식»은 노트 2장 표의 한 줄 라벨로 채택. **자동화 한 칸**: 레퍼런스 정독 결과 → 장면 스펙의 팔레트(hex)·비율·구간 표로 바로 옮기는 템플릿(5-4).
- 난이도: 쉬움(수작업). 한비즈 적용: 사장님이 준 레퍼런스(`techniques.md`) → 쇼츠 한 컷의 스펙.
- 주의: 강의 레퍼런스는 **타인 작품**(`Liqd` 워터마크가 조각마다 보임) — 통째 모사는 «통째 베끼기는 반려»(`design-paths.md` 8장).

### K6. 일관성 — 참조 이미지를 «프롬프트 만들 때»와 «영상 만들 때» 두 번 물린다
- 무엇: 캐릭터/제품 이미지를 ① 프롬프트 작성 모델에게(그림을 보고 묘사하도록) ② 영상 생성 노드에게(실제 모습을 고정하도록) 따로 준다. «한 번만 주면 장면마다 달라진다».
- 왜 먹히나: ⑤(안 물림)보다 ⑥(다시 물림)이 캐릭터가 더 일치(3-5장).
- 시각: 10:17–12:29 · `q_E`/`q_F`.
- 우리 도구로 하는 법: **우리 규칙과 같다** — «마스터피스 → 고정 서술문 → `view_image` 로 먼저 로드»(`ai-video.md` 5장 2·3). 강의는 이를 영상 단계까지 이어 한 번 더 확인 — 우리는 유료 영상화 직전 점검 첫 줄(시작프레임을 직접 열어 봤다)이 같은 자리.
- 난이도: 쉬움. 한비즈 적용: 마스코트·상담원 캐릭터를 쓸 때 Codex 마스터피스(`Same X from image N`).

### K7. 25그리드 연속 스토리보드(번호 붙은 한 장)
- 무엇: 참조 이미지(+ 모션 프롬프트) → **한 장에 번호 붙은 25칸**, 영상 만들기 전에 장면 순서·구도를 눈으로 확인. 영상 노드에 그리드를 참조로 주면 영상이 칸 순서대로 흘러감(⑧). 제품 이미지 한 장 + 한 줄(«프로모션 영상 스토리보드를 만들어줘»)만으로도 스토리가 있는 구성이 나옴. 강의 말: «GPT 이미지 모델로도 충분히 만들 수 있으니 크레딧을 따로 사지 않아도».
- 왜 먹히나: 이미지는 영상보다 싸고(124 vs 140~220) 한 번에 25장면을 비교할 수 있다. 영상 생성 전 «구성 확인» = 우리 확인②와 같은 기능.
- 시각: 13:14–14:42 · `842.jpg` · `862.jpg`.
- 우리 도구로 하는 법: **Codex 이미지 1장(무료)** — 칸 수는 1536×1024 에서 3×3(9칸, 칸당 약 512×341)이 현실적(25칸은 칸이 307×205 로 작아 구도 확인만 가능 — **시험 안 함**). 칸 안 한글은 쓰지 않거나(자리표시) PIL 로 얹음. 칸마다 «다 나온 모습»(SKILL 3장 4)을 그리면 곧 스토리보드.
- 난이도: 쉬움. 한비즈 적용: 15~30초 한 편의 9컷 스토리보드를 확인②에 한 장으로(5-6).

### K8. 스타일 변주 = 지시서의 «비주얼 스타일» 단락만 교체
- 무엇: 구성(샷 수·타이밍·문구)은 그대로 두고 스타일 단락(`near-black + acid lime …` → `Neo-Brutalist editorial + halftone …`)만 바꿔 같은 내용을 다른 룩으로(결과 ①→②).
- 우리 도구로 하는 법: 확인②에서 **같은 스펙 + 스타일 3안(Codex 스틸 3장)** 을 보여 드리고 하나 고르게. 사장님 «시안 추천해봐» 3안 규칙(SKILL 3장 4)과 같은 자리.
- 난이도: 쉬움. 한비즈 적용: 같은 훅 컷을 «차분한 흰 / 대비 강한 검정 / 종이 질감» 3룩 스틸로.

### K9. 사이클 반복 구조(6.7초 사이클 × 2 = 13.4초)
- 무엇: 한 사이클(빌드 → 변환 → 해체)을 완결시키고 **정확히 같은 구간을 더하기 6.700초로 반복** — 길이 확보 + 루프 쇼츠 구조.
- 우리 도구로 하는 법: AE 프리컴프 한 개를 두 번 놓으면 끝. 쇼츠 루프 엔드(마지막 프레임 = 첫 프레임) 용도 — 한비즈 쇼츠 «다시 보기» 효과는 사장님 판단(미확인).
- 난이도: 쉬움. 적용 우선순위 낮음.

### K10. 강의 자체의 설명 모션(정보 카드 반복 틀)
- 무엇: 강의 편집 자체가 «번호 + 짧은 제목(왼쪽) + 도식 카드(오른쪽)» 한 틀을 15분 반복(`01 준비된 가이드 → 프롬프트 입력 → 복사 완료`, 한글 번역 카드 + 우측 3줄 라벨 + 5분할 진행 바). 카드는 흰 바탕 · 연한 보라 · 둥근 모서리 · 그림자 약간.
- 우리 도구로 하는 법: `techniques.md` D 편집 문법(자막)과 별개. 한비즈 쇼츠는 15초대라 해설 카드 불필요 — **쓰지 않음**. 단 «진행 바 5칸(몇 번째 샷인지)»은 가로 강의용, 세로 쇼츠엔 부적합.

## 5. 설계자 관점 변형 — 영상이 «하라는 방식» → 우리 파이프라인에서는 이렇게

### 5-1. 설계자의 결론 (한 문단)
**강의가 하라는 방식 = «영상 생성 모델 한 번 호출 = 완성된 모션그래픽 컷».** 우리는 이 호출을 하지 않는다. 이유는 (1) 글자 정확도 — 프레임 근거로 `?`→`,`, `비타민`→`에터민`, `Complex`→`Corxplex`(3-5장) → 우리 광고는 정확한 글자가 필수(`design-paths.md` 핵심 2) (2) 컷 단위 반려 불가 — 사장님은 «컷 번호로 반려»하시는데 이 방식은 10~20초가 한 덩어리라 한 컷만 고치려면 전체를 다시 뽑는다(크레딧 소모 · 우리 규칙 «유료 장면당 1건» 위반 소지) (3) 비용 — 한 번에 140~220 크레딧인데 마음에 안 들면 재생성(원화 환산은 언급 없음) (4) 사실적 질감이 섞임(⑧ 책상 인물)·캐릭터 녹음(⑤)·글자 가림(⑤⑦).
**가져오는 것: 영상 모델이 아니라 «지시서를 쓰는 방식»** — 그 구조는 우리 «장면 스펙»이 되고, 렌더는 AE/HTML(결정론, 글자 정확, 알파, 컷 단위)이 한다. 영상 모델은 **현실 공간·사람 컷(T3)** 에만 쓰고, 그때도 시작프레임 후보를 Codex 로 전부 만든 뒤 확인②를 거쳐 장면당 1건.

### 5-2. 단계 대응표 — 강의 단계 → 우리 단계(workflow.md P0~P7 · 확인①②) · 유지/변경/버림
| # | 강의 단계 | 우리 단계 | 판정 | 이유 |
|---|---|---|---|---|
| 1 | ChatGPT 에 가이드(Master Version) 붙이고 «채널을 리서치한 후 프롬프트를 작성해줘» | **P1 대본·콘티(설계자 직접)** | **변경** | 판단은 설계자가 쥔다. 리서치로 «채널/브랜드 정보를 채우는» 것은 근거 없는 문구·숫자를 부를 위험(`checklist` B 6-2) → 사장님·고객 원문만 쓴다. 단, 가이드의 **«확인되지 않은 효능·수치는 만들지 않는다»** 한 줄은 그대로 유지(우리 규칙과 일치) |
| 2 | 가이드의 출력 규격: 영어 연출문 + 정확한 원문 카피 + 타임코드 + 모션/카메라/트랜지션 + Text Fidelity + End Card, 6,000~7,000자 | **P2 장면 스펙**(5-4) | **유지(형식)·변경(길이·수신자)** | 형식은 훌륭하다 — 우리 실행자(`sonnet-5`/`codex-luna`/AE JSX)가 오해 없이 읽는 «자기완결형 영어» 규칙(`design-paths.md` 2장)과 같은 결. 길이 6,000자는 모델 입력 한도 때문이라 버리고, **수신자는 영상 모델이 아니라 실행자·렌더러** |
| 3 | 영상 모델 선택(MiniMax H3), 비율·해상도·길이·수량 | P3 컷 제작 도구 선택 | **버림(모션그래픽 컷) / 유지(T3)** | 모션그래픽 = AE/HTML. T3 만 `ai-video.md` 3장 모델표(Kling 3.0 · Gemini Omni · Seedance) 그대로. 비율 9:16 는 우리 시퀀스 1080×1920 고정 |
| 4 | 생성 버튼 → 5~10분 → 결과 확인 → 마음에 안 들면 재생성 | P3 렌더 → **0.25초 프레임 시트로 설계자 검수** → P6 점검 | **변경** | «재생성 = 유료 재호출» 루프를 **«스틸에서 먼저 고친다(무료)»** 로 앞당김. 렌더 후 확인은 프레임 시트(SKILL 3장 8, 강의의 `q_*.jpg` 와 같은 방식) |
| 5 | 프롬프트 스타일 단락만 바꿔 다른 룩 생성(네오브루탈) | **확인② 시안 — 스타일 3안(Codex 스틸)** | **변경** | 영상 두 번 생성하는 대신 Codex 정지 화면 3장으로 비교(무료) → 사장님이 고른 것 하나만 움직임 |
| 6 | 레퍼런스 영상 URL → ChatGPT Work(컴퓨터 유즈) → 영상 프롬프트 | **레퍼런스 정독 노트**(`study/`) → 장면 스펙의 팔레트·비율·구간 표 | **변경** | `ref_study.py` 로 컷·움직임·소리 수치가 이미 나오고, 설계자가 시트를 정독한다. 컴퓨터 유즈가 링크를 여는 방식은 쓰지 않는다(외부 서비스에 URL 전송 · 사장님 승인 사항). 결과물의 «hex·비율·구간 표»라는 **산출물 형식**만 가져옴 |
| 7 | 스마트 분석(샷 · 모션 · 음악)으로 레퍼런스를 샷 조각 + 라벨로 분해해 영상 모델에 연결 | `ref_study.py` 컷 시트 + 노트 2장 표의 **한 줄 라벨** | **유지(라벨 형식)·버림(모델에 연결)** | 라벨 «S04 ／ 전체화면·고정 ／ 움직임 한 줄»은 우리 노트 표와 같은 정보. 레퍼런스 조각을 영상 모델에 먹이는 것은 **타인 작품 모사 위험** + 유료 |
| 8 | 캐릭터: 참조 이미지 → 프롬프트 모델 → 영상 모델에 참조 이미지 다시 | **P2 Codex 마스터피스(`Same X from image N`) + P3 AE 리그**(`bisa_need_drop.py`) | **변경** | 일관성은 «이미지 자체»가 보장해야 한다. 강의 ⑤는 프레임에서 팔다리가 녹고(`715.jpg`) 글자를 가렸다 — 우리는 동작 PNG 4~5장 + AE 널(RIG)로 사지를 움직여 형태가 변하지 않게 |
| 9 | 제품: 제품 이미지 참조 → 영상 | (한비즈: 제품 아닌 서비스) 실제 사진/로고를 AE 레이어로 | **해당 적음/변경** | 정책자금 안내에 «제품 박스»가 없다. 로고·서류 같은 실물은 **AI 가 재생성하지 않고 이미지 그대로** 얹는다(`design-paths.md` B 경로 1) — 강의 ⑧에서 제품 글자가 깨진 증거 |
| 10 | 25그리드 연속 스토리보드(이미지 모델 한 장 4K) | **확인② 스토리보드 한 장(Codex 이미지)** | **유지(아이디어)·변경(칸 수·글자)** | 구성을 영상 전에 보는 아이디어는 우리 확인②와 정확히 일치. Codex 1536×1024 에서는 9칸 권장, 글은 PIL(한글 AI 금지) |
| 11 | 스토리보드를 영상 모델의 참조로 연결해 한 번에 20초 영상 | — | **버림** | ⑧에서 글자가 깨지고 컷 반려가 불가능. 스토리보드는 «확인용»에서 끝 |
| 12 | 결과를 내려받아 편집 프로그램으로(편집은 강의 범위 밖) | **P4 조립 편집 → P5 효과음 → P6 납품(프리미어 XML + 층별 소재)** | **유지(우리 쪽이 더 넓음)** | 강의는 BGM·효과음을 지시서에 맡기지만, 우리는 예능 효과음 라이브러리 + `sfx.md` 자연 길이 규칙(생성 오디오를 쓰지 않는다) |
| — | (강의에 없음) 사장님 확인 지점 | **확인①(대본·콘티) · 확인②(시안·스토리보드)** | **추가** | 강의는 «생성 → 보고 → 마음에 들면 끝». 우리는 반려 이력이 규칙이 되는 광고라 생성 전에 두 번 확인 |

### 5-3. 유료 도구 대체 가능성 — 기능별 (돈 규칙: 이미지는 Codex 무료 먼저 · 유료 영상화는 장면당 1건)
| Newtake 기능(강의) | 비용(화면) | 우리 대체 | 품질 차이 / 위험 | 결정 |
|---|---|---|---|---|
| 프롬프트 작성 LLM(Gemini 3.1 등) | ⚡96/회 | **설계자(이 세션) 직접** — 구독 안 | 같음 | 대체 완료. 별도 호출 없음 |
| 이미지 생성 GPT Image 2 (4K 16:9) | ⚡124/장 | **Codex `image_gen`**(무료) | 최대 1536×1024(4K 아님) · 한글 글자는 둘 다 AI → 우리는 PIL 로 얹음 | 대체. 4K 불필요(쇼츠 1080×1920) |
| 25그리드 스토리보드 | ⚡124(이미지 1장) | **Codex 이미지 9칸(무료)** | 칸당 해상도 낮음, 칸 수 25 불가 | 대체 + «칸 수 9» 로 조정. **25칸 시험은 안 함** |
| 영상 모델 MiniMax H3 — **타이포·UI·캐릭터 모션그래픽** | 5s 70 / 10s 140 / 2K 10s 220 | **AE JSX(`ae_scene`·`rf3_ae`) + 클로드 디자인 B + 코드 렌더(`html_motion.py` 제안, 아직 안 만듦)** | 글자 정확(렌더러가 그림) · 알파 MOV 가능 · 컷 단위 수정 · 무료. 영상 모델의 장점은 «지시서 한 번 → 완성», 단점은 문장부호·음절 깨짐·캐릭터 녹음 | **대체. 이 방식으로 모션그래픽 컷에 유료를 쓰지 않는다** |
| 영상 모델 — **현실 공간·사람** | 같음 | 대체 불가 → 기존 규칙(Kling 3.0 등, 장면당 1건, `ai-video.md`) | — | **유지**(강의와 무관) |
| 스마트 분석(샷·모션) | 크레딧 표시 없음 | `ref_study.py` + 설계자 정독 | 속도는 사람이 느림, 정확도·판단은 사람이 위 | 대체 |
| 캐릭터 라이브러리 · 참조 일관성 | 크레딧 표시 없음 | Codex 마스터피스 + `view_image` + AE 리그 | 일관성은 이미지 쪽이 더 확실 | 대체 |
| 노드 캔버스(프롬프트·결과를 한 화면에 이음) | — | 작업기록 장면 틀 + `기록/` 파일 + 클로드 디자인 캔버스(시안 공유) | UX 편의는 Newtake 가 위, 기능은 동등 | 필요 없음 |
| 레이어 분리·요소 편집·다각도·조명(툴바) | 강의에서 안 씀 | — | **언급 없음**(쓰지 않았으니 판단 보류) | 보류 |
**총평**: Newtake 의 모션그래픽 쪽 기능 중 **우리가 돈을 내고 얻을 것은 없다.** 편의(노드 캔버스, 한 번에 완성)는 컷 단위 반려·글자 정확성이라는 우리 요구와 반대 방향이다. 시험 삼아 가입해 보는 것도 하지 않는다(CLAUDE.md 3: «시험 삼아 넣어 보지 않는다»). 사장님이 직접 요청하시면 그때 판단.

### 5-4. 우리 «장면 스펙» 틀 — 강의의 지시서를 우리 규칙으로 바꾼 것
강의 지시서 7블록(길이 / 모드·톤 / 비주얼 스타일 / 샷 / 문구 정확성 / 모션·카메라 / 사운드 / 생성 제어)을 **우리 «글자·UI·타이포 컷 스펙»** 으로 바꾼다. 수신자는 영상 모델이 아니라 **실행자(`sonnet-5`)·Codex(`codex-luna`)·렌더러(AE JSX / HTML)**. 영어 자기완결형(규칙), 수치는 «재서 채울 칸»(SKILL 6장)이 비어 있어 아래는 자리표시.
```
DURATION: <초> s · 1080x1920 · <fps ☐ SKILL 6장 재서 채울 칸>
MODE: <kinetic typography | UI/typing | title card | end card> — one motif only (예: "selection box in the accent color")
PALETTE (3 colors + hex): paper #… · ink #… · accent #… (비교 장면은 쪽마다 색 하나)
TYPE: <font file path: Pretendard Bold | Noto Sans KR VF>, word-break: keep-all, min size <☐ 휴대폰 기준>
BOXES (겹침 검사 입력): person <☐> · caption <☐> · material <☐>   # SKILL 6장
WORD-TIME TABLE (words.txt 에서, 초): w1 "…" t=… · w2 "…" t=…
SHOT TABLE: id | t_in–t_out | elements (≥0.6 s apart, 같은 종류는 묶음) | motion verb (entrance 4–8 frames ease-out, NO overshoot) | exact strings
  S1 | … | … | select → transform → align → output 중 어느 동사 | "…"
EXACT STRINGS (immutable — rendered by the font engine, never AI-drawn): "…", "…", …   # 문장부호·띄어쓰기 포함, EVENTS.text 와 자동 대조
END HOLD: last 0.85 s hold, no new elements
SOUND: role → file name (sfx.md); no generated audio
GUARDRAILS: no logos/업체명 (○○ · 010-0000-0000), no invented numbers, no template-card lists, no neon gradients, glitch ≤ once, overshoot 0
```
- **강의와 다른 점 5개**: ① 타임코드 = 박(BPM)·임의 구간이 아니라 **단어 시각**(`words.py`, SKILL 3장 2) ② 오버슈트 2~3% 허용 → **0** ③ 필수 문구 목록은 «부탁»이 아니라 **렌더러 입력 + 자동 대조** ④ BGM 120BPM 같은 사운드 지시는 버리고 **효과음 역할→파일 이름**(`sfx.md`) ⑤ 영문 몽타주 단어(FORM·TYPE·EXPLORE…)는 **쓰지 않음** — 한국어 광고에서 의미 없는 영문 장식은 말 따라 쓰기/장식 반려 위험(6장).
- **레퍼런스에서 가져올 부분(K5)**: 레퍼런스 정독 노트 → 위 틀의 `PALETTE`(hex) · `글자 폭 비율`(예: 단어가 화면 폭의 44%) · `SHOT TABLE` 구간. 강의 ③ 프롬프트의 «구간마다 한 문단(0.000–0.250 / 0.250–1.150 …)» 이 우리 SHOT TABLE 의 모양.

### 5-5. 돈 규칙에 맞춘 순서 (강의: 생성 → 마음에 안 들면 재생성 · 우리: 무료 먼저 → 확인② → 한 번)
1. **무료 단계에서 후보를 전부 본다**: Codex 한 세션에 ① 스타일 3안 스틸(같은 스펙, K8) ② 스토리보드 9칸 한 장(K7) ③ 시작프레임 후보 3안(T3 컷만) ④ 소재 사진·캐릭터 마스터피스 → 한 번에 몰아서(첫 호출 약 60초 + 장당 약 21초).
2. **확인②**: 스틸·스토리보드를 사장님께 → **고른 것만** 다음 단계.
3. **렌더(무료)**: 글자·UI·타이포는 AE/HTML, 컷마다 0.25초 프레임 시트 검수(설계자) → `rule_check`.
4. **유료는 T3(현실 공간·사람) 컷에 한해 장면당 1건** — `get_cost` → 발주 → 크레딧 누계 기록(`ai-video.md` 4·6장).
5. 강의의 «결과가 마음에 안 들면 다시 생성»은 **금지 방향**: 스틸 단계에서 끝내고, 영상 결과가 나쁘면 «원인을 하나만 바꿔» 다음 건을 사장님께 묻는다(규칙).
참고용 비용 감각(강의 화면 값): MiniMax H3 10초 140~220 크레딧 × 재시도 3회 = 420~660 크레딧 — **원화 환산은 영상에 없다**.

### 5-6. 한비즈 쇼츠 한 편에 적용한 가상 예 — 정책자금 안내 약 19초 (T2 소재 몽타주 + T3 AI 컷 1 + 타이포·카드 컷)
※ **대본·숫자는 구조 시연용 가상 문장**(사장님 원문이 정본, P1 규칙). 숫자 대신 ○○. 시각은 음절 ÷ 5.5 어림 — 실제는 단어 시각(`words.py`)으로 교체. 자막은 대본 원문, 화면 글은 말 따라 쓰기 금지(개념어).

| 컷 | 시각(어림) | 줄(가상) | 그림(길) | 강의에서 가져온 연출 → 우리 방식 | 돈 |
|---|---|---|---|---|---|
| C1 훅 | 0.0–3.3 | «정책자금, 아직도 은행에서만 찾고 계세요?»(18음절) | **코드 렌더/AE 타이포**(검정 바탕) | 샷 1 변형: 검색창 커서가 깜빡이고 **핵심어 «정책자금» 하나만** 타자 → 강조색 선택 박스가 그 단어를 한 번 둘러쌈 → 원형 와이프로 C2 로(섹션 전환 1회). 문장은 자막이 보여 주므로 화면 글은 단어 하나 | 0 |
| C2 | 3.3–5.1 | «서류가 많아 막막하셨죠?»(10) | **A Codex 사진**(책상 위 서류 더미, 사진기 톤, 사람 없음) + 느린 push-in | 강의엔 없음. T2 소재 컷 — 그냥 컷으로 연결 | 0 |
| C3 | 5.1–8.6 | «신청 자격부터 서류, 심사까지 순서가 있습니다.»(19) | **B 클로드 디자인 → `design_layers` → AE** | 샷 2 변형: 3블록 `1 자격 / 2 서류 / 3 심사` 가 **말의 단어 시각마다 하나씩(간격 ≥0.6초)** 선으로 연결(알파 255 카드, 도형 짜깁기 아님 — 글자가 주인공). 마지막에 3블록이 가운데로 모여 한 장이 되며 **크기를 맞춘 매치 컷**으로 C4 에 연결. «이미지→브랜딩→UI→영상» 같은 영문 4블록은 쓰지 않음 | 0 |
| C4 | 8.6–11.5 | «사업장 상황에 맞는 자금은 따로 있어요.»(16) | **T3 AI 영상 1건**(현실 공간: 한국 소상공인 매장, 사진기 톤) | Codex 시작프레임 후보 3안 → 확인② → **유료 1건**(예: Kling 3.0 3초, 생성 길이 = 대사 구간, 1배속). 강의와 연결 없음 — 모션그래픽이 아니라 현실 컷 | **유료 1건** |
| C5 | 11.5–14.4 | «○○ 기준으로 하나씩 확인해 드립니다.»(16) | **코드 렌더/AE 타이포** | 샷 3/4 변형: «확인» 한 단어가 음절 블록 단위로 기준선에 맞물려 쌓이고(`만드는` 같은 방식) 굵기 램프(`typography-remotion.md` T3). 영문 몽타주는 쓰지 않음 | 0 |
| C6 | 14.4–16.4 | «접수 전에 먼저 확인받으세요.»(11) | **A Codex 사진**(상담 책상, 손과 서류) | T2 소재 컷 | 0 |
| C7 엔드 | 16.4–18.85 | «지금 상담 신청하세요.»(9) | **코드 렌더/AE 엔드 카드** + 사장님 로고 파일 | 샷 5 변형: 요소들이 작아져 **한 기준선으로 모이고** 로고 + 문의 장치(010-0000-0000 자리표시)가 한 줄로 합침 → **마지막 0.85초 정지, 새 요소 없음.** CTA 는 마지막 컷 하나(중복 CTA 금지) | 0 |

**P0~P7 에서 누가 무엇을 하나**
| 단계 | 하는 일 | 누가 |
|---|---|---|
| P0 접수·범위 | 건 정보·편 유형(T2+T3)·범위 규칙(분양 규칙 적용 여부 ☐)·사용 허락 범위 기록 | 설계자 |
| P1 대본·콘티 → **확인①** | 위 표(줄 × 그림 × 한 줄 연출)를 사장님께. 대본은 사장님 원문 정본 | 설계자 |
| P2 소재·시안 → **확인②** | TTS/녹음 → 강제정렬(단어 시각) → Codex 한 세션: **타이포 스타일 3안 스틸 · C2/C6 사진 · C4 시작프레임 3안 · 스토리보드 9칸 한 장** → 사장님이 스타일 하나, 시작프레임 하나 선택 | 설계자(스펙·정렬) + `codex-luna`(이미지) |
| P3 컷 제작 | C1·C3·C5·C7 = 장면 스펙(5-4) → AE JSX/HTML 작성은 `sonnet-5`, 설계자가 0.25초 프레임 시트로 검수 · C4 = `get_cost` → 유료 1건 | `sonnet-5` + 설계자 / C4 설계자 직접 |
| P4 조립 | `edit_plan` 배치표 → `edit_render` 미리보기 → `edit_xml` | 설계자 |
| P5 효과음 | 선택 박스 둘러싸는 틱·타자음·블록 정착음 등 역할 → 파일 이름 고정, `rule_check.check_sfx` | 설계자 |
| P6 점검·납품 | 점검표 B+C, 프레임 시트, 납품 폴더 열기 | 설계자 |
| P7 피드백 | 반려는 컷 번호로 → 해당 컷 스펙만 고쳐 같은 이름에 덮어씀 | 설계자 |
- 강의 대비 이득: 반려가 **컷 단위**로 가능(영상 전체 재생성 아님), 글자는 **틀릴 수 없음**(렌더러), 유료는 **0~1건**.
- 이 예의 한계: 정책자금 안내에서 실제로 «타이포 컷이 4개나 필요한지»는 사장님 방향이 정한다(T2 소재 위주면 C1·C7 만 남을 수 있음). C3 의 3블록은 «템플릿 같은 카드 나열»(금지 목록) 위험 — 시안(확인②)에서 글자 디자인으로 통과해야 한다.

### 5-7. 규칙·점검표 후보 (제안 — 설계자 결정 대기, **다른 문서는 이번에 수정하지 않았다**)
| 번호 | 규칙 한 줄(후보) | 점검표 한 줄(후보) | 기계 점검 |
|---|---|---|---|
| N1 | 글자·UI·타이포가 주인공인 컷은 **영상 생성 모델에 맡기지 않는다**(렌더러 폰트) — 강의 결과 ①②⑥⑧에서 문장부호·음절·철자가 깨짐 | «모션그래픽 컷의 글자가 렌더러(폰트)에서 나왔다 · 생성 모델이 그린 글자 없음» | — |
| N2 | 장면 스펙에 **EXACT STRINGS 목록**을 두고 `EVENTS.text`/`edit_plan` 자막과 대조 | «화면 글 목록 = 자막/스펙 목록(문장부호·띄어쓰기 포함)» | `rule_check` 어댑터(미구현, `claude-motion-graphics.md` 5-5 와 같은 항목) |
| N3 | 레퍼런스는 **짚은 요소(팔레트·비율·구간)만** 스펙으로 옮긴다 — 타인 작품 통째 모사·모델 입력 금지 | «레퍼런스 출처·요소 기록 · 통째 모사 아님» | — |
| N4 | 확인②의 스토리보드는 **Codex 한 장(칸 9)**, 영상 모델에 참조로 주지 않는다 | «스토리보드 한 장을 확인② 에서 보여 드렸다» | — |
| N5 | 캐릭터·제품은 **이미지 자체**(마스터피스/실제 사진)로 고정하고 영상 모델에 맡기지 않는다 | 기존 «영상화 직전 점검» 첫 줄과 병합 가능 | — |
| N6 | 텍스트가 캐릭터·제품 뒤로 **가려지지 않게**(겹침 검사) | 기존 «겹침 검사» 줄(`check_boxes`)에 «글자 가림» 추가 | `ae_scene.check_boxes` 입력 |

## 6. 우리 규칙과 부딪히는 것 (SKILL 4장 · checklist) — 그대로 쓰면 반려될 것
| 강의가 한 것 | 부딪히는 규칙 | 처리 |
|---|---|---|
| **글자·로고를 영상 생성 모델이 그림**(한글·영문 모두) | `design-paths.md` 핵심 2 «한글은 어떤 경우에도 AI 에 맡기지 않는다» · 규칙 4-1 «글자는 대사 원문 그대로» | 쓰지 않음. 프레임 증거: `나요,` · `에터민B` · `Corxplex`(3-5장) |
| 라임·시안·보라 포인트, 라임·시안 그라디언트 계열 | 영상미 «3색·핵심어 하나만 강조» · 금지 목록(무지개/네온 그라디언트) | 스펙의 PALETTE 3색. 강의 ① 팔레트(near-black + warm-white + acid lime + cyan + violet)는 5색이라 부적합 |
| 영문 대문자 몽타주(`FORM·TYPE·MOTION…`) 영어 장식 위주, «한글 최소» | 한국어 쇼츠 광고 · 규칙 «말 따라 쓰기 금지·개념어» · 장식 아이콘 반려 | 쓰지 않음. 한글 개념어 1~2단어로 |
| 오버슈트 2~3% 허용, `quick overshoots`, 탄성 지연 | 영상미 3 «등장 4~8프레임 감속, 바운스 금지» | **0 으로 강화**(`claude-motion-graphics.md` 와 같은 결정) |
| 샷 간격이 짧고 연속(0.2~1.3초대 샷 전환, 5단어 몽타주 0.4~0.5초 간격) | 인지 텀 0.6초 · 새 요소 혼자 0.6초 | **한글은 영문보다 읽는 시간이 길다** — 몽타주 속도는 쓰지 않고 단어 시각에 걸기 |
| **한 번에 10~20초 영상을 뽑고 마음에 안 들면 재생성(크레딧)** | CLAUDE.md 3 «유료 생성은 장면당 한 건·시험 삼아 넣지 않는다» · 반려는 컷 번호로 | 스틸에서 끝내고 모션그래픽은 렌더. 유료 영상은 T3 1건 |
| 스마트 분석·ChatGPT 컴퓨터 유즈로 **타인 영상(Pinterest·`Liqd` 워터마크)을 모사** | `design-paths.md` 8장 «통째 베끼기는 반려» · 저작권 | 레퍼런스는 «짚은 요소»만(N3). 컴퓨터 유즈로 외부 사이트를 여는 방식은 쓰지 않음 |
| 캐릭터 몸이 큰 글자를 가림, 제품이 `LEMON ICED TEA` 를 가림 | 겹침 검사(요소끼리·글자) · 가독성 | `check_boxes` 로 렌더 전 멈춤 |
| 제품 박스·실제 브랜드 로고(MYPROTEIN · 바로채움)를 영상 안에 | CLAUDE.md 4 «업체명·로고 실자료 금지» (한비즈 고객 자료는 ○○) | 쓰지 않음. 한비즈 로고 파일만(받아야 함) |
| 스토리보드 25칸 한글 카피를 이미지 모델이 직접 | 한글 AI 금지 | 칸 글자는 자리표시/PIL |
| 사운드를 모델에 지시(BGM 120BPM, 키보드 클릭·스와이프) | `sfx.md`(역할→파일 이름·자연 길이·크기표) · 청음본 요청 금지 | 생성 오디오는 쓰지 않음, 효과음은 라이브러리 |
| 영상·이미지 노드에 **«AI» 배지** 표시(결과 썸네일) | — | 납품물에 AI 생성 표시가 필요한지는 **미확인**(사장님/고객 판단 사항) |
| 한 번에 이어 붙인 20초 컷 안에 장면별 질감이 달라짐(⑧ 실사 인물 ↔ 2D 제품) | 영상미 «시그니처 모티프 하나·질감 통일» · `ai-video.md` 0 «질감이 영상에 그대로 간다» | 한 편에 질감 하나 |

## 7. 못 본 것 · 불확실
- **소리는 귀로 못 들었다**(자막의 [음악] 표기와 수치만). 생성된 영상에 오디오가 붙었는지, 강의 BGM 이 어떤 곡인지 모른다.
- **가이드 프롬프트 «Master Version» 전체**: 영상엔 앞 6문단 + ChatGPT 답변뿐(설명란의 드라이브 파일은 받지 않음, 외부 링크). 우리 5-4 틀은 영상에 보인 **출력 결과의 구조**에서 역산한 것이고, 가이드 원문이 같은 구조라는 보장은 없다.
- **프롬프트 일부는 못 읽음**: 네오브루탈 변주 프롬프트의 뒷부분(샷 02 이후), 캐릭터 프롬프트 ⑤의 샷 구성, 제품 프롬프트 2건의 샷 본문(노드 안 작은 글씨·접힘). 따라서 ②의 영단어 몽타주가 «지시에 있었는지»는 확인 못 함.
- **어느 모델로 만든 결과인지**: 방법 ① 결과는 MiniMax H3 로 시연했고(04:52·화면), ⑤~⑧ 영상의 모델 표시는 화면 하단 작은 글씨(`MiniMax H3 …`)로만 보인다. ⑧ 25그리드 영상 노드는 모델 표시를 읽지 못함.
- **강의 편집으로 결과를 골랐는지**: 몇 번 생성했는지 모른다. 보여 준 결과가 «여러 번 중 최선»일 가능성(선택 편향) — 그래서 오히려 우리 판정(3-5장)의 문제점은 **최선 결과에서도 나온 것**이다.
- **Newtake 정체·요금**: 영상엔 «AI 영상 생성 플랫폼»까지만. 웹 검색으론 LiblibAI 해외판 LibTV 계열이라는 중국어 사이트 한 곳 설명뿐([ai-bot.cn/newtake](https://ai-bot.cn/newtake/) 등 — **공식 확인 아님**). 크레딧의 원화 환산·구독료·무료 크레딧은 **언급 없음 / 확인 못 함**.
- **영상 길이 슬라이더 범위·해상도 선택지 전부**(768P/2K 말고 더 있는지)는 팝업에 안 보임. 9:16 결과물은 강의에 없음.
- **스마트 분석 라벨 `SD 2.5`** 가 무엇인지(모델명? 비용 등급?) 모름.
- 0.25초 시트로는 **0.1초 단위 전환·오버슈트(2~3%)** 를 못 봤다. 정착 감속이 우리 «4~8프레임 감속»과 같은지 미확인.
- K9(사이클 반복) · K7(Codex 9칸 그리드)·5-6 가상 예는 **설계안이며 만들어 시험하지 않았다**(사장님 반응 없음 — 통과로 읽지 않는다). Codex 로 9칸 그리드의 구도 확인 품질이 충분한지는 **미검증**.
- 세로 쇼츠 안전영역·글자 최소 크기·자막 위치·fps 는 SKILL 6장 ☐ — 5-4 틀의 해당 칸은 자리표시.
- 한비즈 로고 파일·브랜드색·글꼴은 이 저장소에 없다 → C7 엔드 카드는 자리표시.
