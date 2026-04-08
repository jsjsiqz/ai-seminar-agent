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
MIN_TEXT_LENGTH = 100             # 본문 최소 길이 (완화)
MAX_TEXT_LENGTH = 3000            # 파싱에 넘길 본문 최대 길이

# ── 관련성 필터 키워드 ─────────────────────────────────────────
RELEVANCE_KEYWORDS = [
    "AI", "인공지능", "머신러닝", "딥러닝", "machine learning", "deep learning",
    "LLM", "MLOps", "RAG", "파인튜닝", "fine-tuning", "transformer", "generative",
    "세미나", "컨퍼런스", "conference", "seminar", "workshop", "강의", "course",
    "Udemy", "Coursera", "NeurIPS", "ICML", "ICLR", "DEVIEW", "GDG", "TFUG",
    "데이터사이언스", "data science", "neural", "GPT", "Claude", "Gemini",
    "hackathon", "해커톤", "bootcamp", "부트캠프",
]

# ── 수집 카테고리 & 검색 쿼리 ─────────────────────────────────
SEARCH_CATEGORIES = [
    {
        "id": "domestic_seminar",
        "label": "🇰🇷 국내 AI 세미나 / 컨퍼런스",
        "queries": [
            f"{_YEAR}년 {_MONTH}월 {_DAY}일 AI 머신러닝 딥러닝 컨퍼런스 세미나 한국",
            f"{_YEAR}년 {_MONTH}월 {_DAY}일 MLOps AI 엔지니어 국내 컨퍼런스 신청",
            f"DEVIEW NDC GDG AI 세미나 {_YEAR} 일정",
            f"{_YEAR} AI 개발자 컨퍼런스 한국 등록",
            f"{_YEAR}년 {_MONTH}월 {_DAY}일 AI LLM 밋업 한국",
        ],
        "relevance_tag": "AI엔지니어/국내컨퍼런스",
    },
    {
        "id": "global_seminar",
        "label": "🌏 해외 AI 세미나 / 컨퍼런스",
        "queries": [
            f"NeurIPS ICML ICLR {_YEAR} conference registration",
            f"AI ML engineering conference {_YEAR} {_MONTH:02d} {_DAY:02d} schedule",
            f"MLOps LLM GenAI summit conference {_YEAR}",
            f"AI developer conference {_YEAR} upcoming",
            f"machine learning workshop {_YEAR} call for participation",
        ],
        "relevance_tag": "AI엔지니어/해외컨퍼런스",
    },
    {
        "id": "online_course",
        "label": "💻 온라인 강의 (Udemy / Coursera 등)",
        "queries": [
            f"best AI MLOps LLM engineering courses Udemy Coursera {_YEAR}",
            f"LangChain RAG vector database online course {_YEAR}",
            f"딥러닝 LLM 파인튜닝 온라인 강의 추천 {_YEAR}",
            f"AI agent 개발 강의 {_YEAR}",
            f"generative AI course free {_YEAR}",
        ],
        "relevance_tag": "딥러닝/LLM/온라인강의",
    },
    {
        "id": "academic_workshop",
        "label": "🎓 대학원 특강 / 워크숍",
        "queries": [
            f"AI 대학원 특강 워크숍 {_YEAR} 한국 등록",
            f"카이스트 포스텍 서울대 AI 특강 세미나 {_YEAR}",
            f"AI winter school summer school {_YEAR} Korea",
            f"AI 연구 워크숍 {_YEAR}년 {_MONTH}월 {_DAY}일",
        ],
        "relevance_tag": "AI엔지니어/워크숍/대학원",
    },
    {
        "id": "hackathon",
        "label": "🏆 AI 해커톤 / 경진대회",
        "queries": [
            f"AI 해커톤 {_YEAR}년 {_MONTH}월 {_DAY}일 한국 참가",
            f"AI hackathon competition {_YEAR} open registration",
            f"LLM AI 경진대회 {_YEAR} 신청",
        ],
        "relevance_tag": "AI엔지니어/해커톤",
    },
]
