
/* ───────── 0.00 «강남 빌딩보다» — 자막 밑에 큰 «강남빌딩»이 레이저처럼 날아와 펑 박힌다(10-20) ───────── */
const LZ = {t0: 0.04, hit: 0.30, t1: 1.97, y: 1262};
LZ.beam = el('div'); Object.assign(LZ.beam.style, {position: 'absolute', left: 0, top: (LZ.y + 82) + 'px', height: '10px', width: '1080px', zIndex: 7,
  background: 'linear-gradient(90deg, rgba(255,212,59,0), #fff 70%, #fff)', boxShadow: '0 0 18px 6px rgba(255,212,59,.9), 0 0 40px 14px rgba(255,140,0,.45)', transformOrigin: '0 50%'});
LZ.ghost = [0, 1, 2].map(i => { const g = el('div', 'big'); g.style.top = LZ.y + 'px'; g.innerHTML = '<span class="seg" style="font-size:156px"><span class="f" style="color:rgba(255,212,59,' + (.35 - i * .1) + ')">강남빌딩</span></span>'; return g; });
LZ.e = el('div', 'big'); LZ.e.style.top = LZ.y + 'px';
LZ.e.innerHTML = '<span class="row" data-box="lz_txt" data-box-bleed><span class="seg" style="font-size:156px"><span class="s">강남빌딩</span><span class="f" style="color:var(--y)">강남빌딩</span></span></span>';
LZ.ring = el('div'); Object.assign(LZ.ring.style, {position: 'absolute', left: '540px', top: (LZ.y + 92) + 'px', width: '12px', height: '12px', borderRadius: '50%', border: '3px solid #fff', zIndex: 6});
LZ.flash = el('div'); Object.assign(LZ.flash.style, {position: 'absolute', left: 0, top: 0, width: '1080px', height: '1920px', background: '#fff', zIndex: 8});
LZ.sp = Array.from({length: 14}, (_, i) => { const s = el('div'); Object.assign(s.style, {position: 'absolute', height: '8px', borderRadius: '4px', background: i % 2 ? '#FFD43B' : '#fff', zIndex: 6, transformOrigin: '0 50%'}); s.a = i / 14 * Math.PI * 2 + .2; s.l = 70 + (i * 37) % 60; return s; });
ev(LZ.t0, 'laser', 'lz'); ev(LZ.hit, 'boom', 'lz_hit');
function drawLZ(t) {
  const hk = t - LZ.hit;
  show(LZ.beam, t >= LZ.t0 && hk < .08 ? clamp((LZ.hit + .08 - t) / .08) : 0);
  LZ.beam.style.transform = `scaleX(${eo((t - LZ.t0) / .12)}) scaleY(${1 - clamp(hk / .08)})`;
  const fly = clamp((t - (LZ.t0 + .08)) / (LZ.hit - LZ.t0 - .08)), x = (1 - fly * fly) * -1150;
  show(LZ.e, vis(t, LZ.t0 + .08, LZ.t1, .02, .15));
  const jig = hk > 0 ? Math.sin(hk * 70) * 14 * Math.exp(-hk * 12) : 0;
  const sc = hk < 0 ? 1 : 1 + .28 * Math.exp(-hk * 10) * Math.cos(hk * 30);
  LZ.e.style.transform = `translateX(${x + jig}px) skewX(${hk < 0 ? -18 : -18 * Math.exp(-hk * 25)}deg) scale(${sc * (1 + .015 * Math.sin(t * 4))})`;
  LZ.ghost.forEach((g, i) => { show(g, hk < 0 && fly > 0 ? 1 : 0); g.style.transform = `translateX(${x - (i + 1) * 120 * (1 - fly)}px) skewX(-18deg)`; });
  const rk = clamp(hk / .35); show(LZ.ring, hk > 0 && hk < .35 ? 1 - rk : 0);
  LZ.ring.style.transform = `translate(-50%,-50%) scale(${1 + rk * 60}, ${(1 + rk * 60) * .45})`;
  show(LZ.flash, hk > 0 && hk < .1 ? .5 * (1 - hk / .1) : 0);
  LZ.sp.forEach(s => { const u = clamp(hk / .4); show(s, hk > 0 && hk < .4 ? 1 : 0); const r = 250 + u * 260;
    s.style.left = (540 + Math.cos(s.a) * r) + 'px'; s.style.top = (LZ.y + 92 + Math.sin(s.a) * r * .45) + 'px'; s.style.width = s.l * (1 - u) + 'px'; s.style.transform = `rotate(${s.a}rad)`; });
}

