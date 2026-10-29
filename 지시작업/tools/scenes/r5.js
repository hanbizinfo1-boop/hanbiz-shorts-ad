// R5+R6 «제조업 아니라고 / 넘기려고 하셨죠? / 위탁 생산도 / 전부 가능합니다»(9.243~13.280) 후보 A·B·C — 10-14 사장님
// «제조업 아니라고 넘기려고 하셨죠 이부분은 어떻게 표현하면 좋을까 다르게 표현하고싶은데» + «위탁생산까지 엮어서 지금 연출별로야 이부분»
// 사진 공간(1536x1024)에 그린 내용을 사진의 흰 칸 마스크(*_matte.png)로만 보이게 → 엄지·손은 저절로 위에 남는다.
// 단어 시각: 제조업 9.42 · 아니라고 9.76 · 넘기려고 10.22 · 하셨죠 10.78 · 위탁 11.32 · 생산도 11.66 · 전부 12.18 · 가능합니다 12.62
window.W=1080; window.H=1920; window.FPS=30; window.DURATION=48.131;
window.PALETTE=['#0B2A5E','#FFFFFF','#F2A33A'];
const V=window.V;
const el=id=>document.getElementById(id);
const cl=(x,a,b)=>Math.min(b,Math.max(a,x));
const lin=(t,a,b)=>cl((t-a)/(b-a),0,1);
const eo=x=>1-Math.pow(1-cl(x,0,1),3);
const ei=x=>Math.pow(cl(x,0,1),3);
const eio=x=>{x=cl(x,0,1);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;};
const T0=9.27, T1=13.28;
const S0=948/1536, OY=(608-1024*S0)/2;   // 사진 → 판(948x608) cover
const D='../../소재/codex/', SITE='../../소재/db1/site/';
const SRC={A:'r5a_phone',B:'r5c_walk',C:'r5d_brochure'}[V];
const BOX=document.createElement('div');

function build(){
  const st=el('st');
  st.innerHTML=`<div id="R" data-box="R" data-box-group="layer" data-box-bleed style="position:absolute;left:0;top:1215px;width:1080px;height:705px;overflow:hidden">
   <div id="card" style="position:absolute;left:60px;top:20px;width:960px;height:620px;border-radius:14px;overflow:hidden;background:#fff;border:6px solid #fff;box-shadow:0 22px 48px rgba(0,0,0,.5);opacity:0">
    <div id="ph" style="position:absolute;inset:0;overflow:hidden;border-radius:9px;background:#222">
     <div id="cam" style="position:absolute;left:0;top:0;width:1536px;height:1024px;transform-origin:0 0">
      ${V==='B'?`<div id="sceneW" class="sc"><img src="${D}r5c_walk.png"><div class="mk" style="-webkit-mask-image:url(${D}r5c_walk_matte.png)">${sign(115,134,298,405)}</div></div>
               <div id="sceneL" class="sc" style="opacity:0"><img src="${D}r5c_look.png"><div class="mk" style="-webkit-mask-image:url(${D}r5c_look_matte.png)">${sign(142,198,293,420)}</div></div>`
              :`<div class="sc"><img src="${D}${SRC}.png"><div class="mk" id="mk" style="-webkit-mask-image:url(${D}${SRC}_matte.png)">${V==='A'?phone():book()}</div></div>${V==='C'?flipPage():''}`}
     </div>
     <div id="whip" style="position:absolute;inset:0;opacity:0;background:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,255,255,.7),rgba(255,255,255,0))"></div>
    </div></div></div>`;
}
// ── A 휴대폰 피드 ──
function phone(){
  const post=(img,cap,ours)=>`<div style="height:470px;padding:18px 0 0;border-bottom:8px solid #EEF0F4;background:#fff">
     <div style="display:flex;align-items:center;gap:12px;padding:0 18px 14px;font:700 26px 'HM Pretendard';color:#1B2A4A">
      <i style="width:44px;height:44px;border-radius:50%;background:${ours?'#0B2A5E':'#C9CED8'};display:inline-block"></i>${ours?'한국중소기업비즈니스센터':''}</div>
     <div style="position:relative;height:290px;overflow:hidden"><img src="${img}" style="width:100%;height:100%;object-fit:cover">
      ${ours?`<div style="position:absolute;right:16px;bottom:12px;font:900 78px/1 'HM Pretendard';color:#FFD54A;-webkit-text-stroke:5px #3A1F00;paint-order:stroke fill">10억</div>`:''}</div>
     ${ours?`<div style="padding:16px 18px 0;font:800 32px 'HM Pretendard';color:#111">제조업 하시면 최대 10억</div>`:''}</div>`;
  return `<div style="position:absolute;left:555px;top:52px;width:423px;height:881px;background:#fff;overflow:hidden">
   <div id="feed" style="position:absolute;left:0;top:0;width:423px">
    ${post(SITE+'field/field_14.jpg','',false)}${post(D+'s1_factory.png','',true)}${post(D+'s16_report.png','',false)}${post(SITE+'field/field_32.jpg','',false)}
   </div>
   <div id="ring" style="position:absolute;left:211px;top:330px;width:10px;height:10px;border-radius:50%;border:4px solid rgba(11,42,94,.6);opacity:0"></div>
   <div id="sheet" style="position:absolute;left:0;top:881px;width:423px;height:881px;background:#fff;border-radius:28px 28px 0 0;box-shadow:0 -8px 30px rgba(0,0,0,.25);padding:46px 28px 0">
    <div style="width:70px;height:7px;border-radius:4px;background:#D5D9E1;margin:0 auto 34px"></div>
    <div style="font:900 44px 'HM Pretendard';color:#0B2A5E;margin-bottom:10px">신청 대상</div>
    <div style="font:600 26px 'HM Pretendard';color:#6A7487;margin-bottom:34px">제조업 정책자금</div>
    ${row('r1','직접 공장 운영')}${row('r2','위탁 생산 (OEM)')}
   </div></div>`;
}
function row(id,txt){return `<div id="${id}" style="position:relative;display:flex;align-items:center;justify-content:space-between;height:120px;margin-bottom:22px;padding:0 22px;border-radius:18px;background:#F3F5F9;font:800 31px 'HM Pretendard';color:#1B2A4A;white-space:nowrap">
  <span style="position:relative;z-index:1">${txt}</span><b id="${id}p" style="position:relative;z-index:1;padding:8px 20px;border-radius:30px;background:#16A34A;color:#fff;font:900 32px 'HM Pretendard';opacity:0">가능 ✓</b>
  <i id="${id}h" style="position:absolute;left:0;top:0;bottom:0;width:0;border-radius:18px;background:#FFE58A"></i></div>`;}
