
import datetime

import streamlit as st
from supabase import create_client


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Inspection Record Management",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# 2. SUPABASE CONNECTION
# ============================================================

@st.cache_resource
def get_supabase_client():
    """
    Create and cache the Supabase client.

    Expected Streamlit secrets:

    [supabase]
    SUPABASE_URL = "https://your-project.supabase.co"
    SUPABASE_KEY = "your-api-key"
    """

    url = st.secrets["supabase"]["SUPABASE_URL"].strip()
    key = st.secrets["supabase"]["SUPABASE_KEY"].strip()

    if not url or not key:
        raise ValueError("Supabase URL or API key is empty.")

    return create_client(url, key)


try:
    supabase = get_supabase_client()
    connection_error = None

except Exception as exc:
    supabase = None
    connection_error = str(exc)


# ============================================================
# 3. CONSTANTS
# ============================================================

ASSEMBLY_TABLE = "emm_ins_asmbly"
RECORD_TABLE = "emt_ia_maintain"

PLACEHOLDER = "-- असेंबली चुनें --"

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


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
            border: 1px solid #e1e7ef;
            border-radius: 12px;
            padding: 30px;
            background-color: #ffffff;
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.04);
        }

        .form-title {
            text-align: center;
            font-size: 24px;
            font-weight: 700;
            color: #172033;
            margin-bottom: 5px;
        }

        .form-subtitle {
            text-align: center;
            font-size: 17px;
            font-weight: 600;
            color: #344054;
            margin-bottom: 28px;
        }

        .section-heading {
            font-size: 18px;
            font-weight: 700;
            color: #175cd3;
            margin-top: 18px;
            margin-bottom: 12px;
        }

        .field-label-hi {
            font-size: 15px;
            font-weight: 600;
            color: #222222;
            margin-bottom: 0;
        }

        .field-label-en {
            font-size: 12px;
            color: #667085;
            margin-top: 0;
            margin-bottom: 8px;
        }

        div.stButton > button {
            border-radius: 7px;
            min-height: 42px;
            font-weight: 600;
        }

        div[data-testid="stFormSubmitButton"] button {
            background-color: #00875a;
            color: white;
            border: none;
            min-height: 44px;
            font-weight: 700;
        }

        div[data-testid="stFormSubmitButton"] button:hover {
            background-color: #006b46;
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

def fetch_registered_assemblies():
    """Fetch assembly codes from the master table."""

    if supabase is None:
        return []

    try:
        response = (
            supabase.table(ASSEMBLY_TABLE)
            .select("ia_code")
            .execute()
        )

        data = response.data or []

        return sorted(
            {
                str(row["ia_code"]).strip()
                for row in data
                if row.get("ia_code") is not None
                and str(row["ia_code"]).strip()
            }
        )

    except Exception as exc:
        st.error(
            "Unable to load assembly codes from the master table. "
            f"Database error: {exc}"
        )
        return []


def fetch_all_records():
    """Retrieve inspection records from Supabase."""

    response = (
        supabase.table(RECORD_TABLE)
        .select("*")
        .order("timestamp", desc=True)
        .limit(1000)
        .execute()
    )

    return response.data or []


def fetch_latest_record(assembly_code):
    """Fetch the most recent inspection record for an assembly."""

    response = (
        supabase.table(RECORD_TABLE)
        .select("*")
        .eq("ia_code", assembly_code)
        .order("timestamp", desc=True)
        .limit(1)
        .execute()
    )

    records = response.data or []

    return records[0] if records else None


def parse_inspection_date(value):
    """Convert a database date into a Python date."""

    if not value:
        return datetime.date.today()

    if isinstance(value, datetime.datetime):
        return value.date()

    if isinstance(value, datetime.date):
        return value

    try:
        return datetime.date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError):
        return datetime.date.today()


def get_int_value(record, column):
    """Safely read an integer-valued database field."""

    try:
        return int(record.get(column, 0) or 0)
    except (ValueError, TypeError):
        return 0


