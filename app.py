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
# 0. 페이지 설정 & 랜덤 닉네임 초기화
# ==============================================================================
st.set_page_config(
    page_title="구동현-TEX AI v3.11 | Demo Edition",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_active_sessions():
    return {}

@st.cache_resource
def get_global_chat_history():
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

if "user_nickname" not in st.session_state:
    adjectives = ["용감한", "재빠른", "꼼꼼한", "냉철한", "노련한", "열정적인", "날카로운", "든든한", "민첩한", "특급"]
    animals = ["호랑이", "사자", "독수리", "표범", "늑대", "상어", "매", "곰", "고슴도치", "판다"]
    st.session_state.user_nickname = f"{random.choice(adjectives)} {random.choice(animals)}"

global_chat_messages = get_global_chat_history()

# ==============================================================================
# 1. 전역 세션 상태 초기화
# ==============================================================================
defaults = {
    "fabric_name": "CVC 30s 싱글 스판 저지 (Single Span Jersey)",
    "pattern_type": "Single Jersey (Standard)",
    "struct_mode": "싱글 저지 (표준 100% 침수)",
    "yarn_origin": "베트남/국내산 코마사 (표준 축률)",
    "rec_inch": 30,
    "rec_gauge": 28,
    "rec_feeds": 90,
    "rec_rpm": 21,
    "target_gsm": 185.0,
    "target_width": 60.0,
    "order_kg": 1200.0,
    "wpi": 38,
    "cpi": 52,
    "plating_factor": 0.70,
    "y1_name": "CVC 30s/1 (전면사 Face)", "y1_count": 30.0, "y1_unit": "Ne(면번수)", "y1_feeds": 90, "y1_sl": 2.82, "y1_price": 3.40, "y1_draft": 1.0, "y1_share": 100.0,
    "y2_name": "Cotton 20s/1 (이면사 Back)", "y2_count": 20.0, "y2_unit": "Ne(면번수)", "y2_feeds": 0, "y2_sl": 3.80, "y2_price": 3.10, "y2_draft": 1.0, "y2_share": 100.0,
    "y3_name": "폴리 75D (특수사)", "y3_count": 75.0, "y3_unit": "Denier(데니어)", "y3_feeds": 0, "y3_sl": 2.10, "y3_price": 1.85, "y3_draft": 1.0, "y3_share": 100.0,
    "y4_name": "Spandex 20D (스판덱스 1)", "y4_count": 20.0, "y4_unit": "Denier(데니어)", "y4_feeds": 90, "y4_sl": 2.82, "y4_price": 6.80, "y4_draft": 3.1, "y4_share": 100.0,
    "y5_name": "Spandex 40D (스판덱스 2)", "y5_count": 40.0, "y5_unit": "Denier(데니어)", "y5_feeds": 0, "y5_sl": 2.82, "y5_price": 6.20, "y5_draft": 3.2, "y5_share": 100.0,
    "calc_daily_kg": 248.0,
    "calc_yarn_cost_kg": 3.58,
    "calc_tf": 1.42,
    "calc_span_pct": 5.1,
    "silicone_g_l": 15.0
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

FACTORY_MACHINES = [
    {"id": "MC-01", "name": "30인치 28G 싱글기 (Mayer & Cie)", "gauge": 28, "inch": 30, "feeds": 90, "rpm": 22, "type": "Single"},
    {"id": "MC-02", "name": "34인치 28G 광폭 싱글기 (Santoni)", "gauge": 28, "inch": 34, "feeds": 102, "rpm": 20, "type": "Single"},
    {"id": "MC-03", "name": "30인치 24G 양면/인터록기 (Terrot)", "gauge": 24, "inch": 30, "feeds": 84, "rpm": 18, "type": "Double"},
    {"id": "MC-04", "name": "30인치 20G 3단 쭈리기 (Pai Lung)", "gauge": 20, "inch": 30, "feeds": 60, "rpm": 16, "type": "Fleece"},
    {"id": "MC-05", "name": "32인치 32G 하이게이지 싱글기", "gauge": 32, "inch": 32, "feeds": 96, "rpm": 20, "type": "Single"},
]

# ==============================================================================
# 2. UI 가시성 및 드롭다운/입력창 검은색 글씨 강제 CSS
# ==============================================================================
st.markdown("""
<style>
    .stApp { background-color: #090D16; color: #FFFFFF !important; }
    
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B;
    }
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
        font-weight: 500;
    }
    div[role="radiogroup"] > label {
        background: rgba(30, 41, 59, 0.75);
        padding: 12px 14px !important;
        border-radius: 12px;
        margin-bottom: 8px;
        border: 1px solid #334155;
        transition: all 0.2s ease;
    }
    div[role="radiogroup"] > label:hover {
        border-color: #00F2FE;
        background: rgba(15, 23, 42, 0.98);
    }

    label, .stFileUploader label, .stTextInput label, .stNumberInput label, .stSelectbox label, .stSlider label, p, span, div, h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
    }
    
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] {
        color: #FFFFFF !important;
    }

    div[data-baseweb="select"] * {
        color: #000000 !important;
    }
    div[data-baseweb="popover"] * {
        color: #000000 !important;
    }

    section[data-testid="stSidebar"] input {
        color: #000000 !important;
        background-color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    [data-testid="stFileUploader"] section {
        background-color: #1E293B !important;
        border: 2px dashed #38BDF8 !important;
    }
    [data-testid="stFileUploader"] section div, [data-testid="stFileUploader"] section span, [data-testid="stFileUploader"] section small {
        color: #FFFFFF !important;
    }

    .hero-card {
        background: linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(30,41,59,0.85) 100%);
        border: 1px solid rgba(0, 242, 254, 0.35);
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.45);
    }
    .glass-card {
        background: rgba(17, 24, 39, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.22);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    .neon-title { color: #38BDF8 !important; font-weight: 800; font-size: 1.08rem; margin-bottom: 8px; }
    .live-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10B981;
        color: #34D399 !important;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .notice-badge {
        display: inline-block;
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid #EF4444;
        color: #F87171 !important;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .demo-badge {
        display: inline-block;
        background: rgba(56, 189, 248, 0.15);
        border: 1px solid #38BDF8;
        color: #38BDF8 !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        vertical-align: middle;
        margin-left: 10px;
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
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 10px;
        max-height: 200px;
        overflow-y: auto;
        font-size: 0.82rem;
        margin-bottom: 8px;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. 유틸리티 함수
# ==============================================================================
def to_tex(count_val, unit_str):
    if count_val <= 0:
        return 0.0
    return (590.5 / count_val) if "Ne" in unit_str else (count_val / 9.0)

def analyze_swatch_pixels(front_img_file, back_img_file):
    try:
        img_f = Image.open(front_img_file).convert("L").resize((256, 256))
        arr_f = np.array(img_f, dtype=np.float32)
        contrast = float(np.std(arr_f))
        grad_x = float(np.mean(np.abs(np.diff(arr_f, axis=1))))
        grad_y = float(np.mean(np.abs(np.diff(arr_f, axis=0))))
        porosity = float(np.mean((arr_f < 45) | (arr_f > 215)) * 100.0)
        return {
            "analyzed": True, "contrast": round(contrast, 1), "porosity": round(porosity, 1),
            "est_wpi": int(np.clip(26 + grad_x * 0.85, 22, 52)),
            "est_cpi": int(np.clip(34 + grad_y * 1.05, 28, 68))
        }
    except Exception:
        return {"analyzed": False}

# ==============================================================================
# 4. 좌측 사이드바 네비게이션 & 채팅창
# ==============================================================================
with st.sidebar:
    st.markdown('<div class="notice-badge">🚨 10/24 서비스 종료 예정</div>', unsafe_allow_html=True)
    
    st.markdown("## ⚡ 구동현-TEX AI")
    st.markdown(f'<div class="live-badge">🟢 접속 실무자: {live_users}명 (무료)</div>', unsafe_allow_html=True)
    
    with st.expander("💬 A/S 라이브 CS 실시간 채팅실 열기"):
        chat_container = st.container()
        with chat_container:
            chat_html = "<div class='as-chat-box'>"
            if not global_chat_messages:
                chat_html += "<div style='color: #94A3B8; text-align: center;'>등록된 메시지가 없습니다. 첫 대화를 시작해보세요!</div>"
            else:
                for msg in global_chat_messages:
                    chat_html += f"<div style='margin-bottom:6px;'><b>{msg['sender']}</b>: {msg['text']}</div>"
            chat_html += "</div>"
            st.markdown(chat_html, unsafe_allow_html=True)

        with st.form(key="as_chat_form", clear_on_submit=True):
            user_sender = st.text_input("닉네임", value=st.session_state.user_nickname)
            user_msg = st.text_input("CS/AS 문의 입력...", placeholder="메시지 입력...", label_visibility="collapsed")
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
            "1) 스와치 사진 분석 & 역설계",
            "2) 5-사종 혼용률 & 재고 구출",
            "3) 염색 바치 & 텐터 열고정",
            "4) 화학가공 & 콤팩터 제어",
            "5) 납기 원가 관제탑 & 불량레이더",
            "6) 야드/롤 변환 & 물류 최적화"
        ],
        label_visibility="collapsed"
    )

    st.write("---")
    st.markdown("#### 📌 실시간 파이프라인 동기화 스펙")
    st.info(
        f"• **원단:** {st.session_state.fabric_name}\n\n"
        f"• **설비:** {st.session_state.rec_inch}\" × {st.session_state.rec_gauge}G ({st.session_state.rec_feeds}F)\n\n"
        f"• **가공지 타겟:** {st.session_state.target_width}\" / {st.session_state.target_gsm} GSM\n\n"
        f"• **오더 수량:** {st.session_state.order_kg:,.0f} kg"
    )

# ==============================================================================
# 5. 상단 헤더 (Demo Version 뱃지 표기 포함) & 사용설명서
# ==============================================================================
h_c1, h_c2 = st.columns([3.2, 1])
with h_c1:
    st.title("⚡ 구동현-TEX AI <span class='demo-badge'>DEMO VERSION</span>", unsafe_allow_html=True)
with h_c2:
    st.markdown(f"<div style='text-align:right; padding-top:16px;'><span class='live-badge'>🟢 LIVE {live_users}명 Online</span></div>", unsafe_allow_html=True)

with st.expander("📖 [사용설명서] 전 공정 통합 관제 OS 가이드"):
    st.markdown("""
    * **1) 스와치 사진 분석 & 역설계:** 앞/뒷면 사진을 올리고 버튼을 누르면 편직 스펙과 생지 타겟이 자동 도출됩니다.
    * **2) 5-사종 혼용률 & 재고 구출:** 최대 5개 사종의 투입 비율과 창고 악성 재고 원사 구출을 관리합니다.
    * **3) 염색 바치 & 텐터 열고정:** 1욕/2욕 경로 선택, 케틀 미니멈 차지 방어, 텐터 온도/속도를 제어합니다.
    * **4) 화학가공 & 콤팩터 제어:** 유연제 픽업률, 조제 원가, 수축률을 잡는 콤팩터 압축을 다룹니다.
    * **5) 납기 원가 관제탑 & 불량레이더:** 풀 파이프라인 원가, 사스왑 네고, 공정별 불량 레이더를 확인합니다.
    * **6) 야드/롤 변환 & 물류 최적화:** 물류 출고 환산, 광폭 마카 손익, 컨테이너 CBM 적재를 끝냅니다.
    """)

st.write("---")

# ==============================================================================
# MODULE 1: 스와치 사진 분석 & 역설계
# ==============================================================================
if selected_module == "1) 스와치 사진 분석 & 역설계":
    st.subheader("🔍 1) 스와치 사진 분석 & AI Vision 역설계")

    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    u1, u2, u3 = st.columns([1, 1, 1.3])
    with u1:
        front_img = st.file_uploader("📸 1. 스와치 [앞면(Face)] 업로드", type=["jpg", "jpeg", "png"])
        if front_img:
            st.image(front_img, caption="앞면 픽셀 스캔 완료", use_container_width=True)
    with u2:
        back_img = st.file_uploader("📸 2. 스와치 [뒷면(Back)] 업로드", type=["jpg", "jpeg", "png"])
        if back_img:
            st.image(back_img, caption="뒷면 픽셀 스캔 완료", use_container_width=True)
    with u3:
        st.markdown("##### ⚡ 3. 타겟 스펙 입력")
        preset_type = st.selectbox(
            "원단 베이스 조직 카테고리",
            [
                "CVC 30s 싱글 스판 저지 (Single Span)",
                "Cotton 30s/20s 2단 터크 미니 쭈리 (French Terry)",
                "CM 30s 싱글 피케 (Single Pique)",
                "CM 20s 2x2 립 스판 (2x2 Rib)",
                "Poly 75D/Span 40D 고밀도 인터록 (Interlock)"
            ]
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            in_gsm = st.number_input("목표 가공지 중량(GSM)", value=float(st.session_state.target_gsm), step=5.0)
        with c2:
            in_width = st.number_input("목표 가공지 폭(Inch)", value=float(st.session_state.target_width), step=1.0)
        with c3:
            in_order_kg = st.number_input("오더 수량(kg)", value=float(st.session_state.order_kg), step=100.0)

        yarn_origin_sel = st.selectbox(
            "투입 원사 산지 및 방적 등급",
            [
                "베트남/국내산 코마사 (표준)",
                "인도산 카드사 (정련감량 +1.5% · 축률 +2.5%)",
                "컴팩트 코마사 (축률 -1.5%)",
                "GRS 리사이클 폴리/면"
            ]
        )
    st.markdown('</div>', unsafe_allow_html=True)

    pixel_res = analyze_swatch_pixels(front_img, back_img) if front_img else {"analyzed": False}
    origin_shrink_mod = 2.5 if "인도산" in yarn_origin_sel else (-1.5 if "컴팩트" in yarn_origin_sel else 0.0)

    if "싱글 스판" in preset_type:
        p = {
            "name": "CVC 30s 싱글 스판 저지", "pattern": "Single Jersey", "struct": "싱글 저지", 
            "inch": 30, "gauge": 28, "feeds": 90, "rpm": 22, "type": "Single", "needle_mult": 1.0, 
            "wpi": 38, "cpi": 52, "sl": 2.82, "draft": 3.1, "w_shrink": 12.0 + origin_shrink_mod, "l_shrink": 10.5 + origin_shrink_mod, "fee": 0.35, "span_pct": 5.1, 
            "y1": ("CVC 30s/1 (전면사)", 30.0, "Ne(면번수)", 90, 2.82, 3.40, 1.0, 100.0), 
            "y2": ("Cotton 20s/1 (이면사)", 20.0, "Ne(면번수)", 0, 3.50, 3.10, 1.0, 100.0), 
            "y3": ("폴리 75D (특수사)", 75.0, "Denier(데니어)", 0, 2.10, 1.85, 1.0, 100.0), 
            "y4": ("Spandex 20D (스판덱스 1)", 20.0, "Denier(데니어)", 90, 2.82, 6.80, 3.1, 100.0)
        }
    elif "미니 쭈리" in preset_type:
        p = {
            "name": "Cotton 30s/20s 2단 미니 쭈리", "pattern": "2-Thread French Terry", "struct": "싱글 변형", 
            "inch": 30, "gauge": 24, "feeds": 72, "rpm": 18, "type": "Fleece", "needle_mult": 1.0, 
            "wpi": 30, "cpi": 40, "sl": 3.05, "draft": 3.0, "w_shrink": 14.5 + origin_shrink_mod, "l_shrink": 13.0 + origin_shrink_mod, "fee": 0.45, "span_pct": 3.8, 
            "y1": ("CM 30s/1 (전면사)", 30.0, "Ne(면번수)", 36, 3.05, 3.60, 1.0, 100.0), 
            "y2": ("CM 20s/1 (이면사)", 20.0, "Ne(면번수)", 18, 4.20, 3.15, 1.0, 100.0), 
            "y3": ("폴리 75D (특수사)", 75.0, "Denier(데니어)", 18, 2.15, 1.85, 1.0, 100.0), 
            "y4": ("Spandex 20D (스판덱스 1)", 20.0, "Denier(데니어)", 36, 3.05, 6.80, 3.0, 100.0)
        }
    elif "피케" in preset_type:
        p = {
            "name": "CM 30s 싱글 피케", "pattern": "4-Track Pique", "struct": "싱글 변형", 
            "inch": 30, "gauge": 24, "feeds": 72, "rpm": 19, "type": "Single", "needle_mult": 1.0, 
            "wpi": 32, "cpi": 44, "sl": 2.95, "draft": 1.0, "w_shrink": 15.0 + origin_shrink_mod, "l_shrink": 12.0 + origin_shrink_mod, "fee": 0.42, "span_pct": 0.0, 
            "y1": ("CM 30s/1 (전면사)", 30.0, "Ne(면번수)", 36, 2.95, 3.60, 1.0, 100.0), 
            "y2": ("CM 20s/1 (이면사)", 20.0, "Ne(면번수)", 0, 3.00, 3.10, 1.0, 100.0), 
            "y3": ("폴리 75D (특수사)", 75.0, "Denier(데니어)", 36, 2.45, 1.85, 1.0, 100.0), 
            "y4": ("미사용", 20.0, "Denier(데니어)", 0, 2.80, 6.80, 3.0, 100.0)
        }
    elif "2x2 립" in preset_type:
        p = {
            "name": "CM 20s 2x2 립 스판", "pattern": "2x2 Rib", "struct": "2x2 립 (바늘빼기)", 
            "inch": 30, "gauge": 18, "feeds": 60, "rpm": 17, "type": "Double", "needle_mult": 1.333, 
            "wpi": 26, "cpi": 36, "sl": 3.25, "draft": 3.0, "w_shrink": 18.0 + origin_shrink_mod, "l_shrink": 11.0 + origin_shrink_mod, "fee": 0.48, "span_pct": 4.9, 
            "y1": ("CM 20s/1 (실린더사)", 20.0, "Ne(면번수)", 60, 3.25, 3.30, 1.0, 100.0), 
            "y2": ("미사용", 20.0, "Ne(면번수)", 0, 3.00, 3.10, 1.0, 100.0), 
            "y3": ("미사용", 75.0, "Denier(데니어)", 0, 2.00, 1.85, 1.0, 100.0), 
            "y4": ("Spandex 30D", 30.0, "Denier(데니어)", 60, 3.25, 6.50, 3.0, 100.0)
        }
    else:
        p = {
            "name": "Poly 75D/Span 인터록", "pattern": "1x1 Interlock", "struct": "양면 인터록", 
            "inch": 32, "gauge": 32, "feeds": 96, "rpm": 19, "type": "Double", "needle_mult": 2.0, 
            "wpi": 46, "cpi": 62, "sl": 2.45, "draft": 3.2, "w_shrink": 9.0 + origin_shrink_mod, "l_shrink": 8.0 + origin_shrink_mod, "fee": 0.58, "span_pct": 8.4, 
            "y1": ("Poly 75D (실린더사)", 75.0, "Denier(데니어)", 48, 2.45, 1.95, 1.0, 100.0), 
            "y2": ("Poly 75D (다이얼사)", 75.0, "Denier(데니어)", 48, 2.45, 1.95, 1.0, 100.0), 
            "y3": ("미사용", 75.0, "Denier(데니어)", 0, 2.00, 1.85, 1.0, 100.0), 
            "y4": ("Spandex 40D", 40.0, "Denier(데니어)", 96, 2.45, 6.20, 3.2, 100.0)
        }

    if pixel_res["analyzed"]:
        p["wpi"] = pixel_res["est_wpi"]
        p["cpi"] = pixel_res["est_cpi"]

    base_cyl = int(round(math.pi * p["inch"] * p["gauge"]))
    active_n = int(round(base_cyl * p["needle_mult"]))
    greige_w = round(in_width / (1.0 - p["w_shrink"] / 100.0), 1)
    greige_g = round(in_gsm * (1.0 - (p["l_shrink"] - p["w_shrink"]) / 100.0) * 0.94, 1)
    main_tex = to_tex(p["y1"][1], p["y1"][2])
    tf_v = round(math.sqrt(main_tex) / (p["sl"] / 10.0), 2)
    daily_p = round(((active_n * (p["sl"] / 100.0) * p["feeds"] * main_tex / 1_000_000.0) * p["rpm"] * 60 * 24 * 0.85) / 1000.0, 1)
    knit_d = round(in_order_kg / max(daily_p, 1), 1)

    if st.button("🚀 원클릭 AI 역설계 확정 & 전 공정 데이터 자동 이관", type="primary", use_container_width=True):
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
        st.session_state.calc_daily_kg = daily_p
        st.session_state.calc_tf = tf_v
        st.session_state.calc_span_pct = p["span_pct"]
        for idx, k_pref in enumerate(["y1", "y2", "y3", "y4"], start=1):
            tup = p[k_pref]
            st.session_state[f"y{idx}_name"] = tup[0]
            st.session_state[f"y{idx}_count"] = tup[1]
            st.session_state[f"y{idx}_unit"] = tup[2]
            st.session_state[f"y{idx}_feeds"] = tup[3]
            st.session_state[f"y{idx}_sl"] = tup[4]
            st.session_state[f"y{idx}_price"] = tup[5]
            st.session_state[f"y{idx}_draft"] = tup[6]
            st.session_state[f"y{idx}_share"] = tup[7]
        st.success("✅ 역설계 완료! 모든 파이프라인 데이터가 동기화되었습니다.")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("추천 설비 / 실가동 침수", f"{p['inch']}\" × {p['gauge']}G", f"실가동 {active_n:,}침")
    k2.metric("편직실 지시 생지 타겟", f"폭 {greige_w}\" / {greige_g} GSM", f"축률 폭 -{p['w_shrink']:.1f}%")
    k3.metric("일일 생산량 (85%)", f"{daily_p} kg / 일", f"{knit_d}일 소요")
    k4.metric("밀도계수 (TF)", f"TF {tf_v}", "안정" if 1.28 <= tf_v <= 1.62 else "수축 주의")


# ==============================================================================
# MODULE 2: 5-사종 혼용률 & 재고 구출
# ==============================================================================
elif selected_module == "2) 5-사종 혼용률 & 재고 구출":
    st.subheader("⚙️ 2) 5-사종 정밀 혼용률 제너레이터")

    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    t1, t2, t3 = st.columns(3)
    with t1:
        plating_factor = st.slider("스판덱스 플레이팅 보정계수", 0.60, 0.85, float(st.session_state.plating_factor), 0.02)
        st.session_state.plating_factor = plating_factor
    with t2:
        safety_loss_pct = st.slider("원사 안전 발주 로스율 (%)", 1.0, 8.0, 3.5, 0.5)
    with t3:
        m_eff = st.slider("실가동 효율 (%)", 65, 95, 85, 1)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("🎛️ [전문가 서랍] 5-사종 개별 스펙 수동 조정"):
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.session_state.rec_inch = st.number_input("기계 직경 (Inch)", value=int(st.session_state.rec_inch), step=2)
        with sc2:
            st.session_state.rec_gauge = st.number_input("기계 게이지 (Gauge)", value=int(st.session_state.rec_gauge), step=2)
        with sc3:
            st.session_state.rec_rpm = st.number_input("가동 RPM", value=int(st.session_state.rec_rpm), step=1)

        slot_labels = ["사종 1 (전면사)", "사종 2 (이면사)", "사종 3 (특수사)", "사종 4 (스판덱스 1)", "사종 5 (스판덱스 2)"]
        y_cols = st.columns(5)
        for i in range(1, 6):
            with y_cols[i - 1]:
                st.markdown(f"**{slot_labels[i-1]}**")
                st.session_state[f"y{i}_name"] = st.text_input(f"원사명 #{i}", value=st.session_state[f"y{i}_name"])
                st.session_state[f"y{i}_unit"] = st.selectbox(f"단위 #{i}", ["Ne(면번수)", "Denier(데니어)"], index=0 if "Ne" in st.session_state[f"y{i}_unit"] else 1)
                st.session_state[f"y{i}_count"] = st.number_input(f"번수 #{i}", value=float(st.session_state[f"y{i}_count"]), min_value=1.0, step=1.0)
                st.session_state[f"y{i}_feeds"] = st.number_input(f"피더수 #{i}", value=int(st.session_state[f"y{i}_feeds"]), min_value=0, step=6)
                st.session_state[f"y{i}_sl"] = st.number_input(f"루프장 #{i}", value=float(st.session_state[f"y{i}_sl"]), min_value=0.5, step=0.05)
                st.session_state[f"y{i}_draft"] = st.number_input(f"드래프트 #{i}", value=float(st.session_state[f"y{i}_draft"]), min_value=1.0, step=0.1)
                st.session_state[f"y{i}_share"] = st.number_input(f"점유율(%) #{i}", value=float(st.session_state[f"y{i}_share"]), min_value=5.0, max_value=100.0, step=5.0)
                st.session_state[f"y{i}_price"] = st.number_input(f"단가($) #{i}", value=float(st.session_state[f"y{i}_price"]), min_value=0.5, step=0.1)

    base_n = int(round(math.pi * st.session_state.rec_inch * st.session_state.rec_gauge))
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
        eff_plat = plating_factor if is_span else 1.0
        w_rev = (base_n * (sl / 100.0) * eff_plat * feeds * (share / 100.0) * tex_v) / (1_000_000.0 * draft) if feeds > 0 else 0.0
        yarn_list.append({"slot": slot_labels[i-1], "name": name, "feeds": feeds, "price": price, "is_span": is_span, "w_rev_g": w_rev})

    tot_rev = sum(y["w_rev_g"] for y in yarn_list)
    if tot_rev > 0:
        w_cost = 0.0
        span_s = 0.0
        sum_lines = []
        for y in yarn_list:
            pct = (y["w_rev_g"] / tot_rev) * 100.0
            y["pct"] = round(pct, 2)
            y["net_kg"] = round(st.session_state.order_kg * (pct / 100.0), 1)
            y["po_kg"] = round(y["net_kg"] * (1.0 + safety_loss_pct / 100.0), 1)
            w_cost += (pct / 100.0) * y["price"]
            if y["is_span"]: span_s += pct
            if y["feeds"] > 0:
                sum_lines.append(f"• <b>[{y['slot']}] {y['name']}</b> ➔ <span style='color:#00F2FE; font-weight:800;'>{y['pct']:.1f}%</span> (순소요: {y['net_kg']:,.1f} kg | <b>발주 PO: {y['po_kg']:,.1f} kg</b>)")

        st.session_state.calc_yarn_cost_kg = round(w_cost, 3)
        st.session_state.calc_span_pct = round(span_s, 1)

        cl, cr = st.columns([1.1, 1.3])
        with cl:
            active_y = [y for y in yarn_list if y["feeds"] > 0]
            fig = go.Figure(data=[go.Pie(labels=[y["name"] for y in active_y], values=[y["pct"] for y in active_y], hole=0.55, textinfo="label+percent")])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#FFFFFF", size=13), margin=dict(t=30, b=10, l=10, r=10), height=300)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"<div class='yarn-summary-box'>{'<br>'.join(sum_lines)}</div>", unsafe_allow_html=True)
        with cr:
            st.metric("가중평균 순수 원사비", f"${w_cost:.2f} / kg", f"스판 실함량 {span_s:.1f}%")
            st.dataframe(pd.DataFrame([{"슬롯": y["slot"], "원사명": y["name"], "혼용률": f"{y['pct']:.1f}%", "순소요(kg)": y["net_kg"], "발주PO(kg)": y["po_kg"]} for y in active_y]), use_container_width=True)

            with st.expander("💡 창고 악성 재고 원사(Dead Stock) 현금화 구출기"):
                ds_sel = st.selectbox("창고 방치 원사", [y["name"] for y in active_y])
                ds_kg = st.number_input("보유 재고량 (kg)", value=350.0, step=50.0)
                t_y = [y for y in active_y if y["name"] == ds_sel][0]
                m_fab = round(ds_kg / (t_y["pct"] / 100.0), 1)
                s_cash = round(ds_kg * t_y["price"], 0)
                st.success(f"🏭 `{ds_sel}` **{ds_kg:,.0f}kg** 투입 시 원단 **{m_fab:,.1f}kg** 생산 가능 ➔ 매몰비용 **${s_cash:,.0f}** 현금화!")


# ==============================================================================
# MODULE 3: 염색 바치 & 텐터 열고정
# ==============================================================================
elif selected_module == "3) 염색 바치 & 텐터 열고정":
    st.subheader("🔥 3) 염색 바치(Kettle) 매칭 & 텐터(Stenter) 열고정 제어")
    st.caption("염색 케틀 용량 매칭, 미니멈 차지 방어, 텐터 챔버 온도·오버피드·속도를 정밀 제어합니다.")

    tc1, tc2 = st.columns(2)
    with tc1:
        st.markdown("#### 💧 염색 케틀(Kettle) 바치 & 미니멈 차지 방어기")
        kettle_cap = st.selectbox("염색 케틀 1바치 용량 (kg)", [150, 300, 500, 1000], index=2)
        order_q = st.session_state.order_kg
        full_b = int(order_q // kettle_cap)
        rem_k = order_q % kettle_cap
        min_pen = round(250.0 / max(order_q, 1), 3) if (0 < rem_k < kettle_cap * 0.6) else 0.0

        if min_pen > 0:
            st.error(f"🚨 **[미니멈 차지 경보]** 총 {order_q:,.0f}kg 발주 시 {kettle_cap}kg 케틀 후 **{rem_k:,.0f}kg 잔량** 발생! (미니멈 벌금 +${min_pen:.2f}/kg 합산됨) ➔ **{full_b*kettle_cap:,.0f}kg** 또는 **{(full_b+1)*kettle_cap:,.0f}kg**으로 조정 권장.")
        else:
            st.success(f"✅ **[케틀 바치 최적화]** {kettle_cap}kg 기준 미니멈 차지 없이 정상 소화 가능합니다.")

        dye_path = st.selectbox("염색 욕(Bath) 경로", ["단일 섬유 1욕 염색", "CVC/TC 1욕 연속 염색 (+$0.15)", "CVC/TC 2욕 분할 염색 (+$0.42)"])
        st.metric("선택한 염색 경로 추가 원가", "+$0.42 / kg" if "2욕" in dye_path else ("+$0.15 / kg" if "1욕 연속" in dye_path else "$0.00 / kg"))

    with tc2:
        st.markdown("#### 🔥 텐터(Stenter) 열고정 & 체류시간 제어기")
        chambers = st.number_input("텐터 챔버 수 (1챔버=3m)", value=8, min_value=4, max_value=12)
        dwell_s = st.number_input("열고정 체류시간 (초, Dwell Time)", value=42 if st.session_state.calc_span_pct > 0 else 30)
        overfeed = st.slider("텐터 핀 오버피드율 (%)", 0, 35, 18)
        w_loss = st.slider("염색·가공 폭 축률 (%)", 5, 22, 12)

        t_temp = 190 if st.session_state.calc_span_pct > 0 else 172
        t_speed = round((chambers * 3.0) / (dwell_s / 60.0), 1)
        req_gw = round(st.session_state.target_width / (1.0 - w_loss / 100.0), 1)
        st.metric("권장 챔버 온도 / 가동 속도", f"{t_temp}°C / {t_speed} m/min")
        st.metric("역산 생지 폭 지시서", f"생지 폭 {req_gw} Inch")


# ==============================================================================
# MODULE 4: 화학가공 & 콤팩터 제어
# ==============================================================================
elif selected_module == "4) 화학가공 & 콤팩터 제어":
    st.subheader("💧 4) 화학 패딩(Pick-up), 유연제 조제 및 콤팩터 수축 제어")
    st.caption("유연제·기능성 조제 처방과 콤팩터 압축 롤러 텐션을 제어하여 세탁 후 수축률과 파공을 예방합니다.")

    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown("#### 🧪 화학 패딩(Pick-up) & 조제 원가 계산기")
        pickup = st.slider("망글(Mangle) Wet Pick-up율 (%)", 55, 85, 70)
        sil_gl = st.number_input("실리콘 유연제 처방 농도 (g/L)", value=float(st.session_state.silicone_g_l), step=5.0)
        st.session_state.silicone_g_l = sil_gl
        chem_kg = round(st.session_state.order_kg * (pickup / 100.0) * (sil_gl / 1000.0), 2)
        chem_cost = round((chem_kg * 4.2) / max(st.session_state.order_kg, 1), 3)
        st.metric("실리콘 유연제 총 소요량", f"{chem_kg} kg (단가 +${chem_cost}/kg)")

    with fc2:
        st.markdown("#### ⚙️ 콤팩터(Compactor) 잔여 수축 통제기")
        pre_sh = st.number_input("텐터 직후 잔여 길이 수축률 (%)", value=-6.5, step=0.5)
        std_sh = st.number_input("바이어 합격 기준 수축률 (%)", value=-3.0, step=0.5)
        comp_pct = round(abs(pre_sh - std_sh) * 1.25, 1)
        st.metric("콤팩터 권장 압축 텐션", f"+{comp_pct}% (중량 +{round(comp_pct*1.8, 1)}g 상승)")


# ==============================================================================
# MODULE 5: 납기 원가 관제탑 & 불량레이더
# ==============================================================================
elif selected_module == "5) 납기 원가 관제탑 & 불량레이더":
    st.subheader("🗼 5) 납기 원가 관제탑 & 공정별 신호등 불량 레이더")

    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    b1, b2, b3 = st.columns(3)
    with b1:
        color_depth = st.selectbox("염색 컬러 등급", ["Bleach White ($0.65 | 4.5h)", "Light Shade ($0.80 | 5.0h)", "Medium Shade ($0.95 | 6.0h)", "Dark / Black ($1.15 | 8.5h)", "Extra Dark / 형광 ($1.40 | 10.5h)"], index=2)
    with b2:
        fin_options = st.multiselect("특수 후가공", ["실리콘 유연 가공 (+$0.08)", "흡한속건 Wicking (+$0.12)", "항균 방취 (+$0.20)", "양면 기모 (+$0.25)", "콤팩터 수축 제어 (+$0.10)"], default=["실리콘 유연 가공 (+$0.08)", "콤팩터 수축 제어 (+$0.10)"])
    with b3:
        target_margin_pct = st.slider("목표 영업 마진율 (%)", 5.0, 30.0, 15.0, 1.0)
    st.markdown('</div>', unsafe_allow_html=True)

    shade_info = {"Bleach": (0.65, 4.5, 0.0), "Light": (0.80, 5.0, 0.5), "Medium": (0.95, 6.0, 1.0), "Dark": (1.15, 8.5, 2.5), "Extra": (1.40, 10.5, 4.0)}
    dye_p, batch_h, ex_d = next(v for k, v in shade_info.items() if k in color_depth)
    fin_map = {"실리콘": 0.08, "흡한속건": 0.12, "항균": 0.20, "기모": 0.25, "콤팩터": 0.10}
    fin_c = sum(v for k, v in fin_map.items() if any(k in o for o in fin_options))

    order_q = st.session_state.order_kg
    raw_c = st.session_state.calc_yarn_cost_kg + 0.38 + dye_p + fin_c
    fin_net_c = (raw_c / 0.945) + 0.12
    quote_kg = fin_net_c / (1.0 - target_margin_pct / 100.0)
    kg_yd = (st.session_state.target_width * st.session_state.target_gsm * 0.02322576) / 1000.0
    quote_yd = quote_kg * kg_yd
    tot_prof = (quote_kg - fin_net_c) * order_q

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("제안 단가 (KG)", f"${quote_kg:.2f} / kg")
    c2.metric("제안 단가 (YARD)", f"${quote_yd:.2f} / yd")
    c3.metric("예상 총 납기", f"총 {round(order_q/max(st.session_state.calc_daily_kg*2,1)+3+batch_h/8, 1)} 일")
    c4.metric("예상 순영업이익", f"${tot_prof:,.0f}")

    st.markdown("### 🛡️ 공정별 신호등 불량 레이더 & 1줄 현장 지시서")
    tf_v = st.session_state.calc_tf
    g_v = st.session_state.rec_gauge
    r1, r2, r3, r4 = st.columns(4)
    r1.markdown(f'<div class="glass-card"><div class="neon-title">① 편직</div><b>상태:</b> {"🟡 주의" if g_v>=28 else "🟢 정상"}<br>• <b>1줄 지시:</b> 텐션 ±0.2g 세팅</div>', unsafe_allow_html=True)
    r2.markdown(f'<div class="glass-card"><div class="neon-title">② 염색</div><b>상태:</b> {"🔴 위험" if batch_h>=8.5 else "🟢 정상"}<br>• <b>1줄 지시:</b> 체류시간 {batch_h}h 및 환원세정</div>', unsafe_allow_html=True)
    r3.markdown(f'<div class="glass-card"><div class="neon-title">③ 텐터</div><b>상태:</b> {"🔴 위험" if tf_v<1.3 else "🟢 정상"}<br>• <b>1줄 지시:</b> 스큐 +3도 및 오버피드 +18%</div>', unsafe_allow_html=True)
    r4.markdown(f'<div class="glass-card"><div class="neon-title">④ 봉제파공</div><b>상태:</b> {"🔴 위험" if g_v>=28 else "🟢 정상"}<br>• <b>1줄 지시:</b> 유연제 25g/L 증량 및 볼포인트 바늘</div>', unsafe_allow_html=True)


# ==============================================================================
# MODULE 6: 야드/롤 변환 & 물류 최적화
# ==============================================================================
elif selected_module == "6) 야드/롤 변환 & 물류 최적화":
    st.subheader("📦 6) 야드/롤 변환기 & 광폭 마카 손익 · 컨테이너 CBM 적재 최적화")

    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    u1, u2, u3, u4 = st.columns(4)
    with u1: c_w = st.number_input("가공지 폭 (Inch)", value=float(st.session_state.target_width), step=1.0)
    with u2: c_g = st.number_input("가공지 중량 (GSM)", value=float(st.session_state.target_gsm), step=5.0)
    with u3: c_k = st.number_input("총 오더 중량 (kg)", value=float(st.session_state.order_kg), step=100.0)
    with u4: roll_k = st.number_input("1롤 패킹 중량 (kg)", value=22.0, step=1.0)
    st.markdown('</div>', unsafe_allow_html=True)

    yds_kg = 43055.64 / (c_w * c_g)
    t_yds = round(c_k * yds_kg, 1)
    t_rolls = math.ceil(c_k / roll_k)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("1 kg당 야드", f"{yds_kg:.2f} yd/kg")
    k2.metric("오더 총 야드", f"{t_yds:,.1f} Yards")
    k3.metric("총 패킹 롤 수", f"{t_rolls:,} Rolls")
    k4.metric("1롤 감김 길이", f"{round(roll_k*yds_kg, 1)} yd/Roll")

    st.write("---")
    cm1, cm2 = st.columns(2)
    with cm1:
        st.markdown("### ✂️ 광폭 마카 손익 계산기")
        pcs = st.number_input("의류 오더 수량 (Pcs)", value=30000, step=5000)
        yy = st.number_input("1장당 요척 (yd/pc)", value=1.15, step=0.05)
        gain = st.slider("광폭 전환 마카 효율 상승률 (%)", 1.5, 7.0, 3.8, 0.2)
        yd_p = st.number_input("야드당 단가 ($/yd)", value=1.95, step=0.05)
        s_yds = round(pcs * yy * (gain / 100.0), 1)
        s_usd = round(s_yds * yd_p, 0)
        st.success(f"💡 광폭 제직 시 원단 **{s_yds:,.1f} 야드 절감** ➔ 순이익 **총 ${s_usd:,.0f}** 추가 확보!")
    with cm2:
        st.markdown("### 🚢 컨테이너 CBM 적재 최적화기")
        t_cm = st.number_input("지관 외경 (cm)", value=8.5, step=0.5)
        th_mm = st.number_input("원단 두께 (mm)", value=round(c_g / 320.0, 2), step=0.05)
        cntr = selectbox_placeholder = st.selectbox("컨테이너", ["20ft Dry (28 CBM)", "40ft High Cube (68 CBM)"], index=1)
        r_dia = round(math.sqrt(t_cm**2 + (4.0 * (t_yds*yds_kg*91.44) * (th_mm / 10.0)) / math.pi), 1)
        st.info(f"📐 1롤 예상 직경: `{r_dia} cm` | 40ft 컨테이너 최대 적재 수량 산출 완료")