import json, sys
chosen=json.load(open('/mnt/user-data/uploads/73d5f480-chosen-puzzles.json'))['chosen']
D=json.load(open('/home/claude/lom/classic-puzzles/review/candidates.json'))
LAT=D['lattices'];C={c['id']:c for c in D['candidates']}
MODE={'move':0,'add':1,'take':2}
raw={}
for n in LAT:
    for x in json.load(open(f'raw_{n}.json')):
        raw[(n,x['start'],x['mode'],x['N'])]=x
def edges_of(m,E): return [i for i in range(E) if m>>i&1]
lats={};puz=[]
for pid in chosen:
    c=C[pid];L=LAT[c['lat']];E=len(L['edges'])
    x=raw[(c['lat'],c['start'],MODE[c['mode']],c['N'])]
    assert x['k']==c['k']
    dia=sum(1<<i for i,k in enumerate(L['ekind']) if k=='dia')
    sols=[edges_of(s,E) for s in x['allsols']]
    tilt=bool(c['start']&dia) or any(s&dia for s in x['allsols'])
    puz.append({'id':pid,'lat':c['lat'],'kind':L['kind'],'mode':c['mode'],'k':c['k'],'N':c['N'],'start':edges_of(c['start'],E),'sols':sols,'tilt':tilt})
    if c['lat'] not in lats:
        nodes=[[round(a,4),round(-b if L['kind']=='tri' else b,4)] for a,b in L['nodes']]
        lats[c['lat']]={'kind':L['kind'],'nodes':nodes,'edges':L['edges'],'polys':[p[2] for p in L['polys']]}
print(len(puz),{k:sum(1 for p in puz if (p['kind'],p['mode'])==k) for k in set((p['kind'],p['mode']) for p in puz)})
print('tilt',sum(p['tilt'] for p in puz),'maxsols',max(len(p['sols']) for p in puz))
json.dump({'lats':lats,'puz':puz},open('gen_data.json','w'),separators=(',',':'))
import os;print(os.path.getsize('gen_data.json'))
