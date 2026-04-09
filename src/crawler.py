"""
crawler.py — DuckDuckGo 검색 + 페이지 본문 크롤링 (API 키 불필요)

흐름:
  1. duckduckgo-search 로 검색 결과 URL 수집
  2. requests + BeautifulSoup 으로 각 페이지 본문 추출
  3. 관련성 키워드 필터링 후 반환
"""

import time
import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

from src.config import (
    SEARCH_RESULTS_PER_QUERY,
    REQUEST_DELAY_SEC,
    REQUEST_TIMEOUT_SEC,
    MIN_TEXT_LENGTH,
    MAX_TEXT_LENGTH,
    RELEVANCE_KEYWORDS,
    EVENT_REQUIRED_KEYWORDS,
    SKIP_DOMAINS,
)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}


@dataclass
class PageResult:
    url: str
    title: str
    text: str          # 정제된 본문 (MAX_TEXT_LENGTH 이하)
    query: str
    category_id: str
    category_label: str
    relevance_tag: str


def _is_skippable(url: str) -> bool:
    return any(d in url for d in SKIP_DOMAINS)


def _extract_text(html: str) -> tuple[str, str]:
    """HTML → (title, 본문 텍스트)"""
    soup = BeautifulSoup(html, "html.parser")

    # 노이즈 제거
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title else ""

    # 본문 우선순위: article > main > body
    body = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", {"id": re.compile(r"content|main", re.I)})
        or soup.body
    )
    raw = body.get_text(separator=" ", strip=True) if body else ""

    # 공백 정리
    text = re.sub(r"\s{2,}", " ", raw).strip()
    return title, text[:MAX_TEXT_LENGTH]


def _is_relevant(text: str) -> bool:
    text_lower = text.lower()
    has_ai = any(kw.lower() in text_lower for kw in RELEVANCE_KEYWORDS)
    has_event = any(kw.lower() in text_lower for kw in EVENT_REQUIRED_KEYWORDS)
    return has_ai and has_event


def crawl_category(category: dict) -> list[PageResult]:
    """
    카테고리의 모든 쿼리를 검색하고 관련 페이지 본문을 반환합니다.
    """
    results: list[PageResult] = []
    seen_urls: set[str] = set()

    for query in category["queries"]:
        print(f"    🔍 {query[:55]}...")

        try:
            with DDGS() as ddgs:
                hits = ddgs.text(query, max_results=SEARCH_RESULTS_PER_QUERY)
            urls = [h["href"] for h in hits if h.get("href")]
        except Exception as e:
            print(f"    ⚠️  DuckDuckGo 검색 오류: {e}")
            time.sleep(REQUEST_DELAY_SEC * 2)
            continue

        for url in urls:
            if url in seen_urls or _is_skippable(url):
                continue
            seen_urls.add(url)

            try:
                resp = requests.get(url, headers=_HEADERS, timeout=REQUEST_TIMEOUT_SEC)
                resp.raise_for_status()
                title, text = _extract_text(resp.text)

                if len(text) < MIN_TEXT_LENGTH or not _is_relevant(text):
                    continue

                results.append(PageResult(
                    url=url,
                    title=title,
                    text=text,
                    query=query,
                    category_id=category["id"],
                    category_label=category["label"],
                    relevance_tag=category["relevance_tag"],
                ))
                print(f"       ✓ {title[:50]}")

            except Exception:
                pass  # 접근 불가 페이지는 조용히 스킵

            time.sleep(REQUEST_DELAY_SEC)

    return results
