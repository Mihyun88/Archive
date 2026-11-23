import json,math
SP='/tmp/claude-0/-home-user/85dc4d50-7164-518f-8e7f-5e232a70a7a7/scratchpad'
cheap={'동대문':11.07,'은평':10.9,'금천':9.79,'구로':9.31,'도봉':8.65,'강북':8.5,'성북':7.45,'중랑':7.25,'노원':6.8,'서대문':5.9,'관악':5.8}
def col(v): return '#FFC400' if v<6 else '#FFE27A' if v<8 else '#BFD8F2' if v<10 else '#8FB0D6'
def won(v):
    e=int(v); m=round((v-e)*10000); return f"{e}억 {m:,}만" if m else f"{e}억"
order=sorted(cheap,key=lambda g:-cheap[g])
geo=json.load(open(SP+'/map/seoul.json'))
rings_all=lambda f:(f['geometry']['coordinates'] if f['geometry']['type']=='Polygon' else [r for poly in f['geometry']['coordinates'] for r in poly])
pts=[c for f in geo['features'] for r in rings_all(f) for c in r]
minx=min(p[0] for p in pts);maxx=max(p[0] for p in pts);miny=min(p[1] for p in pts);maxy=max(p[1] for p in pts)
k=math.cos(math.radians(37.55));W,H=1000,830
sc=min(W/((maxx-minx)*k),H/(maxy-miny))
def P(x,y): return ((x-minx)*k*sc+(W-(maxx-minx)*k*sc)/2,(maxy-y)*sc+(H-(maxy-miny)*sc)/2)
base=[];hot=[];lab=[]
off={'동대문구':(-18,10),'중랑구':(22,-12),'금천구':(-40,30),'관악구':(20,0),'서대문구':(-10,10),'구로구':(-10,0)}
for f in geo['features']:
    nm=f['properties']['name']; g=nm[:-1] if nm!='중구' else '중구'
    d='';allp=[]
    for r in rings_all(f):
        q=[P(*c) for c in r];allp+=q;d+='M'+' L'.join(f'{a:.1f},{b:.1f}' for a,b in q)+'Z'
    cx=sum(a for a,b in allp)/len(allp)+off.get(nm,(0,0))[0];cy=sum(b for a,b in allp)/len(allp)+off.get(nm,(0,0))[1]
    base.append(f'<path d="{d}" fill="#EDEAE3" stroke="#fff" stroke-width="2.5"/>')
    if g in cheap:
        i=order.index(g)
        hot.append(f'<path id="h{i}" class="h" d="{d}" fill="{col(cheap[g])}" stroke="#fff" stroke-width="2.5"/>')
        lab.append(f'<g id="l{i}" class="l" transform="translate({cx:.0f},{cy:.0f})"><g class="li"><text y="-6" class="gn">{nm}</text><text y="22" class="gp">{won(cheap[g])}~</text></g></g>')
    else:
        lab.append(f'<text x="{cx:.0f}" y="{cy+6:.0f}" class="gn gx">{nm}</text>')
svg=f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}">{"".join(base)}{"".join(hot)}{"".join(lab)}</svg>'
N=len(order)
html=f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:G;src:url(https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansBold.woff) format('woff');font-weight:700}}
@font-face{{font-family:P;src:url(https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/woff2/Pretendard-Bold.woff2) format('woff2');font-weight:700}}
@font-face{{font-family:P;src:url(https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/woff2/Pretendard-Regular.woff2) format('woff2');font-weight:400}}
*{{margin:0;box-sizing:border-box}}body{{width:1080px;height:1920px;background:#FBF7EE;font-family:P,sans-serif;color:#1E2A3A;overflow:hidden}}
.top{{position:absolute;top:250px;left:0;right:0;text-align:center}}.top .t1{{font:700 50px G;color:#6b665c}}.top .t2{{font:700 80px G;margin-top:14px}}.top .t2 b{{color:#E0A800}}
.map{{position:absolute;top:560px;left:40px}}
.h{{transform-box:fill-box;transform-origin:center;opacity:0}}.l{{opacity:0}}
.gn{{font:700 25px P,sans-serif;text-anchor:middle;fill:#1E2A3A}}.gp{{font:700 24px P,sans-serif;text-anchor:middle;fill:#1E2A3A}}.gx{{fill:#b3ad9f;font-weight:400}}
.end{{position:absolute;top:1480px;left:0;right:0;text-align:center;font:700 64px G;opacity:0}}.end b{{background:#FFC400;padding:4px 18px;border-radius:14px}}
.src{{position:absolute;bottom:200px;left:0;right:0;text-align:center;font-size:26px;color:#8a8577}}
</style></head><body>
<div class="top"><div class="t1">국토부 실거래 · 34평(84㎡)</div><div class="t2">서울 34평, <b>어디까지</b> 될까?</div></div>
<div class="map">{svg}</div><div class="end" id="end">5억대는 <b>딱 두 곳</b></div>
<div class="src">2026년 6~11월 거래 중간값 · 착한언니복덕방</div>
<script>
const N={N};const S=[];let t0=0.8;for(let i=0;i<N;i++){{S.push(t0);t0+=(i>=N-2?0.9:0.5)}}window.S=S;window.TEND=t0+1.8;
function ease(x){{x=Math.min(1,Math.max(0,x));const c=1.70158;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)}}
window.R=function(t){{for(let i=0;i<N;i++){{const p=(t-S[i])/0.28;const h=document.getElementById('h'+i),l=document.getElementById('l'+i);
 if(p<=0){{h.style.opacity=0;l.style.opacity=0;continue}}const e=ease(p),a=Math.min(1,p*1.6);
 const big=i>=N-2?1.0:0.6;h.style.opacity=a;h.style.transform=`scale(${{1+big*0.12*(1-Math.min(1,p))}})`;
 l.style.opacity=a;l.querySelector('.li').setAttribute('transform',`scale(${{0.4+0.6*e}})`)}}
 const pe=(t-(S[N-1]+0.6))/0.35;const en=document.getElementById('end');en.style.opacity=Math.max(0,Math.min(1,pe));en.style.transform=`scale(${{0.8+0.2*ease(pe)}})`}};
</script></body></html>'''
open(SP+'/vid34.html','w').write(html)
print(order)
