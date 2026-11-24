import html
O='/home/user/Archive/instagram/reels/inserts-2026-11-24/inserts.html'
E=html.escape
pages=[]
def card(name,tag,lines,foot='',hl=None):
    body=''.join(f'<div class="ln">{l}</div>' for l in lines)
    pages.append((name,f'<div class="pg cd"><div class="tg">{E(tag)}</div><div class="cb">{body}</div>{f"<div class=ft>{E(foot)}</div>" if foot else ""}<div class="br">착한언니복덕방</div></div>'))
def q(name,num,text):
    pages.append((name,f'<div class="pg qq"><div class="qn">Q{num}</div><div class="qt">{E(text)}</div><div class="qs">집주인 vs 세입자</div><div class="br">착한언니복덕방</div></div>'))
def sms(name,day,msgs):
    b=''.join(f'<div class="bub {"me" if me else ""}">{E(t)}</div><div class="tm {"me" if me else ""}">{E(tm)}</div>' for me,t,tm in msgs)
    pages.append((name,f'<div class="pg sms"><div class="sb"><span>9:41</span><span>●●● ▮</span></div><div class="top"><div class="av">집</div>집주인</div><div class="chat"><div class="day">{E(day)}</div>{b}</div><div class="wm">예시 화면</div></div>'))
def reg(name,title,rows,cols,note=''):
    th=''.join(f'<th>{E(c)}</th>' for c in cols)
    tr=''
    for r in rows:
        cls=r.get('cls','')
        tr+=f'<tr class="{cls}">'+''.join(f'<td>{c}</td>' for c in r['c'])+'</tr>'
    pages.append((name,f'<div class="pg reg"><div class="rh">등기사항전부증명서 (말소사항 포함) - 집합건물</div><div class="ad">[집합건물] 서울특별시 ○○구 ○○동 000-00 ○○빌라 제3층 제301호</div><div class="sec">【 {E(title)} 】</div><table><tr>{th}</tr>{tr}</table>{f"<div class=nt>{note}</div>" if note else ""}<div class="wm">예시 화면 · 실제 등기부와 다를 수 있음</div></div>'))
def bill(name,title,rows,total,hlrow):
    tr=''.join(f'<tr class="{"hl" if i==hlrow else ""}"><td>{E(a)}</td><td>{E(b)}</td></tr>' for i,(a,b) in enumerate(rows))
    pages.append((name,f'<div class="pg bill"><div class="bt">{E(title)}</div><div class="bm">○○아파트 관리사무소 · 101동 1004호</div><table>{tr}<tr class="tot"><td>합계</td><td>{E(total)}</td></tr></table><div class="wm">예시 화면</div></div>'))