// ── B 안내판 ──
function sign(x,y,w,h){return `<div style="position:absolute;left:${x}px;top:${y}px;width:${w}px;height:${h}px;background:linear-gradient(180deg,#FFFFFF,#F1F4F9)">
  <div style="height:${h*0.36}px;background:#0B2A5E;display:flex;align-items:center;justify-content:center;font:900 ${w*0.22}px 'HM Pretendard';color:#fff;letter-spacing:-1px">제조업</div>
  <div style="text-align:center;font:800 ${w*0.12}px/1.35 'HM Pretendard';color:#0B2A5E;margin-top:${h*0.07}px">정책자금<br>상담 창구</div>
  <div class="strip" style="position:absolute;left:0;right:0;bottom:${h*0.07}px;height:${h*0.2}px;background:#F2A33A;display:flex;align-items:center;justify-content:center;gap:6px;font:900 ${w*0.095}px 'HM Pretendard';color:#fff;clip-path:inset(0 100% 0 0)">위탁 생산도<b class="ok" style="padding:2px 10px;border-radius:20px;background:#16A34A;font:900 ${w*0.085}px 'HM Pretendard';opacity:0">가능</b></div></div>`;}
// ── C 책자 ──
const SP=784, PG={x0:280,x1:1288,y0:156,y1:868};
function rightPage(id){return `<div id="${id}" style="position:absolute;left:${SP}px;top:${PG.y0}px;width:${PG.x1-SP}px;height:${PG.y1-PG.y0}px;background:#fff;padding:46px 40px 0;color:#0B2A5E">
  <div style="font:900 50px 'HM Pretendard';letter-spacing:-1px">제조업 정책자금</div>
  <div style="font:800 30px 'HM Pretendard';color:#E07A10;margin:8px 0 22px">최대 10억</div>
  <div style="height:210px;border-radius:10px;overflow:hidden"><img src="${D}s2_start.png" style="width:100%;height:100%;object-fit:cover"></div>
  <div style="font:800 30px 'HM Pretendard';margin:30px 0 14px">지원 대상</div>
  <div class="li" style="font:700 34px/1.9 'HM Pretendard';position:relative"><span class="bx">☐</span> 직접 생산 공장</div>
  <div class="li" style="font:700 34px/1.9 'HM Pretendard';position:relative"><i class="hl" style="position:absolute;left:-6px;top:14px;height:44px;width:0;background:#FFE14D;z-index:0"></i><span style="position:relative;z-index:1"><span class="bx">☐</span> 위탁 생산(OEM)</span>
   <svg class="circ" viewBox="0 0 400 90" style="position:absolute;left:-26px;top:-6px;width:420px;height:96px;overflow:visible"><path d="M20 50 C 40 5, 360 0, 392 40 S 300 92, 120 86 S 4 70, 30 30" fill="none" stroke="#E0262B" stroke-width="7" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg>
   <b class="ga" style="position:absolute;right:-6px;top:-62px;font:900 56px 'HM Pretendard';color:#E0262B;transform:rotate(-10deg);opacity:0">가능!</b></div>
 </div>`;}
