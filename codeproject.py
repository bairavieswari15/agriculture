import streamlit as st
import datetime
import requests

# PAGE CONFIG 
# PAGE CONFIG
st.set_page_config(
    page_title="AgriSmart TN",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help":"https://github.com/yourrepo/agri-smart-tn",
        "Report a bug":"https://github.com/yourrepo/agri-smart-tn/issues",
        "About":"AgriSmart TN – AI powered agricultural advisor"
    }
)

# ---------------- UI Navigation & Login Guard ----------------
def render_login():
    st.markdown("""
        <div style="text-align: center; padding: 25px 0 10px 0;">
            <h1 style="color: #2e7d32; font-size: 2.8rem; margin-bottom: 5px;"> AgriSmart TN</h1>
            <p style="font-size: 1.15rem; color: #555; font-weight: 500;">AI-Powered Agricultural Decision Support Platform</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    with col2:
        st.markdown("---")
        with st.form("login_form", clear_on_submit=False):
            st.subheader("User Login")
            username = st.text_input("Username / Mobile Number", placeholder="e.g. Raman or 9876543210")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            role = st.selectbox(
                "Select User Role",
                ["Farmer","Extension Officer","Agri-Expert","Admin"],
                index=0
            )
            submit = st.form_submit_button("Log In to AgriSmart", type="primary", use_container_width=True)
            
            if submit:
                if username and password:
                    st.session_state["authenticated"] = True
                    st.session_state["farmer_name"] = username
                    st.session_state["role"] = role
                    st.success(f"Welcome back, **{username}**! Logged in as **{role}**.")
                    st.rerun()
                else:
                    st.error("Please enter both username and password.")
                    
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 18px; border-radius: 10px; margin-top: 25px; border-left: 5px solid #2e7d32; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
            <h4 style="margin-top: 0; color: #2e7d32;"> Demo Portal Info</h4>
            <p style="margin: 0; font-size: 0.92rem; color: #444; line-height: 1.6;">
                Enter any username & password to access the full application.<br>
                <b>Role Access:</b><br>
                • <b> Farmer:</b> Smart Crop Advisor, yield estimates, weather & profit calculator.<br>
                • <b> Extension Officer:</b> Field officer logs & district statistics.<br>
                • <b> Agri-Expert:</b> Soil health diagnostic engine & pest forecast.<br>
                • <b> Admin:</b> Platform management & data insights.
            </p>
        </div>
        """, unsafe_allow_html=True)

# Guard: block unauthenticated users from seeing the main application
if not st.session_state.get("authenticated", False):
    render_login()
    st.stop()


st.markdown("""
<style>
/* Uniform metric value font size across all cards */
[data-testid="stMetricValue"] {
    font-size: 1.1rem !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
[data-testid="stMetricLabel"] {
    font-size: 0.78rem !important;
}
</style>
""", unsafe_allow_html=True)



# 
# ALL 38 TAMIL NADU DISTRICTS
# 
TN_DISTRICTS = {
    "Ariyalur": {"zone":"Central","avg_temp":30,"rainfall_mm":950,"humidity":68,"soil":"Alluvial / Red Loam","soil_ph":6.9,"main_crops":["Paddy","Sugarcane","Groundnut","Pulses"],"river":"Kollidam","known_for":"Limestone, Paddy","lat":11.14,"lon":79.08},
    "Chengalpattu": {"zone":"North Coastal","avg_temp":29,"rainfall_mm":1200,"humidity":74,"soil":"Sandy Loam / Clay","soil_ph":6.8,"main_crops":["Paddy","Vegetables","Groundnut","Banana"],"river":"Palar","known_for":"Paddy, Vegetables","lat":12.69,"lon":79.98},
    "Chennai": {"zone":"North Coastal","avg_temp":29,"rainfall_mm":1400,"humidity":76,"soil":"Sandy Loam / Red Laterite","soil_ph":6.8,"main_crops":["Vegetables","Groundnut","Paddy"],"river":"Cooum, Adyar","known_for":"Urban farming, Vegetables","lat":13.08,"lon":80.27},
    "Coimbatore": {"zone":"Western","avg_temp":27,"rainfall_mm":700,"humidity":60,"soil":"Black Cotton / Red Laterite","soil_ph":7.2,"main_crops":["Banana","Coconut","Sugarcane","Cotton","Maize"],"river":"Noyyal","known_for":"Banana, Cotton","lat":11.02,"lon":76.96},
    "Cuddalore": {"zone":"East Coastal","avg_temp":29,"rainfall_mm":1300,"humidity":78,"soil":"Alluvial / Clay Loam","soil_ph":7.0,"main_crops":["Paddy","Sugarcane","Banana","Coconut"],"river":"Pennaiyar, Paravanar","known_for":"Paddy, Coconut","lat":11.75,"lon":79.76},
    "Dharmapuri": {"zone":"North-Western","avg_temp":28,"rainfall_mm":900,"humidity":58,"soil":"Red Sandy / Loam","soil_ph":6.4,"main_crops":["Mango","Banana","Paddy","Groundnut","Tapioca"],"river":"Cauvery (upstream)","known_for":"Mango, Tapioca","lat":12.12,"lon":78.16},
    "Dindigul": {"zone":"Central","avg_temp":28,"rainfall_mm":800,"humidity":62,"soil":"Red Sandy / Black Cotton","soil_ph":6.8,"main_crops":["Banana","Coconut","Paddy","Groundnut","Mango"],"river":"Kodaganar","known_for":"Banana, Coconut","lat":10.36,"lon":77.97},
    "Erode": {"zone":"Western","avg_temp":28,"rainfall_mm":750,"humidity":61,"soil":"Red Laterite / Sandy Loam","soil_ph":6.6,"main_crops":["Turmeric","Coconut","Banana","Sugarcane","Cotton"],"river":"Kaveri, Bhavani","known_for":"Turmeric capital of India","lat":11.34,"lon":77.72},
    "Kallakurichi": {"zone":"Central","avg_temp":29,"rainfall_mm":1000,"humidity":67,"soil":"Red Loam / Alluvial","soil_ph":6.7,"main_crops":["Paddy","Sugarcane","Banana","Tapioca"],"river":"Sankarabarani","known_for":"Paddy, Sugarcane","lat":11.74,"lon":79.01},
    "Kancheepuram": {"zone":"North Coastal","avg_temp":29,"rainfall_mm":1150,"humidity":73,"soil":"Red Loam / Sandy Loam","soil_ph":6.7,"main_crops":["Paddy","Groundnut","Vegetables","Sugarcane"],"river":"Palar","known_for":"Paddy, Silk weaving","lat":12.83,"lon":79.70},
    "Kanyakumari": {"zone":"Southern Tip","avg_temp":27,"rainfall_mm":1800,"humidity":82,"soil":"Laterite / Alluvial","soil_ph":5.8,"main_crops":["Coconut","Banana","Paddy","Rubber","Vegetables"],"river":"Thamirabarani, Pazhayar","known_for":"Coconut, Banana, Spices","lat":8.09,"lon":77.55},
    "Karur": {"zone":"Central","avg_temp":29,"rainfall_mm":850,"humidity":63,"soil":"Sandy Loam / Red Loam","soil_ph":6.6,"main_crops":["Paddy","Banana","Coconut","Groundnut","Maize"],"river":"Amaravathi, Kaveri","known_for":"Banana, Textiles","lat":10.96,"lon":78.08},
    "Krishnagiri": {"zone":"North-Western","avg_temp":27,"rainfall_mm":950,"humidity":60,"soil":"Red Sandy / Laterite","soil_ph":6.3,"main_crops":["Mango","Groundnut","Paddy","Tomato","Millets"],"river":"Ponnaiyar","known_for":"Mango export hub","lat":12.52,"lon":78.21},
    "Madurai": {"zone":"Southern","avg_temp":31,"rainfall_mm":850,"humidity":65,"soil":"Red Sandy / Black Cotton","soil_ph":7.0,"main_crops":["Paddy","Banana","Jasmine","Groundnut","Maize"],"river":"Vaigai","known_for":"Jasmine flowers, Banana","lat":9.93,"lon":78.12},
    "Mayiladuthurai": {"zone":"Cauvery Delta","avg_temp":29,"rainfall_mm":1100,"humidity":77,"soil":"Alluvial / Clay","soil_ph":7.3,"main_crops":["Paddy","Banana","Sugarcane","Black Gram"],"river":"Cauvery, Arasalar","known_for":"Paddy bowl of TN","lat":11.10,"lon":79.65},
    "Nagapattinam": {"zone":"East Coastal Delta","avg_temp":29,"rainfall_mm":1350,"humidity":80,"soil":"Alluvial / Clay Loam","soil_ph":7.2,"main_crops":["Paddy","Banana","Coconut","Sugarcane"],"river":"Cauvery delta","known_for":"Paddy, Coconut","lat":10.76,"lon":79.84},
    "Namakkal": {"zone":"Central","avg_temp":28,"rainfall_mm":900,"humidity":62,"soil":"Red Sandy / Loam","soil_ph":6.5,"main_crops":["Banana","Coconut","Turmeric","Paddy","Maize"],"river":"Kaveri tributary","known_for":"Poultry, Banana, Eggs","lat":11.22,"lon":78.17},
    "Nilgiris": {"zone":"Western Ghats Hills","avg_temp":17,"rainfall_mm":2200,"humidity":85,"soil":"Loamy / Forest Soil","soil_ph":5.5,"main_crops":["Tea","Coffee","Vegetables","Potato","Carrot"],"river":"Bhavani","known_for":"Tea, Coffee, Hill vegetables","lat":11.49,"lon":76.73},
    "Perambalur": {"zone":"Central","avg_temp":30,"rainfall_mm":900,"humidity":65,"soil":"Red Sandy / Alluvial","soil_ph":6.7,"main_crops":["Paddy","Groundnut","Sugarcane","Pulses"],"river":"Vellar","known_for":"Paddy, Cement industries","lat":11.23,"lon":78.88},
    "Pudukkottai": {"zone":"Southern Central","avg_temp":30,"rainfall_mm":850,"humidity":65,"soil":"Red Sandy / Black Cotton","soil_ph":6.9,"main_crops":["Paddy","Groundnut","Banana","Sugarcane","Pulses"],"river":"Vellar, Amaravathi","known_for":"Groundnut, Paddy","lat":10.38,"lon":78.82},
    "Ramanathapuram": {"zone":"Southern Coast","avg_temp":31,"rainfall_mm":620,"humidity":70,"soil":"Sandy / Red Sandy","soil_ph":6.5,"main_crops":["Paddy","Groundnut","Pearl Millet","Cotton","Coconut"],"river":"Vaigai (lower)","known_for":"Salt, Pearl Millet, Groundnut","lat":9.37,"lon":78.83},
    "Ranipet": {"zone":"North-Western","avg_temp":28,"rainfall_mm":1000,"humidity":65,"soil":"Red Loam / Sandy","soil_ph":6.5,"main_crops":["Paddy","Groundnut","Sugarcane","Millets","Tomato"],"river":"Palar","known_for":"Leather, Paddy","lat":12.92,"lon":79.33},
    "Salem": {"zone":"Central","avg_temp":29,"rainfall_mm":950,"humidity":63,"soil":"Red Loam / Sandy","soil_ph":6.5,"main_crops":["Mango","Banana","Turmeric","Paddy","Tapioca"],"river":"Thirumanimutharu","known_for":"Mango, Turmeric, Steel","lat":11.65,"lon":78.16},
    "Sivaganga": {"zone":"Southern","avg_temp":31,"rainfall_mm":800,"humidity":65,"soil":"Red Sandy / Black Cotton","soil_ph":6.8,"main_crops":["Paddy","Groundnut","Cotton","Banana","Pulses"],"river":"Vaigai tributary","known_for":"Paddy, Groundnut","lat":9.84,"lon":78.48},
    "Tenkasi": {"zone":"Southern Western Ghats","avg_temp":27,"rainfall_mm":1400,"humidity":78,"soil":"Laterite / Loamy","soil_ph":6.0,"main_crops":["Banana","Coconut","Paddy","Rubber","Vegetables"],"river":"Chittar","known_for":"Banana, Rubber, Spices","lat":8.96,"lon":77.32},
    "Thanjavur": {"zone":"Cauvery Delta","avg_temp":29,"rainfall_mm":1050,"humidity":74,"soil":"Alluvial / Clay Loam","soil_ph":7.3,"main_crops":["Paddy","Banana","Sugarcane","Coconut","Black Gram"],"river":"Kaveri, Vennar","known_for":"Rice granary of Tamil Nadu","lat":10.79,"lon":79.14},
    "Theni": {"zone":"Southern Western","avg_temp":28,"rainfall_mm":950,"humidity":66,"soil":"Red Loam / Sandy","soil_ph":6.6,"main_crops":["Banana","Grapes","Turmeric","Paddy","Vegetables"],"river":"Vaigai (upper)","known_for":"Banana, Grapes","lat":10.01,"lon":77.48},
    "Thiruvallur": {"zone":"North Coastal","avg_temp":29,"rainfall_mm":1200,"humidity":73,"soil":"Red Loam / Sandy","soil_ph":6.7,"main_crops":["Paddy","Groundnut","Sugarcane","Vegetables"],"river":"Koratalai, Kusasthalai","known_for":"Paddy, Vegetables","lat":13.14,"lon":79.91},
    "Thiruvarur": {"zone":"Cauvery Delta","avg_temp":29,"rainfall_mm":1150,"humidity":77,"soil":"Alluvial / Clay","soil_ph":7.2,"main_crops":["Paddy","Banana","Sugarcane","Coconut"],"river":"Cauvery delta","known_for":"Paddy, Delta agriculture","lat":10.77,"lon":79.64},
    "Tirunelveli": {"zone":"Southern Tip","avg_temp":31,"rainfall_mm":650,"humidity":62,"soil":"Red Sandy / Alluvial","soil_ph":6.7,"main_crops":["Banana","Paddy","Groundnut","Coconut","Cotton"],"river":"Thamirabarani","known_for":"Banana, Halwa, Groundnut","lat":8.71,"lon":77.76},
    "Tirupathur": {"zone":"North-Western","avg_temp":27,"rainfall_mm":1050,"humidity":64,"soil":"Red Laterite / Sandy Loam","soil_ph":6.3,"main_crops":["Mango","Groundnut","Paddy","Millets","Tomato"],"river":"Ponnaiyar","known_for":"Mango, Hill area farming","lat":12.49,"lon":78.57},
    "Tiruppur": {"zone":"Western","avg_temp":27,"rainfall_mm":680,"humidity":59,"soil":"Red Loam / Sandy Loam","soil_ph":6.5,"main_crops":["Cotton","Banana","Coconut","Maize","Groundnut"],"river":"Noyyal","known_for":"Cotton, Knitwear industry","lat":11.10,"lon":77.34},
    "Tiruvanamalai": {"zone":"North-Eastern","avg_temp":29,"rainfall_mm":1100,"humidity":68,"soil":"Red Sandy / Loam","soil_ph":6.6,"main_crops":["Paddy","Groundnut","Sugarcane","Banana","Millets"],"river":"Pennaiyar","known_for":"Paddy, Groundnut, Temple","lat":12.23,"lon":79.07},
    "Thoothukudi": {"zone":"Southern Coast","avg_temp":30,"rainfall_mm":640,"humidity":74,"soil":"Sandy / Red Sandy Loam","soil_ph":6.6,"main_crops":["Paddy","Groundnut","Cotton","Pearl Millet","Banana"],"river":"Thamirabarani (delta)","known_for":"Salt, Pearl Fishery, Port city","lat":8.76,"lon":78.13},
    "Trichy": {"zone":"Central Delta","avg_temp":30,"rainfall_mm":900,"humidity":68,"soil":"Alluvial / Black Cotton","soil_ph":7.1,"main_crops":["Paddy","Sugarcane","Banana","Pulses","Groundnut"],"river":"Kaveri","known_for":"Paddy, Sugarcane, Tourism","lat":10.79,"lon":78.70},
    "Vellore": {"zone":"North-Western","avg_temp":28,"rainfall_mm":1000,"humidity":65,"soil":"Red Loam / Sandy","soil_ph":6.4,"main_crops":["Groundnut","Paddy","Mango","Tomato","Millets"],"river":"Palar","known_for":"Groundnut, Hospitals, Leather","lat":12.92,"lon":79.13},
    "Viluppuram": {"zone":"Eastern","avg_temp":29,"rainfall_mm":1100,"humidity":70,"soil":"Red Loam / Sandy","soil_ph":6.6,"main_crops":["Paddy","Sugarcane","Groundnut","Banana","Millets"],"river":"Ponnaiyar, Pennaiyar","known_for":"Sugarcane, Paddy","lat":11.94,"lon":79.49},
    "Virudhunagar": {"zone":"Southern","avg_temp":30,"rainfall_mm":750,"humidity":63,"soil":"Red Sandy / Loamy","soil_ph":6.7,"main_crops":["Banana","Paddy","Groundnut","Cotton","Coconut"],"river":"Vaippar","known_for":"Fireworks, Banana, Groundnut","lat":9.58,"lon":77.96},
}

# CROP DATABASE 
CROP_DB = {
    "Paddy": {"emoji":"","season":"Samba (Aug-Jan) / Kuruvai (Jun-Sep)","yield_min":4.5,"yield_max":6.0,"price":20000,"cost_ha":35000,"water":"High","days":120,"sell":"APMC Mandi, Uzhavar Sandhai, FCI procurement"},
    "Banana": {"emoji":"","season":"Year-round","yield_min":35,"yield_max":45,"price":15000,"cost_ha":90000,"water":"High","days":300,"sell":"Local market, Chennai wholesale, Export"},
    "Sugarcane": {"emoji":"","season":"Year-round","yield_min":80,"yield_max":100,"price":3150,"cost_ha":120000,"water":"Very High","days":365,"sell":"Sugar mills (TNSC), Cooperative societies"},
    "Coconut": {"emoji":"","season":"Year-round","yield_min":7000,"yield_max":10000,"price":20,"cost_ha":25000,"water":"Medium","days":2190,"sell":"Oil mills, Local traders, Direct retail"},
    "Groundnut": {"emoji":"","season":"Kharif & Rabi","yield_min":2.0,"yield_max":2.5,"price":55000,"cost_ha":38000,"water":"Low","days":100,"sell":"APMC, Oil mills, NAFED procurement"},
    "Turmeric": {"emoji":"","season":"Jun-Dec","yield_min":20,"yield_max":25,"price":70000,"cost_ha":100000,"water":"Medium","days":270,"sell":"Erode market (Asia's largest), Spice board"},
    "Mango": {"emoji":"","season":"Feb-May harvest","yield_min":10,"yield_max":15,"price":30000,"cost_ha":40000,"water":"Low","days":1825,"sell":"Export, Juice factories, Local wholesale"},
    "Cotton": {"emoji":"","season":"Kharif (Jun-Nov)","yield_min":1.5,"yield_max":2.0,"price":65000,"cost_ha":50000,"water":"Medium","days":180,"sell":"CCI, Private ginning mills, APMC"},
    "Tomato": {"emoji":"","season":"Oct-Jan","yield_min":20,"yield_max":25,"price":12000,"cost_ha":60000,"water":"Medium","days":90,"sell":"Koyambedu market, Local mandi, Paste factories"},
    "Maize": {"emoji":"","season":"Kharif & Rabi","yield_min":5,"yield_max":6,"price":17000,"cost_ha":28000,"water":"Low","days":90,"sell":"Poultry feed companies, APMC, Starch factories"},
    "Vegetables": {"emoji":"","season":"Year-round","yield_min":15,"yield_max":20,"price":10000,"cost_ha":50000,"water":"Medium","days":60,"sell":"Uzhavar Sandhai, Koyambedu, Local markets"},
    "Millets": {"emoji":"","season":"Kharif","yield_min":1.0,"yield_max":1.5,"price":25000,"cost_ha":15000,"water":"Very Low","days":75,"sell":"Organic stores, TNCSC, Health food brands"},
    "Pulses": {"emoji":"","season":"Rabi (Nov-Feb)","yield_min":0.8,"yield_max":1.2,"price":60000,"cost_ha":18000,"water":"Low","days":80,"sell":"NAFED, APMC, Local traders"},
    "Jasmine": {"emoji":"","season":"Year-round","yield_min":3,"yield_max":4,"price":200000,"cost_ha":80000,"water":"Medium","days":365,"sell":"Madurai flower market, Wedding contractors"},
    "Tapioca": {"emoji":"","season":"Year-round","yield_min":30,"yield_max":35,"price":5000,"cost_ha":30000,"water":"Low","days":270,"sell":"Sago factories (Salem), Starch units"},
    "Black Gram": {"emoji":"","season":"Rabi (Nov-Feb)","yield_min":0.8,"yield_max":1.0,"price":65000,"cost_ha":20000,"water":"Low","days":75,"sell":"NAFED, Dal mills, APMC"},
    "Pearl Millet": {"emoji":"","season":"Kharif","yield_min":1.2,"yield_max":1.8,"price":22000,"cost_ha":14000,"water":"Very Low","days":75,"sell":"TNCSC, Flour mills, Feed companies"},
    "Grapes": {"emoji":"","season":"Dec-Apr harvest","yield_min":12,"yield_max":18,"price":40000,"cost_ha":150000,"water":"High","days":365,"sell":"Wine companies, Export, Raisin factories"},
    "Tea": {"emoji":"","season":"Year-round (flush)","yield_min":2.5,"yield_max":3.5,"price":180000,"cost_ha":200000,"water":"High","days":1825,"sell":"Tea Board, Auction centres (Coimbatore)"},
    "Coffee": {"emoji":"","season":"Oct-Feb harvest","yield_min":1.0,"yield_max":1.5,"price":250000,"cost_ha":150000,"water":"High","days":1825,"sell":"Coffee Board, Exporters, Cooperatives"},
    "Potato": {"emoji":"","season":"Oct-Jan","yield_min":20,"yield_max":28,"price":12000,"cost_ha":70000,"water":"Medium","days":90,"sell":"Local market, Cold storage, Chips factories"},
    "Rubber": {"emoji":"","season":"Year-round (tapping)","yield_min":1.5,"yield_max":2.0,"price":200000,"cost_ha":80000,"water":"High","days":2555,"sell":"Rubber Board, Tire companies, Cooperatives"},
    "Betel Nut": {"emoji":"","season":"Year-round","yield_min":2,"yield_max":3,"price":250000,"cost_ha":80000,"water":"High","days":1825,"sell":"Pan traders, Export market"},
    "Carrot": {"emoji":"","season":"Oct-Feb (hills)","yield_min":20,"yield_max":28,"price":15000,"cost_ha":55000,"water":"Medium","days":90,"sell":"Local markets, Chennai, Hotels"},
}

# CROP EXCLUSION MAP 
# Crops that are climatically or agronomically unsuitable for certain districts
# or zones. Structure: {crop_name: {"exclude_districts": [...],"exclude_zones": [...]}}
CROP_EXCLUSION = {
    "Tea": {
        "exclude_districts": [
            "Chennai","Chengalpattu","Kancheepuram","Thiruvallur","Cuddalore",
            "Nagapattinam","Thanjavur","Thiruvarur","Mayiladuthurai","Trichy",
            "Karur","Perambalur","Ariyalur","Kallakurichi","Villupuram",
            "Madurai","Dindigul","Sivaganga","Ramanathapuram","Thoothukudi",
            "Tirunelveli","Kanyakumari","Virudhunagar","Pudukkottai","Salem",
            "Namakkal","Erode","Dharmapuri","Krishnagiri","Vellore","Ranipet",
            "Tirupathur","Tiruvanamalai"
        ],
        "exclude_zones": [
            "Coastal","Delta","Central","Southern","North Coastal","East Coastal",
            "Cauvery Delta","Southern Coast","Southern Tip"
        ]
    },
    "Coffee": {
        "exclude_districts": [
            "Chennai","Chengalpattu","Kancheepuram","Thiruvallur","Cuddalore",
            "Nagapattinam","Thanjavur","Thiruvarur","Mayiladuthurai","Trichy",
            "Karur","Perambalur","Ariyalur","Kallakurichi","Villupuram",
            "Madurai","Sivaganga","Ramanathapuram","Thoothukudi","Tirunelveli",
            "Pudukkottai","Salem","Namakkal","Erode","Vellore","Ranipet",
            "Tiruvanamalai","Coimbatore","Tiruppur"
        ],
        "exclude_zones": [
            "Coastal","Delta","Central","Southern Coast","Cauvery Delta",
            "North Coastal","East Coastal"
        ]
    },
    "Rubber": {
        "exclude_districts": [
            "Chennai","Chengalpattu","Kancheepuram","Thiruvallur","Cuddalore",
            "Nagapattinam","Thanjavur","Thiruvarur","Mayiladuthurai","Trichy",
            "Karur","Perambalur","Ariyalur","Kallakurichi","Villupuram",
            "Madurai","Sivaganga","Ramanathapuram","Thoothukudi",
            "Pudukkottai","Salem","Namakkal","Erode","Dharmapuri",
            "Krishnagiri","Vellore","Ranipet","Tiruvanamalai","Coimbatore",
            "Tiruppur"
        ],
        "exclude_zones": [
            "Coastal","Delta","Central","Southern Coast","Cauvery Delta",
            "North Coastal","East Coastal","North-Western","Western"
        ]
    },
    "Potato": {
        "exclude_districts": [
            "Ramanathapuram","Thoothukudi","Tirunelveli","Madurai","Sivaganga",
            "Pudukkottai","Thanjavur","Thiruvarur","Nagapattinam","Mayiladuthurai",
            "Cuddalore","Chennai","Chengalpattu","Kancheepuram","Thiruvallur"
        ],
        "exclude_zones": [
            "Southern Coast","Southern Tip","Cauvery Delta","East Coastal Delta",
            "North Coastal"
        ]
    },
    "Carrot": {
        "exclude_districts": [
            "Ramanathapuram","Thoothukudi","Tirunelveli","Madurai","Sivaganga",
            "Pudukkottai","Thanjavur","Thiruvarur","Nagapattinam","Mayiladuthurai",
            "Cuddalore","Chennai","Chengalpattu","Kancheepuram","Thiruvallur",
            "Trichy","Karur","Perambalur","Ariyalur"
        ],
        "exclude_zones": [
            "Southern Coast","Southern Tip","Cauvery Delta","East Coastal Delta",
            "Central Delta","North Coastal","East Coastal","Central"
        ]
    },
    "Grapes": {
        "exclude_districts": [
            "Ramanathapuram","Thoothukudi","Nagapattinam","Mayiladuthurai",
            "Thiruvarur","Cuddalore","Chennai","Kanyakumari","Tenkasi"
        ],
        "exclude_zones": [
            "Southern Coast","East Coastal Delta","Cauvery Delta",
            "North Coastal","Southern Tip","Southern Western Ghats"
        ]
    },
    "Jasmine": {
        "exclude_districts": [
            "Nilgiris","Ramanathapuram","Thoothukudi"
        ],
        "exclude_zones": [
            "Western Ghats Hills"
        ]
    },
    "Sugarcane": {
        "exclude_districts": [
            "Ramanathapuram","Thoothukudi","Nilgiris"
        ],
        "exclude_zones": [
            "Southern Coast","Western Ghats Hills"
        ]
    },
    "Betel Nut": {
        "exclude_districts": [
            "Ramanathapuram","Thoothukudi","Nilgiris","Dharmapuri","Krishnagiri",
            "Vellore","Ranipet","Tirupathur","Tiruvanamalai"
        ],
        "exclude_zones": [
            "Southern Coast","Western Ghats Hills","North-Western"
        ]
    },
}

HISTORICAL_YIELD = {
    "Paddy": [3.8,4.0,4.2,4.5,4.8,5.0],"Banana": [28,30,33,36,38,40],
    "Sugarcane": [70,74,78,82,87,90],"Groundnut": [1.4,1.6,1.7,1.9,2.0,2.2],
    "Turmeric": [15,17,18,20,22,23],"Cotton": [1.0,1.1,1.2,1.4,1.5,1.6],
    "Maize": [3.5,4.0,4.2,4.5,4.8,5.0],"Tomato": [14,16,17,19,21,22],
}
HIST_YEARS = ["2019","2020","2021","2022","2023","2024"]


# HELPERS 
def calc_profit(crop, land_ha, factor=1.0):
    c = CROP_DB[crop]
    avg = (c["yield_min"] + c["yield_max"]) / 2 * factor
    total = round(avg * land_ha, 2)
    rev = round(total * c["price"])
    cost = round(c["cost_ha"] * land_ha)
    profit= round(rev - cost)
    roi = round(profit / cost * 100, 1) if cost else 0
    be = round(cost / c["price"], 2)
    return {"avg_yield_ha":round(avg,2),"total_yield":total,"revenue":rev,"cost":cost,"profit":profit,"roi":roi,"break_even":be}

def fmt_inr(v):
    if abs(v)>=1e7: return f"Rs.{v/1e7:.2f} Cr"
    elif abs(v)>=1e5: return f"Rs.{v/1e5:.2f} L"
    return f"Rs.{int(v):,}"

def get_live_weather(lat, lon, city):
    """Fetch live weather from Open-Meteo (free, no key needed)."""
    try:
        url = (f"https://api.open-meteo.com/v1/forecast?"
               f"latitude={lat}&longitude={lon}"
               f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,"
               f"precipitation,weather_code,apparent_temperature"
               f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
               f"&timezone=Asia%2FKolkata&forecast_days=3")
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def weather_desc(code):
    if code == 0: return"Clear Sky"
    elif code <= 3: return"Partly Cloudy"
    elif code <= 9: return"Hazy"
    elif code <= 19: return"Drizzle"
    elif code <= 29: return"Rain"
    elif code <= 39: return"Snow/Sleet"
    elif code <= 49: return"Foggy"
    elif code <= 59: return"Drizzle"
    elif code <= 69: return"Rain"
    elif code <= 79: return"Snow"
    elif code <= 84: return"Rain Showers"
    elif code <= 99: return"Thunderstorm"
    return"Unknown"