# ---- G5 전세 계약
card('G5-1 미납세금 열람','전세 고수 · 4번',['<b>집주인 밀린 세금</b>은','<span class=y>등기부에 안 나와요</span>','','보증금 1천만 원 초과','계약 후 ~ 입주 전까지','집주인 동의 없이','<b>전국 세무서</b>에서 열람'])
card('G5-2 전입 평일','전세 고수 · 5번',['대항력 =','<span class=y>전입 다음 날 0시</span>','','주말에 정부24로 신청하면','<b>월요일에 처리</b>돼요','→ 잔금은 평일로'])
card('G5-3 보증료 지원','전세 고수 · 6번',['전세보증보험료','<span class=y>지원받을 수 있어요</span>','','지자체별 조건 · 금액 달라요','예산 소진 시 마감'],'참고용 · 거주 지자체 공고 확인')
card('G5-4 안심전세앱 주의','전세 고수 · 2번',['집주인 보증사고 이력','<span class=y>안심전세앱</span>에서 조회','','단, 이름이 안 나온다고','100% 안전은 아니에요'])
# ---- G6 이사 나갈 때
bill('G6-1 관리비 고지서','2026년 10월 관리비 고지서',[('일반관리비','38,200원'),('청소비','9,800원'),('경비비','21,500원'),('승강기유지비','3,100원'),('장기수선충당금','12,340원'),('세대전기료','46,200원'),('수도료','18,900원')],'150,040원',4)
card('G6-2 수리 기준','세입자 고수 · 2번',['<b>전구·형광등</b> = 세입자','<span class=y>보일러·수도·누수</span> = 집주인','','소모품은 쓰는 사람','주요 설비는 집주인'],'계약서 특약이 있으면 특약이 우선')
card('G6-3 통상의 손모','세입자 고수 · 3번',['햇빛에 바랜 벽지','가구 자국 · 생활 마모','','<span class=y>통상의 손모</span>','= 원상복구 대상 아니에요'])
bill('G6-4 관리비 정산서','관리비 중간정산서 (전출)',[('정산 기간','11.01 ~ 11.24'),('관리비 (일할)','118,600원'),('수도·전기 검침','52,300원'),('장기수선충당금 납부 확인','148,080원 (12개월)')],'정산 완료',3)
# ---- G7 이사 40만원
card('G7-1 청년 이사비','이사 고수 · 1번',['서울시 청년','<span class=y>중개보수·이사비 최대 40만 원</span>','','만 19~39세 무주택','전월세 거래금액 2억 이하','생애 1회 · 실비 지원'],'다음 모집 공고는 청년몽땅정보통에서 확인')
card('G7-2 종량제봉투','이사 고수 · 3번',['남은 쓰레기봉투','<span class=y>버리지 마세요</span>','','새 동네 주민센터에 가져가면','스티커 붙여 쓰거나','새 봉투로 교환'],'구마다 방식이 달라요 · 주민센터 확인')
card('G7-3 이사 정산','이사 고수 · 5번',['나가는 날','<span class=y>계량기 숫자 사진</span>','','전기 · 수도 · 가스','이사 정산 신청'])
# ---- G8 전세 만기
card('G8-1 묵시적 갱신','전세 고수 · 1번',['자동 연장(묵시적 갱신)돼도','세입자는 <span class=y>언제든 해지 통보</span>','','통보하고','<b>3개월 뒤</b> 계약 끝'])
card('G8-2 갱신요구권','전세 고수 · 2번',['갱신요구권','<span class=y>1번 · 증액 최대 5%</span>','','보증금 5억이면','최대 2,500만 원까지'])
sms('G8-3 문자 만기 통보','2027년 1월 28일 (목)',[(True,'사장님, 3월 31일 계약 만기에 나가겠습니다. 보증금 반환 일정 부탁드립니다.','오후 2:14'),(False,'네 알겠습니다~','오후 3:02')])
card('G8-4 증액 확정일자','전세 고수 · 4번',['보증금 올렸으면','<span class=y>새 계약서 + 확정일자</span>','','올린 금액은','새 확정일자부터 순위'])
card('G8-5 임차권등기','전세 고수 · 7번',['보증금 못 받았으면','<span class=y>임차권등기부터</span>','','등기부에 뜬 걸 확인하고','그다음에 이사'])
reg('G8-6 등기부 소유자 변경','갑 구',[{'c':['1','소유권보존','2021년3월2일<br>제1234호','','소유자 김○○']},{'c':['2','소유권이전','2026년9월14일<br>제56789호','2026년8월20일<br>매매','소유자 이○○'],'cls':'hl'}],['순위번호','등기목적','접수','등기원인','권리자 및 기타사항'],'<b>집주인 바뀜</b> → 만기 전에 등기부 확인 (열람 700원)')
# ---- C1 판정 퀴즈
for i,t in enumerate(['보일러가 갑자기 안 돌아가요','형광등이 나갔어요','윗집에서 물이 새서 천장에 얼룩이 생겼어요','햇빛에 벽지가 바랬어요','고양이가 벽지를 뜯었어요','창문 결로 때문에 곰팡이가 생겼어요','옵션 에어컨이 고장 났어요','도어락 배터리가 다 됐어요'],1):
    q(f'C1-{i} 질문',i,t)
