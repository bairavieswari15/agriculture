"""
AgriSmart TN — Modern Agritech Platform (Standalone Version)
Runs directly on Streamlit Cloud without external FastAPI backend server.
"""

import streamlit as st
import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json

try:
    from utils.theme import apply_custom_theme
    from utils.translations import t, crop_t, TRANSLATIONS
except ImportError:
    from theme import apply_custom_theme
    from translations import t, crop_t, TRANSLATIONS

try:
    from backend.data import TN_DISTRICTS, CROP_DB, CROP_EXCLUSION, HISTORICAL_YIELD, HIST_YEARS
    from backend.services import (
        calc_profit, fmt_inr,
        get_live_weather, weather_desc,
        get_ai_response, get_ai_conclusion,
        get_ai_market_report, get_ai_crop_calendar,
        get_soil_info, get_irrigation_info,
        crop_suitability, build_ml_dataset,
        diagnose_pest_disease, generate_farm_pdf_report,
        match_government_schemes, get_crop_timeline,
        calc_mandi_transport_profit, get_district_weather_risk,
        calc_equipment_labor_cost, calc_seed_requirement, calc_crop_plan, rank_crops,
        calc_solar_pump_roi, predict_crop_yield_ml
    )
except ImportError:
    from data import TN_DISTRICTS, CROP_DB, CROP_EXCLUSION, HISTORICAL_YIELD, HIST_YEARS
    from services import (
        calc_profit, fmt_inr,
        get_live_weather, weather_desc,
        get_ai_response, get_ai_conclusion,
        get_ai_market_report, get_ai_crop_calendar,
        get_soil_info, get_irrigation_info,
        crop_suitability, build_ml_dataset,
        diagnose_pest_disease, generate_farm_pdf_report,
        match_government_schemes, get_crop_timeline,
        calc_mandi_transport_profit, get_district_weather_risk,
        calc_equipment_labor_cost, calc_seed_requirement, calc_crop_plan, rank_crops,
        calc_solar_pump_roi, predict_crop_yield_ml
    )

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG & THEME SETUP
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AgriSmart TN — Modern Agritech Platform",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global custom agritech theme
apply_custom_theme()

# ─────────────────────────────────────────────────────────────────────────────
# STANDALONE DATA HELPERS
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def fetch_all_districts():
    return {
        "districts": list(TN_DISTRICTS.keys()),
        "total": len(TN_DISTRICTS),
        "data": TN_DISTRICTS
    }

@st.cache_data(ttl=3600)
def fetch_all_crops():
    return {
        "crops": list(CROP_DB.keys()),
        "total": len(CROP_DB),
        "data": CROP_DB
    }

@st.cache_data(ttl=3600)
def fetch_historical_yield():
    return {
        "years": HIST_YEARS,
        "data": HISTORICAL_YIELD
    }

def fetch_weather(district_name: str):
    if district_name not in TN_DISTRICTS:
        return None
    dd = TN_DISTRICTS[district_name]
    weather = get_live_weather(dd["lat"], dd["lon"], district_name)
    return {
        "district": district_name,
        "static": dd,
        "live": weather,
        "available": weather is not None
    }

def save_profile(profile_data: dict):
    if "saved_profiles" not in st.session_state:
        st.session_state["saved_profiles"] = {}
    key = profile_data.get("phone_email") or profile_data.get("phone") or "default"
    st.session_state["saved_profiles"][key] = profile_data
    return {"status": "success", "message": "Profile saved", "profile": profile_data}

def login_profile(phone_or_email: str):
    profiles = st.session_state.get("saved_profiles", {})
    if phone_or_email in profiles:
        return profiles[phone_or_email]
    return None

def fetch_smart_crops(district: str, land_acres: float, soil_type: str = "", irrigation: str = "", season: str = "All", min_profit: float = 0):
    if district not in TN_DISTRICTS:
        return []
    return rank_crops(district, land_acres, soil_type, irrigation, season, min_profit)

def fetch_seed_planner(crop: str, land_acres: float):
    if crop not in CROP_DB:
        return {}
    return calc_seed_requirement(crop, land_acres)

def fetch_crop_plan(crop: str, land_acres: float, yield_factor: float = 1.0):
    if crop not in CROP_DB:
        return {}
    return calc_crop_plan(crop, land_acres, district="Thoothukudi", yield_factor=yield_factor)

def fetch_profit(crop: str, land_ha: float, factor: float = 1.0):
    if crop not in CROP_DB:
        return None
    return calc_profit(crop, land_ha, factor)

def fetch_ai_advisor(messages: list, district: str, land_ha: float,
                     farmer_name: str, api_key: str = "", selected_crop: str = None, profile: dict = None) -> str:
    dd = TN_DISTRICTS.get(district, TN_DISTRICTS.get("Thoothukudi", {}))
    return get_ai_response(messages, district, dd, land_ha, farmer_name, api_key, selected_crop, profile)

def fetch_ai_conclusion(district: str, land_ha: float, farmer_name: str, crop: str, api_key: str = "") -> str:
    dd = TN_DISTRICTS.get(district, TN_DISTRICTS.get("Thoothukudi", {}))
    return get_ai_conclusion(district, dd, land_ha, farmer_name, crop, api_key)

def fetch_soil_info(district: str, crop: str):
    if district not in TN_DISTRICTS or crop not in CROP_DB:
        return {}
    return get_soil_info(TN_DISTRICTS[district], crop)

def fetch_irrigation_info(district: str, land_ha: float, crop: str):
    if district not in TN_DISTRICTS or crop not in CROP_DB:
        return {}
    return get_irrigation_info(TN_DISTRICTS[district], land_ha, crop)

def fetch_pest_scanner(crop: str, symptom: str = "", image_b64: str = "", api_key: str = ""):
    return diagnose_pest_disease(crop, symptom, image_b64, api_key)