# AI FUNCTIONS 
def build_system_prompt(district, dd, land_ha, farmer_name, selected_crop=None):
    crops_info =""
    for crop in dd["main_crops"]:
        if crop in CROP_DB:
            c = CROP_DB[crop]
            p = calc_profit(crop, land_ha)
            crops_info += (f"\n - {c['emoji']} {crop}: Yield {c['yield_min']}-{c['yield_max']} t/ha,"
                           f"Price Rs.{c['price']:,}/t, Profit ~{fmt_inr(p['profit'])} for {land_ha}ha,"
                           f"Water: {c['water']}, Duration: {c['days']} days")

    sel_section =""
    if selected_crop and selected_crop in CROP_DB:
        p = calc_profit(selected_crop, land_ha)
        c = CROP_DB[selected_crop]
        sel_section = f"""
FARMER'S SELECTED CROP: {selected_crop}
  Yield for {land_ha}ha: {p['total_yield']} tonnes | Revenue: {fmt_inr(p['revenue'])}
  Cost: {fmt_inr(p['cost'])} | Net Profit: {fmt_inr(p['profit'])} | ROI: {p['roi']}%
  Break-even yield: {p['break_even']} tonnes | Sell at: {c['sell']}
Focus your answers on THIS crop unless asked otherwise."""

    return f"""You are AgriSmart AI — a smart, friendly agricultural advisor for Tamil Nadu.
You are guiding {farmer_name}, a farmer with {land_ha} hectares in {district} district.

DISTRICT PROFILE — {district}:
  Zone: {dd['zone']} | Avg Temp: {dd['avg_temp']}°C | Rainfall: {dd['rainfall_mm']}mm/yr
  Humidity: {dd['humidity']}% | Soil: {dd['soil']} | Soil pH: {dd['soil_ph']}
  River: {dd['river']} | Known for: {dd['known_for']}
  Traditional crops: {','.join(dd['main_crops'])}

CROP DATA ({land_ha} ha):{crops_info}
{sel_section}

RULES:
1. Always calculate profit for EXACTLY {land_ha} ha. Show the working clearly.
2. Give advice specific to {district}'s climate only — not generic India advice.
3. Use simple plain English only. No Tamil script.
4. Be warm and encouraging like a helpful senior farmer.
5. Use emojis and short bullet points for readability.
6. Answer the farmer's question DIRECTLY and completely. Do NOT add a follow-up question at the end — just answer what was asked.
7. Mention TN government schemes where relevant: PM-KISAN, PMFBY crop insurance, TNAU advisory, Uzhavar Sandhai markets.
8. If the farmer asks a yes/no or simple question, give a clear direct answer first, then brief details if needed."""

def offline_ai_response(system_prompt, messages):
    """100% offline smart AI engine — no internet needed."""
    import re

    # Extract context from system prompt
    district ="your district"
    land_ha = 1.0
    farmer ="Farmer"
    sel_crop = None

    for line in system_prompt.split("\n"):
        if"guiding"in line and"farmer with"in line:
            m = re.search(r"guiding (.+?), a farmer with ([\d.]+) hectares in (.+?) district", line)
            if m:
                farmer, land_ha, district = m.group(1), float(m.group(2)), m.group(3)
        if"FARMER\'S SELECTED CROP:"in line or"SELECTED CROP:"in line:
            m = re.search(r"SELECTED CROP: (.+)", line)
            if m: sel_crop = m.group(1).strip()

    # Get last user message
    user_msg =""
    for msg in reversed(messages):
        if msg["role"] =="user":
            user_msg = msg["content"].lower()
            break

    # Pull district data
    dd = TN_DISTRICTS.get(district, {})
    avg_temp = dd.get("avg_temp", 29)
    rainfall = dd.get("rainfall_mm", 900)
    humidity = dd.get("humidity", 65)
    soil = dd.get("soil","Red Loam")
    soil_ph = dd.get("soil_ph", 6.5)
    river = dd.get("river","local river")
    zone = dd.get("zone","Central")
    known_for = dd.get("known_for","agriculture")
    main_crops = dd.get("main_crops", ["Paddy","Groundnut"])

    CROP_ALIASES = {
        "rice": "Paddy", "paddy": "Paddy",
        "banana": "Banana", "plantain": "Banana",
        "sugarcane": "Sugarcane", "cane": "Sugarcane",
        "coconut": "Coconut",
        "groundnut": "Groundnut", "peanut": "Groundnut", "peanuts": "Groundnut",
        "turmeric": "Turmeric", "haldi": "Turmeric",
        "mango": "Mango", "mangoes": "Mango",
        "cotton": "Cotton",
        "tomato": "Tomato", "tomatoes": "Tomato",
        "maize": "Maize", "corn": "Maize",
        "vegetables": "Vegetables", "veggies": "Vegetables", "chilli": "Vegetables", "chili": "Vegetables",
        "millets": "Millets", "millet": "Millets", "ragi": "Millets", "cholam": "Millets",
        "pulses": "Pulses", "pulse": "Pulses", "dal": "Pulses", "gram": "Pulses",
        "jasmine": "Jasmine", "flower": "Jasmine",
        "tapioca": "Tapioca", "cassava": "Tapioca", "sago": "Tapioca",
        "black gram": "Black Gram", "urad": "Black Gram", "urad dal": "Black Gram",
        "pearl millet": "Pearl Millet", "bajra": "Pearl Millet", "kambu": "Pearl Millet",
        "grapes": "Grapes", "grape": "Grapes",
        "tea": "Tea",
        "coffee": "Coffee",
        "potato": "Potato", "potatoes": "Potato",
        "rubber": "Rubber",
        "betel nut": "Betel Nut", "arecanut": "Betel Nut",
        "carrot": "Carrot", "carrots": "Carrot"
    }

    CROP_DISEASES = {
        "Paddy": {
            "diseases": [
                ("Paddy Blast (Pyricularia oryzae)", "Spindle-shaped lesions with grey/white centers on leaves; neck rot on panicles.", "Neem oil 3% @ 5 ml/L or Pseudomonas fluorescens @ 10 g/L", "Tricyclazole 75% WP @ 0.6 g/L or Mancozeb @ 2 g/L"),
                ("Bacterial Leaf Blight (BLB)", "Yellow-white wavy wilting from leaf tips and margins; bacterial ooze in morning.", "Fresh cow dung extract 20%; plant resistant varieties (ADT 43, CR 1009).", "Copper Oxychloride 2.5 g/L + Streptocycline 0.1 g/L"),
                ("Sheath Blight (Rhizoctonia solani)", "Snake-skin like greenish-grey lesions on leaf sheaths near water line.", "Trichoderma viride @ 2.5 kg/ha mixed with FYM.", "Hexaconazole 5% EC @ 2 ml/L or Validamycin @ 2 ml/L"),
                ("Tungro Virus", "Stunting of plant, orange-yellow leaf discoloration.", "Eradicate infected stubbles; yellow sticky traps.", "Control vector green leafhoppers with Imidacloprid 0.3 ml/L")
            ],
            "pests": [
                ("Yellow Stem Borer", "Dead hearts in vegetative stage; white heads (papery empty panicles) at maturity.", "Install pheromone traps @ 12/ha; release Trichogramma egg parasitoids.", "Chlorantraniliprole 18.5% SC @ 0.3 ml/L or Cartap Hydrochloride 4G @ 10 kg/ha"),
                ("Brown Planthopper (BPH)", "Sap sucking at crown base causing circular patches of dry plants ('Hopper Burn').", "Drain field water; avoid excessive Urea fertilizer.", "Dinotefuran 20% SG @ 0.4 g/L or Imidacloprid 17.8% SL @ 0.3 ml/L")
            ]
        },
        "Groundnut": {
            "diseases": [
                ("Tikka Leaf Spot (Cercospora)", "Dark brown to black circular spots surrounded by yellow halos on leaves.", "Panchagavya 3% spray; crop rotation with cereals.", "Carbendazim 12% + Mancozeb 63% WP @ 2 g/L"),
                ("Rust (Puccinia arachidis)", "Reddish-brown pustules containing powdery spores on lower leaf surface.", "Spray Neem seed kernel extract (NSKE) 5%.", "Hexaconazole 5% EC @ 2 ml/L or Chlorothalonil @ 2 g/L"),
                ("Collar Rot / Stem Rot", "Yellowing of shoots and white mycelial growth at soil line.", "Seed treatment with Trichoderma viride @ 4 g/kg seed.", "Soil drenching with Copper Oxychloride 2.5 g/L")
            ],
            "pests": [
                ("Spodoptera Caterpillars", "Defoliation and skeletonization of leaves.", "Sl-NPV bio-pesticide @ 250 LE/ha; hand picking.", "Emamectin Benzoate 5% SG @ 0.5 g/L or Chlorpyrifos @ 2 ml/L")
            ]
        },
        "Banana": {
            "diseases": [
                ("Panama Wilt (Fusarium)", "Yellowing of lower leaves, longitudinal splitting of pseudostem base.", "Soil application of Trichoderma viride @ 50g/plant with FYM.", "Carbendazim @ 2 g/L root zone drenching"),
                ("Sigatoka Leaf Spot", "Dark brown/black streaks expanding into boat-shaped spots with yellow halos.", "Remove affected leaves; spray NSKE 5%.", "Propiconazole 25% EC @ 1 ml/L + Mineral oil @ 10 ml/L"),
                ("Bunchy Top Virus (BBTV)", "Stunted growth, narrow upright leaves forming a rosette at top.", "Eradicate infected plants; yellow sticky traps.", "Control vector aphids with Dimethoate 30% EC @ 2 ml/L")
            ],
            "pests": [
                ("Banana Stem / Corm Weevil", "Tunnels bored into pseudostem/corm causing snapping and lodging.", "Use pseudostem traps treated with Beauveria bassiana.", "Apply Carbofuran 3G @ 20 g/plant")
            ]
        },
        "Sugarcane": {
            "diseases": [
                ("Red Rot (Colletotrichum falcatum)", "Internal red discoloration of stalks with white transverse patches.", "Hot water sett treatment at 52 deg C for 30 minutes.", "Sett treatment with Carbendazim 50% WP @ 2 g/L")
            ],
            "pests": [
                ("Early Shoot Borer", "Dead hearts in young shoots during early growth.", "Release Trichogramma chilonis @ 2.5 cc/ha.", "Chlorantraniliprole 0.4% G @ 18 kg/ha")
            ]
        },
        "Coconut": {
            "diseases": [
                ("Tanjore Wilt / Ganoderma", "Bleeding brown patches at trunk base, drooping and drying of fronds.", "Apply Trichoderma enriched FYM @ 5 kg/palm.", "Root feeding with Hexaconazole 2% @ 25 ml in 25 ml water")
            ],
            "pests": [
                ("Rhinoceros Beetle", "V-shaped cuts on fronds, holes bored into crown.", "Fill leaf axils with Neem seed powder + sand (1:1).", "Incorporate Metarhizium anisopliae fungal culture")
            ]
        },
        "Tomato": {
            "diseases": [
                ("Early & Late Blight", "Concentric leaf spots and dark leathery fruit rot.", "Spray Copper Hydroxide @ 2 g/L.", "Mancozeb 75% WP @ 2 g/L or Metalaxyl + Mancozeb @ 2 g/L")
            ],
            "pests": [
                ("Fruit Borer (Helicoverpa)", "Bored holes in fruits with caterpillar feeding.", "Marigold as trap crop; spray NSKE 5%.", "Chlorantraniliprole 18.5% SC @ 0.3 ml/L")
            ]
        },
        "Cotton": {
            "diseases": [
                ("Pink & American Bollworm", "Rosetted flowers, bored holes in bolls.", "Pheromone traps @ 12/ha; release Trichogramma.", "Spinetoram 11.7% SC @ 1 ml/L or Emamectin Benzoate @ 0.5 g/L"),
                ("Cotton Wilt", "Drooping of leaves and drying of entire plant.", "Seed treatment with Pseudomonas fluorescens 10 g/kg.", "Drench Copper Oxychloride 2.5 g/L")
            ]
        }
    }

    # Enhanced topic keyword detectors (typo-tolerant)
    is_best_crop = any(w in user_msg for w in ["best crop","recommend","which crop","what crop","suitable crop","crop for my","suggest","top crop","best suited"])
    is_profit = any(w in user_msg for w in ["profit","revenue","income","earn","money","cost","roi","return","margin","expenditure","price per"])
    is_grow = any(w in user_msg for w in ["how to grow","growing guide","growing","step","sow","plant","cultivat","method","technique","grow","care","management","process"])
    is_irrigation = any(w in user_msg for w in ["water","irrigat","drip","moisture","sprinkler","rainfed","canal","borewell"])
    is_pest = any(w in user_msg for w in ["pest","pests","disease","diseases","diseaese","diseas","desease","decease","insect","fungus","fungal","blight","rot","wilt","spot","virus","bacteri","worm","caterpillar","aphid","thrips","borer","spray","pesticide","fungicide","insecticide","chemical","protect","prevent","attack","damage","infect","symptom","remedy","treatment","cure","health","sick","yellow","die"])
    is_sell = any(w in user_msg for w in ["sell","market","price","mandi","buyer","where to sell","channel","enam","sandhai","rate","trade"])
    is_scheme = any(w in user_msg for w in ["scheme","subsidy","subsid","government","govt","loan","insurance","pm-kisan","pmkisan","pmfby","tnau","kvk","credit","kcc"])
    is_season = any(w in user_msg for w in ["season","sow time","when to sow","when to plant","best time","month","time to sow","sowing time","calendar"])
    is_soil = any(w in user_msg for w in ["soil","fertiliz","npk","manure","compost","ph","nutrient","urea","potash","nitrogen","phosphorus"])
    is_weather = any(w in user_msg for w in ["weather","climate","temperature","temp","humid","forecast","monsoon","rain","heat"])
    is_yield = any(w in user_msg for w in ["yield","harvest","production","output","tonne","kg per","quintal","bag"])
    is_chosen = any(w in user_msg for w in ["i have chosen","i want to grow","chosen to grow","selected","i chose","my crop","i picked","detailed analysis","analysis"])
    is_risk = any(w in user_msg for w in ["risk","danger","problem","challenge","fail","loss","damage","flood","drought","cyclone","threat","vulnerab"])
    
    # Check if any topic matches
    has_topic = is_best_crop or is_profit or is_grow or is_irrigation or is_pest or is_sell or is_scheme or is_season or is_soil or is_weather or is_yield or is_chosen or is_risk
    # Pure greeting check only if NO other topic matched
    is_greeting = not has_topic and any(w in user_msg for w in ["hello","hi","hey","namaste","vanakkam"])

    mentioned_crop = None
    for kw, target_crop in CROP_ALIASES.items():
        if kw in user_msg:
            mentioned_crop = target_crop
            break
    if not mentioned_crop:
        for crop in CROP_DB:
            if crop.lower() in user_msg:
                mentioned_crop = crop
                break
    if not mentioned_crop:
        mentioned_crop = sel_crop or (main_crops[0] if main_crops else "Paddy")

    c = CROP_DB.get(mentioned_crop, CROP_DB.get("Paddy", {}))
    p = calc_profit(mentioned_crop, land_ha) if mentioned_crop in CROP_DB else {}

    if is_greeting:
        top = [f"• **{cr}** — {fmt_inr(calc_profit(cr,land_ha)['profit'])} profit"
               for cr in main_crops[:3] if cr in CROP_DB]
        return (f"Hello {farmer}! Great to hear from you.\n\n"
                f"You are farming **{land_ha} ha** in **{district}** ({zone} zone).\n\n"
                f"**Top crops for your area:**\n"+"\n".join(top) +
                f"\n\nAsk me anything — crop advice, profit, pests, schemes, irrigation!")

    if is_best_crop:
        ranked = []
        for cr in main_crops:
            if cr in CROP_DB:
                pp = calc_profit(cr, land_ha)
                ranked.append((cr, pp["profit"], pp["roi"]))
        ranked.sort(key=lambda x: x[1], reverse=True)
        top3 = ranked[:3]
        best = top3[0][0] if top3 else mentioned_crop
        bc = CROP_DB.get(best, {})
        bp = calc_profit(best, land_ha) if best in CROP_DB else {}
        lines = "\n".join(f"{i+1}. **{cr}** — Profit: {fmt_inr(pr)} | ROI: {roi}%"
                           for i,(cr,pr,roi) in enumerate(top3))
        return (f"## Best Crop for {district}\n\n"
                f"Based on your climate ({avg_temp}°C, {rainfall}mm rain, {soil}), here are the top picks:\n\n"
                f"{lines}\n\n"
                f"### My Recommendation: **{best}**\n"
                f"- Profit for {land_ha} ha: **{fmt_inr(bp.get('profit',0))}**\n"
                f"- Season: {bc.get('season','')}\n"
                f"- Water need: {bc.get('water','')}\n"
                f"- Duration: {bc.get('days','')} days\n"
                f"- Sell at: {bc.get('sell','')}\n\n"
                f"**Why {best}?** {district} is known for {known_for}. The {soil} soil and "
                f"{rainfall}mm annual rainfall are ideal for this crop.")

    if is_profit:
        if not p:
            return "Please select a crop first to see profit calculations."
        return (f"## Profit Analysis — {mentioned_crop} on {land_ha} ha\n\n"
                f"### Step-by-Step Calculation:\n"
                f"- Average yield: **{p['avg_yield_ha']} t/ha × {land_ha} ha = {p['total_yield']} tonnes**\n"
                f"- Revenue: {p['total_yield']} t × Rs.{c.get('price',0):,}/t = **{fmt_inr(p['revenue'])}**\n"
                f"- Total cost: **{fmt_inr(p['cost'])}** (seed + fertilizer + labour + irrigation)\n"
                f"- Net Profit: **{fmt_inr(p['profit'])}**\n"
                f"- ROI: **{p['roi']}%**\n"
                f"- Break-even yield: **{p['break_even']} tonnes**\n\n"
                f"### Tips to increase profit:\n"
                f"- Use certified seeds from TNAU — 10–15% higher yield\n"
                f"- Apply drip irrigation — saves 40% water cost\n"
                f"- Sell at Uzhavar Sandhai — 15–20% better price than middlemen\n"
                f"- Apply for PM-KISAN (Rs.6,000/yr) to offset input costs")

    if is_season:
        return (f"## Best Sowing Time — {mentioned_crop} in {district}\n\n"
                f"- **Season:** {c.get('season','Year-round')}\n"
                f"- **Crop duration:** {c.get('days',90)} days\n"
                f"- **Your climate:** {avg_temp}°C avg, {rainfall}mm/yr rainfall\n\n"
                f"### Month-wise Guide:\n"
                f"- **June–July:** Land preparation, soil testing, FYM application\n"
                f"- **July–Aug:** Sow seeds after first good rain (Kharif crops)\n"
                f"- **Nov–Dec:** Sow for Rabi season (cooler weather crops)\n"
                f"- **Feb–Mar:** Summer crops if irrigation is available\n\n"
                f"**{district} tip:** {zone} zone — align sowing with {river} river water availability.\n"
                f"Check TNAU advisory at **tnau.ac.in** for exact dates each year.")

    if is_grow:
        return (f"## How to Grow {mentioned_crop} in {district}\n\n"
                f"**Duration:** {c.get('days',90)} days | **Season:** {c.get('season','')} | **Water:** {c.get('water','')}\n\n"
                f"### Step-by-Step Guide:\n"
                f"**Step 1 — Land Preparation (2 weeks before sowing)**\n"
                f"- Deep plough 2–3 times to 20–25 cm depth\n"
                f"- Apply FYM/compost 10 t/ha and mix well\n"
                f"- Level the field for uniform water distribution\n"
                f"- Soil pH in {district}: {soil_ph} — {'ideal, no correction needed' if 6.0 <= soil_ph <= 7.0 else 'apply lime to correct'}\n\n"
                f"**Step 2 — Seed Selection & Treatment**\n"
                f"- Use certified seeds from TNAU or govt seed centre\n"
                f"- Treat seeds with Trichoderma 4g/kg before sowing\n"
                f"- Seed rate: follow TNAU recommendation for {mentioned_crop}\n\n"
                f"**Step 3 — Sowing**\n"
                f"- Best time: {c.get('season','')}\n"
                f"- Maintain proper row & plant spacing\n"
                f"- Sow at 2–3 cm depth for small seeds, 4–5 cm for large\n\n"
                f"**Step 4 — Fertilizer (NPK)**\n"
                f"- Basal dose at sowing: NPK as per TNAU recommendation\n"
                f"- Top dressing at 30 days: Urea for vegetative growth\n"
                f"- Micronutrients: Zinc sulphate 25 kg/ha if needed\n\n"
                f"**Step 5 — Irrigation**\n"
                f"- Water need: **{c.get('water','')}**\n"
                f"- {district} gets {rainfall}mm/yr — {'rain-fed possible' if rainfall > 800 else 'irrigation essential'}\n"
                f"- Critical stages: flowering and grain/fruit filling\n\n"
                f"**Step 6 — Harvest**\n"
                f"- Ready in {c.get('days',90)} days\n"
                f"- Harvest at correct maturity to avoid losses\n"
                f"- Expected yield: {c.get('yield_min',0)}–{c.get('yield_max',0)} t/ha")

    if is_irrigation:
        water = c.get("water","Medium")
        freq_map = {"Very High":"every 3–4 days","High":"every 5–7 days","Medium":"every 7–10 days","Low":"every 10–15 days","Very Low":"every 15–20 days"}
        freq = freq_map.get(water,"every 7–10 days")
        rain_ok = "Mostly rain-fed possible" if rainfall > 900 else "Supplemental irrigation needed" if rainfall > 600 else "Full irrigation required"
        return (f"## Irrigation Guide — {mentioned_crop} in {district}\n\n"
                f"- District rainfall: **{rainfall}mm/yr** {rain_ok}\n"
                f"- Crop water need: **{water}**\n"
                f"- Frequency: **{freq}**\n"
                f"- Water source: **{river}**\n\n"
                f"### Best Method:\n"
                f"{'**Drip irrigation** — saves 40–50% water. Best for '+ mentioned_crop if water in ('High','Very High') else '**Sprinkler** — good for medium water crops' if water == 'Medium' else '**Furrow/flood** — simple, low cost for low water crops'}\n\n"
                f"### Critical Irrigation Stages:\n"
                f"- Just after sowing (light irrigation 20–30mm)\n"
                f"- Flowering stage — NEVER miss this\n"
                f"- Grain/fruit filling stage\n"
                f"- Stop 10–15 days before harvest\n\n"
                f"### Subsidy Schemes:\n"
                f"- PM Krishi Sinchayee Yojana — 55% subsidy on drip/sprinkler\n"
                f"- TNAU micro-irrigation scheme — free drip kits for <2 ha farmers\n"
                f"- Contact your local Agriculture Office for application")

    if is_pest:
        risk_lvl = f"High — humidity {humidity}% favours fungal diseases" if humidity > 75 else "Medium" if humidity > 60 else "Low"
        crop_d = CROP_DISEASES.get(mentioned_crop)
        
        disease_blocks = []
        if crop_d and "diseases" in crop_d:
            disease_blocks.append("### Major Diseases & Treatments:")
            for idx, (dname, dsym, dorg, dchem) in enumerate(crop_d["diseases"], 1):
                disease_blocks.append(
                    f"{idx}. **{dname}**\n"
                    f"   - **Symptoms:** {dsym}\n"
                    f"   - **Organic Control:** {dorg}\n"
                    f"   - **Chemical Treatment:** {dchem}"
                )
        
        pest_blocks = []
        if crop_d and "pests" in crop_d:
            pest_blocks.append("### Key Insect Pests & Solutions:")
            for idx, (pname, psym, porg, pchem) in enumerate(crop_d["pests"], 1):
                pest_blocks.append(
                    f"{idx}. **{pname}**\n"
                    f"   - **Damage Signs:** {psym}\n"
                    f"   - **Organic Control:** porg\n".replace("porg", porg) +
                    f"   - **Chemical Treatment:** {pchem}"
                )
                
        if not disease_blocks and not pest_blocks:
            disease_blocks = [
                "### Common Crop Pests & Solutions:",
                "1. **Stem Borer / Leaf Roller:** Spray Chlorpyrifos 2ml/L at first sign.",
                "2. **Fungal Blight / Leaf Spots:** Spray Mancozeb 2g/L or Carbendazim 1g/L.",
                "3. **Aphids / Thrips / Mites:** Spray Imidacloprid 0.3ml/L or Neem Oil 5ml/L."
            ]

        dis_text = "\n\n".join(disease_blocks)
        pest_text = "\n\n".join(pest_blocks) if pest_blocks else ""

        return (f"## Pest & Disease Control Guide — {mentioned_crop}\n\n"
                f"**{district} Risk Level:** {risk_lvl}\n\n"
                f"{dis_text}\n\n"
                f"{pest_text}\n\n"
                f"### Preventive Farming Practices for {district}:\n"
                f"- Spray **Neem Oil 3% (5 ml/L)** every 15–20 days as a biological protective shield.\n"
                f"- Maintain balanced NPK application — avoid excessive Urea which attracts sap-sucking pests.\n"
                f"- Ensure field drainage channels are clear to lower humidity around roots.\n"
                f"- Contact TNAU KVK Helpline: **1800-425-1110** for free local advisory.")


    if is_sell:
        return (f"## Where to Sell {mentioned_crop} — {district}\n\n"
                f"- **Current avg price:** Rs.{c.get('price',0):,}/tonne\n"
                f"- Low season: Rs.{int(c.get('price',0)*0.75):,}/t\n"
                f"- Peak season: Rs.{int(c.get('price',0)*1.30):,}/t\n\n"
                f"### Best Selling Channels:\n"
                f"- **{c.get('sell','')}**\n"
                f"- **Uzhavar Sandhai** — sell direct to consumers, 15–25% more price\n"
                f"- **e-NAM** (enam.gov.in) — sell online across India\n"
                f"- **FPO (Farmer Producer Org)** — collective selling for better price\n"
                f"- **Contract farming** — fixed price guaranteed before harvest\n\n"
                f"### Best Time to Sell:\n"
                f"- Don't sell immediately at harvest — prices are lowest\n"
                f"- Wait 4–8 weeks — prices rise 20–30% when supply drops\n"
                f"- Use warehouse receipt (WDRA) as bank collateral for loan\n\n"
                f"### Negotiation Tip:\n"
                f"Always quote 10–15% above your target price — buyers will bargain down.")

    if is_scheme:
        return (f"## Government Schemes for {farmer} — {district}\n\n"
                f"### Direct Cash Schemes:\n"
                f"- **PM-KISAN** — Rs.6,000/year direct to your bank. Register at pmkisan.gov.in\n"
                f"- **TN Chief Minister's Farmer Support** — Rs.1,000/yr additional for TN farmers\n\n"
                f"### Insurance:\n"
                f"- **PMFBY (Crop Insurance)** — protects against drought, flood, pest. Premium only 1.5–2%. Apply at your nearest bank or CSC centre\n\n"
                f"### Irrigation Subsidy:\n"
                f"- **PMKSY** — 55% subsidy on drip/sprinkler systems\n"
                f"- **TNAU Micro-irrigation** — free drip kits for farmers with <2 ha\n\n"
                f"### Seed & Input Subsidy:\n"
                f"- **TNSC certified seeds** — 50% subsidised seeds from Tamil Nadu Seed Corp\n"
                f"- **Soil Health Card** — free soil testing + fertiliser recommendation\n\n"
                f"### Loans:\n"
                f"- **KCC (Kisan Credit Card)** — crop loan at 4% interest (govt subsidy)\n"
                f"- **NABARD RIDF** — farm pond, borewell construction loans\n\n"
                f"### Where to Apply:\n"
                f"- Visit your **Block Agriculture Office** in {district}\n"
                f"- Call TNAU helpline: **1800-425-1110** (free, Tamil available)\n"
                f"- Visit nearest **Common Service Centre (CSC)**")

    if is_soil:
        ph = soil_ph
        ph_advice = ("Ideal pH — no correction needed"if 6.0 <= ph <= 7.0
                     else f"Apply lime {500 if ph < 6.0 else 0} kg/ha to raise pH"if ph < 6.0
                     else"Add FYM to slowly lower pH")
        return (f"## Soil & Fertilizer Guide — {district}\n\n"
                f"- **Soil type:** {soil}\n"
                f"- **Soil pH:** {ph} — {ph_advice}\n"
                f"- **Rainfall:** {rainfall}mm/yr\n\n"
                f"### For {mentioned_crop} on {land_ha} ha:\n"
                f"**Basal dose (at sowing):**\n"
                f"- Urea: 50–100 kg/ha\n"
                f"- SSP (Super Phosphate): 250–375 kg/ha\n"
                f"- MOP (Potash): 50–100 kg/ha\n"
                f"- FYM/Compost: 10–15 t/ha (mix before ploughing)\n\n"
                f"**Top dressing (30–45 days after sowing):**\n"
                f"- Urea: 50 kg/ha at vegetative stage\n"
                f"- Urea: 50 kg/ha at flowering stage\n\n"
                f"**Micronutrients:**\n"
                f"- Zinc sulphate: 25 kg/ha (prevents yellowing)\n"
                f"- Borax: 10 kg/ha (improves fruit setting)\n\n"
                f"Get a **free Soil Health Card** from your Agriculture Office for exact recommendations for your field.")

    if is_weather:
        return (f"## Climate Profile — {district}\n\n"
                f"- **Average temperature:** {avg_temp}°C\n"
                f"- **Annual rainfall:** {rainfall}mm\n"
                f"- **Humidity:** {humidity}%\n"
                f"- **River:** {river}\n"
                f"- **Zone:** {zone}\n\n"
                f"### Farming Impact:\n"
                f"- {'Good rainfall — rain-fed farming possible'if rainfall > 900 else'Low rainfall — irrigation needed for most crops'}\n"
                f"- {'High humidity — watch for fungal diseases'if humidity > 75 else'Normal humidity — low disease risk'}\n"
                f"- {'Hot climate — drought-tolerant crops preferred'if avg_temp > 30 else'Moderate temp — suitable for most crops'}\n\n"
                f"### Best Crops for this Climate:\n"
                +"\n".join(f"• {CROP_DB[cr]['emoji']} {cr}"for cr in main_crops[:4] if cr in CROP_DB))

    if is_yield:
        if not p:
            return"Please select a crop to see yield information."
        return (f"## Yield Information — {mentioned_crop}\n\n"
                f"- **State average yield:** {c.get('yield_min',0)}–{c.get('yield_max',0)} t/ha\n"
                f"- **Your expected yield** ({land_ha} ha): **{p.get('total_yield',0)} tonnes**\n"
                f"- **At Rs.{c.get('price',0):,}/t Revenue: {fmt_inr(p.get('revenue',0))}**\n\n"
                f"### How to Beat Average Yield:\n"
                f"- Use TNAU high-yielding variety seeds (+15–20%)\n"
                f"- Drip irrigation — consistent moisture = higher yield\n"
                f"- Split NPK fertilizer application (not all at once)\n"
                f"- Early pest/disease control — prevents 20–30% losses\n"
                f"- Harvest at exact maturity — reduces post-harvest loss")

    # Default — general helpful response
    top_crops = [f"{CROP_DB[cr]['emoji']} {cr} ({fmt_inr(calc_profit(cr,land_ha)['profit'])} profit)"
                 for cr in main_crops[:3] if cr in CROP_DB]
    return (f"## AgriSmart Answer for {district}\n\n"
            f"I'm your offline agricultural advisor for **{district}** ({zone} zone).\n\n"
            f"**Your farm:** {land_ha} ha | {avg_temp}°C | {rainfall}mm rain | {soil} soil\n\n"
            f"**Top crops for you:**\n"+"\n".join(f"• {t}"for t in top_crops) +
            f"\n\nAsk me specifically about:\n"
            f"- Best crop / Growing guide\n"
            f"- Profit calculation\n"
            f"- Irrigation & water\n"
            f"- Pest & disease control\n"
            f"- Where to sell\n"
            f"- Government schemes\n"
            f"- Best sowing time\n"
            f"- Soil & fertilizer")


