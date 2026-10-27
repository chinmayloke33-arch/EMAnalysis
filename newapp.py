import datetime
import streamlit as st
from supabase import create_client, Client

# =====================================================================
# 1. SUPABASE CONNECTION PIPELINE
# =====================================================================
@st.cache_resource
def get_supabase_client() -> Client:
    url: str = st.secrets["supabase"]["SUPABASE_URL"]
    key: str = st.secrets["supabase"]["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = get_supabase_client()

# Fetch active insulator assemblies from master table to fill dropdown options
@st.cache_data(ttl=10)
def fetch_registered_assemblies():
    try:
        res = supabase.table("emm_ins_asmbly").select("ia_code").execute()
        return [row["ia_code"] for row in res.data] if res.data else []
    except Exception:
        return []

master_assembly_options = fetch_registered_assemblies()

# =====================================================================
# SYSTEM VISUAL CONFIGURATION & STYLING (Custom CSS Injection)
# =====================================================================
st.set_page_config(page_title="Add Inspection Record", layout="wide")

st.markdown("""
    <style>
    /* Center and constrain main container card sizing */
    .block-container {
        padding-top: 1.5rem;
        max-width: 1100px !important;
    }
    
    /* Top horizontal navigation styling buttons */
    div.stButton > button[key^="nav_"] {
        background-color: transparent;
        color: #007acc;
        border: none;
        font-weight: 600;
        font-size: 16px;
        padding: 6px 16px;
    }
    
    /* White Card Wrapper Container matching the design border */
    .main-card {
        border: 2px solid #e8edf3;
        border-radius: 8px;
        padding: 35px;
        background-color: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.01);
    }
    
    /* Form Centered Headers */
    .form-title {
        text-align: center;
        font-weight: bold;
        color: #111111;
        font-size: 22px;
        margin-bottom: 2px;
        font-family: inherit;
    }
    .form-subtitle {
        text-align: center;
        color: #111111;
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 30px;
        font-family: inherit;
    }
    
    /* Dual-Language Field Label Styling */
    .field-label-hi {
        font-size: 15px;
        font-weight: 500;
        color: #222222;
        margin-bottom: 0px;
    }
    .field-label-en {
        font-size: 13px;
        color: #666666;
        margin-top: 0px;
        margin-bottom: 6px;
        display: block;
    }
    
    /* Center the action form buttons */
    .stFormSubmitButton {
        display: flex;
        justify-content: center;
    }
    
    /* Green Save Action Button matching layout requirements */
    .save-btn button {
        background-color: #00a86b !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border-radius: 6px !important;
        padding: 10px 36px !important;
        border: none !important;
        width: auto !important;
    }
    
    /* Blue Update Action Button for Modification operations */
    .update-btn button {
        background-color: #007acc !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border-radius: 6px !important;
        padding: 10px 36px !important;
        border: none !important;
        width: auto !important;
    }
    </style>
""", unsafe_allowed_html=True)

# =====================================================================
# 📋 TOP NAVIGATION COMPONENTS MAPPING
# =====================================================================
if "current_view" not in st.session_state:
    st.session_state.current_view = "NEW"

nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([2, 1.5, 1.5, 1.2, 2])
with nav_col2:
    if st.button("New Inspection", key="nav_new"):
        st.session_state.current_view = "NEW"
with nav_col3:
    if st.button("View Records", key="nav_view"):
        st.session_state.current_view = "VIEW"
with nav_col4:
    if st.button("Modify", key="nav_modify"):
        st.session_state.current_view = "MODIFY"

st.markdown("<br>", unsafe_allowed_html=True)

# =====================================================================
# VIEW MODE: HISTORICAL DATA TABLE DISPLAY
# =====================================================================
if st.session_state.current_view == "VIEW":
    st.markdown("<div class='main-card'>", unsafe_allowed_html=True)
    st.markdown("<p class='form-title'>ऐतिहासिक निरीक्षण रिकॉर्ड</p>", unsafe_allowed_html=True)
    st.markdown("<p class='form-subtitle'>Historical Inspection Ledger Records</p>", unsafe_allowed_html=True)
    
    with st.spinner("Loading records from cloud database..."):
        records = supabase.table("emt_ia_maintain").select("*").order("timestamp", desc=True).execute()
        
    if records.data:
        st.dataframe(records.data, use_container_width=True)
    else:
        st.info("No logs currently recorded inside the transaction database.")
    st.markdown("</div>", unsafe_allowed_html=True)

# =====================================================================
# TRANSACTION EDIT ENGINE (New Inspection & Modification Modes)
# =====================================================================
else:
    # Set default standard values for initial dynamic field structures
    default_ia = "-- असेंबली चुनें --"
    default_date = datetime.date(2026, 10, 26)
    default_cw = 0
    default_encum = 0
    default_gap = 0
    default_obs = ""
    default_desc = ""
    default_rem = ""
    target_row_id = None

    # Open the structural wrapper container card 
    st.markdown("<div class='main-card'>", unsafe_allowed_html=True)

    # 🗲 MODIFICATION PRE-LOAD TRACER
    if st.session_state.current_view == "MODIFY":
        st.markdown("<p class='form-title' style='color: #007acc;'>निरीक्षण रिकॉर्ड संशोधित करें</p>", unsafe_allowed_html=True)
        st.markdown("<p class='form-subtitle'>Modify Inspection Record</p>", unsafe_allowed_html=True)
        
        search_target = st.text_input("संशोधित करने के लिए असेंबली कोड डालें / Enter Assembly Code to Modify").strip()
        if search_target:
            res = supabase.table("emt_ia_maintain").select("*").eq("ia_code", search_target).order("timestamp", desc=True).limit(1).execute()
            if res.data:
                st.success(f"Latest record entry for '{search_target}' loaded successfully!")
                row_data = res.data[0]
                target_row_id = row_data.get("id")
                default_ia = row_data.get("ia_code")
                try:
                    default_date = datetime.datetime.strptime(row_data.get("date"), "%Y-%m-%d").date()
                except Exception:
                    pass
                default_cw = int(row_data.get("c_w_ht", 0) or 0)
                default_encum = int(row_data.get("encum", 0) or 0)
                default_gap = int(row_data.get("run_gap", 0) or 0)
                default_obs = row_data.get("observation", "") or ""
                default_desc = row_data.get("description", "") or ""
                default_rem = row_data.get("remarks", "") or ""
            else:
                st.error("No transactional logs found matching that assembly code.")
    else:
        st.markdown("<p class='form-title'>निरीक्षण रिकॉर्ड जोड़ें</p>", unsafe_allowed_html=True)
        st.markdown("<p class='form-subtitle'>Add Inspection Record</p>", unsafe_allowed_html=True)

    # Core Data-Entry Input Form Component Block
    with st.form("transaction_ledger_form", clear_on_submit=True):
        
        # --- ROW 1: INSULATOR SELECTOR & CALENDAR ---
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.markdown("<p class='field-label-hi'>सिलेक्ट इंसुलेटर असेंबली</p><span class='field-label-en'>Select Insulator Assembly</span>", unsafe_allowed_html=True)
            dropdown_list = ["-- असेंबली चुनें --"] + master_assembly_options
            if default_ia in dropdown_list:
                select_idx = dropdown_list.index(default_ia)
            else:
                dropdown_list.append(default_ia)
                select_idx = len(dropdown_list) - 1
            ia_code = st.selectbox("", dropdown_list, index=select_idx, label_visibility="collapsed")
            
        with row1_col2:
            st.markdown("<p class='field-label-hi'>तारीख</p><span class='field-label-en'>Inspection Date</span>", unsafe_allowed_html=True)
            date_val = st.date_input("", value=default_date, label_visibility="collapsed")

        st.markdown("<br>", unsafe_allowed_html=True)

        # --- ROW 2: MEASUREMENTS TRIPLE GRID ---
        row2_col1, row2_col2, row2_col3 = st.columns(3)
        with row2_col1:
            st.markdown("<p class='field-label-hi'>कॉन्टैक्ट वायर हाईट (मिमी)</p><span class='field-label-en'>Contact Wire Height (mm)</span>", unsafe_allowed_html=True)
            c_w_ht = st.number_input("", value=default_cw, step=1, label_visibility="collapsed")
        with row2_col2:
            st.markdown("<p class='field-label-hi'>एन्कम्ब्रन्स (मिमी)</p><span class='field-label-en'>Encumbrance (mm)</span>", unsafe_allowed_html=True)
            encum = st.number_input("", value=default_encum, step=1, label_visibility="collapsed")
        with row2_col3:
            st.markdown("<p class='field-label-hi'>रनर गैप (मिमी)</p><span class='field-label-en'>Runner Gap (mm)</span>", unsafe_allowed_html=True)
            run_gap = st.number_input("", value=default_gap, step=1, label_visibility="collapsed")

        st.markdown("<br>", unsafe_allowed_html=True)

        # --- ROW 3: TEXT AREAS TRIPLE GRID ---
        row3_col1, row3_col2, row3_col3 = st.columns(3)
        with row3_col1:
