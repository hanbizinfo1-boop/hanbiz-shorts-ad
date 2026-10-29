# 2D 캐릭터 (3안 9판 «밧줄 타고 올라오는» 장면)
- `climb_a_key.png` — Codex image_gen(무료) 남색 정장·주황 넥타이 마스코트, 배경 투명. `climb_b_key.png` = A 좌우 반전(번갈아 4프레임마다 → 오르는 동작).
- 처음 프롬프트(«밧줄을 타는 사람»)는 이미지 생성기가 «self-harm» 으로 막았다 → 밧줄은 코드로 그리고 캐릭터는 «손을 뻗어 오르는 자세»만 생성. 프롬프트 `_tmp/codex/climber_prompt.md`.
- 주의: Codex 가 이미지 후처리를 하려고 `convert` 를 찾다가 이 PC 의 `C:\Windows\system32\convert.exe`(디스크 변환 도구)를 잡았다 — 설계자가 중단. 다음부터 프롬프트에 «이미지 후처리 명령 금지»를 넣는다.
