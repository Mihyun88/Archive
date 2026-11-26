"""착한언니 블로그 양식 → 스마트에디터 붙여넣기용 HTML 생성기.

ellarang 블로그 실제 글(2026.10, 25편)의 에디터 구성을 따라 만든다.
- 전체 가운데 정렬 · 본문 16px · 강조 19px
- 소제목 = 1칸 표 (왼쪽 6px #555 선, 19px 굵게, "1. ~")
- 데이터 표 머리줄 = 남색 #1a2f5e + 흰 글씨
- 강조색: 보라 #7b4fd6 · 분홍 #e0157a · 형광 #fff3a0
- 마무리 3단: 이웃추가(청록 #13a89e) · 카톡(#ffe812) · 인스타(#f3d6ff) + 구분선 + 안내문

사용: python3 tools/blog_paste.py  → naver/paste/*.html 생성
"""
import html, os

OUT = os.path.join(os.path.dirname(__file__), "..", "naver", "paste")
P = "#7b4fd6"; PK = "#e0157a"; HL = "#fff3a0"; NAVY = "#1a2f5e"
FONT = "font-family:'나눔바른고딕',NanumBarunGothic,'Apple SD Gothic Neo',sans-serif;"


def esc(s):
    return html.escape(s, quote=False)


def rich(s):
    """**굵게**, [[보라]], {{분홍}}, ==형광== 간단 마크업."""
    import re
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\[\[(.+?)\]\]", rf'<b><span style="color:{P}">\1</span></b>', s)
    s = re.sub(r"\{\{(.+?)\}\}", rf'<b><span style="color:{PK}">\1</span></b>', s)
    s = re.sub(r"==(.+?)==", rf'<span style="background-color:{HL}">\1</span>', s)
    return s


def p(s="", size=16, color=None, extra=""):
    st = f"text-align:center;font-size:{size}px;line-height:1.8;margin:0;{FONT}"
    if color:
        st += f"color:{color};"
    body = rich(s) if s else "&nbsp;"
    if s.startswith("✔"):
        body = f'<b><span style="color:{P}">✔</span></b>' + body[1:]
    return f'<p style="{st}{extra}">{body}</p>'


import re as _re
_MK = _re.compile(r"\*\*.+?\*\*|\[\[.+?\]\]|\{\{.+?\}\}|==.+?==")


def vis(s):
    """마크업 기호 뺀 실제 글자 수"""
    return len(_re.sub(r"\*\*|\[\[|\]\]|\{\{|\}\}|==", "", s))


_CLAUSE = _re.compile(r"(,|—|:|지만|는데|은데|면서|니까|라서|아서|어서|해서|도록|려면|이라|하라|이하라|이면|라면|다면|으면|하면|되면|때|땐|고|아니라|아니고|대신)$")
_PART = _re.compile(r"(은|는|이|가|을|를|에|에서|에게|도|만|과|와|로|으로|의|까지|부터|보다|처럼|,)$")


def _plain(w):
    return _re.sub(r"\*\*|\[\[|\]\]|\{\{|\}\}|==", "", w).replace("\x00", " ")


def _split_long(words, lim):
    """문장을 의미 단위로 둘씩 나눔 — 연결어미·쉼표 뒤 우선, 그다음 조사 뒤, 양쪽 길이가 비슷하게"""
    if vis(" ".join(words)) <= lim or len(words) < 2:
        return [words]
    best, bi = None, 1
    for i in range(1, len(words)):
        L, R = vis(" ".join(words[:i])), vis(" ".join(words[i:]))
        tail = _plain(words[i - 1])
        score = abs(L - R) * 0.6
        if _CLAUSE.search(tail):
            score -= 9
        elif _PART.search(tail):
            score -= 4
        if min(L, R) <= 4:
            score += 25
        if best is None or score < best:
            best, bi = score, i
    return _split_long(words[:bi], lim) + _split_long(words[bi:], lim)


def _wordwise(s):
    """**굵게** [[보라]] {{분홍}} 안의 공백을 기준으로 단어마다 표시를 다시 감싸서, 줄바꿈이 가능하게"""
    for o, c in (("**", "**"), ("[[", "]]"), ("{{", "}}")):
        pat = _re.compile(_re.escape(o) + r"(.+?)" + _re.escape(c))
        s = pat.sub(lambda m: " ".join(f"{o}{w}{c}" for w in m.group(1).split(" ") if w), s)
    return s


def wrap(s, lim=19):
    """모바일(네이버 앱 한 줄 약 19~20자)용 문맥 줄바꿈.
    문장마다 새 줄 → 긴 문장은 연결어미·쉼표·조사 뒤에서, 양쪽 길이를 맞춰 나눔.
    형광(==)·괄호 ( ) 안은 자르지 않음"""
    if not s or vis(s) <= lim:
        return [s]
    t = _wordwise(s)
    t = _re.sub(r"==.+?==", lambda m: m.group(0).replace(" ", "\x00"), t)
    t = _re.sub(r"\([^()]*\)", lambda m: m.group(0).replace(" ", "\x00"), t)
    if t.startswith("✔ "):
        t = "✔\x00" + t[2:]
    words = [w for w in t.split(" ") if w]
    sents, cur = [], []
    for w in words:
        cur.append(w)
        if _re.search(r"[.?!]$", _plain(w)):
            sents.append(cur); cur = []
    if cur:
        sents.append(cur)
    out = []
    for sw in sents:
        for part in _split_long(sw, lim):
            out.append(" ".join(part))
    res = []
    for l in out:
        l = l.replace("\x00", " ")
        for o, c in (("**", "**"), ("[[", "]]"), ("{{", "}}")):
            l = l.replace(f"{c} {o}", " ")
        res.append(l)
    return res


def hlpara(s, bg, fg=None, size=16, lim=19):
    """배경색 강조 문장을 모바일 줄 단위로 나눠 줄마다 형광 칠하기"""
    st = f"text-align:center;font-size:{size}px;line-height:1.9;margin:0;{FONT}"
    fgc = f"color:{fg};" if fg else ""
    return "".join(f'<p style="{st}"><span style="background-color:{bg};{fgc}">&nbsp;{rich(l)}&nbsp;</span></p>' for l in wrap(s, lim))


def para(s, size=16, color=None, lim=19):
    if size <= 14 and " · " in s:
        # 출처·안내처럼 '·'로 나열된 작은 글씨는 항목마다 줄을 나눔
        out = []
        for part in s.split(" · "):
            out += wrap(part, lim)
        return "".join(p(l, size, color) for l in out)
    return "".join(p(l, size, color) for l in wrap(s, lim))


class Post:
    def __init__(self, slug, title, meta):
        self.slug, self.title, self.meta, self.b = slug, title, meta, []

    # --- blocks ---
    def blank(self):
        self.b.append(("body", p()))

    def text(self, *lines, size=16, color=None):
        lim = 19 if size >= 16 else 25
        long_ = any(vis(l) > lim for l in lines) or any(l.startswith("✔") for l in lines)
        out = ""
        for i, l in enumerate(lines):
            prev = _re.sub(r"\*\*|\]\]|\}\}|==", "", lines[i - 1]).rstrip() if i else ""
            if i and long_ and (l.startswith("✔") or _re.search(r"(요|다|\.|\?|!|\))$", prev)):
                out += p()
            out += para(l, size, color, lim)
        self.b.append(("body", out + p()))

    def greet(self):
        self.b.append(("body",
            f'<p style="text-align:center;font-size:16px;line-height:1.8;margin:0;{FONT}">안녕하세요. '
            f'<b><span style="color:#ffffff;background-color:#ff2d8a">착한언니복덕방</span></b> '
            f'신촌자이엘라&amp;마포그랑자이 (착한언니) 부동산입니다.</p>'
            f'<p style="text-align:center;font-size:15px;line-height:1.8;margin:0;color:#666666;{FONT}">'
            f'2014년 겨울부터 신촌 한 자리, <b>12년째</b> 마포·서대문만 보고 있어요.</p>'))

    def voice(self, *qs):
        """손님 질문 (회색 따옴표)"""
        self.b.append(("body", p().join(para(f"“{q}”", 16, "#999999") for q in qs) + p()))

    def head(self, n, t):
        cell = (f'<table style="width:100%;border-collapse:collapse;margin:24px 0 12px;">'
                f'<tr><td style="border-top:1px solid #e5e5e5;border-right:1px solid #e5e5e5;'
                f'border-bottom:1px solid #e5e5e5;border-left:6px solid #555555;padding:10px 14px;'
                f'font-size:19px;{FONT}"><b>{n}. {esc(t)}</b></td></tr></table>')
        self.b.append(("head", p() + cell))
        self.cur_head = t

    def checks(self, *items, color=P):
        self.b.append(("body", p().join(para(f"✔ {i}") for i in items) + p()))

    def numbered(self, title, *items):
        self.b.append(("body", p(f"[[{title}]]", 17) + p() + p().join(para(f"✔ {i}") for i in items) + p()))

    def quote(self, text, kind="기본"):
        """스마트에디터 인용구는 붙여넣기로 생기지 않아요 → 인용구 넣고 이 문장만 붙여넣기."""
        box = (f'<div style="border-left:4px solid #222;margin:16px auto;max-width:560px;padding:10px 16px;'
               f'text-align:center;font-size:19px;{FONT}"><b>{rich(text)}</b></div>')
        self.b.append(("quote", box, kind, text))

    def table(self, header, rows, note=None):
        th = "".join(f'<td style="background-color:{NAVY};color:#ffffff;border:1px solid #d9d9d9;padding:8px;'
                     f'text-align:center;font-size:15px;{FONT}"><b>{esc(h)}</b></td>' for h in header)
        tr = "".join("<tr>" + "".join(
            f'<td style="border:1px solid #d9d9d9;padding:8px;text-align:center;font-size:15px;{FONT}">{rich(c)}</td>'
            for c in r) + "</tr>" for r in rows)
        t = f'<table style="width:100%;border-collapse:collapse;margin:12px 0;"><tr>{th}</tr>{tr}</table>'
        if note:
            t += para(note, 13, "#888888", 26)
        self.b.append(("table", t + p()))

    def photo(self, desc):
        """촬영할 사진 → 본문엔 안 넣고 오른쪽 목록으로"""
        self.todo_photos = getattr(self, "todo_photos", []) + [(getattr(self, "cur_head", "도입"), desc)]

    def image(self, rel, desc):
        """공식 도면 등 실제 이미지: 미리보기에 표시 + 업로드 안내"""
        self.b.append(("photo",
            f'<p style="text-align:center;margin:12px 0 4px"><img src="{rel}" alt="{esc(desc)}" style="max-width:100%;border:1px solid #ddd"></p>'
            + para(f"▲ {desc}", 13, "#999999", 26) + p()))
        self.images = getattr(self, "images", []) + [(rel, desc)]

    def fill(self, desc):
        """직접 채울 칸 (지어 쓰지 않음)"""
        self.b.append(("fill", p(f"✍️ [직접 채우기: {desc}]", 15, "#d0021b") + p()))

    def hl(self, s):
        self.b.append(("body", para(f"=={s}==", 17) + p()))

    def note(self, *lines):
        """착한언니 현장 노트 — 모든 글 필수. 내용이 없으면 직접 채울 칸으로."""
        head = (f'<table style="width:100%;border-collapse:collapse;margin:24px 0 8px;"><tr>'
                f'<td style="background-color:#fff7fb;border:2px solid {PK};border-radius:8px;padding:12px 14px;text-align:center;{FONT}">'
                f'<b><span style="color:{PK};font-size:18px">📝 착한언니 현장 노트</span></b></td></tr></table>')
        if lines:
            self.b.append(("note", p() + head + "".join(para(l) + p() for l in lines)))
        else:
            self.b.append(("fill", p() + head + p("✍️ [직접 채우기: 이 글 주제로 사무소에서 실제로 받은 문의·현장에서 본 것·거래하며 느낀 점 2~3줄 — 가격 전망 없이]", 15, "#d0021b") + p()))
            self.note_todo = True

    def outro(self, follow, extra_note):
        if not any(b[0] == "note" or (b[0] == "fill" and "현장 노트" in b[1]) for b in self.b):
            self.note()
        self.b.append(("body",
            p() +
            f'<table style="width:100%;border-collapse:collapse;margin:8px 0;"><tr><td style="background-color:{NAVY};border-radius:10px;padding:16px 14px;text-align:center;{FONT}">'
            f'<span style="color:#ffde59;font-size:18px"><b>📊 착한언니복덕방 실거래 도구</b></span><br>'
            f'<span style="color:#ffffff;font-size:15px;line-height:1.8">단지&nbsp;시세&nbsp;·&nbsp;내&nbsp;예산&nbsp;진단&nbsp;리포트<br>신촌&nbsp;오피스텔&nbsp;·&nbsp;청약까지<br><br>중개사가&nbsp;매일&nbsp;보는&nbsp;시세표,<br><b>그대로&nbsp;열어&nbsp;드려요</b></span><br>'
            f'<a href="https://unnizip.kr/app/" style="color:#ffffff;font-size:16px"><b>👉 unnizip.kr/app</b></a></td></tr></table>'
            + p() +
            hlpara(follow, "#13a89e", "#ffffff")
            + p() + "@@CTA@@"
            + f'<p style="text-align:center;font-size:14px;line-height:1.8;margin:0;{FONT}"><a href="http://pf.kakao.com/_xcxoBxnX">pf.kakao.com/_xcxoBxnX</a></p>'
            + p() +
            hlpara("인스타그램 **@goodsister4080**", "#f3d6ff", lim=30) + hlpara("이런 내용을 카드뉴스로 정리해요", "#f3d6ff", lim=30)
            + p() + p("쉽고 꾸준하게, 꼭 부자되세요!")
            + p("────────────────", 13, "#bbbbbb")
            + para(extra_note, 13, "#888888", 24)))

    OFFICES = {
        "zaiella": ["중개사무소: 신촌자이엘라부동산공인중개사사무소",
                    "대표 공인중개사: 신수경 · 등록번호 11410-2019-00062",
                    "소재지: 서울특별시 서대문구 대현동 104-36, B101호 · 연락처: 02-364-4080"],
        "grandxi": ["중개사무소: 마포그랑자이(착한언니)부동산공인중개사사무소",
                    "대표 공인중개사: 신혜선 · 등록번호 11440-2022-00085",
                    "소재지: 서울특별시 마포구 대흥로 175, 상가4동 102호 일부 (대흥동) · 연락처: 02-707-3434",
                    "서울시 지정 글로벌 부동산중개사무소 · English available"],
    }

    def signature(self, office="zaiella"):
        """office: zaiella = 오피스텔·신촌·이대 글 / grandxi = 아파트·마포 글 (실제 중개 사무소 기준)"""
        self.office = office
        cta = {"zaiella": "🏠 방 구하기 문의는 카카오톡 채널 **착한언니복덕방**에 「원하는 동네·예산·입주 날짜」만 남겨 주세요. 맞는 방을 골라 드려요.",
               "grandxi": "🏢 매수·매도·전세 상담은 카카오톡 채널 **착한언니복덕방**에 「단지·평형·예산」을 남겨 주세요. 동·층까지 비교해 드려요."}[office]
        cta = hlpara(cta, "#ffe812")
        self.b = [(b[0], b[1].replace("@@CTA@@", cta)) + tuple(b[2:]) for b in self.b]
        lines = ["착한언니복덕방 | 신촌자이엘라 & 마포그랑자이 부동산",
                 "4인 전원 공인중개사 · 중개보조원 없음"] + self.OFFICES[office] + ["카카오톡 채널: pf.kakao.com/_xcxoBxnX"]
        self.b.append(("body", "".join(para(l, 13, "#666666", 24) for l in lines)))

    # --- render ---
    def render(self, side):
        body_html = []
        for blk in self.b:
            kind, h = blk[0], blk[1]
            if kind == "quote":
                body_html.append(f'<div class="q" data-kind="{blk[2]}">{h}</div>')
            else:
                body_html.append(h)
        article = "\n".join(body_html)
        quotes = [b for b in self.b if b[0] == "quote"]
        qlist = "".join(
            f'<li><span class="qk">인용구 · {esc(k)}</span> {esc(t.replace("**",""))} '
            f'<button class="mini" data-t="{html.escape(t.replace("**",""), quote=True)}">문장 복사</button></li>'
            for _, _, k, t in quotes)
        side_html = "".join(f"<li>{rich(x)}</li>" for x in side)
        ims = getattr(self, "images", [])
        imgs = ("<div class=\"card\"><h3>이미지 내려받기 (직접 업로드)</h3><ul>" + "".join(
            f'<li><a href="{r}" download>{esc(d)}</a></li>' for r, d in ims) + "</ul></div>") if ims else ""
        tp = getattr(self, "todo_photos", [])
        if tp:
            imgs += ("<div class=\"card\"><h3>📷 촬영해서 넣을 사진</h3><ul>" + "".join(
                f"<li><b>{esc(h)}</b> 섹션: {esc(d)}</li>" for h, d in tp) + "</ul></div>")
        return PAGE.format(title=esc(self.title), meta=self.meta, article=article, qlist=qlist, side=side_html, imgs=imgs)


PAGE = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · 붙여넣기</title>
<style>
body{{margin:0;background:#f4f4f2;font-family:-apple-system,"Apple SD Gothic Neo",sans-serif;color:#222}}
.bar{{position:sticky;top:0;z-index:5;background:#03c75a;color:#fff;padding:10px 16px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}}
.bar b{{font-size:15px;margin-right:auto}}
.bar button{{font:inherit;font-size:13px;border:0;border-radius:99px;padding:7px 14px;background:#fff;color:#03a14a;font-weight:700;cursor:pointer}}
.wrap{{max-width:1100px;margin:0 auto;padding:16px;display:grid;grid-template-columns:minmax(0,700px) 1fr;gap:16px}}
@media(max-width:900px){{.wrap{{grid-template-columns:1fr}}}}
.paper{{background:#fff;border:1px solid #e3e3e3;border-radius:8px;padding:28px 22px}}
.q{{outline:2px dashed #f5a623;outline-offset:4px;border-radius:4px;margin:8px 0}}
.side{{font-size:13.5px;line-height:1.6}}
.card{{background:#fff;border:1px solid #e3e3e3;border-radius:8px;padding:14px 16px;margin-bottom:12px}}
.card h3{{margin:0 0 8px;font-size:14px}}
.card ul{{padding-left:18px;margin:0}}.card li{{margin:4px 0}}
.qk{{display:inline-block;font-size:11px;font-weight:700;background:#fdebd0;color:#b9770e;border-radius:4px;padding:1px 6px}}
.mini{{font:inherit;font-size:11px;border:1px solid #ccc;background:#fff;border-radius:99px;padding:2px 8px;cursor:pointer}}
.toast{{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#222;color:#fff;padding:8px 16px;border-radius:99px;font-size:13px;display:none}}
</style></head><body>
<div class="bar"><b>📋 {title}</b><button id="all">본문 전체 복사</button><button id="plain">텍스트만 복사</button></div>
<div class="wrap">
<div class="paper" id="art">
{article}
</div>
<div class="side">
<div class="card"><h3>붙여넣는 법 (PC 스마트에디터 ONE)</h3><ul>
<li>① <b>본문 전체 복사</b> → 글쓰기 화면 본문에 <b>Ctrl+V</b></li>
<li>② 표·굵게·글자색·형광·가운데 정렬은 그대로 들어가요 (붙여넣은 뒤 표 색이 빠지면 표 선택 → 셀 배경색만 다시 지정)</li>
<li>③ <span class="qk">주황 점선</span> 문장은 <b>인용구</b>로 바꿔 주세요: 붙여넣은 문장 지우고 → 상단 [인용구] → 오른쪽 목록의 「문장 복사」로 붙여넣기</li>
<li>④ 사진은 붙여넣기로 안 들어가요 → 회색 「▲ 설명」 줄 바로 위에 오른쪽 「이미지 내려받기」 파일을 올려 주세요 (▲ 줄은 사진 설명으로 그대로 두면 돼요) · ✍️ 빨간 줄 = 직접 채울 자리</li>
<li>⑤ 맨 아래 법정 표시는 「내 템플릿」에 저장해 둔 서명과 같아요 — 템플릿을 썼다면 이 부분은 지워도 돼요</li>
</ul></div>
<div class="card"><h3>인용구로 바꿀 문장</h3><ul>{qlist}</ul></div>
{imgs}
<div class="card"><h3>발행 정보</h3><ul>{side}</ul></div>
<div class="card" style="font-size:12px;color:#777">{meta}</div>
</div></div>
<div class="toast" id="toast">복사됐어요</div>
<script>
const t=document.getElementById('toast');function ok(m){{t.textContent=m;t.style.display='block';setTimeout(()=>t.style.display='none',1600)}}
async function copyRich(el){{
  const h=el.innerHTML, x=el.innerText;
  try{{await navigator.clipboard.write([new ClipboardItem({{'text/html':new Blob([h],{{type:'text/html'}}),'text/plain':new Blob([x],{{type:'text/plain'}})}})]);ok('본문을 복사했어요 → 스마트에디터에 Ctrl+V');}}
  catch(e){{const r=document.createRange();r.selectNodeContents(el);const s=getSelection();s.removeAllRanges();s.addRange(r);document.execCommand('copy');s.removeAllRanges();ok('본문을 복사했어요');}}
}}
document.getElementById('all').onclick=()=>copyRich(document.getElementById('art'));
document.getElementById('plain').onclick=()=>navigator.clipboard.writeText(document.getElementById('art').innerText).then(()=>ok('텍스트만 복사했어요'));
document.querySelectorAll('.mini').forEach(b=>b.onclick=()=>navigator.clipboard.writeText(b.dataset.t).then(()=>ok('인용구 문장을 복사했어요')));
</script></body></html>"""


# ======================================================================
def the_classy():
    a = Post("2026-11-the-classy", "마포 더클래시 실거래가 2026",
             "데이터: 국토교통부 아파트 매매·전월세 실거래 (2025.11~2026.10 계약분, 해제 제외, 2026.11.2 조회) · 작성 규칙 CONTENT WORK MASTER v1.2")
    a.fill("도입 — 더클래시 상담에서 실제로 자주 듣는 질문 1개 (예시: “18평이 15억이면 신혼집으로 괜찮을까요?”)")
    a.blank(); a.greet(); a.blank()
    a.text("더클래시는 저희 사무실에서 가장 가까운 단지라", "실제로 거래를 가장 많이 하는 곳 중 하나예요.")
    a.text("그래서 오늘은 **최근 1년 실거래와 전세**를 평형별로 정리하고,", "숫자만으로는 안 보이는 부분까지 같이 짚어볼게요.")
    a.photo("더클래시 단지 전경 (직접 촬영)")
    a.quote("**한 줄 요약** 18평 15억 · 59㎡ 21억 · 84㎡ 24억 5,500만 원 (최근 1년 실거래 중위값)", "기본")

    a.head(1, "더클래시, 어떤 단지인가요?")
    a.table(["항목", "내용"], [["위치", "서울 마포구 아현동"], ["준공", "2022년"],
                              ["세대수", "✍️ 직접 확인 후 입력"], ["가까운 역", "✍️ 아현역·애오개역·이대역 도보 ○분"],
                              ["주요 평형", "18평(전용 43㎡) · 59㎡ · 84㎡"]])
    a.photo("지도 삽입 (단지 + 사무실)")

    a.head(2, "평형별 매매 실거래, 이렇게 거래됐어요")
    a.table(["평형", "거래", "중위값", "범위", "최근 거래"],
            [["**18평 (43㎡)**", "13건", "[[15억]]", "11억 3,000 ~ 15억 8,000", "26.09 · 15억 3,000 (3층)"],
             ["**59㎡**", "19건", "[[21억]]", "20억 3,500 ~ 22억 6,000", "26.07 · 21억 9,000 (5층)"],
             ["**84㎡**", "6건", "[[24억 5,500]]", "23억 9,500 ~ 25억 5,000", "26.08 · 25억 5,000 (6층)"]],
            note="국토부 실거래 · 2025.11~2026.10 계약분 · 계약 해제 거래 제외 · 9~10월분은 신고 기한이 남아 늘어날 수 있어요")
    a.text("✔ 18평 최저 11억 3,000만 원(2026년 5월, 3층) 1건은", "다른 거래와 차이가 커서 {{특수 거래일 수 있어요.}}", "이 1건을 빼면 12건 모두 14억 5,000만 ~ 15억 8,000만 원 사이예요.")
    a.text("✔ 거래는 **2026년 4~5월에 몰렸고**, 6월 이후로는 한 달 1~3건으로 줄었어요.", "그래도 84㎡ 최고가(25억 5,000만 원)는 8월에 나왔어요.")
    a.fill("3월 이전 매매 신고가 없는 이유 — 현장에서 아시는 내용이 있으면 한 단락 (없으면 이 줄 삭제)")

    a.head(3, "18평(전용 43㎡), 누가 사면 좋을까요?")
    a.text("블로그에 [[「마포더클래시 18평」]]으로 찾아오시는 분이 많아서 따로 정리했어요.")
    a.checks("매매 중위 **15억** · 전세 중위 **6억 5,000만 원**", "최근 3개월 신규 전세 중위는 6억 9,500만 원이에요")
    a.fill("구조 (방·욕실·수납)")
    a.fill("이런 분께 맞아요 (1~2인 가구 / 신혼 첫 집 / 마포 입성 후 갈아타기 등)")
    a.fill("아쉬운 점 1가지 — 솔직하게")
    a.photo("18평 내부 2~3장")

    a.head(4, "전세는 지금 얼마에 계약되나요?")
    a.table(["평형", "전세 건수", "전세 중위", "최근 3개월 중위", "전세가율"],
            [["18평 (43~44㎡)", "26건", "6억 5,000", "6억 9,500", "약 43%"],
             ["59㎡", "63건", "8억 5,000", "8억 7,250", "약 40%"],
             ["84㎡", "38건", "10억 5,000", "10억 5,000", "약 43%"]],
            note="전세 = 월세 0원 계약만 · 전세가율 = 전세 중위 ÷ 매매 중위")
    a.hl("전세가율이 40% 초반이라 갭투자보다는 실거주 매수 위주 단지예요.")
    a.text("그런데 이 숫자만 보고 판단하시면 안 됩니다.", "같은 59㎡라도 **동·층·향**에 따라 실제 호가는 꽤 차이가 나요.", "계약 전에는 지금 나와 있는 매물로 다시 비교하세요.")

    a.head(5, "착한언니 현장 노트 — 더클래시 살 때 이 3가지")
    a.numbered("① 동·라인별 차이", "✍️ 조망·소음·엘리베이터 동선 (직접 채우기)")
    a.numbered("② 관리비와 커뮤니티", "✍️ 실제 관리비 수준 (면적·월 기준)")
    a.numbered("③ 세입자 있는 집을 살 때", "전세 만기일과 계약갱신청구권 사용 여부를 먼저 확인해요",
               "보증금 반환 일정과 잔금일을 같이 맞춰야 해요")

    a.head(6, "자주 묻는 질문")
    a.text("**Q. 더클래시 18평 매매가는 얼마인가요?**",
           "최근 1년 실거래 13건 중위값은 15억 원이고,", "13건 중 12건이 14억 5,000만 ~ 15억 8,000만 원 사이에서 거래됐어요.")
    a.blank()
    a.text("**Q. 더클래시 84㎡ 최고가는?**", "2026년 8월 6층 25억 5,000만 원이에요.")
    a.fill("상담에서 자주 받는 질문 1개 + 답")

    a.head(7, "정리하면")
    a.text("✔ 18평 **15억** · 59㎡ **21억** · 84㎡ **24억 5,500만 원** (1년 실거래 중위)",
           "✔ 전세가율 40% 초반 → 실거주 매수 중심 단지",
           "✔ 4~5월에 거래가 몰렸고, 하반기는 거래가 줄었지만 84㎡ 최고가는 8월",
           "==숫자보다 먼저, 내 예산과 입주 시점부터 정리해 보세요.==")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 마포·서대문 단지 실거래를 이어서 정리할게요.",
            "국토교통부 실거래가 공개시스템(2025.11~2026.10 계약분, 2026.11.2 조회) 기준이에요 · 개별 거래의 동·호수는 공개하지 않아요 · 실제 매물 조건은 상담 시점에 다시 확인해 드려요")
    a.signature("grandxi")
    side = ["**제목(BEST)**: 마포 더클래시 실거래가 2026｜18평·59㎡·84㎡ 매매·전세 총정리",
            "**태그**: 더클래시, 마포더클래시, 마포더클래시18평, 더클래시실거래가, 더클래시전세, 아현동아파트, 마포아파트, 착한언니복덕방",
            "**썸네일**: 「18평 15억, 신혼집 될까?」 / 「59㎡ 21억 · 84㎡ 24.5억」 / 「사무실 앞 단지, 직접 정리」",
            "**함께 링크**: 2026.3.13 「마포더클래시 투룸 18평 랜선투어」 글"]
    return a, side


def lagrande():
    a = Post("2026-11-raemian-lagrande", "래미안라그란데 입주 2년 차 실거주 후기",
             "데이터: 국토교통부 아파트 매매·전월세 실거래 (2025.1~2026.11 계약분, 해제 제외, 2026.11.17 조회) · 계약 만기는 전월세 신고의 계약기간 기준 · 단지 규모는 언론 보도 기준 · 작성 규칙 MASTER v1.2 (11-1 생활 전문지역)")
    a.voice("여기 팔고 마포로 오고 싶어요.")
    a.text("얼마 전 **마포그랑자이 사무소**에 래미안라그란데에 사시는 분이 찾아오셨어요.",
           "입주 2년이 다가오니 이제 마포로 옮기고 싶다고요.",
           "그런데 저도 **래미안라그란데 주민**이라, 그 마음이 어떤 건지 누구보다 잘 알겠더라고요.")
    a.text("이유를 여쭤보니 {{“그래도 마포가 한 단계 위잖아요”}} 하시더라고요 ㅎㅎ",
           "새 아파트에서 2년 살아 보니, 이제는 **입지**를 한 단계 올리고 싶어지신 거예요.")
    a.blank(); a.greet(); a.blank()
    a.text("저는 이 단지에 **입주 때부터 살고 있어요.**", "어느새 입주 2년 차, 첫 전세 계약들이 만기를 바라보는 시기가 왔어요.",
           "오늘은 [[중개사로서 본 숫자]]와 {{입주민으로서 겪은 2년}}을 나눠서 정리할게요.",
           "사는 사람이라 좋게만 쓰지 않도록, 아쉬운 점도 같이 적을게요.")
    a.image("img/lagrande/02-gate4.jpg", "래미안라그란데 GATE 4 정문 (2026.11 직접 촬영 · 주변 간판 흐림 처리)")
    a.photo("(있으면) 입주 초기 2025년 같은 자리 사진 — 나란히 놓으면 가장 강해요")
    a.quote("**한 줄 요약** 이 단지 전월세 계약 **870여 건의 만기가 2027년 1~4월에 몰려 있어요** · 59㎡ 신규 전세 4억 9천(입주장) → 7억대", "기본")

    a.head(1, "래미안라그란데, 어떤 단지인가요?")
    a.table(["항목", "내용"], [["위치", "동대문구 이문동 (이문1구역 재개발)"], ["규모", "3,069세대 · 최고 27층 · 39개 동"],
                              ["입주", "2025년 1월 시작"], ["시공", "삼성물산"], ["가까운 역", "1호선 **외대앞역 · 신이문역** (동에 따라 도보 10~15분)"]],
            note="세대수·층수·입주 시기는 언론 보도 기준이에요")
    a.image("img/lagrande/03-entrance-sign.jpg", "단지 문주 — LA GRANDE · 이문로35길")
    a.image("img/lagrande/01-street-raemian-xi.jpg", "단지 앞 큰길 — 오른쪽 래미안라그란데, 왼쪽 길 건너 이문아이파크자이")
    a.text("길 하나를 사이에 두고 **이문아이파크자이**와 마주 보고 있어요.", "두 단지를 합치면 이 일대에만 신축 7천 세대가 넘게 모여 있는 셈이에요.")

    a.head(2, "입주 2년 차, 왜 지금 봐야 하나요?")
    a.text("입주장에 계약한 전세·월세는 대부분 **2년 계약**이에요.", "그래서 전월세 신고에 적힌 **계약 만기**를 세어 봤어요.")
    a.table(["계약 만기", "2027년 1월", "2월", "3월", "4월", "5월", "6월"],
            [["건수", "29", "238", "[[457]]", "147", "88", "41"]],
            note="국토부 전월세 실거래(래미안라그란데, 2025.1~2026.11 계약분)의 계약기간 기준 · 갱신청구권을 쓰면 실제로 나오는 물건은 이보다 적어요")
    a.text("✔ **2027년 2~4월**에 만기가 가장 많아요", "✔ 같은 시기에 세입자는 갱신과 이사를, 집주인은 갱신·신규 전세·실거주를 함께 고민하게 돼요",
           "✔ 만기가 몰린다고 전셋값이 떨어진다고 단정할 수는 없어요 — 갱신 비율에 따라 달라져요")
    a.image("img/lagrande/15-rock-garden.jpg", "단지 안 암석원 산책길 — 입주 2년 차 가을")

    a.head(3, "전세, 지금 얼마에 계약되고 있나요?")
    a.text("갱신 계약은 빼고 **신규 계약만** 봤어요.", "갱신은 인상 상한(5%)이 적용될 수 있어서 지금 시세와 다르거든요.")
    a.table(["59㎡ 신규 전세", "25년 1Q (입주장)", "25년 4Q", "26년 1Q", "26년 2Q", "26년 3Q"],
            [["중위", "4억 9,000", "6억", "6억 4,000", "[[7억 3,000]]", "7억 1,000"], ["건수", "246", "11", "9", "5", "4"]],
            note="국토부 전월세 실거래 · 전세 = 월세 0원 · 26년 2Q부터는 분기당 4~5건이라 표본이 작아요")
    a.table(["84㎡ 신규 전세", "25년 1Q (입주장)", "26년 1Q", "26년 3Q"],
            [["중위", "6억", "7억 5,000", "9억"], ["건수", "212", "5", "3"]])
    a.text("올해 4분기부터는 **갱신 계약**이 신고되기 시작했어요.",
           "59㎡ 갱신 7건 중위 5억 3,550만 원, 84㎡ 갱신 5건 중위 6억 6,000만 원이에요.",
           "{{같은 집이라도 갱신이냐 신규냐에 따라 1억 원 넘게 차이}}가 날 수 있다는 뜻이에요.")
    a.text("✔ 신규 전세 숫자는 입주장 물량이 빠진 뒤라 건수가 적어요 — 계약 전에는 지금 매물로 다시 확인해요")

    a.head(4, "매매는요?")
    a.table(["면적", "입주 초 (2025.1~3)", "최근 (2026)"],
            [["59㎡", "11억 2,000 ~ 12억", "[[16억 4,000]] (26.10 · 19층 · 중개) · 15억 2,010 (26.6 · 직거래)"],
             ["84㎡", "13억 2,000 ~ 13억 8,900", "13억 9,000 (25.10 · 2층) 이후 거래 없음"]],
            note="국토부 매매 실거래 · 해제 제외 · 2년 동안 매매 신고가 12건뿐이라 '시세'로 말하기엔 표본이 적어요 · 직거래는 특수 거래일 수 있어요")
    a.text("매매가 적은 건 입주 2년이 안 돼 팔기 전에 따져 볼 것이 많고, 토지거래허가 등 거래 조건도 있었기 때문으로 보여요.",
           "그래서 이 단지 매매는 **한두 건의 숫자보다 호가와 실거래를 같이** 봐야 해요.")

    a.head(5, "2년 살아보니 — 좋은 점 3가지")
    a.text("[[① 커뮤니티가 생활 안으로 들어와 있어요]]",
           "독서실·작은도서관에 **스크린골프**, **사우나**까지 있어요.",
           "사우나는 **금·토·일만 운영**하고 **입주민만** 이용할 수 있어요.",
           "조식 서비스는 아직 운영 전이고, 지금 입주민 **투표 중**이에요.")
    a.image("img/lagrande/11-library.jpg", "커뮤니티 작은도서관")
    a.image("img/lagrande/12-study-room.jpg", "독서실 (여) 좌석")
    a.text("[[② 산책할 곳이 정말 많아요]]",
           "단지 안 조경도 좋지만, **126·127동 쪽**은 나가면 바로 **한예종(한국예술종합학교) 후문**이에요.",
           "{{의릉과 캠퍼스를 따라 산책하기}} 너무 좋아요.")
    a.image("img/lagrande/05-inner-plaza.jpg", "동 사이 광장과 커뮤니티 동")
    a.image("img/lagrande/04-walkway.jpg", "단지 안 산책로")
    a.text("[[③ 지하주차장으로 다 이어져요]]",
           "**지하주차장에서 커뮤니티까지 전부 연결**돼 있어서, 비 오는 날이나 추운 날에도 밖에 안 나가고 다닐 수 있어요.",
           "단지 안에 놀이터와 유치원·어린이집도 있어서 아이 키우는 집에도 동선이 편해요.")
    a.image("img/lagrande/14-playground.jpg", "단지 안 놀이터")
    a.image("img/lagrande/13-parking.jpg", "지하주차장 — 동 출입구 바로 연결 (차량 번호판 흐림 처리)")

    a.head(6, "커뮤니티, 뭐가 있나요? (현장 안내문 기준)")
    a.table(["구분", "내용"],
            [["안내판 표시 시설", "클럽래미안 · 피트니스센터 · 유치원·어린이집 · 관리사무소 · 경로당 · 작은도서관 · 게스트하우스"],
             ["독서실 운영", "06:00 ~ 익일 01:00 · 연중무휴"],
             ["독서실 요금", "월 정기권 개인실 5만 원 · 일반실 3만 원 / 일일권 1인실 3천 원 · 일반실 2천 원"],
             ["정기권 신청", "매년 1월·7월 선착순 배정 (12월·6월 안내) · 앱으로 신청한 입주민만"],
             ["사우나", "금·토·일 운영 · 입주민 전용"], ["스크린골프", "있음"], ["조식", "아직 운영 전 · 도입 여부 입주민 투표 중"]],
            note="2026년 11월 단지 안 안내문 촬영 + 입주민(필자) 확인 기준 · 운영 내용은 바뀔 수 있어요 (관리 주체 공지 확인)")
    a.image("img/lagrande/09-community-sign.jpg", "커뮤니티 안내판")
    a.image("img/lagrande/08-community-garden.jpg", "커뮤니티 동 주변 정원")
    a.text("✔ 정기권 신청이 **12월**에 열리니, 1월 입주·전세 들어오시는 분은 신청 시기를 놓치지 마세요")

    a.head(7, "2년 살아보니 아쉬운 점")
    a.text("솔직히 **역이 좀 멀어요.** 이게 제가 느끼는 거의 유일한 단점이에요.",
           "동에 따라 외대앞역·신이문역까지 걸어서 10~15분이라, 매일 지하철 타시는 분은 **동 위치**를 꼭 보세요.",
           "대신 **차가 있으면 괜찮아요.** 내부순환로까지 10~15분, 강변북로도 10~15분이면 올라타요.")

    a.head(8, "착한언니 현장 노트 — 2년 차에 챙길 것")
    a.text("대단지라 **어느 동이냐에 따라 가까운 역이 달라요.** 직접 걸어 본 기준이에요.")
    a.table(["동 라인", "가까운 역 · 생활 동선", "도보 (제 걸음)"],
            [["2단지 **201동** 쪽", "**외대앞역** 가장 가까움 · 외대 바로 앞, 경희대도 걸어가기 편함", "가까움"],
             ["**111동** 쪽", "**신이문역**이 더 가까움", "약 10분"],
             ["**126·127동** 쪽", "외대앞역 · 한예종 후문·의릉 산책로 바로 앞", "약 15분 (단지 앞 마을버스 타면 5~10분)"]],
            note="입주민(필자)이 직접 걸어 본 시간이에요 · 걸음·신호에 따라 달라요 · 지도는 스마트에디터 「지도」 첨부로 넣어 주세요")
    a.text("✔ 외대·경희대 다니는 자녀가 있거나 출퇴근에 1호선을 쓰신다면 **동 위치부터** 정하세요")
    a.text("[[관리비, 실제로 얼마 나오나요?]]", "**59㎡** 한 세대의 실제 고지서를 옮겨 볼게요.")
    a.table(["구분", "금액"],
            [["**2026년 9월분 합계**", "[[21만 910원]]"], ["8월분 합계 (에어컨 많이 쓴 달)", "29만 7,060원"],
             ["일반관리비", "3만 1,740원"], ["청소비 · 경비비", "2만 2,920원 · 2만 2,700원"],
             ["세대전기료 (9월)", "4만 2,040원 (전월보다 3만 5,210원 ↓)"], ["장기수선충당금", "1만 2,380원"],
             ["주민공동시설료 · 시설물사용료", "1만 3,000원 · 1만 3,000원"], ["주차비", "1만 4,000원"]],
            note="59㎡ 한 세대 2026년 9월분 관리비 고지 기준 · 세대 사용량(전기·난방·커뮤니티 이용)과 차량 대수에 따라 집마다 달라요")
    a.text("✔ 59㎡ 기준 **사용량이 적은 달은 20만 원 초반, 여름 냉방 달은 30만 원 가까이** 나왔어요",
           "✔ 차이는 대부분 **세대 전기료**에서 나요 — 공용 항목은 매달 거의 같아요",
           "✔ **세입자분 팁**: 관리비에 들어 있는 **장기수선충당금**은 원래 집주인이 내는 돈이라, 이사 나갈 때 집주인에게 정산받을 수 있어요 (59㎡ 월 1만 2,380원 × 2년 ≈ 30만 원)")
    a.checks("**세입자**: 만기 6개월~2개월 전 사이에 갱신 의사를 알려요 (갱신청구권은 이 기간에)",
             "**집주인**: 실거주로 갱신을 거절할 계획이면 이유·시기를 미리 정리해요",
             "**입주민 공통**: 2년 차 하자 점검 — 항목마다 하자담보책임기간이 달라요. 관리사무소 공지와 공동주택관리법 기준을 확인해요",
             "**전세 들어오실 분**: 등기부등본 소유자·근저당, 보증금 반환보증 가입 가능 여부를 호실별로 먼저 확인해요")

    a.head(9, "내 상황에서는?")
    a.numbered("전세 만기가 2027년 2~4월이라면", "같은 단지 만기가 몰리는 시기예요",
               "갱신청구권을 쓸지, 신규로 다시 맞출지 지금부터 정리해 두면 협상이 편해요")
    a.numbered("집주인인데 매도·실거주를 고민한다면", "세금 요건(보유·거주 기간)은 취득 시점에 따라 달라요",
               "결정 전에 세무 상담으로 내 경우를 확인해요 — 블로그 글로 판단하지 마세요")
    a.numbered("마포·서대문으로 갈아타기를 고민한다면", "이 단지 전세금이 매수 자금이 될 수 있어요",
               "가격 비교가 아니라 **자금 흐름**으로 계산해요 — 보유 현금·대출 가능 금액부터")

    a.head(10, "신촌·이대에서 이문동으로 오신다면")
    a.text("저희 신촌·이대 손님 중에는 **연대·이대를 졸업하고 외대(한국외대) 대학원**으로 가시는 분들이 꽤 있어요.",
           "이문동은 외대 바로 앞이고, 경희대도 걸어갈 수 있는 거리예요.")
    a.quote("**착한언니복덕방은 동대문구 이문동 중개도 해요** · 원룸·오피스텔·아파트 전월세 · 신촌에서 상담하고 이문동 집 보러 같이 가요", "기본")
    a.text("✔ 공인중개사는 사무소 위치와 상관없이 **어느 지역 매물이든 중개**할 수 있어요",
           "✔ 이 동네를 직접 걸어 다니는 사람이라, **동 위치별 역 동선**까지 같이 봐 드릴게요")

    a.head(11, "정리하면")
    a.text("✔ 전월세 계약 만기가 **2027년 2~4월**에 몰려 있어요",
           "✔ 59㎡ 신규 전세는 입주장 4억 9천에서 최근 7억대로 계약됐어요 (최근 표본은 적어요)",
           "✔ 갱신 계약은 신규보다 1억 원 넘게 낮게 신고되고 있어요",
           "✔ 매매는 2년간 12건뿐이라 아직 시세를 말하기 어려워요",
           "==제가 사는 동네라, 【동대문 생활 노트】로 계속 기록할게요.==")
    a.image("img/lagrande/16-flowers.jpg", "단지 화단 (2026.11)")
    a.note('실제로 사무소에서 "여기 팔고 마포로 가고 싶어요"라는 상담을 받아요. 그만큼 이 단지에 사시는 분들도 다음 단계를 마포로 보시는 경우가 많아요.', '살아 보니 지하주차장으로 커뮤니티까지 다 이어져서 동선은 정말 편해요. 아쉬운 건 역까지 거리 하나예요.')
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 다음 글은 용두동 신속통합기획 후보지 이야기예요.",
            "국토교통부 매매·전월세 실거래(2025.1~2026.11 계약분, 2026.11.17 조회) 기준이에요 · 10~11월분은 신고 기한이 남아 늘 수 있어요 · 단지 규모는 언론 보도 기준 · 생활 정보는 2026년 11월 기준 제 경험이에요")
    a.signature("grandxi")
    side = ["**제목(BEST)**: 래미안라그란데 입주 2년 차 실거주 후기｜전세 만기 몰리는 2027년 봄, 시세와 장단점",
            "**제목(대안)**: 래미안라그란데 전세 시세 2026｜입주 2년 차, 갱신 vs 신규 1억 차이",
            "**태그**: 래미안라그란데, 래미안라그란데전세, 래미안라그란데후기, 이문동아파트, 이문휘경뉴타운, 동대문구아파트, 전세만기, 갱신청구권, 착한언니복덕방",
            "**썸네일**: 「입주 2년 차, 직접 살아요」 / 「만기 2027년 2~4월에 몰려요」 / 「갱신 vs 신규 1억 차이」",
            "**사진**: 2026.11 촬영 15장 배치 완료 (번호판·주변 부동산 간판 흐림 처리) · 대표 사진은 GATE 4 정문 · 입주 초기 사진이 있으면 추가",
            "**빈칸**: 모두 채움 ✅ (내부순환로 표현 확인) · **지도**: 네이버지도 캡처 대신 스마트에디터 「지도」 버튼으로 래미안라그란데 위치 첨부 (캡처 이미지는 지도 저작권 표시 문제) · **⚠️ 발행 전**: 남은 ✍️ 칸 채우기 · 역 이름 확인 · 하자담보책임기간은 항목별 숫자를 쓰려면 공동주택관리법 시행령 원문 확인"]
    return a, side


def maraepu():
    a = Post("2026-11-maraepu", "마포래미안푸르지오 1~4단지 실거래 비교 2026",
             "데이터: 국토교통부 아파트 매매·전월세 실거래 (2025.11~2026.10 계약분, 해제 제외, 2026.11.2 조회) · 단지 규모·시공사는 언론 보도 기준 · 작성 규칙 MASTER v1.2")
    a.fill("도입 — 마래푸 상담에서 실제로 자주 듣는 질문 1개 (예시: “마래푸는 몇 단지가 제일 좋아요?”)")
    a.blank(); a.greet(); a.blank()
    a.text("마포래미안푸르지오는 **1~4단지를 합쳐 한 단지처럼** 부르지만,", "실거래를 단지별로 나눠 보면 거래 수도, 가격 범위도 조금씩 달라요.")
    a.text("오늘은 최근 1년 실거래를 **단지별로** 정리해 볼게요.")
    a.photo("마래푸 단지 전경 (직접 촬영)")
    a.quote("**한 줄 요약** 1~4단지 합산 59㎡ 21억 2,000 · 84㎡ 24억 8,000 (최근 1년 실거래 중위)", "기본")

    a.head(1, "마래푸, 어떤 단지인가요?")
    a.table(["항목", "내용"], [["위치", "서울 마포구 아현동 (아현3구역 재개발)"], ["준공", "2014년"],
                              ["규모", "4개 단지 · 3,885세대 (임대 661세대 포함)"], ["시공", "1·2단지 대우건설 · 3·4단지 삼성물산"],
                              ["가까운 역", "✍️ 아현역·애오개역 도보 ○분 (단지별)"]],
            note="세대수·시공사는 언론 보도 기준이에요 (공식 대장으로 다시 확인 예정)")

    a.head(2, "1~4단지 합쳐서 보면")
    a.table(["면적", "1년 매매", "매매 중위", "84㎡ 최고", "신규 전세 중위"],
            [["59㎡", "27건", "[[21억 2,000]]", "-", "8억"], ["84㎡", "26건", "[[24억 8,000]]", "26억 6,500 (26.09)", "10억"]],
            note="국토부 실거래 · 2025.11~2026.10 계약분 · 해제 제외 · 전세는 갱신 제외 신규 계약만 · 9~10월분은 신고 기한이 남아 늘 수 있어요")

    a.head(3, "단지별로 나눠 보면 이렇게 달라요")
    a.table(["단지", "1년 매매", "59㎡ 중위 (건)", "84㎡ 중위 (건)", "84㎡ 최근 거래"],
            [["1단지", "9건", "21억 2,000 (5)", "24억 3,500 (4)", "26.09 · 25억 2,000 (6층)"],
             ["2단지", "17건", "21억 3,500 (6)", "24억 9,750 (10)", "26.09 · 26억 6,500 (20층)"],
             ["3단지", "9건", "20억 5,500 (6)", "23억 1,750 (2)", "26.04 · 23억 4,500 (17층)"],
             ["4단지", "20건", "21억 7,000 (10)", "24억 9,000 (10)", "26.06 · 26억 5,000 (21층)"]])
    a.text("✔ 1년 거래는 **4단지(20건)·2단지(17건)**가 많았어요",
           "✔ 84㎡ 최고가 두 건(26억 6,500 · 26억 5,000)도 2단지·4단지에서 나왔어요")
    a.text("그런데 이 숫자만 보고 {{“2·4단지가 더 비싸다”}}고 판단하시면 안 됩니다.",
           "3단지 84㎡는 2건, 1단지 84㎡는 4건뿐이라 표본이 작고,", "단지 안에서도 **동·층·향·조망**에 따라 가격이 꽤 달라요.")
    a.fill("현장 노트 — 단지별로 실제 손님들이 많이 묻는 차이 (역 동선·경사·학교 등, 근거 있는 것만)")

    a.head(4, "전세는 단지별로 비슷해요")
    a.table(["단지", "59㎡ 신규 전세 중위 (건)", "84㎡ 신규 전세 중위 (건)"],
            [["1단지", "8억 (25)", "10억 (10)"], ["2단지", "8억 (25)", "10억 (15)"],
             ["3단지", "8억 (21)", "9억 8,375 (10)"], ["4단지", "8억 1,500 (30)", "10억 3,500 (30)"]])
    a.hl("전세는 단지 간 차이가 거의 없어요. 매매가 대비 전세가율은 40% 안팎이에요.")

    a.head(5, "착한언니 현장 노트 — 마래푸 볼 때 이 3가지")
    a.numbered("① 단지보다 동·라인 먼저", "✍️ 같은 단지 안에서 체감 차이가 큰 부분 (직접 채우기)")
    a.numbered("② 학교 배정은 꼭 확인", "단지마다 배정 초등학교가 다를 수 있다는 보도가 있어요",
               "실제 배정은 **교육청 통학구역**으로 확인해요")
    a.numbered("③ 세입자 있는 집이라면", "전세 만기일과 계약갱신청구권 사용 여부를 먼저 확인해요")

    a.head(6, "정리하면")
    a.text("✔ 1~4단지 합산 59㎡ **21억 2,000** · 84㎡ **24억 8,000** (1년 실거래 중위)",
           "✔ 거래는 2·4단지가 많았고, 84㎡ 최고가도 두 단지에서 나왔어요",
           "✔ 표본이 작은 단지가 있어서, 단지 이름보다 **동·층·향**으로 비교하세요",
           "==후보를 2~3곳으로 좁히면, 실제 매물 조건으로 같이 비교해 드릴게요.==")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 마포 주력 단지 실거래를 이어서 정리할게요.",
            "국토교통부 실거래가 공개시스템(2025.11~2026.10 계약분, 2026.11.2 조회) 기준이에요 · 단지 규모·시공사·학교 배정은 보도 기준으로 공식 확인이 필요해요 · 개별 거래의 동·호수는 공개하지 않아요")
    a.signature("grandxi")
    side = ["**제목(BEST)**: 마포래미안푸르지오 1~4단지 실거래 비교 2026｜59㎡ 21억·84㎡ 24억대, 단지별로 보면",
            "**태그**: 마포래미안푸르지오, 마래푸, 마래푸실거래가, 마래푸4단지, 마래푸전세, 아현동아파트, 마포아파트, 착한언니복덕방",
            "**썸네일**: 「마래푸, 몇 단지가 제일 비쌀까?」 / 「84㎡ 24억 8천 · 최고 26억 6,500」 / 「1~4단지 한눈에」",
            "**⚠️ 발행 전**: ✍️ 칸 채우기 · 학교 배정은 교육청 통학구역으로 확인"]
    return a, side


def zaiella():
    a = Post("2026-11-shinchon-zaiella", "신촌자이엘라 월세·매매 시세 2026",
             "데이터: 국토교통부 아파트(도시형)·오피스텔 매매·전월세 실거래 합산 (2025.11~2026.10 계약분, 2026.11.2 조회) · 건물 정보 건축물대장(표제부) · 작성 규칙 MASTER v1.2")
    a.fill("도입 — 겨울방학 앞두고 학부모님께 실제로 받는 질문 1개 (예시: “3월 입주면 언제부터 방 보러 와야 해요?”)")
    a.blank(); a.greet(); a.blank()
    a.text("신촌자이엘라는 **저희 사무실이 있는 건물**이에요.", "그래서 이 건물 계약은 제일 많이, 제일 가까이에서 봐 왔어요.",
           "그리고 저희는 이 건물의 [[KB시세를 입력하는 중개사무소]]이기도 해요.")
    a.text("오늘은 최근 1년 실거래로 **월세·매매 시세**를 정리하고,", "처음 오시는 학생·학부모님이 헷갈려 하시는 부분을 같이 풀어 볼게요.")
    a.photo("신촌자이엘라 외관 (직접 촬영)")
    a.quote("**한 줄 요약** 보증금 1,000만 원 기준 월 105~120만 원대 계약이 가장 많아요 (최근 1년)", "기본")

    a.head(1, "신촌자이엘라, 어떤 건물인가요?")
    a.table(["항목", "내용"], [["위치", "서울 서대문구 대현동 104-36 (이대역 인근)"], ["사용승인", "2014년 11월"],
                              ["규모", "지하 6층 · 지상 23층"], ["구성", "오피스텔 177호 + 도시형생활주택 92세대 + 근린생활시설"],
                              ["주차", "기계식 73대 + 자주식 31대"], ["가까운 역", "✍️ 이대역 도보 ○분"]],
            note="건축물대장(표제부) 기준")
    a.text("여기서 하나는 구분해서 봐야 하는데요,", "이 건물은 **오피스텔과 도시형생활주택이 한 건물에** 있어요.",
           "그래서 국토부 실거래도 [[아파트(도시형)]]와 {{오피스텔}} 두 곳에 나뉘어 신고돼요.", "아래 시세는 두 자료를 합쳐서 정리했어요.")
    a.fill("현장 노트 — 오피스텔 호실과 도시형 세대가 실제로 어떻게 다른지 (전입·관리비·구조 등, 확인된 것만)")

    a.head(2, "월세, 지금 얼마에 계약되나요?")
    a.text("보증금 **1,000만~2,000만 원** 신규 계약만 모았어요.")
    a.table(["전용면적", "신고 구분", "보증금 / 월세 (최근 1년 신규)", "건수"],
            [["20~22㎡", "도시형", "1,000만 / 110~120만", "3"],
             ["22.13㎡", "도시형", "1,000~2,000만 / 110~115만", "4"],
             ["23~25㎡", "도시형", "1,000만 / 110~155만", "7"],
             ["27~28㎡", "오피스텔", "1,000~2,000만 / 100~110만", "4"],
             ["29.6㎡", "도시형", "1,000만 / 140~145만", "2"]],
            note="국토부 실거래 · 2025.11~2026.10 계약분 · 갱신 계약 제외")
    a.text("✔ 신고 자료를 보면 도시형 세대는 **16층 이상**, 오피스텔 호실은 **15층 이하**에서 거래가 나왔어요",
           "✔ 23㎡대 월 155만 원 1건은 다른 계약과 차이가 커서 특수 거래일 수 있어요")
    a.text("그런데 월세만 보고 판단하시면 안 됩니다.", "**관리비와 포함 항목**(인터넷·수도·난방)까지 더해서 비교하세요.")
    a.fill("관리비 실제 수준과 포함 항목 (면적별)")

    a.head(3, "전세와 반전세도 있어요")
    a.table(["전용면적", "계약", "보증금 / 월세"],
            [["22.13㎡", "전세", "2억 5,000 (2건, 25.12)"], ["22.13㎡", "반전세", "2억 3,000 / 15만"],
             ["28.3㎡", "반전세", "2억 / 15만"], ["29.62㎡", "반전세", "2억 / 20~30만"]])
    a.text("전세·반전세는 보증금이 커지는 만큼,", "**등기부등본(근저당)**과 **보증금 반환보증 가입 가능 여부**를 호실별로 꼭 먼저 확인해요.")

    a.head(4, "매매는 이렇게 거래됐어요")
    a.table(["시점", "신고 구분", "전용", "층", "매매가"],
            [["25.12", "오피스텔", "29.62㎡", "8층", "2억 7,000"], ["26.01", "오피스텔", "29.62㎡", "5층", "2억 6,900"],
             ["26.07", "도시형", "22.13㎡", "16층", "2억 7,000"], ["26.10", "도시형", "22.13㎡", "23층", "2억 5,000"]])
    a.text("1년에 4건뿐이라 **추세로 보지 않아요.**", "매매는 지금 나와 있는 매물로 비교하는 게 정확해요.")
    a.text("매매를 보실 때 가장 많이 헷갈리시는 게 **세 가지 가격**이에요.", "이 건물 KB시세를 직접 입력하는 입장에서 차이를 정리해 드릴게요.")
    a.table(["구분", "무엇인가요", "어디서 보나요", "언제 쓰나요"],
            [["**실거래가**", "실제로 계약하고 신고한 가격", "국토부 실거래가 공개시스템", "과거에 얼마에 거래됐는지"],
             ["**KB시세**", "KB부동산이 공개하는 참고 시세", "KB부동산 (앱·웹)", "대출 한도 상담할 때 참고"],
             ["**호가**", "지금 매물로 나와 있는 가격", "매물 광고 · 중개사무소", "지금 살 수 있는 가격"]])
    a.text("셋은 **같은 숫자가 아니에요.**", "대출을 끼고 사실 거라면 KB시세도 같이 확인하시고,",
           "실제 대출 한도는 **은행 심사에서 확정**된다는 점도 꼭 기억해 주세요.")
    a.fill("KB부동산에 공개된 신촌자이엘라 KB시세 (면적별, 조회일 함께) — 공개된 값만")

    a.head(5, "착한언니 현장 노트 — 학생·학부모님이 먼저 볼 것")
    a.numbered("① 입주 시기부터", "✍️ 겨울방학(1~2월)에 방이 몰리는 실제 흐름 — 언제 보러 오면 좋은지")
    a.numbered("② 계약 전 확인", "등기부등본 소유자와 계약하는 사람이 같은지",
               "전입신고·확정일자가 가능한지 (호실별)", "옵션 목록과 작동 상태를 특약에 남기기")
    a.numbered("③ 지방에서 오시는 부모님이라면", "✍️ 방문 전 미리 보내 주시면 좋은 정보 (입주일·예산·학교·필요 옵션)")

    a.head(6, "정리하면")
    a.text("✔ 보증금 1,000만 원 기준 **월 105~120만 원대** 계약이 가장 많아요",
           "✔ 오피스텔·도시형이 한 건물이라 국토부 자료를 **합쳐서** 봐야 해요",
           "✔ 월세는 **관리비 포함 항목**까지 더해서 비교하세요",
           "==입주 희망일 · 예산 · 학교 · 꼭 필요한 옵션만 남겨 주시면, 지금 볼 수 있는 호실로 추려 드릴게요.==")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 신촌·이대 오피스텔 시세를 건물별로 이어서 정리할게요.",
            "국토교통부 실거래(아파트·오피스텔, 2025.11~2026.10 계약분, 2026.11.2 조회)와 건축물대장 기준이에요 · 호실별 조건(옵션·관리비·입주 가능일)은 문의 시점에 다시 확인해 드려요")
    a.signature("zaiella")
    side = ["**제목(BEST)**: 2026 신촌자이엘라 월세·매매 시세｜오피스텔·도시형 한 번에 정리",
            "**태그**: 신촌자이엘라, 신촌자이엘라월세, 이대역오피스텔, 신촌오피스텔, 이대오피스텔, 대현동오피스텔, 신촌원룸, 착한언니복덕방",
            "**썸네일**: 「저희 사무실 건물이에요 · KB시세 입력 중개사무소」 / 「월 105~120만, 보증금 1천」 / 「겨울방학 전에 꼭 볼 것」",
            "**후속 글 아이디어**: 「KB시세는 누가, 어떻게 정할까? 입력하는 중개사가 알려드리는 실거래가·KB시세·호가 차이」 (산정 방식은 KB부동산 공개 설명 기준으로)",
            "**발행 시기**: 겨울방학 시즌 6주 전 → **11월 중 발행** 추천",
            "**함께 링크**: 2026.5.4 「신촌자이엘라 오피스텔 A1타입」 글 (기존 글은 구조 소개, 이 글은 시세로 역할 분리)"]
    return a, side


def sillim():
    a = Post("2026-11-sillim", "신림 재개발 전망 2026, 지금 사도 될까",
             "데이터: 국토교통부 아파트 매매·전월세·분양권(입주권) 실거래 (관악구, 2025.11~2026.10 계약분, 2026.11.6 조회) · 구역 단계: 관악구 재정비촉진구역 현황(2026.10.26)·서울시/관악구 고시·정비몽땅 · 교통: 서울시 발표 · 작성 규칙 MASTER v1.2 · 도서 협찬 포함")
    a.text("**[광고] 이 글에는 도서 협찬을 받은 책 소개가 포함되어 있어요.**", size=13, color="#888888")
    a.blank(); a.greet(); a.blank()
    a.text("착한언니복덕방은 **마포구·서대문구 전문**이지만,", "서울 전역 토지거래허가구역 등 규제가 강해지면서",
           "상대적으로 **금액대가 낮은 서울 재개발**을 묻는 분들이 늘고 있어요.")
    a.text("지난번 **광명 하안주공** 정리에 이어,", "이번에는 [[신림 재개발 1~10구역]]을 Q&A와 실거래가로 한 번에 정리했습니다.")
    a.text("※ 아래 내용은 관악구 재정비촉진구역 현황(2026.10.26), 서울시·관악구 고시,", "국토교통부 실거래가 공개시스템 기준이며, 사업 단계와 수치는 계속 바뀔 수 있어요.", size=13, color="#888888")
    a.photo("3구역 서울대벤처타운역 푸르지오 전경 (직접 촬영)")
    a.quote("**한 줄 요약** 신림은 \"뉴타운 하나\"가 아니라 단계가 제각각인 10개 사업지예요. 이름보다 **구역별 단계**부터 보세요.", "기본")

    a.head(1, "Q&A로 빠르게 이해하기")
    a.text("**Q. 왜 지금 신림인가요?**")
    a.text("A. 20년 가까이 멈춰 있던 신림 일대가 **한꺼번에 단계를 밟고 있기 때문**이에요.",
           "3구역은 이미 입주했고(2026.5 이전고시), 2구역은 관악구 현황상 착공,", "1구역은 사업시행계획인가(2025.3)까지 왔어요.")
    a.text("✔ 5·8구역은 2026년 2월 정비구역 지정, 6구역은 5월 지정,", "8구역은 10월 조합설립인가, 10구역은 7월 추진위 승인까지 이어졌어요.")
    a.text("그런데 \"한꺼번에 움직인다\"가 \"한꺼번에 완성된다\"는 뜻은 아니에요.", "구역마다 **입주까지 남은 시간이 크게 달라요.**")
    a.blank()
    a.text("**Q. 강남·여의도까지는 얼마나 걸려요?**")
    a.table(["목적지", "노선", "확인된 사실"],
            [["**여의도**", "신림선 (샛강역 = 9호선 환승)", "샛강~관악산(서울대) **전 구간 16분** (서울시 2022 개통 발표)"],
             ["**강남**", "신림선 → 2호선 신림역 환승", "2호선 신림역 → 강남역 **8개 역**"],
             ["**환승**", "신림선 4개 환승역", "9호선 샛강 · 1호선 대방 · 7호선 보라매 · 2호선 신림"]],
            note="실제 소요시간은 집에서 역 출입구까지의 경사·대기·환승 시간에 따라 달라요. 출근 시간대에 지도 앱으로 꼭 확인하세요.")
    a.fill("현장 노트 — 3구역 푸르지오 → 서울대벤처타운역 실제 도보 시간·오르막 (직접 걸어본 기준)")
    a.blank()
    a.text("**Q. 교통 호재가 더 있나요?**")
    a.table(["사업", "현재 단계", "어떻게 봐야 하나"],
            [["**난곡선** (보라매공원~난향동 4.08km)", "예비타당성조사 진행 중 · 결과 2026년 12월 발표 예정 (보도)", "{{예타 통과 전}} — 확정 호재로 보지 않기"],
             ["**서부선** (은평~관악)", "민자사업 추진 중 · 착공 시점 보도마다 다름", "착공·개통 일정은 공식 발표로 확인"],
             ["신림4구역 보행로", "신통기획 가이드라인(2026.4) 계획", "관악산·도림천 연결 **계획** 단계"]])
    a.text("그런데 이 호재들만 보고 판단하시면 안 됩니다.", "**발표 → 예타 → 착공 → 개통** 중 어디까지 왔는지가 가격보다 먼저예요.")
    a.blank()
    a.text("**Q. 학군은 어때요?**")
    a.text("A. 솔직하게 말씀드리면, 신림은 **학군으로 고르는 동네는 아직 아니에요.**",
           "대규모 입주가 이어지면 학교 배치·통학로가 함께 바뀔 수 있어서,", "구역별 **학교 계획(신설·증축)**은 정비계획 원문으로 확인해야 해요.")
    a.fill("현장 노트 — 3구역 입주민 통학 실제 동선 / 아이 있는 손님이 실제로 묻는 학교 (확인된 것만)")
    a.text("✔ 학교 배정·학업 정보는 **학교알리미**와 **교육청 통학구역**으로 확인하세요.", size=15)
    a.blank()
    a.text("**Q. 정비구역 지정되면 바로 가격이 오르나요?**")
    a.text("A. 지정은 **출발선**이에요. 하안주공에서도 그랬듯,", "실제 가격은 **조합설립 → 사업시행인가 → 관리처분** 같은 단계와",
           "시공사 선정이 맞물릴 때 움직이는 경우가 많아요.", "다만 단계가 올라갈수록 **이미 기대감이 가격에 들어가 있을 수 있다**는 점도 같이 보세요.")
    a.blank()
    a.text("**Q. 지금 사면 입주권 받을 수 있나요?**")
    a.text("A. **물건마다 달라요.** 그래서 저희는 아래 세 가지를 확인하기 전엔 계약을 권하지 않아요.")
    a.checks("**권리산정기준일**과 그 이후 지분 쪼개기·신축 여부", "투기과열지구 재개발은 **관리처분계획인가 이후 조합원 지위 양도 제한** + 법정 예외 해당 여부",
             "**토지거래허가** 대상 여부 (지번·용도·면적별 최신 공고)")

    a.head(2, "✨ 신림 1~10구역 한눈에 보기")
    a.table(["구역", "대표 지번", "현재 단계 (기준일)", "규모"],
            [["**1구역**", "신림동 808", "사업시행계획인가 (2025.3.13)", "4,185세대"],
             ["**2구역**", "신림동 324-25", "착공 (관악구 현황 2026.10.26)", "1,430세대"],
             ["**3구역**", "신림동 316-55", "**입주 완료** · 이전고시 (2026.5.14)", "571세대 (서울대벤처타운역 푸르지오)"],
             ["4구역", "신림동 306", "신통 가이드라인 확정 (2026.4.27)", "약 992세대 (계획)"],
             ["5구역", "신림동 412", "구역지정 (2026.2.26) · 신탁 시행자 지정 (6.4)", "3,973세대 (계획)"],
             ["6구역", "신림동 419", "구역지정 (2026.5.28)", "957세대 (지정 후 구청 설명)"],
             ["7구역", "신림동 675", "조합설립인가 (2026.9 게시)", "1,402세대 (계획)"],
             ["**8구역**", "신림동 650", "조합설립인가 (2026.10.7 고시)", "2,257세대 (계획)"],
             ["9구역", "신림동 119-1", "정비계획 수립 용역", "미확정"],
             ["10구역", "신림동 610-200", "추진위 승인 (2026.7.16)", "미확정"]],
            note="1~4구역 = 신림재정비촉진지구 · 5~10구역 = 촉진지구 밖 개별 사업지 · \"계획\" 수치는 인가 단계에서 바뀔 수 있어요")
    a.image("img/sillim-1to4-zones.jpg", "신림 1~4구역 한눈에 보기 — 실제 지도 위 구역 표시 (원도면: 관악구 공고 제2026-1274호, 지도 © OpenStreetMap)")
    a.text("[[1구역]](북쪽 가장 넓은 곳) → {{2구역}} → **3구역**(남쪽, 입주 완료)이 한 줄로 이어지고,", "4구역은 동쪽에 따로 붙어 있어요.", size=15)
    a.image("img/sillim-1to4-boundary.jpg", "원도면 그대로 — 관악구 공고 제2026-1274호 재정비촉진구역 결정도(변경안)")
    a.text("여기서 하나는 구분해서 봐야 하는데요,", "1~3구역을 합치면 **6,186세대**지만 [[3구역 571세대는 이미 입주]]했어요.",
           "\"앞으로 6천 세대가 들어온다\"가 아니라, **입주 시기가 각각 다른 6천여 세대**예요.")

    a.head(3, "1구역 : 신림 최대어, 사업시행인가")
    a.table(["구분", "내용"], [["단계", "사업시행계획인가 (2025.3.13 고시)"], ["규모", "223,168.7㎡ · 4,185세대"],
                               ["장점", "가장 큰 규모 · 도림천·녹지 접근"], ["확인할 것", "분양신청·감정평가·관리처분인가 일정 · 일반분양 물량은 모집공고 전까지 미확정"]])
    a.fill("현장 노트 — 1구역 출입구별 역 접근·단차")

    a.head(4, "2구역 : 착공, 가장 먼저 그려지는 새 아파트")
    a.table(["구분", "내용"], [["단계", "착공 (관악구 현황 2026.10.26)"], ["규모", "96,082.8㎡ · 1,430세대"],
                               ["확인할 것", "공동주택 착공신고 수리일 · 변경 관리처분 · 일반분양 공고 (분양 물량·일정은 공고로 확인)"]])
    a.text("✔ 정비몽땅 화면은 아직 「철거신고」로 표시돼 있어요. **구청 현황이 더 최신**이에요.", size=15)

    a.head(5, "3구역 : 이미 입주, 신림의 비교 기준")
    a.text("서울대벤처타운역 푸르지오(571세대, 2025년 준공)는", "신림 재개발이 완성되면 어떤 모습인지 **직접 확인할 수 있는 기준점**이에요.")
    a.table(["시점", "구분", "전용", "층", "가격"],
            [["25.11", "입주권", "59㎡", "9층", "8억 9,000"], ["25.12", "분양권·입주권", "84㎡", "2층", "9억 3,300"],
             ["26.03", "입주권", "84㎡", "6층", "11억 5,000"], ["26.05", "매매", "84㎡", "13층", "9억 6,000"],
             ["26.09", "매매", "84㎡", "5층", "**11억 8,000**"]],
            note="국토부 실거래 (분양권·입주권 전매 + 아파트 매매) · 1년간 5건뿐이라 추세로 보지 않아요")
    a.text("그런데 이 숫자만 보고 판단하시면 안 됩니다.", "84㎡가 9억 6,000과 11억 8,000으로 **2억 넘게 차이**가 나요.",
           "동·층·향 조건이 달라서일 수 있지만, 근거 없이 단정하지 않을게요.")
    a.table(["전세 (신규)", "59㎡", "84㎡"],
            [["2025.11~12", "5억~5억 5,000", "6억~7억"], ["2026.06~07", "-", "7억 4,000~7억 6,000"]],
            note="전세 = 월세 0원 계약 · 전용 30㎡대 소액 보증금 계약은 일반 전세와 성격이 달라 제외했어요")
    a.fill("네이버 현재 호가 (확인 날짜 함께) — 호가는 실거래가와 다르게 표기")

    a.head(6, "관악 최고가 단지와 비교하면 — 신림 신축은 따라갈 수 있을까?")
    a.text("**관악구에서 지금 가장 비싼 아파트**는 어디일까요?", "최근 1년 실거래(해제 제외)로 같은 면적끼리만 비교했어요.")
    a.table(["단지", "준공 · 세대수", "84㎡ 중위 (건)", "84㎡ 최고", "59㎡ 중위 (건)"],
            [["**힐스테이트뉴포레** (신림동)", "2022 · 1,143세대", "16억 9,500 (3)", "**17억** (26.6)", "**13억 8,000** (33)"],
             ["e편한세상서울대입구 1단지 (봉천동)", "2019 · 711세대", "14억 7,500 (20)", "16억 6,500 (26.6)", "13억 8,000 (9)"],
             ["e편한세상서울대입구 2단지 (봉천동)", "2019 · 565세대", "14억 4,100 (20)", "16억 4,000 (26.6)", "12억 9,750 (4)"],
             ["e편한세상서울대입구 2차 (봉천동)", "2020 · 519세대", "14억 5,250 (14)", "15억 9,500 (26.9)", "13억 (6)"],
             ["신림푸르지오 (신림동)", "2005 · 1,456세대", "10억 2,500 (38)", "12억 2,000 (26.10)", "-"],
             ["**서울대벤처타운역 푸르지오** (3구역)", "2025 · 571세대", "[[10억 5,500 (4)]]", "11억 8,000 (26.9)", "8억 9,000 (1, 입주권)"]],
            note="국토부 실거래 2025.11~2026.10 계약분 · 분양권·입주권 포함 · 세대수·준공은 건축물대장(3구역은 관악구 자료) · 9~10월분은 신고 기한이 남아 늘 수 있어요")
    a.text("여기서 하나는 구분해서 봐야 하는데요,", "3구역은 **2025년 신축인데도 84㎡ 중위가 2005년 준공 신림푸르지오와 비슷**하고,",
           "같은 신림동 신축 힐스테이트뉴포레와는 84㎡ 중위 기준 [[6억 원 넘게]] 차이가 나요.")
    a.text("그런데 이 차이를 \"저평가\"로 바로 읽으시면 안 됩니다.", "3구역 84㎡는 1년에 **4건**, 뉴포레 84㎡는 **3건**뿐이라 표본이 작고,",
           "두 단지는 **규모·역 거리·경사·생활권 완성도**가 달라 서로 대체재인지부터 따져야 해요.")
    a.table(["격차를 만드는 조건", "3구역 지금", "좁혀질 수 있는 계기 (확인할 것)"],
            [["단지 규모", "571세대 단독", "1구역(4,185)·2구역(1,430) 입주 → 같은 생활권 신축 6천여 세대"],
             ["주변 환경", "1·2구역 공사 중", "2구역 입주 시점 · 1구역 관리처분·착공 일정"],
             ["새 기준 가격", "거래 표본 적음", "1·2구역 **일반분양가**가 나오면 주변 시세의 새 기준이 될 수 있어요"],
             ["역·경사", "역까지 오르막 (현장 확인)", "단지 출입구 → 역 실제 동선 · 계획 보행로 실현 여부"],
             ["학교·상권", "확정 계획 확인 필요", "정비계획상 학교·근린생활시설 배치"]])
    a.hl("\"따라간다/못 따라간다\"를 지금 숫자로 정할 수는 없어요. 위 조건이 하나씩 채워지는지를 단계별로 확인하는 게 맞아요.")
    a.fill("현장 노트 — 힐스테이트뉴포레·e편한세상서울대입구와 3구역을 직접 비교해 본 느낌 (역 동선·경사·상권, 확인된 것만)")

    a.head(7, "4~10구역 : 이제 막 출발선")
    a.image("img/sillim-6-boundary.jpg", "신림6구역 정비구역 결정도 (서울시 고시 제2026-303호)")
    a.image("img/sillim-6-plan.jpg", "신림6구역 정비계획 결정도 — 획지·학교·공원 배치 (서울시 고시 제2026-303호)")
    a.image("img/sillim-7-boundary.jpg", "신림7구역 정비구역 결정도 (관악구 고시 제2024-104호)")
    a.fill("5·8구역 경계 도면 — 서울시보 제4129호(2026.2.26) 붙임 도면 확보 후 추가")
    a.table(["구역", "한 줄 정리", "주의할 점"],
            [["4구역", "학교 인접, 관악산·도림천 보행로 계획", "992세대는 기획 수치 · 촉진계획 변경 고시 확인"],
             ["5구역", "서원역 생활권, 신탁 방식", "3,973세대는 지정 후 구청 발표 · 사업시행인가는 별도"],
             ["6구역", "5구역과 생활권 공유", "세대수 자료가 990·992·957로 엇갈림 → 고시 원문 확인"],
             ["7구역", "조합설립인가", "같은 이름 과거 사업과 지번 구별"],
             ["8구역", "난곡로 상권, 우회도로 계획", "2034년 5월은 고시상 **준공 예정일**"],
             ["9·10구역", "초기 단계", "최종 경계·세대수 미확정 → 편입 여부부터"]])

    a.head(8, "✅ 매수 전 꼭 확인할 것")
    a.table(["서류", "확인 내용", "어디서"],
            [["등기부등본 · 건축물대장", "소유자 · 대지권 · 무허가/위반건축", "인터넷등기소 · 정부24"],
             ["권리산정기준일 고시", "기준일 이후 분할·신축·지분 변동", "구청 고시"],
             ["조합·신탁사 확인서", "분양대상 여부 · 승계 가능 여부 (서면)", "조합·신탁사"],
             ["토지거래허가 공고", "해당 지번 허가 대상 · 이용 의무", "관악구 공고"]])
    a.hl("계약서에는 \"입주권(분양대상) 불인정 시 계약 해제·계약금 반환\" 특약을 꼭 넣으세요.")
    a.text("매도인이 서류 제공을 꺼린다면 **한 번 더 의심**해 보시는 게 좋아요.")

    a.head(9, "📚 6년 뒤 순위, 책은 이렇게 봤어요 [광고·도서 협찬]")
    a.text("빠숑 김학렬 소장님의 《이제부터는 오를 곳만 오른다》 전면개정판은", "관악구를 2026년 **20위**, 2032년 **17위**로 전망했어요.")
    a.text("이건 **지역 단위의 조건부 전망**이에요.", "신림의 개별 구역 가격이나 입주권 승계를 설명하는 숫자는 아니에요.")
    a.fill("책 순위 쪽수·전제 조건 원문 대조 후 한 줄 (출판사 인용 범위 확인)")

    a.head(10, "💡 신림 다음, 마포로의 스텝업")
    a.text("신림에서 신축을 먼저 경험하신 분이라면,", "다음 단계로 **공덕·아현 정비가 마무리되는 마포**를 함께 보시길 권해요.",
           "자금 흐름(전세금·매도금 → 다음 매수)으로 같이 계산해 드릴게요.")

    a.head(11, "정리하면")
    a.text("✔ 신림은 단계가 다른 **10개 사업지** — 구역별로 따로 보세요",
           "✔ 3구역은 입주 완료, 2구역 착공, 1구역 사업시행인가 / 4~10구역은 초기",
           "✔ 관악 최고가는 신림동 힐스테이트뉴포레(84㎡ 17억) — 3구역(84㎡ 중위 10억 5,500)과의 격차는 **규모·생활권 조건** 차이부터 보세요",
           "✔ 여의도는 신림선(전 구간 16분), 강남은 2호선 환승 — **집에서 역까지**가 관건",
           "✔ 난곡선·서부선은 아직 **확정 전**",
           "==후보를 2~3곳으로 좁히면, 서류와 실제 조건으로 같이 비교해 드릴게요.==")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 신림 5~10구역 시행 방식 편을 이어서 올릴게요.",
            "구역 단계: 관악구 재정비촉진구역 현황(2026.10.26)·서울시/관악구 고시 · 실거래: 국토교통부(2025.11~2026.10 계약분, 2026.11.6 조회) · 교통: 서울시 발표 · 난곡선·서부선은 보도 기준 · 이 글은 도서 협찬을 받은 책 소개를 포함한 광고 콘텐츠예요")
    a.signature("grandxi")
    side = ["**제목(BEST)**: 신림 재개발 전망 2026, 지금 사도 될까 (1~10구역 Q&A + 실거래가)",
            "**태그**: 신림재개발, 신림뉴타운, 신림1구역, 신림2구역, 서울대벤처타운역푸르지오, 신림8구역, 관악구재개발, 착한언니복덕방",
            "**썸네일**: 「신림, 10개 구역 단계가 다 달라요」 / 「3구역 84㎡ 11억 8천 (26.9)」 / 「여의도 16분 · 강남은?」",
            "**⚠️ 광고 표기**: 상단·책 소개·하단 3곳 유지 (도서 협찬)",
            "**도면 이미지**: 공식 고시·공고 붙임 도면 (저작권법 제7조) · 실제 지도는 OpenStreetMap (출처 표기 필수) — 출처 캡션 포함, 서울시 신통기획 홈페이지 조감도·위치도는 공공누리 4유형(상업 이용·변경 금지)이라 쓰지 않음",
            "**⚠️ 발행 전**: ✍️ 칸 · 네이버 호가(날짜) · 책 쪽수 대조 · 난곡선 예타(12월) 결과 나오면 갱신"]
    return a, side


def min_guarantee():
    a = Post("2026-11-jeonse-fraud-minimum", "전세사기피해자 최소보장제 2026",
             "출처: 국토교통부 보도자료 「전세사기피해자 최소보장제 시행, 10일부터 최소지원금 신청하세요!」(2026.11.9, 참고 Q&A 포함) · 작성 규칙 MASTER v1.2")
    a.fill("도입 — 보증금 문제로 실제로 받은 상담 한 장면 (익명화, 확인된 것만)")
    a.blank(); a.greet(); a.blank()
    a.text("전세사기 피해를 입으신 분들께 꼭 전해야 할 소식이 있어요.", "**보증금의 3분의 1은 국가가 최소한 돌려받게 해 주는 제도**가 시작돼요.")
    a.quote("**한 줄 요약** 11월 13일 시행 · **11월 10일부터 LH 청약플러스 온라인 신청** · 보증금 1/3에서 이미 회복한 금액을 뺀 만큼 현금 지원", "기본")

    a.head(1, "최소보장제, 한 번에 이해하기")
    a.table(["구분", "최소지원금", "선지급금 (선지급-후정산)"],
            [["누구", "전세사기피해자 + 보증금 5억 이하 등 요건 갖춘 임차인", "**신탁사기 등 무권계약** 피해자"],
             ["얼마", "보증금의 1/3 − 이미 회복한 금액", "보증금의 1/3 (변제받은 금액·임대료 지원 등 차감)"],
             ["언제 신청", "**경·공매 끝난 뒤** (LH 매입이면 경매차익 산정 후)", "**경·공매 끝나기 전**에도 가능"],
             ["특징", "회복금이 1/3 미만일 때 부족분 보전", "먼저 받고, LH 매입 차익 생기면 추가 정산"]],
            note="국토교통부 보도자료 (2026.11.9) 기준 · 세부 요건은 LH 청약플러스 공고문으로 확인")

    a.head(2, "얼마나 받을 수 있나요? (보증금 1억 원 예시)")
    a.table(["경우", "이미 회복한 금액", "최소지원금", "최종 회복"],
            [["경매 배당 1천만 원", "1,000만 원", "[[2,333만 원]]", "3,333만 원 (33.3%)"],
             ["회복한 금액 없음", "0원", "[[3,333만 원]]", "3,333만 원 (33.3%)"],
             ["신탁사기 · 회복 없음", "0원", "선지급 [[3,333만 원]]", "3,333만 원 (33.3%)"]],
            note="국토부 보도자료 예시 · 실제 금액은 피해회복금 산정 결과에 따라 달라져요")
    a.text("여기서 하나는 구분해서 봐야 하는데요,", "**\"이미 회복한 금액\"에 들어가는 것**이 정해져 있어요.")
    a.checks("경매·공매 **배당액**", "임대인이나 공인중개사에게 **변제받은 금액** (공인중개사 손해배상액 포함)",
             "LH 매입 과정의 **경매차익**, 공공임대 **임대료 재정지원액**")
    a.text("반대로 **지방정부 지원금이나 금융지원**은 여기에 들어가지 않아요. (국토부 Q&A)", size=15)

    a.head(3, "신청은 이렇게 해요")
    a.numbered("① 자가 진단", "LH 청약플러스(apply.lh.or.kr)에서 지급 대상인지 먼저 확인할 수 있어요")
    a.numbered("② 신청", "**온라인: 11월 10일부터** LH 청약플러스", "**현장: 11월 13일부터** LH 지역본부 (방문·우편)")
    a.numbered("③ 결정·지급", "LH가 신청일부터 **90일 이내** 결정 (보완 필요 시 30일 연장)", "결정에 이의가 있으면 통지받은 날부터 **30일 이내** 이의신청")
    a.table(["필수 서류", "선택 서류 (해당하는 경우)"],
            [["피해자 결정문 · 임대차계약서 · 주민등록표 초본 · 신분증 · 피해주택 등기사항전부증명서",
              "신탁원부(신탁사기) · 배당표 또는 배분계산서(최소지원금) · 임대인 등에게 변제받은 서류"]])
    a.text("✔ 문의: **LH 콜센터 1600-1004**", size=15)

    a.head(4, "자주 묻는 질문")
    a.text("**Q. 제도 시행 전에 경매가 이미 끝났어요. 받을 수 있나요?**", "네, **경·공매가 이미 끝난 피해자도 지원 대상**이에요. (국토부 Q&A)")
    a.blank()
    a.text("**Q. 언제까지 신청해야 하나요?**", "피해자 결정일부터 **3년 이내** 또는 경·공매 완료일부터 **1년 이내**예요.",
           "제도 시행 전에 피해자로 결정된 분은 **2029년 11월 13일까지** 신청할 수 있어요.")
    a.blank()
    a.text("**Q. 신청할 수 없는 경우도 있나요?**", "대한민국 국적이 없는 경우, 보증금 5억 원 초과 임차인,",
           "피해주택을 **직접 매수한 피해자**, 경·공매에서 **배당요구를 하지 않은 피해자**는 신청할 수 없어요.",
           "(단, 2026.11.13 이전에 최초 경매개시결정 등이 있었던 경우는 배당요구 요건에서 예외)", size=15)

    a.head(5, "착한언니 현장 노트 — 앞으로 계약하실 분들께")
    a.text("최소보장제는 **피해가 난 뒤 최소한을 지켜 주는 제도**예요.", "보증금 전부를 돌려주는 제도는 아니라서, 계약 전에 막는 게 가장 중요해요.")
    a.checks("계약 전 **등기부등본**: 소유자·근저당·**신탁** 여부 (신탁이면 신탁원부까지)",
             "**보증금 반환보증** 가입 가능 여부를 호실별로 먼저 확인",
             "잔금 당일 **전입신고 + 확정일자**")
    a.fill("현장 노트 — 신촌·이대 오피스텔 계약에서 실제로 확인하는 순서 (확인된 것만)")

    a.head(6, "정리하면")
    a.text("✔ **11월 13일 시행**, 온라인 신청은 **11월 10일부터** (LH 청약플러스)",
           "✔ 보증금의 **1/3에서 이미 회복한 금액을 뺀 만큼** 현금 지원",
           "✔ 신탁사기 등 무권계약 피해자는 **경매가 끝나기 전에도 선지급** 신청 가능",
           "✔ 이미 경매가 끝난 피해자도 대상 · 신청 기한 확인",
           "==주변에 해당되는 분이 있다면 이 글을 꼭 전해 주세요.==")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 계약 전 보증금 지키는 순서를 이어서 정리할게요.",
            "국토교통부 보도자료(2026.11.9) 및 참고 Q&A 기준이에요 · 세부 요건·서류는 LH 청약플러스 공고문과 LH 콜센터(1600-1004)로 확인하세요 · 이 글은 법률 자문이 아니에요")
    a.signature("zaiella")
    side = ["**제목(BEST)**: 전세사기피해자 최소보장제 2026｜보증금 1/3 보장, 11월 10일부터 신청하세요 (대상·금액·서류)",
            "**태그**: 전세사기피해자, 최소보장제, 최소지원금, 선지급금, 전세사기지원, LH청약플러스, 신탁사기, 착한언니복덕방",
            "**썸네일**: 「보증금 1/3은 국가가 보장」 / 「11/10부터 온라인 신청」 / 「1억이면 3,333만 원」",
            "**발행 시기**: 신청 시작(11/10) 직후 — 오늘~내일 발행 추천"]
    return a, side

# ======================================================================
def jaechohwan():
    a = Post("2026-11-jaechohwan", "재초환 계산법 2026",
             "출처: 「재건축초과이익 환수에 관한 법률」(2024.3.27 시행) · 권영진 의원실 자료(한국경제 2026.11.8 보도) · 서초구 반포현대 통지 보도(2026.11.9) · 착한언니 노션 「재초환 숫자로 이해하기」 · 작성 규칙 MASTER v1.2")
    I = "../../instagram/cards/2026-11-15-jaechohwan/"
    a.fill("도입 — 재건축 아파트 상담에서 실제로 받은 재초환 질문 한 장면 (익명화, 확인된 것만)")
    a.blank(); a.greet(); a.blank()
    a.text("요즘 뉴스에 **재초환** 이야기가 정말 많죠.", "은마 조합원 1인당 예정액이 **4억 6,334만 원**이라는 기사도 나왔어요.",
           "그런데 막상 \"재초환이 정확히 뭐고, 나도 내야 하나?\" 물으면 헷갈리는 분이 많아요.", "오늘은 **숫자로 한 번에** 정리해 드릴게요.")
    a.quote("**한 줄 요약** 재건축으로 '더 번 돈'에 매기는 부담금 · 1인당 초과이익 8천만 원까지 0원 · 추가분담금과 별개 · 집을 안 팔아도 나올 수 있어요", "기본")

    a.head(1, "재초환이 뭐예요? 오른 집값 전부가 아니에요")
    a.text("재초환은 **재건축초과이익환수제**의 줄임말이에요.",
           "재건축으로 집값이 많이 오르면, 나라가 \"원래 오를 만큼 오른 값이랑 공사비는 빼줄게.",
           "그런데 **재건축으로 더 번 돈은 일부 내!**\" 하는 제도예요.")
    a.table(["단계", "숫자 (가상 예시)"],
            [["새 아파트 다 지은 뒤 집값 (준공)", "20억"],
             ["− 조합 만들 때 집값 (조합설립인가일)", "8억"],
             ["− 원래 오를 만큼 오른 값 (동네 평균 상승분)", "4억"],
             ["− 공사비 등 개발비용", "4억"],
             ["**= 1인당 초과이익**", "[[4억]]"]],
            note="이해를 돕기 위한 가상 계산이에요 · 실제로는 단지 전체 초과이익을 조합원 수로 나눈 평균으로 계산해요")
    a.image(I + "card-1115-2.png", "카드 2장 · 재초환 계산 순서")
    a.text("여기서 꼭 기억할 두 가지가 있어요.")
    a.checks("**추가분담금과는 완전히 별개**예요. 분담금을 냈어도 재초환은 따로 나와요.",
             "**집을 안 팔아도** 낼 수 있어요. 판 이익이 아니라 재건축 전후 집값 차이로 계산해요.")

    a.head(2, "얼마나 내요? 4억 벌면 2억이 아니에요")
    a.text("\"최대 50%\"라는 말 때문에 4억의 절반인 2억을 낸다고 생각하기 쉬운데요,", "**구간별로 나눠서** 넘은 부분에만 부과율이 붙어요.")
    a.table(["1인당 초과이익 구간", "부과율", "4억일 때"],
            [["8천만 원 이하", "면제", "0원"],
             ["8천만 ~ 1억 3천", "10%", "500만 원"],
             ["1억 3천 ~ 1억 8천", "20%", "1,000만 원"],
             ["1억 8천 ~ 2억 3천", "30%", "1,500만 원"],
             ["2억 3천 ~ 2억 8천", "40%", "2,000만 원"],
             ["2억 8천 초과", "50%", "6,000만 원"],
             ["**합계**", "", "[[1억 1,000만 원]]"]],
            note="「재건축초과이익 환수에 관한 법률」 2024.3.27 시행 기준")
    a.hl("초과이익 4억 중 약 27%, 1억 1천만 원이에요.")
    a.image(I + "card-1115-3.png", "카드 3장 · 부과율 구간표")

    a.head(3, "지금 서울은 얼마나 나왔나요?")
    a.text("아래는 기사로 확인된 **조합원 1인당 예정액**이에요.", "==확정 금액이 아니라== 집값과 사업 기간에 따라 바뀌는 미리보기 금액이에요.")
    a.table(["단지", "지역", "1인당 예정액"],
            [["한강맨션", "용산 이촌동", "{{7억 2,210만 원}}"],
             ["은마아파트", "강남 대치동", "4억 6,334만 원"],
             ["래미안 트리니원 (옛 반포3주구)", "서초 반포동", "3억 4,700만 원"],
             ["신길10구역", "영등포 신길동", "2억 8,006만 원"]],
            note="권영진 의원실 자료(한국경제 2026.11.8 보도) · 예정액이며 이의신청·감면을 거쳐 확정돼요")
    a.text("그리고 11월 9일에는 서초구가 **반포현대** 조합에 재초환 **179억 원**을 통지했어요.",
           "조합원 80명, 1인당 약 **2억 2천만 원**이에요. 조합은 50일 안에 이의를 제기할 수 있어요.")
    a.image(I + "card-1115-4.png", "카드 4장 · 서울 1인당 예정액")

    a.head(4, "오래 산 1주택자는 최대 70%까지 줄어요")
    a.text("2024년 개정법부터 **1세대 1주택 장기 보유자 감면**이 생겼어요.", "부과가 끝나는 시점에 1세대 1주택이어야 하고, 보유 기간에 따라 줄어요.")
    a.table(["보유 기간", "6년", "7년", "8년", "9년", "10년", "15년", "20년"],
            [["감면율", "10%", "20%", "30%", "40%", "50%", "60%", "[[70%]]"]],
            note="「재건축초과이익 환수에 관한 법률」 2024.3.27 시행 기준 · 실제 감면은 개인별로 따로 계산돼요")
    a.image(I + "card-1115-5.png", "카드 5장 · 장기 보유 감면 그래프")
    a.text("재건축 단지에 오래 사신 **부모님이 계시다면** 이 부분은 꼭 알려 드리세요.")

    a.head(5, "재초환 통지서, 언제 날아와요?")
    a.table(["시점", "무슨 일", "알아둘 것"],
            [["조합설립인가", "계산 시작", "이때 집값이 시작 가격"],
             ["사업시행인가 후", "첫 예정액 통지", "확정 금액 아님 · 미리보기"],
             ["그 뒤 매년", "예정액 다시 안내", "집값 변동에 따라 금액이 바뀜"],
             ["준공", "계산 종료", "새 아파트 집값이 끝 가격"],
             ["준공 후", "부담금 사전통지", "받은 날부터 **50일 안에** 심사 청구 가능"],
             ["준공 후 5개월 안", "부과 확정", "확정 고지"],
             ["부과일부터 6개월 안", "납부", "1차 납부는 조합 · 조합 해산·체납 시 조합원에게 넘어갈 수 있음"]],
            note="「재건축초과이익 환수에 관한 법률」·찾기쉬운 생활법령정보 기준 · 단지별 실제 일정은 달라요")

    a.head(6, "재건축 아파트, 이 가격에 사도 될까? 내 돈 계산표")
    a.text("지금 재건축 아파트를 사려는 분이라면 **이 순서로 직접 써 보세요.**")
    a.table(["칸", "예시", "내 아파트"],
            [["A. 새 아파트 예상가 (주변 신축 실거래)", "20억", ""],
             ["B. 추가분담금", "4억", ""],
             ["C. 예상 재초환 (예정액 통지 금액 또는 시나리오)", "1억 1천", ""],
             ["D. 취득세·이자 등 부대비용", "대략", ""],
             ["**계산이 맞는 구축 가격 = A − B − C − D**", "[[14억 9천 − D]]", ""]],
            note="가상 예시예요 · 공사비 4억과 추가분담금 4억은 이해를 위해 같게 둔 숫자이고, 법에서 빼주는 개발비용과 분담금은 같은 돈이 아니에요")
    a.text("지금 호가가 \"계산이 맞는 구축 가격\"보다 비싸면,", "**재초환만큼 손해 보고 시작하는 거예요.**",
           "예상 재초환을 모를 땐 C칸을 0원 · 1억 · 2억 · 3억으로 바꿔 가며 써 보세요.", "==재초환이 얼마까지 나와도 괜찮은지== 내 기준선이 보여요.")

    a.head(7, "착한언니 현장 노트")
    a.checks("재초환은 **재건축**에 매기는 부담금이에요. 같은 정비사업이라도 재개발과 헷갈리지 마세요.",
             "내 단지가 어느 단계인지는 **서울시 정비사업 정보몽땅**(cleanup.seoul.go.kr)에서 조합설립인가·사업시행인가 날짜로 확인해요.",
             "준공 전에 입주권을 샀다면, 재초환을 낼 수 있는 **조합원이 바로 나**예요. 계약 전에 최근 예정액 통지 금액부터 확인하세요.")
    a.fill("현장 노트 — 마포·서대문 재건축·재개발 매물 상담에서 실제로 확인하는 순서 (확인된 것만)")

    a.head(8, "자주 묻는 질문")
    a.text("**Q. 재초환, 지금도 적용되는 거 맞아요?**", "네. 2006년 도입, 2013~2017년 유예 후 2018년부터 다시 적용 중이에요.",
           "2019년 헌법재판소 합헌 결정을 받았고, 2024년 3월 개정법이 시행 중이에요. 폐지 법안은 국회에 계류 중이에요(2026년 11월 기준).")
    a.blank()
    a.text("**Q. 추가분담금 냈는데 또 내요?**", "네, 둘은 완전히 별개예요. 분담금은 새 아파트를 짓는 내 몫이고, 재초환은 재건축으로 생긴 이익에 매기는 부담금이에요.")
    a.blank()
    a.text("**Q. 누가 내요?**", "1차로는 **재건축조합**이 내요. 조합이 해산했거나 감당하지 못하면 조합원에게 넘어갈 수 있어요.")

    a.head(9, "정리하면")
    a.text("✔ 재초환은 오른 집값 전부가 아니라 **'더 번 돈'(초과이익)**에 매겨요",
           "✔ 1인당 초과이익 **8천만 원까지 0원**, 넘은 구간에만 10~50%",
           "✔ **추가분담금과 별개**, 집을 안 팔아도 나올 수 있어요",
           "✔ 오래 보유한 1세대 1주택자는 **최대 70% 감면**",
           "✔ 재건축 아파트 살 땐 **A − B − C − D** 계산부터",
           "==재건축 단지에 사시는 부모님·지인께 이 글을 꼭 전해 주세요.==")
    a.text("인스타그램 **@goodsister4080** 게시물에 **'재초환'** 댓글을 남기시면", "재건축 내 돈 계산표와 서울 재건축 89곳 리스트를 DM으로 보내 드려요.", size=15)
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 재건축·재개발 매수 전 체크 순서를 이어서 정리할게요.",
            "「재건축초과이익 환수에 관한 법률」(2024.3.27 시행) 및 언론 보도(2026.11) 기준이에요 · 예정액은 확정 금액이 아니며 실제 부담금은 단지·개인별로 달라요 · 투자 권유가 아닌 정보 제공용이에요")
    a.signature("grandxi")
    side = ["**제목(BEST)**: 재초환 계산법 2026｜재건축 부담금, 4억 벌면 2억? 아니에요 (구간표·감면·내 돈 계산표)",
            "**제목(대안)**: 재건축초과이익환수 쉽게 정리｜은마 4.6억·한강맨션 7.2억, 나도 내야 할까?",
            "**태그**: 재초환, 재건축초과이익환수, 재건축부담금, 재초환계산, 은마아파트, 한강맨션, 반포현대, 재건축투자, 착한언니복덕방",
            "**썸네일**: 인스타 카드 1장 그대로 (「집을 안 팔아도 나오는 돈, 재초환」)",
            "**발행 시기**: 인스타 재초환 카드 올린 날 같이 — 인스타 캡션의 프로필 링크와 서로 연결"]
    return a, side


def jongbuse():
    a = Post("2026-11-jongbuse-notice", "마포 아파트 종부세 고지서 2026",
             "출처: 종합부동산세법(2026.1.1 시행본) · 국세청 홈택스 안내 · 작성 규칙 MASTER v1.2 · ⚠️ 분납·납부유예 세부 기준은 발행 전 홈택스/고지서 원문 확인")
    a.fill("도입 — 매년 이맘때 마포그랑자이 사무소로 오는 종부세 문의 한 장면 (익명화)")
    a.blank(); a.greet(); a.blank()
    a.text("11월 말이면 **종합부동산세 고지서**가 나와요.", "고지서를 받으면 금액부터 보게 되지만,",
           "{{금액보다 먼저 확인할 것}}이 있어요. 잘못 나온 걸 그냥 내면 돌려받기가 번거롭거든요.")
    a.photo("종부세 고지서 예시 (이름·주소·금액 등 개인정보 모두 가림) 또는 홈택스 고지 내역 화면")
    a.quote("**한 줄 요약** 납부는 **12월 1일~15일** · 고지서 받으면 ① 주택 목록 ② 1세대 1주택 적용 ③ 공시가격부터 확인", "기본")

    a.head(1, "종부세, 언제 무엇을 내나요?")
    a.table(["구분", "내용"],
            [["과세 기준일", "매년 **6월 1일** 소유 기준"], ["고지", "11월 말 고지서 발송 (홈택스·모바일 고지 포함)"],
             ["납부 기간", "[[12월 1일 ~ 12월 15일]]"], ["1세대 1주택 공제", "공시가격 합계 **12억 원** (현행)"]],
            note="1주택 공제를 14억 원으로 올리는 안은 국회 논의 단계예요 — 이번 고지서에 적용된다고 보시면 안 돼요")

    a.head(2, "고지서 받으면 이것부터 확인하세요")
    a.checks("**과세 대상 주택 목록** — 이미 판 집, 상속 지분, 오피스텔(주거용 신고분)이 들어가 있는지",
             "**1세대 1주택 적용 여부** — 부부 공동명의, 일시적 2주택, 상속주택 특례 신청 여부",
             "**공시가격** — 올해 공시가격이 맞게 반영됐는지 (부동산공시가격알리미에서 확인)",
             "**세액공제** — 1세대 1주택자의 나이·보유 기간 공제가 들어갔는지")
    a.photo("홈택스 화면 캡처 — 종부세 고지 내역 조회 경로 (개인정보 가림)")
    a.text("✔ 고지 내용이 사실과 다르면 **납부 기한 안에 신고**로 바로잡을 수 있어요 (세무서·세무사 확인)")

    a.head(3, "한 번에 내기 부담된다면 — 분납·납부유예")
    a.table(["제도", "핵심", "확인할 곳"],
            [["분납", "세액이 일정 금액을 넘으면 일부를 **최대 6개월 뒤**에 나눠 낼 수 있어요", "고지서 안내문 · 홈택스 분납 신청"],
             ["납부유예", "요건을 갖춘 **1세대 1주택 고령자·장기보유자**는 집을 팔 때까지 미룰 수 있어요", "나이·보유기간·소득·세액 요건 → 세무서 확인"]],
            note="분납 기준 금액과 납부유예 요건은 블로그마다 다르게 적혀 있어요. 발행 전 법 원문·홈택스 안내로 숫자를 확인해 넣을게요")
    a.text("✔ 분납·유예는 **자동으로 되지 않아요** — 납부 기한 안에 신청해야 해요")

    a.head(4, "마포 아파트 1주택이라면?")
    a.fill("우리 주력 단지(마포그랑자이·마포프레스티지자이·마래푸 등) 공시가격 구간과 종부세 대상 여부 — 공시가격알리미로 확인한 숫자만")
    a.text("공시가격이 공제 금액을 넘지 않으면 1세대 1주택자는 종부세 대상이 아니에요.",
           "대상이 되는 경우에도 **나이·보유 기간 공제**에 따라 실제 세액은 많이 달라져요.",
           "그래서 {{옆집 고지서 금액}}과 비교하실 필요가 없어요.")

    a.head(5, "정리하면")
    a.text("✔ 납부는 **12월 1일~15일**", "✔ 주택 목록·1세대 1주택·공시가격 먼저 확인", "✔ 분납·유예는 기한 안에 신청",
           "✔ 14억 공제안은 아직 논의 단계", "==세금 판단은 세무사 상담으로 확인하세요. 이 글은 일정과 확인 순서 안내예요.==")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 매도·갈아타기 전 세금 체크도 이어서 정리할게요.",
            "종합부동산세법(2026.1.1 시행) 및 국세청 홈택스 안내 기준이에요 · 세액·요건은 개인별로 다르니 고지서와 세무 전문가 상담으로 확인하세요 · 이 글은 세무 자문이 아니에요")
    a.signature("grandxi")
    side = ["**제목(BEST)**: 종부세 고지서 2026｜받자마자 확인할 3가지, 12월 15일까지 납부·분납",
            "**제목(지역)**: 마포 아파트 종부세 2026｜1세대 1주택 12억 공제, 고지서 확인 순서",
            "**태그**: 종부세, 종합부동산세, 종부세고지서, 종부세분납, 종부세납부기간, 1세대1주택, 마포아파트, 착한언니복덕방",
            "**발행 시기**: 고지서 발송 직후 (11월 말) — 미리 써 두고 발송 확인 후 발행",
            "**⚠️ 발행 전**: 분납 기준 금액·납부유예 요건·세액공제율은 법 원문으로 숫자 확인 (이 환경에서 법령 원문이 열리지 않았어요)"]
    return a, side


def officetel_price():
    a = Post("2026-11-officetel-standard-price", "오피스텔 기준시가 조회 2027",
             "출처: 국세청 보도참고자료 「내년도 오피스텔 및 상업용 건물 기준시가 사전열람, 12월 2일까지 의견 제출하세요」(2026.11.12) · 작성 규칙 MASTER v1.2")
    a.fill("도입 — 자이엘라점 오피스텔 소유 고객이 실제로 물어본 질문 1개 (예: “기준시가 오르면 재산세도 올라요?”)")
    a.blank(); a.greet(); a.blank()
    a.text("오피스텔을 갖고 계신 분들, **내년 기준시가(안)**이 공개됐어요.", "**12월 2일까지** 내 호실 금액을 미리 보고, 의견도 낼 수 있어요.")
    a.quote("**한 줄 요약** 서울 오피스텔 기준시가(안) **+2.07%** · 열람·의견 제출 **11.13~12.2** · 재산세·종부세엔 안 쓰여요", "기본")

    a.head(1, "기준시가, 어디에 쓰이나요?")
    a.table(["쓰이는 곳", "안 쓰이는 곳"],
            [["상속·증여 때 시가를 알 수 없을 때", "취득세·재산세"], ["양도세 계산 때 취득가액을 알 수 없을 때", "종합부동산세"], ["", "건강보험료 등 사회보험료"]],
            note="국세청 보도참고자료(2026.11.12) 기준")
    a.text("{{“기준시가가 오르면 재산세도 오른다”}}는 오해가 많은데,", "국세청 설명으로는 **재산세·종부세·건보료에는 쓰이지 않아요.**")

    a.head(2, "얼마나 바뀌었나요?")
    a.table(["지역", "오피스텔", "상업용 건물"],
            [["전국", "-0.47%", "-0.81%"], ["**서울**", "[[+2.07%]]", "+0.28%"], ["경기", "-1.39%", "-1.56%"], ["인천", "-3.03%", "-1.91%"]],
            note="2027년 기준시가(안) 전년 대비 변동률 · 국세청")
    a.text("전국은 2년 연속 내렸지만 **서울 오피스텔은 올랐어요.**", "다만 이건 평균이라 **내 호실은 직접 조회**해 봐야 해요.")

    a.head(3, "내 호실 조회하는 법 (5분)")
    a.text("**국세청 누리집** 첫 화면 배너, 또는", "**홈택스 → 전체메뉴 → 상담·불복·제보 → 기타 → 기준시가 조회 → 오피스텔 및 상업용 건물**",
           "하단의 「2027년 오피스텔 및 상업용 건물 기준시가 고시 전 가격 열람 및 의견 제출」 배너 → 소재지·동·호 입력")
    a.photo("홈택스 화면 캡처 ① 메뉴 경로")
    a.photo("홈택스 화면 캡처 ② 소재지·동·호 입력 화면 (예시 주소는 가림)")
    a.photo("홈택스 화면 캡처 ③ 결과 화면 (금액 가림 또는 예시)")

    a.head(4, "의견은 이렇게 내요")
    a.checks("**온라인**: 같은 조회 화면에서 바로 제출", "**방문·우편**: 의견 제출서 내려받아 관할 세무서에",
             "**상담**: 전용 안내센터 1644-2828 (12월 2일까지)", "제출 의견은 한국부동산원 재조사 → **12월 31일 최종 고시**, 수용 여부 개별 통지")

    a.head(5, "신촌·이대 오피스텔 갖고 계시다면")
    a.fill("자이엘라점에서 관리하는 건물 2~3곳 이름 + 이번 열람에서 확인한 방향 (금액은 소유자 동의 없이 쓰지 않기)")
    a.numbered("올해·내년에 증여나 상속을 생각 중이라면", "기준시가가 세금 계산에 쓰일 수 있어요", "열람 기간에 확인하고 세무 상담으로 시점을 정해요")
    a.numbered("그냥 보유·임대 중이라면", "재산세·종부세와는 별개예요", "열람만 해 두셔도 충분해요")

    a.head(6, "정리하면")
    a.text("✔ 열람·의견 제출 **12월 2일까지**", "✔ 서울 오피스텔 평균 **+2.07%**(안)", "✔ 상속·증여·양도 계산에 쓰이고, 재산세·종부세엔 안 쓰여요",
           "==증여·상속 계획이 있다면 이번 기간에 꼭 조회해 보세요.==")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 신촌·이대 오피스텔 시세도 이어서 정리할게요.",
            "국세청 보도참고자료(2026.11.12) 기준이에요 · 최종 금액은 12월 31일 고시로 확정돼요 · 세금 판단은 세무 전문가와 상담하세요")
    a.signature("zaiella")
    side = ["**제목(BEST)**: 오피스텔 기준시가 조회 2027｜12월 2일까지 열람, 재산세엔 안 쓰여요 (홈택스 경로)",
            "**태그**: 오피스텔기준시가, 기준시가조회, 기준시가열람, 홈택스, 오피스텔증여, 신촌오피스텔, 이대오피스텔, 착한언니복덕방",
            "**썸네일**: 「12월 2일 마감」 / 「서울 오피스텔 +2.07%」 / 「재산세랑 상관없어요」",
            "**발행 시기**: 이번 주 (마감 12/2 전, 늦어도 11/25)"]
    return a, side


def sinchon_room():
    a = Post("2026-11-sinchon-room-guide", "신촌·이대 자취방 구하기 2027",
             "데이터: 국토교통부 오피스텔 전월세 실거래 (마포구·서대문구, 2025.11~2026.11 계약분, 2026.11.17 조회) · 전용 40㎡ 이하 월세 계약 · 작성 규칙 MASTER v1.2")
    a.fill("도입 — 수능·합격 시즌에 자이엘라점으로 오는 학부모님 전화 한 장면 (익명화)")
    a.blank(); a.greet(); a.blank()
    a.text("수능이 끝나고 합격 소식이 들려오는 시기예요.", "신촌·이대 자취방은 **1~2월에 문의가 몰려요.**",
           "오늘은 학부모님들이 가장 많이 물어보시는 **{{“얼마 정도 생각하면 돼요?”}}**에 실거래로 답해 볼게요.")
    a.photo("신촌·이대 거리 사진 (이대역·신촌역 주변, 직접 촬영)")
    a.quote("**한 줄 요약** 신촌·이대 오피스텔 원룸은 **보증금 1,000만 원 · 월세 80~120만 원**대가 가장 많아요 (최근 1년 실거래)", "기본")

    a.head(1, "동네별로 보면")
    a.table(["동", "계약 수", "월세 중위", "많이 보는 학교"],
            [["대현동 (이대 앞)", "575건", "[[95만 원]]", "이화여대 · 연세대"], ["창천동 (신촌역)", "165건", "85만 원", "연세대 · 서강대"],
             ["노고산동 (신촌·서강)", "207건", "80만 원", "서강대 · 연세대"], ["서교동 (홍대)", "130건", "88만 5천 원", "홍익대"],
             ["대흥동 (이대역)", "53건", "110만 원", "이화여대 · 서강대"], ["북아현동 (아현역)", "38건", "127만 원", "이화여대"]],
            note="국토부 오피스텔 전월세 실거래 · 전용 40㎡ 이하 · 보증금 500만~2,000만 원 월세 계약만 · 2025.11~2026.11 계약분 · 관리비 별도")

    a.head(2, "건물별로 보면 (거래 많은 순)")
    a.table(["건물", "동", "준공", "전용", "월세 중위"],
            [["신촌 르메이에르타운5", "창천동", "2005", "25~34㎡", "85만"], ["이대역 푸르지오시티", "대흥동", "2013", "27~30㎡", "109만"],
             ["이대 포레스트", "대현동", "2019", "18㎡", "96만"], ["영타운 지웰 에스테이트", "대현동", "2017", "19~20㎡", "90만"],
             ["에피소드 신촌 369", "노고산동", "2021", "16~32㎡", "118만"], ["더이음", "창천동", "2021", "18~20㎡", "100만"],
             ["신촌푸르지오시티", "대현동", "2014", "23~28㎡", "100만"], ["유씨유 이대", "대현동", "2018", "17~18㎡", "98만"],
             ["이대 더가온", "대현동", "2018", "17~20㎡", "90만"], ["이편한세상신촌(오피스텔)", "북아현동", "2018", "27㎡", "125만"]],
            note="같은 기간·조건 · 대부분 보증금 1,000만 원 · 층·향·옵션에 따라 차이가 커요")
    a.text("✔ **2018년 이후 신축**은 같은 면적이라도 월세가 더 높아요", "✔ **넓은 면적(25㎡ 이상)**은 르메이에르·푸르지오시티처럼 2005~2014년 건물에 많아요",
           "✔ 보증금을 3,000만 원 이상 넣으면 월세가 내려가는 계약도 있어요 (건물마다 달라요)")
    a.photo("오피스텔 원룸 내부 (자사 매물 · 직접 촬영 · 호수 가림)")

    a.head(3, "학부모님이 가장 많이 물어보시는 것")
    a.voice("관리비는 얼마나 나와요?", "보증금 떼일 걱정은 없나요?", "언제부터 알아봐야 해요?")
    a.fill("관리비 실제 수준 — 우리가 중개한 건물 기준 (2026년 ○월, 면적 기준)")
    a.checks("**보증금**: 계약 전 등기부등본 소유자·근저당 확인, 보증보험 가입 가능 여부 확인",
             "**전입신고·확정일자**: 입주 당일 바로", "**시기**: 원하는 건물이 있다면 합격 발표 직후부터 — 1월 말~2월엔 선택지가 줄어요")

    a.head(4, "정리하면")
    a.text("✔ 신촌·이대 원룸은 **보증금 1,000만 · 월세 80~120만 원**대가 가장 많아요", "✔ 신축일수록, 역에 가까울수록 높아요",
           "✔ 관리비·보증금 안전까지 같이 봐야 해요", "==합격 축하드려요! 첫 자취방, 착한언니가 같이 볼게요.==")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 건물별 상세 글도 이어서 올릴게요.",
            "국토교통부 오피스텔 전월세 실거래(2025.11~2026.11 계약분, 2026.11.17 조회) 기준이에요 · 최근 1~2개월은 신고 기한이 남아 늘 수 있어요 · 관리비는 별도예요")
    a.signature("zaiella")
    side = ["**제목(BEST)**: 신촌 이대 자취방 시세 2027｜보증금 1천·월세 얼마? 건물 10곳 실거래",
            "**제목(대안)**: 이대 원룸 오피스텔 월세 2026｜합격 후 자취방, 학부모님 Q&A",
            "**태그**: 신촌자취방, 이대자취방, 신촌원룸, 이대원룸, 신촌오피스텔, 이대오피스텔, 연대자취, 대학생자취방, 착한언니복덕방",
            "**썸네일**: 「신촌·이대 자취방 얼마?」 / 「보증금 1천 · 월세 80~120」 / 「건물 10곳 실거래」",
            "**사진**: 거리 1 · 원룸 내부 2~3 (자사 매물) · 건물 외관 2~3 — 건물 외관은 건물명 검색에도 걸려요",
            "**발행 시기**: 수시 합격 발표가 이어지는 12월 초"]
    return a, side


def lachels():
    a = Post("2026-11-mapo-xi-hillstate-lachels", "마포자이힐스테이트 라첼스 입주 2027",
             "출처: 입주자모집공고(정정, 2024.6.27) · 국토부 주택공급 정례 브리핑(2026.11.13) · 국토부 아파트 전월세 실거래 (2025.10~2026.11 계약분, 2026.11.17 조회) · 작성 규칙 MASTER v1.2")
    a.text("{{1,100세대가 한꺼번에 입주하면, 전세는 얼마까지 내려갈까요?}}")
    a.text("답은 **\"같은 달에도 몇억씩 벌어질 수 있다\"**예요.", "먼저 입주한 단지에서 실제로 그랬거든요.")
    a.text("공덕동 **마포자이힐스테이트 라첼스**,", "**2027년 3월 입주 예정**이에요.")
    a.text("추측 말고,", "**분양 공고와 먼저 입주한 단지의 실거래가**를 보면서", "하나씩 짚어 볼게요.")
    a.blank(); a.greet(); a.blank()
    a.photo("라첼스 공사 현장 외관 (직접 촬영 · 공덕역 방향)")
    a.quote("**한 줄 요약** 1,101세대 · 2027년 3월 입주 예정 · 분양가 59㎡ 12억 5천~13억 4천, 84㎡ 16억 4천~17억 4천", "기본")

    a.head(1, "어떤 단지인가요?")
    a.table(["항목", "내용"],
            [["위치", "마포구 공덕동 (공덕1구역 재건축)"], ["규모", "지하 4층 · 지상 13~22층 · 10개 동 · **1,101세대**"],
             ["구성", "조합 573 · 임대 65 · 일반분양 463세대"], ["시공", "GS건설 · 현대건설"], ["입주", "[[2027년 3월 예정]] (정확한 날짜는 추후 통보)"]],
            note="입주자모집공고(2024.6.27 정정공고) 기준 · 국토부 11.13 브리핑에도 2027년 1분기 주요 입주 단지로 표기")

    a.head(2, "분양가는 얼마였나요?")
    a.table(["타입", "분양가 범위 (층별)"],
            [["59A", "12억 6,330만 ~ 13억 4,070만"], ["59B", "12억 5,140만 ~ 13억 2,880만"],
             ["84A~E", "16억 4,140만 ~ 17억 4,510만"]],
            note="입주자모집공고 공급금액표 · 발코니 확장·옵션 별도 · 분양가상한제 미적용 민영주택")

    a.head(3, "입주장 전세, 얼마쯤 생각해야 할까요?")
    a.text("아직 입주 전이라 이 단지 전세 실거래는 없어요.", "대신 **가까운 신축 단지의 최근 신규 전세**를 참고로 볼게요.")
    a.table(["단지 (준공)", "59㎡ 신규 전세", "84㎡ 신규 전세"],
            [["마포프레스티지자이 (2021)", "9억 3,000 (8건)", "12억 8,000 (4건)"], ["더클래시 (2022)", "9억 (12건)", "12억 3,000 (3건)"],
             ["마포자이더센트리지 (2022)", "8억 7,200 (4건)", "11억 (2건)"], ["마포그랑자이 (2020)", "8억 9,000 (1건)", "11억 (3건)"],
             ["공덕자이 (2015)", "8억 8,000 (4건)", "11억 (1건)"]],
            note="국토부 전월세 실거래 · 2026.10~11 계약분 신규 전세 중위 · 표본 적음 · 최근분은 신고 기한이 남아 늘 수 있어요")
    a.text("{{입주장은 한꺼번에 전세가 나와서}} 주변 시세보다 낮게 계약되는 경우가 많아요.",
           "하지만 얼마나 낮을지는 **입주 시점 물량과 대출 상황**에 따라 달라서 지금 숫자로 단정할 수 없어요.")

    a.head(4, "먼저 입주한 곳은 어땠을까 — 힐스테이트마포더퍼스트")
    a.text("가장 가까운 '입주장 선배'는", "광흥창역 쪽 신수동 **힐스테이트마포더퍼스트**예요.", "2026년 8월 무렵 입주를 시작했어요.")
    a.table(["", "힐스테이트마포더퍼스트", "라첼스"],
            [["위치", "신수동 · 6호선 광흥창역", "공덕동 · 공덕역·애오개역"], ["세대수", "488세대", "**1,101세대** (약 2.3배)"],
             ["입주", "2026년 8월 무렵", "2027년 3월 예정"]],
            note="더퍼스트 세대수·입주는 단지 정보 사이트 기준, 라첼스는 입주자모집공고 기준")
    a.text("더퍼스트 입주장 전세는 이렇게 계약됐어요.")
    a.table(["계약 월", "59㎡ 전세", "84㎡ 전세"],
            [["6~7월 (입주 전)", "8억 5,000 ~ 9억", "10억 ~ 11억 5,000"],
             ["8~9월 (입주 시작)", "8억 3,000 ~ 8억 5,000", "**7억 7,000** ~ 12억 (중위 약 10억)"],
             ["10월", "-", "9억 5,000 ~ 10억 5,000"]],
            note="국토부 전월세 실거래 · 월세 0원 신규 계약만 · 2026.6~10 계약분 · 최근분은 신고가 더 늘 수 있어요")
    a.text("✔ 전세 계약이 **입주 직전·직후 3~4개월에 몰렸어요** (6~10월 39건, 전부 신규)",
           "✔ 84㎡는 같은 달에도 **7억 7천부터 12억까지** 벌어졌어요. 잔금이 급한 집은 낮게, 여유 있는 집은 제값을 받은 흐름이에요",
           "✔ 입주가 지나고 물량이 빠지자 10월엔 **10억 안팎**으로 모였어요")
    a.text("라첼스는 세대수가 **두 배가 넘어서**", "입주장에 한꺼번에 나오는 전세도 더 많을 수 있어요.")
    a.text("그래서 **세입자를 맞춰야 하는 분**은 일찍 준비할수록,", "**전세를 찾는 분**은 입주 지정 기간 초반을 노릴수록", "유리할 가능성이 커요.")
    a.text("※ 단지·입지·시기가 달라 더퍼스트 숫자가 라첼스에 그대로 적용되는 건 아니에요.", size=14, color="#888888")

    a.head(5, "지금 준비할 것")
    a.numbered("입주장 전세를 찾는 분이라면", "원하는 타입·동·층을 미리 정리해요", "보증금 반환보증 가입 가능 여부를 호실별로 확인해요",
               "잔금일과 내 이사 날짜를 맞출 수 있는지 확인해요")
    a.numbered("분양받고 세입자를 맞춰야 하는 분이라면", "잔금대출과 전세 보증금 순서를 먼저 정리해요 (은행 확인 필수)",
               "입주 지정 기간 안에 전세 계약이 되도록 일찍 내놓아요", "같은 타입이 한꺼번에 나오니 **조건(입주 날짜·옵션)**으로 차별화해요")
    a.fill("공덕역·애오개역 동선, 주변 생활 — 직접 걸어본 내용")
    a.photo("공덕역 주변 / 단지 주변 길 (직접 촬영)")

    a.head(6, "정리하면")
    a.text("✔ **2027년 3월 입주 예정** · 1,101세대", "✔ 분양가 59㎡ 12억 5천~13억 4천, 84㎡ 16억 4천~17억 4천",
           "✔ 먼저 입주한 더퍼스트는 입주 전후 넉 달에 전세가 몰렸고, 84㎡가 7억 7천~12억으로 크게 벌어졌어요",
           "==입주장 전세·세입자 맞추기는 미리 준비할수록 유리해요. 12월에 라첼스 매물 접수 안내로 다시 정리할게요.==")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 입주가 가까워지면 실제 전세 계약 흐름을 업데이트할게요.",
            "입주자모집공고(2024.6.27 정정공고)·국토부 실거래(2026.11.17 조회) 기준이에요 · 입주 일정은 공정에 따라 바뀔 수 있어요 · 대출 가능 여부는 은행에 확인하세요")
    a.signature("grandxi")
    side = ["**제목(BEST)**: 마포자이힐스테이트 라첼스 입주 2027｜입주장 전세 얼마? 분양가·주변 신축 전세 비교",
            "**태그**: 마포자이힐스테이트라첼스, 라첼스, 라첼스전세, 공덕1구역, 공덕동아파트, 공덕신축, 입주장전세, 마포아파트, 착한언니복덕방",
            "**썸네일**: 「공덕 라첼스 2027년 3월 입주」 / 「입주장 전세 얼마?」 / 「주변 신축 전세 비교」",
            "**사진**: 공사 현장 외관 2 (가림막 문구·사람 없이) · 공덕역 주변 1 · 주변 신축 단지 외관 1",
            "**⚠️**: 단지명 공식 표기는 '마포자이힐스테이트 라첼스' (띄어쓰기 두 가지 모두 태그에)",
            "**태그 추가**: 힐스테이트마포더퍼스트, 입주장분위기",
            "**후속 글 (12월)**: 「라첼스 입주장 매물 접수 받아요」 — 전세 놓을 집주인·전세 찾는 분 접수형, 그때 실거래 갱신"]
    return a, side


def bukahyeon2():
    a = Post("2026-11-bukahyeon2-relocation", "북아현2구역 이주 시작, 주변 전세",
             "출처: 정비몽땅 사업장 현황 · 언론 보도(MTN 2026.9.23 등) · 국토부 아파트 전월세 실거래 (2025.10~2026.11 계약분, 2026.11.17 조회) · 작성 규칙 MASTER v1.2")
    a.fill("도입 — 신촌·아현에서 최근 받은 이주 관련 문의 한 장면 (익명화)")
    a.blank(); a.greet(); a.blank()
    a.text("북아현2구역이 **정비구역 지정 18년 만에 이주**를 시작했어요.", "이주하는 분들은 가까운 곳에서 집을 찾는 경우가 많아서,",
           "오늘은 **이주 일정**과 **주변 아파트 전세 실거래**를 같이 정리해 볼게요.")
    a.photo("북아현2구역 일대 골목 (직접 촬영 · 번지·사람·차량 번호판 가림)")
    a.quote("**한 줄 요약** 이주 **2026.11.9 ~ 2027.3.8** (보도) · 관리처분인가 2026.4.23 · 재개발 후 약 2,320가구", "기본")

    a.head(1, "북아현2구역, 어디까지 왔나요?")
    a.table(["항목", "내용"],
            [["단계", "[[관리처분인가]] (2026.4.23) → 이주"], ["이주 기간", "2026.11.9 ~ 2027.3.8 (보도)"],
             ["이주비 대출", "HUG 보증 승인, 신청 9.29~10.12 (보도)"], ["재개발 후", "약 2,320가구 (보도마다 2,320~2,350)"]],
            note="단계는 정비몽땅, 일정은 언론 보도 기준 · 정확한 일정은 조합 공지로 확인하세요")
    a.text("이웃한 **북아현3구역**은 사업시행인가 단계에서 조합 운영 문제로 일정이 불확실하다는 보도가 이어지고 있어요.", "두 구역의 속도는 다르게 보셔야 해요.")

    a.head(2, "주변 아파트 전세, 지금 얼마인가요?")
    a.table(["단지 (준공)", "59㎡ 신규 전세", "84㎡ 신규 전세"],
            [["힐스테이트신촌 (2023)", "7억 7,000", "8억 3,500"], ["e편한세상신촌1단지 (2018)", "7억 7,500", "9억 5,000"],
             ["신촌푸르지오 (2015)", "6억 8,000", "9억 5,500"], ["두산 (1999)", "5억 5,000", "-"], ["신촌럭키 (1999)", "4억 8,500", "6억 5,000"],
             ["마포그랑자이 (2020)", "9억 3,000", "11억"], ["마포프레스티지자이 (2021)", "9억 5,000", "12억 5,000"]],
            note="국토부 전월세 실거래 · 2026년 2~3분기 계약분 신규 전세 중위 · 갱신 제외")
    a.text("✔ 같은 북아현동이라도 **연식에 따라 2억 원 넘게** 차이가 나요", "✔ 대흥·염리동 신축(그랑자이·프레스티지자이)은 한 단계 위 가격대예요",
           "✔ 이주 수요가 전세 가격을 얼마나 움직일지는 **단정할 수 없어요** — 물량과 시기를 같이 봐야 해요")

    a.head(3, "이주하시는 분이 챙길 것")
    a.checks("**이주비 대출과 새 집 보증금 순서** — 대출 실행일과 계약 잔금일을 맞춰요",
             "**전입·확정일자** — 새 집 입주 당일", "**보증보험** — 이주용 전세라도 가입 가능 여부부터",
             "**아이 학교** — 전학 여부, 통학 동선")
    a.fill("우리 사무소에서 실제로 도와드린 이주 사례 (익명화, 확인된 것만) 또는 '이주 상담 이렇게 진행해요' 안내")

    a.head(4, "정리하면")
    a.text("✔ 북아현2구역 이주 **2027년 3월 8일까지** (보도)", "✔ 주변 신규 전세는 59㎡ 기준 4억대 후반~9억대까지 연식별로 넓어요",
           "✔ 이주비 대출·잔금·전입 순서를 먼저 맞춰요", "==북아현·아현·신촌 전세, 단지별로 같이 비교해 드릴게요.==")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 북아현3구역 소식도 확인되는 대로 정리할게요.",
            "정비몽땅 단계·언론 보도·국토부 실거래(2026.11.17 조회) 기준이에요 · 이주 일정은 조합 공지가 우선이에요")
    a.signature("zaiella")
    side = ["**제목(BEST)**: 북아현2구역 이주 시작 2026｜이주 기간·주변 아파트 전세 실거래 정리",
            "**태그**: 북아현2구역, 북아현뉴타운, 북아현이주, 북아현동아파트, 힐스테이트신촌, 이편한세상신촌, 신촌푸르지오, 재개발이주, 착한언니복덕방",
            "**썸네일**: 「북아현2구역 이주 시작」 / 「2027년 3월 8일까지」 / 「주변 전세 7곳 비교」",
            "**사진**: 구역 골목 2 · 주변 단지 외관 2~3 — 사람·번지·차량 번호판 가림"]
    return a, side


def imun_newtown():
    a = Post("2026-11-imun-hwigyeong-newtown", "이문휘경뉴타운 구역별 진행 2026",
             "출처: 서울시 정비사업 정보몽땅 사업장 현황 (2026.11.16 수집) · 언론 보도 · 작성 규칙 MASTER v1.2 (11-1 생활 전문지역)")
    a.fill("도입 — 이문동에 사는 사람으로서 지난 2년 동네가 바뀐 장면 1~2문장 (사진과 함께)")
    a.blank(); a.greet(); a.blank()
    a.text("저는 **이문동 래미안라그란데**에 살고 있어요.", "그래서 이문휘경뉴타운은 {{중개사로서도, 주민으로서도}} 매일 보는 동네예요.",
           "구역마다 단계가 달라서 헷갈리시는 분이 많아, 공식 자료로 한 번에 정리해 볼게요.")
    a.image("img/lagrande/01-street-raemian-xi.jpg", "이문동 큰길 — 왼쪽 이문아이파크자이, 오른쪽 래미안라그란데 (2026.11 직접 촬영)")
    a.photo("신축 단지와 공사 중인 구역(이문4구역 등)이 같이 보이는 장면 — 다음 촬영 때")
    a.quote("**한 줄 요약** 이문1·휘경3은 **입주 완료**, 이문3은 **부분 준공**, 이문4는 **관리처분인가 → 이주**", "기본")

    a.head(1, "구역별로 어디까지 왔나요?")
    a.table(["구역", "단지명", "정비몽땅 단계", "메모"],
            [["이문1", "래미안라그란데", "준공인가", "2025년 1월 입주 시작"], ["이문3", "이문아이파크자이", "[[부분준공인가]]", "4,321가구 (보도)"],
             ["이문4", "(미정)", "**관리처분인가**", "3,488가구 계획 · 이주 진행, 2027년 상반기 착공 예정 (보도)"],
             ["휘경3", "휘경자이디센시아", "준공인가", ""], ["휘경5", "-", "추진위원회승인", "초기 단계"],
             ["신이문역세권", "-", "조합설립인가", "장기전세주택 도시정비형"], ["신이문2 역세권", "-", "정비계획 수립", "초기 단계"]],
            note="단계는 서울시 정비사업 정보몽땅(2026.11.16 수집) · 가구 수·일정은 언론 보도 기준 · 휘경1·2구역은 사업을 마치고 조합이 해산된 구역이에요")
    a.photo("구역별 위치를 표시한 지도 (직접 제작 또는 네이버 지도 캡처에 표시)")

    a.head(2, "살면서 느끼는 변화")
    a.fill("변화 ① — 상권·편의시설 (사진)"); a.photo("변화 ① 사진")
    a.fill("변화 ② — 도로·통학·교통 (아쉬운 점도 솔직하게)"); a.photo("변화 ② 사진")
    a.text("언론에서도 {{“신축은 많이 들어섰는데 길은 그대로”}}라는 지적이 있었어요.", "사는 사람 입장에서 맞는 부분과 아닌 부분을 적어 볼게요.")
    a.fill("도로·교통 지적에 대한 생활자 의견 (확인된 것만)")

    a.head(3, "구역별로 볼 때 체크할 것")
    a.checks("**입주 완료 단지**(이문1·3, 휘경3): 실거래·전세 만기 시점", "**이주 중인 구역**(이문4): 착공 시점, 주변 전세 수요",
             "**초기 구역**(휘경5·신이문2): 권리산정기준일, 동의율, 지분 쪼개기 제한")

    a.head(4, "정리하면")
    a.text("✔ 이문1·휘경3 입주 완료, 이문3 부분 준공", "✔ 이문4는 관리처분인가 후 이주 — 다음 큰 변화", "✔ 휘경5·신이문2는 아직 초기",
           "==제가 사는 동네라, 【동대문 생활 노트】로 단계가 바뀔 때마다 업데이트할게요.==")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 래미안라그란데 입주 2년 차 이야기도 함께 보세요.",
            "서울시 정비사업 정보몽땅(2026.11.16 수집)·언론 보도 기준이에요 · 단계와 구청 고시가 다르면 고시가 우선이에요")
    a.signature("grandxi")
    side = ["**제목(BEST)**: 이문휘경뉴타운 구역별 진행 2026｜이문4구역 이주, 휘경5구역까지 한눈에 (주민이 정리)",
            "**태그**: 이문휘경뉴타운, 이문4구역, 이문3구역, 휘경5구역, 래미안라그란데, 이문아이파크자이, 휘경자이디센시아, 동대문재개발, 착한언니복덕방",
            "**썸네일**: 「이문휘경뉴타운 지금 어디까지?」 / 「주민이 정리한 구역별 단계」",
            "**사진**: 대표님 사진이 핵심 — 동네 변화 3~5장 · 구역 지도 1장",
            "**연결**: 래미안라그란데 2년 차 글과 서로 링크"]
    return a, side


def deal_story():
    a = Post("2026-11-deal-story-template", "거래 후기 (템플릿)",
             "템플릿: 「홍은벽산 9억 2천 매매 후기」(2026.11.11, 블로그탭 4위) 구성 기준 · 개인정보 제외 · 작성 규칙 MASTER v1.2 (현장 노트는 실제 경험만)")
    a.text("⚠️ 이 글은 **실제 거래 경험으로만** 채워요. 빨간 칸에 대표님 이야기를 넣어 주세요.", size=14, color="#d0021b")
    a.fill("도입 — 손님과 처음 만난 장면 (언제, 어떤 계기로 · 이름·나이·직업 등 특정 정보 빼기)")
    a.blank(); a.greet(); a.blank()
    a.quote("**한 줄 요약** [단지명] [면적] [금액] [매매/전세] — [이 거래의 한 줄 포인트]", "기본")
    a.photo("단지 외관 (직접 촬영 · 동 번호 노출 주의)")

    a.head(1, "이분이 찾던 집")
    a.fill("조건 3가지 (예: 예산, 통근, 학교) — 숫자는 범위로")
    a.head(2, "같이 본 집들")
    a.fill("비교한 단지 2~3곳과 각각의 장단점 (다른 단지 깎아내리지 않기)")
    a.table(["단지", "면적", "최근 실거래", "장점", "아쉬운 점"], [["✍️", "", "", "", ""], ["✍️", "", "", "", ""]],
            note="실거래는 국토부 실거래 기준으로 제가 채워 드릴게요 (단지명만 알려 주세요)")
    a.head(3, "결정한 이유")
    a.fill("결정의 순간 — 손님이 한 말 한 줄 (허락받은 범위)")
    a.head(4, "계약부터 잔금까지")
    a.fill("기억에 남는 과정 1~2개 (가계약금, 특약, 잔금일 조율 등) — 다른 손님께 도움이 되는 팁으로")
    a.photo("계약 후 사진 (손님 동의 시 · 얼굴 가림 또는 손·열쇠만)")
    a.head(5, "착한언니 체크포인트")
    a.checks("✍️ 이 거래에서 배운 점 1", "✍️ 이 거래에서 배운 점 2", "✍️ 비슷한 조건의 분께 드리는 한마디")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 다음 거래 이야기도 들려드릴게요.",
            "손님 동의를 받아 개인을 알 수 없도록 각색했어요 · 금액은 국토부 실거래 공개 범위 기준이에요")
    a.signature("grandxi")
    side = ["**제목 공식**: [단지명] [금액] [매매/전세] 후기｜[손님 상황 한 줄] (예: 홍은벽산 9억 2천 매매 후기｜첫 자취방 손님의 일곱 번째 계약)",
            "**왜 잘 되나**: 단지명 + 금액이 검색어 · 실제 이야기라 체류 시간이 길어요",
            "**후보**: 최근 계약 중 손님 동의 받은 건 — 단지명·면적·금액만 알려 주시면 실거래 표를 채워 드려요",
            "**주의**: 동·호수, 계약일 정확한 날짜, 손님 직업·나이는 쓰지 않기 · 사진은 손님 동의 필수",
            "**태그**: [단지명], [단지명]매매, [단지명]후기, [동네]아파트, 매매후기, 착한언니복덕방"]
    return a, side


def public_redev_fee():
    a = Post("2026-11-public-redevelopment-fee", "공공재개발 수수료 1% 계산법",
             "출처: 국토교통부 보도자료 「공공재개발 사업수수료 3%→1% 한시 인하」(2026.11.12) · 서울시 정비사업 정보몽땅 (2026.11.16 수집) · 작성 규칙 MASTER v1.2")
    a.fill("도입 — 정비사업 상담에서 들은 질문 1개 (예: “공공재개발 하면 LH가 수수료 많이 떼가지 않아요?”)")
    a.blank(); a.greet(); a.blank()
    a.text("공공재개발 **사업수수료가 3%에서 1%로** 내려가요.", "그런데 {{모든 공공재개발 구역에 적용되는 건 아니에요.}}",
           "오늘은 누가 적용받는지, 그리고 실제로 얼마나 줄어드는지 **계산표**로 보여드릴게요.")
    a.quote("**한 줄 요약** **2027년 12월 31일까지 후보지를 새로 신청하는 구역만** 1% · 국비 15% 지원 유지 → 실부담 0.85%", "기본")

    a.head(1, "무엇이 바뀌었나요?")
    a.table(["구분", "기존", "바뀐 뒤"],
            [["사업수수료", "총사업비의 3%", "[[총사업비의 1%]]"], ["국비 지원", "수수료의 최대 15%", "그대로 유지"],
             ["실제 부담", "2.55%", "**0.85%**"], ["적용 대상", "-", "**'27.12.31까지 후보지 신규 신청 구역**"]],
            note="국토교통부 보도자료(2026.11.12) · 민간 방식으로 추진하던 구역도 기간 안에 공공재개발 후보지로 신청하면 적용")

    a.head(2, "우리 구역이면 얼마? — 계산표")
    a.table(["총사업비", "기존 3%", "→ 1%", "국비 15% 반영 시", "줄어드는 금액 (국비 반영)"],
            [["3,000억", "90억", "30억", "76억 5천 → 25억 5천", "**51억**"], ["5,000억", "150억", "50억", "127억 5천 → 42억 5천", "**85억**"],
             ["7,200억", "216억", "72억", "183억 6천 → 61억 2천", "[[122억 4천]]"], ["1조", "300억", "100억", "255억 → 85억", "**170억**"]],
            note="계산: 총사업비 × 수수료율 × (1 − 국비 15%) · 7,200억은 국토부 예시(약 2,200세대)와 같은 조건 · 국비는 사업 단계별로 지원 · 국토부 발표 '구역당 평균 약 130억 원 절감'")
    a.text("✔ 국토부 예시(총사업비 약 7,200억 원)로는 **216억 → 72억**, 국비까지 반영하면 **184억 → 61억**이에요",
           "✔ 조합원 수로 나누면 1인당 부담이 얼마나 줄어드는지 감이 와요", "✔ 다만 **분담금 전체**는 공사비·분양가·비례율에 따라 훨씬 크게 움직여요 — 수수료는 그중 일부예요")

    a.head(3, "오해하기 쉬운 3가지")
    a.numbered("“이미 공공재개발 하는 우리 구역도 1%?”", "**아니에요.** 2027년 말까지 **새로 후보지를 신청하는 구역**이 대상이에요",
               "예: 동대문 전농9구역(LH 공공재개발)·용두1구역 6지구 등 이미 진행 중인 구역은 해당 여부를 조합에 확인하세요")
    a.numbered("“용적률 1.3배, 동의율 60%도 확정?”", "**아직이에요.** 용적률 1.3배는 법 개정안 본회의 상정 예정, 시행자 지정 동의 60%는 제도개선 추진 중이에요",
               "현재는 법적상한용적률 1.2배, 시행자 지정 동의 2/3")
    a.numbered("“수수료 줄면 분담금도 그만큼 준다?”", "수수료 절감은 확실한 플러스지만, 분담금은 공사비·분양 수입 영향이 더 커요")

    a.head(4, "정리하면")
    a.text("✔ **'27.12.31까지 새로 신청하는 구역만** 1%", "✔ 국비 15%까지 받으면 실부담 **0.85%**",
           "✔ 7,200억 사업장 기준 수수료 **216억 → 72억** (국비 반영 시 184억 → 61억)", "✔ 용적률 1.3배·동의 60%는 아직 미확정",
           "==우리 구역이 해당되는지, LH 컨설팅(서부권 02-6213-0011 · 동부권 02-6215-0011)에서 확인할 수 있어요.==")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 재초환 계산법에 이어 정비사업 계산 시리즈로 정리할게요.",
            "국토교통부 보도자료(2026.11.12) 기준이에요 · 계산표는 이해를 돕는 예시이며 실제 수수료는 사업계획에 따라 달라요 · 이 글은 투자 권유가 아니에요")
    a.signature("grandxi")
    side = ["**제목(BEST)**: 공공재개발 수수료 1% 계산법 2026｜우리 구역이면 얼마 줄어들까? (계산표)",
            "**태그**: 공공재개발, 공공재개발수수료, 공공재개발1%, LH공공재개발, 재개발분담금, 정비사업, 재초환계산법, 착한언니복덕방",
            "**썸네일**: 「공공재개발 수수료 3%→1%」 / 「7,200억이면 216억 → 72억」 / 「기존 구역은 해당 없을 수도」",
            "**사진**: 필요 없음 — 계산표를 카드 이미지 1장으로 만들어 넣으면 좋아요 (원하시면 만들어 드려요)",
            "**연결**: 재초환 계산법 글(11/14)과 서로 링크 — '정비사업 계산 시리즈'"]
    return a, side


def registry_fee():
    a = Post("2026-11-registry-fee", "등기부등본 수수료 인상 2026",
             "출처: 대법원 「등기사항증명서 등 수수료규칙」 개정 (2026.11.12 발표, 11.23 시행) · 법률신문·뉴스1 보도(2026.11.12) · 작성 규칙 MASTER v1.2")
    a.fill("도입 — 계약 전에 등기부를 같이 떼어 보던 상담 한 장면 (익명화, 확인된 것만)")
    a.blank(); a.greet(); a.blank()
    a.text("집 계약할 때 제일 먼저 보는 서류, **등기부등본**이죠.", "그 등기부 열람·발급 수수료가 **11월 23일부터 400원씩** 올라요.",
           "{{20년 넘게 그대로였던 금액}}이라 기사도 많이 나왔는데요, 오늘은 얼마로 바뀌는지와", "그래도 **언제는 꼭 떼어 봐야 하는지**를 정리해 드릴게요.")
    a.quote("**한 줄 요약** 2026년 11월 23일부터 인터넷 열람 700원 → **1,100원** · 발급 1,000원 → **1,400원** · 방문 1,200원 → **1,600원**", "기본")

    a.head(1, "얼마나 오르나요?")
    a.table(["구분", "지금", "11월 23일부터"],
            [["인터넷 열람", "700원", "[[1,100원]]"], ["인터넷·무인 발급", "1,000원", "[[1,400원]]"],
             ["등기소 방문 열람·발급", "1,200원", "[[1,600원]]"], ["20장 초과 시 추가", "장당 50원", "장당 50원 (그대로)"]],
            note="대법원 「등기사항증명서 등 수수료규칙」 개정 (2026.11.12 발표) · 법률신문·뉴스1 보도 기준")
    a.text("✔ 모든 항목이 **똑같이 400원씩** 올라요", "✔ 20장 넘는 등기부의 장당 추가 요금은 그대로예요")

    a.head(2, "왜 올리나요?")
    a.text("대법원 설명으로는, 등기 시스템을 운영하는 **등기특별회계가 2022년부터 적자**예요.",
           "부동산 거래가 줄어 수입은 줄었는데, 시스템 운영비는 늘었다는 거예요.",
           "수수료는 짧게는 22년, 길게는 29년 동안 동결돼 있었어요.")
    a.text("늘어난 재원은 AI 등기정보 분석 같은 **새 등기 시스템 구축**에 쓰고,", "재정이 회복되면 예전(2002년·2005년)처럼 **다시 내리는 방안도 검토**하겠다고 밝혔어요.")

    a.head(3, "반대 목소리도 있어요")
    a.table(["입장", "주장"],
            [["한국공인중개사협회 · 국회 청원", "등기 확인은 전세사기를 막는 기본 절차 → 인터넷 열람·발급 **무료화** 요구 (청원 5만 명 넘어 법사위 회부)"],
             ["대법원", "무료화하면 대출·체납 같은 민감 정보가 프로그램으로 대량 수집될 우려 · 특정 직군 비용을 세금으로 메우게 됨"]],
            note="2026.11.12~13 보도 기준 · 각 주체의 입장을 소개한 것이에요")
    a.text("대법원은 보완책으로 국토교통부 **안심전세앱**에서 선순위 권리 같은 필수 등기정보를 **무료로 확인하는 기능을 개발 중**이라고 했어요.",
           "==아직 개발 중이라, 지금은 등기부를 직접 떼어 보셔야 해요.==")

    a.head(4, "그래도 이 세 번은 꼭 떼어 보세요")
    a.numbered("① 계약금 넣기 전", "소유자가 계약하는 사람과 같은지, 근저당·압류·가압류가 있는지 확인해요")
    a.numbered("② 잔금 치르는 날 아침", "계약 뒤에 새로 생긴 근저당이나 압류가 없는지 **당일에 다시** 확인해요")
    a.numbered("③ 전입신고·확정일자 다음 날", "잔금일에 몰래 들어온 권리가 없는지 마지막으로 확인해요")
    a.hl("세 번 다 떼도 인터넷 열람 기준 3,300원이에요. 보증금을 생각하면 아끼면 안 되는 돈이에요.")

    a.head(5, "등기부, 어디를 보면 돼요?")
    a.text("실제로 저희가 계약 전에 뽑아 본 등기부로 보여드릴게요.", "(소유자·주소·호수 같은 개인정보는 모두 가렸어요)")
    a.text("[[① 맨 앞 「주요 등기사항 요약」부터]]", "인터넷 열람 때 함께 나오는 **참고용 요약**이에요.",
           "**소유자가 누구인지(갑구)**, **근저당·전세권이 있는지(을구)**가 한 장에 정리돼 있어요.")
    a.image("img/registry/01-summary.jpg", "주요 등기사항 요약 (참고용) — 소유자·지분, 근저당 '기록사항 없음' (개인정보 모자이크)")
    a.text("✔ 다만 요약은 **증명서 효력이 없는 참고용**이라, 뒤쪽 본문까지 꼭 확인해요")
    a.text("[[② 표제부 — 이 집이 맞는지]]", "주소·동·호수, **전용면적**이 계약서와 같은지 봐요.", "오피스텔은 면적이 작아서 계약서 면적과 다르면 바로 물어보세요.")
    a.image("img/registry/02-pyojebu.jpg", "표제부 — 1동 건물, 대지권, 전유부분(전용면적) (주소·호수 모자이크)")
    a.text("[[③ 갑구 — 집주인이 맞는지]] [[④ 을구 — 빚이 있는지]]",
           "갑구의 **소유자 이름**이 계약하는 사람과 같은지, 압류·가압류가 없는지 확인해요.",
           "을구에 **근저당·전세권**이 있으면 금액(채권최고액)을 확인하고, **'기록사항 없음'**이면 깨끗한 상태예요.")
    a.image("img/registry/03-gapgu-eulgu.jpg", "갑구(소유권) · 을구(소유권 이외의 권리) — 을구 '기록사항 없음' (소유자 정보 모자이크)")
    a.text("✔ 줄이 그어진 부분은 **이미 지워진(말소된) 기록**이에요. 지금 살아 있는 권리만 보면 돼요")

    a.head(6, "열람과 발급, 뭐가 달라요?")
    a.table(["", "열람", "발급"],
            [["용도", "내용 확인용 (화면·출력)", "제출용 증명서"], ["11/23부터", "1,100원", "1,400원"], ["추천", "계약 전 확인은 **열람으로 충분**", "은행·관공서 제출 때"]],
            note="대법원 인터넷등기소(iros.go.kr)에서 열람·발급 가능")
    a.fill("착한언니 현장 노트 — 우리 사무소는 계약 때 등기부를 어떻게 같이 확인해 드리는지 (실제 방식만)")

    a.head(7, "정리하면")
    a.text("✔ **11월 23일부터** 등기부 열람 1,100원 · 발급 1,400원 · 방문 1,600원", "✔ 적자 때문이라는 대법원, 무료화하자는 중개사협회·청원 — 의견이 갈려요",
           "✔ 안심전세앱 무료 확인은 아직 개발 중", "✔ 계약금 전 · 잔금 당일 · 전입 다음 날, **세 번은 꼭** 확인하세요",
           "==400원 올라도, 등기부 확인은 내 보증금을 지키는 가장 싼 보험이에요.==")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 등기부에서 꼭 볼 칸 3곳도 이어서 정리할게요.",
            "대법원 수수료규칙 개정(2026.11.12 발표, 11.23 시행) 및 법률신문·뉴스1 보도 기준이에요 · 시행 후 금액은 인터넷등기소 공지로 한 번 더 확인하세요")
    a.signature("zaiella")
    side = ["**제목(BEST)**: 등기부등본 수수료 인상 2026｜11월 23일부터 열람 1,100원, 그래도 꼭 떼야 하는 3번",
            "**제목(대안)**: 등기부등본 열람 1,100원으로 인상｜왜 올리나, 무료화 청원은?",
            "**태그**: 등기부등본, 등기부등본수수료, 등기부등본열람, 등기사항증명서, 인터넷등기소, 전세사기예방, 안심전세앱, 착한언니복덕방",
            "**썸네일**: 「등기부등본 400원 인상」 / 「11월 23일부터 1,100원」 / 「그래도 꼭 떼야 하는 3번」",
            "**발행 시기**: 시행 전 (11/20~22) 추천 — 시행 당일 검색이 몰려요",
            "**사진**: 실제 등기부 3장 배치 완료 (소유자·주민번호 앞자리·주소·호수·고유번호 모자이크) · 예비 2장(영타운 요약·표제부)은 img/registry/04·05"]
    return a, side


def swiss_grand():
    a = Post("2026-11-swiss-grand-hotel", "스위스그랜드호텔 부지 아파트 개발 2026",
             "출처: 블로터 「[부동산 PF 점검] 연합와이앤제이, 스위스그랜드호텔 '종상향' 과제」(2026.11.3) · 르데스크(2026.10.30) · 네이트뉴스 보도(2026.11.5) · 서울시 정비사업 정보몽땅(2026.11.18 수집) · 작성 규칙 MASTER v1.2")
    a.fill("도입 — 이 호텔에 얽힌 개인적인 기억 한 줄 (결혼식·행사·지나다니던 길 등, 사실만) + 영업 종료 후 현장 사진")
    a.blank(); a.greet(); a.blank()
    a.text("홍은동 **스위스그랜드호텔**(옛 그랜드힐튼서울)이 **11월 9일 영업을 마쳤어요.**",
           "그 자리에 **약 1,300가구 아파트**를 짓는다는 소식에 문의가 많은데요,",
           "기사마다 숫자가 달라서 {{\"벌써 1,300가구 확정됐대요\"}}라는 말까지 돌고 있어요.",
           "오늘은 **확정된 것과 아직 아닌 것**을 나눠서 정리해 볼게요.")
    a.photo("호텔 정문·간판 + 영업 종료 안내문 (직접 촬영 · 사람·차량 번호판 없이)")
    a.quote("**한 줄 요약** 매각·영업 종료는 끝났어요 · 1,300가구·2027년 6월 착공은 시행사 '목표' · 지으려면 용도지역 상향(종상향)이 먼저예요", "기본")

    a.head(1, "어떤 호텔이었나요?")
    a.table(["항목", "내용"],
            [["위치", "서울 서대문구 **홍은동** (흔히 '홍제동 그랜드호텔'로 불러요)"], ["개관", "1988년 서울올림픽을 앞두고 관광숙박시설 특례로 건립"],
             ["이름", "2002~2020년 '그랜드힐튼서울' → 2020년부터 '스위스그랜드호텔'"], ["규모", "객실 396실 · 레지던스 · 대형 연회·컨벤션"],
             ["영업 종료", "[[2026년 11월 9일]] (10월 28일 공식 SNS 공지)"]],
            note="블로터(2026.11.3) 보도 기준")

    a.head(2, "확정된 것 vs 아직 아닌 것")
    a.table(["구분", "내용", "상태"],
            [["소유권", "기존 소유주(동원아이엔씨 측) → 개발 법인 **홍제353PFV**", "✅ 2026년 7월 이전 (보도)"],
             ["영업", "호텔 영업 종료", "✅ 11월 9일"],
             ["자금", "부지 매입·초기 사업비 **브리지론 4,500억 원** (키움증권)", "✅ 조달 (공사비 아님)"],
             ["규모", "호텔+주변 땅 약 **3만 9,101㎡**에 공동주택 약 **1,300가구**", "🟡 시행사 계획"],
             ["착공", "**2027년 6월** 착공", "🟡 시행사 목표"],
             ["용도지역", "제2종일반주거 → 상향(종상향)", "⏳ 확정 안 됨"],
             ["공공기여", "방식·규모", "⏳ 확정 안 됨"],
             ["건축비", "본PF(공사비 대출)", "⏳ 남은 단계"]],
            note="블로터(2026.11.3)·르데스크(2026.10.30) 보도 기준 · 소유권 이전 시점은 7월(블로터·르데스크)과 8월(일부 보도)로 엇갈려요")
    a.photo("부지 전경 — 길 건너편 또는 언덕 위에서 (직접 촬영)")

    a.head(3, "1,300가구, 왜 '종상향'이 관건일까요?")
    a.text("이 땅은 지금 **제2종일반주거지역**이에요.", "서울시 조례 기준 용적률 상한이 **200%**예요.",
           "보도에 따르면 1,300가구 규모를 맞추려면 **준주거지역 수준(용적률 400%)으로 상향**이 필요하다는 업계 전망이 나와요.")
    a.text("용도지역을 올리려면 서울시 도시계획 절차를 거쳐야 하고,", "그 대가로 **공공기여**(기부채납, 공공임대 등)를 얼마나 할지 정해야 해요.",
           "==그래서 지금은 \"아파트 개발 추진 중\"이 맞고, \"1,300가구 확정\"은 아니에요.==")

    a.head(4, "'1,358가구·34층' 기사, 지금 계획과 달라요")
    a.text("검색하면 **1,358가구·지상 34층·9개 동**이라는 숫자도 나와요.",
           "이건 **2023년 서대문구가 검토한 '상생주택' 구상**이에요. 공공임대 270가구를 포함한 안이었고,", "**최종 인허가를 받지 못해** 실제 개발로 이어지지 않았어요.")
    a.text("✔ 지금 사업 주체(연합와이앤제이·홍제353PFV)와 계획은 그때와 달라요", "✔ 그때의 공공임대 270가구를 지금 계획에 그대로 적용할 수 없어요")

    a.head(5, "4,500억 원, 공사비가 아니에요")
    a.text("기사에 나온 **4,500억 원**은 **브리지론**이에요.", "땅을 사고 초기 비용을 내는 데 쓰는 **단기 대출**이에요.",
           "실제 아파트를 짓는 공사비는 용도지역·공공기여·공사비가 정해진 뒤 **본PF**로 따로 조달해야 해요.")
    a.table(["", "브리지론", "본PF"],
            [["언제", "땅 살 때", "착공 전"], ["용도", "토지 매입·초기 사업비", "공사비 등 건축 자금"], ["이 사업", "✅ 4,500억 조달", "⏳ 아직"]])

    a.head(6, "주변도 같이 움직여요")
    a.text("호텔 하나만 바뀌는 게 아니에요. 홍은·홍제 일대에서 여러 사업이 동시에 진행 중이에요.")
    a.table(["사업", "규모(계획)", "단계"],
            [["고은산 서측 도심공공주택 복합사업 (홍제동 360-6 일대)", "2,577가구", "2026.9.4 복합지구 지정"],
             ["홍은15구역 재개발 (홍은동 8-400)", "1,834가구", "조합설립인가 (2026.3)"],
             ["홍은5구역 재건축 (홍은동 277-45)", "604가구", "사업시행인가"],
             ["홍제3구역 재건축 (홍제동 104-41)", "확인 필요", "**관리처분인가**"],
             ["홍제역 역세권활성화 (인왕시장·유진상가 일대)", "1,010가구 (보도)", "정비몽땅 '사업시행인가' · 보도는 통합심의 조건부 의결 → 확인 중"],
             ["홍은13구역 (서대문센트럴아이파크)", "827세대", "2026.9 **준공**"]],
            note="단계는 서울시 정비사업 정보몽땅(2026.11.18 수집) · 고은산 서측은 르데스크(2026.10.30) · 가구 수는 계획 기준이라 바뀔 수 있어요 · 홍은·홍제 정비사업 전체 정리는 다음 글에서")
    a.photo("홍제역·유진상가 일대 또는 홍은15구역 골목 (직접 촬영)")

    a.head(7, "논란도 함께 알아 두세요")
    a.checks("**컨벤션 기능 상실** — 서북권 대표 연회·컨벤션 시설이 사라지는 문제가 보도됐어요",
             "**주민 반발** — 고층 개발에 따른 경관·일조 우려가 제기되고 있어요 (보도)",
             "**친일재산 논란** — 호텔 주변 임야의 국가귀속 소송은 2023년 대법원에서 정부 패소로 확정됐어요")

    a.head(8, "착한언니 체크 — 이 소식 보고 근처 집을 본다면")
    a.numbered("호가와 실거래를 꼭 나눠 보세요", "개발 소식이 나오면 호가가 먼저 움직여요",
               "보도에도 인근 빌라 41㎡가 지난해 9월 2억 2,500만 원에 거래됐는데 지금 호가가 2억 6,000만 원이라는 사례가 나왔어요")
    a.numbered("'확정' 단어를 확인하세요", "종상향·공공기여·본PF가 남아 있어요", "일정이 늦어질 수 있다는 전제로 자금 계획을 세워요")
    a.numbered("소유자는 등기부로 직접", "개발 부지든 내가 살 집이든, 소유자와 근저당은 등기부로 확인해요 (11월 23일부터 열람 1,100원)")
    a.fill("착한언니 현장 노트 — 홍은·홍제 손님 문의에서 느끼는 분위기 (확인된 사실만, 가격 전망 없이)")

    a.head(9, "정리하면")
    a.text("✔ **매각·영업 종료는 끝났어요** (소유권 이전 2026년 7월, 영업 종료 11월 9일)",
           "✔ **1,300가구·2027년 6월 착공은 시행사 목표**예요",
           "✔ 남은 관문: **종상향 → 공공기여 → 본PF**",
           "✔ 1,358가구·34층은 2023년 구청 구상 — 지금 계획과 달라요",
           "✔ 주변에 고은산 서측·홍은15·홍제역 일대까지 함께 움직여요",
           "==서대문 사무소에서 진행 상황이 바뀔 때마다 업데이트할게요.==")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 다음 글은 홍은·홍제 정비사업 전체 지도예요.",
            "블로터(2026.11.3)·르데스크(2026.10.30) 등 보도와 서울시 정비사업 정보몽땅(2026.11.18) 기준이에요 · 계획·일정은 인허가 과정에서 바뀔 수 있어요 · 이 글은 투자 권유가 아니에요")
    a.signature("zaiella")
    side = ["**제목(BEST)**: 스위스그랜드호텔 부지 아파트 2026｜1,300가구 확정일까? 확정된 것 vs 아닌 것 (홍은동 옛 그랜드힐튼)",
            "**제목(대안)**: 홍제동 그랜드호텔 영업 종료, 아파트는 언제? 종상향·브리지론 쉽게 정리",
            "**태그**: 스위스그랜드호텔, 그랜드힐튼서울, 홍은동아파트, 홍제동개발, 홍은동재개발, 서대문구개발, 고은산서측, 홍은15구역, 착한언니복덕방",
            "**썸네일**: 「그랜드호텔 자리에 1,300가구?」 / 「확정 vs 아직」 / 「종상향이 관건」",
            "**사진(촬영 목록)**: ① 정문·간판·영업종료 안내문 ② 부지 전경 ③ 홍제역·유진상가 또는 홍은15 골목 ④ (있으면) 예전 호텔 사진 — 공공 도로에서만, 사람·차량 번호판 없이",
            "**⚠️ 발행 전**: 홍제역 역세권활성화 단계(정비몽땅 vs 보도), 홍제3구역 가구 수 확인 · 소유권 이전 7월/8월 보도 엇갈림 → 등기부 열람으로 확인 가능"]
    return a, side


def ahyeon_nogosan():
    a = Post("2026-11-ahyeon1-nogosan", "아현1구역·노고산동 재개발, 정말 될까?",
             "출처: 마포구의회 의견청취안(아현1 의안 25-137·2025.11 / 마포4구역 5·6·7·10지구 의안 26-29·2026.2 / 마포3구역 3지구 의안 25-139·2025.11, 마포구청 제출) · 서울시 보도자료(2026.6.28·8.7) · 하우징워치(2025.9.30·2026.11.17)·머니투데이(2026.11.11)·월간도시(2026.5.30) · 마포구 구역공개(2025.1) · 작성 규칙 MASTER v1.2")
    A = "img/ahyeon1/"; N = "img/nogosan/"
    a.text("아현1구역 3,476세대.", "신촌 노고산동 49층.")
    a.text("요즘 두 사무실에서", "제일 자주 듣는 동네 이야기예요.")
    a.text("그런데 저는 기사 제목보다", "{{\"이게 정말 될까?\"}}가 더 궁금하더라고요.")
    a.text("그래서 구청이 구의회에 낸", "**정비계획 원문**을 직접 찾아 읽어봤어요.", "팩트는 짧게, 제 생각은 솔직하게 써볼게요.")
    a.blank(); a.greet(); a.blank()
    a.quote("**결론부터** 아현1은 '될까'보다 '얼마에 될까'가 문제 · 노고산 5·6·7·10지구는 철거 끝난 빈 땅, 셋 중 가장 현실적 · 3지구는 멈췄다가 철거 시작 · 19-1은 아직 일러요", "기본")
    a.text("※ 정비계획(안)·심의 단계 수치라 바뀔 수 있어요.", "투자 권유가 아니라 제 개인적인 분석이에요.", size=14, color="#888888")

    a.head(1, "아현1구역, 막힌 건 풀었어요")
    a.image(A + "01-location.jpg", "아현1구역 위치 (아현동 699 일대) — 아현역·애오개역·충정로역 사이 / 마포구의회 의견청취안(2025.11, 마포구청 제출)")
    a.table(["", "팩트"],
            [["규모", "3,476세대 · 최고 35층 · 10만 6천㎡"], ["시행", "SH 공공재개발"],
             ["단계", "정비구역 지정(2026.5) → SH 사업시행자 지정(2026.9) → 첫 주민총회(11.7)"],
             ["권리산정기준일", "**2020.8.20** (서울시 고시 제2020-346호)"]],
            note="마포구의회 의견청취안·언론 보도 기준")
    a.text("이 동네가 20년 멈춰 있던 이유는", "딱 하나예요.")
    a.text("**지분이 너무 잘게 쪼개져 있었거든요.**")
    a.text("80년대 판자촌을 허물고", "주민들이 직접 빌라를 지으면서", "한 필지를 여러 명이 나눠 가졌어요.")
    a.text("지분이 작으면 새 아파트를 못 받아요.", "그래서 **740명**이 현금청산 대상이었고,", "이분들 입장에선 재개발에 찬성할 이유가 없었죠.")
    a.text("SH가 내놓은 답이 **14㎡(약 4.5평) 아파트 30세대**예요.", "가장 작은 새 집 값을 1억 9천만 원대로 낮춰서", "지분이 작은 분들도 분양 자격을 갖게 한 거예요.")
    a.text("[[740명 → 156명]]")
    a.text("저는 이 부분은 **정말 잘 풀었다**고 봐요.", "사람을 살리는 쪽으로 구조를 바꾼 거니까요.")

    a.head(2, "그런데, 이게 정말 될까?")
    a.text("막힌 걸 풀었다고", "사업성이 생긴 건 아니에요.", "제가 걸리는 건 세 가지예요.")
    a.text("[[① 일반분양이 사실상 없어요]]")
    a.table(["전용", "전체", "토지등소유자 분양", "임대·공공분양"],
            [["14㎡", "30", "30", "-"], ["29㎡", "810", "679", "131"], ["39㎡", "847", "494", "353"],
             ["49㎡", "515", "475", "40"], ["59㎡", "892", "**863**", "29"], ["84㎡", "382", "239", "143"],
             ["**합계**", "**3,476**", "**2,780**", "**696**"]],
            note="마포구의회 의견청취안 '주택의 규모 및 규모별 건설비율' · 최종 분양은 사업시행인가 시 확정")
    a.text("3,476세대 중 2,780세대가", "원래 주인들 몫이고, 나머지는 임대예요.")
    a.text("보통 재개발은 일반분양으로 번 돈으로", "공사비를 메우는데,", "여기는 **그 돈이 거의 없어요.**")
    a.text("결국 공사비는", "조합원(토지등소유자)이 나눠 낸다고 봐야 해요.")
    a.text("[[② 작은 평형이 너무 많아요]]")
    a.text("29~49㎡가 **1,648세대**예요. (조합원 분양분 기준)", "지분이 작은 분이 그만큼 많다는 뜻이고,", "큰 평형으로 갈 수 있는 분은 적다는 뜻이에요.")
    a.text("[[③ 높낮이 차가 59m인 언덕이에요]]")
    a.text("영화 '기생충' 계단 장면, 기억나시죠?", "언덕 땅은 깎고 다지는 데부터 돈이 들어요.", "공사비가 평지보다 쉽게 내려가긴 어려워요.")
    a.image(A + "03-site-plan.jpg", "아현1구역 배치도 — 획지1 966세대·획지2 2,510세대 / 마포구의회 의견청취안(2025.11)")
    a.table(["항목", "정비계획(안) 추정"],
            [["조합원 분양가", "59㎡ 10억 · 84㎡ 12억 5,800만"], ["권리가액 5.5억 가정 분담금", "49㎡ 약 3.3억 · 59㎡ 약 4.4억"], ["추정 비례율", "102.58%"]],
            note="하우징워치(2025.9.30) 보도의 2025.9 주민설명 추정치 · 인근에선 59㎡ 분담금이 10억에 이를 수 있다는 말도 나온다는 보도(머니투데이 2026.11.11)")
    a.text("그래도 플러스는 있어요.", "SH가 시행하니까", "**이주비 최대 3억(LTV 40%)**, **공사비 최대 70% 대출**이 붙어요.", "민간이었으면 여기까지 오지도 못했을 거예요.")

    a.head(3, "착한언니 생각 — 아현1구역")
    a.text("저는 **\"되긴 될 것 같다\"** 쪽이에요.", "공공이 붙었고, 주민총회까지 열렸으니까요.")
    a.text("다만 진짜 질문은", "{{\"얼마를 내고 들어가느냐\"}}예요.")
    a.text("그게 처음 숫자로 나오는 게", "**시공사 선정(2027년 상반기 목표)** 때예요.", "그 전까지는 분담금 숫자는 다 추정이에요.")
    a.checks("**지분 매수를 생각하신다면** — 권리산정기준일(2020.8.20) 이후 쪼갠 지분은 입주권이 안 나올 수 있어요",
             "**지하층·무허가 건물**은 아직 구제 대상이 아니에요 (약 130세대, 소송 진행 여지)",
             "공부해 보실 만한 곳이지만, **시공사·공사비가 나오기 전 판단은 이르다**고 봐요")
    a.photo("아현1구역 언덕길·계단 (직접 촬영 — 경사가 보이게)")

    a.head(4, "노고산동은 '지구'로 쪼개서 봐야 해요")
    a.text("노고산동은 아현1처럼", "한 번에 짓는 재개발이 아니에요.")
    a.text("신촌역 일대를 작은 **'지구'**로 나눠서", "지구마다 따로 지어요.", "그래서 같은 동네인데 속도가 다 달라요.")
    a.image(N + "01-mapo4-districts.jpg", "신촌지역 마포4구역 지구별 추진현황 — 15지구 완료, 9·10·12지구 관리처분인가 / 마포구의회 의견청취안(2026.2)")
    a.text("이 동네에 개발 얘기가 끊이지 않는 이유는", "결국 **입지**예요.")
    a.text("연대·이대·서강대가 받쳐주는 **대학가**,", "서강대교만 건너면 **여의도**,", "**2호선 한 번**이면 강남이에요.")
    a.text("이게 어떤 느낌인지는", "신촌로터리 건너편을 보면 바로 알아요.")
    a.image(N + "site-11-sinchon2-2-gate.jpg", "신촌로터리 건너편 서대문구 창천동 2-2지구 — 이미 크레인이 올라갔어요 (직접 촬영 2026.11)")
    a.table(["", "신촌 2-2지구 (서대문구 창천동 18-42)"],
            [["규모", "지하 5층 ~ 지상 22층 · 오피스텔·근린생활시설"], ["공사기간", "**2026.1.20 ~ 2028.6.30** (착공)"],
             ["용적률", "834.81%"], ["시공", "대명건설"]],
            note="현장 건축허가표지판 (서대문구청) 기준")
    a.image(N + "site-13-sinchon2-2-permit.jpg", "2-2지구 건축허가표지판 (직접 촬영)")
    a.text("같은 '신촌지역 도시정비형 재개발'인데", "여기는 벌써 짓고 있고,", "길 건너 노고산동은 이제 철거 중이에요.")
    a.text("**지구마다 시계가 따로 가는 거예요.**")

    a.head(5, "① 5·6·7·10지구 — 셋 중 제일 현실적이에요")
    a.table(["", "팩트"],
            [["위치", "노고산동 109-62 일대 (서강대역~신촌역 사이)"], ["계획", "지상 49층 · **497세대** (공공임대 53)"],
             ["단계", "도시계획위원회 수정가결(6.26) → **정비계획 변경 결정 고시 (2026.9.23)**"]],
            note="서울시 보도자료(2026.6.28) · 서울특별시고시 제2026-543호(서울시보 제4181호)")
    a.image(N + "07-gosi-plan-before.jpg", "정비계획 결정도 (기정) — 10지구와 작은 5·6·7지구가 따로 / 서울특별시고시 제2026-543호(2026.9.23)")
    a.image(N + "08-gosi-plan-after.jpg", "정비계획 결정도 (변경) — 4개 지구 통합 / 서울특별시고시 제2026-543호(2026.9.23)")
    a.text("제가 여기를 제일 현실적으로 보는 이유는", "**10지구가 이미 관리처분인가(2025.3)까지** 받은 곳이라서예요.")
    a.text("권리관계가 정리된 땅에", "혼자서는 못 짓던 옆의 작은 땅(5·6·7지구)을", "**붙인 거예요.**")
    a.text("그리고 주용도를 **업무 → 주거**로 바꿨어요.", "요즘 시장에서 오피스보다", "주거가 더 확실하다고 본 판단 같아요.")
    a.text("정비계획 변경 **고시도 9월 23일에 이미 났어요.**", "서류상 첫 관문은 넘은 거예요.")
    a.text("그리고 직접 가봤더니,", "**땅이 이미 비어 있어요.**")
    a.image(N + "site-06-mapo4-10-cleared-lot.jpg", "마포4-10지구 현장 — 철거가 끝나고 빈 땅만 남았어요 (직접 촬영 2026.11)")
    a.image(N + "site-09-mapo4-10-demolition-sign.jpg", "해체공사 안내 표지판 — 노고산동 109-91 외 25필지, 해체규모 7,558㎡, 2025.8.18~2026.1.31 (직접 촬영)")
    a.text("철거 표지판엔 **2025년 8월~2026년 1월**로 적혀 있고,", "지금은 풀만 자란 빈 땅이에요.")
    a.text("빈 땅이 됐다는 건", "이주·철거라는 **제일 시끄러운 고비를 넘겼다**는 뜻이에요.", "제가 셋 중 여기를 제일 현실적으로 보는 이유가 하나 더 생긴 거죠.")
    a.image(N + "site-10-sogang-exit1.jpg", "서강대역 1번 출구 — 현장까지 걸어서 금방이에요 (직접 촬영)")
    a.text("✔ 지켜볼 것: 사업시행계획 변경인가 → 관리처분 변경 → **착공 시점**", "✔ 49층 초고층이라 공사비가 얼마로 나오는지")

    a.head(6, "② 3지구 — 멈췄다가, 다시 움직여요")
    a.table(["", "예전(2022)", "지금"],
            [["층수", "27층", "**42층**"], ["세대", "288", "**298**"], ["평형", "소형 위주", "59·84㎡ 중형 위주"],
             ["단계", "관리처분인가까지 받고 멈춤", "**2026.8.6 통합심의 조건부 의결**"]],
            note="구의회 의견청취안(2025.11) · 서울시 발표(2026.8.7)")
    a.image(N + "05-mapo33-site-plan.jpg", "마포3구역 3지구 배치도 — 42층 2개 동, 신촌로터리 방면 30m 도로 / 구의회 의견청취안(2025.11)")
    a.text("재밌는 건 이 부분이에요.", "층수는 거의 **두 배**가 됐는데", "세대수는 **10세대**만 늘었어요.")
    a.text("작은 집을 많이 짓던 계획을", "**팔리는 중형 평형**으로 바꾼 거예요.", "방향은 맞다고 봐요.")
    a.text("이곳은 2022년에", "관리처분까지 받고도 **사업성 때문에 멈췄던** 곳이에요.")
    a.text("그런데 현장에 가보니", "**철거가 시작됐어요.**")
    a.image(N + "site-01-mapo33-fence-rotary.jpg", "마포3구역 3지구 현장 — 신촌로터리 쪽 가림막 (직접 촬영 2026.11)")
    a.image(N + "site-04-mapo33-demolition-sign.jpg", "해체공사 안내 표지판 — 노고산동 31-77 외 13필지, 2026.9.1~2027.1.31, 진행공정 철거공사 (직접 촬영)")
    a.text("표지판을 보면", "**2026년 9월 ~ 2027년 1월 철거**,", "통합심의 통과(8.6) 한 달 만에 바로 들어갔어요.")
    a.text("멈췄던 곳이 다시 움직이는 건 **분명**해요.")
    a.text("다만 철거는 착공이 아니에요.", "땅 3,245㎡에 42층 2개 동이면", "공사비 부담이 작지 않거든요.")
    a.text("✔ 철거가 끝나는 내년 초,", "**착공과 공사비가 실제로 따라오는지** 보면 돼요")

    a.head(7, "③ 19-1 일대 — 아직 일러요")
    a.image(N + "06-nogosan19-boundary.jpg", "노고산동 19-1 일대 구역계 (신청인 제출안) / 마포구 구역공개(2025.1)")
    a.image(N + "site-17-nogosan19-aerial-school.jpg", "창천초등학교 뒤편 노고산 언덕 저층 주택가 — 19-1 일대 방향 (직접 촬영 2026.11)")
    a.text("신속통합기획 후보지에서 **2025년 6월 떨어졌어요.**", "반대 동의율이 취소 요건(25%)에 가까웠다고 해요.", "2025년 11월부터 다시 동의서를 받고 있지만", "**아직 후보지도 아니에요.**")
    a.image(N + "site-15-nogosan19-banner.jpg", "골목에 걸린 '노고산동 신속 민간재개발 추진위원회' 현수막 (직접 촬영 · 연락처 가림)")
    a.text("골목엔 추진위원회 현수막이 걸려 있어요.", "하고 싶은 분들이 있다는 건 분명한데,", "**반대하는 분들도 그만큼 있다는 게** 지난번 결과였죠.")
    a.text("관심 있으시면 공부는 해두시되,", "지금 판단할 단계는 아니라고 봐요.")

    a.head(8, "한 장으로 정리하면")
    a.table(["구역", "착한언니 한 줄"],
            [["아현1구역", "되긴 될 것 같아요. 관건은 **분담금** → 시공사 선정 때 다시 보기"],
             ["노고산 5·6·7·10지구", "셋 중 **가장 현실적** (9.23 고시 · 철거 끝난 빈 땅) → 착공 시점 보기"],
             ["노고산 3지구", "멈췄다가 **철거 시작** (~2027.1) → 착공·공사비 따라오는지 보기"],
             ["노고산 19-1", "**아직 일러요** → 후보지 선정 여부부터"]])
    a.text("두 동네 다 저희 사무실에서 걸어서 갈 거리라,", "단계가 바뀔 때마다 다시 정리해 드릴게요.")
    a.photo("지도 — 스마트에디터 「지도」로 아현1구역·노고산동·두 사무소 위치 표시")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 노고산동 지구별 도면은 「신촌 노고산동 재개발 2026」 글에 따로 정리했어요.",
            "도면 출처: 마포구의회 의견청취안(마포구청 제출, 2025.11·2026.2), 마포구 구역공개(2025.1) · 수치는 정비계획(안)·심의 단계 기준이라 최종 고시와 다를 수 있어요 · 이 글은 투자 권유가 아닌 개인적인 분석이에요")
    a.signature("grandxi")
    side = ["**제목(BEST)**: 아현1구역·노고산동 재개발, 정말 될까?｜착한언니가 정비계획 원문 읽고 따져봤어요",
            "**제목(대안)**: 아현1구역 재개발 2026｜14㎡로 청산 740명→156명, 그런데 분담금은? (노고산동 49층·42층까지)",
            "**태그**: 아현1구역, 아현1구역재개발, 공공재개발, 노고산동재개발, 마포4구역, 마포3구역3지구, 신촌재개발, 마포재개발, 착한언니복덕방",
            "**톤**: 짧은 줄바꿈 · 팩트는 표로 · 판단은 '되긴 될 것 같다 / 지켜봐야 / 아직 이르다' 3단계 (투자 권유 표현 없음)",
            "**도면 7장**: 아현1 위치도·배치도(구의회 의견청취안), 노고산 지구현황·결정도 기정/변경·3지구 배치도·19-1 구역계 — 투시도·조감도는 설계 저작물일 수 있어 제외",
            "**지도**: 스마트에디터 「지도」(네이버 지도) 첨부 추천 — 플레이스 연결에 유리",
            "**현장 사진 반영 (11/21 촬영)**: 2-2지구 착공 현장·허가표지판, 4-10지구 빈 땅·해체 표지판, 서강대역, 3지구 가림막·해체 표지판, 19-1 언덕·추진위 현수막 — 얼굴·번호판·연락처 블러",
            "**사진 (촬영 남음)**: 아현1 언덕길·계단 1장"]
    return a, side


def nogosan():
    a = Post("2026-11-nogosan-redevelopment", "신촌 노고산동 재개발 2026",
             "출처: 마포구의회 의견청취안 「신촌지역 마포4구역 및 5·6·7·10지구 정비구역 및 정비계획 결정(변경)」(의안 26-29, 2026.2)·「신촌지역 마포3구역 3지구 정비계획 결정(변경)」(의안 25-139, 2025.11) · 서울시 보도자료(2026.6.28 제8차 도시계획위원회, 2026.8.7 통합심의) · 마포구 구역공개(노고산동 19-1, 2025.1) · 위클리한국주택경제(2025.11.18) · 하우징워치(2022.11.14) · 국토부 실거래 · 작성 규칙 MASTER v1.2")
    I = "img/nogosan/"
    a.text("{{신촌역 앞에 49층 아파트, 정말 들어설까요?}}")
    a.text("답은 **\"한 곳은 이미 철거가 끝났다\"**예요.", "다만 바로 옆 블록은 이제 철거 중이고,", "언덕 위는 아직 시작도 안 했어요.")
    a.text("신촌역 바로 남쪽인데도", "**아파트가 거의 없던 동네**, 노고산동이에요.", "자이엘라점에서 길만 건너면 나와요.")
    a.text("기사 말고,", "**정비계획 원문·고시 도면·현장 사진**을 보면서", "하나씩 짚어 볼게요.")
    a.blank(); a.greet(); a.blank()
    a.quote("**한 줄 요약** 마포3구역 3지구 42층 298세대(통합심의 통과) · 마포4구역 5·6·7·10지구 49층 497세대(정비계획 변경 통과) · 19-1은 아직 출발 전", "기본")

    a.head(1, "먼저, 노고산동 재개발은 '지구' 단위예요")
    a.text("신촌역 일대는 2014년 **'신촌지역(마포) 도시환경정비구역'**으로 지정됐어요 (서울시 고시 제2014-304호).",
           "아파트 재개발처럼 구역 전체를 한 번에 짓는 게 아니라, 구역을 **작은 '지구'로 나눠 지구마다 따로** 사업을 해요.",
           "그래서 같은 구역 안에서도 **어떤 지구는 다 지었고, 어떤 지구는 아직 시작도 안 했어요.**")
    a.table(["구분", "아파트 재개발(예: 아현1구역)", "노고산동 도시정비형 재개발"],
            [["단위", "구역 전체 한 번에", "**지구별**로 따로"], ["용도지역", "주거지역 위주", "**일반상업·준주거** (역세권)"],
             ["건물", "단지형 아파트", "**초고층 주상복합** (40층대)"], ["시행", "조합·SH 등", "주로 **토지등소유자**"]])
    a.text("신촌로터리 건너편 **서대문구 창천동 2-2지구**를 보면 감이 와요. 같은 '신촌지역' 도시정비형 재개발인데, 여기는 2026년 1월에 이미 착공했어요.")
    a.image(I + "site-11-sinchon2-2-gate.jpg", "신촌지역 도시정비형 재개발구역 2-2지구 (서대문구 창천동 18-42) — 크레인이 올라간 착공 현장 (직접 촬영 2026.11)")
    a.image(I + "site-13-sinchon2-2-permit.jpg", "2-2지구 건축허가표지판 — 지하 5층~지상 22층 오피스텔·근생, 공사기간 2026.1.20~2028.6.30, 시공 대명건설 (직접 촬영)")

    a.head(2, "마포4구역, 19개 지구 지금 어디까지?")
    a.text("마포4구역(노고산동 107-1 일대, 5만 2,583㎡)은 **19개 지구**로 나뉘어 있어요. 구청 자료의 현황표예요.")
    a.image(I + "01-mapo4-districts.jpg", "신촌지역 마포4구역 지구별 추진현황 및 위치도 (마포구의회 의견청취안 2026.2, 마포구청 제출)")
    a.table(["지구", "단계 (구청 자료 기준)"],
            [["1지구", "사업시행계획인가 (2025.2.13)"], ["9지구", "관리처분계획인가 (2025.11.13)"], ["**10지구**", "**관리처분계획인가 (2025.3.27)**"],
             ["12지구", "관리처분계획인가 (2025.9.25)"], ["15지구", "**사업 완료** (2025.5.29, 83.9m 업무시설)"], ["5·7지구 등", "미시행 / 6지구 등은 존치"]],
            note="마포구의회 의견청취안(의안 26-29, 2026.2) 추진현황표 기준")
    a.photo("15지구 완공 건물과 주변 지구 (신촌역 남측 대로변, 직접 촬영)")

    a.head(3, "① 마포4구역 5·6·7·10지구 — 서강대역~신촌역 사이 49층")
    a.text("가장 큰 변화는 **노고산동 109-62 일대**예요.",
           "이미 관리처분인가까지 받은 **10지구**에, 땅이 작고 경사가 심해 혼자 개발하기 어려웠던 **5·6·7지구를 합쳐서** 한 번에 짓기로 했어요.")
    a.image(I + "07-gosi-plan-before.jpg", "정비계획 결정도 (기정) — 10지구와 5·6·7지구가 나뉘어 있던 모습 / 서울특별시고시 제2026-543호(2026.9.23)")
    a.image(I + "08-gosi-plan-after.jpg", "정비계획 결정도 (변경) — 5·6·7·10지구 통합, 문화공원 부담 추가 / 서울특별시고시 제2026-543호(2026.9.23)")
    a.text("✔ 이 계획은 **2026년 9월 23일 정비계획 변경 결정 고시**까지 끝났어요 (서울시보 제4181호)")
    a.table(["항목", "기존 (10지구)", "변경 (5·6·7·10지구)"],
            [["시행면적", "4,750.7㎡", "[[7,813.2㎡]]"], ["주용도", "업무", "**주거**"],
             ["높이", "89m 이하 (준주거 79m)", "**165m 이하** (구의회 안) → 서울시 발표 **최고 161m·지상 49층**"],
             ["용적률 (일반상업)", "500/660/767.71%", "600/659/**973%** (구의회 안) → 서울시 발표 **939%**"],
             ["세대수", "-", "[[497세대]] (공공임대 53 포함)"]],
            note="구의회 의견청취안(2026.2) → 서울시 도시계획위원회 수정가결(2026.6.26) 결과로 일부 수치 조정 · 최종 수치는 정비계획 변경 고시로 확인")
    a.table(["전용면적", "일반분양", "공공임대"],
            [["40㎡ 이하", "28", "22"], ["40~60㎡", "**290**", "22"], ["60~85㎡", "79", "9"], ["85㎡ 초과", "47", "-"], ["**합계**", "444", "53"]],
            note="구의회 의견청취안 '주택의 규모 및 규모별 건설비율' 기준 · 총 497세대")
    a.text("✔ **높이가 왜 이렇게 높아졌나요?** 서울시가 2025년 규제를 풀면서 신촌 일대 기준높이를 80m(이면부 60m)에서 **130m로 일괄 완화**했고,",
           "도로·공원 같은 공공용지를 내놓은 만큼 **35m를 더** 올려 165m까지 가능해졌어요",
           "✔ 서강대역에서 신촌역까지 **폭 6m 이상 평탄한 보행통로**, 경의선숲길과 이어지는 소공원, 2층 문화시설(가칭 '서강대역 스페이스')·주거안심종합센터가 들어서요",
           "✔ 단지 안에는 어린이놀이터·경로당·어린이집·주민운동시설이 계획돼 있어요")
    a.text("✔ [[현장은 지금 — 철거가 끝난 빈 땅이에요.]] 해체공사 표지판 기준 노고산동 109-91 외 25필지, 해체규모 7,558㎡, 공사기간 2025.8.18~2026.1.31 (시공 자이에스앤디)")
    a.image(I + "site-08-mapo4-10-gate.jpg", "「신촌(마포)4-10지구 도시정비형 재개발사업」 공사장 출입구 (직접 촬영 2026.11)")
    a.image(I + "site-06-mapo4-10-cleared-lot.jpg", "가림막 안쪽 — 철거를 마치고 비어 있는 부지 (직접 촬영)")
    a.image(I + "site-09-mapo4-10-demolition-sign.jpg", "해체공사 안내 표지판 (마포구청장) — 2025.8.18~2026.1.31")
    a.image(I + "site-10-sogang-exit1.jpg", "서강대역 1번 출구 — 현장 바로 옆이에요 (직접 촬영)")

    a.head(4, "② 마포3구역 3지구 — 신촌로터리 대로변 42층 2개 동")
    a.text("두 번째는 **노고산동 31-77 일대**(3,245㎡), 신촌로터리 방면 30m 대로에 붙은 자리예요.",
           "2022년에 사업시행인가와 관리처분인가까지 받았지만, 사업성이 맞지 않아 멈춰 있었어요.",
           "규제 완화를 반영해 계획을 다시 짰고, **2026년 8월 6일 서울시 통합심의를 조건부로 통과**했어요.")
    a.image(I + "04-mapo33-building-table.jpg", "신촌지역(마포) 3-3지구 건축계획(안) — 지하 6층·지상 42층, 298세대 (마포구의회 의견청취안 2025.11)")
    a.image(I + "05-mapo33-site-plan.jpg", "배치도 — 42층 2개 동, 신촌로터리 방면 30m 도로 접함")
    a.table(["항목", "예전 계획 (2022)", "새 계획"],
            [["층수", "최고 27층 (보도)", "[[지상 42층 (146.97m)]]"], ["세대수", "288세대 (소형 위주)", "**298세대** (59㎡대 222 · 84㎡ 38 · 133㎡ 1 등)"],
             ["용적률", "806.5% 이하", "**987.73%** (법정 1,009% 이하)"], ["주차", "-", "321대"],
             ["특별시설", "-", "**청년창업정보교육센터 · 외국인주민센터**"]],
            note="구의회 의견청취안(의안 25-139, 2025.11) 건축계획(안) · 재개발 의무 공공임대 15세대 포함 · 통합심의 조건부 의결 내용에 따라 바뀔 수 있어요")
    a.text("✔ **외국인주민센터**가 들어서는 건 연세대·이화여대·서강대 유학생이 많은 신촌 특성을 반영한 거예요",
           "==서울시 지정 글로벌 부동산중개사무소인 그랑자이점과도 연결되는 변화라 반가운 소식이에요.==")
    a.text("✔ [[현장은 지금 — 철거 중이에요.]] 해체공사 표지판 기준 노고산동 31-77 외 13필지, 연면적 3,983.7㎡, **2026.9.1~2027.1.31**, 진행공정 '철거공사' (시공 자이에스앤디)",
           "통합심의 통과 한 달 만에 철거에 들어간 거라, 멈췄던 사업이 **다시 움직이는 건 분명**해요. 다만 철거 다음 **착공·분양 일정**은 아직 발표 전이에요")
    a.image(I + "site-01-mapo33-fence-rotary.jpg", "마포3구역 3지구 — 신촌로터리 쪽 가림막 (직접 촬영 2026.11)")
    a.image(I + "site-03-mapo33-gate.jpg", "3지구 공사장 출입구 (직접 촬영)")
    a.image(I + "site-04-mapo33-demolition-sign.jpg", "해체공사 안내 표지판 (마포구청장) — 2026.9.1~2027.1.31, 진행공정 철거공사")
    a.image(I + "site-05-sinchon-exit6.jpg", "신촌역 6번 출구 — 3지구는 출구 바로 앞이에요 (직접 촬영)")

    a.head(5, "③ 노고산동 19-1 일대 — 아직 출발 전")
    a.image(I + "06-nogosan19-boundary.jpg", "노고산동 19-1번지 일대 구역계 (신청인 제출안, 마포구 구역공개 2025.1) — 후보지 추천 시 변경될 수 있음")
    a.table(["시기", "내용"],
            [["2009.10", "단독주택재건축 정비구역 지정"], ["2013.4", "정비구역 **해제**"], ["2022", "신속통합기획 공모 신청 (동의율 약 61%, 보도)"],
             ["2025.3", "신통 후보지 신청"], ["2025.6.30", "**미선정** — 반대 동의율이 입안취소 요건(25%)에 근접, 찬반 갈등"],
             ["2025.11", "동의서 번호 다시 부여 → **재도전**"]],
            note="위클리한국주택경제(2025.11.18)·하우징워치(2022.11.14) 보도 · 2026년 후보지 선정 여부는 확인되지 않았어요 (마포구·정비몽땅 확인 필요)")
    a.image(I + "site-17-nogosan19-aerial-school.jpg", "창천초등학교 뒤 노고산 언덕 — 19-1 일대 저층 주택가 (직접 촬영 2026.11)")
    a.image(I + "site-18-nogosan19-aerial-wide.jpg", "언덕을 따라 빌라·단독주택이 빽빽한 모습 (직접 촬영)")
    a.image(I + "site-15-nogosan19-banner.jpg", "골목의 '노고산동 신속 민간재개발 추진위원회' 현수막 (직접 촬영 · 연락처 가림)")
    a.text("✔ 골목엔 추진위원회 현수막이 걸려 있어요. 다만 이곳은 **후보지도 아닌 단계**예요. 위 두 곳(철거 완료·철거 중)과 같은 속도로 보시면 안 돼요")

    a.head(6, "왜 하필 신촌일까 — 입지 3가지")
    a.text("노고산동에 40층대가 연달아 올라오는 건 규제 완화 때문만은 아니에요.", "**입지 자체가 받쳐주는 동네**라서예요.")
    a.table(["", "신촌 입지"],
            [["① 대학가", "**연세대·이화여대·서강대**가 걸어서 닿는 거리 (홍익대도 한 정거장) — 학생·교직원·유학생 수요가 **매년 새로** 들어와요"],
             ["② 여의도", "신촌로터리에서 **서강대교만 건너면 여의도** — 업무지구 출퇴근이 가까워요"],
             ["③ 강남", "신촌역 **2호선 한 번**에 강남역까지 (환승 없음) · 경의중앙선(신촌·서강대역) · 공항철도 홍대입구 한 정거장"]],
            note="역·노선 기준 · 실제 이동 시간은 시간대·교통 상황에 따라 달라요")
    a.image(I + "site-12-sinchon-rotary-sign.jpg", "신촌로터리 표지판 — 서강대교(여의도)·서강대·연세대가 한 교차로에 (직접 촬영 2026.11)")
    a.text("✔ 대학가 수요는 원룸·오피스텔을, 여의도·강남 접근성은 **직장인 실거주 수요**를 받쳐줘요. 노고산동 새 단지가 업무 → **주거**로 방향을 바꾼 것도 이 흐름과 맞닿아 있어요")

    a.head(7, "착한언니 체크 — 노고산동을 보신다면")
    a.numbered("매수를 생각한다면", "내 땅·건물이 **몇 지구**인지부터 확인해요 (같은 구역이라도 지구마다 단계가 달라요)",
               "관리처분인가가 난 지구는 **조합원 지위 양도 제한**과 **현금청산** 여부를 꼭 확인해요")
    a.numbered("근처 원룸·오피스텔에 사신다면", "노고산동 오피스텔 원룸은 최근 1년 실거래 기준 **보증금 1,000만 원·월세 80만 원**대가 가장 많아요",
               "공사가 시작되면 소음·통행 불편이 생겨요 — 계약 전 공사장과 거리를 직접 걸어서 확인해요")
    a.numbered("'심의 통과'는 '착공'이 아니에요", "정비계획 변경 고시 → 사업시행계획(변경)인가 → 관리처분(변경) → 이주·철거 → 착공 순서예요",
               "지금 5·6·7·10지구는 **철거 완료**, 3지구는 **철거 중**, 건너편 2-2지구는 **착공** — 같은 신촌인데 단계가 다 달라요")

    a.head(8, "정리하면")
    a.text("✔ 노고산동 재개발은 **지구 단위**라 속도가 제각각이에요",
           "✔ **마포4구역 5·6·7·10지구**: 4개 지구 통합, 지상 49층·497세대 (**9.23 정비계획 변경 고시**, 현장은 철거 끝난 빈 땅)",
           "✔ **마포3구역 3지구**: 지상 42층·298세대, 외국인주민센터 (8.6 통합심의 조건부 의결, **철거 중 ~2027.1**)",
           "✔ **19-1 일대**: 신통 후보지 미선정 후 재도전 중 (추진위 활동)",
           "==자이엘라 사무소 바로 앞 동네라, 단계가 바뀔 때마다 도면과 함께 업데이트할게요.==")
    a.note('11월에 노고산동 세 곳을 직접 걸어 봤어요. 4-10지구는 철거가 끝나 빈 땅이 됐고, 3지구는 가림막 안에서 철거가 한창이에요.', "같은 노고산동인데도 한쪽은 빈 땅, 한쪽은 철거 중, 언덕 위 19-1은 현수막만 걸린 단계라 '노고산동 재개발'을 한 덩어리로 보시면 안 돼요.")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 바로 옆 아현1구역 이야기도 함께 보세요.",
            "도면 출처: 마포구의회 의견청취안(마포구청 제출, 2025.11·2026.2), 마포구 구역공개(2025.1) · 수치는 정비계획(안)·심의 단계 기준이라 최종 고시와 다를 수 있어요 · 이 글은 투자 권유가 아니에요")
    a.signature("zaiella")
    side = ["**제목(BEST)**: 노고산동 재개발 2026｜신촌역 49층·42층 두 곳 통과, 19-1은? (정비계획 도면 정리)",
            "**제목(대안)**: 신촌 노고산동 재개발 지금 어디까지｜마포4구역 5·6·7·10지구·마포3구역 3지구 도면으로 보기",
            "**태그**: 노고산동재개발, 노고산동, 신촌재개발, 마포4구역, 마포3구역3지구, 신촌역, 서강대역, 도시정비형재개발, 마포재개발, 착한언니복덕방",
            "**썸네일**: 「신촌 노고산동 49층·42층」 / 「도면으로 보는 재개발」 / 「19-1은 아직」",
            "**도면 6장 배치 완료**: 마포구의회 의견청취안(구청 제출 공문)·구역공개 공고 도면 — 출처 캡션 표기 · 투시도는 설계 저작물일 수 있어 제외",
            "**현장 사진 13장 반영 (11/21 촬영)**: 2-2지구·4-10지구·3지구·19-1 — 얼굴·번호판·연락처·번지판 블러 · 2-2지구 투시도 패널은 제외(허가표지판만)",
            "**사진 (촬영 남음)**: 15지구 완공 건물, 자이엘라 사무소 앞",
            "**확인 완료**: 5·6·7·10지구 정비계획 변경 결정 고시 2026.9.23 (서울특별시고시 제2026-543호) · **⚠️ 발행 전**: 3-3지구 서울시 고시 제2026-268호 원문, 19-1 2026년 진행"]
    return a, side


def sinchon22_officetel():
    a = Post("2026-11-sinchon2-2-officetel", "에르노 플레이스 신촌 분양 정리 (신촌 2-2지구 오피스텔)",
             "출처: 현장 건축허가표지판(서대문구청)·사업 안내판 (2026.11 직접 촬영) · 분양가는 분양 측 안내 가격표(2026.11) · 일정은 입주자모집공고(2026.4.22)·서울신문(2026.11.10)·서울경제TV(2026.11.17) 보도 · 작성 규칙 MASTER v1.2")
    I = "img/nogosan/"
    a.text("{{신촌역 앞 원룸 한 칸, 5억이 넘는다면 비싼 걸까요?}}")
    a.text("답은 **\"어떤 평수로 계산하느냐에 따라 다르다\"**예요.", "같은 집도 평당가가 두 배 넘게 달라 보이거든요.")
    a.text("신촌로터리 현대백화점 옆,", "빨간 크레인이 올라간 **에르노 플레이스 신촌** 이야기예요.")
    a.text("분양 광고 말고,", "**현장 허가표지판과 전용면적 기준 가격**을 보면서", "하나씩 짚어 볼게요.")
    a.blank(); a.greet(); a.blank()
    a.quote("**한 줄 요약** 에르노 플레이스 신촌 · 창천동 18-42 · 22층 오피스텔 · 전용 6.7평 5억 4,800만~ · 2028.6 공사 완료 예정 · 판단은 **전용 평당가**로", "기본")
    a.text("※ 분양가·조건은 분양 측 안내(2026.11) 기준이라 바뀔 수 있어요.", "투자 권유가 아니라 정보 정리예요.", size=14, color="#888888")

    a.head(1, "어디에, 뭘 짓나요?")
    a.image(I + "site-11-sinchon2-2-gate.jpg", "신촌 2-2지구 현장 — 신촌로터리 대로변, 크레인이 올라간 상태 (직접 촬영 2026.11)")
    a.table(["항목", "내용"],
            [["위치", "서울 서대문구 **창천동 18-42** 일원 (신촌로터리·현대백화점 유플렉스 옆)"], ["용도지역", "일반상업지역 · 지구단위계획(신촌지구)"],
             ["규모", "**지하 5층 ~ 지상 22층** · 철근콘크리트"], ["용도", "업무시설(**오피스텔**) · 근린생활시설"],
             ["대지 / 연면적", "1,556.90㎡ / 17,850.22㎡"], ["건폐율 / 용적률", "56.59% / **834.81%**"],
             ["실수", "오피스텔 **144실** (복층 130실 · 단층 14실) · 전용 약 22~51㎡"],
             ["공사기간", "**2026.1.20 ~ 2028.6.30** (입주 예정 2028.10)"], ["시행 · 시공", "원경개발(위탁)·코리아신탁(수탁) · **(주)대명건설**"]],
            note="현장 건축허가표지판(서대문구청) · 언론 보도(2026.11) 기준")
    a.image(I + "site-13-sinchon2-2-permit.jpg", "건축허가표지판 (직접 촬영)")
    a.image(I + "site-14-sinchon2-2-fence.jpg", "연세로2길 쪽 가림막 (직접 촬영)")
    a.text("✔ 재개발이라고 해서 아파트 단지가 아니에요. 신촌지역 도시정비형 재개발은 **지구 단위로 건물 한 동씩** 짓는 방식이라, 여기는 오피스텔 한 동이에요",
           "✔ 길 건너 노고산동(마포구)은 이제 철거 단계인데, 여기는 **이미 올라가는 중**이에요")

    a.head(2, "분양 조건 (분양 직원 안내 기준)")
    a.table(["일정", "내용"],
            [["2024.12~2025.2", "미주(LA) 한인 대상 우선 분양 홍보 (보도)"], ["**2026.4.22**", "입주자모집공고 → 4.27 청약 · 4.30 발표 · 5.1 계약"],
             ["**2026.11 현재**", "**분양 진행 중** (11월 언론 보도 다수)"], ["2028.10", "입주 예정"]],
            note="청약 정보 사이트·언론 보도 기준 · 최신 잔여 호실과 조건은 분양사무실 확인")
    a.text("4월 청약 뒤에도 **분양이 계속 이어지는 중**이에요.", "이럴 땐 처음 공고 때와 **계약 조건(계약금·중도금·혜택)이 달라졌는지**", "꼭 물어보세요.")
    a.text("단지명은 **에르노 플레이스 신촌**이에요.", "분양 측에서 받은 가격표를 **전용면적 기준**으로 다시 정리했어요.")
    a.table(["타입 (안내 예시 호실)", "전용", "분양가 (부가세 포함)", "**전용 평당가**"],
            [["22A · 13호 서북향 (10~14층)", "6.7평", "5억 4,823만", "약 **8,180만**"],
             ["23D · 12호 서북향 (10~14층)", "7.1평", "5억 7,548만", "약 **8,110만**"],
             ["24A · 4·5·6호 동향", "7.3평", "6억 8,584만 ~ 7억 553만", "약 **9,400만 ~ 9,660만**"],
             ["37A · 1호 동향", "11.5평", "10억 7,308만 ~ 11억 4,855만", "약 **9,330만 ~ 9,990만**"],
             ["47A · 11호 남향", "14.4평", "13억 9,596만 ~ 15억 1,412만", "약 **9,690만 ~ 1억 510만**"]],
            note="분양 측 안내 가격표 기준 (2026.11 · 바뀔 수 있음) · 전용 평당가 = 분양가 ÷ 전용평 (착한언니 계산) · 같은 타입도 층·향마다 가격이 달라요")
    a.text("[[원룸 한 칸에 5억 중반부터]]")
    a.text("✔ 분양가에는 **건물분 부가세**가 들어 있어요 (22A 약 2,811만 원). 일반임대사업자로 등록하면 돌려받을 수 있는 구조라, 계약 전에 세무 상담을 꼭 받아 보세요",
           "✔ 공사 완료 예정이 2028년 6월이라, **입주는 그 이후**예요. 지금 계약하면 약 1년 반~2년을 기다리는 구조예요")

    a.head(3, "숫자 볼 때 속지 말아야 할 3가지")
    a.text("오피스텔 분양 자료에는 **평수가 여러 개** 나와요.", "어떤 숫자로 보느냐에 따라 평당가가 **두 배 넘게** 달라져요.")
    a.table(["자료에 나오는 숫자", "뭐가 들어간 거예요?", "착한언니 기준"],
            [["**전용면적**", "실제 내 방 (벽 안쪽)", "✅ **비교는 이걸로**"],
             ["계약면적 '평형'", "전용 + 복도·주차장·기계실 등 공용", "전용의 **2배 넘게** 커 보여요 → 평당가는 **절반**처럼 들려요"],
             ["'실사용' 평수", "전용 + 발코니 + 다락", "발코니·다락은 **서비스면적** — 분양가에도, 전용에도 안 들어가요"]])
    a.text("✔ 다락은 높이 제한(1.5m 이하)이 있어서 **방이 아니에요**. 오피스텔 발코니는 **실내로 확장할 수 없고요**",
           "✔ 그래서 \"평당 4천만 원대\"라는 말을 들으면 **계약평 기준인지, 전용평 기준인지** 꼭 물어보세요")

    a.head(4, "임대 수익, 직접 계산해 보세요")
    a.text("분양 상담에서 **\"수익률 높은 타입\"**이라는 말을 들으셨다면,", "아래처럼 **직접** 계산해 보세요.")
    a.table(["예시: 22A", "계산"],
            [["분양가", "5억 4,823만"], ["가정: 보증금 1,000만 · 월세 90만", "1년 월세 1,080만"],
             ["실투자금 (분양가 − 보증금)", "5억 3,823만"], ["**연 수익률 (세전·대출 없음)**", "**약 2.0%**"]],
            note="월세는 계산 예시를 위한 가정이에요 (실제 신촌 신축 원룸 시세는 계약 전 직접 확인) · 취득세 4.6%·중개보수·관리비·공실·대출이자 미반영 → 실제 수익률은 더 낮아질 수 있어요")
    a.text("요즘 예금 금리와 **꼭 나란히 놓고** 비교해 보세요.", "신촌이라 공실 걱정은 덜하지만,", "**분양가가 수익률을 정하는** 상품이에요.")

    a.head(5, "신촌 입지, 세 가지만 기억하세요")
    a.table(["", "신촌 입지"],
            [["① 대학가", "**연세대·이화여대·서강대**가 걸어서 닿는 거리 (홍익대도 한 정거장) — 학생·교직원·유학생 수요가 **매년 새로** 들어와요"],
             ["② 여의도", "신촌로터리에서 **서강대교만 건너면 여의도** — 업무지구 직장인 수요"],
             ["③ 강남", "신촌역 **2호선 한 번**에 강남역까지 (환승 없음) · 경의중앙선 신촌역 · 공항철도 홍대입구 한 정거장"]],
            note="역·노선 기준 · 실제 이동 시간은 시간대·교통 상황에 따라 달라요")
    a.image(I + "site-12-sinchon-rotary-sign.jpg", "신촌로터리 — 서강대교(여의도)·서강대·연세대 방향이 한 교차로에 (직접 촬영)")
    a.text("오피스텔은 결국 **누가 살러 오느냐**가 제일 중요한데,", "신촌은 학생 수요에 **여의도·강남 직장인 수요**까지 겹쳐요.", "이건 신촌의 오래된 장점이에요.")

    a.head(6, "착한언니 체크 — 계약 전에 꼭 보세요")
    a.numbered("분양가가 적정한지", "주변 **신축 오피스텔 실거래가·월세**와 **전용 평당가**로 비교해 보세요",
               "**전용률**은 '전용 ÷ 계약면적'으로 계산했는지 확인해요 — 발코니·다락을 넣어 계산하면 실제보다 높게 나와요",
               "**호실별 가격표**를 받아서 층·향별 차이를 보세요")
    a.numbered("세금·대출", "오피스텔 취득세는 **4.6%**(지방교육세·농특세 포함)로 아파트와 달라요",
               "주거용으로 쓰면 **주택 수에 들어갈 수 있어서** 다른 집 세금에 영향이 있어요 — 계약 전 세무 상담 권해요",
               "중도금·잔금 대출 조건과 **DSR**을 미리 확인해요")
    a.numbered("임대를 생각하신다면", "2028년 입주 시점에 **주변 공급**(노고산동 3지구·4-10지구 등)이 어떻게 겹치는지도 같이 보세요",
               "관리비·주차 대수·근생(상가) 구성도 세입자 만족도에 영향이 커요")

    a.head(7, "정리하면")
    a.text("✔ **에르노 플레이스 신촌 (2-2지구)**: 창천동 18-42, 22층 오피스텔 144실, 2026.4 청약 후 **지금도 분양 중**, 2028.10 입주 예정 (시공 대명건설)",
           "✔ 분양가는 전용 6.7평 **5억 4,823만**부터, 전용 평당 **약 8,100만~1억 500만** (안내 가격표 기준)",
           "✔ 입지는 **대학가 + 여의도 + 2호선 강남**, 신촌에서 검증된 조합이에요",
           "✔ 판단은 **전용 평당가 vs 주변 신축 시세**, 그리고 **직접 계산한 수익률**로",
           "==신촌 오피스텔 매매·임대 상담은 자이엘라점에서 도와드려요.==")
    a.note('얼마 전 분양 직원분이 저희 사무소에 직접 다녀가셨어요. 그만큼 분양이 계속 진행 중이에요.', "상담하면서 제일 먼저 확인하는 건 '전용면적 기준 가격'이에요. 실사용·계약 평수로 들으면 같은 집도 훨씬 싸게 느껴지거든요.")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 길 건너 노고산동 재개발 이야기는 「신촌 노고산동 재개발 2026」에서 보세요.",
            "출처: 현장 건축허가표지판(서대문구청, 2026.11 촬영) · 분양가는 분양 측 안내 가격표(2026.11) · 일정은 모집공고(2026.4.22)·언론 보도 · 투시도·조감도는 설계 저작물이라 싣지 않았어요 · 이 글은 투자 권유가 아니에요")
    a.signature("zaiella")
    side = ["**제목(BEST)**: 에르노 플레이스 신촌 분양가 정리｜원룸 5억 4천부터, 전용 평당가로 다시 계산해 봤어요",
            "**제목(대안)**: 에르노플레이스 신촌 분양 2026｜신촌로터리 22층 오피스텔, 계약 전 체크 3가지",
            "**태그**: 에르노플레이스신촌, 에르노플레이스, 신촌오피스텔분양, 신촌오피스텔, 신촌2-2지구, 창천동오피스텔, 신촌신축오피스텔, 착한언니복덕방",
            "**숫자 출처**: 분양가는 고객용 가격표 사진 기준 · 대외비 표시가 있는 영업 교육자료(면적표·CG·배치도)는 사용하지 않음 — 공식 분양 공고 나오면 면적·실수 추가",
            "**수익률 예시**: 월세 90만은 가정값 — 실제 신촌 신축 원룸 월세 확인 후 바꾸거나, 분양 측과의 관계상 부담되면 4번 섹션 빼도 돼요",
            "**사진 4장**: 현장 크레인·허가표지판·가림막·신촌로터리 표지판 — 번호판·얼굴 블러, 투시도 패널·분양 팸플릿 표지는 제외",
            "**톤**: 분양 광고처럼 보이지 않게 — 장점(입지)과 체크포인트(분양가·세금·공급)를 같이"]
    return a, side


def daeheung():
    a = Post("2026-11-daeheung-apt", "대흥동 아파트 시세 2026",
             "출처: 국토교통부 아파트 매매·전월세 실거래가(마포구, 2025.11~2026.10 신고분, 해제 거래 제외) · 서울 청약 면적별 비중(우리은행 부동산리서치랩, 한국부동산원 청약홈 분석, 2026.11.22 보도) · KB부동산 면적별 상승률(2026.1~10, 보도) · 작성 규칙 MASTER v1.2")
    a.text("{{대흥동에 15억대로 들어갈 수 있을까요?}}")
    a.text("답은 **\"있다\"**예요.", "다만 고를 수 있는 단지가 딱 정해져 있어요.")
    a.text("2호선 이대역부터 6호선 대흥역까지,", "저희 **마포그랑자이점**이 있는 동네예요.")
    a.text("호가 말고,", "**지난 1년 동안의 실거래가**를 보면서", "하나씩 짚어 볼게요.")
    a.blank(); a.greet(); a.blank()
    a.quote("**한 줄 요약** 대흥동 84㎡는 마포태영 21억 · 마포그랑자이 25억 · 마포자이2차 26억 (1년 실거래 중위) · 거래가 제일 많은 곳은 마포태영", "기본")

    a.head(1, "대흥동은 어떤 동네예요?")
    a.text("공덕동이 **업무지구** 느낌이라면,", "대흥동은 **주거지** 느낌이 강해요.")
    a.table(["", "대흥동"],
            [["교통", "**6호선 대흥역** · 2호선 이대역 · 걸어서 공덕역(5·6호선·경의중앙선·공항철도)"],
             ["학교·학원", "서강대가 동네 한가운데 · **대흥역~공덕역 대로변 학원가**"],
             ["생활", "경의선숲길 · 공덕·신촌 상권 사이"],
             ["아파트", "대단지 몇 곳에 거래가 모여요 — 단지 수가 많지 않아요"]])
    a.text("요즘 대흥역 일대를 **'마포 학원가'**라고 부르는 분들이 많아요.", "주변 신축 대단지 학부모 수요가 학원을 불러온 거죠.")

    a.head(2, "단지별 실거래, 한 장으로")
    a.table(["단지 (국토부 등록명)", "준공", "59㎡ 중위", "84㎡ 중위", "1년 거래"],
            [["마포그랑자이", "2020", "**21억 8,500만**", "**25억 3,250만**", "16건"],
             ["마포자이2차", "2014", "-", "**26억**", "4건"],
             ["**마포태영** (대흥동태영)", "1999", "**16억 8,000만**", "**20억 9,800만**", "[[44건]]"],
             ["대흥동세양", "2000", "-", "15억 5,500만", "2건"]],
            note="국토부 실거래 2025.11~2026.10 신고분 · 해제 거래 제외 · 59㎡=전용 57~61㎡, 84㎡=80~86㎡ · 최근 1~2개월은 신고가 더 늘 수 있어요")
    a.text("✔ **마포그랑자이**: 2020년 준공, 대흥동에서 가장 새 아파트예요. 분양 때 이름은 **'신촌그랑자이'**였는데 지금은 마포그랑자이로 바뀌었어요. 59㎡도 21억대예요",
           "✔ **마포자이2차**: 대흥역 가까운 2014년식. 거래는 적지만 84㎡ 3건이 모두 **26억**이었어요",
           "✔ **마포태영**: 1999년식이지만 **거래가 1년 44건**으로 대흥동에서 압도적이에요. 그만큼 사고파는 사람이 많다는 뜻이에요. 한때 리모델링 이야기가 나왔지만, **실제로 진행된 건 없어요**",
           "✔ **대흥동세양**: 공덕역·대흥역 사이. 84㎡가 15~16억대로 대흥동에서 진입 가격이 가장 낮아요")
    a.image("img/daeheung/05-taeyoung-sign.jpg", "마포태영아파트 입구 (독막로 266) — 직접 촬영 2026.11")
    a.image("img/daeheung/01-taeyoung-towers.jpg", "마포태영 단지 안 — 대단지라 동·층에 따라 시세 차이가 커요 (직접 촬영)")
    a.image("img/daeheung/03-taeyoung-playground.jpg", "단지 안 놀이터 (직접 촬영)")
    a.image("img/daeheung/06-academy-street.jpg", "마포태영 앞 상가 — 어학원·수학학원이 모여 있어요 (직접 촬영)")
    a.image("img/daeheung/08-daeheung-sign.jpg", "마포세무서 앞 — 대흥역·공덕오거리·신석초교 갈림길 (직접 촬영)")
    a.photo("마포그랑자이·마포자이2차 단지 외관 (각 1장)")

    a.head(3, "1년 동안 어떻게 움직였나 — 마포태영")
    a.text("거래가 많은 마포태영으로 흐름을 보면,", "숫자가 제일 믿을 만해요.")
    a.table(["마포태영", "25.11~26.4", "26.5~26.10", "변화"],
            [["59㎡ 중위", "16억 4,250만 (6건)", "**16억 9,000만** (11건)", "+4,750만"],
             ["84㎡ 중위", "20억 4,500만 (12건)", "**21억** (9건)", "+5,500만"],
             ["84㎡ 최고", "", "**22억 3,000만** (2026.9)", ""]],
            note="국토부 실거래 · 반기별 중위값 (착한언니 계산) · 층·향·동에 따라 차이가 커요")
    a.text("✔ 오르긴 올랐지만 **반년에 5천만 원 안팎**이에요. 급하게 뛴 게 아니라 꾸준히 따라 올라온 흐름이에요",
           "✔ 반면 마포그랑자이 59㎡는 상반기 22억 6,500만 → 하반기 21억 1,000만으로 **중위값이 낮아졌어요** (거래 각 6건, 표본이 적어 층·동 영향이 커요)")

    a.head(4, "요즘 59㎡가 강한 이유")
    a.text("최근 기사에서 눈에 띄는 숫자가 있었어요.")
    a.table(["", "숫자"],
            [["서울 아파트 청약 신청 중 **60㎡ 이하** 비중", "**79.81%** (2026.1~9)"],
             ["서울 60㎡ 이하 아파트값 상승률", "**13.96%** — 면적대 중 1위 (2026.1~10)"]],
            note="우리은행 부동산리서치랩(청약홈 분석)·KB부동산, 2026.11.22 보도")
    a.text("대흥동도 그래요.", "마포태영 59㎡는 84㎡ 가격의 **약 80%**,", "마포그랑자이 59㎡는 **약 86%**예요.")
    a.text("대출 한도는 묶여 있고, 분양가와 세금은 오르니까", "**\"84 대신 59\"**를 고르는 분들이 많아진 거예요.", "저희 사무소에서도 실제로 그렇게 느껴요.")

    a.head(5, "전세는 어느 정도예요?")
    a.table(["단지", "59㎡ 전세 중위", "84㎡ 전세 중위"],
            [["마포그랑자이", "8억 6,000만 (82건)", "10억 5,000만 (91건)"],
             ["마포자이2차", "-", "10억 9,000만 (23건)"],
             ["마포태영", "6억 3,000만 (53건)", "8억 5,000만 (34건)"]],
            note="국토부 전월세 실거래 중 월세 0원 거래 · 신규·갱신 계약 모두 포함이라 새로 구할 때 시세보다 낮게 보일 수 있어요")
    a.text("✔ 매매가 대비 전세는 **40% 안팎**이에요. 갭이 커서, 대흥동은 **실거주로 들어오는 분**이 대부분이에요")

    a.head(6, "착한언니 체크 — 대흥동을 보신다면")
    a.numbered("예산별로 보면", "**15~17억**: 마포태영 59㎡ · 대흥동세양 84㎡", "**20~22억**: 마포태영 84㎡ · 마포그랑자이 59㎡", "**25억 이상**: 마포그랑자이·마포자이2차 84㎡")
    a.numbered("같은 단지도 꼭 비교하세요", "마포태영은 대단지라 **동·층·향**에 따라 1억 넘게 차이 나요", "실거래 최고가만 보지 말고 **최근 3건**을 같이 보세요")
    a.numbered("대출 구간 확인", "수도권 주담대 한도는 시가 **15억 이하 6억 · 15~25억 4억 · 25억 초과 2억**이에요 — 대흥동은 단지마다 구간이 갈려요")
    a.text("가격 전망은 단정하지 않을게요.", "다만 **거래가 꾸준한 단지**는", "사고팔 때 시세를 판단하기가 훨씬 쉬워요.")

    a.head(7, "정리하면")
    a.text("✔ 대흥동 84㎡ 1년 실거래 중위: **마포태영 21억 · 마포그랑자이 25억 · 마포자이2차 26억 · 세양 15.5억**",
           "✔ 거래는 **마포태영**에 몰려 있어요 (1년 44건)",
           "✔ 59㎡ 선호가 뚜렷해요 — 84㎡의 80~86% 가격",
           "==마포그랑자이점이 바로 이 동네에 있어요. 단지별 동·층 비교가 필요하시면 편하게 물어보세요.==")
    a.note('마포그랑자이점이 바로 이 동네에 있어서, 요즘 마포태영·공덕 쪽 계약을 연달아 진행했어요.', '상담에서 체감하는 것도 숫자와 같아요. "84 대신 59"를 먼저 물어보시는 분이 확실히 늘었어요.')
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 다음 글은 마포태영·공덕삼성 실제 계약 후기예요.",
            "출처: 국토교통부 실거래가 공개시스템(2025.11~2026.10 신고분) · 청약 면적 비중·면적별 상승률은 2026.11.22 언론 보도 인용 · 가격 전망이 아닌 실거래 정리이며 투자 권유가 아니에요")
    a.signature("grandxi")
    side = ["**제목(BEST)**: 대흥동 아파트 시세 2026｜마포그랑자이·마포자이2차·마포태영 실거래로 비교 (59㎡가 강한 이유)",
            "**제목(대안)**: 마포 대흥동 아파트 어디가 좋을까｜84㎡ 15억~26억, 예산별로 정리했어요",
            "**태그**: 대흥동아파트, 대흥동시세, 마포그랑자이, 신촌그랑자이, 마포자이2차, 마포태영, 대흥태영, 대흥태영리모델링, 대흥역, 마포아파트, 착한언니복덕방",
            "**확인 완료**: 신촌그랑자이 → 마포그랑자이 개명 (본문 반영, 옛 이름 검색 유입용으로 태그에도 넣음) · 마포태영 리모델링 진행 없음 (본문 한 줄)",
            "**⚠️ 확인해 주세요**: 단지별 역 거리 표현(대흥역·이대역) · 동양엔파트는 1년간 실거래가 없어 표에서 뺐어요",
            "**참고 글 처리**: 붙여 주신 다른 블로그 글은 구성만 참고 — 문장·표·지도는 쓰지 않았어요",
            "**다음 글 연결**: 계약 후기(마포태영·공덕삼성) 올리면 6번 섹션 아래에 링크"]
    return a, side


def gyeonghuigung_epit():
    a = Post("2026-11-gyeonghuigung-epit", "경희궁 에피트 청약 총정리",
             "출처: 경희궁 에피트 입주자모집공고(2026.11.13) 원문 · 경희궁자이 시세는 언론 보도(2026.11) · 현장 촬영 · 작성 규칙 MASTER v1.2")
    a.text("{{시세보다 2억 싼 25억짜리 새 아파트, 당첨되면 무조건 이득일까요?}}")
    a.text("답은 **\"현금이 버텨줄 때만\"**이에요.", "당첨 직후부터 분양가의 30%를", "내 돈으로 내야 하거든요.")
    a.text("서대문역 바로 옆 돈의문2구역,", "**경희궁 에피트**가 **11월 25일 특별공급**부터 청약을 시작해요.")
    a.text("분양 홍보 말고,", "**입주자모집공고 원문**을 보면서", "하나씩 짚어 볼게요.")
    a.blank(); a.greet(); a.blank()
    a.quote("**한 줄 요약** 84㎡ 23억 5천~25억 7천 · 옆 경희궁자이보다 약 2억 낮게 · 중도금 20%는 자납 · 84㎡는 토지거래허가 대상 · 재당첨 10년", "기본")
    a.text("※ 입주자모집공고(2026.11.13) 원문을 직접 읽고 정리했어요. 청약 전에 공고문을 꼭 한 번 더 확인하세요.", "투자 권유가 아니라 정보 정리예요.", size=14, color="#888888")

    a.head(1, "어디에, 뭘 짓나요?")
    a.photo("돈의문2구역 공사 현장 (서대문역 쪽에서, 출근길)")
    a.table(["항목", "내용"],
            [["위치", "종로구 **교남동** (돈의문 재개발 **2구역**)"],
             ["규모", "지하 6층 ~ 지상 21층 · **3개 동 · 228세대**"],
             ["228세대 구성", "일반분양 **134** · 임대 78 · 토지등소유자 10 · 보류지 5 · 기타 1"],
             ["일반분양", "**134세대** = 특별공급 72 + 일반공급 62"],
             ["시공 · 시행", "HL디앤아이한라 · 한국투자부동산신탁(수탁)"], ["입주 예정", "**2030년 8월**"]],
            note="입주자모집공고 기준 (일부 기사의 '2개 동'은 공고상 3개 동)")
    a.text("돈의문 재개발은 세 구역이에요.", "1구역이 **경희궁자이**, 3구역이 **NH농협타워**,", "그리고 마지막 남은 2구역이 바로 여기예요.")
    a.table(["타입", "분양 (특공 / 일반)", "분양가 (층·동별)", "대지지분"],
            [["39㎡", "5 (0 / **5**)", "11억 5,852만 ~ 11억 8,241만", "7.09㎡"],
             ["59㎡", "31 (18 / **13**)", "**18억 1,214만 ~ 18억 9,843만**", "10.65㎡"],
             ["84㎡A", "53 (28 / **25**)", "23억 7,866만 ~ **25억 7,484만**", "15.08㎡"],
             ["84㎡B", "45 (26 / **19**)", "23억 4,635만 ~ 25억 1,744만", "15.09㎡"]],
            note="입주자모집공고 공급금액표 · 분양가상한제 미적용 · 발코니 확장비 별도 (39㎡ 1,500만 · 59㎡ 2,500만 · 84㎡ 3,500만) · 견본주택은 확장형")

    a.head(2, "평면, 이렇게 생겼어요")
    a.text("공식 홈페이지 평면도와 공고문 옵션표를 같이 보고", "타입별로 **한 줄씩** 정리했어요.")
    a.table(["타입", "구조", "눈에 띄는 점"],
            [["39㎡", "방 1 + 거실 · 욕실 1", "거실이 넓은 **1LDK** · 옵션(330만)으로 **알파룸 분리** → 1.5룸처럼"],
             ["59㎡", "방 3 · 욕실 2", "건물이 사선이라 **비정형 평면** — 현관·욕실 쪽 모서리 공간이 있어 가구 배치 확인 필요"],
             ["84㎡A", "방 3 · 욕실 2 · 드레스룸", "침실1·거실·침실2가 **앞쪽에 나란히** · 오픈발코니 · 옵션(350만)으로 **침실3 대신 주방 팬트리+식탁 공간**"],
             ["84㎡B", "방 3 · 욕실 2 · 드레스룸 · **팬트리**", "현관이 사선 모서리 · 침실2·3과 거실이 **반대편에 떨어진** 구조 · 오픈발코니"]],
            note="경희궁 에피트 공식 홈페이지 세대안내(확장형 기준) · 입주자모집공고 추가선택품목 · 오픈발코니 위치는 층마다 달라요 · 실제 크기·창 위치는 견본주택에서 확인")
    a.text("✔ **84A vs 84B**: 방 3개를 다 쓸 가족이면 84A 기본형, 수납·식탁 공간이 중요하면 84A 수납특화나 팬트리 있는 84B가 맞아요",
           "✔ **59㎡**는 방 3·욕실 2를 다 넣었지만 사선 구조라, 숫자보다 **실제 모양**을 꼭 보세요",
           "✔ 견본주택은 **발코니 확장형 + 옵션이 섞여** 있어요. 기본형이 어떻게 다른지 꼭 물어보세요")
    a.text("👉 평면도 원본은 공식 홈페이지 「세대안내」에서 타입별로 볼 수 있어요 (brand.hldni.com/gyeonghuigung)", size=14, color="#888888")

    a.head(3, "교통 — 광화문까지 걸어가요")
    a.table(["", "경희궁 에피트"],
            [["지하철", "**5호선 서대문역** · 3호선 독립문역"],
             ["업무지구", "광화문·시청(CBD) 직주근접 — 서대문역에서 광화문역은 한 정거장"],
             ["지하 연결", "서대문역 쪽과 이어지는 **지하연결통로** (공고: 인허가 조건으로 설치 · 유지관리 주체는 아직 미확정이라 **관리비를 입주자가 부담**할 수도 있어요)"],
             ["생활", "강북삼성병원·서울적십자병원 · 영천시장 · 경희궁·서울역사박물관 · 안산·인왕산"]],
            note="입주자모집공고·보도 기준 · 견본주택(은평구 증산동 223-6)은 주차 불가 → 대중교통으로")
    a.text("✔ 마포·서대문에서 광화문으로 출퇴근하는 분들이 가장 부러워하는 자리예요")

    a.head(4, "경희궁자이랑 비교하면")
    a.table(["", "경희궁 에피트", "경희궁자이"],
            [["구역", "돈의문 2구역", "돈의문 1구역"],
             ["입주", "**2030년 8월** (신축)", "2017년"],
             ["규모", "228세대 · **소규모**", "**대단지**"],
             ["84㎡ 가격", "분양가 **23억 5천 ~ 25억 7천**", "실거래 **27억 5천** (2단지, 2026.11 초 보도)"],
             ["강점", "새 아파트 · 분양가가 시세보다 낮음", "대단지 커뮤니티 · 이미 검증된 생활"]],
            note="경희궁자이 가격은 언론 보도 기준 · 동·층·면적에 따라 차이 큼")
    a.text("✔ 84㎡ 기준 **약 2억 차이**예요. 다만 에피트는 2030년까지 **4년을 기다리는 값**이 들어 있어요",
           "✔ 경희궁자이는 바로 들어가 살 수 있고, 에피트는 **새 집 + 낮은 가격 + 시간**을 바꾸는 선택이에요")

    a.head(5, "장점과 아쉬운 점")
    a.table(["👍 장점", "🤔 아쉬운 점"],
            [["4대문 안 신축 — 희소해요", "**현금 부담**이 커요 (아래 자금 일정 참고)"],
             ["광화문·시청 직주근접", "228세대 **소규모** — 커뮤니티·관리비 규모의 한계"],
             ["주변 시세보다 낮은 분양가", "**2030년 입주**까지 4년"],
             ["경희궁자이 생활 인프라 공유", "**84㎡는 토지거래허가 대상** — 나중에 팔 때 허가가 필요해요 (아래 8번)"]])

    a.head(6, "과연 완판될까? 시장의 기대")
    a.text("정답은 12월 4일 발표 때 나오지만,", "착한언니가 보는 포인트는 이래요.")
    a.table(["기대가 큰 이유", "변수"],
            [["시세보다 낮은 분양가 (84㎡ 약 2억)", "당첨 직후부터 **분양가의 30%를 현금**으로"],
             ["4대문 안 마지막 재개발 구역", "에피트는 자이보다 **브랜드 인지도**가 낮은 편"],
             ["서울 청약은 **소형 쏠림** (60㎡ 이하 신청 비중 약 80%, 2026.1~9 보도)", "84㎡는 **현금 여력 있는 수요층**으로 좁혀져요"]])
    a.text("제 생각엔 **39·59㎡는 경쟁이 셀 것** 같고,", "84㎡는 \"현금으로 버틸 수 있느냐\"가", "경쟁률을 가를 것 같아요.")
    a.text("결과 나오면 경쟁률과 함께 다시 정리해 드릴게요.", size=15, color="#888888")

    a.head(7, "청약 공략법")
    a.table(["날짜", "일정"],
            [["11.25 (수)", "**특별공급**"], ["11.26 (목)", "1순위 **해당지역** (서울 2년 이상 거주)"],
             ["11.27 (금)", "1순위 기타지역 (서울 2년 미만·경기·인천)"], ["11.30 (월)", "2순위"],
             ["**12.4 (금)**", "당첨자 발표"], ["12.16 ~ 18", "정당계약"]],
            note="입주자모집공고 기준 · 청약은 한국부동산원 청약홈")
    a.numbered("특별공급 72세대부터 보세요", "신혼부부 20 · 신생아 13 · 다자녀 13 · 기관추천 13 · 생애최초 9 · 노부모부양 4",
               "해당되면 특공과 일반 1순위를 **둘 다** 넣을 수 있어요 (특공에 당첨되면 일반은 무효)")
    a.table(["일반공급", "세대", "가점 : 추첨", "이런 분께"],
            [["39㎡", "5", "40 : 60", "가점 낮은 1~2인 (특공 없이 전부 일반)"],
             ["59㎡", "13", "40 : 60", "가점 낮은 신혼·소가족"],
             ["84㎡A·B", "25 + 19", "**70 : 30**", "가점 높은 분 (가점 싸움)"]],
            note="입주자모집공고 · 추첨 물량의 75%는 무주택세대구성원에게 먼저 · 1주택 이상 세대는 가점제 신청 불가")
    a.numbered("가점이 낮다면 '추첨' 물량을 노리세요", "60㎡ 이하는 **추첨 60%** — 39·59㎡가 현실적이에요",
               "다만 일반공급이 39㎡ 5세대, 59㎡ 13세대뿐이라 **경쟁이 몰릴 수** 있어요")
    a.numbered("자격 체크", "일반 1순위는 **세대주**만 · 청약통장 **24개월** 이상 · 지역·면적별 **예치금** 충족",
               "서울 2년 이상 거주(2024.11.13 이전부터)면 **해당지역**으로 먼저 뽑혀요",
               "같은 날 발표하는 다른 단지와 **중복 신청하면 무효**예요 (특공 1건 + 일반 1건은 가능)")

    a.head(8, "당첨되면 이런 제한이 있어요")
    a.table(["제한", "내용"],
            [["재당첨 제한", "**10년**"],
             ["1순위 제한", "당첨자와 세대원은 **5년간** 투기과열지구·청약과열지역 1순위 청약 불가"],
             ["전매제한", "최초 당첨자 발표일부터 **3년**"],
             ["실거주 의무", "**없음** (분양가상한제 미적용)"],
             ["토지거래허가", "종로구는 토허구역 · **대지지분 15㎡ 초과면 허가 대상** → 84㎡A·B(15.08㎡)는 **나중에 팔 때 허가**가 필요해요"]],
            note="입주자모집공고 원문 기준 · 토허 규정은 정부 정책에 따라 바뀔 수 있어요")
    a.text("✔ 재당첨 10년이 제일 무거워요. **다른 단지 청약 계획**이 있다면 꼭 같이 따져 보세요",
           "✔ 84㎡는 처음 분양받을 땐 허가가 필요 없지만, **되팔 때 사는 사람이 토허 요건**(실거주 등)을 맞춰야 해요. 39·59㎡는 대지지분이 15㎡ 이하라 해당이 없어요")

    a.head(9, "자금 조달 일정 — 언제, 얼마를 내나")
    a.table(["시기", "84㎡A 최고 (25억 7,484만)", "59㎡ 최고 (18억 9,843만)"],
            [["12.16~18 계약", "**5,000만**", "**5,000만**"],
             ["계약 후 15일 안", "2억 748만 → 계약금 합계 **2억 5,748만**", "1억 3,984만 → 합계 **1억 8,984만**"],
             ["중도금 1차 · 2027.5.10", "2억 5,748만", "1억 8,984만"],
             ["중도금 2차 · 2027.12.10", "2억 5,748만", "1억 8,984만"],
             ["중도금 3차 · 2028.7.10", "2억 5,748만", "1억 8,984만"],
             ["중도금 4차 · 2029.4.10", "2억 5,748만", "1억 8,984만"],
             ["중도금 5차 · 2029.9.10", "2억 5,748만", "1억 8,984만"],
             ["중도금 6차 · 2030.2.11", "2억 5,748만", "1억 8,984만"],
             ["**잔금 · 2030.8 입주**", "**7억 7,245만**", "**5억 6,953만**"]],
            note="입주자모집공고 공급금액표 · 중도금은 이자후불제로 분양가의 40%까지 대출 알선, **20%는 직접 납부** (대출기관·금리는 추후 견본주택 안내 · 대출 알선이 안 돼도 계약 해지 사유가 아님) · 발코니 확장비 별도")
    a.text("[[입주 전까지 현금 30%]]")
    a.text("84㎡면 계약금 2억 5천에", "대출 안 되는 중도금 20% 5억 1천,", "합쳐서 **약 7억 7천만 원**이에요.")
    a.text("✔ 입주 때는 **잔금 + 중도금 대출 상환**을 한 번에 해야 해요. 지금 규제라면 시가 25억 초과 주택은 주담대 한도가 **2억**이에요",
           "✔ 2030년 규제는 아무도 몰라요. \"입주 때 전세 놓고 맞추자\"는 계획도 그때 전세가와 규제를 같이 봐야 해요")

    a.head(10, "견본주택 다녀온 후기")
    a.photo("84㎡ 유니트 — 거실·주방 / 안방·수납")
    a.photo("마감재·옵션 안내판, 단지 모형")
    a.fill("견본주택(은평구 증산동, DMC역 인근) 다녀오시면 후기 3~4줄 — 못 가시면 이 섹션 통째로 지우기")

    a.head(11, "착한언니 한 줄 정리")
    a.table(["이런 분이라면", "착한언니 생각"],
            [["현금 30% + 입주 때 자금 계획이 서 있는 분", "**넣어볼 만해요** — 시세보다 낮은 분양가"],
             ["가점 낮은 1~2인 가구", "**39·59㎡ 추첨** 물량을 노려보세요"],
             ["몇 년 안에 다른 청약 계획이 있는 분", "**재당첨 10년**부터 따져보세요"],
             ["지금 바로 살 집이 필요한 분", "경희궁자이 등 **기존 아파트**와 같이 비교해 보세요"]])
    a.text("==서대문·마포 쪽 기존 아파트와 비교 상담이 필요하시면 편하게 물어보세요.==")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 12월 4일 당첨자 발표 후 경쟁률도 정리할게요.",
            "출처: 입주자모집공고(2026.11.13)·언론 보도(2026.11) · 가점·추첨 비율은 주택공급에 관한 규칙(투기과열지구) 기준 · 조감도·투시도는 설계 저작물이라 싣지 않았어요 · 청약 일정·자격은 반드시 공고문으로 확인하세요 · 이 글은 투자 권유가 아니에요")
    a.signature("zaiella")
    side = ["**제목(BEST)**: 경희궁 에피트 청약 총정리｜84㎡ 25억, 당첨되면 현금 얼마? (경희궁자이 비교·공략법)",
            "**제목(대안)**: 경희궁 에피트 분양가·청약 일정｜완판될까? 착한언니가 따져봤어요",
            "**태그**: 경희궁에피트, 경희궁에피트분양가, 경희궁에피트청약, 경희궁에피트청약일정, 경희궁자이, 돈의문2구역, 서대문역신축, 4대문신축, 착한언니복덕방",
            "**발행**: 11.25(수) 아침 — 출근길 현장 사진 넣고 바로 (특별공급 당일)",
            "**공고문 원문 대조 완료 (11/23)**: 3개 동 · 228세대 구성 · 타입별 특공/일반 세대 · 분양가 전 구간 · 대지지분 · 중도금 일정·20% 자납 · 가점/추첨 비율 · 토허(84㎡) · 지하연결통로 관리비",
            "**남은 확인**: 경희궁자이 84㎡ 최신 실거래 (종로구 실거래 조회 — 공공데이터 서버 복구되면)",
            "**사진**: 현장 사진 우선 / 견본주택은 다녀오시면 추가 · 조감도·투시도·팸플릿 표지는 제외 · 얼굴 블러",
            "**평면도**: 공식 홈페이지 평면 이미지는 시행사 저작물이라 본문엔 글·표로 정리하고 링크만 — 넣고 싶으시면 견본주택에서 직접 찍은 유니트·평면 안내판 사진으로",
            "**썸네일 (캔바 은마 틀)**: 노란 「경희궁 에피트 84㎡ 25억」 / 흰 「당첨되면 현금 얼마?」 — 배경 현장 사진",
            "**후속 글**: 12.4 발표 후 경쟁률·가점 커트라인 (검색 2차 피크)"]
    return a, side

def define_yeonhui():
    a = Post("2026-11-define-yeonhui", "드파인 연희 공사 현황 2026",
             "출처: 더팩트·데일리안·아이뉴스24(2026.1.17)·SBS Biz(2026.1.21) 분양 보도 · 정비몽땅 · 현장 촬영 · 작성 규칙 MASTER v1.2")
    a.text("{{역에서 1km, 초등학교까지 걸어서 25분. 그래도 44대 1이었다면?}}")
    a.text("답은 **\"연희동 신축이라서\"**예요.", "서울 서북권에 새 아파트가 그만큼 귀하거든요.")
    a.text("연희동에 9년 만에 들어서는 신축,", "SK에코플랜트의 **드파인 연희**예요.")
    a.text("분양 홍보 말고,", "**청약 결과와 현장**을 보면서", "하나씩 짚어 볼게요.")
    a.blank(); a.greet(); a.blank()
    a.quote("**한 줄 요약** 연희1구역 재개발 · 959세대 · 1순위 평균 44.1대 1 마감 · 2029년 1월 입주 예정 · 전매제한 3년", "기본")

    a.head(1, "어떤 단지예요?")
    a.photo("드파인 연희 공사 현장 — 가림막·타워크레인 (직접 촬영)")
    a.table(["항목", "내용"],
            [["위치", "서대문구 **연희동 533-5** 일대 (연희1구역 재개발)"],
             ["규모", "지하 4층 ~ 지상 29층 · **13개 동 · 959세대**"],
             ["구성", "조합원 485 · 임대 142 · **일반분양 332**"],
             ["시공", "**SK에코플랜트** (브랜드 '드파인' 서울 첫 적용)"], ["입주 예정", "**2029년 1월**"]],
            note="분양 당시 언론 보도(2026.1) 기준 · 입주 일정은 공정에 따라 바뀔 수 있어요")
    a.text("궁동근린공원과 내부순환로 사이에", "길게 늘어선 배치예요.")

    a.head(2, "청약은 어땠나요?")
    a.table(["타입", "일반분양", "분양가"],
            [["59㎡", "172", "11억 2,000만 ~ 12억 4,300만"], ["74㎡", "24", "12억 6,300만 ~ 13억 3,100만"],
             ["75㎡", "23", "12억 9,000만 ~ 13억 7,900만"], ["84㎡", "112", "**13억 9,200만 ~ 15억 6,500만**"],
             ["115㎡", "1", "23억 5,900만 (펜트하우스)"]],
            note="분양 보도 기준 · 보도마다 일부 금액 차이 있음 · 84㎡ 물량 상당수가 저층이라는 보도도 있어요")
    a.table(["", "모집", "신청", "경쟁률"],
            [["특별공급", "181", "6,840명", "평균 37.8 : 1"],
             ["1순위", "151", "6,655명", "**평균 44.1 : 1** (전 타입 마감)"]],
            note="SBS Biz(2026.1.21) · 1순위 최고는 59㎡A 66.2 : 1")
    a.text("✔ 서울 서북권은 신축 공급이 적은 편이라 관심이 몰렸어요",
           "✔ 근처 DMC파크뷰자이 84㎡가 16억 1천에 거래됐다는 보도가 나오면서 \"분양가가 시세보다 낮다\"는 얘기가 많았어요")

    a.head(3, "장점과 아쉬운 점")
    a.table(["👍 장점", "🤔 아쉬운 점"],
            [["연희동 신축 · 서북권 신축 희소", "지하철역이 멀어요 (경의중앙선 **가좌역** 약 1km, 걸어서 15분 안팎)"],
             ["신촌·홍대 상권, 연희동 카페거리 가까움", "배정 초등학교(**연희초**)가 걸어서 25~30분 (셔틀은 미정)"],
             ["홍제천·궁동공원 — 자연환경", "단지 앞 **내부순환로 소음** (방음벽 설치 예정)"],
             ["4베이·남향 위주, 하이엔드 옵션", "**전매제한 3년** — 입주 전 분양권 거래 불가"]],
            note="분양 당시 언론 보도 내용을 정리했어요")

    a.head(4, "지금 공사 현장은")
    a.photo("현장 공사 안내판 (공사기간·시공사가 보이게)")
    a.photo("단지 앞 내부순환로 쪽 / 연희동 골목 쪽")
    a.fill("현장 다녀온 느낌 2~3줄 — 공정(터파기·골조 몇 층), 주변 분위기")

    a.head(5, "착한언니 체크")
    a.numbered("분양권을 사고 싶다면", "**전매제한 3년**이라 지금은 거래가 안 돼요 — 입주 무렵부터 가능해요")
    a.numbered("입주 때 전세를 생각한다면", "959세대가 한꺼번에 입주하니 **입주장 전세 물량**이 몰릴 수 있어요",
               "먼저 입주한 신축들도 입주 직후 몇 달은 전세 가격 폭이 크게 벌어졌어요")
    a.numbered("학교·교통은 직접 걸어보세요", "연희초·가좌역까지 실제 동선을 아이 걸음으로 걸어보는 게 제일 정확해요")

    a.head(6, "정리하면")
    a.text("✔ **드파인 연희**: 연희동 533-5 일대, 13개 동 959세대, SK에코플랜트",
           "✔ 1순위 평균 **44.1 : 1**로 전 타입 마감 · 84㎡ 13억 9천~15억 6천",
           "✔ **2029년 1월 입주 예정** · 전매제한 3년",
           "==신촌·연희 쪽 집 찾으시면 자이엘라점에서 편하게 상담하세요.==")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 공정이 바뀌면 현장 사진으로 다시 보여드릴게요.",
            "출처: 분양 당시 언론 보도(2026.1) · 현장 직접 촬영 · 조감도·투시도는 설계 저작물이라 싣지 않았어요 · 이 글은 투자 권유가 아니에요")
    a.signature("zaiella")
    side = ["**제목(BEST)**: 드파인 연희 공사 현황 2026｜연희1구역 959세대, 2029년 입주 (청약 44대 1 결과·장단점)",
            "**제목(대안)**: 연희동 신축 드파인 연희 지금 어디까지?｜SK에코플랜트 첫 하이엔드 현장 다녀왔어요",
            "**태그**: 드파인연희, 연희1구역, 연희동아파트, 연희동신축, SK에코플랜트, 드파인, 서대문신축, 가좌역아파트, 착한언니복덕방",
            "**사진 필요**: 공사 현장(가림막·크레인) · 공사 안내판 · 내부순환로 쪽 · 연희동 골목 — 사람·번호판 없이",
            "**⚠️ 확인**: 84㎡ 일반분양 물량 해석이 보도마다 달라요(일부 보도는 대부분 조합원 물량이라고) → 본문엔 표 아래 한 줄로만",
            "**입주 예정**: 보도는 2029년 1월, 일부 사이트는 2029년 6월 준공 → 현장 안내판으로 확인"]
    return a, side

def imun_ipark_xi():
    a = Post("2026-11-imun-ipark-xi", "이문아이파크자이 커뮤니티·동선 2026",
             "출처: 단지 커뮤니티시설 이용안내 게시물(2026.11 현장 촬영) · 단지 규모는 단지 정보 사이트·언론 보도 · 국토부 실거래 · 작성 규칙 MASTER v1.2")
    I = "img/imunipx/"
    a.text("{{외대앞역까지 1분. 사진으로 보면 믿으실까요?}}")
    a.text("답은 **\"101·102동이라면 진짜예요\"**예요.", "단지 옆 철길을 따라 난 통로로 나가면", "바로 외대앞역 승강장이 보이거든요.")
    a.text("길 건너 래미안라그란데에 사는 사람으로서", "옆 단지 **이문아이파크자이**를 직접 걸어봤어요.")
    a.text("분양 광고 말고,", "**커뮤니티 안내판과 현장 동선**을 보면서", "하나씩 짚어 볼게요.")
    a.blank(); a.greet(); a.blank()
    a.quote("**한 줄 요약** 4,321세대 · 84㎡ 매매 20억 6천 · 전세 8억대 · 101·102동 외대앞역 1분 · 204·205동 신이문역 5분", "기본")
    a.image(I + "02-towers.jpg", "이문아이파크자이 — 40층 안팎 타워형 동이 빽빽해요 (직접 촬영 2026.11)")

    a.head(1, "어떤 단지예요?")
    a.table(["항목", "내용"],
            [["위치", "동대문구 이문동 (이문3재정비촉진구역)"], ["규모", "최고 41층 · 전체 **4,321세대** (3-1BL 4,169세대)"],
             ["동 수", "1단지 10개 동 · 2단지 9개 동 (3단지 별도)"], ["사용승인", "**2025년 11월 27일** (3-1BL)"],
             ["용적률 · 건폐율", "357% · 26%"], ["주차", "5,531대 (세대당 약 1.28대)"],
             ["난방", "개별난방 (도시가스)"], ["시공", "HDC현대산업개발 · GS건설"],
             ["역", "1호선 **외대앞역** · 신이문역"]],
            note="단지 정보 사이트(호갱노노·당근부동산 등) 공통 표기 기준 · 동 수는 자료마다 차이 · 정비몽땅 단계 '부분준공인가'")
    a.image(I + "01-sign.jpg", "단지 입구 IPARK X1 사인 (직접 촬영)")
    a.image(I + "03-entrance.jpg", "차량 진입로 — 왼쪽은 단지 상가, 병원이 꽉 차 있어요 (직접 촬영)")

    a.head(2, "외대앞역 1분 — 이 통로예요")
    a.image(I + "04-passage.jpg", "철길 옆 방음벽 통로 — 101·102동에서 외대앞역으로 이어져요 (직접 촬영)")
    a.image(I + "05-hufs-station.jpg", "통로에서 내려다보이는 외대앞역 승강장 (직접 촬영)")
    a.table(["동", "가까운 역", "걸어서"],
            [["**101·102동**", "1호선 **외대앞역**", "**1분** (철길 옆 통로)"],
             ["**204·205동**", "1호선 **신이문역**", "**5분**"]],
            note="착한언니가 직접 걸어본 기준 · 다른 동은 위치에 따라 달라요")
    a.text("✔ 단지가 크다 보니 **동마다 가까운 역이 달라요.** 역세권이라는 말만 듣지 말고 동 번호부터 확인하세요",
           "✔ 이 통로는 **지금은 누구나 다녀요.** 입주민 전용 출입문을 11월 말까지 만드는 중이라, 앞으로 통로 이용 방식이 바뀔 수 있어요")
    a.image(I + "06-rail-walk.jpg", "철길을 따라 이어지는 단지 산책로 (직접 촬영)")
    a.text("[[대신 철길 바로 옆이라는 뜻이기도 해요]]")
    a.text("직접 걸어보니 **철도 소음은 확실히 있어요.**", "방음벽이 있어도", "**철로 쪽 동·저층**은 열차 소리를", "꼭 직접 들어보세요.")

    a.head(3, "커뮤니티, 이용료까지 정리했어요")
    a.image(I + "13-community-board.jpg", "커뮤니티시설 이용안내 게시물 (직접 촬영 2026.11)")
    a.table(["시설", "이용 방식", "요금"],
            [["기본이용료", "전 세대 관리비에 부과", "**월 15,000원**"],
             ["카페(폴바셋)", "아메리카노 쿠폰 (1세대 1일 1잔)", "월 2잔 제공"],
             ["헬스장", "세대원 합산, 초과 1회 1,000원", "월 30회 제공"],
             ["사우나", "**금·토·일 운영** · 1일 1인 1회(2시간)", "월 10회 · 초과 1회 4,000원"],
             ["일반 독서실", "추가 요금", "월 30,000원 (1일 5,000원)"],
             ["프라이빗 독서실", "추가 요금", "월 90,000원 (1일 10,000원)"],
             ["골프", "GDR 연습장 1일 1시간 · 스크린골프 18홀", "월 30,000원 · 1인 10,000원"]],
            note="단지 게시물(2026.11) 기준 · 운영 방식은 입주자대표회의 결정에 따라 바뀔 수 있어요")
    a.table(["시설", "평일", "주말"],
            [["헬스장·골프장", "06:00 ~ 22:00", "09:00 ~ 22:00"], ["독서실", "06:00 ~ 02:00", "09:00 ~ 02:00"],
             ["실내 체육관", "09:00 ~ 21:00", "09:00 ~ 21:00"], ["카페", "09:00 ~ 21:00", "09:00 ~ 18:00"],
             ["사우나 (금·토·일)", "09:00 ~ 22:00", "09:00 ~ 22:00"]])
    a.image(I + "14-gym.jpg", "피트니스 — 창밖으로 조경이 보여요 (직접 촬영 · 이용자 얼굴 가림)")
    a.image(I + "16-paul-bassett.jpg", "단지 안 카페 IPARK X1 × PAUL BASSETT (직접 촬영)")
    a.image(I + "15-cafe.jpg", "카페 좌석 (직접 촬영)")
    a.image(I + "17-library.jpg", "독서실 가는 길 (직접 촬영)")
    a.text("✔ 모든 시설은 **안면인식 등록 후** 앱으로 이용해요 (입주민 등록 때 신분증 필요)")

    a.head(4, "단지 안을 걸어보면")
    a.image(I + "09-patio.jpg", "웰컴라운지 파티오 — 단차를 살린 야외 테라스 (직접 촬영)")
    a.image(I + "12-teahouse.jpg", "티하우스와 주민공동시설·어린이집 안내 (직접 촬영)")
    a.image(I + "10-playground.jpg", "놀이터 (직접 촬영)")
    a.image(I + "11-guesthouse.jpg", "게스트하우스 A·B — 손님 오실 때 좋아요 (직접 촬영)")
    a.image(I + "19-elevator.jpg", "단지 안 엘리베이터 — 높낮이 차이를 이어줘요 (직접 촬영)")
    a.image(I + "20-imun1-office.jpg", "단지 바로 옆 이문1동 복합청사 (주민센터·보건지소)")
    a.text("[[상가가 정말 잘 돼 있어요]]")
    a.text("단지 앞 상가에 병원·학원이 꽉 차 있고,", "**맛집도 라그란데 쪽보다 많아요.**", "단지 안에 **오피스텔동**도 따로 있어요.")

    a.head(5, "관리비는 얼마나 나올까")
    a.text("{{84㎡ 한 세대, 10월 관리비 22만 9,750원이에요.}}")
    a.image(I + "21-maintenance-fee.jpg", "이문아이파크자이 1·2단지 관리비 명세서 2026년 10월분 (동·호수 가림)")
    a.table(["항목", "금액"],
            [["일반관리비", "38,930"], ["청소비", "26,770"], ["경비비", "24,810"], ["승강기유지비", "4,490"],
             ["수선유지비 · 소독비 · 건물보험료 · 대표회의·선거관리 운영비", "6,150"],
             ["전기 (338kWh)", "67,550"], ["공동전기 · 승강기전기", "18,100"], ["수도 (21㎥) · 공동수도", "25,030"],
             ["**커뮤니티 기본료**", "**15,000**"], ["TV수신료 · 음식물", "2,920"],
             ["**합계**", "**229,750원**"]],
            note="관리면적 82.16㎡ 한 세대 실제 명세서 (2026년 10월분) · 커뮤니티 이용료 2,500원은 같은 금액 차감 · 세대마다 사용량에 따라 달라요")
    a.table(["월", "관리비"], [["2026년 8월", "336,270원 (에어컨)"], ["9월", "231,780원"], ["10월", "229,750원"]])
    a.text("✔ 여름엔 30만 원대, 냉방이 끝나면 **22~23만 원대**예요. 전기·수도가 절반 가까이 차지해요",
           "✔ 커뮤니티 **기본료 15,000원**이 매달 붙어요 — 안 써도 나가는 돈이에요",
           "✔ 명세서의 **수선유지비 1,800원**은 엘리베이터·공용시설 같은 작은 수리비예요. **장기수선충당금과는 다른 항목**이에요",
           "✔ **장기수선충당금**은 법상 **사용검사 1년이 지난 달부터** 적립해요. 1·2단지는 2025년 11월 사용승인이라 **곧 관리비에 새로 붙을 수 있어요** — 그만큼 관리비가 오른다고 보시면 돼요",
           "✔ 장기수선충당금은 **집주인 부담**이에요. 세입자가 관리비로 냈다면 이사 나갈 때 돌려받을 수 있어요")

    a.head(6, "라그란데랑 비교하면")
    a.table(["", "이문아이파크자이", "래미안라그란데"],
            [["역", "**101·102동 외대앞역 1분 · 204·205동 신이문역 5분**", "동에 따라 외대앞·신이문역 걸어서 10~15분"],
             ["커뮤니티 기본요금", "**월 15,000원** (전 세대 관리비)", "**없음**"],
             ["10월 관리비", "84㎡대 한 세대 **22만 9,750원**", "-"],
             ["카페", "**폴바셋 카페 운영 중** (쿠폰 월 2잔)", "아직 운영 전 (조식 투표 중)"],
             ["사우나", "금·토·일 · 월 10회", "금·토·일 · 입주민 전용"],
             ["상가", "**병원·맛집 많음** · 오피스텔동 있음", "상대적으로 적은 편"],
             ["철도 소음", "철로 쪽 동은 **있어요**", "철로와 떨어져 있어요"],
             ["단지 동선", "단차를 엘리베이터·계단으로 연결", "지하주차장으로 커뮤니티까지 연결"]],
            note="라그란데는 실거주 경험·단지 안내 기준 · 동·층에 따라 체감이 달라요")
    a.text("라그란데 사는 사람으로서 솔직하게 말하면,", "**역·카페·상가는 아이파크자이가 부럽고,**", "**커뮤니티 기본요금이 없는 건 라그란데가 나아요.**")

    a.head(7, "실거래는요")
    a.text("{{84㎡ 17억대에서 시작해 20억을 넘었어요.}}")
    a.table(["전용", "최근 매매 (중개거래)", "흐름"],
            [["59㎡", "**15억 8,000만** (26.6 · 27층)", "25.11 15억 → 26.3~6 15억대"],
             ["84㎡", "**20억 6,000만** (26.8 · 15층)", "26.1 17억대 → 26.4~5 18억대 → 26.8 20억대"],
             ["102㎡", "**21억** (26.9 · 33층) — 단지 최고가", "18억대에서 21억으로"]],
            note="국토부 실거래 (부동산 앱 조회, 2026.11.24) · 직거래·해제 거래는 빼고 봤어요 · 층·동에 따라 1억 넘게 차이 나요")
    a.text("✔ 84㎡는 **올해 1월 17억대 → 8월 20억 6천**이에요. 입주 첫해에 계단식으로 올라온 모습이에요",
           "✔ 59㎡는 15억 안팎에서 크게 움직이지 않았어요. 바로 옆 라그란데 59㎡ 15억 2천(26.6)과 비슷한 수준이에요",
           "✔ **직거래**(9억 9천, 13억 988만 등)는 가족 간 거래일 수 있어서 시세로 보지 않아요")
    a.text("[[전세·월세는 이 정도예요]]")
    a.table(["전용", "최근 전세", "최근 월세"],
            [["59㎡", "-", "6,000 / 265 · 1억 / 260 · 5억 / 100"],
             ["84㎡", "**8억 5,000 ~ 8억 8,000** (26.11)", "6억 / 135 · 1억 2,000 / 320"]],
            note="국토부 실거래 (부동산 앱 조회, 2026.11.24) · 41㎡ 3억 2,214 · 59㎡ 4억 6,410처럼 같은 금액이 반복되는 계약은 임대 물량으로 보여 빼고 봤어요")
    a.text("✔ 84㎡ 매매 20억대에 전세 8억대면, 전세가율은 **40%대**예요. 갭이 커서 실거주로 들어오는 분이 대부분이에요")

    a.head(8, "착한언니 체크")
    a.numbered("동 번호부터 확인", "**역 1분은 101·102동 이야기**예요 — 같은 단지라도 동마다 역 거리가 달라요",
               "3단지는 별도 블록이라 입주 일정·위치를 따로 확인하세요")
    a.numbered("철길 쪽 동이라면", "역은 가깝지만 **철도 소음은 있어요** — 저층·철로 쪽은 직접 들어보세요",
               "외대앞역 통로는 입주민 출입문 공사 중(11월 말 예정)이라 이용 방식이 바뀔 수 있어요")
    a.numbered("관리비에 커뮤니티가 포함", "기본이용료 **월 15,000원**은 쓰든 안 쓰든 모든 세대에 붙어요")

    a.head(9, "정리하면")
    a.text("✔ **이문아이파크자이**: 4,321세대 · 최고 41층 · 1·2단지 2025.11 입주",
           "✔ 101·102동은 **외대앞역 1분**, 204·205동은 **신이문역 5분**",
           "✔ 84㎡ 매매 **17억대 → 20억 6천** (2026.1 → 8) · 전세 8억대",
           "✔ 상가·맛집이 풍부하고 단지 안에 오피스텔동도 있어요",
           "✔ 커뮤니티 기본이용료 월 15,000원 · 폴바셋 카페 · 사우나 금·토·일",
           "==이문동 아파트 매수·전세 상담도 편하게 남겨 주세요.==")
    a.note("길 건너 래미안라그란데에 살면서 옆 단지를 직접 걸어봤어요. 101·102동에서 철길 옆 통로로 나가면 정말 1분 만에 외대앞역이에요.",
           "솔직히 역·카페·상가는 부러웠어요. 다만 철도 소음은 있고, 커뮤니티 기본요금이 붙는다는 점은 같이 보셔야 해요.")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 래미안라그란데 실거주 후기도 같이 보세요.",
            "출처: 단지 커뮤니티 게시물(2026.11 촬영) · 단지 규모는 정보 사이트·언론 보도 · 사진은 직접 촬영(얼굴·번호판 가림) · 이 글은 투자 권유가 아니에요")
    a.signature("grandxi")
    side = ["**제목(BEST)**: 이문아이파크자이 외대앞역 1분｜커뮤니티 이용료·동선 직접 가봤어요 (라그란데와 비교)",
            "**제목(대안)**: 이문아이파크자이 커뮤니티 2026｜폴바셋 카페·사우나·독서실 요금 정리",
            "**태그**: 이문아이파크자이, 이문아이파크자이커뮤니티, 이문3구역, 외대앞역아파트, 이문동아파트, 래미안라그란데, 이문휘경뉴타운, 동대문아파트, 착한언니복덕방",
            "**썸네일 (캔바 은마 틀)**: 노란 「이문아이파크자이 / 외대앞역 1분」 · 흰 「커뮤니티까지 직접 가봤어요」 · 배경 철길 통로(04)나 타워(02)",
            "**사진 20장 반영 (11/24 촬영)**: 헬스장 이용자 얼굴·입구 행인 가림 · 상가 현수막 전화번호·다른 부동산 간판 사진은 제외",
            "**⚠️ 채울 것**: 통로 입주민 출입문 완공 후 업데이트 · 기본개요는 건축물대장 API 접속 불가로 단지 정보 사이트 기준 — 서버 복구되면 대장 원문과 대조"]
    return a, side


def hillstate_mapo():
    a = Post("2026-11-hillstate-mapo-the-first", "힐스테이트마포더퍼스트 입주 3개월",
             "출처: 국토부 아파트 매매·전월세 실거래 (2025.11~2026.10 신고분) · 단지 규모는 단지 정보 사이트 · 현장 촬영(2026.11) · 작성 규칙 MASTER v1.2")
    I = "img/hsmapo/"
    a.text("{{광흥창역과 서강대역 사이 새 아파트, 전세 얼마면 들어갈까요?}}")
    a.text("답은 **\"84㎡ 10억 안팎\"**이에요.", "다만 입주 직후엔 같은 84㎡가", "7억대에 계약된 적도 있어요.")
    a.text("신수동 **힐스테이트마포더퍼스트**,", "입주한 지 3개월 된 단지예요.")
    a.text("분양 광고 말고,", "**현장과 지난 1년 실거래가**를 보면서", "하나씩 짚어 볼게요.")
    a.blank(); a.greet(); a.blank()
    a.quote("**한 줄 요약** 신수동 488세대 · 2026년 8월 입주 · 84㎡ 전세 중위 10억 · 매매 19~23억대 · 광흥창역·서강대역 사이", "기본")
    a.image(I + "01-hillstate-tower.jpg", "힐스테이트마포더퍼스트 — 독막로 쪽에서 본 모습 (직접 촬영 2026.11)")

    a.head(1, "어떤 단지예요?")
    a.table(["항목", "내용"],
            [["위치", "마포구 **신수동** (독막로 · 광성고 옆)"], ["규모", "**488세대** (향후 2차 포함 약 700세대 규모라는 얘기도 있어요)"],
             ["입주", "**2026년 8월**부터"], ["시공", "현대건설 (힐스테이트)"],
             ["역", "6호선 **광흥창역** · 경의중앙선 **서강대역** (걸어서 이동 가능)"]],
            note="세대수는 단지 정보 사이트(1차 기준) · 2차 규모는 확인되지 않은 이야기라 참고만")
    a.image(I + "02-gate-102.jpg", "단지 정문 — 102동과 상가 (직접 촬영)")
    a.image(I + "03-hillstate-sign.jpg", "HILLSTATE 사인과 단지 진입로 (직접 촬영)")

    a.head(2, "단지 안은 이래요")
    a.image(I + "04-clubhills-entrance.jpg", "커뮤니티 CLUB HILLS 입구 (직접 촬영)")
    a.image(I + "05-clubhills-reception.jpg", "CLUB HILLS 안내데스크 (직접 촬영)")
    a.image(I + "06-underground-path.jpg", "동과 커뮤니티를 잇는 지하 연결 통로 (직접 촬영)")
    a.image(I + "07-cloud-playground.jpg", "CLOUD 놀이터 — 뒤로 광성고가 바로 보여요 (직접 촬영)")
    a.image(I + "08-daycare.jpg", "단지 안 어린이집 (직접 촬영)")
    a.image(I + "09-golden-lounge.jpg", "경로당 GOLDEN LOUNGE (직접 촬영)")
    a.fill("CLUB HILLS 시설 구성(피트니스·골프·독서실 등)·이용료, 관리비 수준 — 아시는 것만 2~3줄")

    a.head(3, "교통 — 역이 두 개예요")
    a.image(I + "11-gwangheungchang-exit4.jpg", "6호선 광흥창역 4번 출구 (직접 촬영)")
    a.image(I + "12-sogang-exit2.jpg", "경의중앙선 서강대역 2번 출구 (직접 촬영)")
    a.image(I + "14-road-sign.jpg", "단지 앞 도로표지판 — 합정·서강대교·강변북로·신촌로터리 (직접 촬영)")
    a.text("✔ 6호선(광흥창)과 경의중앙선(서강대)을 같이 쓰고, **서강대교만 건너면 여의도**예요",
           "✔ 강변북로 진입도 가까워서 차로 다니기도 편해요")
    a.image(I + "10-gwangseong-hs.jpg", "단지 바로 옆 광성고등학교 (직접 촬영)")

    a.head(4, "전세 — 입주장에 어떻게 계약됐나")
    a.table(["계약 월", "59㎡ 전세", "84㎡ 전세"],
            [["6~7월 (입주 전)", "8억 5,000 ~ 9억", "10억 ~ 11억 5,000"],
             ["8~9월 (입주 시작)", "8억 3,000 ~ 8억 5,000", "**7억 7,000** ~ 12억 (중위 약 10억)"],
             ["10월", "-", "9억 5,000 ~ 10억 5,000"]],
            note="국토부 전월세 실거래 · 월세 0원 신규 계약 · 2026.6~10 계약분 · 최근분은 신고가 더 늘 수 있어요")
    a.text("✔ 입주 전후 넉 달에 전세 계약이 몰렸고, 84㎡는 같은 시기에 **7억 7천~12억**까지 벌어졌어요",
           "✔ 잔금이 급한 집은 낮게, 여유 있는 집은 제값을 받은 흐름이에요. 10월엔 **10억 안팎**으로 모였어요")

    a.head(5, "매매, 그리고 옆 단지와 비교")
    a.table(["단지", "84㎡ 매매", "84㎡ 전세 중위"],
            [["**힐스테이트마포더퍼스트** (2026)", "19억 ~ 22억 9,500만 (중개거래 3건, 26.9~10)", "약 10억"],
             ["마포아이파크포레 (옛 신촌숲아이파크, 2019)", "중위 **24억 5,250만** (18건)", "10억 7,000만"]],
            note="국토부 실거래 2025.11~2026.10 신고분 · 직거래·해제 거래 제외 · 더퍼스트는 입주 초기라 거래가 적고 층·타입별 차이가 커요")
    a.text("✔ 바로 옆 **마포아이파크포레**(옛 신촌숲아이파크)보다 매매는 아직 낮게 거래됐고, 전세는 비슷한 수준이에요",
           "✔ 입주 1년이 안 돼서 **시세가 자리 잡는 중**이에요. 숫자 한두 건으로 판단하기보다 동·층별 호가를 같이 보세요")

    a.head(6, "착한언니 체크")
    a.numbered("전세로 들어간다면", "입주장이 끝나 가는 지금은 **10억 안팎**이 기준 · 2년 뒤 만기가 한꺼번에 돌아오는 단지예요")
    a.numbered("매수를 생각한다면", "서울 전역 토지거래허가 — **실거주 요건** 확인 · 거래가 적어 동·층별 비교가 꼭 필요해요")
    a.numbered("주변 개발도 같이", "근처 **신수동 250번지 일대**에 신속통합 재개발 추진준비위원회가 생겼어요 (아직 초기 단계)")

    a.head(7, "정리하면")
    a.text("✔ **힐스테이트마포더퍼스트**: 신수동 488세대, 2026년 8월 입주, 광흥창역·서강대역",
           "✔ 84㎡ 전세 **10억 안팎**, 매매 **19~23억대** (거래 적음)",
           "✔ 옆 마포아이파크포레보다 매매는 아직 낮고 전세는 비슷",
           "==신수동·광흥창 쪽 매수·전세 상담 편하게 남겨 주세요.==")
    a.note("광흥창역에서 서강대역까지 단지 주변을 직접 걸어봤어요. 새 단지답게 커뮤니티와 지하 연결 통로가 깔끔했고, 광성고가 바로 옆이라 학부모 문의가 많을 것 같은 자리예요.")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 공덕 라첼스 입주장 글도 같이 보세요.",
            "출처: 국토부 실거래(2026.10 신고분까지) · 단지 정보 사이트 · 사진은 직접 촬영(얼굴·번호판 가림) · 이 글은 투자 권유가 아니에요")
    a.signature("grandxi")
    side = ["**제목(BEST)**: 힐스테이트마포더퍼스트 입주 3개월｜전세 10억 안팎, 단지·커뮤니티 직접 가봤어요",
            "**제목(대안)**: 힐스테이트마포더퍼스트 전세·매매 시세 2026｜광흥창역 신축, 마포아이파크포레와 비교",
            "**태그**: 힐스테이트마포더퍼스트, 힐스테이트마포, 신수동아파트, 광흥창역아파트, 서강대역아파트, 마포아이파크포레, 신촌숲아이파크, 마포신축, 입주장전세, 착한언니복덕방",
            "**⚠️ 확인**: 매매 실거래가 사이트 데이터라 빠진 거래가 있을 수 있어요 → 부동산 앱 실거래 캡처 주시면 정정 · CLUB HILLS 시설·관리비 채우기",
            "**사진 15장 (11/25 촬영)**: 번호판·행인 가림 · 서강대역 주변 단지(삼익·금호·래미안·IPARK) 사진은 다른 글용으로 보관"]
    return a, side


def mapo_grancio():
    a = Post("2026-12-mapo-gran-xi", "마포그랑자이 시세 2026",
             "출처: 국토부 아파트 매매 실거래 (2025.1~2026.11 계약, 해제·취소 제외, 1·2단지 합산) · 전월세 실거래 (2025.11~2026.10 계약) · 단지 개요는 단지 정보 사이트(KB부동산·호갱노노 등) 공통 표기 — 건축물대장 원문 대조 전 · 현장 촬영 · 작성 규칙 MASTER v1.2")
    a.text("{{마포그랑자이 59㎡, 지금 얼마면 들어갈까요?}}")
    a.text("답은 **\"전세 8억 후반, 매매 21억 안팎\"**이에요.", "다만 같은 59㎡도 층·동에 따라", "매매가가 2억 넘게 벌어져요.")
    a.text("저희 **마포그랑자이점**이", "바로 이 단지 상가에 있어요.")
    a.text("호가 말고,", "**지난 1년 동안의 실거래가**를 보면서", "하나씩 짚어 볼게요.")
    a.blank(); a.greet(); a.blank()
    a.quote("**한 줄 요약** 대흥동 1,248세대 · 2020년 입주 · 59㎡ 매매 20~23억 · 84㎡ 23~26억 · 신규 전세 59㎡ 8억 8,500 · 토허 이후 매매 거래 뚝", "기본")
    a.photo("마포그랑자이 정문·단지명 사인")

    a.head(1, "마포그랑자이, 어떤 단지인가요?")
    a.table(["항목", "내용"],
            [["위치", "마포구 **대흥동** · 2호선 **이대역** 바로 앞 (6호선 대흥역도 이용)"], ["분양 때 이름", "**신촌그랑자이** → 마포그랑자이로 개명"],
             ["규모", "**1,248세대** (임대 216세대 포함) · 최고 23층"], ["사용승인", "**2020년 2월**"],
             ["구성", "1·2단지 (1단지가 메인, 2단지는 떨어져 있음) · 18개 동 (자료에 따라 22개 동)"], ["용적률 · 건폐율", "약 253~256% · 22~26%"],
             ["주차", "약 1,420~1,470대 (세대당 약 1.1대)"], ["난방", "개별난방 (도시가스)"], ["시공", "GS건설"]],
            note="단지 정보 사이트 공통 표기 기준 · 동 수·주차대수는 자료마다 달라 건축물대장으로 다시 확인할게요")
    a.photo("단지 안 조경·동 사이 산책로")

    a.head(2, "토지거래허가 이후, 매매가 확 줄었어요")
    a.table(["기간", "매매 거래", "59㎡", "84㎡"],
            [["2025.1~3", "17건", "16억 ~ 17억 대", "18억 4천 ~ 22억"],
             ["2025.4~6", "30건", "17억 ~ 21억 8천", "18억 7천 ~ 27억"],
             ["2025.7~10", "18건", "21억 ~ 23억", "24억 ~ 26억 8,500"],
             ["**2025.11~2026.11 (13개월)**", "**19건**", "20억 2천 ~ 23억 2천", "23억 ~ 26억 1,500"]],
            note="국토부 실거래 (계약일 기준 · 해제·취소 제외 · 1·2단지 합산 · 2026.11 조회) · 최근 한두 달은 신고가 더 늘 수 있어요")
    a.text("2025년 상반기에는 한 달에 10건 넘게 거래되면서", "59㎡가 16억대에서 21억대로 올라왔어요.")
    a.text("그런데 **2025년 10월 서울 전역이 토지거래허가구역**이 된 뒤로는", "**13개월 동안 19건**,", "한 달에 1~2건꼴로 줄었어요.")
    a.text("✔ 가격은 크게 꺾이지 않았어요. 59㎡ 20억~23억, 84㎡ 23억~26억 사이에서 **거래량만 줄어든 보합** 흐름이에요",
           "✔ 반면 전세·월세는 같은 기간 **280건 넘게** 계약됐어요. 실거주 요건 때문에 사는 사람은 줄고, 빌려 사는 수요는 그대로인 거죠")

    a.head(3, "전세, 지금 얼마에 계약되나요?")
    a.table(["전용", "신규 전세 중위", "전세 범위 (신규·갱신)", "월세 예시"],
            [["59㎡", "**8억 8,500만** (38건)", "6억 6,150만 ~ 9억 8,000만", "7,000 / 60 · 3억 / 215"],
             ["84㎡", "**10억 9,750만** (44건)", "~ 13억 5,000만", "9억 / 100 · 5,000 / 330"]],
            note="국토부 전월세 실거래 · 신규=새로 맺은 계약, 갱신 계약은 시세보다 낮게 잡혀요 · 최근분은 신고가 더 늘 수 있어요")
    a.text("✔ 갱신 계약(5% 상한)이 섞여 있어서, **새로 구할 때는 '신규 중위'를 기준**으로 보세요")

    a.head(4, "최근 매매 실거래")
    a.table(["거래월", "전용", "층", "매매가"],
            [["26.10", "96㎡", "8층", "**28억 5,000만**"], ["26.7", "59㎡", "4·5층", "22억 3,000만"],
             ["26.6", "84㎡", "7층", "26억 1,500만"], ["26.5", "84㎡", "3층", "23억"], ["26.5", "59㎡", "11층", "21억 4,000만"],
             ["26.4", "84㎡", "10층", "24억 9,500만"], ["26.3", "59㎡", "17층", "22억 8,000만"], ["25.12", "59㎡", "14층", "23억 2,000만"]],
            note="국토부 실거래 (해제·취소 제외) · 2026.11.2 계약 59㎡ 15억 5,000만 1건은 시세와 차이가 커서(특수 거래 가능성) 표에서 뺐어요")
    a.text("✔ 같은 59㎡도 **저층 20억대 초반 ~ 고층 23억대**, 2억 넘게 차이 나요",
           "✔ 거래가 적은 만큼 **최근 한 건이 시세처럼 보이기 쉬워요.** 동·층·향을 같이 봐야 해요")
    a.photo("커뮤니티 이용안내판 (이용료·운영시간)")

    a.head(5, "커뮤니티와 생활")
    a.table(["어디", "시설 (2022년 기준)"],
            [["1단지 커뮤니티", "**수영장** · 헬스 · 사우나 · 스크린골프"],
             ["103동 클럽 자이안", "기구 필라테스 (개인·듀엣·6인 그룹)"],
             ["2단지 커뮤니티", "GX·문화강좌 — 플라잉요가 등"]],
            note="2022년 입주민 블로그 소개 기준 · 지금 운영 여부·이용료는 현장 안내판으로 다시 확인")
    a.text("✔ 지금도 **수영장 운영 중**이에요. 강북 단지에서 수영장까지 있는 커뮤니티는 흔하지 않아요 (마프자도 있어요)")
    a.fill("현재 커뮤니티 이용료·운영시간 (안내판 사진 보고 표로) · 최근 이용 제한 이슈가 있다면 한 줄")
    a.fill("관리비 — 59·84㎡ 한 달 명세서 (동·호수 가림)")
    a.text("[[사무소에서 매일 보는 좋은 점]]")
    a.text("✔ **평지예요.** 마포는 언덕 단지가 많은데, 그랑자이는 단지 안팎이 평평해서 유모차·어르신 동선이 편해요",
           "✔ **커뮤니티가 잘 돼 있어요.** 입주민 만족도가 높은 편이에요")
    a.text("[[아쉬운 점]]")
    a.text("✔ **초등학교**예요. 배정되는 창천초가 빌라 밀집 지역과 같이 있고, **학급 수가 적은 편**이에요",
           "✔ 그래서 초등 자녀가 있는 집은 학교·학원가가 가까운 **마포프레스티지자이**를 같이 보는 경우가 많아요")

    a.head(6, "대흥동 다른 단지와 비교하면")
    a.table(["단지", "준공", "59㎡ 매매 중위", "84㎡ 매매 중위"],
            [["**마포그랑자이**", "2020", "21억 4,000만", "24억 9,500만"], ["마포자이2차", "2014", "- (59타입 없음)", "26억"],
             ["마포태영", "1999", "16억 8,000만", "20억 9,800만"], ["대흥동세양", "2000", "-", "15억 5,500만"]],
            note="국토부 실거래 2025.11~2026.10 · 대흥동 전체 비교는 「대흥동 아파트 시세 2026」 글 참고")

    a.head(7, "착한언니 체크")
    a.numbered("전세를 구한다면", "갱신 말고 **신규 계약 기준**으로 시세를 보세요 · 동·층별 호가 차이가 커요")
    a.numbered("매수를 생각한다면", "서울 전역 토지거래허가 — **실거주 요건** · 시가 15억·25억 대출 구간을 타입별로 확인")
    a.numbered("집주인이라면", "전월세가 많이 도는 단지라 **입주 날짜·옵션**으로 차별화하면 빨리 맞춰져요")

    a.head(8, "정리하면")
    a.text("✔ **마포그랑자이**: 대흥동 1,248세대, 2020년 입주 (옛 신촌그랑자이)",
           "✔ 59㎡ 매매 20~23억 · 84㎡ 23~26억 · 신규 전세 59㎡ 8억 8,500",
           "✔ 토허 이후 매매는 13개월 19건으로 줄었지만, 전월세는 꾸준히 계약되는 단지",
           "==마포그랑자이점이 단지 상가에 있어요. 동·층 비교가 필요하시면 편하게 들러 주세요.==")
    a.note("저희 사무소가 이 단지 상가에 있어서, 동별 채광·소음·엘리베이터 대기 같은 건 매일 보고 있어요.")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 다음 편은 마포프레스티지자이, 그다음은 마포 신축 3대장 비교예요.",
            "출처: 국토부 실거래(2026.10 신고분까지) · 단지 개요는 단지 정보 사이트 기준(건축물대장 대조 예정) · 이 글은 투자 권유가 아니에요")
    a.signature("grandxi")
    side = ["**제목(BEST)**: 마포그랑자이 시세 2026｜사무소가 단지 안에 있는 중개사가 정리했어요 (전세·매매·관리비)",
            "**제목(대안)**: 마포그랑자이 전세 시세｜59㎡ 8억 후반, 84㎡ 11억 (신규 계약 기준)",
            "**태그**: 마포그랑자이, 마포그랑자이시세, 마포그랑자이전세, 마포그랑자이실거래가, 신촌그랑자이, 대흥동아파트, 대흥역아파트, 마포신축, 착한언니복덕방",
            "**시리즈**: 마포 신축 3대장 ① (→ ② 마포프레스티지자이 → ③ 더클래시 보강 → ④ 3대장 비교)",
            "**⚠️ 채울 것 (내일 촬영)**: 정문·조경·커뮤니티 안내판·관리비 명세서 · 좋은 점/아쉬운 점",
            "**매매 실거래**: 대표님 앱 목록으로 2025.1~2026.11 전체 대조 완료 (11/26) · 동·호수는 글에 안 씀",
            "**확인**: 동 수·주차·용적률은 사이트마다 달라 건축물대장 대조 필요 (공공데이터 서버 차단 중 — 정부24 대장 캡처 주시면 정정)"]
    return a, side


def mapo_prestige_xi():
    a = Post("2026-12-mapo-prestige-xi", "마포프레스티지자이 시세 2026",
             "출처: 국토부 아파트 매매 실거래 (2025.1~2026.10 계약, 해제·취소 제외) · 전월세 실거래 (2025.11~2026.10 계약) · 단지 개요는 단지 정보 사이트(KB부동산·당근부동산·리치고 등) 공통 표기 — 건축물대장 원문 대조 전 · 작성 규칙 MASTER v1.2")
    a.text("{{같은 59㎡인데, 왜 그랑자이보다 1억 넘게 비쌀까요?}}")
    a.text("답은 **\"아이 키우는 집이 먼저 찾는 단지\"**라서예요.", "초등학교와 학원가가 가깝고,", "주변이 아파트 단지로 둘러싸여 있거든요.")
    a.text("염리동 **마포프레스티지자이**,", "마포 신축 3대장 중 84㎡ 가격이 가장 높은 단지예요.")
    a.text("호가 말고,", "**지난 1년 동안의 실거래가**를 보면서", "하나씩 짚어 볼게요.")
    a.blank(); a.greet(); a.blank()
    a.quote("**한 줄 요약** 염리동 1,694세대 · 2021년 입주 · 59㎡ 22~24억 · 84㎡ 26~28억대 · 신규 전세 59㎡ 9억 3,500 / 84㎡ 12억", "기본")
    a.photo("마포프레스티지자이 정문·단지명 사인")

    a.head(1, "마포프레스티지자이, 어떤 단지인가요?")
    a.table(["항목", "내용"],
            [["위치", "마포구 **염리동** (아현뉴타운 염리3구역) · 2호선 **이대역** 역세권"], ["규모", "**1,694세대** · 1~3단지 (1단지가 메인) · 18개 동 · 최고 27층"],
             ["사용승인", "**2021년 12월**"], ["용적률 · 건폐율", "약 250~251% · 19~20%"],
             ["주차", "약 2,000대 (세대당 약 1.2대)"], ["시공", "GS건설"], ["초등학교", "**한서초** (단지에서 약 200m)"]],
            note="단지 정보 사이트 공통 표기 기준 · 초등 배정은 교육청 확인 필요 · 건축물대장으로 다시 확인할게요")
    a.photo("단지 안 조경·놀이터")

    a.head(2, "아이 키우는 집이 왜 여기를 먼저 볼까")
    a.text("저희 사무소에서 상담하면서 느끼는 건 이래요.")
    a.text("✔ **초등학교가 단지 바로 옆**이에요. 한서초까지 200m 남짓이라 아이 혼자 등하교하기 좋아요",
           "✔ 한서초 주변이 **마포더클래시·마포자이더센트리지·마래푸 3단지·마프자** 같은 신축급 단지로 둘러싸여 있어요",
           "✔ **대흥역~공덕역 학원가**와도 가까운 편이에요")
    a.text("그래서 **아이 키우는 집은 마프자를 조금 더 선호**하는 분위기예요.", "같은 대흥·염리 생활권인 마포그랑자이와 비교하면", "이 차이가 가격에도 보여요.")
    a.photo("한서초 가는 길 · 학원가")

    a.head(3, "매매는요? — 토허 직전에 몰리고, 이후엔 뚝")
    a.table(["기간", "매매 거래", "59㎡", "84㎡"],
            [["2025.1~3", "40건", "16억 8천 ~ 19억 6천", "22억 6천 ~ 24억 7천"],
             ["2025.4~6", "35건", "17억 4천 ~ 23억 1천", "22억 5천 ~ 27억"],
             ["2025.7~10", "22건 (10월에만 12건)", "22억 ~ 24억", "24억 6천 ~ **29억 6천**"],
             ["**2025.11~2026.10 (12개월)**", "**18건**", "21억 5천 ~ 24억", "26억 ~ 28억 5천"]],
            note="국토부 실거래 (계약일 기준 · 해제·취소 제외 · 2026.11 조회) · 59㎡는 301·302동이 다른 동보다 낮게 거래되는 편이라 범위 하단에 영향")
    a.text("2025년 상반기에만 **75건**이 거래되면서", "59㎡가 17억대에서 23억대로 올라왔어요.")
    a.text("서울 전역 토지거래허가 지정 직전인 **2025년 10월엔 한 달에 12건**,", "84㎡ **29억 6천**까지 찍었어요.", "이후 12개월은 **18건**으로 줄었어요.")
    a.table(["거래월", "전용", "층", "매매가"],
            [["26.10", "84㎡", "11층", "**27억 8,000만**"], ["26.9", "59㎡", "13층", "22억 7,000만"], ["26.8", "59㎡", "12층", "23억 5,000만"],
             ["26.6", "84㎡", "18층", "28억 3,000만"], ["26.5", "84㎡", "22층", "26억 8,000만"], ["26.4", "59㎡", "22층", "23억 6,000만"],
             ["26.1~3", "59㎡", "11~13층", "24억"], ["26.4~5", "42㎡", "12·13층", "15억 4,000 ~ 15억 5,000"]],
            note="최근 대표 거래 · 2025.10 114㎡ 27층 40억 거래도 있었어요")
    a.text("✔ 가격은 꺾이지 않고 **59㎡ 22~24억, 84㎡ 26~28억대**에서 보합이에요",
           "✔ 84㎡는 시가 **25억을 넘어서 주담대 한도 2억** 구간이에요. 현금 비중이 커야 하는 단지예요")

    a.head(4, "전세, 지금 얼마에 계약되나요?")
    a.table(["전용", "신규 전세 중위", "전세 범위 (신규·갱신)", "월세 예시 (신규)"],
            [["59㎡", "**9억 3,500만** (29건)", "5억 7,900만 ~ 9억 8,000만", "1억 / 320 · 4억 / 220"],
             ["84㎡", "**12억** (33건)", "5억 5,000만 ~ 14억", "5억 / 280 · 5,000 / 400"],
             ["대형 (114㎡ 등)", "18억 2,500만 (6건)", "13억 7,800만 ~ 19억", "-"]],
            note="국토부 전월세 실거래 · 갱신 계약은 시세보다 낮게 잡혀요 · 최근분은 신고가 더 늘 수 있어요")

    a.head(5, "커뮤니티와 생활")
    a.text("✔ 마프자도 **수영장이 있는 커뮤니티**예요. 마그자와 함께 강북에서 드문 구성이에요")
    a.fill("커뮤니티 시설·이용료·운영시간 (안내판 사진 보고 표로)")
    a.fill("관리비 — 59·84㎡ 한 달 명세서 (동·호수 가림)")
    a.fill("역까지 동선(이대역·대흥역·애오개역 중 어디가 가까운지, 동별) · 언덕 여부 · 아쉬운 점 1~2가지")

    a.head(6, "마포그랑자이랑 비교하면")
    a.table(["", "마포프레스티지자이", "마포그랑자이"],
            [["입주", "2021", "2020"], ["세대수", "1,694", "1,248"], ["59㎡ 최근 매매 (26년)", "**22억 5천 ~ 24억**", "20억 2천 ~ 22억 8천"],
             ["84㎡ 최근 매매 (26년)", "**26억 ~ 28억 5천**", "23억 ~ 26억 1,500"],
             ["토허 이후 매매 (약 1년)", "18건", "19건"], ["59㎡ 신규 전세", "9억 3,500만", "8억 8,500만"],
             ["84㎡ 신규 전세", "12억", "10억 9,750만"], ["초등학교", "**한서초 (단지 옆)**", "창천초 (빌라와 함께, 학급 수 적은 편)"],
             ["수영장", "있음", "있음"],
             ["지형", "-", "**평지**"], ["이런 분께", "**초등 자녀** 있는 집", "평지·커뮤니티 중시, 아이 없는 2~3인 가구"]],
            note="국토부 실거래 2025.11~2026.10 · 학교·지형은 착한언니 현장 판단")

    a.head(7, "착한언니 체크")
    a.numbered("매수라면", "84㎡는 **25억 초과 → 주담대 2억** 구간 · 59㎡도 층에 따라 25억 근처예요", "서울 전역 토지거래허가 — 실거주 요건")
    a.numbered("전세라면", "**신규 계약 기준** 시세로 보세요 · 학기 시작 전(1~2월) 수요가 몰려요")
    a.numbered("초등 배정", "단지·동에 따라 다를 수 있으니 **교육청 학교배정 조회**로 꼭 확인하세요")

    a.head(8, "정리하면")
    a.text("✔ **마포프레스티지자이**: 염리동 1,694세대, 2021년 입주, 한서초 단지 옆",
           "✔ 59㎡ 22~24억 · 84㎡ 26~28억대 — 3대장 중 84㎡ 최고 · 토허 직전 2025.10에 84㎡ 29억 6천",
           "✔ 아이 키우는 집이 먼저 찾는 단지 — 그랑자이보다 59㎡ 기준 1억~1억 5천 정도 높게 거래돼요",
           "==마포그랑자이점에서 걸어서 가까운 단지예요. 두 단지 비교 상담 편하게 남겨 주세요.==")
    a.note("상담하다 보면 초등 자녀가 있는 집은 마프자부터, 평지와 커뮤니티를 중시하는 분은 그랑자이부터 보시는 경우가 많아요.")
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 마포그랑자이 편과 3대장 비교 편도 같이 보세요.",
            "출처: 국토부 실거래(2026.10 신고분까지) · 단지 개요는 단지 정보 사이트 기준(건축물대장 대조 예정) · 이 글은 투자 권유가 아니에요")
    a.signature("grandxi")
    side = ["**제목(BEST)**: 마포프레스티지자이 시세 2026｜그랑자이보다 1억 넘게 비싼 이유 (학교·전세·매매)",
            "**제목(대안)**: 마포프레스티지자이 전세 시세｜59㎡ 9억 3천, 84㎡ 12억 (신규 계약 기준)",
            "**태그**: 마포프레스티지자이, 마프자, 마포프레스티지자이시세, 마포프레스티지자이전세, 염리동아파트, 한서초, 마포그랑자이, 마포신축, 착한언니복덕방",
            "**시리즈**: 마포 신축 3대장 ② (① 마포그랑자이 → ③ 더클래시 보강 → ④ 3대장 비교)",
            "**⚠️ 채울 것**: 정문·조경·학교 가는 길 사진 · 커뮤니티 안내판 · 관리비 · 역 동선·언덕 여부",
            "**매매 실거래**: 대표님 앱 목록으로 2024.7~2026.10 대조 (11/26) · 동 번호는 글에 안 씀",
            "**확인**: 301·302동이 낮게 거래되는 이유(위치·향·구조?) 확인 · 한서초 배정·거리는 사이트 기준 → 교육청 확인 · 사용승인(2021.12) vs 입주 시점 표기 차이"]
    return a, side



def songs8():
    a = Post("2026-11-songs8-officetel", "송스8 오피스텔 매매 급매 (이대 정문 2분)",
             "출처: 매물 가격·임대 조건·관리비는 착한언니복덕방 매물 정보(2026.11) · 주변 실거래는 국토교통부 오피스텔 매매 실거래(계약 2025.11~2026.10, 2026.11.1 수집) · 사진 직접 촬영 · 작성 규칙 MASTER v1.2")
    I = "img/songs8/"
    a.text("{{이대 정문 앞 오피스텔, 1억 중반에 살 수 있을까요?}}")
    a.text("답은 **\"지금 있어요\"**예요.", "이대 정문까지 걸어서 **2~3분**, **송스8(Song's 8)** 매물이에요.")
    a.text("광고 문구 말고,", "**월세·관리비·주변 실거래**를 보면서", "하나씩 짚어 볼게요.")
    a.blank(); a.greet(); a.blank()
    a.quote("**한 줄 요약** 송스8 오피스텔 · 이대 정문 2~3분 · 매매 **1억 4,800만** · 월세 1,000/85~90 기준 수익률 **약 7.4~7.8%** (세전·대출 없음) · 분양가보다 **3,200만 원↓** · 네이버 호가 중 최저 · **즉시 입주** · 관리비 12만 원(인터넷 포함)", "기본")
    a.text("※ 가격·조건은 2026년 11월 기준이고, 거래가 되면 바로 마감돼요.", "투자 권유가 아니라 매물 정보예요.", size=14, color="#888888")

    a.head(1, "어디에 있나요?")
    a.image(I + "01-exterior.jpg", "송스8 전경 — 지하 1층~지상 9층 (직접 촬영 2026.11)")
    a.image(I + "02-entrance.jpg", "건물 출입구 — 이화여대5길 쪽 (직접 촬영)")
    a.text("✔ **이대 정문까지 걸어서 2~3분**",
           "✔ **2호선 이대역**도 가까워서 신촌·홍대·시청 방향으로 바로 나가요",
           "✔ **호텔처럼 카드키**로 움직여요 — 1층 출입구도 카드, 엘리베이터도 카드를 대야 **내가 사는 층에만** 올라가요")
    a.image(I + "18-ewha-street.jpg", "이대 정문 쪽으로 이어지는 골목 — 식당·카페·수선집이 모여 있어요 (직접 촬영)")

    a.head(2, "매물 정보")
    a.table(["중개대상물 표시·광고", "내용"],
            [["소재지", "서울특별시 서대문구 대현동 56-119 (송스8) · **8층** / 총 9층"], ["종류 · 거래형태", "오피스텔 · **매매**"],
             ["가격", "**1억 4,800만 원**"], ["면적", "전용 **19.8㎡**"],
             ["총 층수", "지하 1층 / 지상 9층"], ["사용승인일", "2015년 7월 30일"],
             ["방 수 / 욕실 수", "1개 / 1개"], ["방향", "북향 (주된 창 기준)"],
             ["입주 가능일", "**즉시 입주**"], ["주차 대수", "총 0대 (건축물대장 기준)"],
             ["관리비", "월 **12만 원** · 인터넷 포함 · 개별 난방(가스)·전기 사용료 별도"],
             ["중개사무소", "신촌자이엘라부동산공인중개사사무소 · 대표 공인중개사 신수경 · 등록번호 11410-2019-00062"],
             ["소재지 · 연락처", "서울특별시 서대문구 대현동 104-36, B101호 · 02-364-4080"]],
            note="공인중개사법 제18조의2 · 중개대상물 표시·광고 명시사항 세부기준 · 면적·층·사용승인일·주차는 건축물대장(2026.11.26 조회) · 표시·광고 기준일 2026.11.26")
    a.text("**이 방의 포인트**")
    a.table(["", "내용"],
            [["임대 시세 (일반)", "보증금 **1,000만 / 월 85만~90만**"], ["임대 시세 (단기)", "보증금 **200만 / 월 120만** 안팎"],
             ["관리비", "**12만 원, 인터넷 포함**"], ["입주", "**즉시 입주** — 실거주도, 새 세입자 맞추기도 바로 가능"], ["보안", "출입구·엘리베이터 **카드키** (호텔식 — 내 층만 이동)"],
             ["건물", "철근콘크리트 · 오피스텔 **42실** · 엘리베이터 1대"],
             ["옵션", "에어컨 · 세탁기 · 냉장고 · 전자레인지 · 인덕션 · TV · 책상 · 침대"]],
            note="임대 시세·옵션은 착한언니복덕방 매물 정보(2026.11) · 건물 정보는 건축물대장")

    a.head(3, "집 안 둘러보기")
    a.image(I + "03-entry-view.jpg", "현관에서 본 모습 — 왼쪽 욕실, 오른쪽 주방·수납장 (직접 촬영)")
    a.image(I + "05-room-wide.jpg", "주방 쪽에서 현관 방향 — 일자형 주방, 냉장고 자리 (직접 촬영)")
    a.image(I + "06-kitchen-front.jpg", "주방 정면 — 2구 인덕션, 상하부장, TV장, 세탁기까지 한 줄로 (직접 촬영)")
    a.image(I + "07-room-bed.jpg", "창 쪽 — 침대·책상 놓고도 동선이 남아요 (직접 촬영)")
    a.image(I + "08-window-view.jpg", "창밖 — 앞 건물 사이로 하늘이 트여 있어요 (직접 촬영)")
    a.image(I + "09-aircon-tv.jpg", "벽걸이 에어컨 · TV · 붙박이장 (직접 촬영)")
    a.image(I + "15-washer-microwave.jpg", "빌트인 세탁기 · 전자레인지 자리 (직접 촬영)")
    a.image(I + "16-storage.jpg", "현관 옆 키 큰 수납장 — 원룸에서 제일 아쉬운 게 수납인데, 넉넉해요 (직접 촬영)")
    a.image(I + "12-bathroom.jpg", "욕실 — 세면대·샤워·변기, 수납 거울장 (직접 촬영)")
    a.image(I + "14-boiler.jpg", "개별 보일러 (나비엔) (직접 촬영)")
    a.image(I + "11-corridor.jpg", "복도 (직접 촬영)")
    a.image(I + "10-elevator.jpg", "엘리베이터 — 카드를 대야 내 층 버튼이 눌려요 (직접 촬영)")

    a.head(4, "수익률, 직접 계산해 볼게요")
    a.text("오피스텔은 결국 **얼마에 사서, 얼마를 받느냐**예요.", "월세 85만·90만, 그리고 단기까지 나란히 놓았어요.")
    a.table(["", "월세 85만", "**월세 90만**", "단기 임대"],
            [["보증금 / 월세", "1,000만 / 85만", "1,000만 / 90만", "200만 / 120만"],
             ["1년 월세", "1,020만", "1,080만", "1,440만"], ["실투자금 (1억 4,800만 − 보증금)", "1억 3,800만", "1억 3,800만", "1억 4,600만"],
             ["**연 수익률 (세전·대출 없음)**", "**약 7.4%**", "**약 7.8%**", "**약 9.9%**"],
             ["취득세 4.6% (약 681만) 포함하면", "약 7.0%", "약 7.5%", "약 9.4%"]],
            note="착한언니 계산 · 중개보수·재산세·공실·수선비 미반영 · 월세 90만은 올해 같은 건물 신규 월세 신고(1,000/90~94) 기준 · 단기 임대는 공실·청소·가구 관리 부담이 있어 매달 같은 금액이 보장되진 않아요")
    a.text("[[일반 월세만 맞춰도 7%대]]")
    a.text("요즘 예금 금리와 **꼭 나란히 놓고** 비교해 보세요.")

    a.head(5, "솔직히 말씀드릴게요 — 이런 분께 추천해요")
    a.text("오피스텔은 **시세차익 보고 사는 상품이 아니에요.**", "솔직히 그건 아파트 얘기예요.",
           "오피스텔은 **매달 들어오는 월세**, 아니면 **내가 내던 월세를 아끼는 것**, 이 두 가지로 보시는 게 맞아요.")
    a.table(["이런 분", "왜 송스8인가요?"],
            [["**① 실거주로 오피스텔 사실 분**", "이대 앞은 원룸 월세가 비싸요. 이 방도 **월 85~90만**을 받는 방이에요. 내가 들어가 살면 **그 월세를 매달 아끼는 셈**이에요"],
             ["**② 월세 받는 오피스텔 하나 갖고 싶은 분**", "1억 중반으로 **수익률 7%대**. 큰돈 없이 시작하는 첫 수익형 부동산으로 딱이에요"]])
    a.text("[[대학가 월세 수요는 늘 있어요]]")
    a.text("✔ 이대 앞은 **매 학기 새로 들어오는 학생**이 있어서 월세 수요가 끊기지 않아요",
           "✔ 세입자 대부분이 **학생**이라, 부모님이 월세를 챙기는 경우가 많아 **안정적인 임대 수요**가 받쳐 줘요",
           "✔ 이대 정문 2~3분 + 호텔식 카드키 — **여학생과 부모님이 제일 먼저 보는 두 가지**를 다 갖췄어요")

    a.head(6, "송스8, 실제로 얼마에 거래됐을까요?")
    a.text("같은 건물 실거래부터 볼게요. 송스8은 **전용 19.8㎡와 20.3㎡** 두 가지예요.")
    a.table(["계약", "전용", "층", "매매가"],
            [["2026.11", "20.3㎡", "9층", "1억 4,850만"], ["2025.2", "19.8㎡", "4층", "1억 3,650만"],
             ["2024.12", "19.8㎡", "7층", "1억 3,650만"], ["2024.10", "19.8㎡", "4층", "1억 3,650만"],
             ["2024.7", "19.8㎡", "8층", "1억 3,800만"], ["2024.1", "19.8㎡", "3층", "1억 4,750만"],
             ["2024.1", "20.3㎡", "3층", "1억 4,900만"], ["2023.8", "20.3㎡", "5층", "1억 4,900만"],
             ["2017.9", "19.8㎡", "6층", "1억 8,028만"], ["**2016.2~3 (분양)**", "19.8㎡ / 20.3㎡", "3~9층 · 30여 건", "**1억 8,028만 / 1억 8,467만**"]],
            note="국토교통부 오피스텔 매매 실거래 (2015.1~2026.11 전체, 2026.11.26 조회) · 해제된 거래 2건 제외 · 2016년 초 같은 가격 일괄 신고는 분양 물량으로 보여요 · 최근 거래는 신고 기한(30일) 때문에 더 늘어날 수 있어요")
    a.text("월세는 이렇게 신고됐어요.")
    a.table(["계약", "전용", "보증금 / 월세", "구분"],
            [["2026.8", "20.3㎡", "1,000만 / 92만~94만", "신규"], ["2026.8", "20.3㎡", "2,000만 / 80만", "신규"],
             ["2026.5", "20.3㎡", "1,000만 / 90만", "신규"], ["2026.2", "20.3㎡", "3,000만 / 78만", "신규"],
             ["2026.1", "20.3㎡", "1,000만 / 80만", "갱신"]],
            note="국토교통부 오피스텔 전월세 실거래 (2025.11~2026.11) · 반전세 1건 제외")
    a.text("[[분양가보다 3,200만 원 낮게]]")
    a.text("✔ 2016년 분양 때 19.8㎡는 **1억 8,028만**이었어요 — 이 집도 **분양받아 지금까지 갖고 계시던 집주인** 매물이에요",
           "✔ 지금 매물은 분양가보다 **3,228만 원 낮고**, **네이버 부동산 송스8 매물 중 최저가**예요 (2026.11.26 기준)",
           "✔ 2024년 이후 19.8㎡는 **1억 3,650만~1억 4,750만**에 거래됐어요",
           "✔ 올해 신규 월세는 20.3㎡ 기준 **1,000만 / 90만 안팎** — 1,000/85는 무리 없는 조건이에요")

    a.head(7, "주변 오피스텔은 얼마에 거래됐을까요?")
    a.text("같은 대현동, 이대 앞 **소형 오피스텔(전용 13~20㎡)** 실거래를 모아 봤어요.")
    a.table(["단지 (준공)", "전용", "실거래 범위", "건수"],
            [["슈테리움 (2019)", "13㎡", "1억 2,380만 ~ 1억 4,300만", "3"],
             ["이대오늘아침 (2018)", "16~19㎡", "1억 4,500만 ~ 1억 5,800만", "2"],
             ["이대프리젠#1 (2017)", "14~16㎡", "1억 5,800만 ~ 1억 6,500만", "5"],
             ["더가온 (2018)", "17~20㎡", "1억 7,000만 ~ 1억 7,600만", "4"],
             ["영타운 지웰 에스테이트 (2017)", "19~20㎡", "1억 5,500만 ~ 1억 9,600만", "14"],
             ["유씨유 이대 (2018)", "17㎡", "1억 8,500만 ~ 1억 9,700만", "5"],
             ["이대 포레스트 (2019)", "18㎡", "1억 9,800만 ~ 2억 2,000만", "11"]],
            note="국토교통부 오피스텔 매매 실거래 · 계약 2025.11~2026.10 · 대현동 전용 22㎡ 이하 · 해제 거래 제외 · 면적·층·준공연도가 달라 단순 비교는 어려워요")
    a.text("✔ 이대 앞 소형 오피스텔은 대부분 **1억 5천~2억** 사이에서 거래됐어요",
           "✔ 비슷한 크기(19~20㎡)인 영타운 지웰 에스테이트(2017)는 1억 5,500만~1억 9,600만, 더가온(2018)은 1억 7,000만대예요",
           "✔ 송스8(2015)은 준공이 2~3년 빠른 만큼, **1억 중반에 이대 정문 앞 20㎡**를 살 수 있다는 게 포인트예요")

    a.head(8, "착한언니 체크 — 계약 전에 꼭 보세요")
    a.numbered("즉시 입주 매물이에요", "세입자 승계 없이 **바로 들어가 살거나**, 원하는 조건으로 **새 세입자를 맞출 수** 있어요", "2월 새 학기 전에 잔금 치르면 바로 월세 맞추기 좋은 타이밍이에요")
    a.numbered("세금", "오피스텔 취득세는 **4.6%**(지방교육세·농특세 포함)예요",
               "주거용으로 임대하면 **주택 수에 들어갈 수 있어요** — 다른 집 세금에 영향이 있는지 계약 전 세무 상담을 권해요")
    a.numbered("단기 임대를 생각하신다면", "관리 규약상 단기 임대가 가능한지, 청소·가구 관리는 누가 할지 미리 정해요",
               "월 120만은 **채워졌을 때** 금액이에요 — 공실 기간을 넣고 다시 계산해 보세요")
    a.numbered("공용 시설", "1층 공용 세탁실·스타일러가 있어요 (점검일 기준 건조기 1대 고장 안내) — 관리사무소에 수리 일정 확인")
    a.image(I + "17-laundry-room.jpg", "공용 세탁실 — 대형 세탁기·건조기·스타일러 (직접 촬영)")

    a.head(9, "정리하면")
    a.text("✔ **송스8 오피스텔**: 이대 정문 2~3분 · 이대역 근처 · 호텔식 카드키 · 전용 19.8㎡ · 2015년 준공",
           "✔ 매매 **1억 4,800만**, 월세 **1,000/85~90** 기준 수익률 **약 7.4~7.8%** (세전·대출 없음)",
           "✔ 시세차익보다 **월세 수익 또는 실거주 월세 절감**용 — 대학가라 임대 수요가 늘 있어요",
           "✔ 단기 **200/120** 맞추면 약 9.9% — 공실·관리 부담은 따로 계산",
           "✔ 관리비 **12만 원, 인터넷 포함** · **즉시 입주**",
           "✔ 분양가(1억 8,028만)보다 **3천만 원 넘게 낮은**, 지금 **네이버 송스8 매물 중 최저가** · 주변 소형 오피스텔(1억 5천~2억)보다도 낮아요",
           "==보러 오실 땐 자이엘라점으로 연락 주세요. 이대 앞 골목은 직접 걸어 보셔야 감이 와요.==")
    a.note()
    a.outro("새 글 알림을 받고 싶으시다면 블로그 이웃 추가 해 두세요. 신촌·이대 원룸 고르는 법은 「신촌 원룸 구하기」 글에서 보세요.",
            "매물 정보는 2026년 11월 기준이고 거래 완료 시 마감돼요 · 수익률은 세전·대출 없음 가정의 착한언니 계산 · 주변 실거래는 국토교통부 공개 자료 · 이 글은 투자 권유가 아니에요")
    a.signature("zaiella")
    side = ["**제목(BEST)**: 송스8 오피스텔 매매 급매 1억 4,800만｜분양가보다 3천만 원 낮은 최저가, 이대 정문 2분",
            "**제목(대안)**: 이대 오피스텔 매매 급매｜송스8 1억 4,800만, 월세 90만이면 수익률 7.8%",
            "**태그**: 송스8, 송스8오피스텔, 이대오피스텔, 이대오피스텔매매, 이대역오피스텔, 대현동오피스텔, 신촌오피스텔매매, 오피스텔급매, 소액투자, 착한언니복덕방",
            "**표시·광고 명시사항**: 다 채웠어요 (관리비 별도 항목은 개별 난방·전기로 적었어요 — 수도가 관리비에 포함인지 다르면 수정)",
            "**광고 표현 체크**: '급매'·'최저가'는 근거(분양가 대비·네이버 호가 기준일) 같이 적어 둠 — 가격 바뀌거나 거래 완료되면 글 수정/'거래 완료' 표시 (미수정 시 부당 광고)",
            "**'급매' 근거**: 분양가(19.8㎡ 1억 8,028만) 대비 3,228만 원↓ · 네이버 송스8 호가 중 최저(2026.11.26 대표님 확인) · 주변 소형 오피스텔보다 낮음",
            "**발행 직전**: 네이버 호가 최저가인지 한 번 더 확인 (다른 매물이 내려오면 문구 수정)",
            "**블러 처리**: 보일러 호수 손글씨·시리얼, 엘리베이터 개인 연락처 스티커, 출입하는 사람 — 우편함(호수 전체 노출)·거울에 얼굴 비친 욕실 사진은 뺐어요",
            "**사진 18장 순서**: 전경 → 출입구 → 골목 → 현관 → 주방 → 창·뷰 → 에어컨·TV → 세탁기 → 수납 → 욕실 → 보일러 → 복도 → 엘리베이터 → (체크 섹션) 공용 세탁실",
            "**공용 세탁실 사진**: 건조기 '고장' 안내가 보여요 — 솔직해서 좋지만, 빼고 싶으면 6번 섹션 4번 항목과 사진만 지우면 돼요"]
    return a, side


SERIES = {
    **{k: "【마포·서대문 아파트】" for k in ("2026-12-mapo-prestige-xi", "2026-12-mapo-gran-xi", "2026-11-hillstate-mapo-the-first", "2026-11-the-classy", "2026-11-maraepu", "2026-11-mapo-xi-hillstate-lachels", "2026-11-daeheung-apt")},
    "2026-11-raemian-lagrande": "【착한언니 사는 동네】",
    "2026-11-imun-ipark-xi": "【동대문 아파트】",
    **{k: "【신촌·이대 오피스텔】" for k in ("2026-11-shinchon-zaiella", "2026-11-sinchon-room-guide", "2026-11-officetel-standard-price", "2026-11-sinchon2-2-officetel", "2026-11-songs8-officetel")},
    **{k: "【재개발 현장】" for k in ("2026-11-nogosan-redevelopment", "2026-11-ahyeon1-nogosan", "2026-11-imun-hwigyeong-newtown", "2026-11-bukahyeon2-relocation",
                                   "2026-11-define-yeonhui", "2026-11-swiss-grand-hotel", "2026-11-sillim")},
    "2026-11-gyeonghuigung-epit": "【청약·분양】",
    **{k: "【착한언니 체크】" for k in ("2026-11-jaechohwan", "2026-11-jongbuse-notice", "2026-11-jeonse-fraud-minimum", "2026-11-registry-fee",
                                    "2026-11-public-redevelopment-fee")},
    "2026-11-deal-story-template": "【거래 후기】",
}
BASE_TAGS = {
    "zaiella": ["신촌부동산", "이대부동산", "신촌공인중개사", "서대문부동산", "신촌자이엘라부동산", "대현동부동산"],
    "grandxi": ["마포부동산", "마포공인중개사", "대흥동부동산", "공덕부동산", "마포그랑자이부동산", "마포구아파트"],
}


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    drafts = []
    for fn in (the_classy, lagrande, maraepu, zaiella, sillim, min_guarantee, jaechohwan,
               jongbuse, officetel_price, sinchon_room, lachels, bukahyeon2, imun_newtown, deal_story, public_redev_fee, registry_fee, swiss_grand, ahyeon_nogosan, nogosan, sinchon22_officetel, daeheung, gyeonghuigung_epit, define_yeonhui, imun_ipark_xi, hillstate_mapo, mapo_grancio, mapo_prestige_xi, songs8):
        post, side = fn()
        ser = SERIES.get(post.slug, "")
        side = list(side)
        for i, x in enumerate(side):
            if ser and (x.startswith("**제목(BEST)**:") or x.startswith("**제목(대안)**:")):
                k, v = x.split(":", 1)
                v = v.strip()
                if not v.startswith("【"):
                    side[i] = f"{k}: {ser} {v}"
            if x.startswith("**태그**:"):
                tg = [t.strip() for t in x.split(":", 1)[1].split(",") if t.strip()]
                for t in BASE_TAGS.get(getattr(post, "office", ""), []):
                    if len(tg) >= 15:
                        break
                    if t not in tg:
                        tg.insert(-1 if tg and tg[-1] == "착한언니복덕방" else len(tg), t)
                side[i] = "**태그**: " + ", ".join(tg)
        if ser:
            side.insert(0, f"**시리즈**: {ser} — 제목 맨 앞에 그대로 붙여요")
        path = os.path.join(OUT, post.slug + ".html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(post.render(side))
        print("생성:", os.path.relpath(path))
        import re as _r
        best = next((_r.sub(r"\*\*제목\(BEST\)\*\*:\s*", "", x) for x in side if x.startswith("**제목(BEST)")), post.title)
        tags = next((_r.sub(r"\*\*태그\*\*:\s*", "", x) for x in side if x.startswith("**태그**")), "")
        drafts.append({"slug": post.slug, "title": post.title, "best": best, "tags": tags,
                       "office": {"zaiella": "자이엘라", "grandxi": "그랑자이"}.get(getattr(post, "office", ""), ""),
                       "file": "naver/paste/" + post.slug + ".html",
                       "images": len(getattr(post, "images", [])),
                       "photos": [d for _, d in getattr(post, "todo_photos", [])],
                       "fills": sum(1 for b in post.b if b[0] == "fill"),
                       "series": ser, "note_todo": bool(getattr(post, "note_todo", False)) or any(b[0] == "fill" and "현장 노트" in b[1] for b in post.b)})
    import json as _j
    lib = os.path.join(OUT, "..", "library")
    os.makedirs(lib, exist_ok=True)
    with open(os.path.join(lib, "drafts.json"), "w", encoding="utf-8") as f:
        _j.dump(drafts, f, ensure_ascii=False, indent=1)
    print("목록:", len(drafts), "편 → naver/library/drafts.json")