function book(){return `<div style="position:absolute;left:${PG.x0}px;top:${PG.y0}px;width:${SP-PG.x0}px;height:${PG.y1-PG.y0}px;background:#fff;padding:46px 40px 0;color:#0B2A5E">
   <div style="font:700 26px 'HM Pretendard';color:#6A7487">2026 중소기업</div><div style="font:900 46px 'HM Pretendard';margin:4px 0 26px">정책자금 안내</div>
   <div style="height:430px;border-radius:10px;overflow:hidden"><img src="${D}s1_factory.png" style="width:100%;height:100%;object-fit:cover"></div></div>
  ${rightPage('rp')}`;}
function flipPage(){return `<div id="flip" style="position:absolute;left:${SP}px;top:${PG.y0}px;width:${PG.x1-SP}px;height:${PG.y1-PG.y0}px;transform-origin:0 50%;opacity:0;perspective:none">
   <div style="position:absolute;inset:0;transform:none">${rightPage('rp2').replace(`left:${SP}px;top:${PG.y0}px;`,'left:0;top:0;')}</div>
   <div id="shade" style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.0),rgba(0,0,0,.25))"></div></div>`;}

const css=document.createElement('style');
css.textContent=`.sc{position:absolute;left:0;top:0;width:1536px;height:1024px}.sc>img{position:absolute;left:0;top:0;width:1536px;height:1024px}
.mk{position:absolute;left:0;top:0;width:1536px;height:1024px;-webkit-mask-size:1536px 1024px;-webkit-mask-repeat:no-repeat}`;
document.head.appendChild(css);
build();

function camSet(cx,cy,s){   // 사진 좌표 (cx,cy) 를 판 가운데에, 배율 s(1 = cover)
  const k=S0*s; el('cam').style.transform=`translate(${474-cx*k}px,${304-cy*k}px) scale(${k})`;}
function keyCam(t,KEY){let c=KEY[0][1];for(let i=0;i<KEY.length-1;i++){const [a,A]=KEY[i],[b,B]=KEY[i+1];if(t<a){c=A;break;}if(t<b){const k=eio((t-a)/(b-a));c=A.map((v,j)=>v+(B[j]-v)*k);break;}c=B;}return c;}

