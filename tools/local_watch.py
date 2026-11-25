#!/usr/bin/env python3
"""우리 동네 단지·경매 워치 — 네이버 뉴스 검색(최신순)으로 마포·서대문 핵심 단지와 경매 기사를 모은다.

  python3 -I tools/local_watch.py          # 새 기사만 출력 + data/localwatch/seen.json 갱신
  python3 -I tools/local_watch.py --all    # 이미 본 기사도 출력 (저장 안 함)

- 법원경매(courtauction.go.kr) 물건 검색은 이 환경에서 응답이 끊김 → 경매 기사(뉴스)로 대체.
  실제 물건·감정가·최저가는 대표님 앱/법원경매 사이트에서 확인 후 글에 사용.
- 기사 문장은 옮기지 않는다. 제목·링크만 모아 콘텐츠 후보 판단용으로 쓴다.
"""
import html, json, os, re, sys, urllib.parse, urllib.request

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "localwatch")
SEEN = os.path.join(BASE, "seen.json")

# (검색어, 묶음) — 단지명은 기사에서 쓰는 표기 기준
QUERIES = [
    ("마포 아파트 경매", "경매"), ("서대문 아파트 경매", "경매"), ("마포구 경매 낙찰", "경매"),
    ("서울서부지법 경매 아파트", "경매"), ("마포 경매 감정가", "경매"),
    ("마포래미안푸르지오", "단지"), ("마포프레스티지자이", "단지"), ("마포그랑자이", "단지"),
    ("마포 더클래시", "단지"), ("공덕자이", "단지"), ("마포태영", "단지"),
    ("힐스테이트마포더퍼스트", "단지"), ("마포자이", "단지"), ("신촌그랑자이", "단지"),
    ("신촌자이엘라", "단지"), ("래미안 라그란데", "단지"), ("이문아이파크자이", "단지"),
    ("마포 재개발", "정비"), ("신촌 재개발", "정비"), ("아현 재건축", "정비"),
]
# 마포·서대문과 무관한 기사를 거르는 단어 (경매 검색용)
LOCAL = re.compile(r"마포|서대문|신촌|아현|공덕|염리|대흥|노고산|창전|신수|망원|합정|상암|북아현|이문")
SKIP = re.compile(r"미술|그림|경매장|옥션|와인|명품|자동차 경매|중고차")


def fetch(q):
    url = "https://search.naver.com/search.naver?" + urllib.parse.urlencode(
        {"where": "news", "query": q, "sort": "1", "pd": "1"})  # 최신순 · 최근 1주 (seen.json 으로 중복 제거)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    t = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
    out = []
    for m in re.finditer(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>', t, re.S):
        link, title = m.group(1), html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        title = title.replace("새 창 열림", "").strip()
        if not (12 < len(title) < 120) or "naver.com" in link or "keep" in link:
            continue
        ctx = html.unescape(re.sub(r"<[^>]+>", " ", t[m.end():m.end() + 1500]))
        out.append((title, link, re.sub(r"\s+", " ", ctx)[:300]))
    return out


def main():
    show_all = "--all" in sys.argv
    os.makedirs(BASE, exist_ok=True)
    try:
        seen = set(json.load(open(SEEN, encoding="utf-8")))
    except FileNotFoundError:
        seen = set()
    new, got = {}, set()
    for q, group in QUERIES:
        key = q.replace("마포 ", "") if group == "단지" else q
        try:
            items = fetch(q)
        except Exception as e:  # 한 검색어 실패해도 계속
            print(f"! {q}: {e}", file=sys.stderr)
            continue
        for title, link, ctx in items:
            text = title + " " + ctx
            if SKIP.search(title):
                continue
            if group == "경매" and not ("경매" in text and LOCAL.search(text)):
                continue
            if group == "단지" and key.replace(" ", "") not in text.replace(" ", ""):
                continue
            if group == "정비" and not LOCAL.search(title):
                continue
            if link in got or (link in seen and not show_all):
                continue
            got.add(link)
            new.setdefault(f"[{group}] {q}", []).append((title, link))
    for k, rows in new.items():
        print(f"\n## {k}")
        for title, link in rows[:6]:
            print(f"- {title} | {link}")
    if not new:
        print("새 기사 없음")
    if not show_all:
        json.dump(sorted(seen | got)[-3000:], open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=0)


if __name__ == "__main__":
    main()