def fetch_pdf_report(district: str, farmer_name: str, land_ha: float, crop: str):
    dd = TN_DISTRICTS.get(district, TN_DISTRICTS.get("Thoothukudi", {}))
    return generate_farm_pdf_report(district, dd, farmer_name, land_ha, crop)

def fetch_schemes(farmer_type: str = "Small/Marginal (<2 ha)", land_ha: float = 1.0, category: str = "All"):
    return match_government_schemes(farmer_type, land_ha, category)

def fetch_crop_timeline(crop: str, district: str):
    return get_crop_timeline(crop, district)

def fetch_mandi_compare(crop: str, district: str, land_ha: float):
    return calc_mandi_transport_profit(crop, district, land_ha)

def fetch_weather_risk(district: str):
    return get_district_weather_risk(district)

def fetch_equipment_calc(crop: str, land_ha: float):
    return calc_equipment_labor_cost(crop, land_ha)

def fetch_solar_pump(land_ha: float, current_source: str = "Diesel", well_depth_ft: int = 150):
    return calc_solar_pump_roi(land_ha, current_source, well_depth_ft)

def fetch_ml_yield(crop: str, rainfall_mm: float, avg_temp: float, soil_ph: float, nitrogen: float = 80, phosphorus: float = 40, potassium: float = 40):
    return predict_crop_yield_ml(crop, rainfall_mm, avg_temp, soil_ph, nitrogen, phosphorus, potassium)

# ─────────────────────────────────────────────────────────────────────────────
# LOAD BACKEND DATA
# ─────────────────────────────────────────────────────────────────────────────

all_data = fetch_all_districts()
crops_data = fetch_all_crops()
hist_data = fetch_historical_yield()

TN_DISTRICTS_DATA = all_data["data"] if all_data else TN_DISTRICTS
CROP_DB_DATA = crops_data["data"] if crops_data else CROP_DB
dist_list = sorted(TN_DISTRICTS_DATA.keys())
HIST_YEARS_DATA = hist_data["years"] if hist_data else HIST_YEARS
HISTORICAL_YIELD_DATA = hist_data["data"] if hist_data else HISTORICAL_YIELD

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE DEFAULTS
# ─────────────────────────────────────────────────────────────────────────────