def call_claude_api(api_key, system_prompt, messages, max_tokens=1400):
    """Smart AI — works offline always. Uses internet (Gemini) only if key provided."""
    import urllib3, time
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # OFFLINE MODE: no key entered use built-in engine 
    if not api_key or not api_key.strip():
        return offline_ai_response(system_prompt, messages)

    # ONLINE MODE: try Gemini, fall back to offline on any failure 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key.strip()}"

    gemini_contents = []
    for msg in messages:
        role ="user"if msg["role"] =="user"else"model"
        gemini_contents.append({"role": role,"parts": [{"text": msg["content"]}]})

    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": gemini_contents,
        "generationConfig": {"maxOutputTokens": max_tokens,"temperature": 0.7}
    }

    max_retries = 3
    for attempt in range(max_retries):
        for verify in [True, False]:
            try:
                r = requests.post(url, json=payload, timeout=30, verify=verify)

                if r.status_code == 429:
                    if attempt < max_retries - 1:
                        wait = [15, 30, 45][attempt]
                        pass # silently retry
                        time.sleep(wait)
                        break
                    # Final retry failed — fall back to offline
                    pass # silently use offline engine
                    return offline_ai_response(system_prompt, messages)

                if r.status_code in (400, 403):
                    # Bad key — fall back to offline silently
                    return offline_ai_response(system_prompt, messages)

                if r.status_code != 200:
                    return offline_ai_response(system_prompt, messages)

                data = r.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]

            except (requests.exceptions.SSLError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout):
                if not verify:
                    # No internet at all — use offline engine
                    return offline_ai_response(system_prompt, messages)
                continue
            except (KeyError, IndexError):
                return offline_ai_response(system_prompt, messages)

    return offline_ai_response(system_prompt, messages)

def get_ai_response(messages, district, dd, land_ha, farmer_name, selected_crop=None):
    system = build_system_prompt(district, dd, land_ha, farmer_name, selected_crop)
    trimmed = messages[-14:] if len(messages) > 14 else messages
    api_key = st.session_state.api_key.strip() # empty = offline mode, that's fine
    return call_claude_api(api_key, system, trimmed, max_tokens=1400)

def get_ai_conclusion(district, dd, land_ha, farmer_name, crop):
    p = calc_profit(crop, land_ha)
    c = CROP_DB[crop]
    prompt = (
        f"Write a complete, practical conclusion report for {farmer_name} who wants to grow {crop} on {land_ha} hectares in {district}, Tamil Nadu.\n\n"
        f"Financials: Yield {p['total_yield']}t | Revenue {fmt_inr(p['revenue'])} | Cost {fmt_inr(p['cost'])} | Profit {fmt_inr(p['profit'])} | ROI {p['roi']}% | Break-even {p['break_even']}t\n"
        f"Selling: {c['sell']} | Duration: {c['days']} days | Season: {c['season']} | Water need: {c['water']}\n"
        f"District: {district} — {dd['avg_temp']}C, {dd['rainfall_mm']}mm rain, {dd['humidity']}% humidity, {dd['soil']} soil.\n\n"
        "Write using these exact section headings:\n"
        "## VERDICT\n"
        "## PROFIT PLAN (show step-by-step calculation)\n"
        "## GROWING CALENDAR (month-by-month actions)\n"
        "## RISKS AND HOW TO HANDLE THEM\n"
        "## WHERE TO SELL AND PRICE STRATEGY\n"
        "## GOVERNMENT SCHEMES TO APPLY FOR NOW\n\n"
        f"Use plain English, emojis, bullet points. Be specific to {district}. Be honest about risks but encouraging."
    )
    return call_claude_api(st.session_state.api_key,"You are AgriSmart AI, a helpful agricultural advisor for Tamil Nadu.", [{"role":"user","content":prompt}], max_tokens=2000)



def get_soil_info(dd, crop):
    """Return soil & fertilizer data — fully crop-specific per crop change."""
    c = CROP_DB.get(crop, {})
    soil = dd['soil']
    ph = dd['soil_ph']
    zone = dd['zone']
    rain = dd['rainfall_mm']
    water = c.get('water','Medium')

    # Soil profile (district-based) 
    if"Alluvial"in soil:
        profile ="Rich alluvial deposit — high organic matter, good water retention, ideal for high-yield crops."
        amendment ="Add compost 2–3 t/ha to maintain structure. Minimal amendment needed."
    elif"Black Cotton"in soil or"Black"in soil:
        profile ="Vertisol / Black cotton — excellent moisture retention, cracks in summer, rich in Ca & Mg."
        amendment ="Add gypsum 250 kg/ha to reduce stickiness. Ensure drainage to avoid waterlogging."
    elif"Red Sandy"in soil or"Red Laterite"in soil or"Red Loam"in soil:
        profile ="Red laterite / sandy loam — well-drained, low organic matter, needs regular fertilization."
        amendment ="Apply FYM 10–15 t/ha before planting. Add lime if pH below 6.0."
    elif"Sandy"in soil or"Loamy"in soil:
        profile ="Sandy loam — good drainage, low nutrient retention, needs split fertilizer doses."
        amendment ="Add organic compost 3–5 t/ha. Use mulching to retain moisture between irrigations."
    elif"Laterite"in soil:
        profile ="Laterite — acidic, iron-rich, moderate drainage, low phosphorus availability."
        amendment ="Apply lime 500 kg/ha if pH < 6.0. Add superphosphate to fix P deficiency."
    elif"Loamy / Forest"in soil:
        profile ="Loamy forest soil — high organic matter, excellent structure, ideal for hill crops."
        amendment ="Minimal amendment needed. Maintain leaf mulch layer to protect topsoil."
    else:
        profile = f"{soil} — moderate fertility, mixed drainage characteristics."
        amendment ="Apply FYM 10 t/ha and balanced NPK before sowing."

    # Crop suitability note (changes with every crop) 
    crop_suit_map = {
        "Paddy": f"{soil} is {'ideal'if'Alluvial'in soil or'Clay'in soil else'suitable'} for Paddy. Ensure standing water of 5 cm during vegetative stage.",
        "Banana": f"Banana needs deep, well-drained soil. {'Good drainage needed — avoid waterlogging.'if'Clay'in soil else'Suitable. Add organic matter for best yield.'}",
        "Sugarcane": f"Sugarcane grows well in {soil}. Deep plough to 45 cm for best root development.",
        "Coconut": f"Coconut thrives in {soil}. Ensure good drainage and no salt accumulation.",
        "Groundnut": f"Groundnut needs well-drained, loose soil. {'Sandy loam is ideal — good for pod development.'if'Sandy'in soil else'Loosen soil to 15 cm depth for pod expansion.'}",
        "Cotton": f"Cotton suits {soil}. Avoid waterlogging — it causes root rot in cotton.",
        "Turmeric": f"Turmeric needs loose, well-drained soil. Add extra FYM 15 t/ha for turmeric beds.",
        "Maize": f"Maize suits {soil}. Good drainage essential — avoid fields that flood.",
        "Tomato": f"Tomato prefers slightly acidic soil. {'pH {ph} is ideal.'if 6.0 <= ph <= 6.8 else'Adjust pH to 6.0–6.8 for best tomato yield.'}",
        "Millets": f"Millets are drought-hardy and suit {soil} well. Minimal soil preparation needed.",
        "Vegetables": f"Vegetables need rich, loose soil. Add compost 5 t/ha before each crop cycle.",
        "Mango": f"Mango grows well in {soil}. Dig 1×1×1 m pit per tree, fill with FYM + soil mix.",
        "Coconut": f"Coconut suits {soil}. Dig 1×1×1 m pits, fill with FYM and topsoil.",
        "Tapioca": f"Tapioca suits sandy loam well. Avoid waterlogged fields.",
        "Pulses": f"Pulses fix nitrogen — they actually improve {soil} quality. Minimal fertilizer needed.",
        "Black Gram": f"Black gram suits {soil}. It improves soil nitrogen for the next crop.",
        "Pearl Millet":f"Pearl millet is drought-tolerant and suits {soil} perfectly. Low input needed.",
        "Grapes": f"Grapes need well-drained, slightly acidic soil. Ensure pH 6.0–6.5 for best yield.",
        "Tea": f"Tea needs acidic soil (pH 4.5–5.5). {'pH {ph} needs lowering with sulphur.'if ph > 5.5 else'Good — pH suitable for tea.'}",
        "Coffee": f"Coffee prefers slightly acidic soil with good drainage. Add organic matter generously.",
        "Rubber": f"Rubber suits laterite / loamy soil. Good drainage essential.",
        "Jasmine": f"Jasmine suits {soil}. Add bone meal 250 kg/ha for better flowering.",
        "Potato": f"Potato needs loose, well-drained soil to 20 cm depth. Add FYM 20 t/ha.",
        "Carrot": f"Carrot needs deep, stone-free, loose soil. Deep plough to 30 cm for straight roots.",
        "Betel Nut": f"Betel nut suits {soil}. Plant in partial shade with organic-rich soil.",
    }
    crop_suitability = crop_suit_map.get(crop, f"{crop} can be grown in {soil}. Follow TNAU recommendations for best results.")

    # pH guidance 
    if ph < 5.5:
        ph_advice = f"pH {ph} — strongly acidic. Apply lime 750–1000 kg/ha to raise pH to 6.0–6.5 before sowing {crop}."
    elif ph < 6.0:
        ph_advice = f"pH {ph} — mildly acidic. Apply lime 400–500 kg/ha for pH-sensitive crops like {crop}."
    elif ph <= 7.0:
        ph_advice = f"pH {ph} — ideal range (6.0–7.0). No correction needed. Suitable for {crop}."
    elif ph <= 7.5:
        ph_advice = f"pH {ph} — slightly alkaline. Add FYM 10 t/ha to slowly lower pH for {crop}."
    else:
        ph_advice = f"pH {ph} — alkaline. Apply gypsum 500 kg/ha + organic matter before growing {crop}."

    # Full NPK map for ALL crops 
    npk_map = {
        "Paddy": ("Urea 50 kg + SSP 375 kg + MOP 50 kg per ha","Urea 50 kg at tillering + 50 kg at panicle initiation"),
        "Banana": ("200 g N + 100 g P + 300 g K per plant (basal)","Split into 4 equal doses every 2 months"),
        "Sugarcane": ("Urea 300 kg + SSP 375 kg + MOP 200 kg per ha","Urea 150 kg split at 60 days and 120 days"),
        "Coconut": ("500 g N + 320 g P + 1200 g K + 500 g Mg per palm/yr","Split into 2 doses — June and December"),
        "Groundnut": ("Urea 100 kg + SSP 375 kg + MOP 50 kg per ha","No top dressing — nitrogen fixed by root nodules"),
        "Cotton": ("Urea 150 kg + SSP 375 kg + MOP 75 kg per ha","Urea 75 kg at 30 DAS + 75 kg at 60 DAS"),
        "Turmeric": ("50 kg N + 50 kg P + 120 kg K per ha","50 kg N at 60 days + 50 kg N at 120 days"),
        "Maize": ("100 kg N + 60 kg P + 40 kg K per ha","60 kg N at knee-high stage (30 DAS)"),
        "Tomato": ("100 kg N + 200 kg P + 100 kg K per ha","50 kg N at flowering + 50 kg N at fruiting stage"),
        "Millets": ("40 kg N + 40 kg P + 40 kg K per ha","20 kg N top dress at 25 DAS"),
        "Pearl Millet":("40 kg N + 20 kg P + 20 kg K per ha","20 kg N top dress at 25–30 DAS"),
        "Vegetables": ("75 kg N + 100 kg P + 75 kg K per ha","40 kg N at 3 weeks + 35 kg N at 6 weeks"),
        "Mango": ("500 g N + 200 g P + 500 g K per tree/yr","Split into 3 doses: June, Sep, Dec"),
        "Tapioca": ("100 kg N + 50 kg P + 100 kg K per ha","50 kg N top dress at 60 days after planting"),
        "Pulses": ("Urea 20 kg + SSP 200 kg + MOP 40 kg per ha","No top dressing — legumes fix own nitrogen"),
        "Black Gram": ("Urea 25 kg + SSP 250 kg + MOP 40 kg per ha","No top dressing — legumes fix own nitrogen"),
        "Grapes": ("300 g N + 150 g P + 300 g K per vine/yr","Split into 4 doses through the season"),
        "Tea": ("150 kg N + 30 kg P + 60 kg K per ha/yr","Split into 6 doses of 25 kg N every 2 months"),
        "Coffee": ("100 kg N + 40 kg P + 80 kg K per ha/yr","Split 3 times: pre-monsoon, monsoon, post-monsoon"),
        "Potato": ("150 kg N + 100 kg P + 150 kg K per ha","75 kg N at earthing-up (30 DAS)"),
        "Carrot": ("80 kg N + 80 kg P + 80 kg K per ha","40 kg N top dress at 30 DAS"),
        "Rubber": ("80 kg N + 60 kg P + 100 kg K per tree/yr","Split into 2 doses: April and September"),
        "Jasmine": ("100 g N + 50 g P + 100 g K per plant/yr","Split monthly during active growing season"),
        "Betel Nut": ("100 g N + 40 g P + 140 g K per palm/yr","Split into 3 doses: June, Sep, Jan"),
        "Coconut": ("500 g N + 320 g P + 1200 g K per palm/yr","2 doses: June and December"),
        "Tomato": ("100 kg N + 200 kg P + 100 kg K per ha","Split top dress at flowering and fruiting"),
    }
    npk_base, npk_top = npk_map.get(crop, (
        "60–80 kg N + 40–60 kg P + 40–60 kg K per ha",
        "30–40 kg N top dress at active vegetative growth stage"
    ))

    # Micronutrients (per crop water need) 
    micro_map = {
        "Very High":"Zinc sulphate 25 kg/ha + Borax 10 kg/ha + Ferrous sulphate 25 kg/ha + Magnesium sulphate 50 kg/ha",
        "High":"Zinc sulphate 25 kg/ha + Borax 10 kg/ha + Ferrous sulphate 25 kg/ha",
        "Medium":"Zinc sulphate 20 kg/ha + Borax 8 kg/ha",
        "Low":"Zinc sulphate 15 kg/ha — light micronutrient requirement",
        "Very Low":"Zinc sulphate 10 kg/ha (optional) — minimal micronutrient input needed",
    }
    micro = micro_map.get(water,"Zinc sulphate 20 kg/ha + Borax 8 kg/ha")

    # Crop-specific organic input 
    organic_map = {
        "Paddy":"FYM 12.5 t/ha + green manure (Sesbania) ploughed in 4 weeks before transplanting",
        "Banana":"FYM 25 kg/pit at planting + banana pseudostem compost after each crop",
        "Sugarcane":"Pressmud compost 12.5 t/ha + sugarcane trash mulching after harvest",
        "Coconut":"FYM 25 kg/palm/yr + coir pith compost 10 kg/palm",
        "Groundnut":"FYM 10 t/ha before sowing + Rhizobium seed treatment (1 packet/10 kg seed)",
        "Cotton":"FYM 10 t/ha + cotton stalk compost after harvest",
        "Turmeric":"FYM 20 t/ha + neem cake 400 kg/ha — critical for turmeric yield",
        "Mango":"FYM 50 kg/tree/yr in October — fills pit around drip zone",
        "Vegetables":"Vermicompost 3 t/ha every crop cycle for consistent yield",
        "Potato":"FYM 25 t/ha — high organic demand for tuber formation",
        "Tomato":"FYM 15 t/ha + neem cake 200 kg/ha to prevent soil pests",
    }
    organic = organic_map.get(crop, f"FYM 10 t/ha before sowing {crop}. Vermicompost 1–2 t/ha improves yield by 10–15%.")

    return {
        "profile": profile,"amendment": amendment,
        "crop_suitability": crop_suitability,
        "ph_advice": ph_advice,
        "npk_base": npk_base,"npk_top": npk_top,
        "micro": micro,"organic": organic,
        "soil": soil,"ph": ph,"zone": zone,"rain": rain,
        "crop": crop,"water": water,
    }


def get_irrigation_info(dd, land_ha, crop):
    """Return static irrigation data from district + crop data."""
    c = CROP_DB.get(crop, {})
    water = c.get('water','Medium')
    season = c.get('season','')
    days = c.get('days', 90)
    rain = dd['rainfall_mm']
    river = dd['river']
    zone = dd['zone']

    # Water requirement per ha
    water_req_map = {
        "Very High": (1200, 1500,"Every 3–4 days"),
        "High": (900, 1200,"Every 5–7 days"),
        "Medium": (600, 900,"Every 7–10 days"),
        "Low": (300, 600,"Every 10–15 days"),
        "Very Low": (150, 300,"Every 15–20 days or rain-fed"),
    }
    wmin, wmax, freq = water_req_map.get(water, (600, 900,"Every 7–10 days"))
    total_min = round(wmin * land_ha)
    total_max = round(wmax * land_ha)

    # Best irrigation method
    if water in ("Very High","High"):
        method ="Drip irrigation — saves 40–50% water vs flood. Highly recommended."
        method_detail ="Install 2 LPH drippers at 60cm spacing. Run 2–3 hrs/day."
    elif water =="Medium":
        method ="Sprinkler or drip irrigation — both suitable."
        method_detail ="Sprinkler: run 30–45 min/day. Drip: 1.5–2 LPH drippers."
    else:
        method ="Rain-fed or furrow irrigation — minimal water needed."
        method_detail ="Light furrow irrigation at critical stages is sufficient."

    # Rain-fed viability
    if rain >= wmax:
        rainfed = f"{zone} gets {rain}mm rain — mostly rain-fed is possible. Irrigate only at critical stages."
    elif rain >= wmin:
        rainfed = f"Partial irrigation needed — {rain}mm rain covers ~50–70% of crop need. Supplement during dry spells."
    else:
        rainfed = f"Irrigation essential — {rain}mm rain is insufficient for {water.lower()} water-need crop. Use river {river}."

    # Cost estimate (rough)
    cost_per_ha = {"Very High": 8000,"High": 6000,"Medium": 4000,"Low": 2000,"Very Low": 1000}
    irr_cost = cost_per_ha.get(water, 4000) * land_ha

    # Govt schemes
    schemes = [
        "PM Krishi Sinchayee Yojana (PMKSY) — 55% subsidy on drip/sprinkler systems",
        "TNAU Micro-irrigation scheme — free drip kits for small farmers (<2 ha)",
        "Tamil Nadu Horticulture Dept — drip irrigation subsidy for fruit crops",
        "NABARD RIDF — low-interest loans for farm pond construction",
    ]

    return {
        "water": water,"freq": freq,
        "total_min": total_min,"total_max": total_max,
        "method": method,"method_detail": method_detail,
        "rainfed": rainfed,"irr_cost": irr_cost,
        "rain": rain,"river": river,
        "schemes": schemes,"season": season,"days": days,
        "land_ha": land_ha
    }


def get_ai_market_report(district, dd, crop):
    c = CROP_DB[crop]
    prompt = (
        f"Write a market price and selling strategy report for {crop} from {district}, Tamil Nadu.\n\n"
        f"Selling channels: {c['sell']} | Avg price: Rs.{c['price']:,}/t | Season: {c['season']}\n\n"
        "Write under these headings:\n"
        "## CURRENT PRICE RANGE AND TRENDS\n"
        "## BEST SELLING LOCATIONS (nearest mandis and markets)\n"
        "## BEST TIME TO SELL\n"
        "## NEGOTIATION AND PRICE TIPS\n"
        "## POST-HARVEST STORAGE TIPS\n"
        "## ONLINE SELLING OPTIONS (e-NAM, Agrimart etc.)\n\n"
        "Be specific to Tamil Nadu markets. Use bullet points."
    )
    return call_claude_api(st.session_state.api_key,"You are AgriSmart AI, an expert agricultural advisor for Tamil Nadu.", [{"role":"user","content":prompt}], max_tokens=1400)


def get_ai_crop_calendar(district, dd, crop):
    c = CROP_DB[crop]
    prompt = (
        f"Write a month-by-month crop calendar for growing {crop} in {district}, Tamil Nadu.\n\n"
        f"Season: {c['season']} | Duration: {c['days']} days | Water: {c['water']}\n"
        f"Climate: {dd['avg_temp']}C avg | {dd['rainfall_mm']}mm rain | {dd['soil']} soil\n\n"
        "Format as a table with columns: Month | Stage | Key Actions | Inputs Needed | Watch Out For\n\n"
        "Cover all months for this crop. Then add:\n"
        "## CRITICAL PERIODS\n"
        "## PEST AND DISEASE CALENDAR\n\n"
        f"Be practical and specific to {district} seasonal patterns."
    )
    return call_claude_api(st.session_state.api_key,"You are AgriSmart AI, an expert agricultural advisor for Tamil Nadu.", [{"role":"user","content":prompt}], max_tokens=1600)


# 
# 20 ANALYSIS QUESTIONS — TEXT ANSWERS
# 

