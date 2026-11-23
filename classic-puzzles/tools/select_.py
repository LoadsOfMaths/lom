import json, random, collections, math
from lat import *
from run import build, mask, bits
random.seed(3)
LATS={n:build(n) for n in ['R22','R32','R33','T2','T3']}
MODE=['move','add','take']
def segdist(p,q,r,s_):
    # min distance between segments pq and rs
    import math
    def pd(a,b,c):
        dx,dy=c[0]-b[0],c[1]-b[1];l=dx*dx+dy*dy
        t=0 if l==0 else max(0,min(1,((a[0]-b[0])*dx+(a[1]-b[1])*dy)/l))
        return math.hypot(a[0]-b[0]-t*dx,a[1]-b[1]-t*dy)
    def cross(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    d1,d2,d3,d4=cross(p,q,r),cross(p,q,s_),cross(r,s_,p),cross(r,s_,q)
    if ((d1>1e-9 and d2<-1e-9) or (d1<-1e-9 and d2>1e-9)) and ((d3>1e-9 and d4<-1e-9) or (d3<-1e-9 and d4>1e-9)): return 0
    return min(pd(p,r,s_),pd(q,r,s_),pd(r,p,q),pd(s_,p,q))
CONN={}
def connected(L,m):
    es=[i for i in range(len(L.edges)) if m>>i&1]
    if not es: return False
    seg=lambda e:(L.nodes[L.edges[e][0]],L.nodes[L.edges[e][1]])
    seen={es[0]};stack=[es[0]]
    while stack:
        a=stack.pop()
        for b in es:
            if b in seen: continue
            if segdist(*seg(a),*seg(b))<1e-6: seen.add(b);stack.append(b)
    return len(seen)==len(es)
cands=[]
for n,L in LATS.items():
    dia=[i for i,k in enumerate(L.ekind) if k=='dia']
    diam=mask(dia)
    for x in json.load(open(f'raw_{n}.json')):
        st=x['start'];k=x['k'];mode=x['mode']
        if x['nclass']>2: continue
        if mode==0 and k==1 and L.name!='R22': pass
        sols=x['allsols']
        uses=any((s&diam)!=0 for s in sols) and (st&diam)==0
        lateral=uses
        nm=bin(st).count('1')
        score=0
        score+=4 if x['nclass']==1 else 1
        score+=2.5 if lateral else 0
        score+=1.0 if k>=2 else 0
        score+=0.5 if mode==0 else 0
        if mode==2 and k<3: score-=1
        if mode==1 and k==1: score-=1.5
        if mode==0 and k==1: score-=.5
        if x['N']<2 and mode!=2: score-=1
        if nm<6: score-=1.5
        if x['N']==x['c0']: continue
        if not connected(L,st) or not connected(L,x['rep']): continue
        if k*2.5>nm and mode!=1: continue
        if mode==2 and x['c0']<3: continue
        if mode==1 and k>=3 and nm<5: continue
        # penalise huge change in count for add (too easy)
        score+=random.random()*0.9
        cands.append(dict(x,score=score,lateral=lateral,nm=nm))
print(len(cands))
# pick with quotas
quota={'R33':85,'R32':32,'R22':12,'T3':65,'T2':8}
picked=[];seen_start=collections.Counter();bucket=collections.Counter()
for n,q in quota.items():
    pool=sorted([c for c in cands if c['lat']==n],key=lambda c:(-int(c['lateral']) if n.startswith('R') else 0,-c['score']))
    if n.startswith('R'):
        lat_first=[c for c in pool if c['lateral']][:int(q*0.45)]
        rest=sorted([c for c in pool if c not in lat_first],key=lambda c:-c['score'])
        pool=lat_first+rest
    cnt=0
    for c in pool:
        if cnt>=q: break
        b=(c['lat'],c['mode'],c['k'],c['N'])
        if bucket[b]>=(4 if n=='R33' else 3): continue
        if seen_start[(n,c['start'])]>=1: continue
        # cap lateral share
        picked.append(c);cnt+=1;seen_start[(n,c['start'])]+=1;bucket[b]+=1
print(len(picked),collections.Counter((c['lat'],MODE[c['mode']],c['k']) for c in picked).most_common(40))
print('lateral',sum(c['lateral'] for c in picked),'unique',sum(c['nclass']==1 for c in picked))
# order shuffle then number
random.shuffle(picked)
out=[]
for i,c in enumerate(picked,1):
    out.append({'id':'P%03d'%i,'lat':c['lat'],'start':c['start'],'mode':MODE[c['mode']],'k':c['k'],'N':c['N'],'c0':c['c0'],
        'sol':c['rep'],'nclass':c['nclass'],'lateral':c['lateral']})
json.dump(out,open('cands.json','w'))
