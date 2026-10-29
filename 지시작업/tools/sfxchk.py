import json,glob,sys,re,os
sys.path.insert(0,'tools'); import sfx_audit as A
D=sys.argv[1] if len(sys.argv)>1 else '지시작업/납품/한비즈_DB광고1_A지시_1014'
PL=sys.argv[2] if len(sys.argv)>2 else '지시작업/_tmp/a/plan_A지시.json'
p=json.load(open(PL,encoding='utf-8'))
fs=sorted(glob.glob(D+'/media/SFX_*.wav'))
x=open(D+'/한비즈_DB광고1_A지시.xml',encoding='utf-8').read()
rows=[]
for f in fs:
    name=os.path.basename(f)
    i=x.find('<name>'+name+'</name>'); m=re.search(r'<start>(\d+)</start>',x[i:]) if i>=0 else None
    st=int(m.group(1))/30 if m else -1
    rows.append((st,name,A.measure(f)))
rows.sort(key=lambda r:r[1])
print(len(rows),'개')
bad=0
rs=sorted(rows,key=lambda r:r[0])
for (s1,n1,m1),(s2,n2,m2) in zip(rs,rs[1:]):
    ov=(s1+m1['end'])-(s2+m2['attack'])
    if ov>0.02: bad+=1; print(f'겹침 {ov*1000:.0f}ms {n1}@{s1:.2f} -> {n2}@{s2:.2f}')
print('겹침',bad)
cues=p['sfx']; late=0
for (s,n,m),c in zip(rows,cues):
    al=p['sfx_roles'][c['role']].get('align','onset'); d=s+(m['peak'] if al=='peak' else m['attack'])-c['t']
    if abs(d)>0.034: late+=1; print(f'밀림 {d*1000:+.0f}ms {n} 큐 {c["t"]}')
print('밀림',late)
