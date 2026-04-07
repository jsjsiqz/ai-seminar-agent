"""
config.py — 전체 프로젝트 설정
검색 쿼리·키워드 필터·출력 경로를 이 파일에서만 수정하세요.
"""

from pathlib import Path

# ── 출력 경로 ──────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).parent.parent / "ai_info_results"

# ── 크롤링 설정 ────────────────────────────────────────────────
SEARCH_RESULTS_PER_QUERY = 5      # 쿼리당 수집할 URL 수
REQUEST_DELAY_SEC = 2.0           # 요청 간 대기 (Google 차단 방지)
REQUEST_TIMEOUT_SEC = 8           # 페이지 로딩 타임아웃
MIN_TEXT_LENGTH = 200             # 본문 최소 길이 (너무 짧으면 스킵)
MAX_TEXT_LENGTH = 3000            # 파싱에 넘길 본문 최대 길이

# ── 관련성 필터 키워드 ─────────────────────────────────────────
# 페이지 본문에 아래 키워드 중 하나라도 있어야 수집합니다.
RELEVANCE_KEYWORDS = [
    "AI", "인공지능", "머신러닝", "딥러닝", "machine learning", "deep learning",
    "LLM", "MLOps", "RAG", "파인튜닝", "fine-tuning", "transformer",
    "세미나", "컨퍼런스", "conference", "seminar", "workshop", "강의", "course",
    "Udemy", "Coursera", "NeurIPS", "ICML", "ICLR", "DEVIEW",
]

# ── 수집 카테고리 & 검색 쿼리 ─────────────────────────────────
SEARCH_CATEGORIES = [
    {
        "id": "domestic_seminar",
        "label": "🇰🇷 국내 AI 세미나 / 컨퍼런스",
        "queries": [
            "2025 AI 머신러닝 딥러닝 컨퍼런스 세미나 한국 일정",
            "2025 MLOps AI 엔지니어 국내 컨퍼런스 신청",
            "DEVIEW NDC AI 세미나 2025 일정",
        ],
        "relevance_tag": "AI엔지니어/국내컨퍼런스",
    },
    {
        "id": "global_seminar",
        "label": "🌏 해외 AI 세미나 / 컨퍼런스",
        "queries": [
            "NeurIPS ICML ICLR 2025 conference registration",
            "AI ML engineering conference 2025 schedule",
            "MLOps LLM summit conference 2025",
        ],
        "relevance_tag": "AI엔지니어/해외컨퍼런스",
    },
    {
        "id": "online_course",
        "label": "💻 온라인 강의 (Udemy / Coursera 등)",
        "queries": [
            "best AI MLOps LLM engineering courses Udemy Coursera 2025",
            "LangChain RAG vector database online course 2025",
            "딥러닝 LLM 파인튜닝 온라인 강의 추천 2025",
        ],
        "relevance_tag": "딥러닝/LLM/온라인강의",
    },
    {
        "id": "academic_workshop",
        "label": "🎓 대학원 특강 / 워크숍",
        "queries": [
            "AI 대학원 특강 워크숍 2025 한국 등록",
            "카이스트 포스텍 서울대 AI 특강 세미나 2025",
            "AI winter school summer school 2025 Korea",
        ],
        "relevance_tag": "AI엔지니어/워크숍/대학원",
    },
]
