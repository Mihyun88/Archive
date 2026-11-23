#!/usr/bin/env python3
"""부동산 신문 스크랩 (무료 공개 RSS·기사 페이지만 사용, 개인 열람용)

사용: python3 -I tools/news_scrap.py [--hours 24] [--chars 350] [--out 파일.md]
      python3 -I tools/news_scrap.py --json 후보.json --add-to news/data.json
        → 후보.json: 기사별 본문 앞부분 포함 (요약 재료, 저장소에 올리지 않기)
        → news/data.json 오늘 날짜의 "all"(제목·언론사·시간·분류·링크만)을 채움
- 조선일보(경제 RSS 중 부동산 + 사설·칼럼), 한국경제(부동산 RSS + 오피니언),
  매일경제(부동산 RSS · 본문은 앞 2줄만 공개), 연합뉴스(경제 RSS 키워드)
- 본문은 앞부분만 잘라 보여 줌. 기사 전문·스크랩 결과는 저장소에 커밋하지 않기 (저작권).
"""
import argparse, html, re, sys, time, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

KST = timezone(timedelta(hours=9))
UA = {"User-Agent": "Mozilla/5.0 (compatible; news-scrap)"}
KW = re.compile(r"부동산|아파트|집값|전세|월세|전월세|주택|분양|청약|재건축|재개발|정비사업|종부세|양도세|보유세|취득세|"
                r"토지거래|토허|공시가|임대|오피스텔|LH|SH공사|주담대|주택담보|DSR|입주|매물|빌라|상가|PF|갭투자")
NS = {"content": "http://purl.org/rss/1.0/modules/content/", "dc": "http://purl.org/dc/elements/1.1/"}

# (언론사, RSS, 필터 방식, 칼럼 여부)
FEEDS = [
    ("조선일보", "https://www.chosun.com/arc/outboundfeeds/rss/category/economy/?outputType=xml", "url:/real_estate/", False),
    ("조선일보", "https://www.chosun.com/arc/outboundfeeds/rss/category/opinion/?outputType=xml", "kw", True),
    ("한국경제", "https://www.hankyung.com/feed/realestate", "all", False),
    ("한국경제", "https://www.hankyung.com/feed/opinion", "kw", True),
    ("매일경제", "https://www.mk.co.kr/rss/50300009/", "all", False),
    ("연합뉴스", "https://www.yna.co.kr/rss/economy.xml", "kw", False),
]

CATS = [
    ("📍 마포·서대문·동대문", r"마포|서대문|동대문|신촌|이대|아현|공덕|홍대|홍제|북아현|연희|청량리|이문|휘경|전농|답십리|용두|돈의문|경희궁"),
    ("📝 청약·분양", r"청약|분양|모집공고|당첨|특별공급|로또"),
    ("🏗️ 재건축·재개발", r"재건축|재개발|정비사업|정비구역|조합|시공사|수주|재초환|초과이익|통합심의|모아타운|신통기획"),
    ("💸 정책·세금·대출", r"세제|종부세|양도세|보유세|취득세|공시가|대출|DSR|주담대|금리|토지거래|토허|규제|국토부|국토교통부|금융위|조례|법안|정부"),
    ("🔑 전월세", r"전세|월세|임대차|임차|보증금|전세사기|HUG"),
    ("📊 시세·매물", r"집값|매물|실거래|호가|상승|하락|거래량|시세|신고가|매매|아파트.*억"),
    ("🏠 공급·입주·공공주택", r"입주|공급|공공주택|임대주택|신도시|LH|철도|역세권|주거타운"),
    ("🏢 건설사·업계", r"건설|사장|부문|시공|엔지니어링|데이터센터|플랫폼|임직원"),
]


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            err = e
            time.sleep(2 ** i)
    print(f"  ! 불러오기 실패: {url} ({err})", file=sys.stderr)
    return ""


def clean(s):
    s = re.sub(r"(?is)<(script|style|figure|figcaption|table)[^>]*>.*?</\1>", " ", s or "")
    s = re.sub(r"(?i)<br\s*/?>|</p>", "\n", s)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    lines = [re.sub(r"[ \t ]+", " ", l).strip() for l in s.split("\n")]
    return "\n".join(l for l in lines if l)


def cut(text, n):
    text = re.sub(r"\s*\n\s*", " ", text).strip()
    text = re.sub(r"^\([^)]{2,20}=연합뉴스\)\s*\S+\s*기자\s*=\s*", "", text)
    if len(text) <= n:
        return text
    t = text[:n]
    m = max(t.rfind("다. "), t.rfind("다."))
    return (t[: m + 2] if m > n * 0.5 else t) + " …"


def hk_body(url):
    s = get(url)
    i = s.find('id="articletxt"')
    if i < 0:
        return ""
    start = s.find(">", i) + 1
    ends = [k for k in (s.find(m, start) for m in ("article-byline-wrap", "article-copyright", "ad-area-wrap")) if k > 0]
    return clean(s[start : min(ends) if ends else start + 20000])


def pdate(s):
    try:
        d = parsedate_to_datetime(s)
    except Exception:
        try:
            d = datetime.fromisoformat(s.strip())
        except Exception:
            return None
    return d if d.tzinfo else d.replace(tzinfo=KST)


