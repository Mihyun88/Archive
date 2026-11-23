#!/usr/bin/env python3
"""정책 추적 (news/tracks.json) — 같은 정책이 발의→통과→시행으로 바뀌는 흐름을 계속 쌓는다.

  python3 -I tools/news_track.py list                      # 추적 중인 정책 id·제목·현재 단계
  python3 -I tools/news_track.py add --id seoul-jungong-rental \
      --date 2026-11-23 --stage "조례 발의" --text "한 줄 요약" --link URL --press 한국경제 \
      [--title "새 추적이면 제목"] [--seoul] [--area 서울|전국|마포 …] [--close 시행|폐기|철회]

- 이미 있는 id면 이벤트만 추가(같은 날짜·같은 링크는 건너뜀), 없으면 새 추적을 만든다 (--title 필수).
- tracks.json 은 지우지 않는다 (data.json 의 60일 정리와 별개).
- 기사 문장을 옮기지 말고 우리 말 한 줄 요약 + 링크만 (저작권).
"""
import argparse, json, os, sys
from datetime import datetime, timedelta, timezone

PATH = os.path.join(os.path.dirname(__file__), "..", "news", "tracks.json")
KST = timezone(timedelta(hours=9))


def load():
    try:
        return json.load(open(PATH, encoding="utf-8"))
    except FileNotFoundError:
        return {"updated": "", "tracks": []}


def save(d):
    d["tracks"].sort(key=lambda t: t["events"][-1]["date"] if t["events"] else "", reverse=True)
    d["updated"] = datetime.now(KST).strftime("%Y-%m-%d")
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    a = sub.add_parser("add")
    a.add_argument("--id", required=True)
    a.add_argument("--date", default=datetime.now(KST).strftime("%Y-%m-%d"))
    a.add_argument("--stage", required=True)
    a.add_argument("--text", required=True)
    a.add_argument("--link", default="")
    a.add_argument("--press", default="")
    a.add_argument("--title")
    a.add_argument("--seoul", action="store_true")
    a.add_argument("--area", default="")
    a.add_argument("--topic", default="", help="세금|대출|정비사업|청약|임대차|공급|토지거래허가|기타")
    a.add_argument("--close", default="", help="흐름이 끝났으면: 시행|폐기|철회|완료")
    o = ap.parse_args()
    d = load()
    if o.cmd == "list":
        for t in d["tracks"]:
            last = t["events"][-1] if t["events"] else {}
            print(f"{t['id']:<34} {t.get('status','진행 중'):<6} {last.get('date','')} {last.get('stage','')} | {t['title']}")
        return
    t = next((x for x in d["tracks"] if x["id"] == o.id), None)
    if t is None:
        if not o.title:
            sys.exit(f"새 추적 '{o.id}' 은 --title 이 필요해요. 기존 id 확인: tools/news_track.py list")
        t = {"id": o.id, "title": o.title, "seoul": o.seoul, "area": o.area or ("서울" if o.seoul else "전국"),
             "topic": o.topic, "status": "진행 중", "events": []}
        d["tracks"].append(t)
    if any(e["date"] == o.date and (e.get("link") == o.link and o.link or e["text"] == o.text) for e in t["events"]):
        print("이미 있는 소식 — 건너뜀")
        return
    t["events"].append({"date": o.date, "stage": o.stage, "text": o.text, "link": o.link, "press": o.press})
    t["events"].sort(key=lambda e: e["date"])
    if o.seoul:
        t["seoul"] = True
    if o.topic:
        t["topic"] = o.topic
    if o.close:
        t["status"] = o.close
    save(d)
    print(f"{o.id}: {len(t['events'])}번째 소식 추가 ({o.stage})")


if __name__ == "__main__":
    main()