defaults = {
    "profile": None,
    "selected_crop": "Paddy",
    "active_nav": "Smart Crop Finder",
    "messages": [],
    "api_key": "",
    "conclusion_text": None,
    "weather_data": None,
    "weather_district": "Thoothukudi",
    "soil_report": None,
    "irrigation_report": None,
    "market_report": None,
    "lang": "English"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# 1. LOGIN / FARMER PROFILE SCREEN
# ─────────────────────────────────────────────────────────────────────────────

def render_login_view():
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1rem 0;">
        <h1 style="color: #059669; font-size: 2.5rem;"> AgriSmart TN</h1>
        <p style="color: #475569; font-size: 1.1rem; max-width: 600px; margin: 0 auto;">
            Tamil Nadu's Next-Gen Agricultural Intelligence & Advisory Platform.
            Connect your farm profile for personalised crop plans, seed calculators & profit projections.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        st.subheader("Farmer Account & Farm Profile Registration")
        
        tab_login, tab_demo = st.tabs(["Create / Access Profile", "Quick Demo Account"])
        
        with tab_login:
            with st.form("farmer_profile_form"):
                fn1, fn2 = st.columns(2)
                with fn1:
                    farmer_name = st.text_input("Farmer Full Name", value="Ramasamy K.", placeholder="e.g. Ramasamy")
                    phone_email = st.text_input("Mobile Number / Email", value="9840012345", placeholder="98400XXXXX")
                    district = st.selectbox("District (Tamil Nadu)", dist_list if dist_list else ["Thoothukudi"], 
                                            index=dist_list.index("Thoothukudi") if "Thoothukudi" in dist_list else 0)
                    land_acres = st.number_input("Total Farm Land Area (in Acres)", min_value=0.25, max_value=500.0, value=3.0, step=0.5)
                
                with fn2:
                    soil_type = st.selectbox("Primary Soil Type", [
                        "Red Loamy", "Black Cotton", "Alluvial Soil", "Coastal Alluvial", "Sandy Clay", "Laterite Soil", "Clay Soil"
                    ], index=0)
                    irrigation = st.selectbox("Main Water / Irrigation Source", [
                        "Canal / River Water", "Borewell / Groundwater", "Drip Irrigation", "Rainfed / Monsoon", "Tank / Pond"
                    ], index=0)
                    current_crop = st.selectbox("Current / Planned Crop", ["-- Not decided yet --"] + list(CROP_DB.keys()), index=1)
                
                st.markdown("---")
                submitted = st.form_submit_button("Enter AgriSmart Platform", use_container_width=True)
                
                if submitted:
                    c_crop = None if current_crop == "-- Not decided yet --" else current_crop
                    p_data = {
                        "farmer_name": farmer_name.strip() or "Farmer",
                        "phone_email": phone_email.strip() or "9840012345",
                        "district": district,
                        "land_acres": land_acres,
                        "soil_type": soil_type,
                        "irrigation": irrigation,
                        "current_crop": c_crop
                    }
                    save_profile(p_data)
                    st.session_state.profile = p_data
                    if c_crop:
                        st.session_state.selected_crop = c_crop
                    
                    # Welcome prompt in AI chat
                    welcome_msg = (
                        f"Hello {p_data['farmer_name']}! Welcome to AgriSmart TN.\n\n"
                        f"Your profile is active for **{p_data['land_acres']} Acres** in **{p_data['district']}** "
                        f"({p_data['soil_type']} soil, {p_data['irrigation']}).\n\n"
                        f"How can I assist you with your farming decisions today?"
                    )
                    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
                    st.rerun()
                    
        with tab_demo:
            st.info("Click below to immediately launch AgriSmart with a sample 3.0 Acre farm in Thoothukudi.")
            if st.button("Start Instant Demo Mode", use_container_width=True):
                p_data = {
                    "farmer_name": "Ramasamy K.",
                    "phone_email": "9840012345",
                    "district": "Thoothukudi",
                    "land_acres": 3.0,
                    "soil_type": "Red Loamy",
                    "irrigation": "Canal / River Water",
                    "current_crop": "Paddy"
                }
                save_profile(p_data)
                st.session_state.profile = p_data
                st.session_state.selected_crop = "Paddy"
                st.rerun()

    with col_side:
        st.subheader("Why Register?")
        st.markdown("""
        - **Tailored Crop Engine**: Get crop recommendations matched directly to your soil & water source.
        - **Acre-based Precision**: All seed rates, fertilizers, equipment & labor costs scale to your exact land size in Acres.
        - **Context-Aware AI Chatbot**: Ask questions without re-typing your farm details every time.
        - **Bank Loan Ready PDF Reports**: Download farm financial feasibility reports instantly.
        """)

# ─────────────────────────────────────────────────────────────────────────────
# 2. MAIN APPLICATION WORKSPACE
# ─────────────────────────────────────────────────────────────────────────────

def main():
    if st.session_state.profile is None:
        render_login_view()
        return

    else:
        # Load active farmer profile context
        prof = st.session_state.profile
        farmer_name = prof.get("farmer_name", "Farmer")
        district = prof.get("district", "Thoothukudi")
        land_acres = prof.get("land_acres", 3.0)
        land_ha = land_acres * 0.404686
        soil_type = prof.get("soil_type", "Red Loamy")
        irrigation = prof.get("irrigation", "Canal / River Water")
        dist_info = TN_DISTRICTS.get(district, {})

    # ─────────────────────────────────────────────────────────────────────────────
    # SIDEBAR NAVIGATION & PROFILE SUMMARY
    # ─────────────────────────────────────────────────────────────────────────────

    with st.sidebar:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
            <span style="font-size: 2rem;"></span>
            <div>
                <h3 style="margin: 0; color: #059669;">AgriSmart TN</h3>
                <small style="color: #64748b;">Smart Agritech Platform</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Feature 4: Language Switcher (English / தமிழ்)
        sel_lang = st.radio("Language / மொழி", ["English", "தமிழ்"], index=0 if st.session_state.lang == "English" else 1, horizontal=True)
        if sel_lang != st.session_state.lang:
            st.session_state.lang = sel_lang
            st.rerun()
        cur_lang = st.session_state.lang

        # Profile Card
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.08); padding: 14px; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.2); margin-bottom: 15px;">
            <div style="font-weight: 700; color: #065f46; font-size: 1.05rem;"> {farmer_name}</div>
            <div style="font-size: 0.85rem; color: #047857; margin-top: 4px; line-height: 1.4;">
                 <b>{district}</b> ({dist_info.get('zone', 'Agro')} Zone)<br>
                 <b>{land_acres} Acres</b> ({land_ha:.2f} ha)<br>
                 {soil_type} | {irrigation}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Edit Profile / Switch Account", use_container_width=True):
            st.session_state.profile = None
            st.rerun()

        st.markdown("<div class='sidebar-nav-header'> CROP PLANNING & ML</div>", unsafe_allow_html=True)
        plan_options = [
            "Smart Crop Finder", "Seed & Input Planner", "Acre-based Profit & Cost",
            "ML Crop Yield Predictor", "Solar Pump & PM-KUSUM ROI", "AI Crop Advisor Chat"
        ]
        for item in plan_options:
            is_active = (st.session_state.active_nav == item)
            label = f" {item}" if is_active else f" {item}"
            if st.button(label, key=f"nav_{item}", use_container_width=True):
                st.session_state.active_nav = item
                st.rerun()

        st.markdown("<div class='sidebar-nav-header'> FARM OPERATIONS</div>", unsafe_allow_html=True)
        ops_options = ["Live Weather & Climate Risk", "Pest AI Diagnostics", "Crop Lifecycle Gantt", "Govt Schemes & Subsidies"]
        for item in ops_options:
            is_active = (st.session_state.active_nav == item)
            label = f" {item}"if is_active else f" {item}"
            if st.button(label, key=f"nav_{item}", use_container_width=True):
                st.session_state.active_nav = item
                st.rerun()

        st.markdown("<div class='sidebar-nav-header'> MARKET & ADVISORY</div>", unsafe_allow_html=True)
        mkt_options = ["Mandi Price Tracker", "Machinery & Labor Estimator", "Soil Health & Irrigation", "Farm Summary & PDF Export"]
        for item in mkt_options:
            is_active = (st.session_state.active_nav == item)
            label = f" {item}"if is_active else f" {item}"
            if st.button(label, key=f"nav_{item}", use_container_width=True):
                st.session_state.active_nav = item
                st.rerun()

        st.markdown("---")
        st.subheader("Access Key (Optional)")
        typed_key = st.text_input(
            "Online API Key", value=st.session_state.api_key,
            type="password", placeholder="Leave blank for offline mode",
            key="api_key_widget"
        )
        if typed_key:
            st.session_state.api_key = typed_key

    # ─────────────────────────────────────────────────────────────────────────────
    # PAGE ROUTING & VIEW IMPLEMENTATIONS
    # ─────────────────────────────────────────────────────────────────────────────

    nav = st.session_state.active_nav

    # TOP METRIC BAR (Visible on all views)
    top_c1, top_c2, top_c3, top_c4, top_c5 = st.columns(5)
    with top_c1: st.metric("Selected District", district)
    with top_c2: st.metric("Farm Land", f"{land_acres} Acres")
    with top_c3: st.metric("Active Crop", st.session_state.selected_crop or "None")
    with top_c4: st.metric("Soil Type", soil_type)
    with top_c5: st.metric("District Temp", f"{dist_info.get('avg_temp', 29)}°C")
    st.markdown("---")

    # ─────────────────────────────────────────────────────────────────────────────
    # VIEW 1: SMART CROP FINDER & FILTERING
    # ─────────────────────────────────────────────────────────────────────────────
    if nav == "Smart Crop Finder":
        st.subheader("Smart Crop Filtering & Recommendation Engine")
        st.caption("AI-driven crop suitability matching based on your district's soil, climate, water availability & market ROI.")

        f1, f2, f3, f4 = st.columns(4)
        with f1:
            filter_soil = st.checkbox(f"Filter for my soil ({soil_type})", value=True)
        with f2:
            filter_irr = st.checkbox(f"Filter for my irrigation source", value=True)
        with f3:
            season_sel = st.selectbox("Growing Season", ["All", "Kharif (Monsoon)", "Rabi (Winter)", "Zaid (Summer)", "Year-round"], index=0)
        with f4:
            min_prof = st.slider("Min Est. Profit / Acre (₹)", 0, 100000, 20000, step=5000)

        s_soil = soil_type if filter_soil else ""
        s_irr = irrigation if filter_irr else ""

        rec_crops = fetch_smart_crops(district, land_acres, s_soil, s_irr, season_sel, min_prof)

        st.markdown(f"### Recommended Crops for {land_acres} Acres in {district}")

        if not rec_crops:
            st.warning("No crops match your strict filter settings. Try lowering the minimum profit or unchecking soil filters.")
        else:
            for idx, crop_item in enumerate(rec_crops):
                score = crop_item.get("suitability_score", 80)
                badge_cls = "badge-highly-suitable" if score >= 90 else "badge-suitable" if score >= 75 else "badge-moderate"

                with st.container():
                    c_head, c_btn = st.columns([3, 1])
                    with c_head:
                        st.markdown(f"""
                        <div style="display:flex; align-items:center; gap:12px;">
                            <span style="font-size:2.2rem;">{crop_item.get('emoji','')}</span>
                            <div>
                                <h3 style="margin:0; color:#0f172a;">{crop_item['crop']}</h3>
                                <span class="{badge_cls}">Match Score: {score}%</span>
                                <span style="color:#64748b; font-size:0.88rem; margin-left:10px;">Season: {crop_item.get('season','General')}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c_btn:
                        if st.button(f"Plan for {crop_item['crop']}", key=f"sel_crop_{idx}", use_container_width=True):
                            st.session_state.selected_crop = crop_item['crop']
                            st.session_state.active_nav = "Seed & Input Planner"
                            st.rerun()

                    m1, m2, m3, m4 = st.columns(4)
                    with m1: st.metric("Est. Yield / Acre", f"{crop_item['yield_per_acre']} Tons")
                    with m2: st.metric("Profit / Acre", fmt_inr(crop_item['profit_per_acre']))
                    with m3: st.metric(f"Total Net Profit ({land_acres} Acres)", fmt_inr(crop_item['total_profit']))
                    with m4: st.metric("Market Risk", crop_item.get('market_risk', 'Medium'))

                    st.markdown("**Why this crop is suitable:**")
                    reasons = crop_item.get("match_reasons", [])
                    st.markdown(" • " + "\n • ".join(reasons))
                    st.markdown("---")

    # ─────────────────────────────────────────────────────────────────────────────
    # VIEW 2: SEED & INPUT PLANNER
    # ─────────────────────────────────────────────────────────────────────────────
    elif nav == "Seed & Input Planner":
        st.subheader("Seed & Agronomic Input Requirements Planner")
        st.caption(f"Exact seed quantity, spacing, seed treatment & sowing schedule for {land_acres} Acres.")

        sel_c = st.selectbox("Select Crop for Seed Planning", list(CROP_DB.keys()),
                             index=list(CROP_DB.keys()).index(st.session_state.selected_crop) if st.session_state.selected_crop in CROP_DB else 0)

        if sel_c != st.session_state.selected_crop:
            st.session_state.selected_crop = sel_c

        seed_plan = fetch_seed_planner(sel_c, land_acres)

        if seed_plan:
            st.markdown(f"### Seed Requirement Summary — {sel_c}")

            s1, s2, s3, s4 = st.columns(4)
            with s1: st.metric(f"Total Seed Needed ({land_acres} Acres)", f"{seed_plan.get('total_seed_kg',0)} {seed_plan.get('unit','kg')}")
            with s2: st.metric("Seed Rate per Acre", f"{seed_plan.get('seed_rate_per_acre','--')}")
            with s3: st.metric("Method", seed_plan.get("sowing_method","--"))
            with s4: st.metric("Est. Seed Cost", fmt_inr(seed_plan.get("est_seed_cost",0)))

            st.markdown("---")

            sp1, sp2 = st.columns(2)
            with sp1:
                st.markdown("#### Spacing & Nursery Specifications")
                st.info(f"**Optimal Spacing:** {seed_plan.get('spacing','')}")
                st.info(f"**Nursery Duration:** {seed_plan.get('nursery_duration_days', 0)} days before transplanting")
                st.info(f"**Expected Germination Rate:** {seed_plan.get('germination_rate','')}")
                st.info(f"**Ideal Sowing Months:** {seed_plan.get('sowing_window','')}")

            with sp2:
                st.markdown("#### Mandatory Seed Treatment Protocol")
                st.warning(f"{seed_plan.get('seed_treatment','')}")
                st.success(f"**Agronomic Advice:** {seed_plan.get('advice','')}")

    # ─────────────────────────────────────────────────────────────────────────────
    # VIEW 3: ACRE-BASED PROFIT & COST BREAKDOWN
    # ─────────────────────────────────────────────────────────────────────────────
    elif nav == "Acre-based Profit & Cost":
        st.subheader("Acre-Based Financial Estimator & Cost Breakdown")
        st.caption("Complete income statement, cost per acre, gross revenue & net profit scaled dynamically.")

        pc1, pc2, pc3 = st.columns(3)
        with pc1:
            c_crop = st.selectbox("Select Crop", list(CROP_DB.keys()),
                                  index=list(CROP_DB.keys()).index(st.session_state.selected_crop) if st.session_state.selected_crop in CROP_DB else 0,
                                  key="plan_crop_sel")
        with pc2:
            c_acres = st.number_input("Land Size (Acres)", min_value=0.25, max_value=500.0, value=float(land_acres), step=0.5)
        with pc3:
            c_factor = st.slider("Yield Performance Factor", 0.7, 1.3, 1.0, 0.05, help="1.0 = Average yield, 1.15 = Best practices yield")

        plan = fetch_crop_plan(c_crop, c_acres, c_factor)

        if plan:
            r1, r2, r3, r4, r5 = st.columns(5)
            with r1: st.metric("Net Profit", fmt_inr(plan['net_profit']))
            with r2: st.metric("Gross Revenue", fmt_inr(plan['gross_revenue']))
            with r3: st.metric("Cultivation Cost", fmt_inr(plan['total_cost']))
            with r4: st.metric("ROI", f"{plan['roi_percent']}%")
            with r5: st.metric("Break-Even Yield", f"{plan['break_even_yield_tons']} Tons")

            st.markdown("---")

            ch1, ch2 = st.columns([1, 1])

            with ch1:
                st.markdown(f"#### Cost Breakdown for {c_acres} Acres")
                costs = plan.get("cost_breakdown", {})
                df_costs = pd.DataFrame([{"Item": k, "Cost (₹)": v} for k, v in costs.items()])

                fig = px.pie(df_costs, values="Cost (₹)", names="Item", hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320)
                st.plotly_chart(fig, use_container_width=True)

            with ch2:
                st.markdown("#### Per-Acre vs Total Financial Breakdown")
                df_table = pd.DataFrame([
                    {"Metric": "Expected Yield", "Per Acre": f"{plan['yield_per_acre']} Tons", f"Total ({c_acres} Acres)": f"{plan['total_yield_tons']} Tons"},
                    {"Metric": "Cost of Cultivation", "Per Acre": fmt_inr(plan['cost_per_acre']), f"Total ({c_acres} Acres)": fmt_inr(plan['total_cost'])},
                    {"Metric": "Selling Price / Ton", "Per Acre": f"₹{plan['selling_price_per_ton']:,}", f"Total ({c_acres} Acres)": f"₹{plan['selling_price_per_ton']:,}"},
                    {"Metric": "Gross Revenue", "Per Acre": fmt_inr(plan['gross_revenue'] / c_acres), f"Total ({c_acres} Acres)": fmt_inr(plan['gross_revenue'])},
                    {"Metric": "Net Profit", "Per Acre": fmt_inr(plan['profit_per_acre']), f"Total ({c_acres} Acres)": fmt_inr(plan['net_profit'])},
                ])
                st.dataframe(df_table, use_container_width=True, hide_index=True)

    # ─────────────────────────────────────────────────────────────────────────────
    # VIEW 3B: FEATURE 3 — MACHINE LEARNING CROP YIELD PREDICTOR (scikit-learn)
    # ─────────────────────────────────────────────────────────────────────────────
    elif nav == "ML Crop Yield Predictor":
        st.subheader(t("ml_yield_title", cur_lang))
        st.caption("Predict harvest yield using trained Random Forest Regressor ML pipeline based on soil pH, rainfall & temperature.")

        ml1, ml2 = st.columns([1, 1])
        with ml1:
            ml_crop = st.selectbox("Select Crop", list(CROP_DB.keys()),
                                   index=list(CROP_DB.keys()).index(st.session_state.selected_crop) if st.session_state.selected_crop in CROP_DB else 0,
                                   key="ml_crop_sel")
            ml_rain = st.slider("Expected Season Rainfall (mm)", 100, 2500, int(dist_info.get("rainfall_mm", 900)), step=50)
            ml_temp = st.slider("Average Season Temperature (°C)", 15.0, 45.0, float(dist_info.get("avg_temp", 29.0)), step=0.5)
            ml_ph = st.slider("Soil pH Level", 4.5, 9.0, float(dist_info.get("soil_ph", 6.5)), step=0.1)
            ml_npk = st.number_input("Nitrogen Input (kg/ha)", min_value=10.0, max_value=300.0, value=80.0, step=10.0)

        with ml2:
            ml_res = fetch_ml_yield(ml_crop, ml_rain, ml_temp, ml_ph, ml_npk)
            if ml_res:
                st.markdown(f"### ML Prediction Results — {crop_t(ml_crop, cur_lang)}")

                y1, y2, y3 = st.columns(3)
                with y1: st.metric("Yield per Hectare", f"{ml_res.get('predicted_yield_ha', 0)} Tonnes")
                with y2: st.metric("Yield per Acre", f"{ml_res.get('predicted_yield_acre', 0)} Tonnes")
                with y3: st.metric(t("confidence_score", cur_lang), f"{ml_res.get('confidence_r2', 0.88)*100:.1f}%")

                st.markdown("---")
                st.markdown("#### Feature Importance Breakdown")
                f_imp = ml_res.get("feature_importance", {})
                df_imp = pd.DataFrame([{"Feature": k, "Importance (%)": v} for k, v in f_imp.items()])

                fig_imp = px.bar(df_imp, x="Importance (%)", y="Feature", orientation="h",
                                 color="Importance (%)", color_continuous_scale="Viridis",
                                 title="Machine Learning Factor Influence")
                fig_imp.update_layout(height=260, showlegend=False, margin=dict(t=30, b=10, l=10, r=10))
                st.plotly_chart(fig_imp, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────────────
    # VIEW 3C: FEATURE 2 — SOLAR PUMP & PM-KUSUM SUBSIDY ROI CALCULATOR
    # ─────────────────────────────────────────────────────────────────────────────
    elif nav == "Solar Pump & PM-KUSUM ROI":
        st.subheader(t("solar_pump_title", cur_lang))
        st.caption("Calculate exact pump HP capacity, 60% PM-KUSUM state & central subsidy, monthly fuel savings & payback period.")

        sp1, sp2 = st.columns([1, 1])
        with sp1:
            cur_source = st.radio("Current Irrigation Energy Source", ["Diesel", "Grid Electricity"], index=0)
            well_depth = st.slider("Well / Borehole Depth (Feet)", 50, 600, 150, step=25)

        with sp2:
            sp_res = fetch_solar_pump(land_ha, cur_source, well_depth)
            if sp_res:
                st.markdown(f"### Recommended Solar Pump: **{sp_res.get('recommended_pump_hp')} HP**")

                k1, k2, k3 = st.columns(3)
                with k1: st.metric("Total System Cost", fmt_inr(sp_res.get("total_system_cost", 0)))
                with k2: st.metric("PM-KUSUM Subsidy (60%)", fmt_inr(sp_res.get("pm_kusum_subsidy_60pct", 0)))
                with k3: st.metric("Farmer Share (10%)", fmt_inr(sp_res.get("farmer_down_payment_10pct", 0)))

                st.markdown("---")

                k4, k5, k6 = st.columns(3)
                with k4: st.metric("Monthly Savings", fmt_inr(sp_res.get("monthly_savings_inr", 0)))
                with k5: st.metric(t("payback_period", cur_lang), f"{sp_res.get('payback_period_months', 0)} Months")
                with k6: st.metric("Annual CO₂ Saved", f"{sp_res.get('co2_saved_tonnes_yr', 0)} Tonnes")

                st.success(f"**Government Subsidy:** Eligible for 60% direct subsidy under PM-KUSUM Scheme + 30% low-interest bank loan. Net out-of-pocket payment required: **{fmt_inr(sp_res.get('farmer_down_payment_10pct', 0))}**.")

    # ─────────────────────────────────────────────────────────────────────────────
    # VIEW 4: AI CROP ADVISOR CHAT
    # ─────────────────────────────────────────────────────────────────────────────
    elif nav == "AI Crop Advisor Chat":
        st.subheader("AI Agricultural Advisor & Farming Guide")
        st.caption(f"Context-aware AI chatbot pre-loaded with your {land_acres} Acre farm details in {district}.")

        # Pre-built query chips
        chip1, chip2, chip3, chip4 = st.columns(4)
        with chip1:
            if st.button("Recommend best crop", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": f"What is the single best crop for my {land_acres} acres in {district}?"})
                st.rerun()
        with chip2:
            if st.button("Fertilizer schedule", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": f"Give me exact NPK fertilizer schedule for {st.session_state.selected_crop} on {land_acres} acres."})
                st.rerun()
        with chip3:
            if st.button("Water management", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": f"How much water does {st.session_state.selected_crop} need and what is the best irrigation method?"})
                st.rerun()
        with chip4:
            if st.button("Applicable subsidies", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": f"What government subsidy schemes can I apply for in {district}?"})
                st.rerun()

        st.markdown("---")

        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # If the last message is from user and needs assistant reply
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing farm context & generating reply..."):
                        reply = fetch_ai_advisor(
                            st.session_state.messages, district, land_ha, farmer_name,
                            st.session_state.api_key, st.session_state.selected_crop, prof
                        )
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                        st.markdown(reply)

        user_input = st.chat_input(f"Ask AgriSmart AI anything about farming in {district}...", key="chat_input_box")
        if user_input and user_input.strip():
            st.session_state.messages.append({"role": "user", "content": user_input.strip()})
            st.rerun()

    # ─────────────────────────────────────────────────────────────────────────────
    # VIEW 5: LIVE WEATHER & CLIMATE RISK
    # ─────────────────────────────────────────────────────────────────────────────
    elif nav == "Live Weather & Climate Risk":
        st.subheader("Live District Weather & Climate Risk Matrix")

        wresult = fetch_weather(district)
        w_risk = fetch_weather_risk(district)

        wdata = wresult.get("live") if wresult else None

        if wdata and "current" in wdata:
            cur = wdata["current"]
            daily = wdata.get("daily", {})

            st.caption(f"LIVE WEATHER — {district}, Tamil Nadu")
            w1, w2, w3, w4, w5 = st.columns(5)
            with w1: st.metric("Temperature", f"{cur.get('temperature_2m','--')}°C")
            with w2: st.metric("Feels Like", f"{cur.get('apparent_temperature','--')}°C")
            with w3: st.metric("Humidity", f"{cur.get('relative_humidity_2m','--')}%")
            with w4: st.metric("Wind Speed", f"{cur.get('wind_speed_10m','--')} km/h")
            with w5: st.metric("Rainfall Today", f"{cur.get('precipitation', 0)} mm")
        else:
            st.info(f"Showing static climate averages for {district}")
            w1, w2, w3, w4 = st.columns(4)
            with w1: st.metric("Avg Temp", f"{dist_info.get('avg_temp', 29)}°C")
            with w2: st.metric("Annual Rain", f"{dist_info.get('rainfall_mm', 900)} mm/yr")
            with w3: st.metric("Humidity", f"{dist_info.get('humidity', 65)}%")
            with w4: st.metric("Soil pH", dist_info.get("soil_ph", 6.5))

        st.markdown("---")
        st.subheader("Extreme Weather Risk Matrix")
        if w_risk:
            rk1, rk2, rk3, rk4 = st.columns(4)
            with rk1: st.metric("Cyclone Risk", w_risk.get("cyclone_risk","--"))
            with rk2: st.metric("Flood Risk", w_risk.get("flood_risk","--"))
            with rk3: st.metric("Drought Risk", w_risk.get("drought_risk","--"))
            with rk4: st.metric("Heatwave Risk", w_risk.get("heat_risk","--"))

            st.markdown("#### District Contingency Action Plan")
            for plan in w_risk.get("contingency_plans", []):
                st.info(f"• {plan}")

    # ─────────────────────────────────────────────────────────────────────────────
    # VIEW 6: PEST AI DIAGNOSTICS
    # ─────────────────────────────────────────────────────────────────────────────
    elif nav == "Pest AI Diagnostics":
        st.subheader("Smart Pest & Crop Disease Diagnostics")
        st.caption("Upload a leaf photo or describe symptoms to receive immediate organic and chemical treatments.")

        p_col1, p_col2 = st.columns([1, 1])
        with p_col1:
            pest_crop = st.selectbox("Crop", list(CROP_DB.keys()), 
                                     index=list(CROP_DB.keys()).index(st.session_state.selected_crop) if st.session_state.selected_crop in CROP_DB else 0)
            pest_symptom = st.text_area("Describe Symptoms (e.g. yellowing leaves, stem borer, brown spots)", placeholder="e.g. Spindle shaped spots with brown margins")
            leaf_file = st.file_uploader("Upload Crop/Leaf Photo (Optional)", type=["jpg","jpeg","png"])
            diag_btn = st.button("Run Diagnostics", use_container_width=True)

        with p_col2:
            if diag_btn or pest_symptom:
                diag = fetch_pest_scanner(pest_crop, pest_symptom, "", st.session_state.api_key)
                if diag:
                    st.success(f"**Diagnosis Result:** {diag.get('diagnosis','Issue Detected')}")
                    st.write(f"**Type:** {diag.get('type','')}")
                    st.write(f"**Root Cause:** {diag.get('cause','')}")
                    st.markdown("---")
                    st.markdown(f"** Organic Remedy:**\n{diag.get('organic_remedy','')}")
                    st.markdown(f"** Chemical Treatment:**\n{diag.get('chemical_treatment','')}")
                    st.markdown(f"** Preventive Steps:**\n{diag.get('prevention','')}")

    # ─────────────────────────────────────────────────────────────────────────────
    # VIEW 7: CROP LIFECYCLE GANTT
    # ─────────────────────────────────────────────────────────────────────────────
    elif nav == "Crop Lifecycle Gantt":
        st.subheader("Interactive Crop Lifecycle Timeline & Input Schedule")

        t_crop = st.selectbox("Select Crop", list(CROP_DB.keys()),
                              index=list(CROP_DB.keys()).index(st.session_state.selected_crop) if st.session_state.selected_crop in CROP_DB else 0)
        stages = fetch_crop_timeline(t_crop, district)

        if stages:
            df_timeline = pd.DataFrame(stages)
            fig_gantt = px.timeline(df_timeline, x_start="StartDay", x_end="EndDay", y="Stage", color="Stage",
                                    hover_data=["Action","Input"], title=f"Lifecycle Timeline — {t_crop} in {district} (Days from Sowing)")
            fig_gantt.update_yaxes(autorange="reversed")
            fig_gantt.update_layout(template="plotly_white", height=320, showlegend=False)
            st.plotly_chart(fig_gantt, use_container_width=True)

            st.markdown("### Stage-by-Stage Input Checklist")
            for s in stages:
                with st.expander(f"**{s['Stage']}** (Day {s['StartDay']} to Day {s['EndDay']})"):
                    st.write(f"**Key Action:** {s['Action']}")
                    st.write(f"**Required Inputs:** {s['Input']}")

    # ─────────────────────────────────────────────────────────────────────────────
    # VIEW 8: GOVT SCHEMES & SUBSIDIES
    # ─────────────────────────────────────────────────────────────────────────────
    elif nav == "Govt Schemes & Subsidies":
        st.subheader("Government Subsidy & Scheme Eligibility Finder")

        sc1, sc2 = st.columns(2)
        with sc1:
            farmer_type = st.selectbox("Farmer Category", ["Small/Marginal (<2 ha)", "Medium/Large (>2 ha)", "Women Farmer / SC/ST"])
        with sc2:
            scheme_cat = st.selectbox("Scheme Category", ["All", "Direct Income Support", "Irrigation Subsidy", "Crop Risk Insurance", "Low-Interest Credit", "Input Subsidy", "Farm Mechanization", "Direct Marketing"])

        schemes_list = fetch_schemes(farmer_type, land_ha, scheme_cat)
        st.caption(f"Found {len(schemes_list)} eligible government schemes for your farm profile")

        for sch in schemes_list:
            with st.expander(f"**{sch['name']}** — {sch['category']}"):
                st.write(f"**Benefit:** {sch['benefit']}")
                st.write(f"**Eligibility:** {sch['eligibility']}")
                st.write(f"**Required Documents:** {', '.join(sch['docs'])}")
                st.markdown(f"[Official Application Portal]({sch['link']})")

    # ─────────────────────────────────────────────────────────────────────────────
    # VIEW 9: MANDI PRICE TRACKER
    # ─────────────────────────────────────────────────────────────────────────────
    elif nav == "Mandi Price Tracker":
        st.subheader("Multi-Mandi Price Tracker & Transport Profitability Engine")

        m_crop = st.selectbox("Select Crop", list(CROP_DB.keys()),
                               index=list(CROP_DB.keys()).index(st.session_state.selected_crop) if st.session_state.selected_crop in CROP_DB else 0)
        mandis = fetch_mandi_compare(m_crop, district, land_ha)

        if mandis:
            df_mandi = pd.DataFrame(mandis)
            fig_m = go.Figure()
            fig_m.add_trace(go.Bar(x=df_mandi["mandi"], y=df_mandi["net_profit"], name="Net Profit (₹)", marker_color="#10b981"))
            fig_m.add_trace(go.Bar(x=df_mandi["mandi"], y=df_mandi["transport_cost"], name="Transport Cost (₹)", marker_color="#ef4444"))
            fig_m.update_layout(barmode="group", title=f"Net Profit vs Transport Cost across Mandis ({m_crop} on {land_acres} Acres)", template="plotly_white", height=360)
            st.plotly_chart(fig_m, use_container_width=True)

            st.dataframe(df_mandi[["mandi", "distance_km", "price_per_tonne", "gross_revenue", "transport_cost", "net_profit", "roi"]].rename(columns={
                "mandi": "Mandi Market", "distance_km": "Distance (km)", "price_per_tonne": "Price (₹/t)", "gross_revenue": "Gross Revenue", "transport_cost": "Transport Cost", "net_profit": "Net Profit", "roi": "ROI %"
            }), use_container_width=True, hide_index=True)

    # ─────────────────────────────────────────────────────────────────────────────
    # VIEW 10: MACHINERY & LABOR ESTIMATOR
    # ─────────────────────────────────────────────────────────────────────────────
    elif nav == "Machinery & Labor Estimator":
        st.subheader("Equipment Rental & Labor Cost Estimator")

        e_crop = st.selectbox("Select Crop", list(CROP_DB.keys()),
                              index=list(CROP_DB.keys()).index(st.session_state.selected_crop) if st.session_state.selected_crop in CROP_DB else 0)
        eq = fetch_equipment_calc(e_crop, land_ha)

        if eq:
            eq1, eq2, eq3, eq4 = st.columns(4)
            with eq1: st.metric("Tractor Hours", f"{eq.get('tractor_hrs',0)} hrs", f"₹{eq.get('tractor_cost',0):,}")
            with eq2: st.metric("Harvester Usage", f"{land_acres} acres", f"₹{eq.get('harvester_cost',0):,}")
            with eq3: st.metric("Drone Sprays", f"{eq.get('drone_sprays',0)} sprays", f"₹{eq.get('drone_cost',0):,}")
            with eq4: st.metric("Labor Days Needed", f"{eq.get('total_labor_days',0)} days", f"₹{eq.get('total_labor_cost',0):,}")

            st.markdown("---")
            st.success(f"**Total Mechanization Cost:** ₹{eq.get('total_mech_cost',0):,}")
            st.success(f"**Total Labor Cost:** ₹{eq.get('total_labor_cost',0):,}")
            st.info("Rates benchmarked against Tamil Nadu Custom Hiring Centres (CHC) subsidised tariffs.")

    # ─────────────────────────────────────────────────────────────────────────────
    # VIEW 11: SOIL HEALTH & IRRIGATION
    # ─────────────────────────────────────────────────────────────────────────────
    elif nav == "Soil Health & Irrigation":
        st.subheader("Soil Health & Precision Irrigation Guide")

        s_crop = st.selectbox("Select Crop", list(CROP_DB.keys()),
                              index=list(CROP_DB.keys()).index(st.session_state.selected_crop) if st.session_state.selected_crop in CROP_DB else 0)

        sr = fetch_soil_info(district, s_crop)
        ir = fetch_irrigation_info(district, land_ha, s_crop)

        t1, t2 = st.tabs(["Soil & NPK Schedule", "Irrigation Plan"])

        with t1:
            if sr:
                st.markdown(f"**Soil Profile:** {sr.get('profile','')}")
                st.markdown(f"**Amendment:** {sr.get('amendment','')}")
                st.markdown(f"**pH Advice:** {sr.get('ph_advice','')}")
                st.markdown("---")
                st.markdown("#### NPK Fertilizer Schedule")
                st.write(f"**Basal dose:** {sr.get('npk_base','')}")
                st.write(f"**Top dressing:** {sr.get('npk_top','')}")
                st.write(f"**Micronutrients:** {sr.get('micro','')}")
                st.write(f"**Organic inputs:** {sr.get('organic','')}")

        with t2:
            if ir:
                ir1, ir2, ir3, ir4 = st.columns(4)
                with ir1: st.metric("Water Need", ir.get("water","--"))
                with ir2: st.metric("Frequency", ir.get("freq","--"))
                with ir3: st.metric("Min Water", f"{ir.get('total_min',0)} mm")
                with ir4: st.metric("Max Water", f"{ir.get('total_max',0)} mm")
                st.info(ir.get("rainfed",""))
                st.markdown(f"**Best Method:** {ir.get('method','')}")
                st.markdown(f"**Installation Detail:** {ir.get('method_detail','')}")
                st.markdown(f"**Est. Irrigation Cost:** ₹{ir.get('irr_cost',0):,.0f}")

    # ─────────────────────────────────────────────────────────────────────────────
    # VIEW 12: FARM SUMMARY & PDF EXPORT
    # ─────────────────────────────────────────────────────────────────────────────
    elif nav == "Farm Summary & PDF Export":
        st.subheader("Farm Financial Summary & Bank Loan PDF Report")

        sel_crop = st.session_state.selected_crop
        p = fetch_profit(sel_crop, land_ha)

        if p:
            rr1, rr2, rr3, rr4 = st.columns(4)
            with rr1: st.metric("Selected Crop", sel_crop)
            with rr2: st.metric("Est. Net Profit", fmt_inr(p["profit"]))
            with rr3: st.metric("ROI", f"{p['roi']}%")
            with rr4: st.metric("Total Production", f"{p['total_yield']} Tons")

        st.markdown("---")

        pdf_bytes = fetch_pdf_report(district, farmer_name, land_ha, sel_crop)
        if pdf_bytes:
            st.download_button(
                label="Download Bank Loan Farm Advisory PDF Report",
                data=pdf_bytes,
                file_name=f"AgriSmart_Farm_Report_{district}_{sel_crop}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("### Comprehensive AI Conclusion Report")

        if st.session_state.conclusion_text:
            st.markdown(st.session_state.conclusion_text)
        else:
            if st.button("Generate AI Conclusion Report", use_container_width=True):
                with st.spinner("Generating personalized farm report..."):
                    report = fetch_ai_conclusion(district, land_ha, farmer_name, sel_crop, st.session_state.api_key)
                    st.session_state.conclusion_text = report
                    st.rerun()

if __name__ == '__main__':
    main()
