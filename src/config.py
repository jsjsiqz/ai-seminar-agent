"""
config.py — 전체 프로젝트 설정
검색 쿼리·키워드 필터·출력 경로를 이 파일에서만 수정하세요.
"""

from datetime import datetime
from pathlib import Path

_NOW   = datetime.now()
_YEAR  = _NOW.year
_MONTH = _NOW.month
_DAY   = _NOW.day

# ── 출력 경로 ──────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).parent.parent / "ai_info_results"

# ── 크롤링 설정 ────────────────────────────────────────────────
SEARCH_RESULTS_PER_QUERY = 10     # 쿼리당 수집할 URL 수
REQUEST_DELAY_SEC = 1.5           # 요청 간 대기
REQUEST_TIMEOUT_SEC = 10          # 페이지 로딩 타임아웃
MIN_TEXT_LENGTH = 100             # 본문 최소 길이
MAX_TEXT_LENGTH = 3000            # 파싱에 넘길 본문 최대 길이

# ── AI 관련성 키워드 (하나 이상 포함 필수) ─────────────────────
RELEVANCE_KEYWORDS = [
    "AI", "인공지능", "머신러닝", "딥러닝", "machine learning", "deep learning",
    "LLM", "MLOps", "RAG", "파인튜닝", "fine-tuning", "transformer", "generative",
    "데이터사이언스", "data science", "neural", "GPT", "Claude", "Gemini",
    "Udemy", "Coursera", "NeurIPS", "ICML", "ICLR", "DEVIEW", "GDG", "TFUG",
]

# ── 이벤트 필수 키워드 (하나 이상 포함 필수 — 관련성 키워드와 AND 조건) ──
EVENT_REQUIRED_KEYWORDS = [
    "세미나", "컨퍼런스", "conference", "seminar",
    "workshop", "워크숍", "밋업", "meetup",
    "강의", "course", "강좌", "lecture", "bootcamp", "부트캠프",
    "hackathon", "해커톤", "경진대회",
    "등록", "신청", "참가", "registration", "register", "apply",
    "특강", "행사", "이벤트", "event",
]

# ── 노이즈 도메인 블랙리스트 ──────────────────────────────────
SKIP_DOMAINS = {
    "facebook.com", "instagram.com", "twitter.com", "x.com",
    "linkedin.com", "naver.me", "youtube.com",
    # 금융/주식/코인
    "coindesk.com", "cointelegraph.com", "decrypt.co", "cryptonews.com",
    "investing.com", "marketwatch.com", "bloomberg.com", "reuters.com",
    "depositcoin.net", "thestreamingwars.tv", "parameter.io",
    "chromia.com", "theglobalhues.com",
}

# ── 수집 카테고리 & 검색 쿼리 ─────────────────────────────────
SEARCH_CATEGORIES = [
    {
        "id": "domestic_seminar",
        "label": "🇰🇷 국내 AI 세미나 / 컨퍼런스",
        "queries": [
            f"site:onoffmix.com AI 머신러닝 {_YEAR}",
            f"site:festa.io AI LLM 세미나 {_YEAR}",
            f"site:meetup.com AI 머신러닝 Seoul {_YEAR}",
            f"DEVIEW GDG TFUG AI 세미나 {_YEAR}년 {_MONTH}월 신청",
            f"AI LLM MLOps 컨퍼런스 한국 {_YEAR}년 {_MONTH}월 등록 참가",
        ],
        "relevance_tag": "AI엔지니어/국내컨퍼런스",
    },
    {
        "id": "global_seminar",
        "label": "🌏 해외 AI 세미나 / 컨퍼런스",
        "queries": [
            f"NeurIPS ICML ICLR {_YEAR} conference registration open",
            f"site:eventbrite.com AI machine learning conference {_YEAR}",
            f"site:meetup.com AI LLM workshop {_YEAR}",
            f"MLOps LLM GenAI summit conference {_YEAR} upcoming register",
            f"AI developer conference {_YEAR} {_MONTH:02d} call for participation",
        ],
        "relevance_tag": "AI엔지니어/해외컨퍼런스",
    },
    {
        "id": "online_course",
        "label": "💻 온라인 강의 (Udemy / Coursera 등)",
        "queries": [
            f"site:udemy.com AI LLM MLOps course {_YEAR}",
            f"site:coursera.org AI machine learning course {_YEAR}",
            f"LangChain RAG 온라인 강의 {_YEAR} 추천",
            f"AI agent LLM 파인튜닝 강좌 {_YEAR}",
            f"generative AI course free certificate {_YEAR}",
        ],
        "relevance_tag": "딥러닝/LLM/온라인강의",
    },
    {
        "id": "academic_workshop",
        "label": "🎓 대학원 특강 / 워크숍",
        "queries": [
            f"카이스트 포스텍 서울대 AI 특강 세미나 {_YEAR}년 {_MONTH}월 신청",
            f"AI winter school summer school {_YEAR} Korea 등록",
            f"AI 연구 워크숍 특강 {_YEAR}년 {_MONTH}월 참가",
            f"KAIST POSTECH AI workshop lecture {_YEAR}",
        ],
        "relevance_tag": "AI엔지니어/워크숍/대학원",
    },
    {
        "id": "hackathon",
        "label": "🏆 AI 해커톤 / 경진대회",
        "queries": [
            f"AI 해커톤 {_YEAR}년 {_MONTH}월 한국 신청 참가",
            f"site:dacon.io AI 경진대회 {_YEAR}",
            f"site:kaggle.com AI competition {_YEAR}",
            f"LLM AI hackathon {_YEAR} open registration",
        ],
        "relevance_tag": "AI엔지니어/해커톤",
    },
]