/* ───────── 0.88 «확실한 투자가 있다?» — 물음표 3개 띵·띵·띵(10-20) ───────── */
const QM = [{t: 0.98, x: 760, y: 280, r: -12, s: 150}, {t: 1.22, x: 880, y: 190, r: 8, s: 175}, {t: 1.46, x: 990, y: 310, r: 18, s: 135}];
QM.forEach((q, i) => { q.e = el('div', 'big'); q.e.style.left = (q.x - 540) + 'px'; q.e.style.top = q.y + 'px';
  q.e.innerHTML = '<span class="row" data-box="qm' + i + '" data-box-group="qm"><span class="seg" style="font-size:' + q.s + 'px"><span class="s">?</span><span class="f" style="color:var(--y)">?</span></span></span>'; ev(q.t, 'ding', 'qm' + i); });
function drawQM(t) { for (const q of QM) { const o = vis(t, q.t, 1.97, .02, .12); show(q.e, o); if (o <= 0) continue;
  q.e.style.transform = `translateY(${Math.sin((t - q.t) * 5) * 8}px) rotate(${q.r + Math.sin((t - q.t) * 7) * 4}deg) scale(${back((t - q.t) / .25)})`; } }

/* ───────── 1.97 «아, 말도 안돼요» · 2.72 «그거는»(10-20 «연출이 너무 부족함») ─────────
   작아진 화면이 절레절레(바탕 r4_build_v3) + 큰 빨간 «말도 안 돼!» + 🙅 + 빨간 강조선 / «그거는»에서 집중선이 몰리며 당김 */
const NO = {t0: 1.97, t1: 2.72};
NO.emo = el('div', 'emo', '🙅‍♂️', 'no_emo'); Object.assign(NO.emo.style, {position: 'absolute', fontSize: '180px', left: '780px', top: '300px', zIndex: 6});
NO.lines = [0, 1, 2].map(() => { const l = el('div'); Object.assign(l.style, {position: 'absolute', width: '80px', height: '14px', borderRadius: '7px', background: '#FF4D4F', zIndex: 6, transformOrigin: '0 50%'}); return l; });
NO.big = el('div', 'big'); NO.big.style.top = '1290px';
NO.big.innerHTML = '<span class="row" data-box="no_txt"><span class="seg" style="font-size:120px"><span class="s">말도 안 돼!</span><span class="f" style="color:var(--y)">말도 안 돼!</span></span></span>';
ev(2.02, 'buzz', 'no'); ev(2.20, 'pop', 'no_emo');
const FOC = {t0: 2.72, t1: 3.47}; FOC.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
Object.assign(FOC.svg.style, {position: 'absolute', left: 0, top: 0, zIndex: 3}); FOC.svg.setAttribute('width', 1080); FOC.svg.setAttribute('height', 1920); st.appendChild(FOC.svg);
let fs = 5; const fr = () => (fs = (fs * 16807) % 2147483647) / 2147483647;
FOC.rays = Array.from({length: 46}, (_, i) => { const p = document.createElementNS('http://www.w3.org/2000/svg', 'path'); p.setAttribute('fill', '#fff'); FOC.svg.appendChild(p); return {p, a: i / 46 * Math.PI * 2 + fr() * .1, w: 6 + fr() * 14, l: .3 + fr() * .2}; });
ev(2.72, 'focus', 'foc');
function drawNO(t) {
  show(NO.emo, vis(t, NO.t0 + .2, NO.t1, .04, .1)); show(NO.big, vis(t, NO.t0 + .05, NO.t1, .04, .1));
  NO.emo.style.transform = `scale(${back((t - NO.t0 - .2) / .3)}) rotate(${Math.sin((t - NO.t0) * 22) * 10}deg)`;
  NO.big.style.transform = `translateX(${Math.sin((t - NO.t0) * 40) * 9 * Math.exp(-(t - NO.t0) * 3)}px) scale(${back((t - NO.t0 - .05) / .25)})`;
  NO.lines.forEach((l, i) => { show(l, vis(t, NO.t0 + .1 + i * .05, NO.t1, .03, .1)); l.style.left = (330 - i * 10) + 'px'; l.style.top = (400 + i * 44) + 'px';
    l.style.transform = `rotate(${195 + i * 15}deg) scaleX(${eo((t - NO.t0 - .1 - i * .05) / .15)})`; });
  const fo = vis(t, FOC.t0, FOC.t1, .06, .12); FOC.svg.style.display = fo > 0 ? 'block' : 'none'; FOC.svg.style.opacity = fo * .8;
  if (fo > 0) { const cx = 540, cy = 560, R = 1300, k = eo((t - FOC.t0) / .2), fl = Math.sin(t * 40) * .03;
    for (const r of FOC.rays) { const r0 = R * (r.l + (1 - k) * .5 + fl), a1 = r.a - r.w / R, a2 = r.a + r.w / R;
      r.p.setAttribute('d', `M${cx + Math.cos(r.a) * r0},${cy + Math.sin(r.a) * r0} L${cx + Math.cos(a1) * R * 1.4},${cy + Math.sin(a1) * R * 1.4} L${cx + Math.cos(a2) * R * 1.4},${cy + Math.sin(a2) * R * 1.4}Z`); } }
}
