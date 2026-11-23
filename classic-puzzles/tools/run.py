import random, subprocess, sys, json, itertools, collections
from lat import *
random.seed(int(sys.argv[2]) if len(sys.argv)>2 else 1)
def mask(es): 
    m=0
    for e in es: m|=1<<e
    return m
def bits(m): return [i for i in range(70) if m>>i&1]
def build(name):
    return {'R22':lambda:rect(2,2),'R32':lambda:rect(3,2),'R33':lambda:rect(3,3),'T2':lambda:tri(2),'T3':lambda:tri(3)}[name]()
def analyse(L,starts_n):
    pm=[mask(p[2]) for p in L.polys]
    syms=symmetries(L)
    def apply(pm_,m):
        r=0
        for i in bits(m): r|=1<<pm_[i]
        return r
    def canon(m): return min(apply(p,m) for p in syms)
    def count(m):
        c=0;cov=0
        for p in pm:
            if m&p==p:c+=1;cov|=p
        return c,(m&~cov)==0
    # starts
    seen={};tries=0
    nlat=sum(1 for k in L.ekind if k=='lat')
    while len(seen)<starts_n and tries<starts_n*60:
        tries+=1
        k=random.choice([1,2,2,3,3,4])
        cand=[p for p in L.polys if p[0]!='d'] if random.random()<.9 else L.polys
        m=0
        for p in random.sample(cand,min(k,len(cand))): m|=mask(p[2])
        c,v=count(m)
        if c<1 or not v: continue
        if bin(m).count('1')<5: continue
        cm=canon(m)
        if cm not in seen: seen[cm]=m
    starts=list(seen.values())
    inp=[f"{len(L.edges)} {len(pm)}"," ".join(map(str,pm)),str(len(starts))]+[str(s) for s in starts]
    out=subprocess.run(['./srch','4','4','5'],input="\n".join(inp),capture_output=True,text=True).stdout
    res=[]
    best=collections.defaultdict(dict)
    for line in out.splitlines():
        t=line.split();si,mode,k,c,n,ns=map(int,t[:6]);sols=list(map(int,t[6:6+ns]))
        key_=(si,mode,c)
        if key_ not in best or k<best[key_]['k']:
            best[key_]={'k':k,'n':n,'sols':sols}
    for (si,mode,c),d in best.items():
        st=starts[si]
        if d['n']>len(d['sols']): continue
        # stabiliser classes
        stab=[p for p in syms if apply(p,st)==st]
        classes=set()
        for s in d['sols']: classes.add(min(apply(p,s) for p in stab))
        res.append({'lat':L.name,'start':st,'mode':mode,'k':d['k'],'N':c,'c0':count(st)[0],'nclass':len(classes),'rep':min(classes),'allsols':d['sols']})
    return res
if __name__=='__main__':
    name=sys.argv[1];n=int(sys.argv[3]) if len(sys.argv)>3 else 300
    L=build(name)
    r=analyse(L,n)
    json.dump(r,open(f'raw_{name}.json','w'))
    print(name,len(r))
