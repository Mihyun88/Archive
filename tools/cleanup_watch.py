"""서울시 정비사업 정보몽땅(cleanup.seoul.go.kr) 사업장 현황 수집 + 이전 스냅샷과 비교.

정비몽땅은 공개 API가 없어 '사업장 현황' 목록 화면(HTML)을 구별로 읽는다.
사용: python3 tools/cleanup_watch.py            # 마포·서대문·동대문
      python3 tools/cleanup_watch.py 11440 11410 # 구 코드 직접 지정
결과: data/cleanup/YYYY-MM-DD.json 저장, 직전 스냅샷 대비 단계 변화 출력
주의: 정비몽땅 단계는 자치구 고시보다 늦게 갱신될 수 있다 → 고시 원문과 교차 확인.
"""
import datetime, glob, html, json, os, re, sys, time, urllib.parse, urllib.request

GU = {"11440": "마포구", "11410": "서대문구", "11230": "동대문구"}
BASE = "https://cleanup.seoul.go.kr/cleanup/bsnssttus/lscrMainIndx.do?"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "cleanup")


def get(params):
    url = BASE + urllib.parse.urlencode(params)
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")
        except Exception:
            if i == 3:
                raise
            time.sleep(2 * (i + 1))


def rows(page):
    out = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        cells = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip()
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(cells) >= 6:
            out.append({"gu": cells[1], "type": cells[2], "name": cells[3],
                        "jibun": cells[4], "stage": cells[5]})
    return out


def collect(codes):
    data = []
    for code in codes:
        for p in range(1, 60):
            r = rows(get({"cpage": p, "pageSize": 10, "scupBsnsSttus.signguCode": code}))
            data += r
            if len(r) < 10:
                break
    return data


def main():
    codes = sys.argv[1:] or list(GU)
    today = datetime.date.today().isoformat()
    data = collect(codes)
    os.makedirs(OUT, exist_ok=True)
    prev_files = sorted(f for f in glob.glob(os.path.join(OUT, "*.json")) if not f.endswith(today + ".json"))
    with open(os.path.join(OUT, today + ".json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"수집 {len(data)}개 사업장 ({today})")
    if not prev_files:
        print("이전 스냅샷 없음 — 비교 생략")
        return
    prev = {(d["name"], d["jibun"]): d["stage"] for d in json.load(open(prev_files[-1], encoding="utf-8"))}
    cur = {(d["name"], d["jibun"]): d for d in data}
    changes = []
    for k, d in cur.items():
        if k not in prev:
            changes.append(f"🆕 [{d['gu']}] {d['name']} ({d['jibun']}) — {d['stage']}")
        elif prev[k] != d["stage"]:
            changes.append(f"🔁 [{d['gu']}] {d['name']} ({d['jibun']}) — {prev[k]} → {d['stage']}")
    for k in prev:
        if k not in cur:
            changes.append(f"❌ 목록에서 빠짐: {k[0]} ({k[1]})")
    print(f"직전 스냅샷 {os.path.basename(prev_files[-1])} 대비 변화 {len(changes)}건")
    print("\n".join(changes) or "변화 없음")


if __name__ == "__main__":
    main()