def show_field_label(hindi, english):
    """Display a bilingual field label."""

    st.markdown(
        f"""
        <div class="field-label-hi">{hindi}</div>
        <div class="field-label-en">{english}</div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 6. APPLICATION HEADER
# ============================================================

st.title("📋 Inspection Record Management")

st.caption(
    "Insulator Assembly Maintenance | Inspection Ledger | "
    "Supabase Database"
)

if connection_error:
    st.error(
        "Supabase connection failed. Check your Streamlit Secrets "
        "and installed package versions."
    )

    with st.expander("Connection error details"):
        st.code(connection_error)

    st.stop()


# ============================================================
# 7. NAVIGATION
# ============================================================

if "current_view" not in st.session_state:
    st.session_state.current_view = "NEW"

nav1, nav2, nav3 = st.columns(3)

with nav1:
    if st.button(
        "➕ New Inspection",
        use_container_width=True,
        key="nav_new",
    ):
        st.session_state.current_view = "NEW"
        st.rerun()

with nav2:
    if st.button(
        "📚 View Records",
        use_container_width=True,
        key="nav_view",
    ):
        st.session_state.current_view = "VIEW"
        st.rerun()

with nav3:
    if st.button(
        "✏️ Modify Record",
        use_container_width=True,
        key="nav_modify",
    ):
        st.session_state.current_view = "MODIFY"
        st.rerun()


st.divider()


# ============================================================
# 8. VIEW RECORDS
# ============================================================

if st.session_state.current_view == "VIEW":

    st.markdown(
        '<div class="form-title">ऐतिहासिक निरीक्षण रिकॉर्ड</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="form-subtitle">Historical Inspection Records</div>',
        unsafe_allow_html=True,
    )

    refresh_col, info_col = st.columns([1, 3])

    with refresh_col:
        refresh = st.button(
            "🔄 Refresh Records",
            use_container_width=True,
        )

    if refresh:
        st.rerun()

    with st.spinner("Loading inspection records..."):

        try:
            records = fetch_all_records()

            if records:
                st.success(
                    f"Loaded {len(records)} inspection record(s)."
                )

                st.dataframe(
                    records,
                    use_container_width=True,
                    hide_index=True,
                )

                csv_data = (
                    __import__("pandas")
                    .DataFrame(records)
                    .to_csv(index=False)
                    .encode("utf-8")
                )

                st.download_button(
                    label="⬇️ Download Records as CSV",
                    data=csv_data,
                    file_name=(
                        "inspection_records_"
                        + datetime.date.today().isoformat()
                        + ".csv"
                    ),
                    mime="text/csv",
                )

            else:
                st.info("No inspection records were found.")

        except Exception as exc:
            st.error(
                "Unable to retrieve inspection records. "
                f"Database error: {exc}"
            )


# ============================================================
# 9. NEW INSPECTION / MODIFY RECORD
# ============================================================

else:

    is_modify = st.session_state.current_view == "MODIFY"

    if is_modify:

        st.markdown(
            '<div class="form-title">निरीक्षण रिकॉर्ड संशोधित करें</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="form-subtitle">Modify Inspection Record</div>',
            unsafe_allow_html=True,
        )

        st.warning(
            "Select an assembly code to load its latest inspection record."
        )

        search_code = st.text_input(
            "Enter Assembly Code / असेंबली कोड",
            key="modify_search_code",
        ).strip()

        loaded_record = None

        if search_code:

            try:
                with st.spinner("Searching for the latest record..."):
                    loaded_record = fetch_latest_record(search_code)

                if loaded_record:
                    st.success(
                        f"Latest inspection record for "
                        f"{search_code} loaded."
                    )
                else:
                    st.warning(
                        "No inspection record was found for this assembly."
                    )

            except Exception as exc:
                st.error(f"Record search failed: {exc}")

        if not loaded_record:
            st.info(
                "Enter an assembly code with an existing inspection "
                "record to enable modification."
            )
            st.stop()

        target_row_id = loaded_record.get("id")

        if target_row_id is None:
            st.error(
                "The selected record does not contain an 'id' column. "
                "A unique record identifier is required for safe updates."
            )
            st.stop()

        default_ia = str(
            loaded_record.get("ia_code", search_code)
        )

        default_date = parse_inspection_date(
            loaded_record.get("date")
        )

        default_cw = get_int_value(loaded_record, "c_w_ht")
        default_encum = get_int_value(loaded_record, "encum")
        default_gap = get_int_value(loaded_record, "run_gap")

        default_obs = str(
            loaded_record.get("observation") or ""
        )

        default_desc = str(
            loaded_record.get("description") or ""
        )

        default_rem = str(
            loaded_record.get("remarks") or ""
        )

    else:

        st.markdown(
            '<div class="form-title">निरीक्षण रिकॉर्ड जोड़ें</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="form-subtitle">Add New Inspection Record</div>',
            unsafe_allow_html=True,
        )

        default_ia = PLACEHOLDER
        default_date = datetime.date.today()

        default_cw = 0
        default_encum = 0
        default_gap = 0

        default_obs = ""
        default_desc = ""
        default_rem = ""

        target_row_id = None


    # --------------------------------------------------------
    # INSPECTION FORM
    # --------------------------------------------------------

    with st.form(
        "transaction_ledger_form",
        clear_on_submit=False,
    ):

        st.markdown(
            '<div class="section-heading">Inspection Details</div>',
            unsafe_allow_html=True,
        )

        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:

            show_field_label(
                "सिलेक्ट इंसुलेटर असेंबली",
                "Select Insulator Assembly",
            )

            assembly_options = fetch_registered_assemblies()

            if default_ia not in assembly_options:
                assembly_options.insert(0, default_ia)

            if PLACEHOLDER not in assembly_options:
                assembly_options.insert(0, PLACEHOLDER)

            selected_index = assembly_options.index(default_ia)

            ia_code = st.selectbox(
                "Assembly",
                options=assembly_options,
                index=selected_index,
                label_visibility="collapsed",
                key=(
                    "modify_assembly_select"
                    if is_modify
                    else "new_assembly_select"
                ),
            )

        with row1_col2:

            show_field_label(
                "तारीख",
                "Inspection Date",
            )

            date_val = st.date_input(
                "Inspection date",
                value=default_date,
                label_visibility="collapsed",
                key=(
                    "modify_date_input"
                    if is_modify
                    else "new_date_input"
                ),
            )


        st.markdown(
            '<div class="section-heading">Measurements</div>',
            unsafe_allow_html=True,
        )

        row2_col1, row2_col2, row2_col3 = st.columns(3)

        with row2_col1:

            show_field_label(
                "कॉन्टैक्ट वायर हाईट (मिमी)",
                "Contact Wire Height (mm)",
            )

            c_w_ht = st.number_input(
                "Contact Wire Height",
                value=default_cw,
                step=1,
                label_visibility="collapsed",
                key=(
                    "modify_cw_input"
                    if is_modify
                    else "new_cw_input"
                ),
            )

        with row2_col2:

            show_field_label(
                "एन्कम्ब्रन्स (मिमी)",
                "Encumbrance (mm)",
            )

            encum = st.number_input(
                "Encumbrance",
                value=default_encum,
                step=1,
                label_visibility="collapsed",
                key=(
                    "modify_encum_input"
                    if is_modify
                    else "new_encum_input"
                ),
            )

        with row2_col3:

            show_field_label(
                "रनर गैप (मिमी)",
                "Runner Gap (mm)",
            )

            run_gap = st.number_input(
                "Runner Gap",
                value=default_gap,
                step=1,
                label_visibility="collapsed",
                key=(
                    "modify_gap_input"
                    if is_modify
                    else "new_gap_input"
                ),
            )


        st.markdown(
            '<div class="section-heading">Observations and Remarks</div>',
            unsafe_allow_html=True,
        )

        row3_col1, row3_col2, row3_col3 = st.columns(3)

        with row3_col1:

            show_field_label(
                "ऑब्जर्वेशन",
                "Observation Details",
            )

            observation = st.text_area(
                "Observation",
                value=default_obs,
                height=110,
                label_visibility="collapsed",
                key=(
                    "modify_obs_input"
                    if is_modify
                    else "new_obs_input"
                ),
            )

        with row3_col2:

            show_field_label(
                "किये गये कार्य का विवरण",
                "Description / Work Done",
            )

            description = st.text_area(
                "Description",
                value=default_desc,
                height=110,
                label_visibility="collapsed",
                key=(
                    "modify_desc_input"
                    if is_modify
                    else "new_desc_input"
                ),
            )

        with row3_col3:

            show_field_label(
                "टिप्पणी",
                "Additional Remarks",
            )

            remarks = st.text_area(
                "Remarks",
                value=default_rem,
                height=110,
                label_visibility="collapsed",
                key=(
                    "modify_remarks_input"
                    if is_modify
                    else "new_remarks_input"
                ),
            )


        st.markdown("<br>", unsafe_allow_html=True)

        if is_modify:
            submit_triggered = st.form_submit_button(
                "Update Inspection Record",
                use_container_width=True,
            )
        else:
            submit_triggered = st.form_submit_button(
                "Save Inspection Record",
                use_container_width=True,
            )


    # --------------------------------------------------------
    # SUBMISSION AND DATABASE OPERATIONS
    # --------------------------------------------------------

    if submit_triggered:

        if ia_code == PLACEHOLDER:
            st.error("Please select a valid Insulator Assembly.")

        else:

            tx_payload = {
                "ia_code": ia_code,
                "date": date_val.isoformat(),
                "c_w_ht": int(c_w_ht),
                "encum": int(encum),
                "run_gap": int(run_gap),
                "observation": observation.strip(),
                "description": description.strip(),
                "remarks": remarks.strip(),
                "user_id": "Omkar_Dev",
                "timestamp": datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat(),
                "sup_emp_no": 204,
                "sup_emp_name": "Supervisor_Alpha",
            }

            try:

                with st.spinner("Saving inspection record..."):

                    if is_modify:

                        # Update only the exact selected record.
                        tx_payload["modify_id"] = "Omkar_Dev"
                        tx_payload["modify_rea"] = (
                            "System UI Parameter Correction"
                        )

                        response = (
                            supabase.table(RECORD_TABLE)
                            .update(tx_payload)
                            .eq("id", target_row_id)
                            .execute()
                        )

                        if not response.data:
                            st.error(
                                "The update returned no modified record. "
                                "Check database permissions and row-level "
                                "security policies."
                            )
                        else:
                            st.success(
                                "Inspection record updated successfully."
                            )

                    else:

                        response = (
                            supabase.table(RECORD_TABLE)
                            .insert(tx_payload)
                            .execute()
                        )

                        if response.data:
                            st.success(
                                "Inspection record saved successfully."
                            )
                        else:
                            st.warning(
                                "The database returned no inserted record. "
                                "Verify the table permissions and response."
                            )

            except Exception as exc:

                st.error(
                    "Database operation failed. "
                    f"Details: {exc}"
                )


# ============================================================
# 10. FOOTER
# ============================================================

st.divider()

st.caption(
    "Inspection Record Management System | "
    "Supabase Database Integration"
)

