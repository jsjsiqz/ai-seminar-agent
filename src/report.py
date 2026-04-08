"""
report.py — 수집 결과를 마크다운 리포트와 JSON으로 저장합니다.
"""

import json
from datetime import datetime
from pathlib import Path

from src.config import OUTPUT_DIR, SEARCH_CATEGORIES


def _group_by_category(flat: list[dict]) -> dict[str, list]:
    result: dict[str, list] = {cat["id"]: [] for cat in SEARCH_CATEGORIES}
    for item in flat:
        cid = item.get("category_id", "")
        if cid in result:
            result[cid].append(item)
    return result


def _build_markdown(flat: list[dict]) -> str:
    by_cat = _group_by_category(flat)
    now = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
    total = len(flat)

    lines = [
        "# 🤖 AI 엔지니어 학습 기회 정보 리포트",
        f"\n> 수집 일시: {now}  |  총 {total}건",
        "\n---\n",
        "## 📋 목차\n",
    ]
    for cat in SEARCH_CATEGORIES:
        count = len(by_cat.get(cat["id"], []))
        lines.append(f"- {cat['label']} ({count}건)")

    lines.append("\n---\n")

    for cat in SEARCH_CATEGORIES:
        items = by_cat.get(cat["id"], [])
        lines.append(f"## {cat['label']}\n")
        if not items:
            lines.append("_이번 검색에서 수집된 정보가 없습니다._\n")
            continue

        for i, item in enumerate(items, 1):
            title = item.get("title", "제목 없음")
            url   = item.get("url", "")
            lines.append(f"### {i}. [{title}]({url})" if url else f"### {i}. {title}")
            lines.append("")
            for label, key in [
                ("유형", "type"), ("주최/플랫폼", "organizer"),
                ("일정", "date"), ("장소", "location"),
                ("가격", "price"), ("태그", "relevance"),
            ]:
                lines.append(f"- **{label}**: {item.get(key, '미확인')}")
            if s := item.get("summary"):
                lines.append(f"\n> {s}")
            lines.append("")

        lines.append("---\n")

    lines += [
        "_본 리포트는 Google 크롤링 기반으로 자동 수집된 정보입니다._",
        "_정확한 정보는 공식 링크를 통해 반드시 확인하세요._",
    ]
    return "\n".join(lines)


def save(flat: list[dict]) -> tuple[Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    md_path = OUTPUT_DIR / f"ai_info_{ts}.md"
    md_path.write_text(_build_markdown(flat), encoding="utf-8")

    json_path = OUTPUT_DIR / f"ai_info_{ts}.json"
    json_path.write_text(json.dumps(flat, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n  📄 마크다운: {md_path}")
    print(f"  📦 JSON:    {json_path}")
    return md_path, json_path


def latest_json() -> Path | None:
    files = sorted(OUTPUT_DIR.glob("ai_info_*.json"), reverse=True)
    return files[0] if files else None
