import datetime
import sqlite3
import streamlit as st

DB_FILE = "em_platform.db"

# =====================================================================
# 1. DATABASE LAYER (Matches Your Schema Exactly)
# =====================================================================
def initialize_database():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Provision Master Table Structure
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emm_ins_asmbly (
                ia_code TEXT PRIMARY KEY,
                stn_cd TEXT NOT NULL,
                loc_bet TEXT NOT NULL,
                es_bet TEXT NOT NULL,
                make_9 TEXT NOT NULL,
                make_s TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        
        # Provision Transaction Table Structure
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emt_ia_maintain (
                ia_code TEXT NOT NULL,
                date TEXT NOT NULL,
                c_w_ht INTEGER,
                encum INTEGER,
                run_gap INTEGER,
                observation TEXT,
                description TEXT,
                remarks TEXT,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                modify_rea TEXT,
                modify_id TEXT,
                sup_emp_no INTEGER DEFAULT 0 NOT NULL,
                sup_emp_name TEXT DEFAULT '' NOT NULL,
                FOREIGN KEY (ia_code) REFERENCES emm_ins_asmbly(ia_code)
            )
        """)
        conn.commit()

initialize_database()

# =====================================================================
# 2. PRESENTATION UI ENGINE
# =====================================================================
st.set_page_config(page_title="EM Module Engine Migration", layout="wide")
st.title("⚡ Unified Energy Management Module Platform")
st.markdown("---")

navigation = st.sidebar.radio(
    "Application Modules", 
    ["🛠️ EMMIN0100 - Master Configuration", "💸 EMTIN0100 - Transaction Logs"]
)

# =====================================================================
# MODULE A: EMMIN0100 MASTER SETUP
# =====================================================================
if navigation == "🛠️ EMMIN0100 - Master Configuration":
    st.subheader("Configure Installation Assembly Master (`emm_ins_asmbly`)")
    
    with st.form("master_input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            ia_code = st.text_input("Installation Assembly Code (ia_code) *").strip()
            stn_cd = st.text_input("Station Code (stn_cd) *").strip()
            loc_bet = st.text_input("Location Between (loc_bet) *").strip()
            es_bet = st.text_input("ES Between (es_bet) *").strip()
        with col2:
            make_9 = st.text_input("Make 9 (make_9) *").strip()
            make_s = st.text_input("Make S (make_s) *").strip()
            status = st.selectbox("Current Status", ["ACTIVE", "INACTIVE"])
            
        submit_master = st.form_submit_button("Commit Master Record to System")
        
        if submit_master:
            if not all([ia_code, stn_cd, loc_bet, es_bet, make_9, make_s]):
                st.error("Validation Error: All mandatory master configuration fields (*) must be completed.")
            else:
                try:
                    with sqlite3.connect(DB_FILE) as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO emm_ins_asmbly (ia_code, stn_cd, loc_bet, es_bet, make_9, make_s, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (ia_code, stn_cd, loc_bet, es_bet, make_9, make_s, status))
                        conn.commit()
                    st.success(f"Success: Master Entry '{ia_code}' committed safely to ledger mappings.")
                except sqlite3.IntegrityError:
                    st.error(f"Duplicate Error: An installation assembly matching code '{ia_code}' is already active.")

    # View Current Assemblies
    st.markdown("### Active Master Assemblies Map")
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM emm_ins_asmbly")
        records = cursor.fetchall()
        if records:
            st.dataframe([dict(row) for row in records], use_container_width=True)

# =====================================================================
# MODULE B: EMTIN0100 TRANSACTION SETUP
# =====================================================================
elif navigation == "💸 EMTIN0100 - Transaction Logs":
    st.subheader("Process Maintenance Logs Ledger Data (`emt_ia_maintain`)")
    
    # Query registered keys dynamically for verification routing checks
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ia_code FROM emm_ins_asmbly WHERE status='ACTIVE'")
        available_codes = [row[0] for row in cursor.fetchall()]

    if not available_codes:
        st.warning("Prerequisite Halt: Please configure at least one Active Master Assembly entry before processing transactions.")
    else:
        with st.form("transaction_input_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                selected_ia = st.selectbox("Assembly Identification Code Reference (ia_code) *", available_codes)
                tx_date = st.date_input("Transaction Log Date (date) *", datetime.date.today())
                c_w_ht = st.number_input("C W Height Parameter Measurement (c_w_ht)", value=0, step=1)
                encum = st.number_input("Encumbrance Value Metric (encum)", value=0, step=1)
                run_gap = st.number_input("Running Gap Calibration Check (run_gap)", value=0, step=1)
                user_id = st.text_input("Operator Identifier Profile (user_id) *", value="Omkar_Dev").strip()
            with col2:
                sup_emp_no = st.number_input("Supervisor Employee ID No (sup_emp_no) *", min_value=0, value=0, step=1)
                sup_emp_name = st.text_input("Supervisor Employee Name (sup_emp_name) *", value="").strip()
                observation = st.text_input("Field Observation Notes (observation)")
                description = st.text_input("Action Item Description (description)")
                remarks = st.text_input("Engineering Performance Remarks (remarks)")
                
            submit_tx = st.form_submit_button("Submit & Authorize Transaction Data")
            
            if submit_tx:
                if not user_id or not sup_emp_name or sup_emp_no <= 0:
                    st.error("Validation Error: Please make sure mandatory fields user_id, supervisor name, and employee number are verified.")
                else:
                    date_str = tx_date.strftime("%Y-%m-%d")
                    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    with sqlite3.connect(DB_FILE) as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO emt_ia_maintain (
                                ia_code, date, c_w_ht, encum, run_gap, observation, description, 
                                remarks, user_id, timestamp, sup_emp_no, sup_emp_name
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (selected_ia, date_str, c_w_ht, encum, run_gap, observation, description, 
                              remarks, user_id, timestamp_str, sup_emp_no, sup_emp_name))
                        conn.commit()
                    st.success(f"Transaction Confirmed: Maintenance logged cleanly under code '{selected_ia}'.")

    # View Current Logs Ledger Pipeline 
    st.markdown("### Active Transaction Ledger Summary")
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM emt_ia_maintain ORDER BY timestamp DESC")
        tx_records = cursor.fetchall()
        if tx_records:
            st.dataframe([dict(row) for row in tx_records], use_container_width=True)
