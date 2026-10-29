FIG.e = el('img', null, null, 'fig'); FIG.e.src = A + 'r4_figure_puzzled_a.png';   // 10-20 «밑에 사람이 예금? 하면서 의문을 품는듯한 연출»
const FQ = el('div', 'bub', '예금…<b>?</b>', 'fig_q');
Object.assign(FQ.style, {left: '372px', top: '1330px', fontSize: '58px', padding: '22px 36px 26px', transformOrigin: '0% 100%'});
const FQt = el('span', 'tail', null, null, null, FQ); FQt.style.left = '30px';
const FQm = [0, 1].map(i => { const q = el('div', null, '?'); Object.assign(q.style, {position: 'absolute', fontSize: '84px', fontWeight: 900, color: '#FFD43B', WebkitTextStroke: '6px #0d0d0f', paintOrder: 'stroke fill', zIndex: 6}); return q; });
function drawFQ(t) {
  const oq = vis(t, 8.55, FIG.t1, .05, .15); show(FQ, oq);
  if (oq > 0) FQ.style.transform = `scale(${.6 + .4 * back((t - 8.55) / .3)})`;
  FQm.forEach((q, i) => { const t0 = 8.85 + i * .22, oo = vis(t, t0, FIG.t1, .05, .15); show(q, oo);
    q.style.left = (250 + i * 80) + 'px'; q.style.top = (1200 - i * 34 + Math.sin((t - t0) * 5) * 8) + 'px'; q.style.transform = `scale(${back((t - t0) / .3)}) rotate(${i ? 14 : -10}deg)`; });
}
