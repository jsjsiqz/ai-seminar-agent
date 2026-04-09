"""
parser.py — 크롤링된 본문에서 이벤트/강의 정보를 규칙 기반으로 추출

API 없이 정규식 + 키워드 매칭으로 구조화된 데이터를 만듭니다.
"""

import re
from datetime import datetime, date
from src.crawler import PageResult


# ── 날짜 패턴 ─────────────────────────────────────────────────
_DATE_PATTERNS = [
    r"\d{4}[-./]\d{1,2}[-./]\d{1,2}",          # 2025-06-01
    r"\d{4}년\s*\d{1,2}월\s*\d{1,2}일",         # 2025년 6월 1일
    r"\d{1,2}/\d{1,2}/\d{4}",                   # 6/1/2025
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}",
    r"\d{4}년\s*\d{1,2}월",                      # 2025년 6월
]
_DATE_RE = re.compile("|".join(_DATE_PATTERNS), re.IGNORECASE)

# ── 가격 패턴 ─────────────────────────────────────────────────
_FREE_RE = re.compile(r"무료|free|₩\s*0|0\s*원", re.IGNORECASE)
_PAID_RE = re.compile(r"₩[\d,]+|[\d,]+원|\$[\d.]+|USD\s*[\d.]+|유료", re.IGNORECASE)

# ── 장소 패턴 ─────────────────────────────────────────────────
_ONLINE_RE = re.compile(r"온라인|online|zoom|webinar|virtual|비대면", re.IGNORECASE)
_VENUE_HINTS = ["서울", "강남", "코엑스", "잠실", "판교", "부산", "대전", "광주",
                "Seoul", "COEX", "Gangnam", "San Francisco", "New York", "London"]

# ── 타입 분류 키워드 ──────────────────────────────────────────
_TYPE_MAP = [
    (re.compile(r"컨퍼런스|conference|summit|symposium", re.I), "컨퍼런스"),
    (re.compile(r"워크숍|workshop", re.I), "워크숍"),
    (re.compile(r"특강|bootcamp|boot camp", re.I), "특강"),
    (re.compile(r"강의|course|강좌|lecture", re.I), "온라인강의"),
    (re.compile(r"세미나|seminar|meetup|밋업", re.I), "세미나"),
]

# ── 주최자 힌트 ───────────────────────────────────────────────
_ORGANIZER_HINTS = [
    "KAIST", "카이스트", "POSTECH", "포스텍", "서울대", "연세대", "고려대", "성균관대",
    "Naver", "네이버", "Kakao", "카카오", "Samsung", "삼성", "LG", "SK",
    "Google", "Microsoft", "AWS", "Meta", "Anthropic", "OpenAI",
    "Udemy", "Coursera", "fast.ai", "Hugging Face",
    "DEVIEW", "NDC", "NeurIPS", "ICML", "ICLR", "AAAI",
]


_MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _find_date(text: str) -> str:
    match = _DATE_RE.search(text)
    return match.group().strip() if match else "미정"


def _parse_date_to_obj(date_str: str) -> date | None:
    """날짜 문자열 → date 객체. 파싱 실패 시 None 반환."""
    s = date_str.strip()
    # 2026-04-10 / 2026.04.10 / 2026/04/10
    m = re.match(r"(\d{4})[-./](\d{1,2})[-./](\d{1,2})", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    # 2026년 4월 10일
    m = re.match(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    # 2026년 4월 (일 없으면 해당 월 1일로)
    m = re.match(r"(\d{4})년\s*(\d{1,2})월", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), 1)
    # April 10, 2026 / Apr 10 2026
    m = re.match(r"([A-Za-z]+)\.?\s+(\d{1,2}),?\s+(\d{4})", s)
    if m:
        mon = _MONTH_MAP.get(m.group(1).lower()[:3])
        if mon:
            return date(int(m.group(3)), mon, int(m.group(2)))
    # 6/1/2025
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        return date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
    return None


def _is_expired(date_str: str) -> bool:
    """날짜가 오늘 이전이면 True. 파싱 불가 / 미정이면 False."""
    if date_str in ("미정", "미확인"):
        return False
    d = _parse_date_to_obj(date_str)
    if d is None:
        return False
    return d < date.today()


def _find_price(text: str) -> str:
    if _FREE_RE.search(text):
        return "무료"
    if _PAID_RE.search(text):
        m = _PAID_RE.search(text)
        return m.group().strip() if m else "유료"
    return "미확인"


def _find_location(text: str) -> str:
    if _ONLINE_RE.search(text):
        return "온라인"
    for hint in _VENUE_HINTS:
        if hint in text:
            # hint 주변 문맥 30자 추출
            idx = text.index(hint)
            snippet = text[max(0, idx - 5): idx + 25].strip()
            return re.sub(r"\s+", " ", snippet)
    return "미확인"


def _find_type(text: str) -> str:
    for pattern, label in _TYPE_MAP:
        if pattern.search(text):
            return label
    return "세미나"  # 기본값


def _find_organizer(text: str) -> str:
    for hint in _ORGANIZER_HINTS:
        if hint.lower() in text.lower():
            return hint
    return "미확인"


def _make_summary(title: str, text: str) -> str:
    """제목 + 본문 앞부분으로 50자 요약 생성"""
    base = title if title else text[:80]
    base = re.sub(r"\s+", " ", base).strip()
    return base[:50]


def parse(page: PageResult) -> dict:
    """PageResult 한 건 → 구조화된 dict"""
    text = page.text
    event_date = _find_date(text)

    return {
        "title":          page.title[:100] if page.title else page.url,
        "type":           _find_type(text),
        "organizer":      _find_organizer(text),
        "date":           event_date,
        "location":       _find_location(text),
        "url":            page.url,
        "price":          _find_price(text),
        "summary":        _make_summary(page.title, text),
        "relevance":      page.relevance_tag,
        "category_id":    page.category_id,
        "category_label": page.category_label,
        "source_query":   page.query,
        "is_expired":     _is_expired(event_date) if page.category_id != "online_course" else False,
    }


def parse_all(pages: list[PageResult]) -> list[dict]:
    """중복 URL 제거 후 전체 파싱"""
    seen: set[str] = set()
    results = []
    for page in pages:
        if page.url not in seen:
            seen.add(page.url)
            results.append(parse(page))
    return results
