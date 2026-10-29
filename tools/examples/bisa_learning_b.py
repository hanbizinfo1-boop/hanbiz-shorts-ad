# -*- coding: utf-8 -*-
# ★ 본보기(원본 경로 상수 그대로) — 실행을 보장하지 않는다. 베껴 쓰지 말고 «이런 식으로 짠다»를 본다.
# 보여 주는 것: B 경로: 클로드 디자인 캔버스 → design_layers 레이어 PNG → 애펙 keys() 로 움직임만 거는 법 + 마스코트 인형 연출
# 원본: D:/영상제작/도구/광고편집/bisa_learning_b.py (통과/반려 이력은 references/feedback-log.md)
# 모듈 대응: bisa_web_vs_instant → ae_scene · bisa_meta_sfx / bisa_toc_cards.by_name → sfx · rf3_ae·rule_check·lec_xml·design_layers → tools/ 같은 이름.
# 이 폴더에 없는 모듈(bisa_ab_setup 1판, bisa_toc_cards 노트 틀 등)을 import 하는 줄은 원본을 읽어 대응한다.
r"""빡이사DB 본편 16 «광고 계정도 학습을 해요 ~ 돈을 천 원 쓸 거를 한 만 원을 더 써야 한다 라고만» (시퀀스 1367.182~1388.40)
— B 경로(클로드 디자인 캔버스 → 레이어 → 애펙) + 11 의 «Meta» 인형(광고 계정 = 인형)이 공부하고, DB 가 쌓이면 «아하 · 오케이»,
빡빡한 퍼널이면 학습 막대가 거의 안 참 → 천 원 쓸 걸 만 원. 사장님 10-07 «클로드 디자인으로 상호작용하는 느낌».

  python bisa_learning_b.py [--소리만]
    캔버스: (캔버스 링크 생략) (Main.dc.html = 레이어 모음, 비공개)
    레이어: design_layers.py <Main.dc.html> _tmp\빡이사\ds16\L --자산 _tmp\빡이사\ds16\자산.json
    이미지: 빡이사DB\소재\16\ (Codex 3D 장난감 — 공부·OK 인형, 좁은 퍼널, 동전) + 11b 아하 인형
    → 빡이사DB\납품\16_계정학습_1367.18~.mp4 (V1 1388.40 은 클립 가운데 — 잘라서) · _효과음.xml · _미리보기.mp4
앞뒤 맥락(기록.md 16)
  앞 1358.96 «빡이사님은 허수 DB 뽑는 것만 알려 주시는 분 아니야 · 처음 돌리시는 분들이잖아요»
  뒤 1388.42 «라고만 이해하시면 · 제 말 안 믿기시면 이렇게 세팅하셔도 · 더 많은 제출 수 권장»
흐름(시퀀스 초, 단어 시각)
  1367.18 판 · 인형이 떨어져 착지(책 읽는 동작) · 1368.24 «학습을» 제목
  1369.44 «어느 정도» «DB·데이터가 쌓이면» · 1369.88 «DB가» DB 카드 셋 · 1370.38 «쌓이고» 셋 더 · 1370.68 «데이터가» 학습 막대가 참
  1372.42 «아하» 인형 «아하» + 말풍선 «아하, 이 광고주는 이런 사람 좋아하는구나»
  1375.32 «오케이» 인형 OK + «오케이!» · 1376.30 «알아서» «알아서 잘 찾아가요»
  1378.48 «근데» DB 카드·막대가 비워짐, 인형은 다시 책 · 1378.70 «아무런» «학습 데이터 없이 퍼널을 빡빡하게 하면»
  1380.80 «애초부터» 좁은 퍼널이 떨어짐 → 1381.88 «빡빡하게» 꽉 조여짐 · 1383.18 «학습이» 막대가 아주 조금만(빨강) + «학습이 너무 더뎌요»
  1385.86 «1000원» 동전 조금 «천 원» · 1386.64 «한 만 원» → 동전 많이 «만 원» · 1387.90 판이 빠짐
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import rf3_ae as AE  # noqa: E402
import design_layers as DL  # noqa: E402
import ae_scene as M  # noqa: E402  (본보기: 원본 bisa_web_vs_instant 의 틀 → ae_scene)

M.T0, M.T1 = 1367.182, 1388.40
M.DUR = M.T1 - M.T0
# 사장님 컷(10-07 16:19 저장본): (시퀀스 시작, 끝, V1 녹화 원본 시작, V2·A1 사람 원본 시작)
M.SEGS = [(1367.182, 1369.235, 2220.835, 2222.504), (1369.235, 1372.371, 2223.037, 2224.706), (1372.371, 1378.46, 2226.925, 2228.593), (1378.46, 1380.763, 2233.331, 2234.999), (1380.763, 1382.948, 2235.8, 2237.469), (1382.948, 1384.583, 2238.119, 2239.788), (1384.583, 1385.167, 2239.988, 2241.673), (1385.167, 1385.851, 2240.722, 2242.407), (1385.851, 1388.4, 2242.373, 2244.058)]
M.NAME = "16_계정학습"
M.SFX_DIR = Path(r"D:\영상제작\빡이사DB\소재\효과음16")
M.WORK = Path(r"D:\영상제작\_tmp\빡이사\ae16")
LAYERS = Path(r"D:\영상제작\_tmp\빡이사\ds16\L")
T0, T1 = M.T0, M.T1
T_IN, T_OUT = 1367.182, 1387.90
T_DROP, T_TITLE, T_S1 = 1367.45, 1368.24, 1369.44
T_DB1, T_DB2, T_LEARN = 1369.88, 1370.38, 1370.68
T_AHA, T_OK, T_S2 = 1372.42, 1375.32, 1376.30
T_RESET, T_S3, T_FUN, T_SQZ = 1378.48, 1378.70, 1380.80, 1381.88          # 퍼널은 «애초부터»에 떨어짐(빈 구간 메움)
T_SLOW, T_COIN_S, T_COIN_B = 1383.18, 1385.86, 1386.64


def jsx(out_mov):
    js = AE.js
    s = lambda t: round(t - T0, 4)                         # noqa: E731
    L = ["function eo(p){ for(var k=1;k<=p.numKeys;k++){ var n=p.isSpatial?1:(p.value.length||1), o=[], i=[]; for(var j=0;j<n;j++){ o.push(new KeyframeEase(0,0.1)); i.push(new KeyframeEase(0,85)); } p.setTemporalEaseAtKey(k,i,o); } }",
         f"(function(){{ var comp=app.project.items.addComp('bisa16',{M.W},{M.H},1,{M.DUR:.3f},{M.FPS});"]
    a = L.append
    a(f"var iv=imp({js(str(M.REC))});")
    for i, (ta, tb, rs, _) in enumerate(M.SEGS):
        a(f"var R{i}=comp.layers.add(iv); R{i}.startTime={s(ta) - rs:.4f}; R{i}.inPoint={s(ta):.4f}; R{i}.outPoint={s(tb):.4f};")
    a("var RIG=comp.layers.addNull(); RIG.name='RIG'; RIG.enabled=false; RIG.transform.position.setValue([0,0]);")
    a(f"keys(RIG.transform.position,[[{s(T_IN)},[{M.W},0]],[{s(T_IN) + 0.45:.3f},[0,0]],[{s(T_OUT)},[0,0]],[{s(T_OUT) + 0.45:.3f},[{-M.W},0]]]); eo(RIG.transform.position);")
    lines, var, meta = DL.ae_lines(LAYERS, js)
    L.extend(lines)
    box = {x["name"]: x["bbox"] for x in meta["layers"]}
    slide = "value+[thisComp.layer('RIG').transform.position[0],0]"
    a(f"L_base.transform.position.expression=\"{slide}\";")
    for n in var:                                           # 모든 레이어: 판과 같이 밀림 + 처음엔 숨김(아래에서 켬)
        a(f"{var[n]}.transform.position.expression=\"{slide}\"; {var[n]}.transform.opacity.setValue(0);")

    def c(n):
        x0, y0, x1, y1 = box[n]
        return (x0 + x1) / 2, (y0 + y1) / 2

    def life(n, t_in, t_out=T_OUT, fi=0.25, fo=0.25):
        a(f"keys({var[n]}.transform.opacity,[[{max(0, s(t_in) - 0.001)},0],[{s(t_in) + fi:.3f},100],[{s(t_out)},100],[{s(t_out) + fo:.3f},0]]);")

    def hold(n, t_in, t_out):                               # 인형 동작: 딱 바꿔 끼움
        a(f"keys({var[n]}.transform.opacity,[[0,0],[{s(t_in)},100],[{s(t_out)},0]]); for(var q=1;q<=3;q++){{ {var[n]}.transform.opacity.setInterpolationTypeAtKey(q,KeyframeInterpolationType.HOLD); }}")

    def move(n, t, dx=0, dy=20, dur=0.35):
        x, y = c(n)
        a(f"keys({var[n]}.transform.position,[[{s(t)},[{x + dx:.1f},{y + dy:.1f}]],[{s(t) + dur:.3f},[{x:.1f},{y:.1f}]]]); eo({var[n]}.transform.position);")

    def pop(n, t, frm=80, dur=0.28, foot=False):
        x0, y0, x1, y1 = box[n]
        if foot:                                            # 발밑 기준(인형)
            a(f"{var[n]}.transform.anchorPoint.setValue([{(x0 + x1) / 2},{y1}]); {var[n]}.transform.position.setValue([{(x0 + x1) / 2},{y1}]);")
        a(f"keys({var[n]}.transform.scale,[[{s(t)},[{frm},{frm}]],[{s(t) + dur:.3f},[100,100]]]); eo({var[n]}.transform.scale);")

    def squash(n, t, k=1.0):
        x0, y0, x1, y1 = box[n]
        a(f"{var[n]}.transform.anchorPoint.setValue([{(x0 + x1) / 2},{y1}]); {var[n]}.transform.position.setValue([{(x0 + x1) / 2},{y1}]);")
        a(f"keys({var[n]}.transform.scale,[[{s(t)},[{100 + 10 * k:.0f},{100 - 10 * k:.0f}]],[{s(t) + 0.12:.3f},[{100 - 5 * k:.0f},{100 + 6 * k:.0f}]],[{s(t) + 0.26:.3f},[100,100]]]);")

    def bob(n):
        a(f"{var[n]}.transform.position.expression=\"value+[thisComp.layer('RIG').transform.position[0],6*Math.sin(time*5.2)]\";")

    # 글
    life("label", T_IN + 0.3); move("label", T_IN + 0.3, dx=-20, dy=0)
    life("title", T_TITLE); move("title", T_TITLE, dx=-24, dy=0)
    for n, t_in, t_out in (("s1", T_S1, T_S2), ("s2", T_S2, T_RESET), ("s3", T_S3, T_SLOW), ("s4", T_SLOW, T_OUT)):
        life(n, t_in, t_out, fo=0.2); move(n, t_in, dx=-20, dy=0)
    # 인형: 공부(떨어져 착지) → 아하 → OK → 다시 공부
    for n, t_in, t_out in (("m_study", T_DROP, T_AHA), ("m_aha", T_AHA, T_OK), ("m_ok", T_OK, T_RESET)):
        hold(n, t_in, t_out)
        squash(n, t_in, 1.3 if n == "m_study" else 1.0)
        bob(n)
    x0, y0, x1, y1 = box["m_study"]
    a(f"keys({var['m_study']}.transform.position,[[{s(T_DROP)},[{(x0 + x1) / 2},{y1 - 600}]],[{s(T_DROP) + 0.42:.3f},[{(x0 + x1) / 2},{y1}]]]); eo({var['m_study']}.transform.position);")
    a(f"keys({var['m_study']}.transform.scale,[[{s(T_DROP) + 0.42:.3f},[113,87]],[{s(T_DROP) + 0.55:.3f},[94,107]],[{s(T_DROP) + 0.7:.3f},[100,100]]]);")
    # 다시 공부(같은 그림을 한 번 더)
    a(f"var M2={var['m_study']}.duplicate(); while(M2.transform.opacity.numKeys>0) M2.transform.opacity.removeKey(1); while(M2.transform.position.numKeys>0) M2.transform.position.removeKey(1); while(M2.transform.scale.numKeys>0) M2.transform.scale.removeKey(1);")
    a(f"keys(M2.transform.opacity,[[0,0],[{s(T_RESET)},100],[{s(T_OUT)},100]]); for(var q=1;q<=3;q++){{ M2.transform.opacity.setInterpolationTypeAtKey(q,KeyframeInterpolationType.HOLD); }}")
    a(f"keys(M2.transform.scale,[[{s(T_RESET)},[110,90]],[{s(T_RESET) + 0.12:.3f},[95,106]],[{s(T_RESET) + 0.26:.3f},[100,100]]]);")
    # 말풍선
    life("bubble", T_AHA + 0.15, T_OK, fo=0.2)
    xb0, yb0, xb1, yb1 = box["bubble"]
    a(f"{var['bubble']}.transform.anchorPoint.setValue([{(xb0 + xb1) / 2},{yb1}]); {var['bubble']}.transform.position.setValue([{(xb0 + xb1) / 2},{yb1}]);")
    a(f"keys({var['bubble']}.transform.scale,[[{s(T_AHA + 0.15)},[60,60]],[{s(T_AHA + 0.45):.3f},[100,100]]]); eo({var['bubble']}.transform.scale);")
    life("bubble2", T_OK + 0.1, T_RESET, fo=0.2); pop("bubble2", T_OK + 0.1, 60)
    # DB 카드 쌓임 → 비워짐
    for k in range(6):
        t = (T_DB1 if k < 3 else T_DB2) + (k % 3) * 0.15
        life(f"db{k}", t, T_RESET, fi=0.2, fo=0.3); move(f"db{k}", t, dy=-40, dur=0.35)
    # 학습 막대: 쭉 참 → 비움 → 아주 조금(빨강)
    life("learn", T_LEARN - 0.2, fi=0.3)
    for n, t, dur, t_out in (("fill_full", T_LEARN, 1.1, T_RESET), ("fill_slow", T_SLOW, 1.4, T_OUT)):
        x0, y0, x1, y1 = box[n]
        a(f"{var[n]}.transform.anchorPoint.setValue([{x0},{(y0 + y1) / 2}]); {var[n]}.transform.position.setValue([{x0},{(y0 + y1) / 2}]);")
        a(f"keys({var[n]}.transform.scale,[[{s(t)},[0,100]],[{s(t) + dur:.3f},[100,100]]]);")
        life(n, t, t_out, fi=0.05, fo=0.3)
    # 좁은 퍼널: 떨어짐 → 조임
    life("funnel", T_FUN, T_COIN_S - 0.4, fi=0.15, fo=0.3)
    x0, y0, x1, y1 = box["funnel"]
    a(f"keys({var['funnel']}.transform.position,[[{s(T_FUN)},[{(x0 + x1) / 2},{(y0 + y1) / 2 - 500}]],[{s(T_FUN) + 0.4:.3f},[{(x0 + x1) / 2},{(y0 + y1) / 2}]]]); eo({var['funnel']}.transform.position);")
    a(f"keys({var['funnel']}.transform.scale,[[{s(T_SQZ)},[100,100]],[{s(T_SQZ) + 0.25:.3f},[78,104]],[{s(T_SQZ) + 0.6:.3f},[84,102]]]); eo({var['funnel']}.transform.scale);")
    # 동전: 천 원 → 만 원
    life("coin_s", T_COIN_S); pop("coin_s", T_COIN_S, 60, foot=True)
    life("coin_s_lab", T_COIN_S + 0.1); move("coin_s_lab", T_COIN_S + 0.1, dy=14)
    life("arrow", T_COIN_B - 0.1); move("arrow", T_COIN_B - 0.1, dx=-20, dy=0)
    life("coin_b", T_COIN_B); pop("coin_b", T_COIN_B, 50, 0.35, foot=True)
    life("coin_b_lab", T_COIN_B + 0.2); move("coin_b_lab", T_COIN_B + 0.2, dy=14)
    a(f"var rq=app.project.renderQueue.items.add(comp); var om=rq.outputModule(1); om.applyTemplate({js('고품질')}); om.file=new File({js(str(out_mov))});")
    a("log('ok bisa16'); })();")
    assert T_OUT + 0.45 < T1
    return "\n".join(L)


M.SND_FIX = {
    "in":    ("휙２.mp3", 0.6, 4, "peak"),
    "land":  ("ML_Cartoon bubbles popping.wav", 0.5, 5, "onset"),   # 인형 착지 · 퍼널 떨어짐
    "st1":   ("KN_pepSound1.wav", 0.4, 8, "onset"),
    "st2":   ("KN_pepSound2.wav", 0.4, 8, "onset"),
    "gauge": ("SEL_ゲージ回復1.mp3", 0.6, 12, "onset"),             # 학습 막대 참
    "talk":  ("채팅 효과음.mp3", 0.6, 5, "onset"),                   # 아하 말풍선
    "ok":    ("맑은소리.mp3", 0.8, 7, "onset"),
    "reset": ("휙1.mp3", 0.7, 8, "peak"),                           # 비워짐 · 판이 빠짐
    "slow":  ("KN_error_003.wav", 0.5, 5, "onset"),                 # 학습 너무 더딤
    "coin":  ("SEL_宝箱を開ける.mp3", 0.8, 5, "onset"),              # 만 원(돈 더 듦) — 새 파일, 기본 +5
}
M.EVENTS = [(T_IN + 0.25, "in"), (T_DROP + 0.42, "land"), (T_TITLE, "st1"), (T_S1, "st2"), (T_DB1, "st1"), (T_DB2, "st2"),
            (T_LEARN, "gauge"), (T_AHA, "talk"), (T_OK, "ok"), (T_S2, "st1"), (T_RESET + 0.2, "reset"),
            (T_FUN + 0.35, "land"), (T_SLOW, "slow"), (T_COIN_S, "st2"), (T_COIN_B, "coin"), (T_OUT + 0.2, "reset")]


if __name__ == "__main__":
    M.pieces = lambda: None
    M.jsx = jsx
    M.WORK.mkdir(parents=True, exist_ok=True)
    scene = M.OUT / f"{M.NAME}_{T0:.2f}~.mp4"
    if "--소리만" not in sys.argv:
        scene = M.build()
    print(scene)
    print(M.sfx(scene))
