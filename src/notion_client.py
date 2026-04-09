"""
notion_client.py — Notion API 연동 (urllib 전용, 추가 설치 불필요)

필요 환경변수:
  NOTION_TOKEN       - Notion Integration 토큰 (secret_...)
  NOTION_DATABASE_ID - 업로드할 DB ID (32자리 hex)
"""

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone


_API = "https://api.notion.com/v1"
_VER = "2022-06-28"


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


def _norm_price(raw: str) -> str:
    p = (raw or "").lower()
    if any(k in p for k in ("무료", "free", "0원")):  return "무료"
    if any(k in p for k in ("유료", "$", "₩", "usd", "won")): return "유료"
    return "미확인"


def _build_page(item: dict, db_id: str) -> dict:
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

    page: dict = {"parent": {"database_id": db_id}, "properties": props}
    if s := item.get("summary"):
        page["children"] = [{"object": "block", "type": "paragraph",
                              "paragraph": {"rich_text": [{"type": "text",
                                            "text": {"content": s[:2000]}}]}}]
    return page


def _existing_titles(token: str, db_id: str) -> set[str]:
    try:
        res = _req("POST", f"/databases/{db_id}/query", token,
                   {"page_size": 100,
                    "filter": {"timestamp": "created_time",
                               "created_time": {"past_week": {}}}})
        return {
            page["properties"]["이름"]["rich_text"][0]["plain_text"].strip()
            for page in res.get("results", [])
            if page["properties"].get("이름", {}).get("rich_text")
        }
    except Exception:
        return set()


def upload(items: list[dict]) -> dict[str, int]:
    token = os.environ["NOTION_TOKEN"]
    db_id = os.environ["NOTION_DATABASE_ID"].replace("-", "")

    print(f"\n  📓 Notion 업로드 시작 (총 {len(items)}건)")
    existing = _existing_titles(token, db_id)
    print(f"  기존 DB 항목(최근 1주): {len(existing)}건")

    added = skipped = failed = 0
    for item in items:
        title = item.get("title", "").strip()
        if title in existing:
            skipped += 1
            continue
        try:
            _req("POST", "/pages", token, _build_page(item, db_id))
            existing.add(title)
            added += 1
            print(f"  ✅ 추가: {title[:55]}")
        except urllib.error.HTTPError as e:
            print(f"  ❌ 실패: {title[:45]} → {e.code}: {e.read().decode()[:150]}")
            failed += 1

    print(f"\n  결과: 추가 {added}건 / 중복 {skipped}건 / 실패 {failed}건")
    return {"added": added, "skipped": skipped, "failed": failed}