def collect(hours, chars):
    since = datetime.now(KST) - timedelta(hours=hours)
    out, seen = [], set()
    for src, url, flt, opinion in FEEDS:
        xml = get(url)
        if not xml:
            continue
        try:
            root = ET.fromstring(xml)
        except ET.ParseError:
            print(f"  ! RSS 해석 실패: {url}", file=sys.stderr)
            continue
        for it in root.iter("item"):
            title = clean(it.findtext("title") or "").replace("\n", " ")
            link = (it.findtext("link") or "").strip()
            d = pdate(it.findtext("pubDate") or "")
            if not title or not link or link in seen or (d and d < since):
                continue
            if flt.startswith("url:") and flt[4:] not in link:
                continue
            if flt == "kw" and not KW.search(title):
                continue
            seen.add(link)
            author = (it.findtext("dc:creator", namespaces=NS) or it.findtext("author") or "").strip()
            body = clean(it.findtext("content:encoded", namespaces=NS) or "")
            if not body and src == "한국경제":
                body = hk_body(link)
            if not body:
                body = clean(it.findtext("description") or "")
            if src == "연합뉴스" and not KW.search(title + body[:200]):
                continue
            out.append(dict(src=src, title=title, link=link, date=d, author=author,
                            lead=cut(body, chars), opinion=opinion))
    return out


def categorize(a):
    if a["opinion"]:
        return "🗞️ 사설·칼럼"
    text = a["title"] + " " + a["lead"][:200]
    for name, pat in CATS:
        if re.search(pat, text):
            return name
    return "📰 기타"


def dedupe(items):
    """제목이 거의 같은 기사(같은 사안 여러 매체)는 첫 번째만 남기고 '같은 소식' 표시."""
    def key(t):
        return set(re.findall(r"[가-힣A-Za-z0-9]{2,}", t))
    kept = []
    for a in items:
        k = key(a["title"])
        for b in kept:
            kb = key(b["title"])
            if k and kb and len(k & kb) / min(len(k), len(kb)) >= 0.6:
                if a["src"] != b["src"]:
                    b.setdefault("also", []).append(a["src"])
                break
        else:
            kept.append(a)
    return kept


def render(items, hours):
    now = datetime.now(KST)
    order = ["📍 마포·서대문·동대문", "🗞️ 사설·칼럼", "💸 정책·세금·대출", "🏗️ 재건축·재개발",
             "📝 청약·분양", "🔑 전월세", "📊 시세·매물", "🏠 공급·입주·공공주택", "🏢 건설사·업계", "📰 기타"]
    groups = {}
    for a in items:
        groups.setdefault(categorize(a), []).append(a)
    srcs = sorted({a["src"] for a in items})
    L = [f"# 부동산 신문 스크랩 {now:%Y.%m.%d (%a)} {now:%H:%M}",
         f"최근 {hours}시간 · {len(items)}건 · {', '.join(srcs)}", ""]
    for g in order:
        if g not in groups:
            continue
        L.append(f"## {g} ({len(groups[g])})")
        for a in sorted(groups[g], key=lambda x: x["date"] or now, reverse=True):
            when = f"{a['date'].astimezone(KST):%m/%d %H:%M}" if a["date"] else ""
            by = f" · {a['author']}" if a["author"] and a["author"] not in (a["src"],) else ""
            also = f" (같은 소식: {', '.join(sorted(set(a['also'])))})" if a.get("also") else ""
            L.append(f"### {a['title']}")
            L.append(f"{a['src']} {when}{by}{also}")
            if a["lead"]:
                L.append(f"> {a['lead']}")
            L.append(f"🔗 {a['link']}")
            L.append("")
    if not items:
        L.append("새 부동산 기사 없음")
    return "\n".join(L)


def to_json(items):
    import json
    rows = []
    for a in items:
        rows.append(dict(cat=categorize(a), title=a["title"], press=a["src"],
                         time=f"{a['date'].astimezone(KST):%m/%d %H:%M}" if a["date"] else "",
                         link=a["link"], also=sorted(set(a.get("also", []))), lead=a["lead"]))
    return rows


def add_to_page(rows, path):
    """news/data.json 의 오늘 날짜 항목에 all(본문 없이 제목·링크만)을 넣는다. items(요약 카드)는 건드리지 않음."""
    import json
    today = datetime.now(KST).strftime("%Y-%m-%d")
    data = json.load(open(path, encoding="utf-8"))
    day = next((d for d in data["days"] if d["date"] == today), None)
    if day is None:
        day = {"date": today, "source": "", "items": []}
        data["days"].insert(0, day)
    day["all"] = [{k: r[k] for k in ("cat", "title", "press", "time", "link", "also")} for r in rows]
    cutoff = (datetime.now(KST) - timedelta(days=60)).strftime("%Y-%m-%d")
    data["days"] = sorted([d for d in data["days"] if d["date"] >= cutoff], key=lambda d: d["date"], reverse=True)
    data["updated"] = today
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--chars", type=int, default=350, help="기사당 본문 앞부분 글자 수")
    ap.add_argument("--out")
    ap.add_argument("--json", help="후보 기사 JSON 저장 경로 (본문 앞부분 포함)")
    ap.add_argument("--add-to", help="news/data.json 경로: 오늘 날짜의 전체 기사 목록(all) 갱신")
    o = ap.parse_args()
    items = dedupe(collect(o.hours, o.chars))
    if o.json or o.add_to:
        import json
        rows = to_json(items)
        if o.json:
            json.dump(rows, open(o.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        if o.add_to:
            add_to_page(rows, o.add_to)
        print(f"기사 {len(rows)}건" + (f" → {o.json}" if o.json else "") + (f" · {o.add_to} 갱신" if o.add_to else ""))
        sys.exit(0)
    md = render(items, o.hours)
    if o.out:
        open(o.out, "w", encoding="utf-8").write(md)
    print(md)
