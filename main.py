"""
main.py — AI 세미나/강의 정보 수집 에이전트 (API 키 불필요)

실행:
    pip install -r requirements.txt
    cp .env.example .env       # NOTION_TOKEN, NOTION_DATABASE_ID 입력
    python main.py             # 크롤링 + Notion 업로드
    python main.py --skip-notion   # 크롤링 + 파일 저장만
    python main.py --notion-only   # 최근 JSON → Notion 재업로드
"""

import argparse
import json
import os
import sys
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.config import SEARCH_CATEGORIES
from src import crawler, parser, report, notion_client


def _banner(msg: str):
    bar = "=" * 54
    print(f"\n{bar}\n  {msg}\n{bar}")


def _check_env(*keys: str):
    missing = [k for k in keys if not os.getenv(k)]
    if missing:
        print(f"❌ 환경변수 누락: {', '.join(missing)}")
        print("   .env 파일을 확인하세요.")
        sys.exit(1)


def run_crawl_and_upload(skip_notion: bool):
    _banner("🤖 AI 세미나/강의 정보 수집 에이전트 (무료 크롤링)")
    print(f"  시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  카테고리: {len(SEARCH_CATEGORIES)}개  |  Anthropic API: 사용 안 함")

    all_pages = []
    for category in SEARCH_CATEGORIES:
        print(f"\n{'─' * 52}")
        print(f"  {category['label']}")
        print(f"{'─' * 52}")
        pages = crawler.crawl_category(category)
        all_pages.extend(pages)
        print(f"  ✅ {len(pages)}개 페이지 수집")

    _banner("🔍 구조화 파싱")
    flat = parser.parse_all(all_pages)
    print(f"  총 {len(flat)}건 파싱 완료")

    _banner("💾 파일 저장")
    report.save(flat)

    if not skip_notion:
        _check_env("NOTION_TOKEN", "NOTION_DATABASE_ID")
        notion_client.remove_expired()
        result = notion_client.upload(flat)
        notion_client.deduplicate_existing()
        if result["failed"] > 0:
            sys.exit(1)
    else:
        print("\n  --skip-notion 지정됨, Notion 업로드 건너뜀")

    _banner("📊 수집 결과 요약")
    from src.report import _group_by_category
    by_cat = _group_by_category(flat)
    for cat in SEARCH_CATEGORIES:
        count = len(by_cat.get(cat["id"], []))
        print(f"  {cat['label']}: {count}건")
    print(f"  {'─' * 46}")
    print(f"  총계: {len(flat)}건\n  완료! 🎉")


def run_notion_only():
    _check_env("NOTION_TOKEN", "NOTION_DATABASE_ID")
    _banner("📓 Notion 업로드 (크롤링 생략)")
    path = report.latest_json()
    if not path:
        print("❌ ai_info_results/ 에 JSON 파일이 없습니다.")
        sys.exit(1)
    items = json.loads(path.read_text(encoding="utf-8"))
    print(f"  파일: {path.name}  ({len(items)}건)")
    result = notion_client.upload(items)
    if result["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    parser_args = argparse.ArgumentParser(description="AI 세미나/강의 정보 수집 에이전트 (무료)")
    parser_args.add_argument("--skip-notion", action="store_true")
    parser_args.add_argument("--notion-only", action="store_true")
    parser_args.add_argument("--dedup", action="store_true", help="Notion DB 기존 중복 항목 제거")
    args = parser_args.parse_args()

    if args.dedup:
        _check_env("NOTION_TOKEN", "NOTION_DATABASE_ID")
        notion_client.deduplicate_existing()
    elif args.notion_only:
        run_notion_only()
    else:
        run_crawl_and_upload(skip_notion=args.skip_notion)
