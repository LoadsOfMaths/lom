import json, math, html
from lat import *
from run import build, mask, bits
C=json.load(open('cands.json'))
LATS={}
def lat(n):
    if n not in LATS: LATS[n]=build(n)
    return LATS[n]
S=46
def svg(L,present,added=0,removed=0):
    xs=[n[0] for n in L.nodes];ys=[n[1] for n in L.nodes]
    x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
    M=0.35
    w=(x1-x0+2*M)*S;h=(y1-y0+2*M)*S
    out=[f'<svg viewBox="0 0 {w:.0f} {h:.0f}" width="{w*0.8:.0f}" height="{h*0.8:.0f}" xmlns="http://www.w3.org/2000/svg">']
    P=lambda n:((L.nodes[n][0]-x0+M)*S,(L.nodes[n][1]-y0+M)*S)
    # lattice dots
    for i,n in enumerate(L.nodes):
        pass
    def stick(e,cls):
        a,b=L.edges[e]
        pa,pb=P(a),P(b)
        if pa[0]>pb[0]+1e-6 or (abs(pa[0]-pb[0])<1e-6 and pa[1]>pb[1]): pa,pb=pb,pa
        dx,dy=pb[0]-pa[0],pb[1]-pa[1];l=math.hypot(dx,dy);k=5
        x1_,y1_=pa[0]+dx/l*k,pa[1]+dy/l*k;x2_,y2_=pb[0]-dx/l*k,pb[1]-dy/l*k
        if cls=='gone':
            return f'<line x1="{x1_:.1f}" y1="{y1_:.1f}" x2="{x2_:.1f}" y2="{y2_:.1f}" stroke="#c0392b" stroke-width="2.2" stroke-dasharray="4 4" opacity=".75"/>'
        col='#2e9e5b' if cls=='new' else '#e4b568'
        s=f'<line x1="{x1_:.1f}" y1="{y1_:.1f}" x2="{x2_:.1f}" y2="{y2_:.1f}" stroke="{col}" stroke-width="6.5" stroke-linecap="round"/>'
        hc='#1d6e40' if cls=='new' else '#b9302a'
        s+=f'<circle cx="{x1_+dx/l*2:.1f}" cy="{y1_+dy/l*2:.1f}" r="4.3" fill="{hc}"/>'
        return s
    for e in range(len(L.edges)):
        if removed>>e&1: out.append(stick(e,'gone'))
    for e in range(len(L.edges)):
        if present>>e&1:
            out.append(stick(e,'new' if added>>e&1 else 'old'))
    out.append('</svg>')
    return ''.join(out)
def squares(L): return 'square' if L.kind=='sq' else 'triangle'
def text(c):
    L=lat(c['lat']);w=squares(L);k=c['k'];N=c['N']
    ms=f"{k} match" if k==1 else f"{k} matches"
    ws=f"{N} {w}" + ("" if N==1 else "s")
    if c['mode']=='move': t=f"Move <b>{ms}</b> to make exactly <b>{ws}</b>."
    elif c['mode']=='add': t=f"Add <b>{ms}</b> to make exactly <b>{ws}</b>."
    else: t=f"Take away <b>{ms}</b> to leave exactly <b>{ws}</b>."
    if L.kind=='sq': t+=" Squares of every size, and at any angle, count."
    else: t+=" Triangles of every size, pointing either way, count."
    t+=" Every match must belong to a "+w+"."
    return t
rows=[];data=[]
for c in C:
    L=lat(c['lat']);st=c['start'];so=c['sol']
    added=so&~st;removed=st&~so
    start_svg=svg(L,st)
    sol_svg=svg(L,so,added,removed)
    note=[]
    note.append(f"Starts with {c['c0']} {squares(L)}{'' if c['c0']==1 else 's'}")
    if c['lateral']: note.append("tilted answer")
    if st&mask([i for i,k in enumerate(L.ekind) if k=='dia']): note.append("tilted square in the start")
    if c['nclass']>1: note.append(f"{c['nclass']} different answers")
    dm=mask([i for i,k in enumerate(L.ekind) if k=='dia'])
    tilt=1 if (st&dm) else 0
    rows.append(f'''<div class="row" data-id="{c['id']}" data-tilt="{tilt}"><div class="id">{c['id']}<small>{c['lat']}</small></div>
<div class="pic">{start_svg}</div>
<div class="txt"><p>{text(c)}</p><p class="meta">{' · '.join(note)}</p></div>
<div class="pic sol">{sol_svg}</div>
<label class="sw"><input type="checkbox"><span></span></label></div>''')
    data.append({k:c[k] for k in ('id','lat','start','sol','mode','k','N','c0','nclass','lateral')})
page=open('review_tpl.html').read().replace('%%ROWS%%','\n'.join(rows)).replace('%%N%%',str(len(C)))
open('review.html','w').write(page)
json.dump({'lattices':{n:{'nodes':l.nodes,'edges':l.edges,'kind':l.kind,'ekind':l.ekind,'polys':[[p[0],p[1],p[2]] for p in l.polys]} for n,l in LATS.items()},'candidates':data},open('candidates.json','w'))
print(len(rows))
