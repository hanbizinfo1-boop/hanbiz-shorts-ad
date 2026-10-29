"""효과음 배치 점검 — 낱개 wav 를 실제로 읽어 «겹침»과 «밀림»을 잰다.

- 겹침: 앞 효과음의 들리는 꼬리(피크 대비 −30dB 위)가 다음 효과음의 어택(피크 대비 −20dB 첫 도달)과 겹치는 길이
- 밀림: 큐가 의도한 시각(align=onset 이면 어택, peak 면 피크)과 실제로 들리는 어택/피크의 차이(+ 면 늦음)

python tools/sfx_audit.py --place 납품/효과음준비_1012/3안_소리미리듣기_낱개/_배치.json --cue 기록/효과음큐_3안_1012.json
"""
import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf


def env_db(x, sr, win=0.005):
    if x.ndim > 1:
        x = np.abs(x).max(axis=1)
    else:
        x = np.abs(x)
    n = max(1, int(sr * win))
    m = len(x) // n
    e = x[:m * n].reshape(m, n).max(axis=1)
    return 20 * np.log10(e + 1e-9), win


def measure(path):
    x, sr = sf.read(str(path), always_2d=False)
    e, w = env_db(x, sr)
    pk = e.max()
    ipk = int(e.argmax())
    m = np.abs(x).max(axis=1) if x.ndim > 1 else np.abs(x)        # 피크는 20ms RMS 로(리미터에 깎인 꼭대기 흔들림 방지)
    n2 = int(sr * 0.02); k2 = len(m) // n2
    pk_t = (float(np.sqrt((m[:k2 * n2].reshape(k2, n2) ** 2).mean(axis=1)).argmax()) + 0.5) * 0.02 if k2 else ipk * w
    att = int(np.argmax(e >= pk - 20))
    aud = np.where(e >= pk - 30)[0]
    return dict(attack=att * w, peak=pk_t, end=(aud[-1] + 1) * w if len(aud) else 0, pk_db=float(pk))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--place', required=True)
    ap.add_argument('--cue', required=True)
    ap.add_argument('--overlap-ms', type=float, default=20)
    ap.add_argument('--late-ms', type=float, default=34)
    a = ap.parse_args()
    place = json.load(open(a.place, encoding='utf-8'))
    cues = json.load(open(a.cue, encoding='utf-8'))['cues']
    base = Path(a.place).parent
    rows = []
    for s in place['sfx']:
        m = measure(base / s['file'])
        rows.append(dict(file=s['file'], role=s['role'], start=s['start'], t=s.get('t'), align=s.get('align'), a=s['start'] + m['attack'],
                         p=s['start'] + m['peak'], e=s['start'] + m['end'], db=m['pk_db']))
    rows.sort(key=lambda r: r['a'])
    # 큐 대응: 번호 순서 = 큐 순서(시각 정렬)
    cs = sorted([c for c in cues if c['role'] != 'logo_ending'], key=lambda c: c['t'])
    bad = 0
    print(f"{'시각':>7} {'역할':<12} {'어택':>7} {'피크':>7} {'끝':>7} {'밀림ms':>7} {'겹침ms':>7}  파일")
    for i, r in enumerate(rows):
        if r['t'] is not None and r['role'] != 'logo_ending':      # 배치표에 큐 시각이 있으면 그걸 쓴다
            c = dict(t=r['t'], align=r['align'])
        else:
            cand = [c for c in cs if c['role'] == r['role'] and abs(c['t'] - r['start']) < 0.6]
            c = min(cand, key=lambda c: abs(c['t'] - r['start'])) if cand else None
        late = None
        if c:
            ref = r['p'] if c.get('align') == 'peak' else r['a']
            late = (ref - c['t']) * 1000
        ov = 0.0
        if i + 1 < len(rows) and not (r['role'] == rows[i + 1]['role'] == 'logo_ending'):   # 레이저 엔딩은 승인된 겹친 설계
            ov = max(0.0, (r['e'] - rows[i + 1]['a']) * 1000)
        flag = ''
        if late is not None and abs(late) > a.late_ms:
            flag += ' ◀밀림'
        if ov > a.overlap_ms:
            flag += ' ◀겹침'
        bad += bool(flag)
        print(f"{r['start']:7.3f} {r['role']:<12} {r['a']:7.3f} {r['p']:7.3f} {r['e']:7.3f} "
              f"{'' if late is None else f'{late:+7.0f}':>7} {ov:7.0f}  {r['file']}{flag}")
    print(f"\n문제 {bad}건 (밀림 > ±{a.late_ms:.0f}ms · 겹침 > {a.overlap_ms:.0f}ms)")


if __name__ == '__main__':
    main()
