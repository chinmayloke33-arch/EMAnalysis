import streamlit as st
import pandas as pd
import datetime
import secrets
import string
from supabase import create_client


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="KRCL | Inspection Management",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# 2. SUPABASE CONNECTION
# ============================================================

@st.cache_resource
def get_supabase():
    url = st.secrets["supabase"]["SUPABASE_URL"].strip()
    key = st.secrets["supabase"]["SUPABASE_KEY"].strip()

    return create_client(url, key)


ASSEMBLY_TABLE = "emm_ins_asmbly"
TRANSACTION_TABLE = "emt_ia_maintain"

try:
    supabase = get_supabase()
except Exception as exc:
    st.error("Unable to connect to Supabase.")
    st.code(str(exc))
    st.stop()


# ============================================================
# 3. CONSTANTS
# ============================================================

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

PLACEHOLDER = "-- असेंबली चुनें --"

USER_ID = "Omkar_Dev"
SUPERVISOR_NUMBER = 204
SUPERVISOR_NAME = "Supervisor_Alpha"


# ============================================================
# 4. CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1100px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .main-card {
        background: white;
        border: 1px solid #dfe7ef;
        border-top: 4px solid #0788bd;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.04);
    }

    .form-title {
        text-align: center;
        font-size: 23px;
        font-weight: 700;
        color: #172033;
        margin-bottom: 0;
    }

    .form-subtitle {
        text-align: center;
        font-size: 15px;
        font-weight: 600;
        color: #475467;
        margin-bottom: 25px;
    }

    .field-label-hi {
        font-size: 14px;
        font-weight: 600;
        color: #252525;
        margin-bottom: 0;
    }

    .field-label-en {
        font-size: 12px;
        color: #667085;
        margin-bottom: 6px;
    }

    div.stButton > button {
        border-radius: 7px;
        min-height: 40px;
        font-weight: 600;
    }

    div.stButton > button[kind="primary"] {
        background-color: #0788bd;
        border-color: #0788bd;
        color: white;
    }

    div[data-testid="stFormSubmitButton"] button {
        background-color: #0ba779;
        color: white;
        border: none;
        min-height: 43px;
        font-weight: 700;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #07845f;
        color: white;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #e1e7ef;
        border-radius: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 5. HELPER FUNCTIONS
# ============================================================

def field_label(hindi, english):
    """Display bilingual field labels."""

    st.markdown(
        f"""
        <div class="field-label-hi">{hindi}</div>
        <div class="field-label-en">{english}</div>
        """,
        unsafe_allow_html=True,
    )


def clean(value):
    """Remove spaces from CHAR database values."""

    if value is None:
        return ""

    return str(value).strip()


def get_assemblies():
    """Retrieve assembly master records."""

    response = (
        supabase.table(ASSEMBLY_TABLE)
        .select("*")
        .order("ia_code")
        .limit(1000)
        .execute()
    )

    return response.data or []


def get_transactions():
    """Retrieve inspection records."""

    response = (
        supabase.table(TRANSACTION_TABLE)
        .select("*")
        .order("timestamp", desc=True)
        .limit(1000)
        .execute()
    )

    return response.data or []


def get_station_codes():
    """Get available station codes from the assembly master."""

    records = get_assemblies()

    codes = sorted({
        clean(row.get("stn_cd"))
        for row in records
        if clean(row.get("stn_cd"))
    })

    return codes


def get_assembly_codes():
    """Get assembly codes for transaction selection."""

    records = get_assemblies()

    return sorted({
        clean(row.get("ia_code"))
        for row in records
        if clean(row.get("ia_code"))
    })


def generate_assembly_code(station_code):
    """
    Generate a unique assembly code.

    Example:
    IA-RN-20261027-A1B2C3

    The random suffix reduces collision risk.
    """

    station_code = clean(station_code).upper()

    station_code = "".join(
        character
        for character in station_code
        if character.isalnum()
    )

    if not station_code:
        station_code = "KRCL"

    date_part = datetime.datetime.now(IST).strftime("%Y%m%d")

    alphabet = string.ascii_uppercase + string.digits

    suffix = "".join(
        secrets.choice(alphabet)
        for _ in range(6)
    )

    return f"IA-{station_code[:8]}-{date_part}-{suffix}"


def show_error(prefix, exc):
    """Display a database error."""

    st.error(prefix)

    with st.expander("Technical details"):
        st.code(str(exc))


def show_header(hindi, english):
    """Display the page heading."""

    st.markdown(
        f"""
        <div class="form-title">{hindi}</div>
        <div class="form-subtitle">{english}</div>
        """,
        unsafe_allow_html=True,
    )


def record_label(record):
    """Create a readable label for an inspection record."""

    assembly = clean(record.get("ia_code"))
    inspection_date = clean(record.get("date"))
    timestamp = clean(record.get("timestamp"))

    return (
        f"{assembly} | {inspection_date} | {timestamp}"
    )


# ============================================================
# 6. APPLICATION HEADER
# ============================================================

st.title("KRCL | Inspection Management System")

st.caption(
    "Insulator Assembly Master • Inspection Transactions"
)

st.divider()


# ============================================================
# 7. NAVIGATION
# ============================================================

if "current_page" not in st.session_state:
    st.session_state.current_page = "ASSEMBLY_ADD"


nav1, nav2, nav3, nav4, nav5 = st.columns(5)

with nav1:
    if st.button("➕ Assembly Add", use_container_width=True):
        st.session_state.current_page = "ASSEMBLY_ADD"
        st.rerun()

with nav2:
    if st.button("📋 Assembly View", use_container_width=True):
        st.session_state.current_page = "ASSEMBLY_VIEW"
        st.rerun()

with nav3:
    if st.button("➕ New Inspection", use_container_width=True):
        st.session_state.current_page = "TX_ADD"
        st.rerun()

with nav4:
    if st.button("📚 View Records", use_container_width=True):
        st.session_state.current_page = "TX_VIEW"
        st.rerun()

with nav5:
    if st.button("✏️ Modify", use_container_width=True):
        st.session_state.current_page = "TX_MODIFY"
        st.rerun()


st.divider()


# ============================================================
# 8. ASSEMBLY MASTER - ADD
# ============================================================

if st.session_state.current_page == "ASSEMBLY_ADD":

    show_header(
        "इंसुलेटर असेंबली मास्टर",
        "Insulator Assembly Master",
    )

    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    try:
        station_codes = get_station_codes()
    except Exception as exc:
        show_error("Unable to load station codes.", exc)
        station_codes = []

    col1, col2, col3 = st.columns(3)

    with col1:

        field_label(
            "स्टेशन कोड",
            "Station Code",
        )

        station_options = ["Select City..."] + station_codes + [
            "Other / Enter Manually"
        ]

        selected_station = st.selectbox(
            "Station Code",
            station_options,
            label_visibility="collapsed",
            key="assembly_station",
        )

        manual_station = ""

        if selected_station == "Other / Enter Manually":

            manual_station = st.text_input(
                "Enter Station Code",
                max_chars=8,
                key="manual_station_code",
            ).strip()

            station_code = manual_station.upper()

        elif selected_station == "Select City...":
            station_code = ""

        else:
            station_code = selected_station

    with col2:

        field_label(
            "लोकेशन के बीच",
            "Location Between",
        )

        loc_bet = st.text_input(
            "Location Between",
            max_chars=30,
            label_visibility="collapsed",
            key="assembly_location",
        )

    with col3:

        field_label(
            "एल्बो-टू-सेक्शन के बीच",
            "Elbow-to-Section Between",
        )

        es_bet = st.text_input(
            "Elbow-to-Section Between",
            max_chars=30,
            label_visibility="collapsed",
            key="assembly_section",
        )

    col4, col5, col6 = st.columns(3)

    with col4:

        field_label(
            "इंसुलेटर का मेक (9-टन)",
            "Make Insulator (9-ton)",
        )

        make_9 = st.text_input(
            "Make Insulator 9-ton",
            max_chars=30,
            label_visibility="collapsed",
            key="assembly_make9",
        )

    with col5:

        field_label(
            "इंसुलेटर का मेक स्थिति",
            "Make Insulator Status",
        )

        make_s = st.text_input(
            "Make Insulator Status",
            max_chars=20,
            label_visibility="collapsed",
            key="assembly_makes",
        )

    with col6:

        field_label(
            "स्थिति",
            "Status",
        )

        assembly_status = st.selectbox(
            "Status",
            ["Active", "Inactive"],
            label_visibility="collapsed",
            key="assembly_status",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Generate a code before displaying the code field.
    code_col, button_col = st.columns([2, 1])

    with button_col:

        if st.button(
            "Generate Assembly Code",
            use_container_width=True,
            type="primary",
        ):

            if not station_code:
                st.error("Please select or enter a station code.")
            else:
                st.session_state.generated_assembly_code = (
                    generate_assembly_code(station_code)
                )

    with code_col:

        field_label(
            "इंसुलेटर असेंबली कोड",
            "Insulator Assembly Code",
        )

        assembly_code = st.text_input(
            "Assembly Code",
            value=st.session_state.get(
                "generated_assembly_code", ""
            ),
            max_chars=30,
            placeholder="Click Generate Assembly Code",
            label_visibility="collapsed",
            key="assembly_code_input",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(
        "💾 Save Assembly",
        use_container_width=True,
        type="primary",
    ):

        if not station_code:
            st.error("Please select or enter a Station Code.")

        elif not assembly_code.strip():
            st.error("Please generate an Assembly Code first.")

        elif not loc_bet.strip():
            st.error("Please enter Location Between.")

        elif not es_bet.strip():
            st.error("Please enter Elbow-to-Section Between.")

        elif not make_9.strip():
            st.error("Please enter Make Insulator (9-ton).")

        elif not make_s.strip():
            st.error("Please enter Make Insulator Status.")

        else:

            payload = {
                "ia_code": assembly_code.strip(),
                "stn_cd": station_code.strip(),
                "loc_bet": loc_bet.strip(),
                "es_bet": es_bet.strip(),
                "make_9": make_9.strip(),
                "make_s": make_s.strip(),
                "status": assembly_status,
            }

            try:

                response = (
                    supabase.table(ASSEMBLY_TABLE)
                    .insert(payload)
                    .execute()
                )

                if response.data:

                    st.success(
                        f"Assembly {assembly_code} saved successfully."
                    )

                    st.session_state.generated_assembly_code = ""

                    st.rerun()

                else:
                    st.warning(
                        "No record was returned. Check Supabase "
                        "permissions and the table response."
                    )

            except Exception as exc:
                show_error(
                    "Unable to save assembly. Check whether the "
                    "assembly code already exists.",
                    exc,
                )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# 9. ASSEMBLY MASTER - VIEW
# ============================================================

elif st.session_state.current_page == "ASSEMBLY_VIEW":

    show_header(
        "इंसुलेटर असेंबली रिकॉर्ड",
        "Insulator Assembly Master Records",
    )

    refresh_col, filter_col = st.columns([1, 2])

    with refresh_col:

        if st.button("🔄 Refresh Assemblies"):
            st.rerun()

    try:

        assemblies = get_assemblies()

        if assemblies:

            df = pd.DataFrame(assemblies)

            if "stn_cd" in df.columns:

                with filter_col:

                    station_filter = st.selectbox(
                        "Filter by Station",
                        ["All Stations"] + sorted(
                            df["stn_cd"]
                            .fillna("")
                            .astype(str)
                            .str.strip()
                            .unique()
                            .tolist()
                        ),
                    )

                if station_filter != "All Stations":

                    df = df[
                        df["stn_cd"].astype(str).str.strip()
                        == station_filter
                    ]

            st.success(f"{len(df)} assembly record(s)")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                "⬇️ Download Assembly Records",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="assembly_master.csv",
                mime="text/csv",
            )

        else:
            st.info("No assembly records found.")

    except Exception as exc:
        show_error("Unable to retrieve assemblies.", exc)


# ============================================================
# 10. TRANSACTION - NEW INSPECTION
# ============================================================

elif st.session_state.current_page == "TX_ADD":

    show_header(
        "निरीक्षण रिकॉर्ड जोड़ें",
        "Add Inspection Record",
    )

    try:
        assembly_codes = get_assembly_codes()
    except Exception as exc:
        show_error("Unable to load assembly codes.", exc)
        assembly_codes = []

    if not assembly_codes:

        st.warning(
            "No assemblies found. Add an Insulator Assembly "
            "before creating an inspection record."
        )

    else:

        st.markdown('<div class="main-card">', unsafe_allow_html=True)

        with st.form("new_inspection_form"):

            col1, col2 = st.columns(2)

            with col1:

                field_label(
                    "सिलेक्ट इंसुलेटर असेंबली",
                    "Select Insulator Assembly",
                )

                ia_code = st.selectbox(
                    "Assembly",
                    [PLACEHOLDER] + assembly_codes,
                    label_visibility="collapsed",
                )

            with col2:

                field_label(
                    "तारीख",
                    "Inspection Date",
                )

                inspection_date = st.date_input(
                    "Inspection Date",
                    value=datetime.datetime.now(IST).date(),
                    label_visibility="collapsed",
                )

            st.markdown("### Measurements")

            c1, c2, c3 = st.columns(3)

            with c1:

                field_label(
                    "कॉन्टैक्ट वायर हाइट (मिमी)",
                    "Contact Wire Height (mm)",
                )

                c_w_ht = st.number_input(
                    "Contact Wire Height",
                    min_value=0,
                    step=1,
                    value=0,
                    label_visibility="collapsed",
                )

            with c2:

                field_label(
                    "एनकम्ब्रन्स (मिमी)",
                    "Encumbrance (mm)",
                )

                encum = st.number_input(
                    "Encumbrance",
                    min_value=0,
                    step=1,
                    value=0,
                    label_visibility="collapsed",
                )

            with c3:

                field_label(
                    "रनर गैप (मिमी)",
                    "Runner Gap (mm)",
                )

                run_gap = st.number_input(
                    "Runner Gap",
                    min_value=0,
                    step=1,
                    value=0,
                    label_visibility="collapsed",
                )

            st.markdown("### Observations and Remarks")

            c4, c5, c6 = st.columns(3)

            with c4:

                field_label(
                    "ऑब्जर्वेशन",
                    "Observation Details",
                )

                observation = st.text_area(
                    "Observation",
                    max_chars=100,
                    height=100,
                    label_visibility="collapsed",
                )

            with c5:

                field_label(
                    "किये गये कार्य का विवरण",
                    "Description / Work Done",
                )

                description = st.text_area(
                    "Description",
                    max_chars=100,
                    height=100,
                    label_visibility="collapsed",
                )

            with c6:

                field_label(
                    "टिप्पणी",
                    "Additional Remarks",
                )

                remarks = st.text_area(
                    "Remarks",
                    max_chars=100,
                    height=100,
                    label_visibility="collapsed",
                )

            submitted = st.form_submit_button(
                "Save Inspection Record",
                use_container_width=True,
            )

        if submitted:

            if ia_code == PLACEHOLDER:

                st.error("Please select an Insulator Assembly.")

            else:

                payload = {
                    "ia_code": ia_code,
                    "date": inspection_date.isoformat(),
                    "c_w_ht": int(c_w_ht),
                    "encum": int(encum),
                    "run_gap": int(run_gap),
                    "observation": observation.strip(),
                    "description": description.strip(),
                    "remarks": remarks.strip(),
                    "user_id": USER_ID,
                    "timestamp": datetime.datetime.now(
                        datetime.timezone.utc
                    ).replace(tzinfo=None).isoformat(
                        timespec="microseconds"
                    ),
                    "sup_emp_no": SUPERVISOR_NUMBER,
                    "sup_emp_name": SUPERVISOR_NAME,
                }

                try:

                    response = (
                        supabase.table(TRANSACTION_TABLE)
                        .insert(payload)
                        .execute()
                    )

                    if response.data:

                        st.success(
                            "Inspection record saved successfully."
                        )

                    else:

                        st.warning(
                            "No inserted record was returned. "
                            "Check your database permissions."
                        )

                except Exception as exc:

                    show_error(
                        "Unable to save inspection record.",
                        exc,
                    )

        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# 11. TRANSACTION - VIEW RECORDS
# ============================================================

elif st.session_state.current_page == "TX_VIEW":

    show_header(
        "ऐतिहासिक निरीक्षण रिकॉर्ड",
        "Historical Inspection Records",
    )

    try:

        records = get_transactions()

        if records:

            df = pd.DataFrame(records)

            col1, col2 = st.columns([2, 1])

            with col1:

                search = st.text_input(
                    "Search by Assembly Code",
                    placeholder="Enter assembly code...",
                ).strip().lower()

            with col2:

                if st.button(
                    "🔄 Refresh Records",
                    use_container_width=True,
                ):
                    st.rerun()

            if search:

                df = df[
                    df["ia_code"]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .str.contains(search, regex=False)
                ]

            st.success(
                f"{len(df)} inspection record(s) found."
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                "⬇️ Download Inspection Records as CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=(
                    "inspection_records_"
                    + datetime.date.today().isoformat()
                    + ".csv"
                ),
                mime="text/csv",
            )

        else:

            st.info("No inspection records found.")

    except Exception as exc:

        show_error(
            "Unable to retrieve inspection records.",
            exc,
        )


# ============================================================
# 12. TRANSACTION - MODIFY RECORD
# ============================================================

elif st.session_state.current_page == "TX_MODIFY":

    show_header(
        "निरीक्षण रिकॉर्ड संशोधित करें",
        "Modify Inspection Record",
    )

    try:

        records = get_transactions()

    except Exception as exc:

        show_error("Unable to load inspection records.", exc)
        records = []

    if not records:

        st.info("No inspection records are available to modify.")

    else:

        # The current database schema has no transaction ID column.
        # Select by the assembly code and timestamp of the chosen row.

        record_options = {
            record_label(record): record
            for record in records
        }

        selected_label = st.selectbox(
            "Select the inspection record to modify",
            list(record_options.keys()),
        )

        selected_record = record_options[selected_label]

        st.info(
            "You are editing the selected inspection record. "
            "The assembly code cannot be changed here."
        )

        try:

            selected_date = datetime.date.fromisoformat(
                clean(selected_record.get("date"))[:10]
            )

        except (ValueError, TypeError):

            selected_date = datetime.datetime.now(IST).date()

        with st.form("modify_inspection_form"):

            c1, c2 = st.columns(2)

            with c1:

                field_label(
                    "इंसुलेटर असेंबली कोड",
                    "Insulator Assembly Code",
                )

                st.text_input(
                    "Assembly Code",
                    value=clean(selected_record.get("ia_code")),
                    disabled=True,
                    label_visibility="collapsed",
                )

            with c2:

                field_label(
                    "तारीख",
                    "Inspection Date",
                )

                new_date = st.date_input(
                    "Inspection Date",
                    value=selected_date,
                    label_visibility="collapsed",
                )

            c3, c4, c5 = st.columns(3)

            with c3:

                field_label(
                    "कॉन्टैक्ट वायर हाइट (मिमी)",
                    "Contact Wire Height (mm)",
                )

                new_cw = st.number_input(
                    "Contact Wire Height",
                    min_value=0,
                    value=int(selected_record.get("c_w_ht") or 0),
                    step=1,
                    label_visibility="collapsed",
                )

            with c4:

                field_label(
                    "एनकम्ब्रन्स (मिमी)",
                    "Encumbrance (mm)",
                )

                new_encum = st.number_input(
                    "Encumbrance",
                    min_value=0,
                    value=int(selected_record.get("encum") or 0),
                    step=1,
                    label_visibility="collapsed",
                )

            with c5:

                field_label(
                    "रनर गैप (मिमी)",
                    "Runner Gap (mm)",
                )

                new_gap = st.number_input(
                    "Runner Gap",
                    min_value=0,
                    value=int(selected_record.get("run_gap") or 0),
                    step=1,
                    label_visibility="collapsed",
                )

            c6, c7, c8 = st.columns(3)

            with c6:

                field_label(
                    "ऑब्जर्वेशन",
                    "Observation Details",
                )

                new_observation = st.text_area(
                    "Observation",
                    value=clean(selected_record.get("observation")),
                    max_chars=100,
                    height=100,
                    label_visibility="collapsed",
                )

            with c7:

                field_label(
                    "किये गये कार्य का विवरण",
                    "Description / Work Done",
                )

                new_description = st.text_area(
                    "Description",
                    value=clean(selected_record.get("description")),
                    max_chars=100,
                    height=100,
                    label_visibility="collapsed",
                )

            with c8:

                field_label(
                    "टिप्पणी",
                    "Additional Remarks",
                )

                new_remarks = st.text_area(
                    "Remarks",
                    value=clean(selected_record.get("remarks")),
                    max_chars=100,
                    height=100,
                    label_visibility="collapsed",
                )

            modify_reason = st.text_input(
                "Modification Reason",
                max_chars=30,
                value="System UI Parameter Correction",
            )

            update_clicked = st.form_submit_button(
                "Update Inspection Record",
                use_container_width=True,
            )

        if update_clicked:

            timestamp_value = selected_record.get("timestamp")
            assembly_value = clean(selected_record.get("ia_code"))

            if not timestamp_value or not assembly_value:

                st.error(
                    "The selected record is missing its assembly code "
                    "or timestamp. The record cannot be safely updated."
                )

            else:

                update_payload = {
                    "date": new_date.isoformat(),
                    "c_w_ht": int(new_cw),
                    "encum": int(new_encum),
                    "run_gap": int(new_gap),
                    "observation": new_observation.strip(),
                    "description": new_description.strip(),
                    "remarks": new_remarks.strip(),
                    "modify_id": USER_ID,
                    "modify_rea": modify_reason.strip(),
                }

                try:

                    response = (
                        supabase.table(TRANSACTION_TABLE)
                        .update(update_payload)
                        .eq("ia_code", assembly_value)
                        .eq("timestamp", timestamp_value)
                        .execute()
                    )

                    if response.data:

                        st.success(
                            "Inspection record updated successfully."
                        )

                        st.rerun()

                    else:

                        st.warning(
                            "No record was returned as updated. "
                            "Check your database permissions and confirm "
                            "that the selected record still exists."
                        )

                except Exception as exc:

                    show_error(
                        "Unable to update inspection record.",
                        exc,
                    )


# ============================================================
# 13. FOOTER
# ============================================================

st.divider()

st.caption(
    "KRCL | Insulator Assembly Master & Inspection Management"
)