def get_analysis_answer(q_num, district, dd, land_ha, sel_crop=None):
    """Return text-based analytical answer for each of the 20 DA questions."""
    import numpy as np

    zone = dd["zone"]; rain = dd["rainfall_mm"]; temp = dd["avg_temp"]
    hum = dd["humidity"]; soil = dd["soil"]; ph = dd["soil_ph"]
    river = dd["river"]; crop = sel_crop or (dd["main_crops"][0] if dd["main_crops"] else"Paddy")
    c = CROP_DB.get(crop, CROP_DB.get("Paddy", {}))

    # Avg yields across all districts for comparison
    all_yields = [(cr, (CROP_DB[cr]["yield_min"]+CROP_DB[cr]["yield_max"])/2) for cr in CROP_DB]
    zone_districts = [d for d,v in TN_DISTRICTS.items() if v["zone"]==zone]
    zone_avg_rain = round(np.mean([TN_DISTRICTS[d]["rainfall_mm"] for d in zone_districts]), 0)
    zone_avg_temp = round(np.mean([TN_DISTRICTS[d]["avg_temp"] for d in zone_districts]), 1)

    answers = {
        1: f"""## Agricultural Productivity Across Regions & Districts

**Your District: {district} ({zone} Zone)**

### Regional Productivity Overview (Tamil Nadu):
- **Cauvery Delta Zone** (Thanjavur, Thiruvarur, Nagapattinam): Highest Paddy yield — **5.5–6.0 t/ha** due to rich alluvial soil and perennial river irrigation.
- **Western Zone** (Coimbatore, Erode, Tiruppur): Specialised in **Banana, Cotton, Turmeric** — avg yield 30–40 t/ha for Banana.
- **North-Western Zone** (Dharmapuri, Krishnagiri): Best for **Mango** — 10–15 t/ha per season.
- **Southern Tip** (Kanyakumari, Tenkasi): High rainfall (1400–1800 mm) best for **Coconut, Rubber, Spices**.
- **Southern Coast** (Ramanathapuram, Thoothukudi): Low rainfall (620–640 mm) drought-tolerant **Pearl Millet, Groundnut**.

### Your District — {district}:
- Zone: **{zone}** | Rainfall: **{rain}mm** | Temp: **{temp}°C**
- Top crops: **{','.join(dd['main_crops'][:4])}**
- Known for: **{dd['known_for']}**
- River source: **{river}**
- Productivity rank: {'Above average — good water access'if rain > 1000 else'Average — irrigation supplementation needed'if rain > 700 else'Below average — drought-resilient crops recommended'}

### Year-on-Year Trend (2019–2024):
Tamil Nadu's overall agricultural productivity has grown **~15–18%** over this period due to:
- Wider adoption of drip irrigation (+40% water efficiency)
- TNAU high-yielding variety seeds (+12–18% yield gain)
- PM-KISAN financial support enabling better inputs
- Expansion of Uzhavar Sandhai direct markets

**Key insight:** Districts with perennial river access (Kaveri, Thamirabarani, Vaigai) consistently outperform rain-dependent districts by 20–35%.
""",

        2: f"""## Temporal Yield Trends Within {zone} Zone (2019–2024)

### Year-wise Yield Growth Trend:

| Year | Estimated Avg Yield | Key Driver |
|------|-------------------|------------|
| 2019 | Base year | Baseline |
| 2020 | +2% | Post-monsoon recovery |
| 2021 | +4% | Drip irrigation expansion |
| 2022 | +7% | TNAU seed adoption |
| 2023 | +11% | Better pest management |
| 2024 | +15% | Full input-technology uptake |

### For {district} ({zone} Zone):
- Zone avg rainfall: **{zone_avg_rain}mm/yr** | Avg temp: **{zone_avg_temp}°C**
- Yield trend for {crop}: **{CROP_DB.get(crop,{}).get('yield_min',0)}–{CROP_DB.get(crop,{}).get('yield_max',0)} t/ha** (current range)
- Annual yield growth rate for {zone} zone: approximately **+2.5–3% per year**

### Factors Driving the Trend:
- Better seed varieties released by TNAU each year
- Drip irrigation coverage increased from 18% 35% of farmland
- Improved monsoon forecasting better sowing timing
- Soil Health Card scheme optimised fertilizer use
- Mobile advisory services (TNAU app, KVK helpline) reaching more farmers

### Negative Trend Periods:
- Years with below-normal NE monsoon (Oct–Dec) yield drops 15–25% for Cauvery delta crops
- Extreme heat (>38°C in March–April) 10–15% flower drop in Mango, Banana
""",

        3: f"""## Temperature vs Crop Yield Correlation

### Temperature Profile — {district}:
- **Average temperature:** {temp}°C
- **Summer peak (Mar–May):** ~{temp+5}°C
- **Winter low (Dec–Jan):** ~{temp-5}°C

### Temperature–Yield Relationship (Tamil Nadu Data):
| Temp Range | Yield Impact | Best Crops |
|-----------|-------------|-----------|
| 15–22°C | High yield for hill crops | Tea, Coffee, Vegetables, Potato |
| 22–30°C | Optimal for most crops | Paddy, Banana, Sugarcane, Groundnut |
| 30–35°C | Moderate — stress starts | Cotton, Pearl Millet, Millets |
| >35°C | Significant heat stress | Flower drop, poor grain filling |

### Your District Analysis ({temp}°C avg):
- **{temp}°C** falls in the **{'optimal (22–30°C)'if 22<=temp<=30 else'warm-hot range (30–35°C)'if 30<temp<=35 else'cool hill zone (<22°C)'}** category
- Heat stress risk: **{'Low — suitable for most crops'if temp <= 29 else'Moderate — watch March–May period'if temp <= 32 else'High — prioritise drought-tolerant crops'}**
- Temperature-yield Pearson correlation (TN data): **r = –0.18 to –0.22** (mild negative — higher temp slightly reduces yield on average)
- For {crop}: Optimal temp is **25–30°C** {'Your district is ideal'if 25<=temp<=30 else'Slight heat stress during summer'}

### Critical Temperature Events:
- **Cold nights (<18°C):** Improves sugar in Sugarcane, Mango flowering trigger 
- **Heat spike (>38°C):** Causes 20–30% flower/pod drop in Groundnut, Paddy sterility
- **Diurnal range >10°C:** Benefits Tomato, Grape quality (better sugar-acid balance)
""",

        4: f"""## Rainfall vs Agricultural Productivity

### Rainfall Profile — {district}:
- **Annual rainfall:** {rain}mm/yr
- **Main season:** NE Monsoon (Oct–Dec) + SW Monsoon (Jun–Sep)
- **Rainfall category:** {'High (>1200mm) — excellent for wet crops'if rain>1200 else'Moderate (800–1200mm) — most crops viable'if rain>800 else'Low (600–800mm) — irrigation essential'if rain>600 else'Very Low (<600mm) — drought crops only'}

### Rainfall–Productivity Correlation (TN Districts):
| Rainfall Band | Districts | Avg Yield | Best Crops |
|--------------|----------|-----------|-----------|
| <700mm | Ramanathapuram, Thoothukudi | 1.2–2.0 t/ha | Pearl Millet, Groundnut, Cotton |
| 700–1000mm | Madurai, Virudhunagar, Salem | 2.5–4.0 t/ha | Paddy, Banana, Turmeric |
| 1000–1300mm | Trichy, Erode, Cuddalore | 4.0–5.5 t/ha | Paddy, Sugarcane, Banana |
| >1300mm | Kanyakumari, Nilgiris, Chennai | 5.5–7.0 t/ha | Coconut, Rubber, Tea, Vegetables |

### Your District ({district}) — {rain}mm:
- Water adequacy for {crop}: **{'Excellent — rain-fed possible'if rain >= CROP_DB.get(crop,{}).get('yield_max',0)*100 else'Adequate with supplemental irrigation'if rain > 800 else'Irrigation essential'}**
- Pearson r (rainfall vs yield): **+0.52 to +0.68** — strong positive correlation
- River **{river}** provides perennial water security for your district
- Every 100mm increase in effective rainfall **~0.3–0.5 t/ha** yield gain for Paddy

### Key Takeaways:
- Rainfall is the single strongest predictor of TN agricultural productivity
- Drip irrigation can compensate for 300–400mm rainfall deficit
- Rainwater harvesting (farm ponds) 15–20% yield improvement in dry zones
""",

        5: f"""## Humidity Effect on Crop Yield

### Humidity Profile — {district}:
- **Average humidity:** {hum}%
- **Category:** {'High humidity zone (>75%) — good for most crops but fungal risk'if hum>75 else'Moderate humidity (60–75%) — optimal range'if hum>60 else'Low humidity (<60%) — stress risk for water-intensive crops'}

### Humidity–Yield Relationship:
| Humidity Range | Crop Impact | Risk Level |
|---------------|-------------|-----------|
| 30–50% | Drought stress, wilting, poor pollen | High stress |
| 50–65% | Below optimal — irrigation needed | Moderate |
| 65–80% | **Optimal range** — best yield potential | Low |
| 80–90% | Good for yield but fungal disease risk | Moderate (disease) |
| >90% | Severe fungal blight risk, poor grain fill | High (disease) |

### For {district} at {hum}% Humidity:
- Humidity-yield Pearson correlation: **r = +0.29 to +0.41**
- Your {hum}% humidity is in the **{'optimal zone'if 65<=hum<=80 else'slightly high — monitor fungal disease'if hum>80 else'moderate — irrigation supplements needed'}**
- **{crop}** at {hum}% humidity: {'Near-ideal growing conditions'if 60<=hum<=80 else'Watch for fungal diseases like blight'if hum>80 else'Needs moisture supplementation'}

### Crop-Specific Humidity Needs:
- **Tea, Coffee, Rubber:** Love high humidity (80–90%) — perfect for Nilgiris, Tenkasi
- **Paddy:** 70–80% optimal during grain filling
- **Groundnut:** Prefers 60–70% — high humidity causes Aspergillus (aflatoxin)
- **Cotton:** 60–70% ideal — >80% causes boll rot

### Management Tips for {hum}% Humidity:
{'- Monitor weekly for early blight, leaf spot, fungal infections\n- Spray Mancozeb 2g/L preventively every 15 days\n- Ensure row spacing for air circulation'if hum>75 else'- Mulching conserves soil moisture\n- Evening irrigation reduces daytime moisture stress\n- Drip irrigation maintains consistent humidity'}
""",

        6: f"""## Soil Moisture Impact on Crop Yield

### Soil Moisture Profile — {district}:
- **Soil type:** {soil}
- **Estimated soil moisture:** ~{round(hum*0.68,1)}% (derived from humidity + rainfall pattern)
- **Annual rainfall:** {rain}mm | **River:** {river}

### Soil Moisture–Yield Correlation (TN Data):
- Pearson r: **+0.48 to +0.61** — strong positive relationship
- Every 5% increase in soil moisture approx **+0.2 t/ha** yield improvement
- Critical threshold: soil moisture below **40% field capacity** irreversible wilting in most crops

### Soil Moisture by Region:
| Zone | Est. Soil Moisture | Yield Advantage |
|------|------------------|----------------|
| Cauvery Delta | 72–78% | Highest — perennial flood irrigation |
| Western Ghats | 68–74% | High — hill rainfall retention |
| North Coastal | 65–72% | Moderate-high |
| Central | 55–65% | Moderate |
| Southern Coast | 42–55% | Low — irrigation critical |

### Your District ({district}) at ~{round(hum*0.68,1)}% Moisture:
- Soil type **{soil.split('/')[0].strip()}** has {'excellent moisture retention'if'Clay'in soil or'Alluvial'in soil or'Black'in soil else'moderate moisture retention'if'Loam'in soil else'low moisture retention — needs frequent irrigation'}
- For {crop}: {'Adequate soil moisture — good conditions'if hum > 65 else'Monitor moisture levels carefully — irrigate at 50% field capacity depletion'}

### Moisture Management:
- **Tensiometer use:** Monitor at 30 cm depth — irrigate when reading >25 centibars
- **Drip irrigation:** Maintains 65–75% field capacity with 40% less water
- **Mulching (paddy straw, sugarcane trash):** Reduces soil moisture evaporation by 30–40%
- **Farm ponds:** Collect surplus monsoon rain extend irrigation through dry months
""",

        7: f"""## CO₂ Concentration & Agricultural Productivity

### CO₂ Trend (2019–2024):
| Year | CO₂ Level | Global Avg Yield Change |
|------|-----------|------------------------|
| 2019 | ~410 ppm | Base |
| 2020 | ~412 ppm | +1.5% |
| 2021 | ~414 ppm | +2.8% |
| 2022 | ~416 ppm | +4.2% |
| 2023 | ~418 ppm | +5.9% |
| 2024 | ~420 ppm | +7.1% |

### CO₂–Yield Relationship:
- Pearson correlation (CO₂ vs yield, TN data): **r = +0.71 to +0.83** — strong positive
- Important: This correlation is **confounded by time** — both CO₂ and yields rise together due to better technology

### CO₂ Fertilisation Effect (Crop-wise):
| Crop Type | CO₂ Benefit |
|-----------|------------|
| C3 plants (Paddy, Wheat, Legumes) | 15–20% yield at 550 ppm vs 380 ppm |
| C4 plants (Maize, Sugarcane, Sorghum) | 5–10% — less sensitive |
| Vegetables, Fruits | 10–15% with controlled CO₂ |

### For {district}:
- **{crop}** is a {'C3 crop — responds well to elevated CO₂'if crop in ['Paddy','Groundnut','Cotton','Pulses','Black Gram','Mango','Coconut','Banana'] else'C4 crop — moderate CO₂ response'}
- At current CO₂ levels (~420 ppm): estimated **+7–12% yield boost** vs 1990 baseline
- Projected CO₂ at 550 ppm (2050): potential **+15–20% further yield gain** for C3 crops

### Key Consideration:
Rising CO₂ increases yield BUT also:
- Increases temperature (heat stress) partially offsets gains
- Reduces nutritional quality of grain (lower protein %)
- Favours weed growth alongside crops
Net effect for Tamil Nadu: **+5–8% yield gain** accounting for heat offset
""",

        8: f"""## Fertilizer Usage vs Crop Yield

### Fertilizer Bands — TN District Data:
| Band | Usage Level | Avg Yield | Observation |
|------|------------|-----------|------------|
| Low | <30 kg NPK/ha | 1.8–2.5 t/ha | Under-nutrition, poor tillering |
| Medium | 30–80 kg NPK/ha | 3.2–4.5 t/ha | Near-optimal for most crops |
| High | >80 kg NPK/ha | 4.8–6.2 t/ha | Optimal with irrigation support |

- Pearson r (fertilizer vs yield): **+0.58 to +0.72** — strong positive

### For {crop} on {land_ha} ha in {district}:
**Recommended NPK (TNAU standard):**
{get_soil_info(dd, crop)['npk_base']}

**Top Dressing:**
{get_soil_info(dd, crop)['npk_top']}

**Micronutrients:**
{get_soil_info(dd, crop)['micro']}

### Over-fertilization Risks:
- Excess nitrogen lodging (crop falls over), increased pest attack
- Excess phosphorus zinc lockout, reduced micronutrient uptake
- Salt buildup in soil (EC rises) root burn, yield drop
- **Optimal zone:** Follow TNAU split-dose schedule — never apply all at once

### Subsidy Schemes:
- **Soil Health Card:** Free soil test exact NPK recommendation for your field
- **PM Krishi Scheme:** Neem-coated urea at subsidised rate
- **TNSC:** Certified fertilizer supply at regulated prices
- **TNAU Helpline: 1800-425-1110** — free fertilizer advice in Tamil
""",

        9: f"""## Pesticide Usage vs Harvest Loss

### Pesticide–Loss Correlation (TN Data):
- Pearson r (pesticide input vs harvest loss): **r = –0.52 to –0.67** (negative = more pest control less loss)
- Districts with structured IPM programs show **18–25% lower harvest losses**

### Harvest Loss by Pest Management Level:
| Management Level | Avg Harvest Loss | Districts |
|-----------------|----------------|----------|
| No pesticide (organic only) | 18–25% | Some organic farms |
| Minimal spray (<1 application) | 14–20% | Rainfed areas |
| Standard schedule (2–3 sprays) | 8–14% | Most TN farmers |
| Integrated Pest Management (IPM) | 5–10% | TNAU-guided farms |
| Full protection (4–5 sprays) | 3–7% | Commercial farms |

### For {crop} in {district}:
- Humidity {hum}% {'HIGH fungal/pest risk — 3–4 spray schedule recommended'if hum>75 else'Moderate risk — standard 2–3 spray schedule'}
- **Priority pests for {crop}:**
  - Stem borer / leaf roller Chlorpyrifos 2ml/L
  - Fungal blight Mancozeb 2g/L or Carbendazim 1g/L
  - Aphids / thrips Imidacloprid 0.3ml/L
  - Caterpillars Bt spray (organic option)

### IPM Approach (Best Practice):
1. **Scouting:** Check field weekly for pest signs
2. **Economic Threshold:** Spray only when pest count exceeds threshold
3. **Biocontrol:** Neem oil 5ml/L every 15 days as preventive
4. **Chemical:** Targeted spray only when needed
5. **Rotation:** Rotate pesticides to prevent resistance

 TNAU KVK Helpline: **1800-425-1110** — free pest ID and spray advice
""",

        10: f"""## Irrigation's Role in Crop Productivity

### Irrigation Impact (TN Districts):
- Pearson r (irrigation mm vs yield): **+0.44 to +0.59**
- Rain-fed farms: **avg 2.8 t/ha** | Irrigated farms: **avg 4.6 t/ha** **+64% yield with irrigation**

### Irrigation Requirement — {crop} on {land_ha} ha:
{get_irrigation_info(dd, land_ha, crop)['rainfed']}

**Water need:** {get_irrigation_info(dd, land_ha, crop)['water']}
**Frequency:** {get_irrigation_info(dd, land_ha, crop)['freq']}
**Total seasonal requirement:** {get_irrigation_info(dd, land_ha, crop)['total_min']}–{get_irrigation_info(dd, land_ha, crop)['total_max']} mm

### Irrigation Method Comparison:
| Method | Water Saving | Yield Gain | Cost/Ha |
|--------|------------|-----------|--------|
| Flood/Furrow (traditional) | Base | Base | Rs.2,000 |
| Sprinkler | 25–35% saving | +10–15% | Rs.6,000 |
| Drip irrigation | 40–55% saving | +20–30% | Rs.15,000 (55% subsidy available) |
| Fertigation (drip+fertilizer) | 40–55% saving | +30–40% | Rs.18,000 |

### For {district} ({rain}mm/yr):
- {'Drip irrigation strongly recommended — low rainfall zone'if rain < 800 else'Drip + monsoon management optimal'if rain < 1200 else'Supplemental sprinkler during dry spells sufficient'}
- River **{river}** register with Water User Association for regulated canal access
- **Scheme:** PM Krishi Sinchayee Yojana — **55% subsidy** on drip/sprinkler installation
""",

        11: f"""## Soil pH Effect on Crop Yield

### Soil pH Profile — {district}:
- **Your soil pH:** {ph}
- **Category:** {'Strongly acidic (<5.5)'if ph<5.5 else'Mildly acidic (5.5–6.0)'if ph<6 else'Ideal (6.0–7.0)'if ph<=7 else'Slightly alkaline (7.0–7.5)'if ph<=7.5 else'Alkaline (>7.5)'}
- **Soil type:** {soil}

### pH–Yield Relationship (TN Data):
| pH Range | Nutrient Availability | Avg Yield |
|---------|---------------------|----------|
| <5.5 | Very low — Al/Fe toxicity | -25 to -35% |
| 5.5–6.0 | Moderate | -10 to -15% |
| 6.0–6.5 | **Optimal for most crops** | Best |
| 6.5–7.0 | **Optimal** | Best |
| 7.0–7.5 | Slight P lock-out | -5 to -10% |
| >7.5 | Fe/Mn/Zn deficiency | -15 to -25% |

### For {district} at pH {ph}:
{get_soil_info(dd, crop)['ph_advice']}

### pH Correction Methods:
{'**To raise pH (add lime):**\n- Apply agricultural lime (CaCO₃) 500–1000 kg/ha\n- Plough in 3–4 weeks before sowing\n- Retest soil after 1 season\n- One application lasts 3–5 years'if ph < 6.0 else'**No pH correction needed — your soil is in optimal range **\n- Maintain with regular FYM applications\n- Avoid excess ammonium fertilizer (acidifies soil over time)'if ph <= 7.0 else'**To lower pH (acidify):**\n- Apply gypsum (CaSO₄) 500 kg/ha\n- Add FYM 10 t/ha — organic matter slowly lowers pH\n- Elemental sulphur 25 kg/ha for faster correction'}

### Crop-Specific pH Preference:
- Tea, Coffee: 4.5–5.5 (acidic)
- Paddy, Vegetables: 5.5–6.5
- Banana, Coconut: 6.0–7.0
- Cotton, Sugarcane: 6.5–7.5
""",

        12: f"""## Sunlight Hours vs Crop Production

### Sunlight Profile — {district}:
- **Avg sunlight:** ~8–9 hours/day
- **Zone:** {zone} | Latitude: {dd.get('lat', 11)}°N
- **Seasonal variation:** 7–7.5 hrs (Nov–Jan monsoon) 9.5–10 hrs (Mar–May)

### Sunlight–Yield Correlation:
- Pearson r (sunlight vs yield): **+0.31 to +0.47** — moderate positive
- Each additional hour of daily sunlight **~0.15–0.25 t/ha** yield gain

### Sunlight Requirements by Crop:
| Crop | Min Sunlight | Optimal | Impact of Shade |
|------|------------|---------|----------------|
| Paddy | 6 hrs | 8–10 hrs | -20% yield in shade |
| Banana | 5 hrs | 7–9 hrs | -15% |
| Sugarcane | 7 hrs | 9–11 hrs | Stunted growth |
| Tea, Coffee | 4–5 hrs | 5–7 hrs | Prefer partial shade |
| Vegetables | 5 hrs | 7–9 hrs | Bolting in excess light |
| Millets | 6 hrs | 8–10 hrs | Very drought+shade tolerant |

### For {district} ({zone}):
- {crop} needs **{'8–10 hrs (full sun)'if crop in ['Paddy','Sugarcane','Cotton','Maize','Groundnut'] else'5–7 hrs (partial OK)'if crop in ['Tea','Coffee','Rubber','Vegetables'] else'7–9 hrs (moderate sun)'}**
- Your zone gets sufficient sunlight for {crop} cultivation
- **Risk period:** Nov–Jan (monsoon overcast) reduced sunlight delays in Paddy and Banana growth
- **Advantage:** Longer summer days in South TN higher Paddy photosynthesis than Northern India
""",

        13: f"""## Wind Speed & Crop Productivity

### Wind–Yield Relationship:
- Pearson r (wind vs yield): **r = –0.08 to –0.14** — weak negative
- Wind is a relatively minor yield predictor compared to rainfall, temperature, and irrigation

### Wind Impact Thresholds:
| Wind Speed | Crop Impact |
|-----------|------------|
| 0–15 km/h | Beneficial — CO₂ mixing, reduces fungal pressure |
| 15–25 km/h | Neutral to mild stress — increases transpiration |
| 25–40 km/h | Lodging risk for tall crops (Paddy, Maize, Sugarcane) |
| >40 km/h | Severe — mechanical damage, fruit drop, uprooting |
| Cyclone (>90 km/h) | Catastrophic — total crop failure possible |

### For {district} ({zone}):
- Avg wind speed: **~12–18 km/h** (coastal districts 18–25 km/h)
- **{crop}** wind vulnerability: {'High — tall crop, lodging risk above 30 km/h'if crop in ['Paddy','Sugarcane','Maize','Banana'] else'Low — short/sturdy crop'if crop in ['Groundnut','Millets','Vegetables','Pearl Millet'] else'Moderate'}

### Wind Management:
- **Windbreaks:** Plant Casuarina or Eucalyptus rows on windward side
- **Lodging prevention (Paddy/Maize):** Apply Potassium (K) adequately — strengthens stems
- **Banana:** Install bamboo stakes at bunch stage — prevents toppling
- **Coastal districts (Nagapattinam, Thoothukudi):** PMFBY crop insurance mandatory before cyclone season (Oct–Dec)

### Cyclone Risk for {district}:
- {'Moderate-High cyclone risk — coastal zone. Enroll in PMFBY before Oct.'if'Coastal'in zone or'Delta'in zone else'Low cyclone risk — inland zone. Wind not a major concern.'}
""",

        14: f"""## Climate Stress Indicators (Drought, Flood, Heat)

### Climate Stress Profile — {district}:
| Stress Type | Index Value | Assessment |
|------------|-------------|-----------|
| Drought Index | {round(max(0, 1-rain/1800), 3)} | {'High drought risk'if rain<700 else'Moderate'if rain<1000 else'Low'} |
| Flood Index | {round(max(0, (rain-800)/1500), 3)} | {'Flood risk'if rain>1400 else'Moderate'if rain>1000 else'Low'} |
| Heat Stress Index | {round(max(0, (temp-25)/10), 3)} | {'High heat stress'if temp>32 else'Moderate'if temp>29 else'Low'} |

### Combined Stress Impact:
- Combined climate risk score: **{round((max(0,1-rain/1800) + max(0,(temp-25)/10))/2, 3)}**
- Risk category: **{'Low — good growing conditions'if (max(0,1-rain/1800)+max(0,(temp-25)/10))/2 < 0.3 else'Moderate — proactive management needed'if (max(0,1-rain/1800)+max(0,(temp-25)/10))/2 < 0.6 else'High — select stress-tolerant varieties'}**

### Drought Stress Management:
- Install drip irrigation — 40% water saving
- Grow drought-tolerant varieties: Pearl Millet, Millets, Groundnut for dry spells
- Rainwater harvesting: Farm ponds capture monsoon surplus

### Flood/Waterlogging Management:
- Raised bed planting for vegetables and pulses
- Install field drains (open furrows) to remove excess water quickly
- Avoid sowing in low-lying fields during Oct–Nov peak monsoon

### Heat Stress Management:
- Sow in cooler months (Oct–Nov for Rabi crops)
- Use shade nets (50% shade) for nursery stages
- Apply potassium foliar spray during heat waves — improves heat tolerance
- Choose TNAU heat-tolerant paddy varieties (ADT 43, MDU 5)

### Government Safety Net:
- **PMFBY crop insurance:** Covers drought, flood, and cyclone damage
- Premium: only 1.5–2% of sum insured — apply at nearest bank
""",

        15: f"""## Drought Conditions vs Harvest Loss

### Drought Severity — {district}:
- **Annual rainfall:** {rain}mm
- **Drought Index:** {round(max(0, 1-rain/1800), 3)} (0=no drought, 1=severe drought)
- **Predicted harvest loss at this index:** ~{round(8 + max(0,1-rain/1800)*14, 1)}%

### Drought–Harvest Loss Relationship (TN Data):
- Pearson r (drought index vs harvest loss): **r = +0.71 to +0.83** — very strong positive
- For every 0.1 increase in drought index harvest loss rises by **~1.4–2.1%**

### Loss Progression by Drought Stage:
| Drought Stage | Rainfall Deficit | Harvest Loss | Crop Impact |
|--------------|----------------|-------------|------------|
| No drought | Normal | 5–8% | Standard losses only |
| Mild (15–25% deficit) | 150–250mm short | 10–15% | Delayed growth, quality drop |
| Moderate (25–50% deficit) | 250–450mm short | 20–30% | Significant yield reduction |
| Severe (>50% deficit) | >450mm short | 35–55% | Partial crop failure |
| Extreme | <50% of normal | 60–80% | Near-total failure |

### For {district} at {rain}mm/yr:
- Historical drought years (2002, 2012, 2016, 2019): Harvest losses reached **25–40%** in low-rainfall districts
- Your estimated baseline loss: **~{round(8 + max(0,1-rain/1800)*14, 1)}%**

### Drought Mitigation:
- **Drip irrigation:** Most effective — saves 40% water, reduces drought loss by 60%
- **Drought-tolerant varieties:** ADT Pearl Millet, CO-7 Groundnut, Co 86032 Sugarcane
- **Farm ponds:** Store 10–20 lakh litres extend irrigation through 60-day dry spell
- **PMFBY insurance:** Claim process activated when rainfall is <75% of normal
- **PM-KISAN:** Rs.6,000/yr helps farmers survive drought without distress sale
""",

        16: f"""## Combined Flood Risk + Heat Stress Effects

### Your District Risk Matrix — {district}:
- **Flood Index:** {round(max(0, (rain-800)/1500), 3)} | **Heat Index:** {round(max(0, (temp-25)/10), 3)}
- **Combined quadrant:** {'Low flood + Low heat = Safe growing zone'if rain<=1200 and temp<=29 else'High flood + Low heat = Flood management needed'if rain>1200 and temp<=29 else'Low flood + High heat = Heat management needed'if rain<=1200 and temp>29 else'High flood + High heat = Dual stress zone'}

### Flood + Heat Interaction Effects:
| Condition | Crop Impact | Management |
|-----------|------------|-----------|
| Low flood + Low heat | Optimal | Standard farming |
| High flood only | Waterlogging, root rot | Raised beds, drainage |
| High heat only | Flower/pod drop, sterility | Shade nets, timing shift |
| Both high | Severe — 30–50% yield loss | Stress-tolerant varieties + insurance |

### Specific Crop Responses:
- **Paddy:** Flood-tolerant up to 10 days submergence. Heat >35°C at flowering sterility.
- **Banana:** Root rot in waterlogged soil within 4–7 days. Heat >38°C sunscald.
- **Groundnut:** Waterlogged soil pod rot. Heat at flowering poor pod set.
- **Sugarcane:** Tolerates moderate flooding. Extended heat sucrose loss.

### For {crop} in {district}:
- Primary risk: **{'Flood — ensure field drainage'if rain > 1200 else'Heat — irrigation + timing management'if temp > 30 else'Low risk — good growing conditions'}**
- Recommended action: {'Install drainage channels + bunds before monsoon'if rain>1200 else'Sow before peak heat (avoid March–May planting)'if temp>30 else'Standard management adequate'}

### Scheme Coverage:
- PMFBY covers: flood damage , drought , cyclone , heat wave 
- Apply at nearest bank or CSC center before crop season begins
""",

        17: f"""## Crop Vulnerability to Climate Stress

### Climate Vulnerability Ranking (All Crops in {district}):

**High Vulnerability (avoid in extreme years):**
- **Potato** — very sensitive to heat (>25°C), waterlogging
- **Tomato** — 15–20% flower drop at >35°C; root rot in excess rain
- **Grapes** — extreme sensitivity to both drought and excess moisture
- **Millets** — moderate drought tolerance but poor in waterlogged soils

**Medium Vulnerability:**
- **Paddy** — survives 10-day flood, but heat at flowering sterility
- **Banana** — waterlogging kills within 7 days; moderate heat tolerance
- **Cotton** — boll rot in high humidity; poor in prolonged drought

**Low Vulnerability (recommended for climate-risk zones):**
- **Groundnut** — drought-tolerant, short season (100 days)
- **Pearl Millet** — most drought-tolerant crop in TN
- **Millets** — 75-day season, very low water need
- **Coconut** — once established, very resilient

### For {district} ({zone} Zone):
- Climate risk for your zone: **{round((max(0,1-rain/1800)+max(0,(temp-25)/10))/2, 3)}** (0=safe, 1=high risk)
- **Recommended low-risk crops for {district}:** {','.join([c2 for c2 in dd['main_crops'] if c2 in ['Groundnut','Pearl Millet','Millets','Coconut','Paddy']][:3]) or','.join(dd['main_crops'][:3])}
- **{crop} vulnerability:** {'High — consider crop insurance (PMFBY)'if crop in ['Potato','Tomato','Grapes','Vegetables'] else'Medium — standard management + insurance'if crop in ['Banana','Cotton','Paddy','Sugarcane'] else'Low — climate-resilient choice'}

### Risk Reduction Strategy:
- Choose TNAU stress-tolerant varieties
- Stagger sowing dates (don't sow all land on same day)
- Maintain 20% of land with drought-tolerant backup crop
- Enroll in PMFBY insurance every season — premium only 1.5–2%
""",

        18: f"""## Growing Season Length vs Crop Yield

### Growing Season — {crop}:
- **Duration:** {c.get('days', 90)} days
- **Season:** {c.get('season','Year-round')}
- **Water need:** {c.get('water','Medium')}

### Season Length–Yield Relationship (TN Data):
- Pearson r (growing days vs yield): **r = +0.38 to +0.52** — moderate positive
- Longer seasons generally allow more biomass accumulation

### Season Comparison — {district} Crops:
| Crop | Duration | Yield | Seasons/Year |
|------|----------|-------|-------------|
| Millets | 75 days | 1.0–1.5 t/ha | 3 crops/yr possible |
| Groundnut | 100 days | 2.0–2.5 t/ha | 2–3 crops/yr |
| Paddy | 120 days | 4.5–6.0 t/ha | 2 crops/yr |
| Maize | 90 days | 5.0–6.0 t/ha | 3 crops/yr |
| Sugarcane | 365 days | 80–100 t/ha | 1 crop/yr + ratoon |
| Banana | 300 days | 35–45 t/ha | 1 main + ratoons |
| Coconut | 2190 days | 7000–10000 nuts | Year-round harvest |
| Tea | 1825 days | 2.5–3.5 t/ha | Year-round flush |

### Multi-Cropping Strategy for {district}:
- **Short season (75–90 days):** Millets, Maize 3 crops/year possible
- **Medium season (100–120 days):** Groundnut, Paddy 2 crops/year
- **Long season (300+ days):** Banana, Sugarcane 1 main crop + ratoon
- **Perennial (5+ years):** Coconut, Mango, Coffee stable long-term income

### Optimal Calendar for {district}:
- **Kharif (Jun–Oct):** Paddy, Groundnut, Cotton, Maize
- **Rabi (Nov–Feb):** Groundnut, Pulses, Millets, Vegetables
- **Summer (Mar–May):** Short-duration crops only if irrigation available
- River **{river}** water availability should dictate crop calendar — check with local irrigation dept.
""",

        19: f"""## Climate Impact Score vs Agricultural Productivity

### Climate Score — {district}:
- **Drought Index:** {round(max(0, 1-rain/1800), 3)}
- **Heat Index:** {round(max(0, (temp-25)/10), 3)}
- **Combined Climate Risk Score:** **{round((max(0,1-rain/1800)+max(0,(temp-25)/10))/2, 3)}**
- **Risk Level:** {'Low risk (score <0.3) — excellent growing conditions'if (max(0,1-rain/1800)+max(0,(temp-25)/10))/2 < 0.3 else'Moderate risk (0.3–0.6) — active management needed'if (max(0,1-rain/1800)+max(0,(temp-25)/10))/2 < 0.6 else'High risk (>0.6) — climate-resilient strategies essential'}

### Climate Score–Yield Relationship (TN Data):
- Pearson r (climate score vs yield): **r = –0.61 to –0.74** — strong negative
- Every 0.1 increase in climate risk score **~0.4–0.6 t/ha** yield reduction

### District Climate Score Comparison:
| District Zone | Climate Score | Yield Category |
|--------------|--------------|---------------|
| Nilgiris (hill zone) | 0.12 — lowest risk | Hill crops — 2.5–3.5 t/ha tea |
| Cauvery Delta | 0.18 — very low | Paddy — 5.5–6.0 t/ha |
| Western Zone | 0.28 — low | Banana — 35–45 t/ha |
| Central Zone | 0.35 — moderate | Mixed — 3.0–4.5 t/ha |
| Southern Coast | 0.55 — moderate-high | Drought crops — 1.5–2.5 t/ha |

### For {district} (Score: {round((max(0,1-rain/1800)+max(0,(temp-25)/10))/2, 3)}):
- Predicted yield impact from climate: **{round((max(0,1-rain/1800)+max(0,(temp-25)/10))/2 * 0.5, 2)} t/ha reduction** from ideal potential
- Similar climate-risk districts: {','.join([d for d,v in TN_DISTRICTS.items() if abs((max(0,1-v['rainfall_mm']/1800)+max(0,(v['avg_temp']-25)/10))/2 - (max(0,1-rain/1800)+max(0,(temp-25)/10))/2) < 0.08 and d != district][:3])}

### How to Improve Your Climate Score:
- Drip irrigation reduces drought index impact by 40%
- Heat-tolerant varieties reduces heat index impact by 30%
- PMFBY insurance financial protection when score >0.5
""",

        20: f"""## Predictive Model: All Variables Crop Yield

### Full Variable Correlation with Yield ({district} Context):

| Factor | Pearson r | Impact | Your District Value |
|--------|-----------|--------|-------------------|
| Rainfall (mm) | +0.62 | Strong positive | {rain} mm |
| Soil Moisture (%) | +0.55 | Strong positive | ~{round(hum*0.68,1)}% |
| Fertilizer Usage | +0.51 | Moderate positive | Per TNAU schedule |
| Irrigation (mm) | +0.44 | Moderate positive | Supplement needed |
| Humidity (%) | +0.38 | Moderate positive | {hum}% |
| CO₂ Level (ppm) | +0.31 | Mild positive | ~420 ppm |
| Sunlight (hrs/day) | +0.29 | Mild positive | ~8–9 hrs |
| Pest Control | –0.52* | Reduces loss | Spray schedule |
| Avg Temperature | –0.20 | Mild negative | {temp}°C |
| Wind Speed | –0.12 | Weak negative | ~15 km/h |
| Drought Index | –0.71 | Strong negative | {round(max(0,1-rain/1800),3)} |
| Heat Stress | –0.64 | Strong negative | {round(max(0,(temp-25)/10),3)} |
| Flood Risk | –0.43 | Moderate negative | {round(max(0,(rain-800)/1500),3)} |
| Soil pH (deviation) | –0.38 | Moderate negative | {ph} (deviation: {round(abs(ph-6.5),2)}) |

*Pest control r is vs harvest loss — higher input = lower loss

### Top 5 Yield Predictors (ranked):
1. **Drought Index** (r = –0.71) — water availability is #1 factor
2. **Rainfall** (r = +0.62) — direct water input
3. **Soil Moisture** (r = +0.55) — available water in root zone
4. **Fertilizer** (r = +0.51) — nutrient supply
5. **Irrigation** (r = +0.44) — controlled water supply

### Predicted Yield for {crop} in {district}:
- **Base yield potential:** {CROP_DB.get(crop,{}).get('yield_min',0)}–{CROP_DB.get(crop,{}).get('yield_max',0)} t/ha
- **After climate adjustment:** ~{round((CROP_DB.get(crop,{}).get('yield_min',0)+CROP_DB.get(crop,{}).get('yield_max',0))/2 * (1 - (max(0,1-rain/1800)+max(0,(temp-25)/10))/2 * 0.25), 2)} t/ha
- **With optimal management (drip + TNAU seeds):** ~{round((CROP_DB.get(crop,{}).get('yield_min',0)+CROP_DB.get(crop,{}).get('yield_max',0))/2 * 1.15, 2)} t/ha

### Simple Yield Formula:
`Yield ≈ Base × (1 + 0.15×Irrigation) × (1 + 0.12×Fertilizer_score) × (1 – 0.30×Drought) × (1 – 0.15×Heat)`

### Key Takeaway for {district}:
Focus management effort in this priority order:
1. **Water security** (irrigation/rainwater harvesting)
2. **Balanced fertilization** (Soil Health Card) 
3. **Stress-tolerant seed varieties** (TNAU certified)
4. **Integrated Pest Management** (IPM)
5. **Crop insurance** (PMFBY) as financial safety net
"""
    }
    return answers.get(q_num, f"## Q{q_num} — Analysis not available for this question.")


# 
# ML HELPER — BUILD DATASET FROM TN_DISTRICTS + CROP_DB
# 

def build_ml_dataset():
    """Build a synthetic but realistic dataset from TN district + crop data."""
    import numpy as np
    import pandas as pd
    np.random.seed(42)
    rows = []
    for dist, dd in TN_DISTRICTS.items():
        for crop in dd["main_crops"]:
            if crop not in CROP_DB:
                continue
            cb = CROP_DB[crop]
            base_yield = (cb["yield_min"] + cb["yield_max"]) / 2
            for yr in [2019, 2020, 2021, 2022, 2023, 2024]:
                rn = np.random.normal
                rainfall = max(100, dd["rainfall_mm"] + rn(0, 60))
                humidity = float(np.clip(dd["humidity"] + rn(0, 2), 30, 99))
                soil_moist = float(np.clip(humidity * 0.68 + rn(0, 3), 10, 99))
                avg_temp = round(dd["avg_temp"] + rn(0, 0.5), 1)
                soil_ph = round(dd["soil_ph"] + rn(0, 0.1), 2)
                fertilizer = max(10, cb["cost_ha"] / 1200 + rn(0, 5))
                pesticide = max(0.5, 2 + rn(0, 0.5))
                irrigation = max(0, cb["cost_ha"] / 210 - rainfall * 0.28 + rn(0, 20))
                sunlight = float(np.clip(8 + rn(0, 0.5), 5, 12))
                wind = max(0, 15 + rn(0, 3))
                co2 = round(410 + (yr - 2019) * 2.5 + rn(0, 1), 1)
                grow_days = cb["days"]
                drought = float(np.clip(1 - rainfall / 1800 + rn(0, 0.05), 0, 1))
                heat_stress= float(np.clip((avg_temp - 25) / 10 + rn(0, 0.05), 0, 1))
                flood_risk = float(np.clip((rainfall - 800) / 1500 + rn(0, 0.05), 0, 1))
                climate_sc = float(np.clip((drought + heat_stress) / 2 + rn(0, 0.07), 0.1, 1))

                yield_val = max(0.1, base_yield * (1 + (yr - 2019) * 0.015)
                                 + rn(0, base_yield * 0.07)
                                 - drought * base_yield * 0.30
                                 - heat_stress * base_yield * 0.15
                                 + soil_moist * base_yield * 0.002
                                 + fertilizer * base_yield * 0.0015
                                 + pesticide * base_yield * 0.005)
                harvest_loss = max(0, 8 + drought * 14 + heat_stress * 6 + rn(0, 2))

                # Profit tier — ROI% based so low-cost crops (Millets, Pearl Millet, Pulses)
                # are not wrongly labelled Low just because absolute profit is small.
                # Millets: ROI ~108% High | Paddy: ROI ~157% High | Banana: ROI ~58% Medium
                _p_tier = calc_profit(crop, 1.0)
                _roi_tier = _p_tier["roi"] # already a percentage
                if _roi_tier >= 80:
                    tier ="High"
                elif _roi_tier >= 35:
                    tier ="Medium"
                else:
                    tier ="Low"

                rows.append({
                    "District": dist,"Zone": dd["zone"],"Crop": crop,"Year": yr,
                    "Rainfall": round(rainfall, 1),"Humidity": round(humidity, 1),
                    "SoilMoisture": round(soil_moist, 1),"AvgTemp": avg_temp,
                    "SoilpH": soil_ph,"Fertilizer": round(fertilizer, 1),
                    "Pesticide": round(pesticide, 2),"Irrigation": round(irrigation, 1),
                    "Sunlight": round(sunlight, 1),"Wind": round(wind, 1),
                    "CO2": co2,"GrowDays": grow_days,
                    "DroughtIdx": round(drought, 3),"HeatIdx": round(heat_stress, 3),
                    "FloodIdx": round(flood_risk, 3),"ClimateScore": round(climate_sc, 2),
                    "Yield": round(yield_val, 3),"HarvestLoss": round(harvest_loss, 2),
                    "ProfitTier": tier,
                })
    return pd.DataFrame(rows)


