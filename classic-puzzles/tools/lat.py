import math, itertools, json
D=math.sqrt(.5)
R3=math.sqrt(3)/2
def key(p): return (round(p[0],4),round(p[1],4))
class Lat:
    def __init__(s,name,kind):
        s.name=name;s.kind=kind;s.nodes=[];s.nidx={};s.edges=[];s.eidx={};s.ekind=[];s.polys=[]
    def node(s,p):
        k=key(p)
        if k not in s.nidx: s.nidx[k]=len(s.nodes);s.nodes.append([k[0],k[1]])
        return s.nidx[k]
    def edge(s,p,q,kind='lat'):
        a,b=s.node(p),s.node(q)
        k=(min(a,b),max(a,b))
        if k not in s.eidx: s.eidx[k]=len(s.edges);s.edges.append([a,b]);s.ekind.append(kind)
        return s.eidx[k]
    def getedge(s,p,q):
        a,b=s.nidx.get(key(p)),s.nidx.get(key(q))
        if a is None or b is None: return None
        return s.eidx.get((min(a,b),max(a,b)))
    def chain(s,p,q):
        """unit edges along a straight segment of integer length; None if any missing"""
        L=round(math.hypot(q[0]-p[0],q[1]-p[1]))
        out=[]
        for i in range(L):
            a=(p[0]+(q[0]-p[0])*i/L,p[1]+(q[1]-p[1])*i/L)
            b=(p[0]+(q[0]-p[0])*(i+1)/L,p[1]+(q[1]-p[1])*(i+1)/L)
            e=s.getedge(a,b)
            if e is None: return None
            out.append(e)
        return out
def rect(W,H,dia=True):
    L=Lat('R%d%d'%(W,H),'sq')
    for y in range(H+1):
        for x in range(W): L.edge((x,y),(x+1,y))
    for x in range(W+1):
        for y in range(H): L.edge((x,y),(x,y+1))
    ndia=[]
    if dia:
        for x in range(1,W):
            for y in range(1,H):
                pts=[(x+D,y),(x,y+D),(x-D,y),(x,y-D)]
                es=[L.edge(pts[i],pts[(i+1)%4],'dia') for i in range(4)]
                L.polys.append(('d',1,es))
    for s in range(1,min(W,H)+1):
        for x in range(W-s+1):
            for y in range(H-s+1):
                es=[];ok=True
                for a,b in [((x,y),(x+s,y)),((x+s,y),(x+s,y+s)),((x+s,y+s),(x,y+s)),((x,y+s),(x,y))]:
                    c=L.chain(a,b)
                    if c is None: ok=False;break
                    es+=c
                if ok: L.polys.append(('s',s,es))
    return L
def tri(T):
    L=Lat('T%d'%T,'tri')
    P=lambda a,b:(a+b/2,-b*R3)
    for a in range(T+1):
        for b in range(T+1-a):
            if a+b+1<=T: L.edge(P(a,b),P(a+1,b))
            if a+b+1<=T: L.edge(P(a,b),P(a,b+1))
            if a-1>=0 and a-1+b+1<=T: L.edge(P(a,b),P(a-1,b+1))
    for Lz in range(1,T+1):
        for a in range(T+1):
            for b in range(T+1):
                if a+b+Lz<=T:  # up
                    es=[];ok=True
                    for p,q in [((a,b),(a+Lz,b)),((a+Lz,b),(a,b+Lz)),((a,b+Lz),(a,b))]:
                        c=L.chain(P(*p),P(*q))
                        if c is None: ok=False;break
                        es+=c
                    if ok: L.polys.append(('u',Lz,es))
                if a+b+2*Lz<=T:  # down
                    es=[];ok=True
                    for p,q in [((a+Lz,b),(a,b+Lz)),((a,b+Lz),(a+Lz,b+Lz)),((a+Lz,b+Lz),(a+Lz,b))]:
                        c=L.chain(P(*p),P(*q))
                        if c is None: ok=False;break
                        es+=c
                    if ok: L.polys.append(('v',Lz,es))
    return L
def symmetries(L):
    """edge permutations for the symmetry group of the lattice"""
    xs=[n[0] for n in L.nodes];ys=[n[1] for n in L.nodes]
    cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2
    ms=[]
    if L.kind=='sq':
        for k in range(4):
            for f in (0,1):
                ms.append((k,f))
        def tr(p,m):
            x,y=p[0]-cx,p[1]-cy
            k,f=m
            if f:x=-x
            for _ in range(k): x,y=-y,x
            return (x+cx,y+cy)
    else:
        # centroid of triangle
        cx=sum(xs)/len(xs) if False else (min(xs)+max(xs))/2
        # use nodes mean (triangle lattice is symmetric about its centroid)
        cx=sum(xs)/len(xs);cy=sum(ys)/len(ys)
        for k in range(3):
            for f in (0,1): ms.append((k,f))
        def tr(p,m):
            x,y=p[0]-cx,p[1]-cy
            k,f=m
            if f:x=-x
            c,s=math.cos(2*math.pi*k/3),math.sin(2*math.pi*k/3)
            return (c*x-s*y+cx,s*x+c*y+cy)
    perms=[]
    for m in ms:
        pm=[]
        for (a,b) in L.edges:
            p=tr(L.nodes[a],m);q=tr(L.nodes[b],m)
            e=L.getedge(p,q)
            pm.append(e)
        if None in pm: continue
        perms.append(pm)
    return perms
if __name__=='__main__':
    for L in (rect(2,2),rect(3,2),rect(3,3),tri(2),tri(3)):
        print(L.name,len(L.nodes),len(L.edges),len(L.polys),len(symmetries(L)))
