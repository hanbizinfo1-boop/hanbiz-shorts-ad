/* ───────── 통장 잔액 30억 → 100억, 머리 위에서 실시간으로 (6.26~7.99) ─────────
   10-20 사장님 «통장에 30억이 찍혀있고 이게 대표머리위에서 실시간으로 계좌잔액이 100억으로 바뀌는 연출» — 은행 이름 없는 일반 통장 화면 */
const C1 = {t0: 6.26, t1: 7.99, a: 3e9, b: 1e10, r0: 6.94, r1: 7.62};
C1.e = el('div', null, `<div style="position:absolute;left:34px;top:26px;display:flex;align-items:center;gap:14px">
    <span style="width:46px;height:46px;border-radius:50%;background:#1f6feb;color:#fff;font-weight:900;font-size:28px;display:flex;align-items:center;justify-content:center">₩</span>
    <span style="font-size:32px;font-weight:800;color:#16181d">내 통장</span><span style="font-size:26px;color:#8a8f99;font-weight:500">입출금</span></div>
  <div style="position:absolute;left:36px;top:96px;font-size:28px;color:#8a8f99;font-weight:600">잔액</div>
  <div id="c1n" style="position:absolute;left:30px;top:132px;height:96px;overflow:hidden;font-size:76px;font-weight:900;letter-spacing:-2px;color:#16181d;white-space:nowrap;display:flex"></div>
  <div id="c1k" style="position:absolute;right:36px;top:30px;padding:6px 18px;border-radius:20px;background:#eef1f5;color:#3a3f4a;font-size:30px;font-weight:800">30억</div>
  <div id="c1d" style="position:absolute;left:34px;right:34px;bottom:-78px;height:64px;border-radius:32px;background:#16a34a;color:#fff;font-size:34px;font-weight:800;display:flex;align-items:center;justify-content:center">입금 +7,000,000,000원</div>`, 'c_bank');
Object.assign(C1.e.style, {position: 'absolute', left: '150px', width: '780px', top: '96px', height: '250px', borderRadius: '32px', background: '#fff',
  boxShadow: '0 22px 46px rgba(0,0,0,.35)', zIndex: 4});
// 자리마다 숫자 기둥(0~9,0) — 잔액이 오르는 동안 아랫자리일수록 빨리 돈다
const C1N = C1.e.querySelector('#c1n'); const LH = 96; const COLS = [];
for (const ch of '10,000,000,000원') {
  const w = document.createElement('span'); w.style.cssText = 'display:inline-block;position:relative;height:' + LH + 'px;overflow:hidden;line-height:' + LH + 'px';
  if (/\d/.test(ch)) { w.innerHTML = '<span style="display:block">' + [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0].map(d => '<div style="height:' + LH + 'px">' + d + '</div>').join('') + '</span>'; COLS.push(w); }
  else w.textContent = ch;
  C1N.appendChild(w);
}
ev(6.30, 'card', 'c_bank'); ev(6.94, 'roll', 'c_bank_roll'); ev(7.64, 'chime', 'c_bank_in');
function drawC1(t) {
  const o = vis(t, C1.t0, C1.t1, 0.1, 0.15); show(C1.e, o); if (o <= 0) return;
  C1.e.style.transform = `translateY(${(1 - eo((t - C1.t0) / .3)) * -40}px) scale(${1 + .03 * Math.sin(Math.PI * clamp((t - C1.r1) / .25))})`;
  const k = clamp((t - C1.r0) / (C1.r1 - C1.r0)), v = C1.a + (C1.b - C1.a) * k * k * (3 - 2 * k);
  const n = COLS.length;   // 11 자리 — 맨 앞이 10^10
  const rolling = k > 0 && k < 1;
  COLS.forEach((c, i) => {
    const pw = n - 1 - i, d = (v / Math.pow(10, pw)) % 10;
    const pos = rolling && pw < 9 ? d : Math.floor(d + 1e-6);            // 오르는 동안 아랫자리는 연속으로 굴러감
    c.firstChild.style.transform = `translateY(${-pos * LH}px)`;
    c.firstChild.style.filter = rolling && pw < 8 ? 'blur(1.5px)' : 'none';
  });
  const lead = v >= 1e10 - 0.5;   // 100억이 되기 전엔 맨 앞 «1» 숨김
  C1N.children[0].style.display = lead ? 'inline-block' : 'none';   // 맨 앞 «1»(10^10 자리)만 — 30억은 «3,000,000,000원»
  const kk = C1.e.querySelector('#c1k'); kk.textContent = (k >= 1 ? 100 : Math.floor(v / 1e8)) + '억';
  kk.style.background = k >= 1 ? '#dcfce7' : '#eef1f5'; kk.style.color = k >= 1 ? '#16a34a' : '#3a3f4a';
  C1N.style.color = k >= 1 ? '#16a34a' : '#16181d';
  const dd = C1.e.querySelector('#c1d'), u = (t - C1.r1) / .3; dd.style.opacity = clamp(u * 2); dd.style.transform = `translateY(${(1 - back(u)) * -30}px)`;
}
