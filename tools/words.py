# -*- coding: utf-8 -*-
r"""사장님 컷 조각을 이어 붙인 말에서 «단어가 나오는 시퀀스 시각» 을 뽑는다 (faster-whisper).

[새로 만든 도구 — 원본은 D:/영상제작/_tmp/w17/mk.py 같은 일회성 스크립트(조각 이어 붙이기 → medium CPU int8 → 단어 시각)를 함수로 뺀 것]

모든 움직임은 «그 말이 나오는 단어 시각» 에 건다(워크플로우 1단계). 받아쓴 글자는 시각용일 뿐 자막 글이 아니다(자막은 사장님 타임라인·대본 원문).
받아쓰기 오인식은 그대로 두지 말고 기록에 «뒷광고는 = 다른 광고는» 처럼 적어 둔다.

    python words.py --src 사람영상.mp4 --seg 1477.76,1482.982,2381.145 --seg 1482.982,1484.066,2386.818 --out _tmp/w17/words.txt
        --seg 시퀀스시작,시퀀스끝,원본영상 안 시작초   (사장님 컷 조각마다 한 번씩, 시퀀스 순서대로)

    import words
    ws = words.word_times([(1477.76, 1482.982, 2381.145), …], "사람영상.mp4")   # → [(시퀀스 초, 단어), …]

말 시작 당기기 (이식본 — 원본 D:/영상제작/도구/광고편집/sg_sync.py 의 env_db·onset·word_t 에서 건 전용(CAPS·STT 경로)을 뺀 것)
    env = words.env_db("목소리.wav")                         # 목소리 10ms 창 RMS(dB)
    t0 = words.speech_onset(env, t=받아쓰기_시각, prev_end=앞_단어_끝)    # 실제 발음 시작(−28dB 쉼의 끝)
    cap = words.caption_t(env, t, prev_end)                  # 자막은 말 시작보다 0.05초 앞세운다 (editing-premiere 5-3)

환경: GPU 에 cublas 가 없는 PC 라 device="cpu", compute_type="int8", 모델 medium 이 기본(10-07 실측으로 돌아가던 설정).
조각 사이가 시퀀스에서 떨어져 있어도(컷 사이 공백) 조각별로 시각을 되돌려 놓는다.
"""
import argparse
import subprocess
from pathlib import Path

import numpy as np


def _load16k(src, ss, dur):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ss}", "-t", f"{dur}", "-i", str(src), "-vn",
                          "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def word_times(segs, src, model="medium", device="cpu", compute_type="int8", language="ko"):
    """segs = [(시퀀스 시작초, 시퀀스 끝초, src 안 시작초), …] → [(시퀀스 초, 단어), …]"""
    from faster_whisper import WhisperModel          # 무거워서 쓸 때만 불러온다
    parts, offs, acc = [], [], 0
    for ta, tb, cs in segs:
        x = _load16k(src, cs, tb - ta)
        n = int(round((tb - ta) * 16000))
        x = np.pad(x, (0, max(0, n - len(x))))[:n]
        parts.append(x)
        offs.append((acc / 16000.0, ta, tb - ta))     # (이어 붙인 소리 안 시작초, 시퀀스 시작초, 길이)
        acc += n
    audio = np.concatenate(parts)
    m = WhisperModel(model, device=device, compute_type=compute_type)
    seg, _ = m.transcribe(audio, language=language, word_timestamps=True)
    out = []
    for s in seg:
        for w in s.words or []:
            p = w.start
            for c0, ta, ln in reversed(offs):
                if p >= c0:
                    out.append((round(ta + min(p - c0, ln), 3), w.word.strip()))
                    break
    return out


ONSET_LOW_DB = -28.0       # 이 아래가 «쉼» (sg_sync.onset 기본값)
CAP_LEAD = 0.05            # 자막은 말 시작보다 이만큼 먼저 (sg_sync: 줄 시작 = 첫 글자 − 0.05초)
_ENV = {}


def env_db(voice):
    """목소리 파일 → 10ms 창 RMS(dB) 배열 (16kHz 모노, 인덱스 i = i/100 초). 같은 파일은 한 번만 읽는다."""
    key = str(voice)
    if key not in _ENV:
        x = _load16k(voice, 0, 36000)
        n = len(x) // 160
        fr = x[:n * 160].reshape(n, 160)
        _ENV[key] = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-6)
    return _ENV[key]


def speech_onset(env, t, prev_end=None, low=ONSET_LOW_DB):
    """실제 발음 시작. 앞 단어가 끝난 뒤(받아쓰기 끝 −0.15초부터) 처음 나오는 쉼(low 아래 20ms 이상)의 끝.
    쉼이 여럿이면 받아쓰기 시각 t 에 가장 가까운 것. 쉼이 없으면(붙여 말함) t 근처 가장 낮은 곳 뒤 6dB 오르는 곳. 못 찾으면 t 그대로.
    prev_end 가 없으면 t − 0.5초 부터 본다."""
    if prev_end is None:
        prev_end = t - 0.5 + 0.15
    i0, i1 = max(0, int((prev_end - 0.15) * 100)), min(len(env) - 1, int((t + 0.10) * 100))
    st, ends = None, []
    for i in range(i0, i1 + 1):
        if env[i] < low:
            st = i if st is None else st
        else:
            if st is not None and i - st >= 2:
                ends.append(i / 100)
            st = None
    if ends:
        return min(ends, key=lambda x: abs(x - t))
    a, b = max(0, int((t - 0.20) * 100)), min(len(env) - 1, int((t + 0.05) * 100))
    if b <= a:
        return t
    w = env[a:b + 1]
    m = int(np.argmin(w))
    for i in range(m, len(w)):
        if w[i] >= w[m] + 6:
            return (a + i) / 100
    return t


def caption_t(env, t, prev_end=None):
    """자막 시작 시각 = 말 시작(speech_onset) − CAP_LEAD."""
    return max(0.0, speech_onset(env, t, prev_end) - CAP_LEAD)


def main():
    ap = argparse.ArgumentParser(description="컷 조각대로 이어 붙인 말에서 단어 시각(시퀀스 초) 뽑기")
    ap.add_argument("--src", required=True)
    ap.add_argument("--seg", action="append", required=True, help="시퀀스시작,시퀀스끝,원본안시작초")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="medium")
    a = ap.parse_args()
    segs = [tuple(float(v) for v in s.split(",")) for s in a.seg]
    ws = word_times(segs, a.src, model=a.model)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(f"{t:.2f} {w}" for t, w in ws) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(ws)}단어 → {a.out}")


if __name__ == "__main__":
    main()
