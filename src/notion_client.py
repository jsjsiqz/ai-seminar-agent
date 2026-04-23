"""
notion_client.py — Notion API 연동 (urllib 전용, 추가 설치 불필요)

필요 환경변수:
  NOTION_TOKEN       - Notion Integration 토큰 (secret_...)
  NOTION_DATABASE_ID - 업로드할 DB ID (32자리 hex)
"""

import json
import os
import re
import urllib.error
import urllib.request
from datetime import date, datetime, timezone


_API = "https://api.notion.com/v1"
_VER = "2022-06-28"

_MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _req(method: str, path: str, token: str, body: dict | None = None) -> dict:
    data = json.dumps(body, ensure_ascii=False).encode() if body else None
    req = urllib.request.Request(
        f"{_API}{path}", data=data, method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": _VER,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def _parse_date_str(s: str) -> date | None:
    """날짜 문자열 → date 객체. 파싱 실패 시 None."""
    s = s.strip()
    m = re.match(r"(\d{4})[-./](\d{1,2})[-./](\d{1,2})", s)
    if m:
        try: return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError: pass
    m = re.match(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", s)
    if m:
        try: return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError: pass
    m = re.match(r"(\d{4})년\s*(\d{1,2})월", s)
    if m:
        try: return date(int(m.group(1)), int(m.group(2)), 1)
        except ValueError: pass
    m = re.match(r"([A-Za-z]+)\.?\s+(\d{1,2}),?\s+(\d{4})", s)
    if m:
        mon = _MONTH_MAP.get(m.group(1).lower()[:3])
        if mon:
            try: return date(int(m.group(3)), mon, int(m.group(2)))
            except ValueError: pass
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        try: return date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        except ValueError: pass
    return None


def _norm_price(raw: str) -> str:
    p = (raw or "").lower()
    if any(k in p for k in ("무료", "free", "0원")):  return "무료"
    if any(k in p for k in ("유료", "$", "₩", "usd", "won")): return "유료"
    return "미확인"


def _build_props(item: dict) -> dict:
    price = _norm_price(item.get("price", ""))
    url   = item.get("url", "")
    tags  = [{"name": t.strip()}
             for t in item.get("relevance", "").replace("/", ",").split(",") if t.strip()]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    props: dict = {
        "":        {"title": [{"text": {"content": item.get("title", "제목 없음")[:100]}}]},
        "이름":    {"rich_text": [{"text": {"content": item.get("title", "제목 없음")[:100]}}]},
        "카테고리": {"rich_text": [{"text": {"content": item.get("category_label", "기타")[:100]}}]},
        "유형":    {"select": {"name": item.get("type", "미확인")[:100]}},
        "날짜":    {"rich_text": [{"text": {"content": item.get("date", "미확인")[:200]}}]},
        "가격":    {"select": {"name": price}},
        "수집일":  {"date": {"start": today}},
    }
    if url and url.startswith("http"):
        props["URL"] = {"url": url}
    if tags:
        props["태그"] = {"multi_select": tags}
    return props


def _build_page(item: dict, db_id: str) -> dict:
    page: dict = {"parent": {"database_id": db_id}, "properties": _build_props(item)}
    if s := item.get("summary"):
        page["children"] = [{"object": "block", "type": "paragraph",
                              "paragraph": {"rich_text": [{"type": "text",
                                            "text": {"content": s[:2000]}}]}}]
    return page


def _fetch_existing(token: str, db_id: str) -> tuple[dict[str, str], dict[tuple, str]]:
    """DB 전체 순회 → (url→page_id, (title,date)→page_id) 두 매핑 동시 반환."""
    by_url: dict[str, str] = {}
    by_title_date: dict[tuple, str] = {}
    body: dict = {"page_size": 100}
    while True:
        try:
            res = _req("POST", f"/databases/{db_id}/query", token, body)
        except Exception:
            break
        for page in res.get("results", []):
            pid = page["id"]
            props = page.get("properties", {})

            url_val = (props.get("URL", {}).get("url") or "").strip()
            if url_val:
                by_url[url_val] = pid

            title_list = props.get("", {}).get("title", [])
            title_val = (title_list[0].get("plain_text", "") if title_list else "").strip()[:100]

            date_rt = props.get("날짜", {}).get("rich_text", [])
            date_val = (date_rt[0].get("plain_text", "") if date_rt else "").strip()[:200]

            if title_val:
                by_title_date[(title_val, date_val)] = pid

        if not res.get("has_more"):
            break
        body["start_cursor"] = res["next_cursor"]
    return by_url, by_title_date


def remove_expired() -> int:
    """날짜가 오늘 이전인 페이지를 Notion DB에서 아카이브."""
    token = os.environ["NOTION_TOKEN"]
    db_id = os.environ["NOTION_DATABASE_ID"].replace("-", "")
    today = date.today()

    removed = 0
    body: dict = {"page_size": 100}
    print(f"\n  🗑️  만료 항목 정리 중...")
    while True:
        try:
            res = _req("POST", f"/databases/{db_id}/query", token, body)
        except Exception:
            break
        for page in res.get("results", []):
            pid = page["id"]
            props = page.get("properties", {})

            date_rt = props.get("날짜", {}).get("rich_text", [])
            date_val = (date_rt[0].get("plain_text", "") if date_rt else "").strip()

            if not date_val or date_val in ("미정", "미확인"):
                continue

            d = _parse_date_str(date_val)
            if d and d < today:
                title_list = props.get("", {}).get("title", [])
                title_val = (title_list[0].get("plain_text", "") if title_list else "?")[:50]
                try:
                    _req("PATCH", f"/pages/{pid}", token, {"archived": True})
                    removed += 1
                    print(f"  🗑️  만료 삭제: {title_val} ({date_val})")
                except Exception as e:
                    print(f"  ❌ 삭제 실패: {title_val} → {e}")

        if not res.get("has_more"):
            break
        body["start_cursor"] = res["next_cursor"]

    print(f"  → 만료 항목 총 {removed}건 삭제 완료")
    return removed


def upload(items: list[dict]) -> dict[str, int]:
    token = os.environ["NOTION_TOKEN"]
    db_id = os.environ["NOTION_DATABASE_ID"].replace("-", "")

    print(f"\n  📓 Notion 업로드 시작 (총 {len(items)}건)")
    by_url, by_title_date = _fetch_existing(token, db_id)
    print(f"  기존 DB 항목: {len(by_title_date)}건")

    added = updated = skipped = failed = 0
    for item in items:
        url   = item.get("url", "")
        title = item.get("title", "").strip()[:100]
        date_val = item.get("date", "").strip()[:200]
        props = _build_props(item)

        if url and url in by_url:
            # URL 일치 → 업데이트
            page_id = by_url[url]
            try:
                _req("PATCH", f"/pages/{page_id}", token, {"properties": props})
                updated += 1
                print(f"  🔄 수정: {title[:55]}")
            except urllib.error.HTTPError as e:
                print(f"  ❌ 수정 실패: {title[:45]} → {e.code}: {e.read().decode()[:150]}")
                failed += 1

        elif title and (title, date_val) in by_title_date:
            # 제목+날짜 일치 → 중복 스킵
            skipped += 1
            print(f"  ⏭️  중복 스킵: {title[:55]} ({date_val})")

        else:
            # 신규 추가
            try:
                _req("POST", "/pages", token, _build_page(item, db_id))
                if url:
                    by_url[url] = ""
                by_title_date[(title, date_val)] = ""
                added += 1
                print(f"  ✅ 추가: {title[:55]}")
            except urllib.error.HTTPError as e:
                print(f"  ❌ 추가 실패: {title[:45]} → {e.code}: {e.read().decode()[:150]}")
                failed += 1

    print(f"\n  결과: 추가 {added}건 / 수정 {updated}건 / 중복스킵 {skipped}건 / 실패 {failed}건")
    return {"added": added, "updated": updated, "skipped": skipped, "failed": failed}
