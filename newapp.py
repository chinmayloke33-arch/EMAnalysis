import streamlit as st

# =====================================================================
# SYSTEM VISUAL CONFIGURATION & STYLING (Custom CSS Injection)
# =====================================================================
st.set_page_config(page_title="Insulator Assembly Master", layout="wide")

st.markdown("""
    <style>
    /* Center the main container box */
    .block-container {
        padding-top: 2rem;
        max-width: 1000px !important;
    }
    
    /* Top horizontal navigation styling buttons */
    .nav-container {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 25px;
    }
    
    /* White Card Wrapper Container matching the design border */
    .main-card {
        border: 2px solid #e0e6ed;
        border-radius: 8px;
        padding: 40px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    /* Form Header Styling */
    .form-title {
        text-align: center;
        font-weight: bold;
        color: #111111;
        font-size: 24px;
        margin-bottom: 5px;
    }
    .form-subtitle {
        text-align: center;
        color: #333333;
        font-size: 18px;
        margin-bottom: 35px;
    }
    
    /* Field Label Custom Styling */
    .field-label-hi {
        font-size: 16px;
        font-weight: 500;
        color: #222222;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .field-label-en {
        font-size: 13px;
        color: #666666;
        margin-top: 0px;
        margin-bottom: 8px;
        display: block;
    }
    
    /* Streamlit button container adjustments */
    div.stButton > button {
        width: 100% !important;
    }
    
    /* Action trigger button customization matching blue theme */
    .generate-btn button {
        background-color: #007acc !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border-radius: 6px !important;
        padding: 12px !important;
        border: none !important;
    }
    </style>
""", unsafe_allowed_html=True)

# =====================================================================
# 📋 TOP NAVIGATION COMPONENTS MAPPING
# =====================================================================
# State tracker for button active view switches
if "sub_view" not in st.session_state:
    st.session_state.sub_view = "ADD"

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([4, 1.2, 1.2, 4])
with nav_col2:
    if st.button("Add", key="btn_nav_add", use_container_width=True):
        st.session_state.sub_view = "ADD"
with nav_col3:
    if st.button("View", key="btn_nav_view", use_container_width=True):
        st.session_state.sub_view = "VIEW"

st.markdown("<br>", unsafe_allowed_html=True)

# =====================================================================
# MODULE MODE INTERFACE SWITCH ROUTING
# =====================================================================
if st.session_state.sub_view == "VIEW":
    st.markdown("<div class='main-card'>", unsafe_allowed_html=True)
    st.markdown("<p class='form-title'>इंसुलेटर असेंबली रिकॉर्ड</p>", unsafe_allowed_html=True)
    st.markdown("<p class='form-subtitle'>Insulator Assembly Records Ledger</p>", unsafe_allowed_html=True)
    
    # Placeholder layout grid to print live database values cleanly
    st.info("Historical configured master values list will print out in this frame section container area.")
    st.markdown("</div>", unsafe_allowed_html=True)

else:
    # Open the stylized visual frame card border wrapper block
    st.markdown("<div class='main-card'>", unsafe_allowed_html=True)
    
    # Core Centered Application Headers
    st.markdown("<p class='form-title'>इंसुलेटर असेंबली मास्टर</p>", unsafe_allowed_html=True)
    st.markdown("<p class='form-subtitle'>Insulator Assembly Master</p>", unsafe_allowed_html=True)

    # Use a base form structure wrapper layout inside the panel box container card
    with st.form("master_generation_form", clear_on_submit=True):
        
        # --- GRID ROW 1 ---
        row1_col1, row1_col2, row1_col3 = st.columns(3)
        with row1_col1:
            st.markdown("<p class='field-label-hi'>ईंसुलेटर असेंबली कोड</p><span class='field-label-en'>Insulator Assembly Code</span>", unsafe_allowed_html=True)
            ia_code = st.text_input("", placeholder="Click Generate to create code", label_visibility="collapsed")
            
        with row1_col2:
            st.markdown("<p class='field-label-hi'>स्टेशन कोड</p><span class='field-label-en'>Station Code</span>", unsafe_allowed_html=True)
            stn_cd = st.selectbox("", ["Select City...", "MUMBAI", "DELHI", "KOLKATA", "CHENNAI"], label_visibility="collapsed")
            
        with row1_col3:
            st.markdown("<p class='field-label-hi'>लोकेशन के बीच</p><span class='field-label-en'>Location Between</span>", unsafe_allowed_html=True)
            loc_bet = st.text_input("", label_visibility="collapsed", key="txt_loc")

        st.markdown("<br>", unsafe_allowed_html=True)

        # --- GRID ROW 2 ---
        row2_col1, row2_col2, row2_col3 = st.columns(3)
        with row2_col1:
            st.markdown("<p class='field-label-hi'>एलिमेंट्री सेक्शन के बीच</p><span class='field-label-en'>Elementary Section Between</span>", unsafe_allowed_html=True)
            es_bet = st.text_input("", label_visibility="collapsed", key="txt_es")
            
        with row2_col2:
            st.markdown("<p class='field-label-hi'>इन्सुलेटर का मेक(9-टन)</p><span class='field-label-en'>Make Insulator (9-ton)</span>", unsafe_allowed_html=True)
            make_9 = st.text_input("", label_visibility="collapsed", key="txt_m9")
            
        with row2_col3:
            st.markdown("<p class='field-label-hi'>इन्सुलेटर का मेक स्थिति</p><span class='field-label-en'>Make Insulator Status</span>", unsafe_allowed_html=True)
            make_s = st.text_input("", label_visibility="collapsed", key="txt_ms")

        st.markdown("<br>", unsafe_allowed_html=True)

        # --- GRID ROW 3 ---
        row3_col1, row3_col2, row3_col3 = st.columns(3)
        with row3_col1:
            st.markdown("<p class='field-label-hi'>स्थिति</p><span class='field-label-en'>Status</span>", unsafe_allowed_html=True)
            status = st.selectbox("", ["Active", "Inactive"], label_visibility="collapsed")
            
        with row3_col2:
            st.write("") # Retain empty padding spaces 
        with row3_col3:
            st.write("") # Retain empty padding spaces

        st.markdown("<br><br>", unsafe_allowed_html=True)

        # --- LOWER ACTION BUTTON ASSEMBLY ---
        btn_col1, btn_col2, btn_col3 = st.columns([1.5, 3, 1.5])
        with btn_col2:
            st.markdown('<div class="generate-btn">', unsafe_allowed_html=True)
            submit_action = st.form_submit_button("Generate Assembly Code")
            st.markdown('</div>', unsafe_allowed_html=True)

        # Form execution response logic
        if submit_action:
            if stn_cd == "Select City..." or not loc_bet.strip():
                st.error("Validation Error: Please configure mandatory Station and Location entries.")
            else:
                st.success("Form validated successfully matching design parameters!")

    # Close the stylized visual frame card border wrapper block
    st.markdown("</div>", unsafe_allowed_html=True)