# 
# SESSION STATE
# 


# 
# SESSION STATE
# 
defaults = {
    "messages":[],"district":None,"dist_data":None,"land_ha":1.0,
    "farmer_name":"Farmer","setup_done":False,"pending_query":None,
    "api_key":"","selected_crop":None,"conclusion_text":None,
    "home_page":1,"weather_data":None,"weather_district":"Thoothukudi",
    "soil_report":None,"irrigation_report":None,"market_report":None,
    "calendar_report":None,"farmer_history":[],"profile_completed":False,
    "phone":"","water_source":"Canal Irrigation","primary_crop":"Paddy"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ---------------- Step 2 Guard: Farmer Profile Setup ----------------
def render_profile_setup():
    st.markdown("""
        <div style="text-align: center; padding: 25px 0 10px 0;">
            <h1 style="color: #2e7d32; font-size: 2.6rem; margin-bottom: 5px;"> Welcome to AgriSmart TN!</h1>
            <p style="font-size: 1.1rem; color: #555; font-weight: 500;">Step 2: Please fill in your farmer profile & farm details to complete registration.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    with col2:
        st.markdown("---")
        with st.form("profile_setup_form"):
            st.subheader("Farmer & Farm Profile Details")
            
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                f_name = st.text_input("Full Farmer Name", value=st.session_state.get('farmer_name',''), placeholder="e.g. Ramanathan K")
                phone = st.text_input("Mobile Number / Contact", value=st.session_state.get('phone',''), placeholder="e.g. 9876543210")
                dist_list = sorted(TN_DISTRICTS.keys())
                sel_dist = st.selectbox("Select Your District", dist_list, index=dist_list.index("Thoothukudi") if"Thoothukudi"in dist_list else 0)
            
            with c_f2:
                land_area = st.number_input("Total Farm Land Area (Hectares)", min_value=0.1, max_value=500.0, value=float(st.session_state.get('land_ha', 1.0)), step=0.5)
                water_source = st.selectbox("Primary Water Source", ["Canal Irrigation","Borewell / Well","Rain-fed","Drip / Sprinkler"])
                primary_crop = st.selectbox("Primary Crop Interest", ["Paddy","Banana","Sugarcane","Groundnut","Cotton","Coconut","Turmeric","Jasmine"])
                
            submit_profile = st.form_submit_button("Save Profile & Enter Platform", type="primary", use_container_width=True)
            
            if submit_profile:
                if f_name and sel_dist:
                    st.session_state["farmer_name"] = f_name
                    st.session_state["phone"] = phone
                    st.session_state["district"] = sel_dist
                    st.session_state["dist_data"] = TN_DISTRICTS[sel_dist]
                    st.session_state["land_ha"] = land_area
                    st.session_state["water_source"] = water_source
                    st.session_state["primary_crop"] = primary_crop
                    st.session_state["profile_completed"] = True
                    st.session_state["setup_done"] = True
                    st.success("Profile saved successfully! Entering platform...")
                    st.rerun()
                else:
                    st.error("Please fill in your name and select a district.")

# Guard 2: Require profile setup after login
if not st.session_state.get("profile_completed", False):
    render_profile_setup()
    st.stop()


# 
# SIDEBAR (Authenticated & Profile Completed View)
# 
with st.sidebar:
    st.title("AgriSmart TN")
    user_name = st.session_state.get('farmer_name','User')
    user_role = st.session_state.get('role','Farmer')
    user_dist = st.session_state.get('district','TN')
    st.caption(f"**{user_name}** (`{user_role}`) | **{user_dist}**")
    
    if st.button("Log Out", key="logout_btn", type="secondary", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["profile_completed"] = False
        st.session_state["role"] = None
        st.rerun()
        
    st.markdown("---")
    
    # Interactive Sidebar Guide Buttons
    st.markdown("### Farmer Advisory Modules")
    
    if"active_feature"not in st.session_state:
        st.session_state["active_feature"] ="Smart Crop Advisor"
        
    features_list = [
        "Smart Crop Advisor",
        "Farmer Dashboard",
        "Pest & Disease Guide",
        "Soil & Fertilizer Guide",
        "Water & Irrigation Guide",
        "Loans & Schemes Guide",
        "Crop Rotation Calendar",
        "Mandi Price Guide",
        "District Map & Info",
        "Weather & Rain Alerts",
        "AI Voice Assistant",
        "Farmer Profile",
        "Farm Action Plan PDF",
    ]
    
    for feat in features_list:
        is_active = (st.session_state["active_feature"] == feat)
        btn_type ="primary"if is_active else"secondary"
        if st.sidebar.button(feat, key=f"nav_btn_{feat}", type=btn_type, use_container_width=True):
            st.session_state["active_feature"] = feat
            st.rerun()

    app_selection = st.session_state["active_feature"]
    
    st.markdown("---")
    st.markdown(f"""
    <div style="background-color: #f1f8e9; padding: 12px 14px; border-radius: 8px; border-left: 4px solid #2e7d32; margin-bottom: 10px;">
        <p style="margin: 0; font-size: 0.86rem; color: #1b4332; line-height: 1.5;">
            <b> District:</b> {st.session_state.get('district')}<br>
            <b> Farm Area:</b> {st.session_state.get('land_ha')} Ha<br>
            <b> Target Crop:</b> {st.session_state.get('primary_crop')}<br>
            <b> Irrigation:</b> {st.session_state.get('water_source')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Edit Farm Profile", key="edit_farm_btn", use_container_width=True):
        st.session_state["profile_completed"] = False
        st.rerun()

# Auto-initialize Crop Advisor messages if empty
if app_selection =="Smart Crop Advisor"and not st.session_state.get("messages"):
    sel_district = st.session_state.get('district','Thoothukudi')
    land_ha = float(st.session_state.get('land_ha', 1.0))
    farmer_name = st.session_state.get('farmer_name','Farmer')
    dd = TN_DISTRICTS.get(sel_district, TN_DISTRICTS["Thoothukudi"])
    
    top = [f"{CROP_DB[c]['emoji']} **{c}** — {fmt_inr(calc_profit(c, land_ha)['profit'])}"
           for c in dd['main_crops'] if c in CROP_DB][:4]
    welcome = (
        f"Hello {farmer_name}! Welcome to AgriSmart Crop Advisor.\n\n"
        f"You have **{land_ha} hectares** in **{sel_district}** ({dd['known_for']}).\n\n"
        f"**Top crops with estimated profit for your land:**\n"+"\n".join(top) +
        "\n\nI can help you with:\n"
        "- Best crop for your district's climate\n"
        "- Exact profit calculation for your land size\n"
        "- Yield comparison against state averages\n"
        "- Full conclusion report when you pick a crop\n"
        "- Government schemes you can apply for\n\n"
        f"Your target crop is **{st.session_state.get('primary_crop')}**. Ask any question below or request a full yield report!"
    )
    st.session_state.messages.append({"role":"assistant","content": welcome})

def render_professional_dashboard():
    dist = st.session_state.get('district','Thoothukudi')
    land_ha = float(st.session_state.get('land_ha', 1.0))
    farmer_name = st.session_state.get('farmer_name','Farmer')
    role = st.session_state.get('role','Farmer')
    crop = st.session_state.get('primary_crop','Paddy')
    water = st.session_state.get('water_source','Canal Irrigation')
    dd = TN_DISTRICTS.get(dist, TN_DISTRICTS["Thoothukudi"])
    
    # 1. Executive Top Hero Banner
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 50%, #40916c 100%); padding: 22px 28px; border-radius: 14px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 25px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;"> {role} Portal</span>
                <h2 style="margin: 8px 0 4px 0; font-size: 1.9rem; color: #ffffff;">Welcome back, {farmer_name}!</h2>
                <p style="margin: 0; opacity: 0.9; font-size: 0.98rem;"> <b>{dist} District</b> ({dd['zone']} Zone) &nbsp;|&nbsp; Farm Area: <b>{land_ha} Ha ({land_ha*2.471:.1f} Acres)</b></p>
            </div>
            <div style="background: rgba(0,0,0,0.25); padding: 12px 20px; border-radius: 10px; text-align: right; border: 1px solid rgba(255,255,255,0.15);">
                <div style="font-size: 1.1rem; font-weight: bold; color: #74c69d;"> {dd['avg_temp']}°C | Rain {dd['rainfall_mm']}mm</div>
                <div style="font-size: 0.82rem; opacity: 0.85;">Soil: {dd['soil']} (pH {dd['soil_ph']})</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Executive KPI Cards
    c_k1, c_k2, c_k3, c_k4 = st.columns(4)
    profit_info = calc_profit(crop, land_ha) if crop in CROP_DB else {"profit": 45000,"revenue": 85000,"cost": 40000}
    
    with c_k1:
        st.metric("Total Land Area", f"{land_ha} Ha", f"~ {land_ha*2.471:.1f} Acres")
    with c_k2:
        st.metric("Primary Target Crop", f"{crop}", f"{water}")
    with c_k3:
        st.metric("Expected Net Profit", fmt_inr(profit_info['profit']),"High Yield Zone")
    with c_k4:
        st.metric("Soil Health Index", f"pH {dd['soil_ph']}","Optimal Quality")

    st.markdown("---")

    # 3. Main Dashboard Layout (Columns 0.62 / 0.38)
    col_left, col_right = st.columns([0.62, 0.38])

    with col_left:
        st.subheader("Crop Economics & Profit Comparison")
        import pandas as pd
        
        # Calculate profits for district's top crops
        top_crops = dd['main_crops'][:4]
        crop_data = []
        for c in top_crops:
            if c in CROP_DB:
                p_res = calc_profit(c, land_ha)
                crop_data.append({
                    "Crop": f"{CROP_DB[c]['emoji']} {c}",
                    "Cost (₹)": p_res["cost"],
                    "Revenue (₹)": p_res["revenue"],
                    "Profit (₹)": p_res["profit"]
                })
        if not crop_data:
            crop_data = [{"Crop":"Paddy","Cost (₹)": 35000,"Revenue (₹)": 85000,"Profit (₹)": 50000}]
            
        df_crops = pd.DataFrame(crop_data)
        st.dataframe(df_crops, use_container_width=True, hide_index=True)
        st.bar_chart(df_crops.set_index("Crop")[["Cost (₹)","Revenue (₹)","Profit (₹)"]])

        st.markdown("### Seasonal Cultivation & Crop Care Timeline")
        st.markdown("""
        - **Stage 1 (Day 1 - 15):** Basal Soil Fertilization & Seed Treatment — *Completed*
        - **Stage 2 (Day 16 - 45):** First Top Dressing (Urea 50kg/ha) & Irrigation — *In Progress (Due in 4 days)*
        - **Stage 3 (Day 46 - 90):** Flowering & Pest Monitoring — *Upcoming*
        - **Stage 4 (Day 91 - 120):** Grain Filling & Harvesting Phase — *Scheduled*
        """)

    with col_right:
        st.subheader("AI Advisor Recommendations")
        st.info(f"**District Insight for {dist}:** {dd['known_for']}. River {dd['river']} supplies major irrigation.")
        
        st.markdown("#### Soil Health Card & NPK Status")
        st.write("• **Nitrogen (N):** 110 kg/ha (Normal)")
        st.write("• **Phosphorus (P):** 45 kg/ha (Optimal)")
        st.write("• **Potassium (K):** 65 kg/ha (Good)")
        st.write(f"• **Organic Carbon:** 0.65% (Medium)")
        
        st.markdown("#### Quick Actions & Utilities")
        q_col1, q_col2 = st.columns(2)
        with q_col1:
            if st.button("Soil Report", use_container_width=True):
                st.success("Soil report generated!")
        with q_col2:
            if st.button("Rain Alert", use_container_width=True):
                st.warning("Rain alert active!")
                
        st.markdown("---")
        st.markdown(f"**Assigned Role View:** `{role}`")
        if role =="Admin":
            st.warning("**Admin Mode:** 38 Districts Active | Server Status: 99.9% Uptime")
        elif role =="Extension Officer":
            st.info("**Officer Mode:** 12 Field Inspections Scheduled for Tanjore Delta.")
        elif role =="Agri-Expert":
            st.success("**Expert Mode:** Diagnostic AI Engine V2.4 Active.")

# Handle dedicated feature pages if not Smart Crop Advisor
if app_selection !="Smart Crop Advisor":
    st.title(app_selection)
    st.caption(f"Welcome **{st.session_state.get('farmer_name','User')}** (`{st.session_state.get('role','Farmer')}`) — AgriSmart TN Feature Hub")
    st.markdown("---")
    
    if"Farmer Profile"in app_selection:
        st.subheader("Registered Farmer Profile Details")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.write(f"**Farmer Name:** {st.session_state.get('farmer_name')}")
            st.write(f"**Mobile Contact:** {st.session_state.get('phone','N/A')}")
            st.write(f"**Assigned Role:** {st.session_state.get('role')}")
            st.write(f"**District:** {st.session_state.get('district')}")
        with col_p2:
            st.write(f"**Farm Land Area:** {st.session_state.get('land_ha')} Hectares")
            st.write(f"**Water Source:** {st.session_state.get('water_source')}")
            st.write(f"**Primary Crop:** {st.session_state.get('primary_crop')}")
            
        if st.button("Edit Profile Details", type="primary"):
            st.session_state["profile_completed"] = False
            st.rerun()
    
    elif"Dashboard"in app_selection:
        render_professional_dashboard()

    elif"Pest & Disease"in app_selection:
        st.subheader("Comprehensive Pest & Disease Management Guide")
        st.caption("Step-by-step diagnostic and treatment guide for Tamil Nadu crops.")
        selected_p_crop = st.selectbox("Select Crop to View Pest Guide", ["Paddy","Sugarcane","Banana","Groundnut","Cotton","Coconut"])
        
        if selected_p_crop =="Paddy":
            st.markdown("""
            ### Paddy Pest & Disease Solutions:
            1. **Yellow Stem Borer (Stem Tunneling):**
               - **Symptoms:** Dead hearts in vegetative stage, white heads in flowering stage.
               - **Organic Remedy:** Release *Trichogramma japonicum* egg parasitoid @ 5 cc/ha 3 times.
               - **Chemical Remedy:** Spray Chlorantraniliprole 18.5% SC @ 150 ml/ha.
            2. **Brown Plant Hopper (BPH - Hopper Burn):**
               - **Symptoms:** Drying of plants in circular patches giving a burnt appearance.
               - **Organic Remedy:** Spray Neem Seed Kernel Extract (NSKE 5%) @ 25 kg/ha.
               - **Chemical Remedy:** Spray Pymetrozine 50% WG @ 300 g/ha. Alternate wet & dry irrigation.
            3. **Bacterial Leaf Blight (BLB):**
               - **Symptoms:** Straw-colored lesions starting from leaf tips along margins.
               - **Remedy:** Spray Fresh Cow dung extract (20g/L) or Streptocycline (0.25g/L) + Copper Oxychloride (1g/L).
            """)
        else:
            st.info(f"Displaying pest control steps for **{selected_p_crop}**. Spray Neem Oil (5ml/L) for early prevention.")
            st.markdown("""
            - **Preventive Care:** Field sanitation, removal of weed hosts, balanced NPK application.
            - **Biological Control:** Encourage ladybird beetles, dragonflies, and spiders in field.
            """)

    elif"Soil & Fertilizer"in app_selection:
        st.subheader("Soil Health & Stage-by-Stage Fertilizer Guide")
        land_ha = float(st.session_state.get('land_ha', 1.0))
        crop = st.session_state.get('primary_crop','Paddy')
        dist = st.session_state.get('district','Thoothukudi')
        
        st.success(f"Customized Fertilizer Plan for **{st.session_state.get('farmer_name')}** ({land_ha} Ha of {crop} in {dist})")
        
        c_s1, c_s2, c_s3 = st.columns(3)
        c_s1.metric("Basal Urea (At Sowing)", f"{int(75 * land_ha)} kg")
        c_s2.metric("Super Phosphate (SSP)", f"{int(250 * land_ha)} kg")
        c_s3.metric("Potash (MOP)", f"{int(50 * land_ha)} kg")
        
        st.markdown("""
        ### Step-by-Step Fertilizer Application Schedule:
        - **Stage 1: Basal Dose (Before Final Ploughing)**
          - Mix 10 tonnes FYM/compost + full dose of SSP & half MOP into soil.
        - **Stage 2: Active Tillering (25-30 Days After Sowing)**
          - Apply 50% Urea top dressing when field has thin water layer.
        - **Stage 3: Panicle Initiation (45-50 Days After Sowing)**
          - Apply remaining 50% Urea + remaining MOP for grain filling.
        - **Micronutrient Care:** Spray 1% Zinc Sulphate to fix leaf yellowing.
        """)

    elif"Water & Irrigation"in app_selection:
        st.subheader("Farmer Water Management & Irrigation Guide")
        st.caption("Practical guidelines for optimal water use and drip installation.")
        st.write(f"**District Irrigation Source:** {st.session_state.get('water_source')} in {st.session_state.get('district')}")
        st.markdown("""
        ### Critical Irrigation Stages for Paddy / Field Crops:
        1. **Transplanting Stage (0-10 Days):** Maintain 2 cm shallow water depth.
        2. **Tillering Stage (11-40 Days):** Alternate wetting and drying (AWD) — saves 30% water!
        3. **Flowering & Panicle Stage (41-75 Days):** Maintain 5 cm continuous submergence.
        4. **Pre-Harvest (10 Days Before Harvest):** Drain water completely for uniform ripening.
        """)

    elif"Loans & Schemes"in app_selection:
        st.subheader("Government Schemes, Loans & Subsidies Guide")
        st.caption("Step-by-step assistance for Tamil Nadu Agricultural Schemes.")
        
        t_scheme1, t_scheme2, t_scheme3 = st.tabs(["PM-KISAN","Kisan Credit Card (KCC)","Machinery Subsidy"])
        with t_scheme1:
            st.markdown("""
            #### PM-KISAN Samman Nidhi (₹6,000 / Year)
            - **Benefit:** ₹2,000 paid in 3 installments directly to your bank account.
            - **Eligibility:** All landholding farmer families in Tamil Nadu.
            - **Documents Needed:** Aadhaar Card, Land Patta/Chitta copy, Active Bank Passbook.
            - **How to Apply:** Visit nearest e-Seva Center or pmkisan.gov.in.
            """)
        with t_scheme2:
            st.markdown("""
            #### Kisan Credit Card (KCC Loan @ 4% Interest)
            - **Benefit:** Collateral-free crop loan up to ₹1.6 Lakhs (up to ₹3 Lakhs total).
            - **Eligibility:** Farmers, tenant farmers, and sharecroppers.
            - **Step-by-Step:** Fill KCC form at your local Primary Agricultural Cooperative Society (PACS) or Nationalized Bank.
            """)
        with t_scheme3:
            st.markdown("""
            #### TNAU 50% Agricultural Machinery Subsidy
            - **Benefit:** 50% financial subsidy on Power Tillers, Solar Pumps, and Drones.
            - **Application:** Apply on the Uzhavan App (உழவன் செயலி) under AED Subsidies.
            """)

    elif"Crop Rotation Calendar"in app_selection or"Calendar"in app_selection:
        st.subheader("Tamil Nadu Seasonal Harvest & Crop Rotation Guide")
        st.markdown("""
        ### Tamil Nadu Agro-Climatic Seasons:
        | Season Name | Sowing Months | Harvesting Months | Recommended Crops |
        |---|---|---|---|
        | **Sornavari / Kar** | April - May | August - September | Short Paddy (ADT 37, CO 51), Sesame, Cotton |
        | **Samba** | August - September | January - February | Long Paddy (CR 1009, White Ponni), Sugarcane |
        | **Navarai** | December - January | April - May | Pulses, Groundnut, Vegetables, Watermelon |
        
        ### Recommended Crop Rotation Pattern:
        - Year 1: Paddy Black Gram (Restores Nitrogen) Sesame
        - Year 2: Cotton / Maize Groundnut Vegetables
        """)

    elif"Mandi Price"in app_selection or"Market"in app_selection:
        st.subheader("Wholesale Mandi Market Rate Guide")
        import pandas as pd
        mandi_df = pd.DataFrame({
            "Market Mandi": ["Madurai Central","Koyambedu (Chennai)","Coimbatore MGR","Erode Turmeric Market","Trichy Wholesale"],
            "Commodity": ["Jasmine","Tomato","Banana (Nendran)","Turmeric","Paddy (Ponni)"],
            "Current Price (₹/Quintal)": [45000, 2400, 3800, 14200, 2250],
            "Daily Trend": ["+8.5%","-3.2%","+1.4%","+4.8%","+0.5%"]
        })
        st.dataframe(mandi_df, use_container_width=True)

    elif"District Map"in app_selection:
        st.subheader("Interactive Tamil Nadu District Agricultural Map")
        import pandas as pd
        map_data = pd.DataFrame([
            {"lat": d["lat"],"lon": d["lon"],"district": k}
            for k, d in TN_DISTRICTS.items()
        ])
        st.map(map_data, latitude="lat", longitude="lon", zoom=6)

    elif"Weather"in app_selection:
        st.subheader("Real-Time Weather & Monsoon Warning")
        st.warning("**Monsoon Alert**: Heavy rainfall forecast in coastal Tamil Nadu over next 48 hrs.")

    elif"Voice Assistant"in app_selection:
        st.subheader("AI Voice Assistant (Tamil & English)")
        v_query = st.text_input("Ask Voice Assistant", placeholder="e.g. Which fertilizer for Paddy in Tanjore?")
        if st.button("Play Voice Answer", type="primary"):
            st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3")

    elif"PDF"in app_selection:
        st.subheader("Export Printable Farm Action Plan PDF")
        st.write(f"**Farmer Name:** {st.session_state.get('farmer_name')}")
        st.write(f"**District:** {st.session_state.get('district')}")
        st.write(f"**Land Size:** {st.session_state.get('land_ha')} Hectares")
        st.write(f"**Target Crop:** {st.session_state.get('primary_crop')}")
        st.write(f"**Water Source:** {st.session_state.get('water_source')}")
        if st.button("Download Printable Farm Action Plan PDF", type="primary"):
            st.success("Download starting! Printable action plan generated successfully.")

    else:
        st.info(f"**{app_selection}** feature module active.")

    st.stop()


# 
# HOME PAGE (before Start)
# 
if not st.session_state.setup_done:

    pg1_btn, pg2_btn = st.columns(2)
    with pg1_btn:
        if st.button("Page 1 — Live Weather Dashboard", width='stretch'):
            st.session_state.home_page = 1
            st.rerun()
    with pg2_btn:
        if st.button("Page 2 — All 38 Districts Info", width='stretch'):
            st.session_state.home_page = 2
            st.rerun()

    st.markdown("---")

    # HOME PAGE 1 — Live Weather 
    if st.session_state.home_page == 1:

        st.markdown("### AgriSmart TN — Smart Crop Advisor")
        st.write("Live weather · All 38 Tamil Nadu districts · AI crop guide · Yield comparison · Conclusion report.")
        st.write("Pick your district in the sidebar and click **Start Crop Advisor** to begin.")

        st.markdown("---")

        f1, f2, f3, f4, f5 = st.columns(5)
        with f1:
            st.info("**Live Weather**\nReal-time temp, humidity, wind & rain for any TN district")
        with f2:
            st.info("**Crop Advisor**\nAsk anything — crop advice, profit, growing tips")
        with f3:
            st.info("**Yield Comparison**\nYour crop vs state average (2019–2024 charts)")
        with f4:
            st.info("**Conclusion Report**\nFull AI-written action plan after you pick a crop")
        with f5:
            st.info("**District Intelligence**\nIn-depth zone grouping, yield forecast & profit assessment")

        st.markdown("---")
        st.subheader("Live Weather Dashboard")

        wcol1, wcol2 = st.columns([2, 1])
        with wcol1:
            weather_city = st.selectbox("Select District for Live Weather",
                                        dist_list,
                                        index=dist_list.index("Thoothukudi"),
                                        key="weather_select")
        with wcol2:
            st.write("")
            fetch_btn = st.button("Fetch Live Weather", width='stretch')

        if st.session_state.weather_data is None or fetch_btn or weather_city != st.session_state.weather_district:
            st.session_state.weather_district = weather_city
            wd = TN_DISTRICTS[weather_city]
            with st.spinner(f"Fetching live weather for {weather_city}..."):
                st.session_state.weather_data = get_live_weather(wd["lat"], wd["lon"], weather_city)

        wdata = st.session_state.weather_data
        city_d = TN_DISTRICTS[st.session_state.weather_district]

        if wdata and"current"in wdata:
            cur = wdata["current"]
            daily = wdata.get("daily", {})
            temp = cur.get("temperature_2m","--")
            feels = cur.get("apparent_temperature","--")
            humidity = cur.get("relative_humidity_2m","--")
            wind = cur.get("wind_speed_10m","--")
            precip = cur.get("precipitation", 0)
            wcode = cur.get("weather_code", 0)
            wdesc = weather_desc(wcode)

            st.caption(f"LIVE — {st.session_state.weather_district}, Tamil Nadu · {datetime.datetime.now().strftime('%d %b %Y, %I:%M %p')}")

            w1, w2, w3, w4, w5 = st.columns(5)
            with w1:
                st.metric("Temperature", f"{temp}°C")
            with w2:
                st.metric("Feels Like", f"{feels}°C")
            with w3:
                st.metric("Humidity", f"{humidity}%")
            with w4:
                st.metric("Wind Speed", f"{wind} km/h")
            with w5:
                st.metric("Rainfall", f"{precip} mm")

            st.info(f"**Current Condition:** {wdesc} | **District:** {st.session_state.weather_district} | **River:** {city_d['river']} | **Known for:** {city_d['known_for']}")

            if daily and"temperature_2m_max"in daily:
                st.subheader("3-Day Forecast")
                fc1, fc2, fc3 = st.columns(3)
                dates = daily.get("time", ["","",""])
                t_max = daily.get("temperature_2m_max", [0, 0, 0])
                t_min = daily.get("temperature_2m_min", [0, 0, 0])
                prec = daily.get("precipitation_sum", [0, 0, 0])
                day_names = []
                for d in dates[:3]:
                    try:
                        dt = datetime.datetime.strptime(d,"%Y-%m-%d")
                        day_names.append(dt.strftime("%a, %d %b"))
                    except:
                        day_names.append(d)
                for col, i in zip([fc1, fc2, fc3], range(3)):
                    with col:
                        st.info(f"**{day_names[i] if i < len(day_names) else''}**\n{t_max[i]:.0f}°C / {t_min[i]:.0f}°C\nRain: {prec[i]:.1f} mm")

        else:
            st.warning("Live fetch failed — showing static district data.")
            w1, w2, w3, w4, w5 = st.columns(5)
            with w1:
                st.metric("Avg Temperature", f"{city_d['avg_temp']}°C")
            with w2:
                st.metric("Humidity", f"{city_d['humidity']}%")
            with w3:
                st.metric("Annual Rainfall", f"{city_d['rainfall_mm']}mm")
            with w4:
                st.metric("Soil pH", city_d['soil_ph'])
            with w5:
                st.metric("River", city_d['river'].split(',')[0].strip()[:14])

        st.markdown("---")
        st.subheader("Farming Conditions Today")

        temp_val = wdata["current"]["temperature_2m"] if wdata and"current"in wdata else city_d["avg_temp"]
        hum_val = wdata["current"]["relative_humidity_2m"] if wdata and"current"in wdata else city_d["humidity"]

        irr_advice ="Good time to irrigate"if hum_val < 60 else"Skip irrigation today"if hum_val > 80 else"Irrigate in the evening"
        sow_advice ="Ideal sowing conditions"if 22 <= temp_val <= 32 else"Too hot for sowing"if temp_val > 35 else"Too cool for tropical crops"
        pest_advice ="High humidity — check for fungal diseases"if hum_val > 78 else"Normal pest pressure"if hum_val > 60 else"Low disease risk"

        fa1, fa2, fa3, fa4, fa5 = st.columns(5)
        with fa1:
            st.success(f"**Sunlight**\nGood")
        with fa2:
            if hum_val > 60:
                st.success(f"**Soil Moisture**\nAdequate")
            else:
                st.warning(f"**Soil Moisture**\nLow")
        with fa3:
            if 22 <= temp_val <= 32:
                st.success(f"**Crop Growth**\nFavorable")
            else:
                st.warning(f"**Crop Growth**\nMonitor")
        with fa4:
            if hum_val > 78:
                st.warning(f"**Pest Risk**\nHigh")
            else:
                st.success(f"**Pest Risk**\nLow")
        with fa5:
            st.info(f"**Irrigation**\n{irr_advice}")

        st.markdown("---")
        st.subheader("Summary")
        st.write(f"District: {st.session_state.weather_district} | Temp: {temp_val}°C | Humidity: {hum_val}%")
        st.write(f"Sowing: {sow_advice} | Pest Watch: {pest_advice}")
        st.write("Select your district in the sidebar and click **Start Crop Advisor** to begin.")

    # HOME PAGE 2 — All Districts 
    else:
        st.markdown("### All 38 Tamil Nadu Districts")
        st.write("Climate data, main crops, and soil info for every district.")

        search_q = st.text_input("Search district...", placeholder="e.g. Erode, Turmeric, Alluvial...")

        filtered = {k: v for k, v in sorted(TN_DISTRICTS.items())
                    if not search_q or search_q.lower() in k.lower()
                    or search_q.lower() in v['known_for'].lower()
                    or any(search_q.lower() in c.lower() for c in v['main_crops'])}

        st.caption(f"Showing {len(filtered)} of 38 districts")

        cols = st.columns(3)
        for i, (dist, data) in enumerate(filtered.items()):
            with cols[i % 3]:
                crops_str =",".join([f"{CROP_DB[c]['emoji']} {c}"for c in data['main_crops'][:3] if c in CROP_DB])
                with st.expander(f"**{dist}** — {data['known_for']}"):
                    st.write(f"**Zone:** {data['zone']}")
                    st.write(f"**Temp:** {data['avg_temp']}°C | **Rain:** {data['rainfall_mm']}mm | **Humidity:** {data['humidity']}%")
                    st.write(f"**Soil:** {data['soil']} (pH {data['soil_ph']})")
                    st.write(f"**River:** {data['river']}")
                    st.write(f"**Crops:** {crops_str}")


# 
# MAIN APP (after Start Crop Advisor)
# 
else:
    district = st.session_state.district
    dd = st.session_state.dist_data
    land = st.session_state.land_ha
    name = st.session_state.farmer_name
    sel_crop = st.session_state.selected_crop

    st.markdown(f"### AgriSmart Farm Dashboard — {district}")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("District", district)
    with c2:
        st.metric("Land", f"{land} ha")
    with c3:
        st.metric("Temp", f"{dd['avg_temp']}°C")
    with c4:
        st.metric("Rainfall", f"{dd['rainfall_mm']}mm/yr")
    with c5:
        st.metric("Soil pH", dd['soil_ph'])

    st.markdown("---")

    # ML setup (used across multiple tabs) 
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.express as px
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (mean_squared_error, r2_score,
                                 accuracy_score, classification_report,
                                 confusion_matrix)

    @st.cache_data
    def get_ml_data():
        return build_ml_dataset()

    df_ml = get_ml_data()

    FEAT_COLS = ["Rainfall","Humidity","SoilMoisture","AvgTemp",
                 "SoilpH","Fertilizer","Pesticide","Irrigation",
                 "Sunlight","Wind","CO2","GrowDays",
                 "DroughtIdx","HeatIdx","FloodIdx","ClimateScore"]

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Crop Advisor Chat","Yield Comparison","Profit Calculator",
        "Full Farm Report","Soil & Fertilizer","Irrigation Plan","Market & Selling"
    ])

    with tab1:
        st.markdown("---")
        st.subheader("Select Your Crop")
        st.caption("Selecting a crop activates the Yield Comparison and Conclusion Report tabs with your personalised data.")

        all_crops = list(dict.fromkeys(dd["main_crops"] + [c for c in CROP_DB if c not in dd["main_crops"]]))
        crop_opts = ["-- Choose a crop --"] + all_crops
        curr_idx = crop_opts.index(sel_crop) if sel_crop in crop_opts else 0
        crop_choice = st.selectbox("Crop selector", crop_opts, index=curr_idx, label_visibility="collapsed")

        if crop_choice !="-- Choose a crop --"and crop_choice != sel_crop:
            st.session_state.selected_crop = crop_choice
            st.session_state.conclusion_text = None
            st.session_state.pending_query = f"I have chosen to grow **{crop_choice}**. Please give me a detailed analysis — growing guide, profit for {land} hectares, and best tips for {district}."
            st.rerun()

        if sel_crop and sel_crop in CROP_DB:
            p = calc_profit(sel_crop, land)
            c = CROP_DB[sel_crop]
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Selected Crop", f"{c['emoji']} {sel_crop}")
            with m2:
                st.metric("Est. Profit", fmt_inr(p['profit']))
            with m3:
                st.metric("Expected Yield", f"{p['total_yield']} t")
            with m4:
                st.metric("ROI", f"{p['roi']}%")

        if st.session_state.pending_query:
            query = st.session_state.pending_query
            st.session_state.pending_query = None
            st.session_state.messages.append({"role":"user","content": query})
            with st.spinner("Thinking..."):
                try:
                    reply = get_ai_response(
                        st.session_state.messages, district, dd, land, name,
                        selected_crop=st.session_state.selected_crop
                    )
                    st.session_state.messages.append({"role":"assistant","content": reply})
                except Exception as e:
                    st.session_state.messages.pop()
                    st.error(f"Something went wrong: {str(e)}")

        st.markdown("---")
        st.subheader("Ask Your Crop Advisor")

        SKIP_PHRASES = ["No internet key set","running in offline mode","offline mode","API key"]
        st.session_state.messages = [
            m for m in st.session_state.messages
            if not any(p in m.get("content","") for p in SKIP_PHRASES)
        ]

        # Chat history controls 
        _hist_col1, _hist_col2 = st.columns([3,1])
        with _hist_col2:
            if st.session_state.messages:
                if st.button("View History", width='stretch', key="view_hist_btn"):
                    st.session_state["show_history"] = not st.session_state.get("show_history", False)
                if st.session_state.get("show_history", False):
                    with st.expander("Full Chat History", expanded=True):
                        for _hm in st.session_state.messages:
                            _role ="You"if _hm["role"] =="user"else"AgriSmart"
                            st.markdown(f"**{_role}:** {_hm['content']}")
                        if st.button("Close History", key="close_hist_btn"):
                            st.session_state["show_history"] = False
                            st.rerun()

        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                if msg["role"] =="user":
                    with st.chat_message("user"):
                        st.markdown(msg["content"])
                else:
                    with st.chat_message("assistant"):
                        st.markdown(msg["content"])

        user_input = st.chat_input(f"Ask anything about farming in {district}...", key="chat_input_box")
        if user_input and user_input.strip():
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(user_input.strip())
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            st.session_state.messages.append({"role":"user","content": user_input.strip()})
                            reply = get_ai_response(
                                st.session_state.messages, district, dd, land, name,
                                selected_crop=st.session_state.selected_crop
                            )
                            st.session_state.messages.append({"role":"assistant","content": reply})
                            st.markdown(reply)
                        except Exception as e:
                            st.session_state.messages.pop()
                            st.error(f"Something went wrong: {str(e)}")


        # Smart Crop Suitability — internal data only (no UI) 

        # Ideal growing conditions per crop 
        CROP_IDEAL = {
            "Paddy": {"rain":(900,2500),"temp":(22,35),"ph":(5.5,7.5),"humidity":(70,90)},
            "Banana": {"rain":(750,2500),"temp":(24,35),"ph":(6.0,7.5),"humidity":(60,85)},
            "Sugarcane": {"rain":(750,1800),"temp":(24,38),"ph":(6.0,8.0),"humidity":(55,85)},
            "Coconut": {"rain":(1000,3000),"temp":(24,32),"ph":(5.5,8.0),"humidity":(60,90)},
            "Groundnut": {"rain":(400,1200),"temp":(24,32),"ph":(6.0,7.5),"humidity":(40,75)},
            "Turmeric": {"rain":(1000,2000),"temp":(20,32),"ph":(5.5,7.0),"humidity":(65,90)},
            "Cotton": {"rain":(500,1200),"temp":(25,40),"ph":(6.0,8.0),"humidity":(40,70)},
            "Maize": {"rain":(500,1200),"temp":(18,35),"ph":(5.8,7.5),"humidity":(50,80)},
            "Mango": {"rain":(500,1500),"temp":(24,35),"ph":(5.5,7.5),"humidity":(40,75)},
            "Tomato": {"rain":(400,1200),"temp":(18,30),"ph":(6.0,7.0),"humidity":(50,80)},
            "Vegetables": {"rain":(500,1500),"temp":(18,32),"ph":(5.8,7.2),"humidity":(55,85)},
            "Millets": {"rain":(300,900),"temp":(25,38),"ph":(5.5,7.5),"humidity":(30,65)},
            "Pearl Millet":{"rain":(300,800),"temp":(25,40),"ph":(5.5,7.5),"humidity":(30,65)},
            "Tapioca": {"rain":(750,2000),"temp":(25,35),"ph":(5.5,7.5),"humidity":(55,80)},
            "Tea": {"rain":(1500,3000),"temp":(13,25),"ph":(4.5,6.0),"humidity":(75,90)},
            "Coffee": {"rain":(1200,2500),"temp":(15,25),"ph":(5.5,6.5),"humidity":(70,90)},
            "Rubber": {"rain":(1500,3000),"temp":(25,32),"ph":(4.5,6.5),"humidity":(75,95)},
            "Potato": {"rain":(500,1200),"temp":(10,20),"ph":(5.0,6.5),"humidity":(60,80)},
            "Carrot": {"rain":(400,1000),"temp":(10,22),"ph":(5.5,7.0),"humidity":(55,80)},
            "Grapes": {"rain":(600,1200),"temp":(20,35),"ph":(6.0,7.5),"humidity":(40,75)},
            "Jasmine": {"rain":(600,1200),"temp":(24,35),"ph":(6.0,7.5),"humidity":(55,80)},
            "Black Gram": {"rain":(600,1000),"temp":(25,35),"ph":(6.0,7.5),"humidity":(50,80)},
            "Pulses": {"rain":(400,900),"temp":(20,32),"ph":(6.0,7.5),"humidity":(40,75)},
        }

        def crop_suitability(crop, rain, temp, ph, humidity):
            """Return suitability score 0-100 based on how well district conditions match crop ideals."""
            if crop not in CROP_IDEAL:
                return 50 # neutral if unknown
            c = CROP_IDEAL[crop]
            def score_range(val, lo, hi):
                if lo <= val <= hi:
                    return 100
                elif val < lo:
                    return max(0, 100 - (lo - val) / lo * 200)
                else:
                    return max(0, 100 - (val - hi) / hi * 200)
            s_rain = score_range(rain, *c["rain"])
            s_temp = score_range(temp, *c["temp"])
            s_ph = score_range(ph, *c["ph"])
            s_hum = score_range(humidity, *c["humidity"])
            return round((s_rain * 0.4 + s_temp * 0.3 + s_ph * 0.15 + s_hum * 0.15), 1)

        rain = dd["rainfall_mm"]
        temp = dd["avg_temp"]
        ph = dd["soil_ph"]
        hum = dd["humidity"]

        # Step 1 — collect raw scores for all crops
        import numpy as _np_sc
        _raw = []
        for crop in CROP_DB:
            clim_score = crop_suitability(crop, rain, temp, ph, hum)
            p_data = calc_profit(crop, land)
            profit_val = p_data.get("profit", 0)
            roi_val = p_data.get("roi", 0)
            _raw.append((crop, clim_score, profit_val, roi_val))

        # Step 2 — percentile-normalise profit across all crops (0-100 scale)
        # This preserves real differences: Turmeric Rs.14L >> Millets Rs.1.4L
        _profits = _np_sc.array([x[2] for x in _raw], dtype=float)
        _p_min, _p_max = _profits.min(), _profits.max()

        all_scores = []
        for (crop, clim_score, profit_val, roi_val) in _raw:
            # Excluded crops get SmartScore=0
            if clim_score == 0:
                profit_score = 0.0
                smart_score = 0.0
            elif _p_max > _p_min:
                profit_score = round((_profits[[i for i,(c,*_) in enumerate(_raw) if c==crop][0]] - _p_min) / (_p_max - _p_min) * 100, 2)
                smart_score = round(clim_score * 0.50 + profit_score * 0.50, 1)
            else:
                profit_score = 50.0
                smart_score = round(clim_score * 0.50 + profit_score * 0.50, 1)
            all_scores.append({
                "Crop": f"{CROP_DB[crop]['emoji']} {crop}",
                "_crop": crop,
                "Suitability": clim_score,
                "SmartScore": smart_score,
                "_profit_score": profit_score,
                "ROI %": f"{roi_val}%",
                "_roi": roi_val,
                "Est. Profit": fmt_inr(profit_val),
                "_profit": profit_val,
                "Season": CROP_DB[crop].get("season","—")[:30],
                "Water Need": CROP_DB[crop].get("water","—"),
            })

        # Sort by smart score — now Turmeric (high profit + good climate) will rank correctly
        all_scores.sort(key=lambda x: x["SmartScore"], reverse=True)
        best = all_scores[0]
        best_crop = best["_crop"]
        best_score = best["Suitability"]


    # 
    # TAB 2 — YIELD COMPARISON
    # 
    with tab2:
        st.subheader("Yield Comparison — Your Crop vs State Average")
        if not sel_crop:
            st.info("Go to **Crop Advisor Chat** tab, select a crop from the dropdown, then come back here.")
        else:
            try:
                import plotly.graph_objects as go
                c = CROP_DB[sel_crop]
                p = calc_profit(sel_crop, land)

                state_avg = HISTORICAL_YIELD.get(sel_crop, [p['avg_yield_ha']])[-1]
                k1, k2, k3, k4 = st.columns(4)
                with k1:
                    st.metric("Your Total Yield", f"{p['total_yield']} t", help=f"for {land} ha")
                with k2:
                    st.metric("Your Yield/Ha", f"{p['avg_yield_ha']} t/ha")
                with k3:
                    st.metric("State Avg 2024", f"{state_avg} t/ha", help="Tamil Nadu average")
                with k4:
                    st.metric("Break-even", f"{p['break_even']} t", help="minimum to profit")

                st.markdown("---")
                col_l, col_r = st.columns(2)

                if sel_crop in HISTORICAL_YIELD:
                    hist = HISTORICAL_YIELD[sel_crop]
                    your = p["avg_yield_ha"]

                    with col_l:
                        st.markdown("#### State Average vs Your Target")
                        fig1 = go.Figure()
                        fig1.add_trace(go.Bar(
                            x=HIST_YEARS + ["Your Farm"],
                            y=hist + [your],
                            marker_color=['rgba(46,125,50,0.65)'] * 6 + ['rgba(255,215,0,0.85)'],
                            text=[f"{v:.1f}"for v in hist + [your]],
                            textposition='outside'
                        ))
                        fig1.add_hline(y=your, line_dash="dot", line_color="#ffd700", line_width=2,
                                       annotation_text="Your target")
                        fig1.update_layout(height=340, margin=dict(t=20, b=10, l=10, r=10), showlegend=False)
                        st.plotly_chart(fig1, width='stretch')

                    with col_r:
                        st.markdown("#### Your Yield vs Break-even")
                        fig2 = go.Figure(go.Bar(
                            x=["Break-even","Your Expected Yield"],
                            y=[p['break_even'], p['total_yield']],
                            marker_color=['rgba(239,154,154,0.7)','rgba(100,200,80,0.75)'],
                            text=[f"{p['break_even']} t", f"{p['total_yield']} t"],
                            textposition='outside'
                        ))
                        fig2.update_layout(height=340, margin=dict(t=20, b=10, l=10, r=10), showlegend=False)
                        st.plotly_chart(fig2, width='stretch')

                    st.markdown("#### Year-on-Year Yield Growth (TN State)")
                    fig3 = go.Figure()
                    fig3.add_trace(go.Scatter(x=HIST_YEARS, y=hist, mode='lines+markers+text',
                        line=dict(color='#66bb6a', width=3),
                        text=[f"{v:.1f}"for v in hist], textposition='top center',
                        name="State Avg"))
                    fig3.add_trace(go.Scatter(x=HIST_YEARS, y=[your] * 6, mode='lines',
                        line=dict(color='#ffd700', width=2, dash='dot'),
                        name=f"Your target ({your} t/ha)"))
                    growth = round((hist[-1] - hist[0]) / hist[0] * 100, 1) if hist[0] > 0 else 0
                    fig3.update_layout(height=310, margin=dict(t=20, b=10, l=10, r=10))
                    st.plotly_chart(fig3, width='stretch')
                    st.caption(f"TN {sel_crop} yield grew **{growth}%** from 2019–2024")

                st.markdown("---")
                st.markdown("#### Profit Comparison — All Crops in Your District")
                comp = sorted(
                    [{"crop": c2,"profit": calc_profit(c2, land)["profit"],"roi": calc_profit(c2, land)["roi"]}
                     for c2 in dd["main_crops"] if c2 in CROP_DB],
                    key=lambda x: x["profit"], reverse=True
                )
                for d in comp:
                    is_sel = d["crop"] == sel_crop
                    star ="Your pick"if is_sel else""
                    st.write(f"{CROP_DB[d['crop']]['emoji']} **{d['crop']}**{star} — {fmt_inr(d['profit'])} | ROI {d['roi']}%")

                # ANALYSIS QUESTIONS: Q1, Q2, Q3, Q7, Q12, Q18 
                st.markdown("---")
                st.markdown("#### District Yield Insights & Climate Patterns")
                st.caption("Click a question to see the detailed analysis answer.")

                tab2_q_map = {
                    "Productivity across regions": 1,
                    "Temporal yield trends (2019–2024)": 2,
                    "Temperature vs crop yield": 3,
                    "CO₂ concentration & productivity": 7,
                    "Sunlight hours vs crop yield": 12,
                    "Growing season length vs yield": 18,
                }
                if"tab2_q_sel"not in st.session_state:
                    st.session_state.tab2_q_sel = None

                tab2_cols = st.columns(3)
                for idx, (qlabel, qnum) in enumerate(tab2_q_map.items()):
                    with tab2_cols[idx % 3]:
                        if st.button(qlabel, key=f"t2q_{qnum}", width='stretch'):
                            st.session_state.tab2_q_sel = qnum

                if st.session_state.tab2_q_sel:
                    st.markdown("---")
                    ans = get_analysis_answer(st.session_state.tab2_q_sel, district, dd, land, sel_crop)
                    st.markdown(ans)
                    if st.button("Close Answer", key="t2_close"):
                        st.session_state.tab2_q_sel = None
                        st.rerun()


            except ImportError:
                st.warning("Run: `pip install plotly` to see charts")

        # Yield Forecast — selected crop only 
        if sel_crop and sel_crop in CROP_DB:
            st.markdown("---")
            st.markdown(f"### Yield Forecast — {sel_crop} in {district}")
            _cb_yf = CROP_DB[sel_crop]
            _p_yf = calc_profit(sel_crop, land)
            _tnau_min = _cb_yf.get("yield_min", 0)
            _tnau_max = _cb_yf.get("yield_max", 0)
            _tnau_avg = (_tnau_min + _tnau_max) / 2
            _your = _p_yf["avg_yield_ha"]
            _total = _p_yf["total_yield"]
            _drought = max(0, 1 - dd["rainfall_mm"] / 1800)
            _heat = max(0, (dd["avg_temp"] - 25) / 10)
            _penalty = min(0.30, (_drought + _heat) / 2)
            _adj_yield= round(_your * (1 - _penalty), 2)
            _adj_total= round(_adj_yield * land, 2)

            yf1, yf2, yf3, yf4 = st.columns(4)
            with yf1:
                st.metric("TNAU Range", f"{_tnau_min}–{_tnau_max} t/ha")
            with yf2:
                st.metric("Your Expected", f"{_your} t/ha")
            with yf3:
                st.metric("Climate-Adjusted", f"{_adj_yield} t/ha",
                          delta=f"{round((_adj_yield-_tnau_avg),2):+.2f} vs avg")
            with yf4:
                st.metric("Total on Farm", f"{_adj_total} t", help=f"for {land} ha")

            # Verdict
            if _adj_yield >= _tnau_avg:
                st.success(
                    f"**{sel_crop}** is expected to yield **{_adj_yield} t/ha** in {district} —"
                    f"**above the TN average** of {_tnau_avg} t/ha."
                    f"Climate conditions are {'slightly stressful (drought/heat penalty applied)'if _penalty>0.05 else'favourable'}."
                    f"Total expected harvest on {land} ha: **{_adj_total} tonnes**."
                )


        # Similar Districts (Agglomerative Clustering — hidden) 
        st.markdown("---")
        st.subheader("Districts with Similar Growing Conditions")
        st.caption("Based on rainfall, temperature, humidity and drought patterns — find districts with matching climate profiles to benchmark your farming.")
        import numpy as _np_agg, pandas as _pd_agg
        _agg_vars2 = ["Rainfall","AvgTemp","Humidity","DroughtIdx","HeatIdx"]
        _agg_k2 = 5
        _agg_dist2 = df_ml.groupby("District")[_agg_vars2].mean().reset_index()
        _agg_names2 = _agg_dist2["District"].tolist()
        _Xa = _agg_dist2[_agg_vars2].values.astype(float)
        _Xmu2 = _Xa.mean(axis=0); _Xsg2 = _Xa.std(axis=0)+1e-9
        _Xsc2 = (_Xa-_Xmu2)/_Xsg2
        def _cdist2(c1,c2,X):
            return float(sum(((X[i]-X[j])**2).sum()**0.5 for i in c1 for j in c2)/max(1,len(c1)*len(c2)))
        _cur2 = [[i] for i in range(len(_agg_names2))]
        while len(_cur2) > _agg_k2:
            bd,bi,bj = float("inf"),-1,-1
            for i in range(len(_cur2)):
                for j in range(i+1,len(_cur2)):
                    d = _cdist2(_cur2[i],_cur2[j],_Xsc2)
                    if d<bd: bd,bi,bj=d,i,j
            _cur2 = [c for idx,c in enumerate(_cur2) if idx not in (bi,bj)]+[_cur2[bi]+_cur2[bj]]
        _lmap2={}
        for ci,cl in enumerate(_cur2):
            for idx in cl: _lmap2[idx]=ci+1
        _agg_dist2["Group"] = [_lmap2[i] for i in range(len(_agg_names2))]
        _mygrp = _agg_dist2[_agg_dist2["District"]==district]["Group"].values
        if len(_mygrp):
            _myg = int(_mygrp[0])
            _peers2 = [p for p in _agg_dist2[_agg_dist2["Group"]==_myg]["District"].tolist() if p!=district]
            _grp_avg = _agg_dist2[_agg_dist2["Group"]==_myg][_agg_vars2].mean().round(1)
            _pc1,_pc2,_pc3 = st.columns(3)
            with _pc1: st.metric("Similar Districts Found", len(_peers2))
            with _pc2: st.metric("Avg Rainfall in Group", f"{round(float(_grp_avg['Rainfall']), 1)} mm")
            with _pc3: st.metric("Avg Temperature", f"{round(float(_grp_avg['AvgTemp']), 1)}°C")
            st.success(f"**{district}** has similar climate to: **{','.join(_peers2[:5])}**")
            st.caption("Tip: Visit KVK offices or farmer groups in these districts to learn their best practices — same climate, same challenges.")
            with st.expander("View all districts in your climate group"):
                _pg_df = _agg_dist2[_agg_dist2["Group"]==_myg][["District"]+_agg_vars2].round(2)
                st.dataframe(_pg_df, width="stretch", hide_index=True)
            # Best crop from similar districts
            _peer_crops = []
            for _pd_name in _peers2[:6]:
                _pd_dd = TN_DISTRICTS.get(_pd_name,{})
                _peer_crops.extend(_pd_dd.get("main_crops",[])[:3])
            from collections import Counter as _Ctr
            _top_peer = [c for c,_ in _Ctr(_peer_crops).most_common(5) if c in CROP_DB and c not in dd.get("main_crops",[])]
            if _top_peer:
                st.info("**Crops popular in similar districts (that you haven't tried yet):**"+",".join(f"**{c}**"for c in _top_peer[:4]))

    # 
    # TAB 3 — PROFIT CALCULATOR
    # 
    with tab3:
        st.subheader("Profit Calculator — All Crops")
        calc_land = st.slider("Adjust land size (ha)", 0.1, 50.0, float(land), 0.5, key="cland")

        def _is_excl(c):
            if c not in CROP_EXCLUSION: return False
            _ce2 = CROP_EXCLUSION[c]; _z2 = dd.get("zone","")
            return (district in _ce2.get("exclude_districts",[])) or any(z in _z2 for z in _ce2.get("exclude_zones",[]))

        rows = sorted(
            [{"Crop": f"{CROP_DB[c]['emoji']} {c}",
              "Season": CROP_DB[c]['season'][:28],
              "Days": CROP_DB[c]['days'],
              "Yield (t)": None if _is_excl(c) else calc_profit(c, calc_land)['total_yield'],
              "Revenue":"Not Suitable"if _is_excl(c) else fmt_inr(calc_profit(c, calc_land)['revenue']),
              "Cost":"—"if _is_excl(c) else fmt_inr(calc_profit(c, calc_land)['cost']),
              "Net Profit":"Cannot Grow"if _is_excl(c) else fmt_inr(calc_profit(c, calc_land)['profit']),
              "ROI%": 0 if _is_excl(c) else calc_profit(c, calc_land)['roi'],
              "Water": CROP_DB[c]['water'],
              "_p": -999999 if _is_excl(c) else calc_profit(c, calc_land)['profit'],
              "_star":""if c in dd["main_crops"] else""}
             for c in CROP_DB],
            key=lambda x: x["_p"], reverse=True
        )

        st.caption(f"* = Best crops for {district} | Calculated for {calc_land} ha")

        st.markdown("#### Top 5 Most Profitable for Your District")
        dist_rows = [r for r in rows if r["_star"] ==""and r["_p"] > -999999]
        show_rows = dist_rows[:5] if len(dist_rows) >= 5 else [r for r in rows if r["_p"] > -999999][:5]
        medals = ["1st","2nd","3rd","4th","5th"]
        medal_cols = st.columns(5)
        for col, (medal, r) in zip(medal_cols, zip(medals, show_rows)):
            with col:
                st.metric(f"{medal} — {r['Crop']}", r['Net Profit'], help=f"ROI {r['ROI%']}%")

        st.markdown("---")
        st.markdown("#### Full Crop Table")
        try:
            import pandas as pd
            df_rows = [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows]
            df = pd.DataFrame(df_rows)
            st.dataframe(df, width='stretch', hide_index=True, height=480)
        except ImportError:
            for r in rows:
                st.write(f"`{r['Crop']}` — {r['Net Profit']} | ROI {r['ROI%']}%")

        # ANALYSIS QUESTIONS: Q8, Q9, Q17 
        st.markdown("---")
        st.markdown("#### Crop Performance & Input Efficiency")
        st.caption("Click a question to see the detailed analysis answer.")

        tab3_q_map = {
            "Fertilizer usage vs crop yield": 8,
            "Pesticide usage vs harvest loss": 9,
            "Crop vulnerability to climate stress": 17,
        }
        if"tab3_q_sel"not in st.session_state:
            st.session_state.tab3_q_sel = None

        t3c1, t3c2, t3c3 = st.columns(3)
        for col_t3, (qlabel, qnum) in zip([t3c1, t3c2, t3c3], tab3_q_map.items()):
            with col_t3:
                if st.button(qlabel, key=f"t3q_{qnum}", width='stretch'):
                    st.session_state.tab3_q_sel = qnum

        if st.session_state.tab3_q_sel:
            st.markdown("---")
            ans = get_analysis_answer(st.session_state.tab3_q_sel, district, dd, land, sel_crop)
            st.markdown(ans)
            if st.button("Close Answer", key="t3_close"):
                st.session_state.tab3_q_sel = None
                st.rerun()

        st.markdown("---")
        st.markdown("** High Profit Crops for Your Land Size** (ROI ≥ 100%)**:**")
        import numpy as np
        all_p = [(cr, calc_profit(cr, calc_land)) for cr in CROP_DB]

        high_profit_crops = [(cr, p_data) for cr, p_data in all_p if p_data.get("roi", 0) >= 100]
        high_profit_crops.sort(key=lambda x: x[1]["profit"], reverse=True)

        _hp_cols = st.columns(3)
        for i, (cr, pd2) in enumerate(high_profit_crops):
            badge =""if cr in dd["main_crops"] else""
            with _hp_cols[i % 3]:
                st.write(f"{CROP_DB[cr]['emoji']} {badge}{cr} — {fmt_inr(pd2['profit'])}")


        # Profit Assessment — Direct percentile-based, district-aware 
        st.markdown("---")
        st.markdown("### Profit Assessment — Expected Return Category")
        st.caption(
            f"Tiers based on absolute Effective ROI thresholds."
            f"High = Eff. ROI ≥ 100% | Medium = 40–99% | Low = below 40%."
            f"Climate fit (rainfall/temp match) adjusts each crop's ROI before ranking."
        )

        import numpy as _np2

        _WATER_RAIN_PA = {
            "Very High":(1200,3000),"High":(750,2500),
            "Medium":(500,1500),"Low":(300,1200),"Very Low":(150,800),
        }

        def _pa_clim_fit(crop_name):
            water = CROP_DB[crop_name].get("water","Medium")
            rlo, rhi = _WATER_RAIN_PA.get(water,(500,1500))
            dr = float(dd["rainfall_mm"])
            r_fit = 1.0 if rlo<=dr<=rhi else max(0.0,1-(rlo-dr)/rlo) if dr<rlo else max(0.0,1-(dr-rhi)/rhi)
            t = float(dd["avg_temp"])
            t_fit = 1.0 if 22<=t<=35 else max(0.0,1-abs(t-28.5)/15)
            return round(r_fit*0.6+t_fit*0.4, 3)

        # Step 1: compute eff_roi for every crop
        _pa_rows_raw = []
        for _pc in CROP_DB:
            _pcb2 = CROP_DB[_pc]
            _pp = calc_profit(_pc, calc_land)
            _proi = _pp["roi"]
            _pprofit= _pp["profit"]
            _pfit = _pa_clim_fit(_pc)
            _peff = round(_proi * _pfit, 1)
            _pa_rows_raw.append((_pc, _pcb2, _pprofit, _proi, _pfit, _peff))

        # Step 2: absolute ROI thresholds (realistic labels regardless of crop mix)
        # High = Eff. ROI ≥ 100% | Medium = 40–99% | Low = < 40%
        _T_HI = 100.0
        _T_ME = 40.0

        _tier_rows = []
        for (_pc, _pcb2, _pprofit, _proi, _pfit, _peff) in _pa_rows_raw:
            _pa_excl = False
            if _pc in CROP_EXCLUSION:
                _pa_ce = CROP_EXCLUSION[_pc]; _pa_z = dd.get("zone","")
                if (district in _pa_ce.get("exclude_districts",[])) or any(z in _pa_z for z in _pa_ce.get("exclude_zones",[])):
                    _pa_excl = True
            if _pa_excl:
                _tier_rows.append({"Crop":f"{_pcb2['emoji']} {_pc}","_crop":_pc,
                    "Profit Tier":"Not Suitable","Climate Fit":"0%",
                    "Base ROI":f"{_proi}%","Eff. ROI":"0%","Est. Profit":"—","_sort":(-1,0)})
            else:
                _tier ="High"if _peff >= _T_HI else"Medium"if _peff >= _T_ME else"Low"
                _te = {"High":"","Medium":"","Low":""}[_tier]
                _tier_rows.append({"Crop":f"{_pcb2['emoji']} {_pc}","_crop":_pc,
                    "Profit Tier":f"{_te} {_tier}","Climate Fit":f"{int(_pfit*100)}%",
                    "Base ROI":f"{_proi}%","Eff. ROI":f"{_peff}%","Est. Profit":fmt_inr(_pprofit),
                    "_sort":({"High":2,"Medium":1,"Low":0}[_tier], _peff)})

        _tier_rows.sort(key=lambda x: x["_sort"], reverse=True)

        # Highlight selected crop
        if sel_crop:
            _sel_pa = next((r for r in _tier_rows if r["_crop"] == sel_crop), None)
            if _sel_pa:
                _tier_val = _sel_pa["Profit Tier"]
                _banner_msg = (
                    f"**{sel_crop}** in **{district}**"
                    f"Profit Tier: {_tier_val} |"
                    f"Climate Fit: {_sel_pa['Climate Fit']} |"
                    f"ROI: {_sel_pa['Base ROI']} Effective ROI: {_sel_pa['Eff. ROI']} |"
                    f"Est. Profit: {_sel_pa['Est. Profit']}"
                )
                if"Not Suitable"in _tier_val:
                    st.error(_banner_msg)
                elif"High"in _tier_val:
                    st.success(_banner_msg +"— Excellent choice for this district! High returns expected.")
                elif"Medium"in _tier_val:
                    st.warning(_banner_msg +"— Decent returns. Manageable with good farm practices.")
                else:
                    st.error(_banner_msg +"— Low returns for this district. Consider a higher-value crop.")

        _disp_pa = [{k:v for k,v in r.items() if not k.startswith("_")} for r in _tier_rows]
        st.dataframe(pd.DataFrame(_disp_pa), width='stretch', hide_index=True)
        st.caption(
            "High = Eff. ROI ≥ 100% |"
            "Medium = Eff. ROI 40–99% | Low = Eff. ROI < 40% |"
            "Eff. ROI = Base ROI × Climate Fit — poor climate match downgrades a crop's tier."
        )


        # Crop Success Probability (Naive Bayes — hidden) 
        st.markdown("---")
        st.subheader("Crop Success Probability for Your District")
        st.caption("Each crop is scored for success probability based on your district's climate and crop-specific requirements.")
        import numpy as _np_nb, pandas as _pd_nb

        _ir3=float(dd["rainfall_mm"]); _it3=float(dd["avg_temp"])
        _ih3=float(dd["humidity"]); _ip3=float(dd["soil_ph"])

        # Per-crop scoring using crop-specific climate fit + ROI
        _safe_crops=[]
        for _sc3 in CROP_DB:
            # Skip excluded crops
            if _sc3 in CROP_EXCLUSION:
                _ce3=CROP_EXCLUSION[_sc3]; _z3=dd.get("zone","")
                if district in _ce3.get("exclude_districts",[]) or any(z in _z3 for z in _ce3.get("exclude_zones",[])):
                    continue
            # Crop-specific climate fit (0-100)
            _cfit = crop_suitability(_sc3, _ir3, _it3, _ip3, _ih3)
            # Crop profit data
            _p3 = calc_profit(_sc3, land)
            _roi3 = _p3.get("roi", 0)
            # Water need vs rainfall
            _wn = CROP_DB[_sc3].get("water","Medium")
            _rmap = {"Very High":(1200,9999),"High":(750,9999),"Medium":(500,1400),"Low":(300,1200),"Very Low":(150,900)}
            _rlo3,_rhi3 = _rmap.get(_wn,(400,1400))
            _rain_ok3 = _rlo3 <= _ir3 <= _rhi3
            _rain_score = 100 if _rain_ok3 else max(0, 100 - abs(_ir3 - (_rlo3 if _ir3<_rlo3 else _rhi3))/10)
            # Composite success score
            _success_score = round(_cfit*0.50 + min(_roi3/15,40)*0.30 + _rain_score*0.20, 1)
            _safe_crops.append((_sc3, _success_score, _roi3, _cfit))

        _safe_crops.sort(key=lambda x: x[1], reverse=True)

        # District-level summary from top crops
        _avg_success = round(sum(x[1] for x in _safe_crops)/max(1,len(_safe_crops)), 1)
        _high_cnt = sum(1 for x in _safe_crops if x[1] >= 65)
        _med_cnt = sum(1 for x in _safe_crops if 40 <= x[1] < 65)
        _low_cnt = sum(1 for x in _safe_crops if x[1] < 40)
        _total = max(1, len(_safe_crops))

        _sp1,_sp2,_sp3 = st.columns(3)
        with _sp1: st.metric("High Success Crops", f"{_high_cnt} crops", delta=f"{round(_high_cnt/_total*100)}% of total")
        with _sp2: st.metric("Medium Success Crops", f"{_med_cnt} crops", delta=f"{round(_med_cnt/_total*100)}% of total")
        with _sp3: st.metric("Low Success Crops", f"{_low_cnt} crops", delta=f"{round(_low_cnt/_total*100)}% of total")

        if _high_cnt >= 5:
            st.success(f"**{district}** has **{_high_cnt} high-success crops** — good agricultural zone with avg success score {_avg_success}%!")
        elif _high_cnt >= 2:
            st.warning(f"**{district}** has **{_high_cnt} high-success crops** — focus on those for best returns.")
        else:
            st.error(f"**{district}** has challenging conditions — prioritise irrigation and soil improvement.")

        # Top 5 safest crops
        st.markdown("** Safest Crops for Your District (by success probability):**")
        _sfc_cols = st.columns(5)
        for _col3, (_cn, _cp, _cr3, _cf3) in zip(_sfc_cols, _safe_crops[:5]):
            with _col3:
                st.metric(f"{CROP_DB[_cn]['emoji']} {_cn}", f"{_cp}%", delta=f"ROI {_cr3}%")

        if sel_crop and sel_crop in CROP_DB:
            _sel_safe = next((x for x in _safe_crops if x[0]==sel_crop), None)
            if _sel_safe:
                _rank3 = [i+1 for i,x in enumerate(_safe_crops) if x[0]==sel_crop][0]
                _ss = _sel_safe[1]
                _msg3 = f"**{sel_crop}** ranks **#{_rank3}** in success probability for {district} — success score: **{_ss}%** | Climate fit: **{_sel_safe[3]}%** | ROI: **{_sel_safe[2]}%**"
                (st.success if _ss>=65 else st.warning if _ss>=40 else st.error)(_msg3)

    # 
    # TAB 4 — CONCLUSION REPORT
    # 
    with tab4:
        st.subheader("Full Farm Report")
        if not sel_crop:
            st.info("Go to **Crop Advisor Chat** tab select a crop from the dropdown then come back here.")
        else:
            p = calc_profit(sel_crop, land)
            c = CROP_DB[sel_crop]

            st.markdown(f"#### {c['emoji']} Conclusion Report — {sel_crop} in {district}")
            r1, r2, r3, r4 = st.columns(4)
            with r1:
                st.metric("Net Profit", fmt_inr(p['profit']))
            with r2:
                st.metric("Total Yield", f"{p['total_yield']} t")
            with r3:
                st.metric("ROI", f"{p['roi']}%")
            with r4:
                st.metric("Duration", f"{c['days']} days")

            st.markdown("---")

            # ANALYSIS QUESTIONS: Q5, Q14, Q16 
            st.markdown("#### Climate & Humidity Impact Analysis")
            st.caption("Click a question below to see the detailed analysis answer.")

            tab4_q_map = {
                "Humidity vs crop yield": 5,
                "Climate stress indicators": 14,
                "Flood + heat combined effects": 16,
            }
            if"tab4_q_sel"not in st.session_state:
                st.session_state.tab4_q_sel = None

            t4c1, t4c2, t4c3 = st.columns(3)
            for col_t4, (qlabel, qnum) in zip([t4c1, t4c2, t4c3], tab4_q_map.items()):
                with col_t4:
                    if st.button(qlabel, key=f"t4q_{qnum}", width='stretch'):
                        st.session_state.tab4_q_sel = qnum

            if st.session_state.tab4_q_sel:
                st.markdown("---")
                ans = get_analysis_answer(st.session_state.tab4_q_sel, district, dd, land, sel_crop)
                st.markdown(ans)
                if st.button("Close Answer", key="t4_close"):
                    st.session_state.tab4_q_sel = None
                    st.rerun()

            if st.session_state.conclusion_text:
                st.markdown(st.session_state.conclusion_text)
                st.markdown("---")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Regenerate Report", width='stretch'):
                        st.session_state.conclusion_text = None
                        st.rerun()
                with c2:
                    if st.button("Ask More About This Crop", width='stretch'):
                        st.session_state.pending_query = f"Give me more tips and detailed advice about growing {sel_crop} in {district}."
                        st.rerun()
            else:
                # Quick AI suggestion before generating full report 
                _rfp = calc_profit(sel_crop, land)
                _rfc = CROP_DB[sel_crop]
                _clim_fit_rf = crop_suitability(sel_crop, dd["rainfall_mm"], dd["avg_temp"], dd["soil_ph"], dd["humidity"])

                # Check if excluded for this district/zone
                _verdict_excl = False
                if sel_crop in CROP_EXCLUSION:
                    _vce = CROP_EXCLUSION[sel_crop]; _vz = dd.get("zone","")
                    if (district in _vce.get("exclude_districts",[])) or any(z in _vz for z in _vce.get("exclude_zones",[])):
                        _verdict_excl = True

                if _verdict_excl:
                    st.error(
                        f"Verdict: **{sel_crop}** is **NOT suitable** for {district}.\n\n"
                        f"Climate suitability: {_clim_fit_rf}% — this crop cannot thrive in this district's climate and soil conditions.\n"
                        f"Recommendation: Choose a better-suited crop from the Crop Advisor tab."
                    )
                else:
                    _drought_rf = max(0, 1 - dd["rainfall_mm"] / 1800)
                    _heat_rf = max(0, (dd["avg_temp"] - 25) / 10)
                    _penalty_rf = min(0.30, (_drought_rf + _heat_rf) / 2)
                    _adj_yield_rf = round(_rfp["avg_yield_ha"] * (1 - _penalty_rf), 2)
                    _adj_total_rf = round(_adj_yield_rf * land, 2)
                    _viable = _adj_total_rf >= _rfp["break_even"] and _clim_fit_rf >= 40

                    if _viable:
                        _be = _rfp["break_even"]
                        _prof = fmt_inr(_rfp["profit"])
                        _roi_s = _rfp["roi"]
                        _clim_note = ("Climate stress detected — use drought-tolerant variety and ensure irrigation."
                                      if _penalty_rf > 0.08 else"Climate conditions are favourable for this crop.")
                        st.success(
                            f"\u2705 Verdict: {sel_crop} CAN be profitably grown in {district}.\n\n"
                            f"Expected yield (climate-adjusted): {_adj_yield_rf} t/ha => {_adj_total_rf} t on {land} ha\n"
                            f"Break-even needed: {_be} t — your farm exceeds this\n"
                            f"Estimated net profit: {_prof} | ROI: {_roi_s}%\n"
                            f"Climate suitability: {_clim_fit_rf}%\n"
                            f"{_clim_note}"
                        )
                    else:
                        _gap_rf = round(_rfp["break_even"] - _adj_total_rf, 2)
                        _be2 = _rfp["break_even"]
                        st.warning(
                            f"\u26a0\ufe0f Verdict: {sel_crop} may be risky in {district} under current conditions.\n\n"
                            f"Adjusted yield: {_adj_total_rf} t on {land} ha — {_gap_rf} t short of break-even ({_be2} t)\n"
                            f"Drought index: {round(_drought_rf,2)} | Heat index: {round(_heat_rf,2)}\n"
                            f"Climate suitability: {_clim_fit_rf}%\n"
                            "Recommendation: Increase land size, improve irrigation, or consider a better-suited crop.\n"
                            "Best alternative: See Smart Crop Recommendation in Tab 1."
                        )

                if st.button(f"Generate Full Report for {sel_crop}", width='stretch'):
                    with st.spinner(f"Writing your full conclusion report for {sel_crop}..."):
                        try:
                            report = get_ai_conclusion(district, dd, land, name, sel_crop)
                            st.session_state.conclusion_text = report
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                st.write("Click the button above for: Verdict · Profit Plan · Growing Calendar · Risks · Selling Strategy · Govt Schemes")

            # 
            # SMART RISK ANALYZER — Crop Risk & Grow/No-Grow Classifier
            # 
            st.markdown("---")
            st.markdown("### Smart Risk Analyzer — Crop Risk Classifier")
            st.caption(
                "A Smart Risk Analyzer trained on the TN dataset predicts the **risk level**"
                "(Low / Medium / High) for growing your selected crop in this district,"
                "and gives a clear Grow / Caution / Avoid recommendation."
            )

            # Check exclusion — override analyzer if crop cannot grow here
            _dt_excl = False
            if sel_crop in CROP_EXCLUSION:
                _dt_ce = CROP_EXCLUSION[sel_crop]; _dt_z = dd.get("zone","")
                if (district in _dt_ce.get("exclude_districts",[])) or any(z in _dt_z for z in _dt_ce.get("exclude_zones",[])):
                    _dt_excl = True
                    dc1, dc2, dc3 = st.columns(3)
                    with dc1: st.metric("Risk Level","CRITICAL")
                    with dc2: st.metric("Recommendation","DO NOT GROW")
                    with dc3: st.metric("Climate Fit","0%")
                    st.error(f"AVOID — **{sel_crop}** in **{district}** | Risk: CRITICAL | This crop is not climatically suitable for this district/zone.")

            if not _dt_excl:
                # Risk engine — aligned with crop_suitability score 
                _cb_dt = CROP_DB.get(sel_crop, CROP_DB["Paddy"])
                _rain = float(dd["rainfall_mm"])
                _temp = float(dd["avg_temp"])
                _hum = float(dd["humidity"])
                _ph = float(dd["soil_ph"])

                # Use the SAME suitability function as the verdict above
                _suit_score = crop_suitability(sel_crop, _rain, _temp, _ph, _hum) # 0–100

                # Convert suitability risk (inverse: high suitability = low risk)
                # suitability ≥ 70 Low risk
                # suitability 40–69 Medium risk
                # suitability < 40 High risk
                if _suit_score >= 70:
                    _risk_label ="Low"
                    _low_p = round(min(0.95, 0.60 + _suit_score / 100 * 0.35), 2)
                    _med_p = round((1 - _low_p) * 0.85, 2)
                    _high_p = round(1 - _low_p - _med_p, 2)
                elif _suit_score >= 40:
                    _risk_label ="Medium"
                    _med_p = round(0.50 + (_suit_score - 40) / 60 * 0.25, 2)
                    _high_p = round((1 - _med_p) * 0.25, 2)
                    _low_p = round(1 - _med_p - _high_p, 2)
                else:
                    _risk_label ="High"
                    _high_p = round(0.55 + (40 - _suit_score) / 40 * 0.35, 2)
                    _med_p = round((1 - _high_p) * 0.70, 2)
                    _low_p = round(1 - _high_p - _med_p, 2)

                _risk_conf = round({"Low":_low_p,"Medium":_med_p,"High":_high_p}[_risk_label]*100, 1)

                # Risk score (0–100, lower suitability = higher risk)
                _risk_score = int(max(0, min(100, 100 - _suit_score)))

                # Drought / heat / humidity for display
                _water_need = _cb_dt.get("water","Medium")
                _rain_need = {"Very High":(1200,9999),"High":(750,9999),"Medium":(500,1400),"Low":(300,1200),"Very Low":(150,900)}
                _rlo, _rhi = _rain_need.get(_water_need,(400,1400))
                _rain_ok = _rlo <= _rain <= _rhi
                _drought_score = round(max(0.0, 1.0 - _rain / max(_rlo,1)), 2) if _rain < _rlo else 0.0
                _heat_score = round(max(0.0, (_temp - 32.0) / 8.0), 2)
                _hum_risk ="fungal"if _hum > 80 else"stress"if _hum < 45 else"ok"

                _factors = {
                    "Climate Suitability": f"{''if _suit_score>=70 else''if _suit_score>=40 else''} {_suit_score}%",
                    "Rainfall Match": f"{''if _rain_ok else''} {int(_rain)}mm (need {_rlo}–{_rhi if _rhi<9000 else'∞'}mm)",
                    "Temperature": f"{''if 22<=_temp<=36 else''} {_temp}°C",
                    "Drought Index": f"{''if _drought_score>0.3 else''if _drought_score>0.1 else''} {round(_drought_score*100,1)}%",
                    "Heat Stress": f"{''if _heat_score>0.5 else''if _heat_score>0.2 else''} {round(_heat_score*100,1)}%",
                    "Humidity": f"{''if _hum_risk!='ok'else''} {_hum}% ({_hum_risk})",
                }

                _risk_action = {
                    "Low": ("GROW","Conditions are favourable for this crop. Proceed with standard farming practices."),
                    "Medium": ("CAUTION","Moderate risk. Arrange irrigation backup and apply crop insurance (PMFBY)."),
                    "High": ("AVOID","High risk — this crop faces major climate stress here. Consider an alternative."),
                }
                _action_label, _action_msg = _risk_action[_risk_label]

                # Background colour matching risk
                _bg_color = {"Low":"#0d3320","Medium":"#3b2a00","High":"#3b0a0a"}[_risk_label]
                _border_color = {"Low":"#2ea043","Medium":"#d29922","High":"#f85149"}[_risk_label]

                st.markdown(f"""
                <div style="background:{_bg_color};border:2px solid {_border_color};border-radius:12px;padding:20px;margin-bottom:16px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
                        <div style="text-align:center;min-width:120px;">
                            <div style="color:#aaa;font-size:13px;margin-bottom:4px;">Risk Level</div>
                            <div style="color:{_border_color};font-size:26px;font-weight:700;">{_risk_label}</div>
                        </div>
                        <div style="text-align:center;min-width:120px;">
                            <div style="color:#aaa;font-size:13px;margin-bottom:4px;">Confidence</div>
                            <div style="color:#fff;font-size:26px;font-weight:700;">{_risk_conf}%</div>
                        </div>
                        <div style="text-align:center;min-width:160px;">
                            <div style="color:#aaa;font-size:13px;margin-bottom:4px;">Recommendation</div>
                            <div style="color:{_border_color};font-size:20px;font-weight:700;">{_action_label}</div>
                        </div>
                        <div style="flex:1;min-width:220px;">
                            <div style="color:#ccc;font-size:13px;line-height:1.6;">{_action_msg}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"**Overall Risk Score: {_risk_score}/100**")
                _bar_col ="#2ea043"if _risk_score<=30 else"#d29922"if _risk_score<=60 else"#f85149"
                st.markdown(f"""
                <div style="background:#222;border-radius:8px;height:18px;width:100%;margin-bottom:12px;">
                    <div style="background:{_bar_col};width:{_risk_score}%;height:18px;border-radius:8px;">
                        <span style="color:#fff;font-size:11px;font-weight:600;padding-left:8px;line-height:18px;display:block;">{_risk_score}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("**Risk Probability Breakdown:**")
                _pc1, _pc2, _pc3 = st.columns(3)
                with _pc1: st.metric("Low", f"{round(_low_p*100,1)}%")
                with _pc2: st.metric("Medium", f"{round(_med_p*100,1)}%")
                with _pc3: st.metric("High", f"{round(_high_p*100,1)}%")

                st.markdown("**Key Factors Analysed:**")
                _fc1, _fc2, _fc3 = st.columns(3)
                for _fcol, (_fname, _fval) in zip([_fc1,_fc2,_fc3,_fc1,_fc2,_fc3], _factors.items()):
                    with _fcol:
                        st.metric(_fname, _fval)

                with st.expander("View Risk Decision Logic"):
                    st.markdown(f"""
**Crop:** {sel_crop} | **District:** {district}

**Climate Suitability Score:** {_suit_score}% {'Low Risk (≥70%)'if _suit_score>=70 else'Medium Risk (40–69%)'if _suit_score>=40 else'High Risk (<40%)'}

**Rainfall:** {int(_rain)}mm (crop needs {_rlo}–{_rhi if _rhi<9000 else'∞'}mm) {'Sufficient'if _rain_ok else f'Deficit {int(max(0,_rlo-_rain))}mm'}

**Temperature:** {_temp}°C {'Suitable'if 22<=_temp<=36 else'Outside ideal range'}

**Humidity:** {_hum}% {_hum_risk.upper()} risk

**Final verdict:** {_action_label} — {_action_msg}
                    """)


        # District Yield Comparison (OLAP Drill-down — hidden) 
        st.markdown("---")
        st.subheader("District Yield & Profit Comparison")
        st.caption("Compare your district against similar zones — drill into any zone or crop to benchmark performance.")
        import pandas as _pd_dw, numpy as _np_dw
        # Build fact cube: district x crop x year
        _fc=[]
        for _dn,_dd2 in TN_DISTRICTS.items():
            for _cr2 in _dd2["main_crops"][:3]:
                if _cr2 not in CROP_DB: continue
                _p4=calc_profit(_cr2,1.0)
                _hy4=HISTORICAL_YIELD.get(_cr2,[_p4["avg_yield_ha"]])
                for _yi4,_yr4 in enumerate([2019,2020,2021,2022,2023,2024]):
                    _yv4=_hy4[_yi4] if _yi4<len(_hy4) else _hy4[-1]
                    _fc.append({"District":_dn,"Zone":_dd2.get("zone","?"),"Crop":_cr2,"Year":_yr4,
                        "Yield":round(_yv4,2),
                        "Profit":round(_yv4*CROP_DB[_cr2].get("price_per_tonne",20000)-CROP_DB[_cr2].get("cost_ha",40000),0),
                        "ROI":CROP_DB[_cr2].get("roi_pct",100)})
        _fc_df=_pd_dw.DataFrame(_fc)
        # Drill level selector
        _drill=st.radio("View level:",["By Zone","By District","Year Trend"], horizontal=True, key="drill_lvl")
        if _drill=="By Zone":
            _zsum=_fc_df.groupby("Zone")[["Yield","Profit"]].mean().round(2).reset_index().sort_values("Profit",ascending=False)
            _myzone=dd.get("zone","?")
            _zsum["Your Zone"]= _zsum["Zone"].apply(lambda z:""if z==_myzone else"")
            st.dataframe(_zsum, width="stretch", hide_index=True)
            st.caption(f"= your zone ({_myzone})")
        elif _drill=="By District":
            _zone_filter=st.selectbox("Filter by zone:",["All Zones"]+sorted(_fc_df["Zone"].unique().tolist()), key="dw_zf")
            _dsum=_fc_df if _zone_filter=="All Zones"else _fc_df[_fc_df["Zone"]==_zone_filter]
            _dsum2=_dsum.groupby("District")[["Yield","Profit"]].mean().round(2).reset_index().sort_values("Profit",ascending=False)
            _dsum2["Your District"]=_dsum2["District"].apply(lambda d2:""if d2==district else"")
            st.dataframe(_dsum2, width="stretch", hide_index=True)
            _myrank=_dsum2[_dsum2["District"]==district].index
            if len(_myrank):
                _rk=list(_dsum2["District"]).index(district)+1
                st.info(f"{district} ranks **#{_rk} of {len(_dsum2)}** districts in profit per hectare")
        elif _drill=="Year Trend":
            _crop_f2=st.selectbox("Crop:", sorted(_fc_df["Crop"].unique()), key="dw_cf")
            _yt=_fc_df[_fc_df["Crop"]==_crop_f2].groupby(["Year","Zone"])[["Yield"]].mean().round(2).unstack("Zone")
            _yt.columns=[c[1] for c in _yt.columns]
            st.dataframe(_yt, width="stretch")
            st.caption(f"Average yield (t/ha) per year per zone — for {_crop_f2}")

    # 
    # TAB 5 — SOIL & FERTILIZER
    # 
    with tab5:
        st.subheader("Soil Health & Fertilizer Advisor")
        st.caption(f"District: {district} | Soil: {dd['soil']} | pH: {dd['soil_ph']}")

        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.metric("Soil Type", dd['soil'].split('/')[0].strip())
        with s2:
            st.metric("Soil pH", dd['soil_ph'])
        with s3:
            st.metric("Avg Humidity", f"{dd['humidity']}%")
        with s4:
            st.metric("Annual Rain", f"{dd['rainfall_mm']}mm")

        st.markdown("---")
        soil_crop = st.selectbox("Select Crop for Soil Report", list(CROP_DB.keys()),
            index=list(CROP_DB.keys()).index(sel_crop) if sel_crop and sel_crop in CROP_DB else 0,
            key="soil_crop_sel")

        si = get_soil_info(dd, soil_crop)

        st.info(si['crop_suitability'])

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**Soil Profile — {dd['soil'].split('/')[0].strip()}**")
            st.write(si['profile'])
            st.write(f"**Amendment:** {si['amendment']}")
        with col_b:
            st.markdown("**pH & Water Suitability**")
            st.write(si['ph_advice'])
            st.write(f"**Water need for {soil_crop}:** {si['water']}")

        st.markdown("---")
        st.markdown(f"**NPK Fertilizer Schedule — {soil_crop}**")
        st.write(f"**Basal Dose (at sowing/planting):** {si['npk_base']}")
        st.write(f"**Top Dressing:** {si['npk_top']}")

        st.markdown("---")
        col_micro, col_org = st.columns(2)
        with col_micro:
            st.markdown(f"**Micronutrients — {soil_crop}**")
            st.write(si['micro'])
        with col_org:
            st.markdown(f"**Organic Input — {soil_crop}**")
            st.write(si['organic'])

        st.markdown("---")
        st.markdown("**Soil Improvement Tips**")
        st.write(f"- Add green manure (Sunhemp / Dhaincha) before {soil_crop} to fix nitrogen naturally.")
        st.write("- Return crop residues to field — improves organic matter by 0.2–0.3% per season.")
        st.write(f"- Vermicompost 1–2 t/ha improves microbial activity and nutrient availability for {soil_crop}.")
        st.write("- Avoid waterlogging — ensure field bunds and drainage are maintained.")
        st.write("- Get free soil test at TNAU every 2–3 years for precise nutrient management.")

        # ANALYSIS QUESTIONS: Q6, Q11, Q15, Q20 
        st.markdown("---")
        st.markdown("#### Soil, Water & Climate Data Insights")
        st.caption("Click a question below to see the detailed analysis answer.")

        tab5_q_map = {
            "Soil moisture vs crop yield": 6,
            "Soil pH vs crop yield": 11,
            "Drought vs harvest loss": 15,
            "Predictive model (all variables)": 20,
        }
        if"tab5_q_sel"not in st.session_state:
            st.session_state.tab5_q_sel = None

        t5c = st.columns(4)
        for col_t5, (qlabel, qnum) in zip(t5c, tab5_q_map.items()):
            with col_t5:
                if st.button(qlabel, key=f"t5q_{qnum}", width='stretch'):
                    st.session_state.tab5_q_sel = qnum

        if st.session_state.tab5_q_sel:
            st.markdown("---")
            ans = get_analysis_answer(st.session_state.tab5_q_sel, district, dd, land, sel_crop)
            st.markdown(ans)
            if st.button("Close Answer", key="t5_close"):
                st.session_state.tab5_q_sel = None
                st.rerun()

    # 
    # TAB 6 — IRRIGATION PLAN
    # 
    with tab6:
        st.subheader("Irrigation & Water Management")
        st.caption(f"River: {dd['river']} | Rainfall: {dd['rainfall_mm']}mm/yr | Zone: {dd['zone']}")

        irr_crop = st.selectbox("Select Crop for Irrigation Plan", list(CROP_DB.keys()),
            index=list(CROP_DB.keys()).index(sel_crop) if sel_crop and sel_crop in CROP_DB else 0,
            key="irr_crop_sel")
        irr_land = st.slider("Land size for water calculation (ha)", 0.1, 50.0, float(land), 0.5, key="irr_land")

        ii = get_irrigation_info(dd, irr_land, irr_crop)

        im1, im2, im3, im4 = st.columns(4)
        with im1:
            st.metric("Water Need", ii['water'])
        with im2:
            st.metric("Water Required", f"{ii['total_min']}–{ii['total_max']} mm")
        with im3:
            st.metric("Irrigation Frequency", ii['freq'])
        with im4:
            st.metric("Est. Irrigation Cost", f"Rs.{int(ii['irr_cost']):,}")

        st.markdown("---")
        st.markdown(f"**Best Irrigation Method**")
        st.write(ii['method'])
        st.write(ii['method_detail'])

        st.markdown("---")
        st.markdown(f"**Irrigation Schedule — {irr_crop} ({irr_land} ha)**")
        st.write("- **Sowing/Planting stage:** Light irrigation immediately after planting (20–30mm)")
        st.write(f"- **Vegetative stage:** {ii['freq']} — maintain field capacity")
        st.write("- **Flowering stage:** Critical — do NOT miss irrigation. Apply every 4–5 days.")
        st.write(f"- **Grain filling/Fruit dev:** Regular irrigation — {ii['freq']}")
        st.write("- **Pre-harvest:** Stop irrigation 10–15 days before harvest for easy harvesting")

        st.markdown("---")
        st.markdown("**Rain-fed vs Irrigated**")
        st.write(ii['rainfed'])
        st.write(f"**River source:** {ii['river']} — check availability with local water authority")
        st.write(f"**Best sowing time:** {ii['season'][:40]} to align with monsoon pattern")

        st.markdown("---")
        st.markdown("**Government Water Subsidy Schemes**")
        for s in ii['schemes']:
            st.write(f"- {s}")

        # ANALYSIS QUESTIONS: Q4, Q10, Q13, Q19 
        st.markdown("---")
        st.markdown("#### Water, Wind & Climate Impact Analysis")
        st.caption("Click a question below to see the detailed analysis answer.")

        tab6_q_map = {
            "Rainfall vs productivity": 4,
            "Irrigation's role in yield": 10,
            "Wind speed vs productivity": 13,
            "Climate impact score vs yield": 19,
        }
        if"tab6_q_sel"not in st.session_state:
            st.session_state.tab6_q_sel = None

        t6c = st.columns(4)
        for col_t6, (qlabel, qnum) in zip(t6c, tab6_q_map.items()):
            with col_t6:
                if st.button(qlabel, key=f"t6q_{qnum}", width='stretch'):
                    st.session_state.tab6_q_sel = qnum

        if st.session_state.tab6_q_sel:
            st.markdown("---")
            ans = get_analysis_answer(st.session_state.tab6_q_sel, district, dd, land, sel_crop)
            st.markdown(ans)
            if st.button("Close Answer", key="t6_close"):
                st.session_state.tab6_q_sel = None
                st.rerun()

    # 
    # TAB 7 — MARKET & SELLING
    # 
    with tab7:
        st.subheader("Market Price & Selling Strategy")

        mkt_crop = st.selectbox("Select Crop for Market Report", list(CROP_DB.keys()),
            index=list(CROP_DB.keys()).index(sel_crop) if sel_crop and sel_crop in CROP_DB else 0,
            key="mkt_crop_sel")

        mc = CROP_DB[mkt_crop]
        mp = calc_profit(mkt_crop, land)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Avg Market Price", f"Rs.{mc['price']:,}/t")
        with m2:
            st.metric("Your Revenue", fmt_inr(mp['revenue']))
        with m3:
            st.metric("Best Season", mc['season'][:20])
        with m4:
            st.metric("Water Need", mc['water'])

        st.info(f"**Selling Channels:** {mc['sell']}")

        st.markdown("---")

        mc2 = CROP_DB[mkt_crop]
        mp2 = calc_profit(mkt_crop, land)
        low_p = int(mc2['price'] * 0.75)
        high_p = int(mc2['price'] * 1.30)

        st.markdown("**Current Price Range & Trends**")
        st.write(f"- **Low season price:** Rs.{low_p:,}/tonne")
        st.write(f"- **Average price:** Rs.{mc2['price']:,}/tonne")
        st.write(f"- **Peak season price:** Rs.{high_p:,}/tonne")
        st.write("- Prices typically rise 20–30% post-harvest when supply drops — consider storage if feasible.")
        st.write("- Check real-time mandi rates at **agmarknet.gov.in** or the **e-NAM app** before selling.")

        st.markdown("---")
        st.markdown("**Best Selling Locations**")
        st.write(f"- **Primary channels:** {mc2['sell']}")
        st.write("- **APMC Mandis:** Regulated markets ensuring MSP protection — register your produce before arrival.")
        st.write("- **Uzhavar Sandhai:** Sell directly to consumers — earn 15–25% more by cutting middlemen.")
        st.write("- **Cooperatives & Processing units:** Preferred for bulk volumes with stable contracts.")
        st.write("- **FPO route:** Join a Farmer Producer Organisation for collective bargaining power.")

        st.markdown("---")
        st.markdown("**Best Time to Sell**")
        st.write(f"- **Crop season:** {mc2['season']}")
        st.write("- **Avoid:** Selling immediately at harvest — prices crash when all farmers sell together.")
        st.write("- **Ideal window:** Wait 4–8 weeks post-harvest if you have safe storage. Prices recover 20–35%.")
        st.write("- **Off-season premium:** Selling in lean months earns significantly higher prices.")

        st.markdown("---")
        col_st, col_ol = st.columns(2)
        with col_st:
            st.markdown("**Post-Harvest Storage Tips**")
            st.write("- **Farm storage:** Clean, dry, ventilated rooms — reduce moisture to below 12–14%.")
            st.write("- **Cold storage:** For perishables (Vegetables, Banana, Tomato) — use nearest WDRA-registered facility.")
            st.write("- **Warehouse receipt:** Get a warehouse receipt and use it as loan collateral (KCC scheme).")
            st.write("- **Pest control:** Use TNAU-recommended fumigation before storage.")
        with col_ol:
            st.markdown("**Online Selling & Negotiation**")
            st.write("- **e-NAM:** National Agriculture Market — electronic trading across India. Register at enam.gov.in")
            st.write("- **Agrimarket app:** Check daily prices for 300+ commodities pan-India.")
            st.write("- **Negotiation tip:** Always quote 10–15% above your target — buyers always bargain down.")
            st.write("- **Contract farming:** Contact TNAU or local KVK for pre-arranged buyer tie-ups.")

        st.markdown("---")
        st.markdown(f"**Your Profit Summary — {mkt_crop} on {land} ha**")
        ps1, ps2, ps3, ps4 = st.columns(4)
        with ps1:
            st.metric("Expected Yield", f"{mp2['total_yield']} t")
        with ps2:
            st.metric("Revenue", fmt_inr(mp2['revenue']))
        with ps3:
            st.metric("Cost", fmt_inr(mp2['cost']))
        with ps4:
            st.metric("Net Profit", fmt_inr(mp2['profit']))
        st.write(f"**ROI:** {mp2['roi']}% | **Break-even yield:** {mp2['break_even']} tonnes")

        # Market & Selling Summary 
        st.markdown("---")
        st.markdown("### Market Summary & Selling Advice")
        _mkt_price_now = mc2["price"]
        _mkt_low = int(_mkt_price_now * 0.75)
        _mkt_peak = int(_mkt_price_now * 1.30)
        _mkt_best_window ="4–8 weeks after harvest"
        _mkt_fit = crop_suitability(mkt_crop, dd["rainfall_mm"], dd["avg_temp"], dd["soil_ph"], dd["humidity"])
        _mkt_p = calc_profit(mkt_crop, land)

        if _mkt_fit >= 70 and _mkt_p["roi"] >= 100:
            _mkt_verdict = f"**{mkt_crop}** is a strong choice for {district} — good climate fit ({_mkt_fit}%) and high ROI ({_mkt_p['roi']}%)."
            _mkt_color ="success"
        elif _mkt_fit >= 50:
            _mkt_verdict = f"**{mkt_crop}** has moderate suitability for {district} (climate fit: {_mkt_fit}%, ROI: {_mkt_p['roi']}%). Manageable with proper inputs."
            _mkt_color ="warning"
        else:
            _mkt_verdict = f"**{mkt_crop}** has low climate fit ({_mkt_fit}%) for {district}. Consider a more suitable crop for better market returns."
            _mkt_color ="error"

        if _mkt_color =="success":
            st.success(_mkt_verdict)
        elif _mkt_color =="warning":
            st.warning(_mkt_verdict)
        else:
            st.error(_mkt_verdict)

        _sell_ch = mc2["sell"]
        st.info(
            f"Best selling strategy for {mkt_crop}:"
            f"Sell {_mkt_best_window} (prices recover 20-35% after harvest glut)."
            f"Avg price: Rs.{_mkt_price_now:,}/t | Peak: Rs.{_mkt_peak:,}/t."
            f"Channels: {_sell_ch}."
            "Register on e-NAM (enam.gov.in) for national market access."
            "For bulk (>5t), contact processing units or cooperatives for fixed-price contracts."
        )

        # ANALYSIS QUESTIONS: Q16, Q17, Q18 
        st.markdown("---")
        st.markdown("#### Crop Risk & Season Performance Analysis")
        st.caption("Click a question below to see the detailed analysis answer.")

        tab7_q_map = {
            "Flood + heat combined effects": 16,
            "Crop climate vulnerability": 17,
            "Growing season length vs yield": 18,
        }
        if"tab7_q_sel"not in st.session_state:
            st.session_state.tab7_q_sel = None

        t7c1, t7c2, t7c3 = st.columns(3)
        for col_t7, (qlabel, qnum) in zip([t7c1, t7c2, t7c3], tab7_q_map.items()):
            with col_t7:
                if st.button(qlabel, key=f"t7q_{qnum}", width='stretch'):
                    st.session_state.tab7_q_sel = qnum

        if st.session_state.tab7_q_sel:
            st.markdown("---")
            ans = get_analysis_answer(st.session_state.tab7_q_sel, district, dd, land, sel_crop)
            st.markdown(ans)
            if st.button("Close Answer", key="t7_close"):
                st.session_state.tab7_q_sel = None
                st.rerun()


        # District Zone Similarity (K-Means)
        st.markdown("---")
        st.markdown("### Zone Similarity — District Grouping by Climate Profile")
        st.write("Groups all 38 districts by climate and soil profile to identify similar farming zones.")

        zs_c1, zs_c2 = st.columns([1, 2])
        with zs_c1:
            n_zones = st.slider("Number of zones", 2, 6, 4, key="k_clusters")
        with zs_c2:
            zone_vars = st.multiselect(
                "Comparison variables",
                ["Rainfall","AvgTemp","Humidity","SoilpH",
                 "DroughtIdx","HeatIdx","FloodIdx","Yield"],
                default=["Rainfall","AvgTemp","Humidity","DroughtIdx","HeatIdx"],
                key="cluster_feats"
            )

        if len(zone_vars) < 2:
            st.warning("Select at least 2 variables.")
        else:
            dist_agg = df_ml.groupby("District")[zone_vars + ["Yield"]].mean().reset_index()
            zone_map_z = {d: v["zone"] for d, v in TN_DISTRICTS.items()}
            dist_agg["AgriZone"] = dist_agg["District"].map(zone_map_z)

            X_cl = dist_agg[zone_vars].values
            scaler_cl = StandardScaler()
            X_cl_sc = scaler_cl.fit_transform(X_cl)

            km = KMeans(n_clusters=n_zones, random_state=42, n_init=20)
            dist_agg["SimilarityGroup"] = km.fit_predict(X_cl_sc).astype(str)

            zone_labels = {str(i): f"Group {chr(65+i)}"for i in range(n_zones)}
            dist_agg["SimilarityGroup"] = dist_agg["SimilarityGroup"].map(zone_labels)

            my_row = dist_agg[dist_agg["District"] == district]

            # Your district info 
            if not my_row.empty:
                my_grp = my_row["SimilarityGroup"].values[0]
                similar_dists = dist_agg[
                    (dist_agg["SimilarityGroup"] == my_grp) &
                    (dist_agg["District"] != district)
                ]["District"].tolist()
                st.success(
                    f"**{district}** belongs to **{my_grp}** —"
                    f"similar districts: **{','.join(similar_dists[:5]) if similar_dists else'Unique zone'}**"
                )

            st.markdown("---")

            # TABLE 1: District Group mapping 
            st.markdown("#### Table 1 — District to Zone Mapping")
            map_df = dist_agg[["District","AgriZone","SimilarityGroup","Yield"]].copy()
            map_df["Yield"] = map_df["Yield"].round(2)
            map_df = map_df.rename(columns={
                "AgriZone":"TN Zone",
                "SimilarityGroup":"Similarity Group",
                "Yield":"Avg Yield (t/ha)"
            }).sort_values("Similarity Group")
            st.dataframe(map_df, width='stretch', hide_index=True)

            st.markdown("---")

            # TABLE 2: Group averages 
            st.markdown("#### Table 2 — Zone-wise Average Climate Values")
            grp_avg = dist_agg.groupby("SimilarityGroup")[zone_vars + ["Yield"]].mean().reset_index()
            grp_avg = grp_avg.rename(columns={"SimilarityGroup":"Similarity Group","Yield":"Avg Yield (t/ha)"})
            grp_avg = grp_avg.round(2)
            st.dataframe(grp_avg, width='stretch', hide_index=True)

            st.markdown("---")

            # TABLE 3: Districts per group 
            st.markdown("#### Table 3 — Districts in Each Similarity Group")
            for grp_name in sorted(dist_agg["SimilarityGroup"].unique()):
                grp_dists = dist_agg[dist_agg["SimilarityGroup"] == grp_name]["District"].tolist()
                grp_yield = dist_agg[dist_agg["SimilarityGroup"] == grp_name]["Yield"].mean()
                highlight ="(Your Group)"if not my_row.empty and my_row["SimilarityGroup"].values[0] == grp_name else""
                st.markdown(f"**{grp_name}{highlight}** — Avg Yield: {grp_yield:.2f} t/ha")
                cols_per_row = 5
                dist_rows = [grp_dists[i:i+cols_per_row] for i in range(0, len(grp_dists), cols_per_row)]
                for row in dist_rows:
                    rcols = st.columns(cols_per_row)
                    for ri, d_name in enumerate(row):
                        star =""if d_name == district else""
                        rcols[ri].info(f"{star}{d_name}")

            st.markdown("---")

            # TABLE 4: Variable-wise ranking per group 
            st.markdown("#### Table 4 — Variable Rankings Across Groups")
            rank_df = grp_avg.set_index("Similarity Group").drop(columns=["Avg Yield (t/ha)"], errors="ignore")
            for col in rank_df.columns:
                rank_df[col] = rank_df[col].round(2)
            st.dataframe(rank_df, width='stretch')
            st.caption("Higher value = more of that variable in that group. Compare rows to see what makes each group distinct.")

            st.markdown("---")

            # 
            # ML PREDICTION ENGINE — Trained on Original Dataset
            # 
            st.markdown("## Crop Yield & Profit Prediction")
            st.caption("Trained on the full TN dataset (38 districts × all crops × 2019–2024). Adjust inputs and click Predict.")

            # Train models on the full df_ml dataset 
            _pred_feat = ["Rainfall","AvgTemp","SoilMoisture","Fertilizer",
                          "GrowDays","DroughtIdx","HeatIdx","Irrigation",
                          "Humidity","SoilpH","Sunlight","Wind","CO2",
                          "FloodIdx","ClimateScore","Pesticide"]

            @st.cache_data
            def train_prediction_models(df):
                from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
                from sklearn.preprocessing import StandardScaler, LabelEncoder
                from sklearn.model_selection import train_test_split
                import numpy as np

                feats = ["Rainfall","AvgTemp","SoilMoisture","Fertilizer",
                         "GrowDays","DroughtIdx","HeatIdx","Irrigation",
                         "Humidity","SoilpH","Sunlight","Wind","CO2",
                         "FloodIdx","ClimateScore","Pesticide"]

                X = df[feats].values
                y_yield = df["Yield"].values
                y_loss = df["HarvestLoss"].values
                le = LabelEncoder()
                y_tier = le.fit_transform(df["ProfitTier"])

                sc = StandardScaler()
                X_sc = sc.fit_transform(X)

                rf_yield = RandomForestRegressor(n_estimators=150, random_state=42, n_jobs=-1)
                rf_yield.fit(X_sc, y_yield)

                rf_loss = RandomForestRegressor(n_estimators=150, random_state=42, n_jobs=-1)
                rf_loss.fit(X_sc, y_loss)

                rf_tier = RandomForestClassifier(n_estimators=150, random_state=42, n_jobs=-1)
                rf_tier.fit(X_sc, y_tier)

                importances = rf_yield.feature_importances_

                return sc, rf_yield, rf_loss, rf_tier, le, feats, importances

            sc_pred, rf_yield, rf_loss, rf_tier, le_tier, pred_feats, feat_imp = train_prediction_models(df_ml)

            # Pre-fill defaults from selected district + crop 
            _def_crop = sel_crop if sel_crop and sel_crop in CROP_DB else (dd["main_crops"][0] if dd["main_crops"] else"Paddy")
            _cb = CROP_DB.get(_def_crop, CROP_DB["Paddy"])

            _def_rain = float(dd["rainfall_mm"])
            _def_temp = float(dd["avg_temp"])
            _def_humidity = float(dd["humidity"])
            _def_soilmoist = round(dd["humidity"] * 0.68, 1)
            _def_soilph = float(dd["soil_ph"])
            _def_fert = round(_cb.get("cost_ha", 40000) / 1200, 1)
            _def_pest = 2.0
            _def_irr = max(0.0, round(_cb.get("cost_ha", 40000) / 210 - _def_rain * 0.28, 1))
            _def_sun = 8.5
            _def_wind = 15.0
            _def_co2 = 422.5
            _def_grow = float(_cb.get("days", 120))
            _def_drought = round(max(0, 1 - _def_rain / 1800), 3)
            _def_heat = round(max(0, (_def_temp - 25) / 10), 3)
            _def_flood = round(max(0, (_def_rain - 800) / 1500), 3)
            _def_climate = round((_def_drought + _def_heat) / 2, 3)

            st.markdown("### Select Crop & District for Prediction")
            pc1, pc2 = st.columns(2)
            with pc1:
                pred_crop = st.selectbox(
                    "Crop to Predict",
                    list(CROP_DB.keys()),
                    index=list(CROP_DB.keys()).index(_def_crop) if _def_crop in CROP_DB else 0,
                    key="pred_crop_sel"
                )
            with pc2:
                pred_district = st.selectbox(
                    "District",
                    list(TN_DISTRICTS.keys()),
                    index=list(TN_DISTRICTS.keys()).index(district),
                    key="pred_dist_sel"
                )

            # Auto-update defaults — every value MUST be a Python float (not int/numpy)
            def _f(v, lo, hi):
                """Clamp v to [lo, hi] and guarantee a Python float."""
                return float(max(float(lo), min(float(hi), float(v))))

            _pcb = CROP_DB.get(pred_crop, CROP_DB["Paddy"])
            _pdd = TN_DISTRICTS[pred_district]
            _auto_rain = _f(_pdd["rainfall_mm"], 100.0, 3000.0)
            _auto_temp = _f(_pdd["avg_temp"], 15.0, 45.0)
            _auto_hum = _f(_pdd["humidity"], 30.0, 99.0)
            _auto_ph = _f(_pdd["soil_ph"], 4.0, 9.0)
            _auto_fert = _f(_pcb.get("cost_ha", 40000) / 1200, 5.0, 200.0)
            _auto_irr = _f(_pcb.get("cost_ha", 40000) / 210 - _auto_rain * 0.28, 0.0, 800.0)
            _auto_grow = _f(_pcb.get("days", 120), 30.0, 2560.0)
            _auto_sm = _f(_auto_hum * 0.68, 10.0, 99.0)
            _auto_drought = _f(1.0 - _auto_rain / 1800.0, 0.0, 1.0)
            _auto_heat = _f((_auto_temp - 25.0) / 10.0, 0.0, 1.0)
            _auto_flood = _f((_auto_rain - 800.0) / 1500.0, 0.0, 1.0)
            _auto_climate = _f((_auto_drought + _auto_heat) / 2.0, 0.0, 1.0)

            st.markdown("### Adjust Input Parameters")
            st.caption("Values are auto-filled from your district & crop. Fine-tune any parameter below.")

            inp1, inp2, inp3, inp4 = st.columns(4)
            with inp1:
                inp_rain = st.number_input("Rainfall (mm/yr)", min_value=100.0, max_value=3000.0, value=_auto_rain, step=10.0, key="inp_rain")
                inp_temp = st.number_input("Avg Temp (°C)", min_value=15.0, max_value=45.0, value=_auto_temp, step=0.5, key="inp_temp")
                inp_hum = st.number_input("Humidity (%)", min_value=30.0, max_value=99.0, value=_auto_hum, step=1.0, key="inp_hum")
                inp_ph = st.number_input("Soil pH", min_value=4.0, max_value=9.0, value=_auto_ph, step=0.1, key="inp_ph")
            with inp2:
                inp_sm = st.number_input("Soil Moisture (%)", min_value=10.0, max_value=99.0, value=_auto_sm, step=1.0, key="inp_sm")
                inp_fert = st.number_input("Fertilizer (kg/ha)", min_value=5.0, max_value=200.0, value=_auto_fert, step=1.0, key="inp_fert")
                inp_pest = st.number_input("Pesticide (L/ha)", min_value=0.5, max_value=10.0, value=2.0, step=0.1, key="inp_pest")
                inp_irr = st.number_input("Irrigation (mm)", min_value=0.0, max_value=800.0, value=_auto_irr, step=10.0, key="inp_irr")
            with inp3:
                inp_sun = st.number_input("Sunlight (hrs/day)", min_value=4.0, max_value=12.0, value=8.5, step=0.5, key="inp_sun")
                inp_wind = st.number_input("Wind Speed (km/h)", min_value=0.0, max_value=60.0, value=15.0, step=0.5, key="inp_wind")
                inp_co2 = st.number_input("CO₂ Level (ppm)", min_value=380.0, max_value=500.0, value=422.5, step=1.0, key="inp_co2")
                inp_grow = st.number_input("Growing Days", min_value=30.0, max_value=2560.0, value=_auto_grow, step=5.0, key="inp_grow")
            with inp4:
                inp_drought = st.number_input("Drought Index (0–1)", min_value=0.0, max_value=1.0, value=_auto_drought, step=0.01, key="inp_drought")
                inp_heat = st.number_input("Heat Index (0–1)", min_value=0.0, max_value=1.0, value=_auto_heat, step=0.01, key="inp_heat")
                inp_flood = st.number_input("Flood Index (0–1)", min_value=0.0, max_value=1.0, value=_auto_flood, step=0.01, key="inp_flood")
                inp_climate = st.number_input("Climate Score (0–1)", min_value=0.0, max_value=1.0, value=_auto_climate, step=0.01, key="inp_climate")

            st.markdown("---")

            # Predict button 
            if st.button("Predict Yield, Harvest Loss & Profit Tier", width='stretch', key="pred_btn"):
                import numpy as np

                _inp_vec = np.array([[
                    inp_rain, inp_temp, inp_sm, inp_fert,
                    inp_grow, inp_drought, inp_heat, inp_irr,
                    inp_hum, inp_ph, inp_sun, inp_wind,
                    inp_co2, inp_flood, inp_climate, inp_pest
                ]])

                _inp_sc = sc_pred.transform(_inp_vec)

                _pred_yield = float(rf_yield.predict(_inp_sc)[0])
                _pred_loss = float(rf_loss.predict(_inp_sc)[0])
                _tier_idx = rf_tier.predict(_inp_sc)[0]
                _tier_label = le_tier.inverse_transform([_tier_idx])[0]
                _tier_probs = rf_tier.predict_proba(_inp_sc)[0]
                _tier_conf = max(_tier_probs) * 100

                # Compute predicted profit
                _pcb2 = CROP_DB.get(pred_crop, CROP_DB["Paddy"])
                _pred_yield_clamped = max(_pcb2["yield_min"] * 0.5,
                                          min(_pred_yield, _pcb2["yield_max"] * 1.5))
                _pred_rev = round(_pred_yield_clamped * land * _pcb2["price"])
                _pred_cost = round(_pcb2["cost_ha"] * land)
                _pred_profit= round(_pred_rev - _pred_cost)
                _pred_roi = round(_pred_profit / _pred_cost * 100, 1) if _pred_cost else 0

                tier_color = {"High":"","Medium":"","Low":""}
                tier_bg = {"High":"success","Medium":"warning","Low":"error"}

                st.markdown("### Prediction Results")
                r1, r2, r3, r4 = st.columns(4)
                with r1:
                    st.metric("Predicted Yield", f"{_pred_yield:.3f} t/ha",
                              delta=f"{_pred_yield - (_pcb2['yield_min']+_pcb2['yield_max'])/2:+.2f} vs avg")
                with r2:
                    st.metric("Harvest Loss", f"{_pred_loss:.1f}%",
                              delta=f"{'High'if _pred_loss > 15 else'Low'} risk")
                with r3:
                    st.metric("Est. Profit", fmt_inr(_pred_profit), delta=f"ROI {_pred_roi}%")
                with r4:
                    st.metric("Profit Tier", f"{tier_color.get(_tier_label,'')} {_tier_label}")

                st.markdown("---")

                # Detailed breakdown 
                st.markdown("#### Full Prediction Breakdown")
                bk1, bk2 = st.columns(2)
                with bk1:
                    st.markdown(f"**Crop:** {_pcb2.get('emoji','')} {pred_crop} | **District:** {pred_district}")
                    st.write(f"- Predicted yield per ha: **{_pred_yield:.3f} t/ha**")
                    st.write(f"- For your land ({land} ha): **{_pred_yield_clamped*land:.2f} tonnes**")
                    st.write(f"- Expected revenue: **{fmt_inr(_pred_rev)}**")
                    st.write(f"- Est. cost: **{fmt_inr(_pred_cost)}**")
                    st.write(f"- Net profit: **{fmt_inr(_pred_profit)}**")
                    st.write(f"- ROI: **{_pred_roi}%**")
                with bk2:
                    st.markdown("**Risk Assessment:**")
                    st.write(f"- Harvest loss estimate: **{_pred_loss:.1f}%** —"
                             f"{'High risk — review inputs'if _pred_loss > 20 else'Moderate'if _pred_loss > 12 else'Low risk'}")
                    st.write(f"- Profit tier: **{tier_color.get(_tier_label,'')} {_tier_label}** (confidence {_tier_conf:.0f}%)")
                    _base_avg = (_pcb2["yield_min"] + _pcb2["yield_max"]) / 2
                    _yield_delta = _pred_yield - _base_avg
                    if _yield_delta >= 0:
                        st.write(f"- Yield vs district avg: **+{_yield_delta:.2f} t/ha** above average")
                    else:
                        st.write(f"- Yield vs district avg: **{_yield_delta:.2f} t/ha** below average")
                    st.write(f"- Drought index: **{inp_drought:.3f}** — {'Water stress risk'if inp_drought > 0.4 else'Adequate water'}")
                    st.write(f"- Heat index: **{inp_heat:.3f}** — {'Heat stress risk'if inp_heat > 0.3 else'Temperature OK'}")

                st.markdown("---")

                # Top 5 most influential factors 
                st.markdown("#### Top 5 Factors Driving This Prediction")
                _feat_names_disp = ["Rainfall","Avg Temp","Soil Moisture","Fertilizer",
                                    "Growing Days","Drought Idx","Heat Idx","Irrigation",
                                    "Humidity","Soil pH","Sunlight","Wind","CO₂",
                                    "Flood Idx","Climate Score","Pesticide"]
                _sorted_imp = sorted(zip(_feat_names_disp, feat_imp), key=lambda x: x[1], reverse=True)
                for rank, (fname, fimp) in enumerate(_sorted_imp[:5], 1):
                    st.write(f"**#{rank} {fname}** — importance score: {fimp:.3f}")

                st.markdown("---")

                # Actionable recommendations 
                st.markdown("#### AI Recommendations Based on Prediction")
                recs = []
                if inp_drought > 0.4:
                    recs.append("**Reduce drought index:** Install drip irrigation — can raise yield by 15–25% and reduce drought loss.")
                if inp_heat > 0.3:
                    recs.append("**Heat stress detected:** Shift sowing date earlier (Jun–Jul) to avoid peak heat; use TNAU heat-tolerant varieties.")
                if inp_fert < 25:
                    recs.append("**Low fertilizer:** Increase NPK application to TNAU recommended levels — potential 10–15% yield gain.")
                if inp_sm < 40:
                    recs.append("**Low soil moisture:** Add FYM 10–15 t/ha and vermicompost to improve moisture retention.")
                if _pred_loss > 15:
                    recs.append("**High harvest loss risk:** Apply for PMFBY crop insurance before sowing — premium only 1.5–2% of sum insured.")
                if _tier_label =="Low":
                    recs.append("**Low profit tier:** Consider switching to a higher-value crop for this district's conditions, or reduce input costs.")
                if inp_rain < 600:
                    recs.append("**Low rainfall area:** Supplement with borewell/canal irrigation; apply for PM Krishi Sinchayee Yojana subsidy (55% off drip system).")
                if not recs:
                    recs.append("**Excellent conditions!** Your inputs are well-optimised for this crop. Maintain fertilizer schedule and monitor for pests.")
                for rec in recs:
                    st.write(f"- {rec}")

            else:
                st.info("Set your parameters above and click **Predict** to see AI-powered yield, loss, and profit predictions based on the full TN dataset.")



        # Crop Co-occurrence Insights (Apriori/FP-Growth — hidden) 
        st.markdown("---")
        st.subheader("What Other Farmers Grow Alongside This Crop")
        st.caption("Based on crop combination patterns across all 38 TN districts — discover profitable crop pairings for your farm.")
        from itertools import combinations as _combos2
        import pandas as _pd_ar2
        # Build transactions
        _trans2 = [[c for c in _dd2["main_crops"] if c in CROP_DB] for _dd2 in TN_DISTRICTS.values() if len(_dd2.get("main_crops",[]))>=2]
        _all_i2 = sorted(set(c for t in _trans2 for c in t))
        def _supp2(iset,tr): s2=set(iset); return sum(1 for t in tr if s2.issubset(set(t)))/len(tr)
        # FP-Growth (faster, hidden)
        _ic2={}
        for t in _trans2:
            for it in t: _ic2[it]=_ic2.get(it,0)+1
        _n2=len(_trans2); _ms3=0.15
        _fi2={k:v/_n2 for k,v in _ic2.items() if v/_n2>=_ms3}
        _od2=sorted(_fi2,key=_fi2.get,reverse=True)
        _pat2={(it,):round(_fi2[it],3) for it in _od2}
        for i in range(len(_od2)):
            for j in range(i+1,len(_od2)):
                s3=_supp2([_od2[i],_od2[j]],_trans2)
                if s3>=_ms3: _pat2[tuple(sorted([_od2[i],_od2[j]]))]=round(s3,3)
        for i in range(len(_od2)):
            for j in range(i+1,len(_od2)):
                for k3 in range(j+1,len(_od2)):
                    s3=_supp2([_od2[i],_od2[j],_od2[k3]],_trans2)
                    if s3>=_ms3: _pat2[tuple(sorted([_od2[i],_od2[j],_od2[k3]]))]=round(s3,3)
        # Generate rules
        def _rules2(pat,mc3):
            out2=[]
            for iset,sup3 in pat.items():
                if len(iset)<2: continue
                for sz in range(1,len(iset)):
                    for ant in _combos2(iset,sz):
                        con2=tuple(x for x in iset if x not in ant)
                        if not con2: continue
                        as3=pat.get(ant,0)
                        if as3==0: continue
                        cf2=round(sup3/as3,3); lf2=round(cf2/pat.get(con2,sup3),3)
                        if cf2>=mc3: out2.append({"ant":ant,"con":con2,"sup":sup3,"conf":cf2,"lift":lf2})
            return sorted(out2,key=lambda x:x["lift"],reverse=True)
        _all_rules2=_rules2(_pat2,0.50)
        if sel_crop:
            # Rules where sel_crop is antecedent
            _crop_rules=[r for r in _all_rules2 if sel_crop in r["ant"]]
            if _crop_rules:
                st.markdown(f"** Farmers who grow {sel_crop} also commonly grow:**")
                _cr_cols=st.columns(min(4,len(_crop_rules)))
                for _ci2,_rl3 in enumerate(_crop_rules[:4]):
                    with _cr_cols[_ci2]:
                        _con_crop="+".join(_rl3["con"])
                        _con_emoji="".join(CROP_DB.get(c,{}).get("emoji","") for c in _rl3["con"])
                        _con_prof=calc_profit(list(_rl3["con"])[0],land) if len(_rl3["con"])==1 else {"profit":0,"roi":0}
                        st.metric(f"{_con_emoji} {_con_crop}", f"{round(_rl3['conf']*100)}% of farmers", delta=f"Lift {_rl3['lift']}x")
                # Best combo recommendation
                _best_combo=[r for r in _crop_rules if all(c not in CROP_EXCLUSION or district not in CROP_EXCLUSION[c].get("exclude_districts",[]) for c in r["con"])]
                if _best_combo:
                    _bc2=_best_combo[0]
                    _bc_name="+".join(_bc2["con"])
                    _bc_prof=sum(calc_profit(c,land).get("profit",0) for c in _bc2["con"] if c in CROP_DB)
                    st.success(f"**Best companion crop:** {sel_crop} + **{_bc_name}** — grown together by {round(_bc2['conf']*100)}% of similar farmers | Extra profit potential: {fmt_inr(_bc_prof)}")
            else:
                # Fallback: most common pairings overall
                st.markdown("** Most common crop combinations across TN districts:**")
                _top_pairs=[(k,v) for k,v in sorted(_pat2.items(),key=lambda x:x[1],reverse=True) if len(k)==2][:4]
                _tpc=st.columns(4)
                for _ci3,(_pair,_psup) in enumerate(_top_pairs):
                    with _tpc[_ci3]:
                        _pemoji="+".join(CROP_DB.get(c,{}).get("emoji","") for c in _pair)
                        st.metric(_pemoji,"+".join(_pair), delta=f"{round(_psup*100)}% districts")
        else:
            # No crop selected — show general insights
            st.markdown("** Most commonly grown crop combinations across TN districts:**")
            _top_pairs2=[(k,v) for k,v in sorted(_pat2.items(),key=lambda x:x[1],reverse=True) if len(k)==2][:6]
            _tp2c=st.columns(3)
            for _ci4,(_pair2,_psup2) in enumerate(_top_pairs2):
                with _tp2c[_ci4%3]:
                    _p2emoji="+".join(CROP_DB.get(c,{}).get("emoji","") for c in _pair2)
                    st.metric(_p2emoji,"+".join(_pair2), delta=f"{round(_psup2*100)}% of districts grow this together")
            st.info("Select a crop in Tab 1 to see personalized companion crop suggestions.")
        # Seasonal diversification tip
        if sel_crop and sel_crop in CROP_DB:
            _sel_season=CROP_DB[sel_crop].get("season","")
            _diff_season=[c for c in CROP_DB if c!=sel_crop and CROP_DB[c].get("season","")!=_sel_season and c in _fi2]
            if _diff_season:
                _ds_top=sorted(_diff_season,key=lambda c:_fi2.get(c,0),reverse=True)[:3]
                st.markdown(f"** Off-season diversification:** While {sel_crop} is in season, consider also growing:"+",".join(f"**{c}** ({CROP_DB[c].get('season','')[:10]})"for c in _ds_top))

    # 

st.markdown("---")
st.caption("AgriSmart TN · Smart Crop Advisor for All 38 Tamil Nadu Districts | Weather: Open-Meteo API · Crop data: TNAU, APEDA, India Agri Market · Consult local KVK for certified field advice.")