async function seek(t){
  const card=el('card');
  if(t<T0||t>=T1+0.17){card.style.opacity=0;return;}
  const a=eo(lin(t,T0,T0+0.2)), out=lin(t,T1,T1+0.17);
  card.style.opacity=Math.min(1,(t-T0)/0.1)*(1-out); card.style.transform=`scale(${(0.84+0.16*a)*(1+0.12*ei(out))})`;
  card.style.filter=(1-a)>0.02?`blur(${(1-a)*10}px)`:'';
  if(V==='A'){
    // 피드: 10.22 넘김(한 칸 위로) → 10.78 다시 끌려 내려와 우리 광고에 멈춤 → 11.32 탭 → 시트 올라옴 → 11.66 위탁 생산 줄 → 12.62 가능
    const base=-470+28, up=eio(lin(t,10.22,10.46)), back=eo(lin(t,10.78,11.04));
    el('feed').style.transform=`translateY(${base-470*up*(1-back)}px)`;
    const rk=lin(t,11.30,11.55); el('ring').style.opacity=rk>0&&rk<1?1-rk:0; el('ring').style.transform=`scale(${1+14*eo(rk)})`;
    const sh=eo(lin(t,11.40,11.66)); el('sheet').style.transform=`translateY(${-881*sh}px)`;
    el('r2h').style.width=(100*eo(lin(t,11.66,11.90)))+'%';
    for(const id of ['r1p','r2p']){const k=lin(t,12.62,12.80);el(id).style.opacity=k>0?1:0;el(id).style.transform=`scale(${1.6-0.6*eo(k)})`;}
    const c=keyCam(t,[[9.27,[766,492,1.0]],[11.30,[766,492,1.0]],[11.80,[766,520,1.22]],[13.4,[766,520,1.27]]]); camSet(...c);
  } else if(V==='B'){
    // 지나침(천천히 따라가는 팬, 10.22 빨라짐) → 10.78 휙 → 뒤돌아봄 → 11.32 안내판으로 들어감 → 11.66 주황 띠 → 12.62 가능
    const look=t>=10.84; el('sceneW').style.opacity=look?0:1; el('sceneL').style.opacity=look?1:0;
    const wk=lin(t,10.76,10.92); el('whip').style.opacity=wk>0&&wk<1?Math.sin(Math.PI*wk):0;
    let c; if(!look){const px=760+60*lin(t,9.27,10.22)+140*eio(lin(t,10.22,10.84)); c=[px,512,1.0];}
    else c=keyCam(t,[[10.84,[700,512,1.0]],[11.32,[640,512,1.0]],[11.78,[300,420,2.15]],[13.4,[300,430,2.25]]]);
    camSet(...c);
    document.querySelectorAll('.strip').forEach(s=>s.style.clipPath=`inset(0 ${100-100*eo(lin(t,11.66,11.95))}% 0 0)`);
    document.querySelectorAll('.ok').forEach(o=>{const k=lin(t,12.62,12.80);o.style.opacity=k>0?1:0;o.style.transform=`scale(${1.7-0.7*eo(k)})`;});
  } else {
    // 책장: 10.22 넘기기 시작 → 10.78 멈칫 → 제자리 → 11.32 지원 대상으로 들어감 → 11.66 형광펜 → 12.62 빨간 동그라미 «가능!»
    const fl=eio(lin(t,10.22,10.70))*0.68, bk=eo(lin(t,10.78,11.10)), ang=-180*fl*(1-bk);
    const flipping=ang<-0.5; el('flip').style.opacity=flipping?1:0; el('rp').style.visibility=flipping?'hidden':'visible';
    el('flip').style.transform=`perspective(2200px) rotateY(${ang}deg)`; el('shade').style.opacity=cl(-ang/90,0,1);
    el('rp2').style.visibility=ang<-90?'hidden':'visible'; el('flip').style.background=ang<-90?'#F7F5F0':'transparent';   // 90° 넘으면 빈 뒷면
    const hl=eo(lin(t,11.66,11.92)); document.querySelectorAll('#rp .hl').forEach(h=>h.style.width=(hl*330)+'px');
    const ck=lin(t,12.62,12.95); document.querySelectorAll('#rp .circ path').forEach(p=>p.style.strokeDashoffset=1-eo(ck));
    document.querySelectorAll('#rp .ga').forEach(g=>{const k=lin(t,12.70,12.85);g.style.opacity=k>0?1:0;g.style.transform=`rotate(-10deg) scale(${1.8-0.8*eo(k)})`;});
    document.querySelectorAll('#rp .bx').forEach(b=>b.textContent=t>=12.62?'☑':'☐');
    const c=keyCam(t,[[9.27,[784,512,1.0]],[11.30,[784,512,1.0]],[11.75,[1030,720,1.75]],[13.4,[1030,720,1.82]]]); camSet(...c);
  }
}
window.EVENTS={
 A:[{t:9.30,role:'photo_in',id:'card'},{t:10.30,role:'swipe',id:'up'},{t:10.86,role:'swipe2',id:'back'},{t:11.32,role:'tap',id:'tap'},{t:11.48,role:'card_in',id:'sheet'},{t:11.70,role:'fill',id:'r2h'},{t:12.62,role:'good',id:'ok'}],
 B:[{t:9.30,role:'photo_in',id:'card'},{t:10.82,role:'swipe',id:'whip'},{t:11.40,role:'zoom',id:'push'},{t:11.70,role:'card_in',id:'strip'},{t:12.62,role:'good',id:'ok'}],
 C:[{t:9.30,role:'photo_in',id:'card'},{t:10.26,role:'flip',id:'flip'},{t:10.82,role:'page2',id:'back'},{t:11.40,role:'zoom',id:'push'},{t:11.70,role:'mark',id:'hl'},{t:12.64,role:'mark2',id:'circ'}]}[V];
