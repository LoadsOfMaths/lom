import json, math, itertools
d=json.load(open('candidates.json'))
LAT=d['lattices']
R3=3**.5/2
for n,l in LAT.items():
    if l['kind']=='tri':
        l['nodes']=[[x,round(y/R3)*R3] for x,y in l['nodes']]
def segs(lat,m):
    out=[]
    for i,(a,b) in enumerate(lat['edges']):
        if m>>i&1: out.append((tuple(lat['nodes'][a]),tuple(lat['nodes'][b])))
    return out
def inter(s,t):
    (x1,y1),(x2,y2)=s;(x3,y3),(x4,y4)=t
    den=(x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
    if abs(den)<1e-9: return None
    px=((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4))/den
    py=((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4))/den
    def on(p,a,b): return min(a[0],b[0])-1e-7<=p[0]<=max(a[0],b[0])+1e-7 and min(a[1],b[1])-1e-7<=p[1]<=max(a[1],b[1])+1e-7
    if on((px,py),*s) and on((px,py),*t): return (px,py)
def covered(p,q,S):
    # is segment pq covered by union of collinear segments in S
    dx,dy=q[0]-p[0],q[1]-p[1];L=math.hypot(dx,dy)
    iv=[]
    for a,b in S:
        # collinear?
        cr=lambda u,v,w:(v[0]-u[0])*(w[1]-u[1])-(v[1]-u[1])*(w[0]-u[0])
        if abs(cr(p,q,a))/L>1e-6 or abs(cr(p,q,b))/L>1e-6: continue
        ta=((a[0]-p[0])*dx+(a[1]-p[1])*dy)/(L*L);tb=((b[0]-p[0])*dx+(b[1]-p[1])*dy)/(L*L)
        iv.append((min(ta,tb),max(ta,tb)))
    iv.sort();cur=0
    for lo,hi in iv:
        if lo>cur+1e-6: break
        cur=max(cur,hi)
    return cur>=1-1e-6
def shapes(lat,m,kind):
    S=segs(lat,m)
    pts={}
    def add(p): pts[(round(p[0],3),round(p[1],3))]=p
    for s in S: add(s[0]);add(s[1])
    for s,t in itertools.combinations(S,2):
        p=inter(s,t)
        if p: add(p)
    P=list(pts.values())
    found=set();used=[]
    for A,B in itertools.permutations(P,2):
        L=math.hypot(B[0]-A[0],B[1]-A[1])
        if L<0.99: continue
        if kind=='sq':
            dx,dy=B[0]-A[0],B[1]-A[1]
            C=(B[0]-dy,B[1]+dx);D=(A[0]-dy,A[1]+dx)
            vs=[A,B,C,D]
        else:
            ca,sa=0.5,math.sqrt(3)/2
            dx,dy=B[0]-A[0],B[1]-A[1]
            C=(A[0]+ca*dx-sa*dy,A[1]+sa*dx+ca*dy);vs=[A,B,C]
        if any((round(v[0],3),round(v[1],3)) not in pts for v in vs): continue
        ok=all(covered(vs[i],vs[(i+1)%len(vs)],S) for i in range(len(vs)))
        if ok:
            key=frozenset((round(v[0],4),round(v[1],4)) for v in vs)
            if key not in found: found.add(key);used.append(vs)
    return found,S,used
def loose(S,used):
    for s in S:
        mid=((s[0][0]+s[1][0])/2,(s[0][1]+s[1][1])/2)
        ok=False
        for vs in used:
            for i in range(len(vs)):
                a,b=vs[i],vs[(i+1)%len(vs)]
                dx,dy=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dy)
                t=((mid[0]-a[0])*dx+(mid[1]-a[1])*dy)/(L*L)
                dist=abs((mid[0]-a[0])*dy-(mid[1]-a[1])*dx)/L
                if dist<1e-6 and -1e-6<=t<=1+1e-6: ok=True;break
            if ok:break
        if not ok:return True
    return False
bad=0
for c in d['candidates']:
    lat=LAT[c['lat']];kind=lat['kind']
    f0,S0,u0=shapes(lat,c['start'],kind);f1,S1,u1=shapes(lat,c['sol'],kind)
    ok=len(f0)==c['c0'] and len(f1)==c['N'] and not loose(S0,u0) and not loose(S1,u1)
    # move count check
    st,so=c['start'],c['sol'];a=bin(so&~st).count('1');r=bin(st&~so).count('1')
    mv={'move':(c['k'],c['k']),'add':(c['k'],0),'take':(0,c['k'])}[c['mode']]
    if (a,r)!=mv: ok=False
    if not ok: bad+=1;print('MISMATCH',c['id'],len(f0),c['c0'],len(f1),c['N'],(a,r),mv)
print('checked',len(d['candidates']),'bad',bad)
