import json,math,html
SP='/tmp/claude-0/-home-user/85dc4d50-7164-518f-8e7f-5e232a70a7a7/scratchpad'
OUT='/home/user/Archive/instagram/resources/seoul-34'
# (구, 단지, 84㎡ 억, 기간 note)
D=[('관악','국제산장',5.8,'b'),('서대문','홍은동 극동',5.9,'b'),('관악','삼성산주공3단지',6.5,'b'),('노원','공릉 한보에센시티',6.8,'a'),
('중랑','용마한신',7.25,'a'),('성북','정릉풍림아이원',7.45,'a'),('관악','관악산휴먼시아2단지',7.55,'a'),('노원','월계 주공2',7.64,'a'),('서대문','홍은동 두산',7.8,'b'),
('강북','에스케이북한산시티',8.5,'a'),('노원','상계주공4',8.5,'a'),('도봉','창동주공3(해등마을)',8.65,'a'),('서대문','홍은동벽산',8.93,'a'),('노원','공릉 풍림',9.3,'a'),('구로','현대홈타운',9.31,'a'),('금천','남서울힐스테이트',9.79,'a'),('성북','돈암 한진',9.85,'a'),
('구로','현대',10.67,'a'),('구로','한마을',10.85,'a'),('은평','백련산파크자이',10.9,'a'),('노원','상계주공3',11.0,'a'),('동대문','이문 쌍용',11.07,'a'),('성북','석관 두산',11.32,'a'),('노원','월계 한진한화그랑빌',11.5,'a'),('관악','벽산블루밍',11.7,'a'),('성북','길음뉴타운2단지푸르지오',11.75,'a'),('관악','봉천우성',11.88,'a'),('서대문','홍제원현대',12.0,'a'),('은평','백련산에스케이뷰아이파크',12.08,'a'),('노원','중계 주공5',12.38,'a'),('동대문','장안현대홈타운',12.5,'a'),('성북','길음동부센트레빌',12.5,'a'),('관악','관악드림(동아)',12.6,'a'),('관악','관악푸르지오',12.75,'a'),('금천','금천롯데캐슬골드파크1차',12.9,'a')]
BANDS=[('5억대',5,6,'#FFC400'),('6~7억대',6,8,'#FFE27A'),('8~9억대',8,10,'#BFD8F2'),('10~11억대',10,12,'#8FB0D6'),('12억대',12,13,'#6C8DB8')]
def band(v):
    for i,(n,a,b,c) in enumerate(BANDS):
        if a<=v<b: return i
def won(v):
    e=int(v); m=round((v-e)*10000)
    return f"{e}억 {m:,}만".replace(' 0만','') if m else f"{e}억"
cheap={}
for g,n,v,_ in D:
    if g not in cheap or v<cheap[g][1]: cheap[g]=(n,v)
geo=json.load(open(SP+'/map/seoul.json'))
pts=[c for f in geo['features'] for ring in (f['geometry']['coordinates'] if f['geometry']['type']=='Polygon' else [r for poly in f['geometry']['coordinates'] for r in poly]) for c in ring]
minx=min(p[0] for p in pts);maxx=max(p[0] for p in pts);miny=min(p[1] for p in pts);maxy=max(p[1] for p in pts)
k=math.cos(math.radians(37.55));W,H=960,800
sc=min(W/((maxx-minx)*k),H/(maxy-miny))
def P(x,y): return ((x-minx)*k*sc+(W-(maxx-minx)*k*sc)/2, (maxy-y)*sc+(H-(maxy-miny)*sc)/2)
paths=[];labels=[]
for f in geo['features']:
    g=f['properties']['name'][:-1] if f['properties']['name']!='중구' else '중구'
    rings=f['geometry']['coordinates'] if f['geometry']['type']=='Polygon' else [r for poly in f['geometry']['coordinates'] for r in poly]
    col='#EDEAE3'
    if g in cheap: col=BANDS[band(cheap[g][1])][3]
    d=''
    allp=[]
    for r in rings:
        q=[P(*c) for c in r]; allp+=q
        d+='M'+' L'.join(f'{a:.1f},{b:.1f}' for a,b in q)+'Z'
    paths.append(f'<path d="{d}" fill="{col}" stroke="#fff" stroke-width="2.5"/>')
    cx=sum(a for a,b in allp)/len(allp); cy=sum(b for a,b in allp)/len(allp)
    off={'동대문구':(-18,10),'중랑구':(22,-12),'금천구':(-40,30),'관악구':(20,0),'서대문구':(-10,10),'구로구':(-10,0)}.get(f['properties']['name'],(0,0)); cx+=off[0]; cy+=off[1]
    nm=f['properties']['name']
    if g in cheap:
        labels.append(f'<text x="{cx:.0f}" y="{cy-6:.0f}" class="gn">{nm}</text><text x="{cx:.0f}" y="{cy+20:.0f}" class="gp">{won(cheap[g][1])}~</text>')
    else:
        labels.append(f'<text x="{cx:.0f}" y="{cy+6:.0f}" class="gn gx">{nm}</text>')