# ---- B3 연봉 6천
card('B3-1 DSR','대출 고수 · 2번',['연봉 6,000만 원','× DSR 40%','','<span class=y>1년 원리금 2,400만 원</span>','= 한 달 약 200만 원'],'참고용 · 실제 한도는 은행 심사')
card('B3-2 대출 4억','대출 고수 · 3번',['대출 4억 · 연 4% · 30년','','<span class=y>한 달 약 191만 원</span>','','스트레스 DSR 적용 시','한도는 더 줄어요'],'참고용 · 내 조건은 언니집 AI로')
card('B3-3 부대비용','대출 고수 · 4번',['6억 집 살 때 더 드는 돈','','취득세 약 660만 원','중개보수(상한) 약 240만 원','','<span class=y>= 약 900만 원 + 이사비</span>'],'취득세 6억 이하 1주택 85㎡ 이하 1.1% 기준 · 중개보수 부가세 별도')
# ---- B4 등기부
reg('B4-1 표제부 근생','표 제 부 ( 전유부분의 건물의 표시 )',[{'c':['1','2019년5월10일','제3층 제301호','철근콘크리트구조<br><b>제2종근린생활시설</b><br>29.8㎡'],'cls':'hl'}],['표시번호','접수','건물번호','건물내역'],'원룸처럼 보여도 용도가 <b>근린생활시설</b>이면 전세대출·보증보험이 막힐 수 있어요')
reg('B4-2 갑구 신탁','갑 구 ( 소유권에 관한 사항 )',[{'c':['2','소유권이전','2022년6월3일','2022년6월3일<br>신탁','수탁자 ○○부동산신탁 주식회사'],'cls':'hl'},{'c':['','신탁','','','신탁원부 제2022-0000호']}],['순위번호','등기목적','접수','등기원인','권리자 및 기타사항'],'<b>신탁</b> → 집주인이 진짜 주인이 아닐 수 있어요 (신탁사 동의 확인)')
reg('B4-3 을구 임차권등기','을 구 ( 소유권 이외의 권리에 관한 사항 )',[{'c':['<s>3</s>','<s>주택임차권</s>','<s>2024년4월2일</s>','<s>2024년3월28일<br>임차권등기명령</s>','<s>임차보증금 금180,000,000원<br>임차권자 박○○</s>'],'cls':'hl'},{'c':['4','3번주택임차권등기말소','2024년10월15일','2024년10월11일<br>해지','']}],['순위번호','등기목적','접수','등기원인','권리자 및 기타사항'],'<b>말소사항 포함</b>으로 떼면 지워진 <b>임차권등기</b>까지 보여요 → 전 세입자가 보증금 못 받고 나갔던 집')
reg('B4-4 갑구 가압류','갑 구 ( 소유권에 관한 사항 )',[{'c':['3','가압류','2026년7월8일','2026년7월5일<br>서울중앙지방법원의<br>가압류결정','청구금액 금50,000,000원<br>채권자 ○○캐피탈'],'cls':'hl'}],['순위번호','등기목적','접수','등기원인','권리자 및 기타사항'],'<b>가압류·압류</b> 있으면 → 풀린 등기부 보고 계약')
# ---- B5 월세 연말정산
card('B5-1 최대 170만','월세 고수 · 1번',['월세 1년 <b>1,000만 원</b>까지','× 15~17%','','<span class=y>최대 170만 원</span> 돌려받기'],'2026년 연말정산 기준 · 참고용')
card('B5-2 예시 계산','월세 고수 · 1번',['월세 60만 원 × 12개월','= 720만 원','× 17%','','<span class=y>= 약 122만 원</span>'],'총급여 5,500만 원 이하 17% · 8천만 원 이하 15%')
card('B5-3 조건','월세 고수 · 2~4번',['무주택 세대주','총급여 8천만 원 이하','<span class=y>계약서 주소 = 등본 주소</span>','집주인 동의 필요 없음','놓친 건 5년 안에 신청'],'국민주택규모 또는 기준시가 4억 이하 · 홈택스 기준 확인')

