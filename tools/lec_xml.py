# -*- coding: utf-8 -*-
r"""[한비즈 쇼츠 이식본 — 원본 D:/영상제작/도구/강의편집/lec_xml.py. 바꾼 것: 시퀀스 크기(SEQ_W/SEQ_H)를 바꿀 수 있게, fps 30 추가]

«얹을 것만» XML — 장면 영상은 V_TRACK, 효과음은 A_TRACK 부터 (강의 때 사장님 09-30 «다음부터 영상은 V3 음성은 A2»).

XML을 프리미어로 불러오면 트랙 번호가 그대로 살아 있어서, 복사해 사장님 시퀀스에 붙일 때 그 트랙 자리에 바로 앉는다.
앞쪽 빈 트랙은 자리만 잡는다. 효과음이 겹치면 다음 트랙으로 넘친다.

    import lec_xml
    lec_xml.SEQ_W, lec_xml.SEQ_H = 1080, 1920          # 세로 쇼츠 (기본값은 가로 1920×1080)
    lec_xml.V_TRACK, lec_xml.A_TRACK = 3, 2
    lec_xml.write(out_xml, seq_name, mov, dur_s, t0_s, sfx=[(시각초, wav경로), …], fps=29.97)

fps 는 59.94 · 29.97 · 30 을 다룬다. 시퀀스 fps 는 사장님 프로젝트에서 확인한 값을 쓴다(틀리면 시각이 어긋난다).
"""
import subprocess
from pathlib import Path

V_TRACK, A_TRACK = 3, 2
SEQ_W, SEQ_H = 1920, 1080


def url(p):
    # 10-14 사장님 «xml 넣었는데 파일을 찾을 수 없다고 뜨네» — --out 을 상대 경로로 주면 «file://localhost/납품/…» 처럼 드라이브가 빠져 프리미어가 못 찾았다
    #   → 항상 절대 경로 + 프리미어가 내보내는 모양(file://localhost/C%3a/…, 한글은 UTF-8 퍼센트 인코딩)
    from pathlib import Path as _P
    from urllib.parse import quote as _q
    s = str(_P(p).resolve()).replace("\\", "/")
    return "file://localhost/" + _q(s, safe="/")


def rate_of(fps):
    """(timebase, ntsc 문자열, 프레임 변환 함수)."""
    if abs(fps - 59.94) < 0.01:
        return 60, "TRUE", lambda t: int(round(t * 60000 / 1001))
    if abs(fps - 29.97) < 0.01:
        return 30, "TRUE", lambda t: int(round(t * 30000 / 1001))
    if abs(fps - 30) < 0.01:
        return 30, "FALSE", lambda t: int(round(t * 30))
    raise ValueError(f"시퀀스 fps {fps} 는 아직 안 다룬다")


def write(out_xml, seq_name, mov, dur_s, t0_s, sfx, fps, tag="c"):
    tb, ntsc, fr = rate_of(fps)
    RATE = f"<rate><timebase>{tb}</timebase><ntsc>{ntsc}</ntsc></rate>"
    mov = Path(mov)
    n_mov = fr(dur_s)
    s0 = fr(t0_s)
    vclip = (f'<clipitem id="v-{tag}"><name>{mov.name}</name><enabled>TRUE</enabled>{RATE}<start>{s0}</start><end>{s0 + n_mov}</end>'
             f'<in>0</in><out>{n_mov}</out><file id="f-{tag}"><name>{mov.name}</name><pathurl>{url(mov)}</pathurl>{RATE}<duration>{n_mov}</duration>'
             f'<media><video><samplecharacteristics><width>{SEQ_W}</width><height>{SEQ_H}</height></samplecharacteristics></video></media></file></clipitem>')
    items = []
    for k, (t, f) in enumerate(sorted(sfx, key=lambda x: x[0])):
        f = Path(f)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                   capture_output=True, text=True).stdout)
        n = max(1, fr(dur))
        st = fr(t)
        items.append((t, t + dur, f'<clipitem id="a-{tag}-{k}"><name>{f.name}</name><enabled>TRUE</enabled>{RATE}<start>{st}</start><end>{st + n}</end><in>0</in><out>{n}</out>'
                                  f'<file id="fa-{tag}-{k}"><name>{f.name}</name><pathurl>{url(f)}</pathurl>{RATE}<duration>{n}</duration><media><audio><channelcount>2</channelcount></audio></media></file>'
                                  '<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack></clipitem>'))
    tracks, ends = [], []                     # 겹치면 다음 트랙으로
    for t, e, it in items:
        for i, last in enumerate(ends):
            if last <= t:
                tracks[i].append(it)
                ends[i] = e
                break
        else:
            tracks.append([it])
            ends.append(e)
    empty = "<track><enabled>TRUE</enabled></track>"
    video = empty * (V_TRACK - 1) + f"<track>{vclip}<enabled>TRUE</enabled></track>"
    audio = empty * (A_TRACK - 1) + "".join(f"<track>{''.join(t)}<enabled>TRUE</enabled></track>" for t in tracks)
    end = s0 + n_mov + 2 * tb
    x = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="4"><sequence id="seq-' + tag + f'"><name>{seq_name}</name>'
         f"<duration>{end}</duration>{RATE}<media><video><format><samplecharacteristics>{RATE}<width>{SEQ_W}</width><height>{SEQ_H}</height>"
         f"<pixelaspectratio>square</pixelaspectratio></samplecharacteristics></format>{video}</video>"
         f"<audio>{audio}</audio></media></sequence></xmeml>\n")
    out_xml = Path(out_xml)
    out_xml.write_text(x, encoding="utf-8", newline="\n")
    return out_xml, [f"A{A_TRACK + i}" for i in range(len(tracks))]
