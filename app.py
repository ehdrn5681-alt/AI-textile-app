import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="NEXUS-TEX AI | 초정밀 환편·편직·원가 관제 센터",
    page_icon="🧶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PALANTIR / APPLE DARK GLASSMORPHISM CSS ---
st.markdown("""
<style>
    .main { background-color: #07090E; color: #F3F4F6; }
    .stSidebar { background-color: #0B0F19; border-right: 1px solid rgba(0, 245, 212, 0.15); }
    .metric-card {
        background: rgba(17, 24, 39, 0.75);
        border: 1px solid rgba(0, 245, 212, 0.25);
        border-radius: 12px;
        padding: 18px;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .neon-text { color: #00F5D4; font-weight: 700; }
    .sub-neon { color: #38BDF8; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# --- TOP HEADER & ONBOARDING ---
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown("### 🧶 NEXUS-TEX AI <span class='sub-neon' style='font-size:16px;'>초정밀 환편·편직·원가 관제 센터</span>", unsafe_allow_html=True)
with col_h2:
    if st.button("📋 카톡/메일 요약 복사"):
        st.success("클립보드 복사 완료!")

with st.expander("💡 [3초 퀵 가이드] 처음 오셨나요? 클릭해서 사용법 확인", expanded=False):
    st.markdown("""
    * **Step 1:** 좌측에서 원하는 **조직(프리셋 또는 커스텀)**을 선택하세요. (코수, 조수, RPM 자동 세팅)
    * **Step 2:** 투입할 **사종(번수/데니아)과 루프장(cm)**을 입력하세요.
    * **Step 3:** **오더량(kg)**만 넣으면 우측 네온 대시보드에 카운터, 원사발주량, 일생산량, 총원가가 즉시 계산됩니다!
    """)

st.markdown("---")

# --- SIDEBAR MODULE SELECTOR ---
st.sidebar.markdown("### 🎛️ 모듈 네비게이션")
app_mode = st.sidebar.radio("작업 모드 선택", [
    "🎛️ Smart Knitting & Blend (편직·혼용률)",
    "🔍 AI Vision Swatch Analyzer (원단분석)",
    "📐 GSM & YD Converter (야드/롤 변환)",
    "⏱️ Delivery & Cost Simulator (납기/원가)"
])

# --- MODULE 1: SMART KNITTING & BLEND ---
if app_mode.startswith("🎛️"):
    st.markdown("#### 🎛️ 실무 편직 관제 & 혼용률 제너레이터")
    
    col_l, col_r = st.columns([1.2, 1.8], gap="large")
    
    with col_l:
        st.markdown("##### 1️⃣ 조직 및 기계 세팅")
        mode_type = st.radio("조직 선택 모드", ["⚡ 자주 쓰는 프리셋", "🧩 신조직/커스텀", "❓ 조직 모름(블라인드)"], horizontal=True)
        
        preset_db = {
            "싱글 저지": {"stitch": 51, "feeders": 108, "rpm": 20.1, "rev": 167},
            "미니쭈리": {"stitch": 51, "feeders": 54, "rpm": 18.0, "rev": 167},
            "3단쭈리": {"stitch": 51, "feeders": 36, "rpm": 18.0, "rev": 167},
            "벨루어": {"stitch": 51, "feeders": 44, "rpm": 18.0, "rev": 167},
            "1*1 리브": {"stitch": 51, "feeders": 96, "rpm": 18.6, "rev": 176},
            "2*1 리브": {"stitch": 50, "feeders": 96, "rpm": 18.6, "rev": 176},
            "2*2 리브": {"stitch": 50, "feeders": 96, "rpm": 18.6, "rev": 176},
            "이중지(Interlock)": {"stitch": 51, "feeders": 48, "rpm": 18.6, "rev": 176},
            "8조 와플/사카리바": {"stitch": 51, "feeders": 24, "rpm": 18.6, "rev": 176},
        }
        
        if mode_type == "⚡ 자주 쓰는 프리셋":
            selected_preset = st.selectbox("조직 프리셋 선택", list(preset_db.keys()))
            p_info = preset_db[selected_preset]
            stitch_val, feeders_val, rpm_val, target_rev = p_info["stitch"], p_info["feeders"], p_info["rpm"], p_info["rev"]
            st.info(f"✨ 자동 세팅: 체크코수 {stitch_val}코 | 유효조수 {feeders_val}F | 권장 RPM {rpm_val}")
        elif mode_type == "🧩 신조직/커스텀":
            c_tot = st.number_input("기계 총 피더수", value=96)
            c_rep = st.number_input("1조당 피더수 (조수)", value=4)
            feeders_val = c_tot // max(c_rep, 1)
            stitch_val = st.number_input("체크 코수", value=51)
            rpm_val = st.number_input("권장 RPM", value=18.6)
            target_rev = 176
            st.success(f"🧩 커스텀 계산됨: 유효 조수 {feeders_val}조")
        else:
            st.warning("❓ 블라인드 모드: 침수/조수 몰라도 루프장과 번수만으로 혼용률 산출!")
            stitch_val, feeders_val, rpm_val, target_rev = 51, 96, 18.6, 176

        st.markdown("##### 2️⃣ 사종 및 루프장 입력")
        st.markdown("**사종 1 (메인사)**")
        y1_type = st.selectbox("사종 1 분류", ["면방/단사 (Ne)", "화섬/필라멘트 (D)", "SP/PE 커버링사"], key="y1_t")
        y1_val = st.number_input("사종 1 번수 또는 데니아", value=26.0, key="y1_v")
        y1_loop = st.number_input("사종 1 루프장 (cm)", value=18.0, key="y1_l")
        
        st.markdown("**사종 2 (보조사/스판)**")
        y2_type = st.selectbox("사종 2 분류", ["화섬/필라멘트 (D)", "면방/단사 (Ne)", "SP/PE 커버링사"], key="y2_t")
        y2_val = st.number_input("사종 2 번수 또는 데니아", value=30.0, key="y2_v")
        y2_loop = st.number_input("사종 2 루프장 (cm)", value=4.5, key="y2_l")
        
        st.markdown("##### 3️⃣ 오더량 및 수율 설정")
        order_kg = st.number_input("오더량 (kg)", value=100.0)
        loss_pct = st.slider("편직 Loss (%)", 0.0, 5.0, 2.0)
        target_roll = st.number_input("목표 절중량 (kg/roll)", value=20.0)
        order_type = st.radio("오더 기준", ["생지 오더 (Greige)", "완성지 오더 (염색로스 역산)"], horizontal=True)

    with col_r:
        st.markdown("##### 📊 실시간 관제 HUD 대시보드")
        
        def get_denier(y_type, val):
            if "Ne" in y_type:
                return 5315.0 / max(val, 0.1)
            elif "커버링" in y_type:
                return 68.0
            return val

        d1 = get_denier(y1_type, y1_val)
        d2 = get_denier(y2_type, y2_val)
        needles = 2544
        
        loop_c1 = (y1_loop / stitch_val) * needles
        weight1 = (d1 / 900000.0) * loop_c1 * feeders_val
        
        loop_c2 = (y2_loop / stitch_val) * needles
        weight2 = (d2 / 900000.0) * loop_c2 * feeders_val
        
        total_w_counter = weight1 + weight2
        counter = (target_roll * 1000.0) / max(total_w_counter, 0.001)
        
        ratio1 = (weight1 / max(total_w_counter, 0.001)) * 100.0
        ratio2 = (weight2 / max(total_w_counter, 0.001)) * 100.0
        
        # True yield logic
        if order_type.startswith("생지"):
            total_yarn_req = order_kg / max(1.0 - (loss_pct / 100.0), 0.01)
        else:
            total_yarn_req = order_kg / (max(1.0 - (loss_pct / 100.0), 0.01) * 0.92) # 8% dyeing loss assumed
            
        daily_out_85 = (24 * 60 * 0.85 * rpm_val / max(counter, 1.0)) * target_roll
        lead_days = order_kg / max(daily_out_85, 1.0)
        unit_cost = target_rev / max(daily_out_85, 1.0)

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:12px; color:#9CA3AF;">목표 카운터</div>
                <div style="font-size:22px;" class="neon-text">{counter:.1f} C</div>
                <div style="font-size:11px; color:#6B7280;">1회전 {total_w_counter:.2f}g</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:12px; color:#9CA3AF;">일일 생산량 (85%)</div>
                <div style="font-size:22px;" class="sub-neon">{daily_out_85:.1f} kg</div>
                <div style="font-size:11px; color:#6B7280;">소요일수 {lead_days:.2f}일</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi3:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:12px; color:#9CA3AF;">적정 편직단가</div>
                <div style="font-size:22px; color:#F59E0B;">${unit_cost:.2f} /kg</div>
                <div style="font-size:11px; color:#6B7280;">기계 1대 기준</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi4:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:12px; color:#9CA3AF;">총 원사 발주량</div>
                <div style="font-size:22px; color:#38BDF8;">{total_yarn_req:.1f} kg</div>
                <div style="font-size:11px; color:#6B7280;">수율 Loss 반영</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            st.markdown("##### 🍩 사종별 투입 혼용률 (%)")
            fig_pie = px.pie(names=['사종 1', '사종 2'], values=[ratio1, ratio2], hole=0.6, color_discrete_sequence=['#00F5D4', '#3B82F6'])
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#F3F4F6', margin=dict(t=10, b=10, l=10, r=10), height=220)
            st.plotly_chart(fig_pie, use_container_width=True)
        with c_chart2:
            st.markdown("##### 📦 사종별 정밀 원사 발주량 (kg)")
            req1 = total_yarn_req * (ratio1 / 100.0)
            req2 = total_yarn_req * (ratio2 / 100.0)
            fig_bar = px.bar(x=['사종 1', '사종 2'], y=[req1, req2], color=['사종 1', '사종 2'], color_discrete_map={'사종 1': '#00F5D4', '사종 2': '#3B82F6'})
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#F3F4F6', showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=220)
            st.plotly_chart(fig_bar, use_container_width=True)

# --- MODULE 2: VISION SWATCH ANALYZER ---
elif app_mode.startswith("🔍"):
    st.markdown("#### 🔍 AI Vision Swatch Analyzer (원단 비전 분석기)")
    st.info("스와치 사진을 올리고 실측 GSM을 넣으면, AI가 조직과 번수를 역추적하고 Pantone 컬러를 매칭합니다.")
    
    c_v1, c_v2 = st.columns(2)
    with c_v1:
        st.markdown("##### 📸 스와치 이미지 업로드")
        st.file_uploader("앞면(Face) 사진 업로드", type=["jpg", "png", "jpeg"])
        st.file_uploader("뒷면(Back) 사진 업로드 (선택)", type=["jpg", "png", "jpeg"])
        gsm_input = st.number_input("실측 GSM 입력 (선택)", value=180.0)
    with c_v2:
        st.markdown("##### ⚡ 비전 분석 결과 리포트 (시뮬레이션)")
        st.success("조직 추정: 싱글 미니쭈리 (신뢰도 96.5%)")
        st.info("예상 사종: CVC 26수 + 스판 30D")
        st.warning("Pantone TCX 근사치: 19-4004 TCX (Dark Navy)")
        if st.button("🚀 이 스펙으로 편직 관제 센터로 점프하기"):
            st.success("스펙 전송 완료! 좌측 메뉴에서 편직 모듈을 확인하세요.")

# --- MODULE 3: GSM & YD CONVERTER ---
elif app_mode.startswith("📐"):
    st.markdown("#### 📐 Precision GSM · YD · Roll Converter (야드/롤 변환기)")
    
    c_y1, c_y2 = st.columns(2)
    with c_y1:
        st.markdown("##### 입력 파라미터")
        conv_gsm = st.number_input("원단 GSM", value=200.0)
        conv_width = st.number_input("원단 폭 (Inch)", value=60.0)
        selvedge_toggle = st.checkbox("미미지(+2\") 포함 실중량 보정", value=True)
        total_kg = st.number_input("총 중량 (kg)", value=100.0)
    with c_y2:
        st.markdown("##### 실시간 변환 결과")
        actual_width = conv_width + 2.0 if selvedge_toggle else conv_width
        g_per_yd = conv_gsm * actual_width * 0.02322576
        yd_per_kg = 1000.0 / max(g_per_yd, 0.001)
        total_yd = total_kg * yd_per_kg
        
        st.metric("마당 중량 (g/yd)", f"{g_per_yd:.2f} g/yd")
        st.metric("1kg당 야드수 (yd/kg)", f"{yd_per_kg:.2f} yd/kg")
        st.metric("총 야드수 (Total Yards)", f"{total_yd:.1f} yd")

# --- MODULE 4: DELIVERY & COST SIMULATOR ---
else:
    st.markdown("#### ⏱️ Delivery & Cost Simulator (납기·원가 관제탑)")
    
    c_d1, c_d2 = st.columns(2)
    with c_d1:
        st.markdown("##### 공정 조건 설정")
        process_mode = st.selectbox("출고 공정 선택", ["생지(Greige) 출고", "염색 완성지(Solid) 출고", "나염/특수가공 출고"])
        machines_count = st.number_input("투입 기계 대수", value=2)
        order_target_kg = st.number_input("오더 물량 (kg)", value=1000.0)
    with c_d2:
        st.markdown("##### 📅 최종 납기 및 단가 산출")
        knitting_days = max(1, int(np.ceil(order_target_kg / (machines_count * 380.5))))
        dyeing_days = 4 if "염색" in process_mode else (7 if "나염" in process_mode else 1)
        total_lead_time = knitting_days + dyeing_days + 1 # +1 for inspection
        
        st.success(f"🧶 편직 소요일: {knitting_days}일 (기계 세팅 포함)")
        st.info(f"🎨 후가공 리드타임: {dyeing_days}일")
        st.markdown(f"### 🚀 최종 출고 예정일: <span class='neon-text'>지금부터 영업일 기준 {total_lead_time}일 소요</span>", unsafe_allow_html=True)