CSS='''@import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css");
@font-face{font-family:G;src:url(https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansBold.woff) format('woff');font-weight:700}
*{margin:0;padding:0;box-sizing:border-box}body{background:#777;font-family:Pretendard,sans-serif}
.pg{width:1080px;height:1920px;position:relative;overflow:hidden;margin-bottom:20px}
.br{position:absolute;bottom:60px;left:0;right:0;text-align:center;font-size:26px;opacity:.5}
.wm{position:absolute;right:30px;bottom:24px;font-size:24px;color:rgba(0,0,0,.28)}
.cd{background:#1E2A3A;color:#fff;display:flex;flex-direction:column;justify-content:center;padding:0 90px}
.cd .tg{position:absolute;top:150px;left:90px;background:#FFD84D;color:#1E2A3A;font:700 34px G;padding:12px 26px;border-radius:99px}
.cd .ln{font:700 66px/1.45 Pretendard;text-align:center;min-height:40px}.cd .ln b{color:#fff}.cd .y{color:#FFD84D}
.cd .ft{position:absolute;bottom:130px;left:90px;right:90px;text-align:center;font-size:30px;color:#a9b4c3;line-height:1.5}
.qq{background:#FBF7EE;color:#1E2A3A;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 80px}
.qq .qn{font:700 120px G;color:#E0A800}.qq .qt{font:700 88px/1.35 G;text-align:center;margin-top:40px;word-break:keep-all}.qq .qs{margin-top:60px;font-size:40px;color:#8a8577}
.sms{background:#fff;color:#111}.sms .sb{height:110px;display:flex;justify-content:space-between;align-items:flex-end;padding:0 60px 16px;font-size:40px;font-weight:600}
.sms .top{height:160px;border-bottom:2px solid #eee;display:flex;align-items:center;padding:0 50px;gap:28px;font-size:48px;font-weight:700}.sms .av{width:96px;height:96px;border-radius:50%;background:#dfe6ef;display:flex;align-items:center;justify-content:center;font-size:40px;color:#5a6b80}
.sms .chat{padding:60px 50px}.sms .day{text-align:center;color:#999;font-size:32px;margin:10px 0 40px}
.sms .bub{max-width:820px;background:#f1f2f4;border-radius:44px;padding:40px 46px;font-size:44px;line-height:1.55}.sms .bub.me{background:#3478f6;color:#fff;margin-left:auto}
.sms .tm{color:#aaa;font-size:28px;margin:12px 0 44px 20px}.sms .tm.me{text-align:right;margin-right:20px}
.reg{background:#fff;color:#111;padding:110px 50px}.reg .rh{text-align:center;font-size:40px;font-weight:800}.reg .ad{font-size:30px;margin:26px 0 40px;color:#333;text-align:center}
.reg .sec{text-align:center;font-size:40px;font-weight:800;background:#f3f3ee;padding:18px;border:2px solid #333;border-bottom:0}
.reg table{width:100%;border-collapse:collapse;font-size:30px}.reg th,.reg td{border:2px solid #333;padding:18px 10px;text-align:center;vertical-align:top;line-height:1.4}.reg th{background:#fafaf6}
.reg tr.hl td{background:#fff3f2}.reg tr.hl{outline:8px solid #ff3b30;outline-offset:-4px}.reg s{color:#d33}
.reg .nt{margin-top:60px;background:#1E2A3A;color:#fff;border-radius:28px;padding:40px 44px;font-size:42px;line-height:1.5}.reg .nt b{color:#FFD84D}
.bill{background:#fff;color:#111;padding:160px 70px}.bill .bt{text-align:center;font-size:58px;font-weight:800}.bill .bm{text-align:center;font-size:32px;color:#666;margin:20px 0 60px}
.bill table{width:100%;border-collapse:collapse;font-size:44px}.bill td{padding:30px 16px;border-bottom:2px solid #eee}.bill td:last-child{text-align:right}
.bill tr.hl td{background:#FFF1A8;font-weight:800}.bill tr.hl{outline:8px solid #ff3b30;outline-offset:-4px}.bill tr.tot td{font-weight:800;border-top:4px solid #111}'''
doc='<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>'+CSS+'</style></head><body>'+''.join(f'<div data-n="{E(n)}">{h}</div>' for n,h in pages)+'</body></html>'
open(O,'w').write(doc); print(len(pages))