svg=f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}">{"".join(paths)}{"".join(labels)}</svg>'
def mon(L): r=0.04/12; return round(L*1e8*r/(1-(1+r)**-360)/10000)
CSS='''@font-face{font-family:G;src:url(https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansBold.woff) format('woff');font-weight:700}
@font-face{font-family:P;src:url(https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/woff2/Pretendard-Regular.woff2) format('woff2');font-weight:400}
@font-face{font-family:P;src:url(https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/woff2/Pretendard-Bold.woff2) format('woff2');font-weight:700}
*{box-sizing:border-box;margin:0}body{font-family:P,sans-serif;color:#1E2A3A;background:#FBF7EE}
.pg{width:1080px;height:1350px;padding:80px 72px;position:relative;overflow:hidden;background:#FBF7EE;page-break-after:always}
.tag{display:inline-block;background:#FFD84D;border-radius:99px;padding:10px 26px;font:700 30px G;margin-bottom:28px}
h1{font:700 76px/1.25 G;letter-spacing:-1px}h2{font:700 56px/1.3 G;margin-bottom:12px}.lead{font-size:32px;line-height:1.6;color:#4a5566;margin-top:24px}
.foot{position:absolute;left:72px;right:72px;bottom:56px;font-size:22px;color:#8a8577;display:flex;justify-content:space-between}
.gn{font:700 22px P,sans-serif;text-anchor:middle;fill:#1E2A3A}.gp{font:700 21px P,sans-serif;text-anchor:middle;fill:#1E2A3A}.gx{fill:#a9a397;font-weight:400}
.leg{display:flex;gap:18px;flex-wrap:wrap;margin:18px 0 8px;font-size:26px}.leg span{display:flex;align-items:center;gap:8px}.leg i{width:26px;height:26px;border-radius:6px;display:inline-block}
table{width:100%;border-collapse:collapse;font-size:30px;margin-top:24px}td{padding:20px 8px;border-bottom:2px solid #ECE6D8}td.v{text-align:right;font-weight:700;white-space:nowrap}td.g{color:#8a8577;width:130px}
.box{background:#fff;border-radius:28px;padding:36px 40px;margin-top:28px;box-shadow:0 4px 0 #ECE6D8}
.big{font:700 44px G}.note{font-size:24px;color:#8a8577;line-height:1.6;margin-top:18px}'''
foot='<div class="foot"><span>착한언니복덕방 · 서울에서 부동산 12년</span><span>{n}/9</span></div>'
pages=[]
stats='<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:28px">'+''.join(f'<div style="background:{c};color:#1E2A3A;border-radius:24px;padding:24px 30px"><div style="font:700 28px G">34평 {n}</div><div style="font:700 50px G;margin-top:6px">{sum(1 for x in D if a<=x[2]<b)}곳</div></div>' for n,a,b,c in [BANDS[0],BANDS[1],BANDS[2],('10억 이상',10,13,'#8FB0D6')])+'</div>'
pages.append(f'''<div class="pg" style="background:#1E2A3A;color:#fff"><div class="tag" style="color:#1E2A3A">착한언니 자료</div>
<h1 style="color:#fff">내 예산으로<br>서울 34평<br><span style="color:#FFD84D">어디까지 될까?</span></h1>
<p class="lead" style="color:#cfd6e0">5억대부터 12억대까지<br>실제로 거래된 서울 34평 단지 35곳</p>
<div class="box" style="background:#26364a;box-shadow:none;color:#fff;font-size:28px;line-height:1.7">📍 국토교통부 실거래가 · 전용 84㎡(34평)<br>📅 2026년 6~11월 거래 중간값<br>✍️ 거래가 활발했던 단지 위주로 골랐어요</div>{stats}
<div class="foot" style="color:#8fa0b5"><span>착한언니복덕방 · 서울에서 부동산 12년</span><span>1/9</span></div></div>''')
leg=''.join(f'<span><i style="background:{c}"></i>{n}</span>' for n,a,b,c in BANDS)+'<span><i style="background:#EDEAE3"></i>이 자료에 없음</span>'
pages.append(f'''<div class="pg"><h2>구별로 보면,<br>34평 시작 가격은 여기부터</h2><div class="leg">{leg}</div>{svg}
<p class="note" style="margin-top:0">구 이름 아래 숫자 = 이 자료 안에서 가장 낮은 34평 단지 가격</p>{foot.format(n=2)}</div>''')
def band_page(i,n):
    nm,a,b,c=BANDS[i]; rows=[x for x in D if a<=x[2]<b]
    tr=''.join(f'<tr><td class="g">{g}</td><td>{html.escape(nm_)}</td><td class="v">{won(v)}</td></tr>' for g,nm_,v,_ in rows)
    fs='26px' if len(rows)>12 else '30px'; pad='12px 8px' if len(rows)>12 else '20px 8px'
    return f'''<div class="pg"><div class="tag" style="background:{c}">{nm}</div><h2>34평 {nm}로 볼 수 있는 곳</h2>
<table style="font-size:{fs}">{tr.replace('<td','<td style="padding:'+pad+'"')}</table>{foot.format(n=n)}</div>'''
for i in range(5): pages.append(band_page(i,3+i))
rows=''.join(f'<tr><td>대출 {L}억 받으면</td><td class="v">한 달 약 {mon(L)}만 원</td></tr>' for L in (3,4,5,6))
pages.append(f'''<div class="pg"><h2>대출 받으면<br>한 달에 얼마 나갈까?</h2><div class="box"><table style="margin-top:0">{rows}</table></div>
<p class="note">계산 기준: 연 4.0% · 30년 · 원리금균등 상환 (예시)<br>대출 가능 금액·금리는 사람마다, 규제마다 달라요.<br>집 살 때는 취득세(6억 이하 1주택 약 1.1%)와 중개보수도 따로 들어요.<br>내 조건으로 계산 → unnizip.kr/app (언니집 AI)</p>{foot.format(n=8)}</div>''')
pages.append(f'''<div class="pg" style="background:#1E2A3A;color:#fff"><div class="tag" style="color:#1E2A3A">상담</div>
<h1 style="color:#fff;font-size:64px">내 예산에 맞는<br>첫 집, 같이 골라요</h1>
<div class="box" style="background:#26364a;box-shadow:none;color:#fff;font-size:30px;line-height:1.8">💬 카카오톡 채널 「착한언니복덕방」<br>📞 02-364-4080 · 02-707-3434<br>🏠 서울 아파트 상담 · 오피스텔은 신촌·서대문·마포<br>⏰ 예약 손님 우선 상담</div>
<p class="note" style="color:#8fa0b5">이 자료는 참고용이에요. 가격은 실제 거래 중간값이라 층·향·동에 따라 달라요.<br>대출·세금은 은행·세무사 상담을 받으세요.<br>출처: 국토교통부 실거래가 공개 (신림 국제산장·삼성산주공3단지, 홍은동 극동·두산은 2026.9~11월 거래 기준)</p>
<div class="foot" style="color:#8fa0b5"><span>착한언니복덕방 · 서울에서 부동산 12년</span><span>9/9</span></div></div>''')
doc=f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>내 예산 서울 34평 지도 · 착한언니복덕방</title><style>{CSS}</style></head><body>'+''.join(pages)+'</body></html>'
open(SP+'/seoul34_pages.html','w').write(doc)
print(len(pages))
