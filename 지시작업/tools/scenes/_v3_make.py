from pathlib import Path
import sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\user\Desktop\한비즈-쇼츠광고")
p = ROOT / "지시작업/tools/scenes/r4_ref_v3.html"
s = (ROOT / "지시작업/tools/scenes/r4_ref_v2.html").read_text(encoding="utf-8")

s = s.replace("<!-- 10-19 4번 레퍼연출 v2", "<!-- 10-20 v3 — 사장님 «강남빌딩할떄 자막 밑에 크게 강남빌딩이 레이저쏘듯이와서 펑 박히면» «확실한투자가 있다 할때 물음표를 약간 띵띵띵 이렇게 3개» «아 말도 안돼요 그거는 << 연출이 너무 부족함» «이 영상보지마세요 할때 x자 하잖아 이때 짧게 흔들리는 연출 (효과음동반)» «30억으로 100억만드려고하는데 → 통장에 30억이 찍혀있고 이게 대표머리위에서 실시간으로 계좌잔액이 100억으로 바뀌는 연출» «예금하려는 분들없죠? → 밑에 사람이 예금? 하면서 의문을 품는듯한 연출» -->\n<!-- 10-19 4번 레퍼연출 v2", 1)

for l in ["  {id: 'e_bld', ch: '🏢', t0: 0.15, t1: 1.97, x: 760, y: 1040},\n", "  {id: 'e_think', ch: '🤔', t0: 0.95, t1: 1.97, x: 930, y: 1040},\n"]:
    assert l in s, l
    s = s.replace(l, "")

a = s.index("/* ───────── 카드 1: 30억 → 100억")
b = s.index("/* ───────── 예금 ✕")
s = s[:a] + (ROOT / "지시작업/tools/scenes/_v3_bank.js").read_text(encoding="utf-8") + "\n" + s[b:]

old = "FIG.e = el('img', null, null, 'fig'); FIG.e.src = A + 'r4_figure_a.png';"
assert old in s
s = s.replace(old, (ROOT / "지시작업/tools/scenes/_v3_fig.js").read_text(encoding="utf-8"))
old = "ev(8.30, 'strike', 'c_dep'); ev(7.99, 'card', 'fig');"
assert old in s
s = s.replace(old, old + " ev(8.55, 'pop', 'fig_q');")
old = "FIG.e.style.transformOrigin = '50% 100%'; }\n}"
assert old in s
s = s.replace(old, "FIG.e.style.transformOrigin = '50% 100%'; }\n  drawFQ(t);\n}")
old = "rotate(${Math.sin((t - FIG.t0) * 6) * 2 * clamp((t - FIG.t0 - .3) / .2)}deg)`;"
assert old in s
s = s.replace(old, "rotate(${-4 + Math.sin((t - FIG.t0) * 3) * 3 * clamp((t - FIG.t0 - .3) / .2)}deg)`;")

s = s.replace("window.EVENTS = EV.sort", (ROOT / "지시작업/tools/scenes/_v3_open.js").read_text(encoding="utf-8") + "\nwindow.EVENTS = EV.sort")
old = "drawBig(t); drawEmo(t);"
assert old in s
s = s.replace(old, "drawLZ(t); drawQM(t); drawNO(t); drawBig(t); drawEmo(t);")
# 인형이 말풍선과 겹치지 않게(점검 ERROR) 오른쪽으로
old = "z-index:5;left:60px'"
assert old in s
s = s.replace(old, "z-index:5;left:84px'")
# 10-20 사장님 «자막은 노란색, 초록색 , 흰색으로만 구성» — 빨간 글을 노랑으로(빨간 선·동그라미 같은 그림은 그대로)
for a, b in [("{r:이 영상 보지마세요}", "{y:이 영상 보지마세요}"), ("{r:급격히}", "{y:급격히}"), ("{r:착각}", "{y:착각}"), ("{r:존재치 않아요}", "{y:존재치 않아요}"),
             ("querySelector('.f .c-r')", "querySelector('.f .c-y')"),
             (".bub b{font-weight:800;color:#e8402e}", ".bub b{font-weight:800;color:#16181d;background:linear-gradient(transparent 58%, #FFD43B 58%)}"),
             ("border:9px solid var(--r);border-radius:18px;color:var(--r)", "border:9px solid var(--g);border-radius:18px;color:#16a34a")]:
    assert a in s, a
    s = s.replace(a, b)
p.write_text(s, encoding="utf-8", newline="\n")
print("ok", len(s))
