import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from PIL import Image
import math
import time
import uuid
import random

# ==============================================================================
# 0. 페이지 설정 & 무료 실시간 접속자 카운터 & 영구 채팅/닉네임 초기화
# ==============================================================================
st.set_page_config(
    page_title="구동현-TEX AI v4.0 | Ultimate Master Edition",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_active_sessions():
    return {}

@st.cache_resource
def get_global_chat_history():
    # 서버 메모리에 채팅 내역 영구 보존 (새로고침 시 초기화 방지)
    return []

def get_live_user_count():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    sessions = get_active_sessions()
    now = time.time()
    sessions[st.session_state.session_id] = now
    expired = [sid for sid, ts in sessions.items() if now - ts > 600]
    for sid in expired:
        del sessions[sid]
    return len(sessions)

live_users = get_live_user_count()

# 최초 접속 시 형용사 + 동물 랜덤 닉네임 부여 (이후 사용자가 직접 수정 가능)
if "user_nickname" not in st.session_state:
    adjectives = ["용감한", "재빠른", "꼼꼼한", "냉철한", "노련한", "열정적인", "날카로운", "든든한", "민첩한", "특급"]
    animals = ["호랑이", "사자", "독수리", "표범", "늑대", "상어", "매", "곰", "고슴도치", "판다"]
    st.session_state.user_nickname = f"{random.choice(adjectives)} {random.choice(animals)}"

global_chat_messages = get_global_chat_history()

# ==============================================================================
# 1. 전역 세션 상태 초기화 (전 공정 모듈 1 -> 6 원클릭 자동 동기화)
# ==============================================================================
defaults = {
    "fabric_name": "CVC 30s 싱글 스판 저지 (Single Span Jersey)",
    "pattern_type": "Single Jersey (1-Track All Knit)",
    "struct_mode": "싱글 저지 (표준 100% 침수)",
    "yarn_origin": "베트남/국내산 코마사 (표준 축률 · 정련감량 0%)",
    "rec_inch": 30,
    "rec_gauge": 28,
    "rec_feeds": 90,
    "rec_rpm": 22,
    "target_gsm": 185.0,
    "target_width": 60.0,
    "order_kg": 1200.0,
    "wpi": 38,
    "cpi": 52,
    "plating_factor": 0.70,
    # 5-사종 데이터
    "y1_name": "CVC 30s/1 (전면사 Face)", "y1_count": 30.0, "y1_unit": "Ne(면번수)", "y1_feeds": 90, "y1_sl": 2.82, "y1_price": 3.40, "y1_draft": 1.0, "y1_share": 100.0,
    "y2_name": "Cotton 20s/1 (이면사 Back)", "y2_count": 20.0, "y2_unit": "Ne(면번수)", "y2_feeds": 0, "y2_sl": 3.80, "y2_price": 3.10, "y2_draft": 1.0, "y2_share": 100.0,
    "y3_name": "CM 30s/1 (터크/결합사)", "y3_count": 30.0, "y3_unit": "Ne(면번수)", "y3_feeds": 0, "y3_sl": 2.15, "y3_price": 3.50, "y3_draft": 1.0, "y3_share": 100.0,
    "y4_name": "Spandex 20D (스판덱스 1)", "y4_count": 20.0, "y4_unit": "Denier(데니어)", "y4_feeds": 90, "y4_sl": 2.82, "y4_price": 6.80, "y4_draft": 3.1, "y4_share": 100.0,
    "y5_name": "Spandex 40D (스판덱스 2)", "y5_count": 40.0, "y5_unit": "Denier(데니어)", "y5_feeds": 0, "y5_sl": 2.82, "y5_price": 6.20, "y5_draft": 3.2, "y5_share": 100.0,
    # 공정 간 공유 연산 결과
    "calc_daily_kg": 248.0,
    "calc_yarn_cost_kg": 3.58,
    "calc_tf": 1.42,
    "calc_span_pct": 5.1,
    "silicone_g_l": 15.0,
    "kettle_cap": 500,
    "dye_path": "CVC/TC 2욕 분할 염색 (+$0.42/kg · +1.5일)",
    "w_shrink_Shared": 12.0,
    "l_shrink_Shared": 10.5
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

FACTORY_MACHINES = [
    {"id": "MC-01", "name": "30인치 28G 싱글기 (Mayer & Cie)", "gauge": 28, "inch": 30, "feeds": 90, "rpm": 22, "type": "Single"},
    {"id": "MC-02", "name": "34인치 28G 광폭 싱글기 (Santoni)", "gauge": 28, "inch": 34, "feeds": 102, "rpm": 20, "type": "Single"},
    {"id": "MC-03", "name": "30인치 24G 양면/인터록/립기 (Terrot)", "gauge": 24, "inch": 30, "feeds": 84, "rpm": 18, "type": "Double"},
    {"id": "MC-04", "name": "30인치 20G 3단 쭈리기 (Pai Lung)", "gauge": 20, "inch": 30, "feeds": 60, "rpm": 16, "type": "Fleece"},
    {"id": "MC-05", "name": "32인치 32G 하이게이지 양면기", "gauge": 32, "inch": 32, "feeds": 96, "rpm": 20, "type": "Double"},
]

# ==============================================================================
# 2. 초고시인성 CSS (배경 위 모든 글씨 순백색 #FFFFFF / 입력창·드롭다운 내부만 #000000)
# ==============================================================================
st.markdown("""
<style>
    /* 전체 배경 및 기본 텍스트 순백색 강제 */
    .stApp { background-color: #090D16 !important; color: #FFFFFF !important; }
    
    /* 사이드바 배경 및 텍스트 순백색 */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #FFFFFF !important;
    }

    /* 본문 내 모든 제목, 라벨, 캡션, 메트릭 값 순백색(#FFFFFF) 강제 고정 (흐릿함 완전 제거) */
    h1, h2, h3, h4, h5, h6, p, label,
    .stMarkdown, .stCaption, small,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span,
    [data-testid="stMetricLabel"] *,
    [data-testid="stMetricValue"] *,
    [data-testid="stMetricDelta"] *,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span {
        color: #FFFFFF !important;
        opacity: 1.0 !important;
    }

    /* 네비게이션 라디오 버튼 스타일링 */
    div[role="radiogroup"] > label {
        background: rgba(30, 41, 59, 0.85) !important;
        padding: 12px 15px !important;
        border-radius: 12px !important;
        margin-bottom: 8px !important;
        border: 1px solid #334155 !important;
        transition: all 0.2s ease;
    }
    div[role="radiogroup"] > label:hover {
        border-color: #00F2FE !important;
        background: rgba(15, 23, 42, 1.0) !important;
        transform: translateX(3px);
    }
    div[role="radiogroup"] > label * {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* 🔥 [핵심] 모든 흰색 입력창(Input, Number, Textarea) 내부 글씨는 선명한 검은색(#000000) */
    input, textarea, [data-baseweb="input"] input, [data-baseweb="base-input"] input {
        color: #000000 !important;
        background-color: #FFFFFF !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 700 !important;
    }
    input::placeholder, textarea::placeholder {
        color: #64748B !important;
        -webkit-text-fill-color: #64748B !important;
    }
    /* 숫자 입력창 우측 +/- 버튼 아이콘 검은색 */
    [data-testid="stNumberInput"] button {
        color: #000000 !important;
        background-color: #F1F5F9 !important;
    }
    [data-testid="stNumberInput"] button svg {
        fill: #000000 !important;
    }

    /* 🔥 [핵심] 셀렉트박스(드롭다운) 본체 및 팝업 메뉴 리스트 글씨 검은색(#000000) 강제 */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    div[data-baseweb="select"] *,
    div[data-baseweb="popover"] *,
    ul[data-baseweb="menu"] *,
    li[role="option"] *,
    div[role="listbox"] * {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 600 !important;
    }
    div[data-baseweb="select"] svg {
        fill: #000000 !important;
    }

    /* 🔥 [핵심] 파일 업로더 박스 & 내부 Upload/Browse 버튼 가시성 완벽 교정 */
    [data-testid="stFileUploader"] section {
        background-color: #1E293B !important;
        border: 2px dashed #38BDF8 !important;
        border-radius: 12px !important;
        padding: 16px !important;
    }
    [data-testid="stFileUploader"] section > div,
    [data-testid="stFileUploader"] section span,
    [data-testid="stFileUploader"] section small {
        color: #FFFFFF !important;
    }
    [data-testid="stFileUploader"] section button {
        background-color: #00F2FE !important;
        color: #000000 !important;
        border: none !important;
        font-weight: 800 !important;
    }
    [data-testid="stFileUploader"] section button * {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 800 !important;
    }

    /* 사이드바 폼 전송 버튼 및 일반 버튼 가시성 보장 */
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF6B6B 100%) !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        border: none !important;
    }
    .stButton > button[kind="primary"] * {
        color: #FFFFFF !important;
    }
    [data-testid="stFormSubmitButton"] > button {
        background-color: #38BDF8 !important;
        color: #000000 !important;
        font-weight: 800 !important;
        border: none !important;
    }
    [data-testid="stFormSubmitButton"] > button * {
        color: #000000 !important;
        font-weight: 800 !important;
    }

    /* 카드 및 배지 디자인 */
    .hero-card {
        background: linear-gradient(135deg, rgba(15,23,42,0.96) 0%, rgba(30,41,59,0.90) 100%);
        border: 1px solid rgba(0, 242, 254, 0.4);
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .glass-card {
        background: rgba(17, 24, 39, 0.92);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        color: #FFFFFF !important;
    }
    .neon-title { color: #38BDF8 !important; font-weight: 800; font-size: 1.08rem; margin-bottom: 8px; }
    .live-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.2);
        border: 1px solid #10B981;
        color: #34D399 !important;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .notice-badge {
        display: inline-block;
        background: rgba(239, 68, 68, 0.2);
        border: 1px solid #EF4444;
        color: #FCA5A5 !important;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .demo-badge {
        display: inline-block;
        background: rgba(56, 189, 248, 0.2);
        border: 1px solid #38BDF8;
        color: #38BDF8 !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 800;
        vertical-align: middle;
        margin-left: 10px;
    }
    .structure-box {
        background: #0F172A;
        border: 1.5px solid #00F2FE;
        border-radius: 12px;
        padding: 16px 18px;
        margin-top: 8px;
        margin-bottom: 14px;
        color: #FFFFFF !important;
        line-height: 1.65;
    }
    .diagram-pre {
        background: #050811;
        border: 1px solid #334155;
        color: #00F2FE !important;
        padding: 10px 14px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 0.86rem;
        margin-top: 8px;
        white-space: pre-wrap;
        line-height: 1.45;
    }
    .yarn-summary-box {
        background: #0F172A;
        border-left: 4px solid #00F2FE;
        padding: 16px 20px;
        border-radius: 10px;
        font-size: 1.0rem;
        color: #FFFFFF !important;
        margin-top: 8px;
        line-height: 1.8;
    }
    .as-chat-box {
        background: #0B0F19;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 10px;
        max-height: 210px;
        overflow-y: auto;
        font-size: 0.84rem;
        margin-bottom: 8px;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. 원단 전문가용 8대 조직 마스터 DB & AI 픽셀 비전 자동 규정 엔진
# ==============================================================================
def to_tex(count_val, unit_str):
    if count_val <= 0:
        return 0.0
    return (590.5 / count_val) if "Ne" in unit_str else (count_val / 9.0)

STRUCTURE_DB = {
    "CVC 30s 싱글 스판 저지 (Single Span Jersey)": {
        "pattern": "Single Jersey (1-Track All Knit + Plating)",
        "struct": "싱글 저지 (표준 100% 침수)",
        "desc": "기본 1트랙 전 피더 니트 루프에 스판덱스를 전 피더 플레이팅 결합한 고신축 표준 싱글 조직",
        "inch": 30, "gauge": 28, "feeds": 90, "rpm": 22, "type": "Single", "needle_mult": 1.0,
        "wpi": 38, "cpi": 52, "sl": 2.82, "draft": 3.1,
        "cam": "Feed 1~90: All Knit (Single Cam) + Spandex Plating (보정계수 0.70)",
        "needle": "1-Track High Butt Needles (실린더 100% 가동)",
        "seq": "전 피더 CVC 30s/1 + Spandex 20D 전 피더 플레이팅",
        "diagram": "Course 1~N (All Feeds):  [ Ω Knit ] ── [ Ω Knit ] ── [ Ω Knit ] ── [ Ω Knit ]\nPlating Carrier (OP):    ( ─── Spandex 20D Full-Plating ─── )",
        "w_shrink": 12.0, "l_shrink": 10.5, "fee": 0.35, "span_pct": 5.1,
        "y1": ("CVC 30s/1 (전면사)", 30.0, "Ne(면번수)", 90, 2.82, 3.40, 1.0, 100.0),
        "y2": ("미사용 (이면사)", 20.0, "Ne(면번수)", 0, 3.50, 3.10, 1.0, 100.0),
        "y3": ("미사용 (터크사)", 30.0, "Ne(면번수)", 0, 2.00, 3.30, 1.0, 100.0),
        "y4": ("Spandex 20D (스판1)", 20.0, "Denier(데니어)", 90, 2.82, 6.80, 3.1, 100.0),
    },
    "Cotton 30s/20s 2단 터크 미니 쭈리 (French Terry)": {
        "pattern": "2-Thread French Terry (1-Knit / 1-Tuck Binding)",
        "struct": "싱글 변형 (표준 100% 침수)",
        "desc": "홀수 피더는 평니트(바닥), 짝수 피더는 1침 터크·1침 미스(Float)로 이면 파일 루프를 형성하는 미니 쭈리",
        "inch": 30, "gauge": 24, "feeds": 72, "rpm": 18, "type": "Fleece", "needle_mult": 1.0,
        "wpi": 30, "cpi": 40, "sl": 3.05, "draft": 3.0,
        "cam": "홀수 Feed: All Knit (Face) / 짝수 Feed: [1 Tuck - 1 Miss(Float)] 교차 배열",
        "needle": "2-Track (High/Low Butt 1:1 교차 배열 - 이면 인레이 루프 바인딩)",
        "seq": "홀수 피더: CM 30s + 20D OP / 짝수 피더: CM 20s 이면 루프사",
        "diagram": "Feed 1 (Face Knit):  [ Ω Knit ] ─── [ Ω Knit ] ─── [ Ω Knit ] ─── [ Ω Knit ]\nFeed 2 (Back Loop):  [ ∧ Tuck ] ─── ( ──Miss── ) ─── [ ∧ Tuck ] ─── ( ──Miss── )",
        "w_shrink": 14.5, "l_shrink": 13.0, "fee": 0.45, "span_pct": 3.8,
        "y1": ("CM 30s/1 (전면사)", 30.0, "Ne(면번수)", 36, 3.05, 3.60, 1.0, 100.0),
        "y2": ("CM 20s/1 (이면 루프사)", 20.0, "Ne(면번수)", 18, 4.20, 3.15, 1.0, 100.0),
        "y3": ("CM 30s/1 (터크 결합사)", 30.0, "Ne(면번수)", 18, 2.15, 3.60, 1.0, 100.0),
        "y4": ("Spandex 20D (스판1)", 20.0, "Denier(데니어)", 36, 3.05, 6.80, 3.0, 100.0),
    },
    "Cotton 20s/30s/10s 3단 헤비 쭈리 (3-Thread Heavy Fleece)": {
        "pattern": "3-Thread Fleece (Face Knit + Binder + Heavy Pile)",
        "struct": "싱글 변형 (표준 100% 침수)",
        "desc": "표면사(Face) + 중간 결합사(Binder) + 태번수 이면 루프사(Pile)가 3피더 1세트로 돌아가는 고중량 헤비 쭈리",
        "inch": 30, "gauge": 20, "feeds": 60, "rpm": 16, "type": "Fleece", "needle_mult": 1.0,
        "wpi": 26, "cpi": 36, "sl": 3.45, "draft": 1.0,
        "cam": "Feed 1: All Knit(Face) / Feed 2: Knit-Miss(Binder) / Feed 3: 1 Tuck - 2 Miss(Pile)",
        "needle": "4-Track (1-2-3-4 사선 바인딩 배열 - 표면 터크 비침 원천 차단)",
        "seq": "F1: CM 20s(표면) / F2: CVC 30s(결합) / F3: CD 10s(이면 헤비 파일)",
        "diagram": "Feed 1 (Face 20s):    [ Ω Knit ] ── [ Ω Knit ] ── [ Ω Knit ]\nFeed 2 (Binder 30s):  [ Ω Knit ] ── ( ──Miss── ) ── [ Ω Knit ]\nFeed 3 (Pile 10s):    [ ∧ Tuck ] ── ( ──Float── ) ── ( ──Float── )",
        "w_shrink": 15.5, "l_shrink": 14.0, "fee": 0.50, "span_pct": 0.0,
        "y1": ("CM 20s/1 (표면사 Face)", 20.0, "Ne(면번수)", 20, 3.45, 3.30, 1.0, 100.0),
        "y2": ("CD 10s/1 (이면 파일사)", 10.0, "Ne(면번수)", 20, 4.60, 2.75, 1.0, 100.0),
        "y3": ("CVC 30s/1 (중간 결합사)", 30.0, "Ne(면번수)", 20, 2.60, 3.40, 1.0, 100.0),
        "y4": ("미사용", 20.0, "Denier(데니어)", 0, 2.80, 6.80, 3.0, 100.0),
    },
    "CM 20s 12조 터크 와플 (12-Course Tuck Waffle)": {
        "pattern": "12-Course Thermal Waffle (Multi-Tuck Honeycomb)",
        "struct": "양면 인터록/1x1립 (200% 침수)",
        "desc": "다이얼과 실린더에서 12코스 주기로 교차 연속 터크(Tuck)를 걸어 깊은 사각 와플 격자 요철을 만드는 보온성 조직",
        "inch": 30, "gauge": 20, "feeds": 60, "rpm": 16, "type": "Double", "needle_mult": 1.8,
        "wpi": 28, "cpi": 42, "sl": 3.20, "draft": 1.0,
        "cam": "Course 1~5: 홀수침 연속 Tuck(요철 기둥) / Course 6: All Knit(수평 격자 마감) / Course 7~12: 짝수침 반전",
        "needle": "Dial 2-Track + Cylinder 2-Track (1x1 Rib Gating 기반 와플 세팅)",
        "seq": "전 피더 CM 20s/1 단독 급사 (연속 터크부 장력 15% 이완 필수)",
        "diagram": "Course 1~5 (Ridge):   [ Ω Knit ] ── [ ∧ Tuck x5 ] ── [ Ω Knit ]\nCourse 6 (Divider):   [ Ω Knit ] ── [ Ω All-Knit ] ── [ Ω Knit ]\nCourse 7~12 (Shift):  [ ∧ Tuck x5 ] ── [ Ω Knit ] ── [ ∧ Tuck x5 ]",
        "w_shrink": 17.5, "l_shrink": 15.5, "fee": 0.55, "span_pct": 0.0,
        "y1": ("CM 20s/1 (실린더 니트사)", 20.0, "Ne(면번수)", 30, 3.20, 3.35, 1.0, 100.0),
        "y2": ("CM 20s/1 (다이얼 니트사)", 20.0, "Ne(면번수)", 15, 3.20, 3.35, 1.0, 100.0),
        "y3": ("CM 20s/1 (12조 연속 터크사)", 20.0, "Ne(면번수)", 15, 2.75, 3.35, 1.0, 100.0),
        "y4": ("미사용", 20.0, "Denier(데니어)", 0, 2.80, 6.80, 3.0, 100.0),
    },
    "CVC 30s/Poly 75D 올터크 담보루 (All-Tuck Cardigan Cushion)": {
        "pattern": "Double Jersey All-Tuck (Full Cardigan / Polka Rib)",
        "struct": "양면 인터록/1x1립 (200% 침수)",
        "desc": "다이얼과 실린더 양면에서 매 코스 번갈아 올터크(All-Tuck)를 걸어 원단 내부에 공기층(쿠션감)과 볼륨을 극대화한 담보루 조직",
        "inch": 30, "gauge": 24, "feeds": 72, "rpm": 17, "type": "Double", "needle_mult": 2.0,
        "wpi": 30, "cpi": 38, "sl": 3.15, "draft": 1.0,
        "cam": "Feed 1: Cylinder All-Knit + Dial All-Tuck / Feed 2: Cylinder All-Tuck + Dial All-Knit",
        "needle": "Rib Gating 2-Track (양면 200% 침수 풀 가동 - 벌키성 극대화)",
        "seq": "홀수 피더: CVC 30s / 짝수 피더: Poly DTY 75D 에어쿠션 터크 급사",
        "diagram": "Feed 1 (Odd):   Cyl [ Ω Knit ] ── Dial [ ∧ All-Tuck ] ── Cyl [ Ω Knit ]\nFeed 2 (Even):  Cyl [ ∧ All-Tuck ] ── Dial [ Ω Knit ] ── Cyl [ ∧ All-Tuck ]",
        "w_shrink": 16.5, "l_shrink": 13.5, "fee": 0.52, "span_pct": 0.0,
        "y1": ("CVC 30s/1 (실린더 메인)", 30.0, "Ne(면번수)", 36, 3.15, 3.40, 1.0, 100.0),
        "y2": ("CVC 30s/1 (다이얼 메인)", 30.0, "Ne(면번수)", 18, 3.15, 3.40, 1.0, 100.0),
        "y3": ("Poly DTY 75D (올터크 볼륨사)", 75.0, "Denier(데니어)", 18, 2.90, 1.95, 1.0, 100.0),
        "y4": ("미사용", 20.0, "Denier(데니어)", 0, 2.80, 6.80, 3.0, 100.0),
    },
    "CM 20s 2x2 립 스판 (2x2 Rib Knit - 시보리/몸판)": {
        "pattern": "2x2 Rib (Needle-Out 66.7% Gating)",
        "struct": "2x2 립 (바늘 빼기 66.7% 가동)",
        "desc": "다이얼 2침·실린더 2침 교차 편성 및 1침 발침(Needle-out)으로 가로 방향 복원력과 골지 입체감을 극대화한 2x2 립",
        "inch": 30, "gauge": 18, "feeds": 60, "rpm": 17, "type": "Double", "needle_mult": 1.333,
        "wpi": 26, "cpi": 36, "sl": 3.25, "draft": 3.0,
        "cam": "Cylinder & Dial [2 Knit - 1 Needle Out] 동시 편성",
        "needle": "다이얼/실린더 각 2본 가동 + 1본 발침(Needle-out) ➔ 실가동 침수 66.7%",
        "seq": "전 피더 CM 20s/1 + Spandex 30D 플레이팅 급사",
        "diagram": "Dial Needles:      [ Ω Knit ][ Ω Knit ] ( ──Out── ) [ Ω Knit ][ Ω Knit ]\nCylinder Needles:  ( ──Out── ) [ Ω Knit ][ Ω Knit ] ( ──Out── )",
        "w_shrink": 18.0, "l_shrink": 11.0, "fee": 0.48, "span_pct": 4.9,
        "y1": ("CM 20s/1 (실린더/다이얼)", 20.0, "Ne(면번수)", 60, 3.25, 3.30, 1.0, 100.0),
        "y2": ("미사용", 20.0, "Ne(면번수)", 0, 3.00, 3.10, 1.0, 100.0),
        "y3": ("미사용", 20.0, "Ne(면번수)", 0, 2.00, 3.10, 1.0, 100.0),
        "y4": ("Spandex 30D (스판1)", 30.0, "Denier(데니어)", 60, 3.25, 6.50, 3.0, 100.0),
    },
    "CM 30s 싱글 피케 (Single Lacoste Pique)": {
        "pattern": "4-Track Single Pique (Knit + Staggered Tuck)",
        "struct": "싱글 변형 (표준 100% 침수)",
        "desc": "2코스 평니트 후 홀수침·짝수침 교차 터크(Tuck)로 표면에 다이아몬드 벌집 공극을 형성하는 폴로 피케 조직",
        "inch": 30, "gauge": 24, "feeds": 72, "rpm": 19, "type": "Single", "needle_mult": 1.0,
        "wpi": 32, "cpi": 44, "sl": 2.95, "draft": 1.0,
        "cam": "Feed 1,2: All Knit / Feed 3: 홀수침 Tuck / Feed 4: 짝수침 Tuck",
        "needle": "4-Track (1-2-1-2 벌집 요철 형성용 바늘 배열)",
        "seq": "전 피더 CM 30s/1 급사 (터크 피더 장력 -10% 이완 세팅)",
        "diagram": "Feed 1,2 (Base):   [ Ω Knit ] ── [ Ω Knit ] ── [ Ω Knit ] ── [ Ω Knit ]\nFeed 3 (Odd Tuck): [ ∧ Tuck ] ── [ Ω Knit ] ── [ ∧ Tuck ] ── [ Ω Knit ]\nFeed 4 (Even Tuck):[ Ω Knit ] ── [ ∧ Tuck ] ── [ Ω Knit ] ── [ ∧ Tuck ]",
        "w_shrink": 15.0, "l_shrink": 12.0, "fee": 0.42, "span_pct": 0.0,
        "y1": ("CM 30s/1 (니트 코어사)", 30.0, "Ne(면번수)", 36, 2.95, 3.60, 1.0, 100.0),
        "y2": ("미사용", 20.0, "Ne(면번수)", 0, 3.00, 3.10, 1.0, 100.0),
        "y3": ("CM 30s/1 (터크 요철사)", 30.0, "Ne(면번수)", 36, 2.45, 3.60, 1.0, 100.0),
        "y4": ("미사용", 20.0, "Denier(데니어)", 0, 2.80, 6.80, 3.0, 100.0),
    },
    "Poly 75D/Span 40D 고밀도 인터록 (Interlock 32G)": {
        "pattern": "1x1 Interlock (Double Jersey Cross Gating 200%)",
        "struct": "양면 인터록/1x1립 (200% 침수)",
        "desc": "다이얼과 실린더 장침·단침이 서로 마주 보며 1:1 교차 편성되어 앞뒷면이 모두 매끈하고 밀도가 극대화된 양면 인터록",
        "inch": 32, "gauge": 32, "feeds": 96, "rpm": 19, "type": "Double", "needle_mult": 2.0,
        "wpi": 46, "cpi": 62, "sl": 2.45, "draft": 3.2,
        "cam": "Cylinder & Dial 1:1 Cross Gating (Long/Short Needle 교차 구동)",
        "needle": "Dial 2-Track + Cylinder 2-Track (양면 200% 풀 침수 가동)",
        "seq": "전 피더 DTY 75D/72F + Spandex 40D 양면 동시 급사",
        "diagram": "Feed 1 (Long Needles):  Cyl [ Ω ] ── (Miss) ── Dial [ Ω ] ── (Miss)\nFeed 2 (Short Needles): (Miss) ── Cyl [ Ω ] ── (Miss) ── Dial [ Ω ]",
        "w_shrink": 9.0, "l_shrink": 8.0, "fee": 0.58, "span_pct": 8.4,
        "y1": ("Poly DTY 75D (실린더)", 75.0, "Denier(데니어)", 48, 2.45, 1.95, 1.0, 100.0),
        "y2": ("Poly DTY 75D (다이얼)", 75.0, "Denier(데니어)", 48, 2.45, 1.95, 1.0, 100.0),
        "y3": ("미사용 (터크사)", 75.0, "Denier(데니어)", 0, 2.00, 1.95, 1.0, 100.0),
        "y4": ("Spandex 40D (스판1)", 40.0, "Denier(데니어)", 96, 2.45, 6.20, 3.2, 100.0),
    }
}

def analyze_swatch_pixels_expert(front_img_file, back_img_file):
    """업로드된 앞/뒷면 스와치 픽셀의 가로/세로 주파수, 명암비, 다공도를 분석하여 8대 조직 중 하나로 자동 규정"""
    try:
        img_f = Image.open(front_img_file).convert("L").resize((256, 256))
        arr_f = np.array(img_f, dtype=np.float32)
        contrast = float(np.std(arr_f))
        grad_x = float(np.mean(np.abs(np.diff(arr_f, axis=1))))
        grad_y = float(np.mean(np.abs(np.diff(arr_f, axis=0))))
        porosity = float(np.mean((arr_f < 45) | (arr_f > 215)) * 100.0)

        back_diff = 0.0
        if back_img_file is not None:
            img_b = Image.open(back_img_file).convert("L").resize((256, 256))
            arr_b = np.array(img_b, dtype=np.float32)
            back_diff = abs(float(np.std(arr_b)) - contrast)

        est_wpi = int(np.clip(26 + grad_x * 0.85, 22, 52))
        est_cpi = int(np.clip(34 + grad_y * 1.05, 28, 68))

        # 전문가 비전 판별 트리
        if contrast > 54.0 and grad_y > 17.5:
            detected_key = "CM 20s 12조 터크 와플 (12-Course Tuck Waffle)"
        elif contrast > 44.0 and porosity > 17.0:
            detected_key = "CVC 30s/Poly 75D 올터크 담보루 (All-Tuck Cardigan Cushion)"
        elif grad_x > 21.0 and grad_x > grad_y * 1.15:
            detected_key = "CM 20s 2x2 립 스판 (2x2 Rib Knit - 시보리/몸판)"
        elif porosity > 13.5 and contrast > 38.0:
            detected_key = "CM 30s 싱글 피케 (Single Lacoste Pique)"
        elif back_diff > 10.0 and porosity < 11.5:
            detected_key = "Cotton 20s/30s/10s 3단 헤비 쭈리 (3-Thread Heavy Fleece)"
        elif back_diff > 5.0 or (32.0 <= contrast <= 44.0 and grad_y >= 14.0):
            detected_key = "Cotton 30s/20s 2단 터크 미니 쭈리 (French Terry)"
        elif contrast < 24.0 and grad_x < 12.0:
            detected_key = "Poly 75D/Span 40D 고밀도 인터록 (Interlock 32G)"
        else:
            detected_key = "CVC 30s 싱글 스판 저지 (Single Span Jersey)"

        return {
            "analyzed": True,
            "detected_key": detected_key,
            "contrast": round(contrast, 1),
            "porosity": round(porosity, 1),
            "grad_x": round(grad_x, 1),
            "grad_y": round(grad_y, 1),
            "est_wpi": est_wpi,
            "est_cpi": est_cpi
        }
    except Exception:
        return {
            "analyzed": False,
            "detected_key": "CVC 30s 싱글 스판 저지 (Single Span Jersey)"
        }

# ==============================================================================
# 4. 좌측 사이드바 (종료 공지 + 실시간 접속자 + 접이식 채팅창 + 6단계 세분화 네비게이션)
# ==============================================================================
with st.sidebar:
    st.markdown('<div class="notice-badge">🚨 10/24 서비스 종료 예정</div>', unsafe_allow_html=True)
    st.markdown("## ⚡ 구동현-TEX AI")
    st.caption("Argon Physics × 6-Stage Pipeline OS")
    st.markdown(f'<div class="live-badge">🟢 실시간 접속 실무자: {live_users}명 (무료)</div>', unsafe_allow_html=True)

    # 접이식 영구 보존 라이브 채팅실 (닉네임 수정 가능)
    with st.expander("💬 A/S 라이브 CS 실시간 채팅실 열기"):
        chat_container = st.container()
        with chat_container:
            chat_html = "<div class='as-chat-box'>"
            if not global_chat_messages:
                chat_html += "<div style='color: #CBD5E1; text-align: center;'>등록된 메시지가 없습니다. 첫 대화를 시작해보세요!</div>"
            else:
                for msg in global_chat_messages:
                    chat_html += f"<div style='margin-bottom:6px;'><b>{msg['sender']}</b>: {msg['text']}</div>"
            chat_html += "</div>"
            st.markdown(chat_html, unsafe_allow_html=True)

        with st.form(key="as_chat_form", clear_on_submit=True):
            user_sender = st.text_input("닉네임 (수정 가능)", value=st.session_state.user_nickname)
            user_msg = st.text_input("메시지", placeholder="메시지 입력...", label_visibility="collapsed")
            submitted = st.form_submit_button("전송 🚀", use_container_width=True)
            if submitted and user_msg.strip():
                st.session_state.user_nickname = user_sender.strip() if user_sender.strip() else "익명 실무자"
                global_chat_messages.append({"sender": st.session_state.user_nickname, "text": user_msg.strip()})
                st.rerun()

    st.write("---")
    st.markdown("### 🧭 공정 파이프라인 네비게이션")
    selected_module = st.radio(
        "공정 이동",
        [
            "1) 스와치 사진 분석 & AI 조직규정",
            "2) 5-사종 혼용률 & 재고 구출",
            "3) 염색 바치 & 텐터 열고정",
            "4) 화학가공 · 콤팩터 · 검단",
            "5) 납기 원가 관제탑 & 불량레이더",
            "6) 야드/롤 변환 & 물류 최적화"
        ],
        label_visibility="collapsed"
    )

    st.write("---")
    st.markdown("#### 📌 실시간 파이프라인 동기화 스펙")
    st.info(
        f"• **규정 원단:** {st.session_state.fabric_name}\n\n"
        f"• **설비:** {st.session_state.rec_inch}\" × {st.session_state.rec_gauge}G ({st.session_state.rec_feeds}F)\n\n"
        f"• **가공지 타겟:** {st.session_state.target_width}\" / {st.session_state.target_gsm} GSM\n\n"
        f"• **오더 수량:** {st.session_state.order_kg:,.0f} kg\n\n"
        f"• **원사 산지:** {st.session_state.yarn_origin.split('(')[0]}"
    )

# ==============================================================================
# 5. 상단 헤더 (DEMO VERSION 배지) & 사용설명서
# ==============================================================================
h_c1, h_c2 = st.columns([3.2, 1])
with h_c1:
    st.markdown("# ⚡ 구동현-TEX AI : 전 공정 통합 관제 OS <span class='demo-badge'>DEMO VERSION</span>", unsafe_allow_html=True)
with h_c2:
    st.markdown(f"<div style='text-align:right; padding-top:16px;'><span class='live-badge'>🟢 LIVE 접속자: {live_users}명 Online</span></div>", unsafe_allow_html=True)

with st.expander("📖 [사용설명서] 6대 공정 파이프라인 가이드 & 스와치 비전 분석률 99.9% 달성 4대 촬영 프로토콜"):
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("""
        #### 🚀 6대 공정 파이프라인 핵심 가이드
        * **1) 스와치 사진 분석 & AI 조직규정:** 수동 선택 없이 앞/뒷면 사진을 올리면 AI가 **RIB, 12조 터크 와플, 올터크 담보루, 미니쭈리, 3단쭈리** 등을 자동 규정하고 **실시간 편직 조직도**와 **6대 임원 결재 리포트**를 생성합니다.
        * **2) 5-사종 혼용률 & 재고 구출:** 스판 플레이팅 계수(0.70)가 반영된 5-사종 도넛 차트, 하단 % 텍스트 명세, 악성 재고 원사 현금화 구출기를 제공합니다.
        * **3) 염색 바치 & 텐터 열고정:** 케틀 용량 매칭, 미니멈 차지 벌금 방어, 텐터 챔버 온도·오버피드·속도를 제어합니다.
        * **4) 화학가공 · 콤팩터 · 검단:** 실리콘 유연제 픽업 처방, 콤팩터 수축률 제어, 팬톤 랩딥 레시피 및 4-Point 검단을 수행합니다.
        * **5) 납기 원가 관제탑 & 불량레이더:** 풀 파이프라인 단가($/kg, $/yd), 4대 공정 신호등 불량 레이더, 원사 스왑 네고 및 영문 견적서(CBD)를 출력합니다.
        * **6) 야드/롤 변환 & 물류 최적화:** 야드/롤 환산, 34인치 광폭 마카 손익, 컨테이너 CBM 적재 시뮬레이션을 확정합니다.
        """)
    with g2:
        st.markdown("""
        #### 📸 원단 비전 분석률 99.9% 달성 4대 촬영 프로토콜
        1. **투과광(Backlight) 촬영 [최우선 권장]:** 스와치 뒤에 스마트폰 플래시나 하얀 모니터 화면을 대고 찍으십시오. 표면 잔털이 사라지고 **루프 골격과 터크(Tuck) 홀이 99% 노출**됩니다.
        2. **규격 카드(Scale Marker) 캘리브레이션:** 스와치 옆에 **신용카드(가로 85.6mm)**나 동전을 함께 두고 찍으면 픽셀당 물리적 크기가 보정되어 **WPI/CPI 밀도 오차가 0%**가 됩니다.
        3. **인장(Tension) 텐션 촬영:** 손으로 원단 양옆을 살짝 당겨 찍으면 내부에 숨어 있는 **스판덱스(OP) 필라멘트와 터크 결합선**이 시각적으로 드러납니다.
        4. **사광(Oblique Lighting) 촬영:** 조명을 옆면 15~30도 각도에서 비스듬히 비추면 피케(Pique), 와플, 립(Rib)의 입체 요철 그림자가 극대화됩니다.
        """)

st.write("---")

# ==============================================================================
# MODULE 1: 스와치 사진 분석 & AI 전문가 조직 자동 규정 (카테고리 수동 선택란 제거 + 조직도 포함)
# ==============================================================================
if selected_module == "1) 스와치 사진 분석 & AI 조직규정":
    st.subheader("🔍 1) 스와치 사진 분석 & AI 원단 전문가 조직 자동 규정 (실시간 조직도 탑재)")

    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    u1, u2, u3 = st.columns([1, 1, 1.35])
    with u1:
        front_img = st.file_uploader("📸 1. 스와치 [앞면(Face)] 업로드", type=["jpg", "jpeg", "png"])
        if front_img:
            st.image(front_img, caption="앞면(Face) 픽셀 스캔 완료", use_container_width=True)
    with u2:
        back_img = st.file_uploader("📸 2. 스와치 [뒷면(Back)] 업로드", type=["jpg", "jpeg", "png"])
        if back_img:
            st.image(back_img, caption="뒷면(Back) 픽셀 스캔 완료", use_container_width=True)
    with u3:
        st.markdown("##### ⚡ 3. AI 비전 자동 조직 규정 & 타겟 스펙 입력")

        # AI 픽셀 분석 실행
        ai_res = analyze_swatch_pixels_expert(front_img, back_img) if front_img else {
            "analyzed": False,
            "detected_key": st.session_state.fabric_name if st.session_state.fabric_name in STRUCTURE_DB else "CVC 30s 싱글 스판 저지 (Single Span Jersey)"
        }

        # 사진 미업로드 시에도 8대 전문 조직의 조직도/역설계를 즉시 테스트할 수 있도록 전문가 오버라이드 옵션 제공
        override_options = ["🤖 AI 비전 자동 판독 (권장 - 사진 픽셀 기반 자동 규정)"] + list(STRUCTURE_DB.keys())
        expert_override = st.selectbox(
            "🔬 AI 전문가 판독 모드 (사진 업로드 시 자동 분석 / 수동 시뮬레이션 전환 가능)",
            override_options,
            index=0
        )

        active_struct_key = ai_res["detected_key"] if expert_override.startswith("🤖") else expert_override
        p = STRUCTURE_DB[active_struct_key].copy()
        p["name"] = active_struct_key

        # AI 정밀 조직 규정 결과 & 실시간 편직 조직도 박스
        st.markdown(f"""
        <div class="structure-box">
            <span style="color: #00F2FE; font-weight: 800; font-size: 1.05rem;">🔬 AI 원단 전문가 정밀 조직 규정 결과</span><br>
            • <b>규정 조직명:</b> <span style="color: #38BDF8; font-weight: 800; font-size: 1.02rem;">{p['name']}</span><br>
            • <b>엔지니어링 구조:</b> {p['pattern']} ({p['struct']})<br>
            • <b>전문가 판독 소견:</b> {p['desc']}
            <div class="diagram-pre"><b>[실시간 편직 조직도 (Knitting Cam & Loop Diagram)]</b>\n{p['diagram']}</div>
        </div>
        """, unsafe_allow_html=True)

        c_in1, c_in2, c_in3 = st.columns(3)
        with c_in1:
            in_gsm = st.number_input("목표 가공지 중량(GSM)", value=float(st.session_state.target_gsm), step=5.0)
        with c_in2:
            in_width = st.number_input("목표 가공지 폭(Inch)", value=float(st.session_state.target_width), step=1.0)
        with c_in3:
            in_order_kg = st.number_input("오더 수량(kg)", value=float(st.session_state.order_kg), step=100.0)

        yarn_origin_sel = st.selectbox(
            "투입 원사 산지 및 방적 등급 (축률·감량 연동)",
            [
                "베트남/국내산 코마사 (표준 축률 · 정련감량 0%)",
                "인도산 카드사 (잔털/정련감량 +1.5% · 축률 +2.5% 증가)",
                "컴팩트 코마사 (형태안정성 우수 · 축률 -1.5% 감소)",
                "GRS 리사이클 폴리/면 (장력 민감 · 축률 +1.0% 증가)"
            ]
        )
    st.markdown('</div>', unsafe_allow_html=True)

    origin_shrink_mod = 2.5 if "인도산" in yarn_origin_sel else (-1.5 if "컴팩트" in yarn_origin_sel else (1.0 if "리사이클" in yarn_origin_sel else 0.0))
    w_shrink_final = p["w_shrink"] + origin_shrink_mod
    l_shrink_final = p["l_shrink"] + origin_shrink_mod

    if ai_res["analyzed"]:
        p["wpi"] = ai_res["est_wpi"]
        p["cpi"] = ai_res["est_cpi"]
        st.info(
            f"🔬 **[실제 업로드 스와치 픽셀 스캔 완료]** "
            f"표면 명암비(Contrast): `{ai_res['contrast']}` | 루프/터크 다공도(Porosity): `{ai_res['porosity']}%` | "
            f"실측 밀도: `{ai_res['est_wpi']} WPI × {ai_res['est_cpi']} CPI` ➔ **{p['name']}** 규정 완료!"
        )

    base_cyl_needles = int(round(math.pi * p["inch"] * p["gauge"]))
    active_needles = int(round(base_cyl_needles * p["needle_mult"]))

    greige_width = round(in_width / (1.0 - w_shrink_final / 100.0), 1)
    greige_gsm = round(in_gsm * (1.0 - (l_shrink_final - w_shrink_final) / 100.0) * 0.94, 1)

    main_tex = to_tex(p["y1"][1], p["y1"][2])
    tf_val = round(math.sqrt(main_tex) / (p["sl"] / 10.0), 2)

    rev_weight_g = round((active_needles * (p["sl"] / 100.0) * p["feeds"] * main_tex) / 1_000_000.0, 2)
    daily_prod_kg = round((rev_weight_g * p["rpm"] * 60 * 24 * 0.85) / 1000.0, 1)
    knit_days = round(in_order_kg / max(daily_prod_kg, 1), 1)

    if st.button("🚀 원클릭 AI 스와치 역설계 확정 & 전 공정(모듈 2~6) 데이터 자동 동기화", type="primary", use_container_width=True):
        st.session_state.fabric_name = p["name"]
        st.session_state.pattern_type = p["pattern"]
        st.session_state.struct_mode = p["struct"]
        st.session_state.yarn_origin = yarn_origin_sel
        st.session_state.rec_inch = p["inch"]
        st.session_state.rec_gauge = p["gauge"]
        st.session_state.rec_feeds = p["feeds"]
        st.session_state.rec_rpm = p["rpm"]
        st.session_state.target_gsm = in_gsm
        st.session_state.target_width = in_width
        st.session_state.order_kg = in_order_kg
        st.session_state.wpi = p["wpi"]
        st.session_state.cpi = p["cpi"]
        st.session_state.calc_daily_kg = daily_prod_kg
        st.session_state.calc_tf = tf_val
        st.session_state.calc_span_pct = p["span_pct"]
        st.session_state.w_shrink_Shared = w_shrink_final
        st.session_state.l_shrink_Shared = l_shrink_final

        for idx, key_prefix in enumerate(["y1", "y2", "y3", "y4"], start=1):
            tup = p[key_prefix]
            st.session_state[f"y{idx}_name"] = tup[0]
            st.session_state[f"y{idx}_count"] = tup[1]
            st.session_state[f"y{idx}_unit"] = tup[2]
            st.session_state[f"y{idx}_feeds"] = tup[3]
            st.session_state[f"y{idx}_sl"] = tup[4]
            st.session_state[f"y{idx}_price"] = tup[5]
            st.session_state[f"y{idx}_draft"] = tup[6]
            st.session_state[f"y{idx}_share"] = tup[7]

        st.success(f"✅ [{p['name']}] 역설계 확정 및 전 공정(모듈 2~6) 데이터 100% 자동 동기화 완료!")

    # 핵심 4대 결론 KPI 카드
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("추천 설비 / 실가동 총침수", f"{p['inch']}\" × {p['gauge']}G", f"실가동 {active_needles:,}침 ({p['struct'].split('(')[0]})")
    k2.metric("편직실 지시 생지 타겟", f"폭 {greige_width}\" / {greige_gsm} GSM", f"가공 축률 폭 -{w_shrink_final:.1f}% 반영")
    k3.metric("1대당 일일 생산량 (85%)", f"{daily_prod_kg} kg / 일", f"{in_order_kg:,.0f}kg 편직 시 {knit_days}일 소요")
    k4.metric("밀도계수 (Tightness Factor)", f"TF {tf_val}", "안정" if 1.28 <= tf_val <= 1.62 else "수축/파공 주의")

    # 편직 임원 결재급 6대 정밀 리포트
    st.markdown("### 📋 편직 임원·부장·팀장 결재급 6대 정밀 역설계 명세서")
    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="neon-title">① 기계 물리 스펙 & 침수 예외 반영</div>
            • <b>추천 기종:</b> {p['inch']}" × {p['gauge']}G ({p['feeds']} Feeds / {p['rpm']} RPM)<br>
            • <b>실린더 기본 침수:</b> {base_cyl_needles:,} 본<br>
            • <b>조직 반영 실가동 침수:</b> <b>{active_needles:,} 본</b> ({p['struct']})<br>
            • <b>원사 산지 특성:</b> {yarn_origin_sel}
        </div>
        <div class="glass-card">
            <div class="neon-title">④ 생지(Greige) ↔ 가공지(Finished) 역학</div>
            • <b>바이어 요구 가공지:</b> 폭 {in_width}" / 중량 {in_gsm} GSM<br>
            • <b>요구 생지(Greige) 스펙:</b> 폭 <b>{greige_width}"</b> / 중량 <b>{greige_gsm} GSM</b><br>
            • <b>산지 반영 예상 축률:</b> 폭 -{w_shrink_final:.1f}% / 길이 -{l_shrink_final:.1f}%
        </div>
        """, unsafe_allow_html=True)
    with rc2:
        st.markdown(f"""
        <div class="glass-card">
            <div class="neon-title">② 편직 조직도 (캠 세팅 · 바늘 배열 · 급사)</div>
            • <b>판독 조직명:</b> {p['pattern']}<br>
            • <b>캠 세팅(Knit/Tuck/Miss):</b> {p['cam']}<br>
            • <b>바늘 배열(Needle Layout):</b> {p['needle']}<br>
            • <b>원사 급사 시퀀스:</b> {p['seq']}
        </div>
        <div class="glass-card">
            <div class="neon-title">⑤ 원가 및 생산성 지표</div>
            • <b>1회전당 생산 중량:</b> {rev_weight_g} g / rev<br>
            • <b>일일 실 생산 캐파:</b> <b>{daily_prod_kg} kg/일</b> (85% 효율)<br>
            • <b>오더 편직 소요일:</b> 1대 {knit_days}일 / 3대 가동 시 <b>{round(knit_days/3, 1)}일</b><br>
            • <b>적정 편직 임가공비:</b> ${p['fee']:.2f} / kg
        </div>
        """, unsafe_allow_html=True)
    with rc3:
        relax_h = 36 if p["span_pct"] >= 4.5 else (24 if p["span_pct"] > 0 else 0)
        st.markdown(f"""
        <div class="glass-card">
            <div class="neon-title">③ 원사 & 루프 역학 (플레이팅 보정 포함)</div>
            • <b>주 원사 번수:</b> {p['y1'][0]}<br>
            • <b>추정 루프장 (SL):</b> {p['sl']} mm / 100침<br>
            • <b>스판 드래프트 & 플레이팅:</b> {p['draft']}배 (플레이팅 계수 0.70 적용)<br>
            • <b>밀도 (WPI × CPI):</b> {p['wpi']} WPI × {p['cpi']} CPI
        </div>
        <div class="glass-card">
            <div class="neon-title">⑥ 품질 리스크 & 스판 에이징 타이머</div>
            • <b>Tightness Factor:</b> <b>{tf_val}</b> (기준 1.30~1.60)<br>
            • <b>스판 릴렉스(Aging) 대기:</b> <b>편직 후 최소 {relax_h}시간 상온 휴지 필수</b><br>
            • <b>주의사항:</b> 미준수 시 염색 중 로프 크리즈 및 폭 편차 발생
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🏭 자사 공장 보유 편직기 가용성 자동 매칭 판정")
    m_list = []
    for m in FACTORY_MACHINES:
        g_ok = abs(m["gauge"] - p["gauge"]) <= 4
        t_ok = (m["type"] == p["type"])
        w_ok = (in_width <= 62) or (m["inch"] >= 34)
        verdict = "✅ 즉시 제직 가능" if (g_ok and t_ok and w_ok) else ("⚠️ 조건부 가능 (광폭/게이지 튜닝 필요)" if (g_ok and t_ok) else "❌ 제직 불가 (기종 불일치)")
        mc_capa = round(daily_prod_kg * (m["feeds"] / p["feeds"]) * (m["rpm"] / p["rpm"]), 1) if "불가" not in verdict else 0
        m_list.append({
            "설비 ID": m["id"], "보유 편직기명": m["name"], "규격": f"{m['inch']}\" × {m['gauge']}G ({m['feeds']}F)",
            "가용 판정": verdict, "일일 생산량 (kg/일)": mc_capa, "예상 편직 소요일": f"{round(in_order_kg/mc_capa, 1)}일" if mc_capa > 0 else "-"
        })
    st.dataframe(pd.DataFrame(m_list), use_container_width=True)


# ==============================================================================
# MODULE 2: 5-사종 혼용률 & 재고 구출
# ==============================================================================
elif selected_module == "2) 5-사종 혼용률 & 재고 구출":
    st.subheader("⚙️ 2) 5-사종 정밀 혼용률 제너레이터 & 창고 악성 재고 원사 구출기")

    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    top1, top2, top3, top4 = st.columns(4)
    struct_options = [
        "싱글 저지 (표준 100% 침수)",
        "싱글 변형 (표준 100% 침수)",
        "양면 인터록/1x1립 (200% 침수)",
        "2x2 립 (바늘 빼기 66.7% 가동)",
        "자카드 조직 (선택비 65% 가동)"
    ]
    default_struct_idx = struct_options.index(st.session_state.struct_mode) if st.session_state.struct_mode in struct_options else 0
    with top1:
        struct_mode = st.selectbox("편직 바늘 구동 구조 (침수 예외 반영)", struct_options, index=default_struct_idx)
        st.session_state.struct_mode = struct_mode
    with top2:
        plating_factor = st.slider("스판덱스 플레이팅 보정계수", 0.60, 0.85, float(st.session_state.plating_factor), 0.02)
        st.session_state.plating_factor = plating_factor
    with top3:
        safety_loss_pct = st.slider("원사 안전 발주 로스율 (%)", 1.0, 8.0, 3.5, 0.5)
    with top4:
        m_eff = st.slider("공장 실가동 효율 (%)", 65, 95, 85, 1)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("🎛️ [전문가 세부 보정 서랍] 5-사종 개별 스펙 및 단가라 회전 점유율 수동 조절 (클릭하여 열기)"):
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            m_inch = st.number_input("기계 직경 (Inch)", value=int(st.session_state.rec_inch), step=2)
        with mc2:
            m_gauge = st.number_input("기계 게이지 (Gauge)", value=int(st.session_state.rec_gauge), step=2)
        with mc3:
            m_rpm = st.number_input("가동 RPM", value=int(st.session_state.rec_rpm), step=1)
        st.session_state.rec_inch, st.session_state.rec_gauge, st.session_state.rec_rpm = m_inch, m_gauge, m_rpm

        st.markdown("---")
        roles = ["사종 1 (전면사 Face)", "사종 2 (이면사 Back)", "사종 3 (터크/결합사)", "사종 4 (스판덱스 1)", "사종 5 (스판덱스 2)"]
        y_cols = st.columns(5)
        for i in range(1, 6):
            with y_cols[i - 1]:
                st.markdown(f"**{roles[i-1]}**")
                st.session_state[f"y{i}_name"] = st.text_input(f"원사명 #{i}", value=st.session_state[f"y{i}_name"])
                st.session_state[f"y{i}_unit"] = st.selectbox(f"단위 #{i}", ["Ne(면번수)", "Denier(데니어)"], index=0 if "Ne" in st.session_state[f"y{i}_unit"] else 1)
                st.session_state[f"y{i}_count"] = st.number_input(f"번수/데니어 #{i}", value=float(st.session_state[f"y{i}_count"]), min_value=1.0, step=1.0)
                st.session_state[f"y{i}_feeds"] = st.number_input(f"급사 피더수 #{i}", value=int(st.session_state[f"y{i}_feeds"]), min_value=0, step=6)
                st.session_state[f"y{i}_sl"] = st.number_input(f"루프장(mm/100침) #{i}", value=float(st.session_state[f"y{i}_sl"]), min_value=0.5, step=0.05)
                st.session_state[f"y{i}_draft"] = st.number_input(f"드래프트율 #{i}", value=float(st.session_state[f"y{i}_draft"]), min_value=1.0, step=0.1)
                st.session_state[f"y{i}_share"] = st.number_input(f"단가라 점유율(%) #{i}", value=float(st.session_state[f"y{i}_share"]), min_value=5.0, max_value=100.0, step=5.0)
                st.session_state[f"y{i}_price"] = st.number_input(f"원사 단가($/kg) #{i}", value=float(st.session_state[f"y{i}_price"]), min_value=0.5, step=0.1)

    mult_map = {
        "싱글 저지 (표준 100% 침수)": 1.0,
        "싱글 변형 (표준 100% 침수)": 1.0,
        "양면 인터록/1x1립 (200% 침수)": 2.0,
        "2x2 립 (바늘 빼기 66.7% 가동)": 1.333,
        "자카드 조직 (선택비 65% 가동)": 1.30
    }
    base_needles = int(round(math.pi * st.session_state.rec_inch * st.session_state.rec_gauge))
    active_needles_m2 = int(round(base_needles * mult_map[struct_mode]))

    yarn_list = []
    for i in range(1, 6):
        name = st.session_state[f"y{i}_name"]
        unit = st.session_state[f"y{i}_unit"]
        cnt = st.session_state[f"y{i}_count"]
        feeds = st.session_state[f"y{i}_feeds"]
        sl = st.session_state[f"y{i}_sl"]
        draft = st.session_state[f"y{i}_draft"]
        share = st.session_state[f"y{i}_share"]
        price = st.session_state[f"y{i}_price"]

        tex_v = to_tex(cnt, unit)
        is_span = (draft > 1.2) or ("Span" in name) or ("스판" in name)
        eff_plating = plating_factor if is_span else 1.0

        w_rev_g = (active_needles_m2 * (sl / 100.0) * eff_plating * feeds * (share / 100.0) * tex_v) / (1_000_000.0 * draft) if feeds > 0 else 0.0
        yarn_list.append({
            "slot": f"사종 {i}", "name": name, "feeds": feeds, "sl": sl, "draft": draft,
            "share": share, "price": price, "is_span": is_span, "w_rev_g": w_rev_g
        })

    tot_rev_g = sum(y["w_rev_g"] for y in yarn_list)
    if tot_rev_g <= 0:
        st.warning("최소 1개 사종의 급사 피더수(Feeds)가 0보다 커야 합니다.")
    else:
        weighted_cost = 0.0
        span_sum = 0.0
        text_lines = []

        for y in yarn_list:
            pct = (y["w_rev_g"] / tot_rev_g) * 100.0
            y["pct"] = round(pct, 2)
            y["net_kg"] = round(st.session_state.order_kg * (pct / 100.0), 1)
            y["po_kg"] = round(y["net_kg"] * (1.0 + safety_loss_pct / 100.0), 1)
            weighted_cost += (pct / 100.0) * y["price"]
            if y["is_span"]:
                span_sum += pct
            if y["feeds"] > 0:
                text_lines.append(
                    f"• <b>[{y['slot']}] {y['name']}</b> ➔ <span style='color:#00F2FE; font-weight:800; font-size:1.08rem;'>{y['pct']:.1f}%</span> "
                    f"(순소요: {y['net_kg']:,.1f} kg | <b>안전발주 PO: {y['po_kg']:,.1f} kg</b>)"
                )

        daily_kg_now = round((tot_rev_g * st.session_state.rec_rpm * 60 * 24 * (m_eff / 100.0)) / 1000.0, 1)
        st.session_state.calc_daily_kg = daily_kg_now
        st.session_state.calc_yarn_cost_kg = round(weighted_cost, 3)
        st.session_state.calc_span_pct = round(span_sum, 1)

        c_left, c_right = st.columns([1.1, 1.3])
        with c_left:
            active_y = [y for y in yarn_list if y["feeds"] > 0]
            fig = go.Figure(data=[go.Pie(
                labels=[f"{y['slot']}: {y['name']}" for y in active_y],
                values=[y["pct"] for y in active_y],
                hole=0.55,
                textinfo="label+percent",
                marker=dict(colors=["#00F2FE", "#38BDF8", "#818CF8", "#F472B6", "#34D399"])
            )])
            fig.update_layout(
                title="📊 5-사종 정밀 투입 혼용률 (플레이팅 보정 완료)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FFFFFF", size=13),
                margin=dict(t=40, b=10, l=10, r=10),
                height=310
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("##### 📝 사종별 정밀 혼용률(%) 및 안전 발주량 텍스트 명세")
            st.markdown(f"<div class='yarn-summary-box'>{'<br>'.join(text_lines)}</div>", unsafe_allow_html=True)

        with c_right:
            m1, m2, m3 = st.columns(3)
            m1.metric("실가동 총침수", f"{active_needles_m2:,} 침", struct_mode.split("(")[0])
            m2.metric("1대당 일일 생산량", f"{daily_kg_now} kg/일", f"효율 {m_eff}% 기준")
            m3.metric("가중평균 순수 원사비", f"${weighted_cost:.2f} / kg", f"스판 실함량 {span_sum:.1f}%")

            st.dataframe(pd.DataFrame([
                {
                    "슬롯": y["slot"], "사종명": y["name"], "피더수": y["feeds"],
                    "혼용률(%)": f"{y['pct']:.1f}%", "순소요(kg)": y["net_kg"],
                    "안전발주 PO(kg)": y["po_kg"], "단가($/kg)": f"${y['price']:.2f}"
                } for y in active_y
            ]), use_container_width=True)

            with st.expander("💡 [현금화 치트키] 창고 악성 재고 원사(Dead Stock) 털기 역산기", expanded=True):
                d1, d2 = st.columns(2)
                with d1:
                    dead_sel = st.selectbox("창고 방치 원사 선택", [y["name"] for y in active_y])
                with d2:
                    dead_kg = st.number_input("보유 재고량 (kg)", value=350.0, step=50.0)
                target_y = [y for y in active_y if y["name"] == dead_sel][0]
                max_fab_kg = round(dead_kg / (target_y["pct"] / 100.0), 1)
                saved_cash = round(dead_kg * target_y["price"], 0)
                st.success(f"🏭 방치된 `{dead_sel}` **{dead_kg:,.0f}kg** 투입 시 현재 원단 **{max_fab_kg:,.1f}kg** 즉시 생산 가능 ➔ 매몰 원사비 **${saved_cash:,.0f}** 현금 구출!")


# ==============================================================================
# MODULE 3: 염색 바치 & 텐터 열고정
# ==============================================================================
elif selected_module == "3) 염색 바치 & 텐터 열고정":
    st.subheader("🔥 3) 염색 케틀(Kettle) 바치 매칭 & 텐터(Stenter) 열고정 정밀 제어")

    tc1, tc2 = st.columns(2)
    with tc1:
        st.markdown('<div class="hero-card">', unsafe_allow_html=True)
        st.markdown("#### 💧 염색 케틀(Kettle) 바치 & 미니멈 차지 방어기")
        kettle_options = [150, 300, 500, 1000]
        k_idx = kettle_options.index(st.session_state.kettle_cap) if st.session_state.kettle_cap in kettle_options else 2
        kettle_cap = st.selectbox("염색 케틀 1바치 용량 (kg)", kettle_options, index=k_idx)
        st.session_state.kettle_cap = kettle_cap

        order_q = st.session_state.order_kg
        full_b = int(order_q // kettle_cap)
        rem_k = order_q % kettle_cap
        min_pen = round(250.0 / max(order_q, 1), 3) if (0 < rem_k < kettle_cap * 0.6) else 0.0

        if min_pen > 0:
            st.error(f"🚨 **[미니멈 차지 & 탕차이 경보]** 총 {order_q:,.0f}kg 발주 시 {kettle_cap}kg 케틀 {full_b}바치 후 **{rem_k:,.0f}kg 잔량** 발생! (미니멈 벌금 +${min_pen:.2f}/kg 합산됨) ➔ **{full_b*kettle_cap:,.0f}kg** 또는 **{(full_b+1)*kettle_cap:,.0f}kg**으로 수량 조정 강력 권장.")
        else:
            st.success(f"✅ **[케틀 바치 최적화]** {kettle_cap}kg 케틀 기준 미니멈 차지 및 바치 간 탕차이 리스크 없이 정상 소화 가능합니다.")

        dye_path_opts = [
            "단일 섬유 1욕 염색 (표준)",
            "CVC/TC 1욕 연속 염색 (+$0.15/kg)",
            "CVC/TC 2욕 분할 염색 (+$0.42/kg · +1.5일)"
        ]
        dye_path = st.selectbox("염색 욕(Bath) 경로", dye_path_opts, index=2 if "CVC" in st.session_state.fabric_name else 0)
        st.session_state.dye_path = dye_path
        st.metric("선택한 염색 경로 추가 원가", "+$0.42 / kg" if "2욕" in dye_path else ("+$0.15 / kg" if "1욕 연속" in dye_path else "$0.00 / kg"))
        st.markdown('</div>', unsafe_allow_html=True)

    with tc2:
        st.markdown('<div class="hero-card">', unsafe_allow_html=True)
        st.markdown("#### 🔥 텐터(Stenter) 열고정 & 체류시간 제어기")
        chambers = st.number_input("텐터 챔버 수 (1챔버=3m)", value=8, min_value=4, max_value=12)
        dwell_s = st.number_input("열고정 체류시간 (초, Dwell Time)", value=42 if st.session_state.calc_span_pct > 0 else 30)
        overfeed = st.slider("텐터 핀 오버피드율 (Overfeed %)", 0, 35, 18)
        w_loss = st.slider("염색·가공 폭 축률 (%)", 5, 22, int(round(st.session_state.w_shrink_Shared)))

        t_temp = 190 if st.session_state.calc_span_pct > 0 else 172
        t_speed = round((chambers * 3.0) / (dwell_s / 60.0), 1)
        req_gw = round(st.session_state.target_width / (1.0 - w_loss / 100.0), 1)
        st.metric("권장 챔버 온도 / 가동 속도", f"{t_temp}°C / {t_speed} m/min", f"오버피드 +{overfeed}% 적용")
        st.metric("역산 생지(Greige) 폭 지시서", f"생지 폭 {req_gw} Inch", f"가공 목표폭 {st.session_state.target_width}\" 기준")
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# MODULE 4: 화학가공 · 콤팩터 · 검단 (랩딥 레시피 및 4-Point 검단 통합)
# ==============================================================================
elif selected_module == "4) 화학가공 · 콤팩터 · 검단":
    st.subheader("💧 4) 화학 패딩(Pick-up), 콤팩터 수축 제어 & 랩딥 · 4-Point 품질 검단")

    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown('<div class="hero-card">', unsafe_allow_html=True)
        st.markdown("#### 🧪 화학 패딩(Pick-up) & 조제 원가 계산기")
        pickup = st.slider("망글(Mangle) Wet Pick-up율 (%)", 55, 85, 70)
        sil_gl = st.number_input("실리콘 유연제 처방 농도 (g/L)", value=float(st.session_state.silicone_g_l), step=5.0)
        st.session_state.silicone_g_l = sil_gl
        chem_kg = round(st.session_state.order_kg * (pickup / 100.0) * (sil_gl / 1000.0), 2)
        chem_cost = round((chem_kg * 4.2) / max(st.session_state.order_kg, 1), 3)
        st.metric("실리콘 유연제 총 소요량", f"{chem_kg} kg", f"조제 원가 +${chem_cost}/kg")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 🎨 바이어 랩딥(Lab-Dip) 1차 합격 배합비 예측기")
        pantone = st.text_input("바이어 요구 팬톤 코드", value="19-4052 TCX (Classic Blue)")
        st.info(f"🎯 **[{pantone}] 조건등색(D65/TL84) 오차 최소화 1차 합격 추천 레시피:**\n\n• Reactive Blue 19 (1.82% o.w.f) + Reactive Red 195 (0.14% o.w.f) / Disperse Blue 79 (1.45% o.w.f)")
        st.markdown('</div>', unsafe_allow_html=True)

    with fc2:
        st.markdown('<div class="hero-card">', unsafe_allow_html=True)
        st.markdown("#### ⚙️ 콤팩터(Compactor) 잔여 수축 통제기")
        pre_sh = st.number_input("텐터 직후 잔여 길이 수축률 (%)", value=-6.5, step=0.5)
        std_sh = st.number_input("바이어 합격 기준 수축률 (%)", value=-3.0, step=0.5)
        comp_pct = round(abs(pre_sh - std_sh) * 1.25, 1)
        st.metric("콤팩터 권장 압축 텐션", f"+{comp_pct}%", f"가공 후 중량 +{round(comp_pct*1.8, 1)} GSM 상승 효과")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 🔎 측색기 색차(ΔE) & 4-Point 원단 검단 판정기")
        q1, q2 = st.columns(2)
        with q1:
            de = st.number_input("측색기 실측 색차 (ΔE)", value=0.58, step=0.05)
            st.metric("색차 판정", f"ΔE {de}", "PASS (0.8 이하)" if de <= 0.8 else "REJECT (재염 필요)")
        with q2:
            pts = st.number_input("100 Sq.Yd당 4-Point 감점", value=14.5, step=1.0)
            st.metric("검단 등급 판정", f"{pts} Points", "A-Grade 합격" if pts <= 20.0 else "B-Grade 불합격")
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# MODULE 5: 납기 원가 관제탑 & 불량레이더 (스왑 네고 & 영문 CBD 다운로드 포함)
# ==============================================================================
elif selected_module == "5) 납기 원가 관제탑 & 불량레이더":
    st.subheader("🗼 5) 납기 원가 관제탑 & 공정별 신호등 불량 레이더 · 영문 견적서(CBD)")

    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        color_depth = st.selectbox(
            "염색 컬러 등급 (단가 & 납기 연동)",
            [
                "Bleach White ($0.65 | 4.5시간/Batch)",
                "Light Shade ($0.80 | 5.0시간/Batch)",
                "Medium Shade ($0.95 | 6.0시간/Batch)",
                "Dark / Black ($1.15 | 8.5시간/Batch)",
                "Extra Dark / 형광 ($1.40 | 10.5시간/Batch)"
            ],
            index=2
        )
    with b2:
        dye_process = st.selectbox(
            "염색 욕(Bath) 경로",
            [
                "단일 섬유 1욕 염색 (표준)",
                "CVC/TC 1욕 연속 염색 (+$0.15/kg)",
                "CVC/TC 2욕 분할 염색 (+$0.42/kg · +1.5일)"
            ],
            index=2 if "CVC" in st.session_state.fabric_name else 0
        )
    with b3:
        kettle_cap = st.selectbox("염색 케틀(Kettle) 1바치 용량 (kg)", [150, 300, 500, 1000], index=2)
    with b4:
        target_margin_pct = st.slider("목표 영업 마진율 (%)", 5.0, 30.0, 15.0, 1.0)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("⚙️ [세부 원가 파라미터 보정] 편직 공임 · 특수 후가공 선택 · 원사 산지별 수율 로스 수동 조정"):
        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            base_yarn_cost = st.number_input("순수 원사비 ($/kg)", value=float(st.session_state.calc_yarn_cost_kg), step=0.05)
            knit_charge = st.number_input("편직 임가공비 ($/kg)", value=0.38, step=0.02)
        with ec2:
            fin_options = st.multiselect(
                "특수 후가공 추가",
                ["실리콘 유연 가공 (+$0.08)", "흡한속건 Wicking (+$0.12)", "항균 방취 (+$0.20)", "양면 기모 (+$0.25)", "콤팩터 수축 제어 (+$0.10)"],
                default=["실리콘 유연 가공 (+$0.08)", "콤팩터 수축 제어 (+$0.10)"]
            )
        with ec3:
            origin_loss_add = 1.5 if "인도산" in st.session_state.yarn_origin else (-0.5 if "컴팩트" in st.session_state.yarn_origin else 0.0)
            yield_loss_pct = st.slider("염색 정련 감량 + 텐터 변사 트리밍 로스 (%)", 2.0, 12.0, float(5.5 + origin_loss_add), 0.5)
            pack_logis_cost = st.number_input("포장 및 내륙 운송비 ($/kg)", value=0.12, step=0.02)

    order_q = st.session_state.order_kg
    full_batches = int(order_q // kettle_cap)
    rem_kg = order_q % kettle_cap
    min_charge_per_kg = round(250.0 / max(order_q, 1), 3) if (0 < rem_kg < kettle_cap * 0.6) else 0.0

    shade_info = {
        "Bleach": (0.65, 4.5, 0.0),
        "Light": (0.80, 5.0, 0.5),
        "Medium": (0.95, 6.0, 1.0),
        "Dark": (1.15, 8.5, 2.5),
        "Extra": (1.40, 10.5, 4.0)
    }
    dye_price, batch_hrs, extra_dye_days = next(v for k, v in shade_info.items() if k in color_depth)
    bath_cost_add = 0.42 if "2욕" in dye_process else (0.15 if "1욕 연속" in dye_process else 0.0)
    bath_day_add = 1.5 if "2욕" in dye_process else 0.0

    knit_days_m3 = round(order_q / max(st.session_state.calc_daily_kg * 2.0, 1), 1)
    relax_days = 1.5 if st.session_state.calc_span_pct >= 4.0 else 0.5
    dye_fin_days = round(3.0 + extra_dye_days + bath_day_add, 1)
    total_lead_days = round(knit_days_m3 + relax_days + dye_fin_days, 1)

    fin_map = {"실리콘": 0.08, "흡한속건": 0.12, "항균": 0.20, "기모": 0.25, "콤팩터": 0.10}
    fin_cost = sum(v for k, v in fin_map.items() if any(k in o for o in fin_options))

    raw_cost = base_yarn_cost + knit_charge + dye_price + bath_cost_add + fin_cost + min_charge_per_kg
    finished_net_cost_kg = (raw_cost / (1.0 - yield_loss_pct / 100.0)) + pack_logis_cost
    quote_price_kg = finished_net_cost_kg / (1.0 - target_margin_pct / 100.0)

    kg_per_yd = (st.session_state.target_width * st.session_state.target_gsm * 0.02322576) / 1000.0
    quote_price_yd = quote_price_kg * kg_per_yd
    net_profit_total = (quote_price_kg - finished_net_cost_kg) * order_q

    k_c1, k_c2, k_c3, k_c4 = st.columns(4)
    k_c1.metric("바이어 제안 단가 (KG)", f"${quote_price_kg:.2f} / kg", f"순원가 ${finished_net_cost_kg:.2f} (로스 {yield_loss_pct}% 반영)")
    k_c2.metric("바이어 제안 단가 (YARD)", f"${quote_price_yd:.2f} / yd", f"폭 {st.session_state.target_width}\" · {st.session_state.target_gsm} GSM")
    k_c3.metric("예상 총 납기 (Lead Time)", f"총 {total_lead_days} 일", f"편직 {knit_days_m3}일 + 에이징 {relax_days}일 + 염색 {dye_fin_days}일")
    k_c4.metric("오더 예상 순영업이익", f"${net_profit_total:,.0f}", f"마진율 {target_margin_pct:.0f}% (염색 {batch_hrs}h/Batch)")

    if min_charge_per_kg > 0:
        st.error(
            f"🚨 **[염색 케틀 바치 불일치 & 탕차이 경보]** {order_q:,.0f}kg 발주 시 {kettle_cap}kg 케틀 {full_batches}바치 후 **{rem_kg:,.0f}kg 잔량** 발생! "
            f"(미니멈 차지 벌금 +${min_charge_per_kg:.2f}/kg 자동 합산됨) ➔ 💡 **{full_batches*kettle_cap:,.0f}kg** 또는 **{(full_batches+1)*kettle_cap:,.0f}kg**으로 수량 조정을 강력 권장합니다."
        )
    else:
        st.success(f"✅ **[염색 케틀 매칭 완료]** {kettle_cap}kg 케틀 기준 미니멈 차지 및 바치 간 탕차이 리스크 없이 최적 가동됩니다.")

    st.markdown("### 🛡️ 공정별 예상 불량 신호등 레이더 & 1줄 현장 액션 지시서")
    tf_v = st.session_state.calc_tf
    sil_v = st.session_state.silicone_g_l
    g_v = st.session_state.rec_gauge

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="neon-title">① 편직 공정 (Knitting)</div>
            <b>상태:</b> {"🟡 주의 (바레/스판끊김)" if g_v >= 28 else "🟢 정상 (안정)"}<br><br>
            • <b>예상 불량:</b> 가로줄(Barre) 및 침선<br>
            • <b>1줄 지시:</b> "전 피더 얀 텐션 ±0.2g 이내 세팅 및 인도산/베트남산 원사 Lot 혼입 절대 금지."
        </div>
        """, unsafe_allow_html=True)
    with r2:
        st.markdown(f"""
        <div class="glass-card">
            <div class="neon-title">② 염색 공정 (Dyeing)</div>
            <b>상태:</b> {"🔴 위험 (올리고머/크리즈)" if batch_hrs >= 8.5 else "🟢 정상 (안정)"}<br><br>
            • <b>예상 불량:</b> 다크 컬러 올리고머 백화 및 주름<br>
            • <b>1줄 지시:</b> "체류시간 {batch_hrs}h 세팅, 승온 분당 1.5°C 제한, 욕중 유연제 1.5g/L 및 환원세정 필수."
        </div>
        """, unsafe_allow_html=True)
    with r3:
        st.markdown(f"""
        <div class="glass-card">
            <div class="neon-title">③ 텐터·가공 (Stenter)</div>
            <b>상태:</b> {"🔴 위험 (사행도/수축 불량)" if tf_v < 1.30 else "🟢 정상 (규격 통과)"}<br><br>
            • <b>예상 불량:</b> 세탁 후 몸판 돌아감(Spirality)<br>
            • <b>1줄 지시:</b> "말로(Mahlo) 스큐 교정기 +3도 보정, 오버피드 +18% 및 챔버 190°C 이하 유지."
        </div>
        """, unsafe_allow_html=True)
    with r4:
        nc_risk = (g_v >= 28 or tf_v >= 1.55) and (sil_v < 20.0)
        st.markdown(f"""
        <div class="glass-card">
            <div class="neon-title">④ 봉제 클레임 (Needle Cut)</div>
            <b>상태:</b> {"🔴 위험 (봉제 파공 90%)" if nc_risk else "🟢 정상 (관통 양호)"}<br><br>
            • <b>예상 불량:</b> 고속 재봉 시 원사 끊어짐(파공)<br>
            • <b>1줄 지시:</b> "텐터 패딩 시 양이온 실리콘 유연제를 25g/L로 증량하고 볼포인트 바늘(SES) 지시."
        </div>
        """, unsafe_allow_html=True)

    n_col, cbd_col = st.columns([1.2, 1])
    with n_col:
        st.markdown("#### 🤝 바이어 타겟 단가 역산 '원사 스왑(Swap) 네고 제안기'")
        target_p = st.number_input("바이어 요구 타겟가 ($/kg)", value=round(quote_price_kg - 0.50, 2), step=0.10)
        if quote_price_kg > target_p:
            st.dataframe(pd.DataFrame([
                {"카운터 오퍼": "옵션 A (원사 등급 스왑)", "스펙 조정": "코마사(CM) ➔ 카드사(CD) + 바이오 효소 워싱", "절감 단가": f"${quote_price_kg - 0.42:.2f}/kg", "유사도": "93%"},
                {"카운터 오퍼": "옵션 B (혼용률 스왑)", "스펙 조정": "CVC 폴리 비중 상향 + 1욕 연속 염색 전환", "절감 단가": f"${quote_price_kg - 0.58:.2f}/kg", "유사도": "89%"},
                {"카운터 오퍼": "옵션 C (중량 다이어트)", "스펙 조정": f"목표 중량 {st.session_state.target_gsm} ➔ {st.session_state.target_gsm - 10:.0f} GSM 합의", "절감 단가": f"${quote_price_kg - 0.35:.2f}/kg", "유사도": "95%"}
            ]), use_container_width=True)
        else:
            st.success("🎉 바이어 타겟가가 견적가 이상입니다! 즉시 수주 확정하십시오.")

    with cbd_col:
        st.markdown("#### 📄 바이어 송부용 영문 견적서(CBD) & ESG 리포트")
        cbd_doc = f"""[구동현-TEX AI OFFICIAL QUOTATION & CBD]
- Item: {st.session_state.fabric_name} ({st.session_state.struct_mode})
- Spec: {st.session_state.target_width}" Width / {st.session_state.target_gsm} GSM (Finished)
- Order Qty: {order_q:,.0f} kg ({order_q / max(kg_per_yd, 0.001):,.0f} yds)
- Quoted Price: USD ${quote_price_kg:.2f} / kg (USD ${quote_price_yd:.2f} / yd)
- Total Lead Time: {total_lead_days} Days (Dyeing {batch_hrs}h/Batch reflected)
- ESG Carbon Saving: -46.5% CO2e available with GRS Recycled Yarn"""
        st.download_button("📥 공식 영문 견적서(CBD) 다운로드 (.txt)", data=cbd_doc, file_name="KDH_TEX_CBD.txt", use_container_width=True)
        st.text_area("카톡/이메일 원클릭 복사용", cbd_doc, height=125)


# ==============================================================================
# MODULE 6: 야드/롤 변환 & 물류 최적화
# ==============================================================================
elif selected_module == "6) 야드/롤 변환 & 물류 최적화":
    st.subheader("📦 6) 초정밀 야드/롤 변환기 & 광폭 봉제 마카 손익 · 컨테이너 CBM 테트리스")

    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    u1, u2, u3, u4 = st.columns(4)
    with u1:
        c_width = st.number_input("가공지 폭 (Inch)", value=float(st.session_state.target_width), step=1.0)
    with u2:
        c_gsm = st.number_input("가공지 중량 (GSM)", value=float(st.session_state.target_gsm), step=5.0)
    with u3:
        c_kg = st.number_input("총 오더 중량 (kg)", value=float(st.session_state.order_kg), step=100.0)
    with u4:
        roll_kg = st.number_input("1롤(Roll) 패킹 기준 중량 (kg)", value=22.0, step=1.0)
    st.markdown('</div>', unsafe_allow_html=True)

    yds_per_kg = 43055.64 / (c_width * c_gsm)
    tot_yds = round(c_kg * yds_per_kg, 1)
    tot_m = round(tot_yds * 0.9144, 1)
    tot_rolls = math.ceil(c_kg / roll_kg)
    yds_per_roll = round(roll_kg * yds_per_kg, 1)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("1 kg당 환산 야드", f"{yds_per_kg:.2f} yd/kg", f"1 yd = {round(1000/yds_per_kg, 1)} g")
    k2.metric("오더 총 환산 길이", f"{tot_yds:,.1f} Yards", f"{tot_m:,.1f} Meters")
    k3.metric("총 출고 패킹 롤 수", f"{tot_rolls:,} Rolls", f"롤당 {roll_kg} kg 기준")
    k4.metric("1롤당 감김 길이", f"{yds_per_roll:,.1f} yd/Roll", f"{round(yds_per_roll*0.9144, 1)} m/Roll")

    st.write("---")
    col_m, col_c = st.columns(2)

    with col_m:
        st.markdown("### ✂️ 봉제 요척(YY) 연동 광폭 마카(Marker) 손익 계산기")
        g_pcs = st.number_input("의류 봉제 오더 수량 (Pcs, 장)", value=30000, step=5000)
        yy_yd = st.number_input("일반폭 기준 1장당 봉제 요척 (yd/pc)", value=1.15, step=0.05)
        eff_gain = st.slider("34인치 광폭 제직 시 마카 효율 상승률 (%)", 1.5, 7.0, 3.8, 0.2)
        yd_price = st.number_input("원단 야드당 단가 ($/yd)", value=1.95, step=0.05)

        saved_y = round(g_pcs * yy_yd * (eff_gain / 100.0), 1)
        saved_usd = round(saved_y * yd_price, 0)
        st.success(
            f"💡 **[광폭 전환 마카 손익 판정]**\n\n"
            f"• 34인치 광폭 제직 시 재단 파지 감소로 원단 **{saved_y:,.1f} 야드 절감**\n"
            f"• 의류 {g_pcs:,}장 오더 기준 **총 ${saved_usd:,.0f} (약 {int(saved_usd*1380):,}원) 원단비 순이익 추가 확보!**"
        )

    with col_c:
        st.markdown("### 🚢 롤 직경(cm) 역산 & 컨테이너 CBM 테트리스 최적화기")
        tube_cm = st.number_input("지관(Paper Tube) 외경 (cm)", value=8.5, step=0.5)
        thick_mm = st.number_input("원단 두께 (mm)", value=round(c_gsm / 320.0, 2), step=0.05)
        cntr = st.selectbox("컨테이너 규격", ["20ft Dry (유효 28 CBM)", "40ft High Cube (유효 68 CBM)"], index=1)

        roll_len_cm = yds_per_roll * 91.44
        roll_dia_cm = round(math.sqrt(tube_cm**2 + (4.0 * roll_len_cm * (thick_mm / 10.0)) / math.pi), 1)
        roll_w_m = (c_width + 2.0) * 0.0254
        roll_cbm = round(((roll_dia_cm / 100.0) ** 2) * roll_w_m * 0.88, 4)

        max_cbm = 68.0 if "40ft" in cntr else 28.0
        max_rolls = int(max_cbm // max(roll_cbm, 0.001))
        order_cbm = round(tot_rolls * roll_cbm, 2)

        st.info(
            f"📐 **[컨테이너 적재 시뮬레이션]**\n\n"
            f"• **1롤 예상 직경:** `{roll_dia_cm} cm` (1롤 부피 `{roll_cbm:.3f} CBM`)\n"
            f"• **현재 오더({tot_rolls}롤) 부피:** `{order_cbm} CBM` ({cntr} 적재율 **{min(100.0, round(order_cbm/max_cbm*100, 1))}%**)\n"
            f"• **컨테이너 1대 최대 선적 가능량:** 지그재그(Nest) 적재 시 최대 **{max_rolls:,} 롤**"
        )