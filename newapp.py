import datetime
import io
import secrets
import string

import pandas as pd
import streamlit as st
from supabase import create_client


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="KRCL | Assembly & Inspection Management",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ASSEMBLY_TABLE = "emm_ins_asmbly"
TRANSACTION_TABLE = "emt_ia_maintain"

PLACEHOLDER = "-- Select Assembly --"
STATION_PLACEHOLDER = "Select Station..."

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


# ============================================================
# COMPLETE STATION MASTER
# ============================================================

STATIONS = [
    # Maharashtra
    {"name": "Roha", "code": "ROHA / RN"},
    {"name": "Kolad", "code": "KOL"},
    {"name": "Indapur", "code": "INP"},
    {"name": "Mangaon", "code": "MNI"},
    {"name": "Goregaon Road", "code": "GNO"},
    {"name": "Veer", "code": "VEER"},
    {"name": "Sape Wamane", "code": "SAPE"},
    {"name": "Karanjadi", "code": "KFD"},
    {"name": "Vinhere", "code": "VINH"},
    {"name": "Diwankhavati", "code": "DWV"},
    {"name": "Khed", "code": "KHED"},
    {"name": "Anjani", "code": "ANJ"},
    {"name": "Chiplun", "code": "CHI"},
    {"name": "Kamathe", "code": "KMT"},
    {"name": "Sawarda", "code": "SGR / SWA"},
    {"name": "Aravali Road", "code": "AVRD"},
    {"name": "Sangameshwar Road", "code": "SGR"},
    {"name": "Ratnagiri", "code": "RN"},
    {"name": "Nivasar", "code": "NVR"},
    {"name": "Adavali", "code": "ADVI"},
    {"name": "Vilavade", "code": "VID"},
    {"name": "Rajapur Road", "code": "RAJP"},
    {"name": "Vaibhavwadi Road", "code": "VBW"},
    {"name": "Nandgaon Road", "code": "NDD"},
    {"name": "Kankavali", "code": "KKW"},
    {"name": "Sindhudurg", "code": "SNDD"},
    {"name": "Kudal", "code": "KUDL"},
    {"name": "Zarap", "code": "ZARP"},
    {"name": "Sawantwadi Road", "code": "SWV"},
    {"name": "Madure", "code": "MADR"},

    # Goa
    {"name": "Pernem", "code": "PERN"},
    {"name": "Thivim", "code": "THVM"},
    {"name": "Karmali", "code": "KRMI"},
    {"name": "Verna", "code": "VNA"},
    {"name": "Madgaon Junction", "code": "MAO"},
    {"name": "Suravali", "code": "SRI"},
    {"name": "Majorda", "code": "MJO"},
    {"name": "Balli", "code": "BLLI"},
    {"name": "Canacona", "code": "CNO"},
    {"name": "Loliem", "code": "LOL"},

    # Karnataka
    {"name": "Asnoti", "code": "AT"},
    {"name": "Karwar", "code": "KAWR"},
    {"name": "Harwada", "code": "HVRD"},
    {"name": "Ankola", "code": "ANKL"},
    {"name": "Gokarna Road", "code": "GOK"},
    {"name": "Kumta", "code": "KT"},
    {"name": "Honnavar", "code": "HNA"},
    {"name": "Manki", "code": "HIL"},
    {"name": "Murdeshwar", "code": "MRDW"},
    {"name": "Bhatkal", "code": "BTJL"},
    {"name": "Mookambika Road Byndoor (H)", "code": "BYNR"},
    {"name": "Bijoor", "code": "BJNR"},
    {"name": "Senapura", "code": "SEN"},
    {"name": "Kundapura", "code": "KUDA"},
    {"name": "Barkur", "code": "BKJ"},
    {"name": "Udupi", "code": "UD"},
    {"name": "Innanje", "code": "INJ"},
    {"name": "Padubidri", "code": "PUD"},
    {"name": "Nandikoor", "code": "NDKD"},
    {"name": "Mulki", "code": "MULK"},
    {"name": "Surathkal", "code": "SLK"},
    {"name": "Thokur", "code": "TKPK"},
]

STATION_CODES = list(
    dict.fromkeys(station["code"] for station in STATIONS)
)


# ============================================================
# SUPABASE CONNECTION
# ============================================================

@st.cache_resource
def get_supabase():
    url = st.secrets["supabase"]["SUPABASE_URL"].strip()
    key = st.secrets["supabase"]["SUPABASE_KEY"].strip()

    return create_client(url, key)


try:
    supabase = get_supabase()
except Exception as exc:
    st.error("Unable to initialize the Supabase connection.")

    with st.expander("Technical details", expanded=True):
        st.code(str(exc))

    st.stop()


# ============================================================
# GENERAL HELPERS
# ============================================================

def clean(value):
    """Safely convert a value to a trimmed string."""
    if value is None:
        return ""

    return str(value).strip()


def label(hindi_text, english_text):
    """Create a bilingual form label."""
    return (
        f'<div>'
        f'<p class="field-label-hi">{hindi_text}</p>'
        f'<p class="field-label-en">{english_text}</p>'
        f'</div>'
    )


def generate_assembly_code(station_code):
    """Generate an assembly code."""
    station = station_code.split("/")[0].strip().upper()

    suffix = "".join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(4)
    )

    return f"KRCL-{station}-9T-{suffix}"


def fetch_records(table_name, page_size=1000, max_pages=100):
    """Fetch records in pages, subject to the configured maximum."""
    records = []

    for page in range(max_pages):
        start = page * page_size

        response = (
            supabase.table(table_name)
            .select("*")
            .range(start, start + page_size - 1)
            .execute()
        )

        batch = response.data or []
        records.extend(batch)

        if len(batch) < page_size:
            break

    return records


def fetch_assembly_codes():
    """Load assembly codes for the inspection form."""
    try:
        records = fetch_records(ASSEMBLY_TABLE)

        codes = [
            clean(row.get("ia_code"))
            for row in records
            if clean(row.get("ia_code"))
        ]

        return sorted(set(codes))

    except Exception as exc:
        st.error("Unable to load assembly codes.")

        with st.expander("Technical details"):
            st.code(str(exc))

        return []


def export_csv(dataframe):
    """Export a DataFrame as a UTF-8 CSV file."""
    return dataframe.to_csv(index=False).encode("utf-8-sig")


def export_excel(dataframe):
    """Export a DataFrame as an Excel workbook."""
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(
            writer,
            index=False,
            sheet_name="Records",
        )

    return output.getvalue()


def show_export_buttons(dataframe, filename_prefix):
    """Display CSV and Excel download buttons."""
    csv_col, excel_col = st.columns(2)

    with csv_col:
        st.download_button(
            label="Download CSV",
            data=export_csv(dataframe),
            file_name=f"{filename_prefix}.csv",
            mime="text/csv",
            key=f"{filename_prefix}_csv",
        )

    with excel_col:
        st.download_button(
            label="Download Excel",
            data=export_excel(dataframe),
            file_name=f"{filename_prefix}.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            key=f"{filename_prefix}_excel",
        )


def show_database_error(message, exc):
    """Display an understandable error with technical details."""
    st.error(message)

    with st.expander("Technical details", expanded=True):
        st.code(str(exc))


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1250px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    .page-title {
        text-align: center;
        font-size: 24px;
        font-weight: 750;
        color: #172033;
        margin-bottom: 2px;
    }

    .page-subtitle {
        text-align: center;
        font-size: 15px;
        color: #475467;
        font-weight: 600;
        margin-bottom: 24px;
    }

    .form-section-header {
        text-align: center;
        margin-bottom: 25px;
    }

    .form-section-hi {
        font-size: 21px;
        font-weight: 700;
        color: #111;
        margin-bottom: 0;
    }

    .form-section-en {
        font-size: 16px;
        color: #555;
        margin-top: -2px;
    }

    .field-label-hi {
        font-size: 14px;
        font-weight: 650;
        color: #222;
        margin-bottom: 0;
    }

    .field-label-en {
        font-size: 12px;
        color: #667085;
        margin-top: -4px;
        margin-bottom: 4px;
    }

    div[data-testid="stFormSubmitButton"] button {
        min-height: 44px;
        background-color: #0076ba;
        color: white;
        font-weight: 700;
        width: 100%;
        border: 0;
        border-radius: 6px;
        font-size: 15px;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #005c91;
        color: white;
    }

    .footer-credits {
        text-align: center;
        font-size: 11px;
        color: #ffffff;
        background-color: #0c3c6c;
        padding: 8px;
        border-radius: 4px;
        margin-top: 40px;
        letter-spacing: 0.5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# ADD ASSEMBLY MASTER
# ============================================================

def add_assembly_master():
    st.markdown(
        '<div class="form-section-header">'
        '<p class="form-section-hi">इंसुलेटर असेंबली मास्टर</p>'
        '<p class="form-section-en">Insulator Assembly Master</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.form("assembly_master_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                label("स्टेशन कोड", "Station Code"),
                unsafe_allow_html=True,
            )

            selected_stn = st.selectbox(
                "stn_cd_select",
                options=[STATION_PLACEHOLDER] + STATION_CODES,
                label_visibility="collapsed",
            )

        with col2:
            st.markdown(
                label("लोकेशन के बीच", "Location Between"),
                unsafe_allow_html=True,
            )

            loc_bet = st.text_input(
                "loc_bet_input",
                placeholder="e.g. Km 42/1-3",
                label_visibility="collapsed",
            )

        with col3:
            st.markdown(
                label(
                    "एलिमेन्ट्री सेक्शन के बीच",
                    "Elementary Section Between",
                ),
                unsafe_allow_html=True,
            )

            es_bet = st.text_input(
                "es_bet_input",
                placeholder="e.g. ES1-ES2",
                label_visibility="collapsed",
            )

        col4, col5, col6 = st.columns(3)

        with col4:
            st.markdown(
                label(
                    "इंसुलेटर का मेक (9-टन)",
                    "Make Insulator (9-ton)",
                ),
                unsafe_allow_html=True,
            )

            make_9t = st.text_input(
                "make_9t_input",
                label_visibility="collapsed",
            )

        with col5:
            st.markdown(
                label(
                    "इन्सुलेटर का मेक (कोअर)",
                    "Make Insulator (Core)",
                ),
                unsafe_allow_html=True,
            )

            make_status = st.text_input(
                "make_status_input",
                label_visibility="collapsed",
            )

        with col6:
            st.markdown(
                label("स्थिति", "Status"),
                unsafe_allow_html=True,
            )

            status = st.selectbox(
                "status_select",
                options=["Active", "Inactive"],
                label_visibility="collapsed",
            )

        submitted = st.form_submit_button("Generate and Save Assembly")

    if not submitted:
        return

    if selected_stn == STATION_PLACEHOLDER:
        st.error("Please select a valid station code.")
        return

    if not all(
        [
            clean(loc_bet),
            clean(es_bet),
            clean(make_9t),
            clean(make_status),
        ]
    ):
        st.error("Please complete all required assembly fields.")
        return

    try:
        existing_codes = set(fetch_assembly_codes())

        # Retry if a randomly generated code already exists.
        for _ in range(10):
            new_code = generate_assembly_code(selected_stn)

            if new_code not in existing_codes:
                break
        else:
            st.error("Could not generate a unique assembly code. Try again.")
            return

        payload = {
            "ia_code": new_code,
            "stn_cd": selected_stn.split("/")[0].strip(),
            "loc_bet": clean(loc_bet),
            "es_bet": clean(es_bet),
            "make_9": clean(make_9t),
            "make_status": clean(make_status),
            "status": status,
        }

        response = (
            supabase.table(ASSEMBLY_TABLE)
            .insert(payload)
            .execute()
        )

        if response.data:
            st.success(
                f"Assembly saved successfully. Assembly Code: {new_code}"
            )
            st.balloons()
        else:
            st.warning(
                "The insert request returned no rows. "
                "Check the database response and table permissions."
            )

    except Exception as exc:
        show_database_error("Failed to save the assembly master record.", exc)


# ============================================================
# ADD INSPECTION TRANSACTION
# ============================================================

def add_inspection():
    st.markdown(
        '<div class="form-section-header">'
        '<p class="form-section-hi">निरीक्षण रिकॉर्ड जोड़ें</p>'
        '<p class="form-section-en">Add Inspection Record</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    available_assemblies = fetch_assembly_codes()
    if not available_assemblies:
        st.warning("No assembly codes were found. Add an Assembly Master record before creating an inspection.")
        return

    with st.form("new_inspection_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(label("इंसुलेटर असेंबली चुनें", "Select Insulator Assembly"), unsafe_allow_html=True)
            selected_assembly = st.selectbox("assembly_select", options=[PLACEHOLDER] + available_assemblies, label_visibility="collapsed")
        with col2:
            st.markdown(label("तारीख", "Inspection / Maintenance Date"), unsafe_allow_html=True)
            inspection_date = st.date_input("inspection_date_input", value=datetime.datetime.now(IST).date(), label_visibility="collapsed")
        with col3:
            st.markdown(label("समय", "Inspection / Maintenance Time"), unsafe_allow_html=True)
            inspection_time = st.time_input("inspection_time_input", value=datetime.datetime.now(IST).time().replace(second=0, microsecond=0), label_visibility="collapsed")

        col4, col5, col6 = st.columns(3)
        with col4:
            st.markdown(label("कर्मचारी संख्या", "Employee Number"), unsafe_allow_html=True)
            employee_no = st.text_input("employee_no_input", label_visibility="collapsed")
        with col5:
            st.markdown(label("पर्यवेक्षक का नाम", "Name of Supervisor"), unsafe_allow_html=True)
            supervisor_name = st.text_input("supervisor_name_input", label_visibility="collapsed")
        with col6:
            st.markdown(label("निरीक्षण स्थिति", "Inspection Status"), unsafe_allow_html=True)
            inspection_status = st.selectbox("inspection_status_input", ["Work in Progress", "Work Completed"], label_visibility="collapsed")

        col7, col8, col9 = st.columns(3)
        with col7:
            st.markdown(label("कॉन्टैक्ट वायर हाइट (मिमी)", "Contact Wire Height (mm)"), unsafe_allow_html=True)
            contact_wire_height = st.number_input("contact_height", min_value=0.0, step=1.0, label_visibility="collapsed")
        with col8:
            st.markdown(label("एनकम्ब्रन्स (मिमी)", "Encumbrance (mm)"), unsafe_allow_html=True)
            encumbrance = st.number_input("encumbrance_val", min_value=0.0, step=1.0, label_visibility="collapsed")
        with col9:
            st.markdown(label("रनर गैप (मिमी)", "Runner Gap (mm)"), unsafe_allow_html=True)
            runner_gap = st.number_input("runner_gap_val", min_value=0.0, step=1.0, label_visibility="collapsed")

        col10, col11 = st.columns(2)
        with col10:
            st.markdown(label("ऑब्जर्वेशन", "Observation Details"), unsafe_allow_html=True)
            observations = st.text_area("obs_details", height=120, label_visibility="collapsed")
        with col11:
            st.markdown(label("किए गए कार्य का विवरण", "Description / Work Done"), unsafe_allow_html=True)
            work_done = st.text_area("work_details", height=120, label_visibility="collapsed")
        st.markdown(label("टिप्पणी", "Additional Remarks"), unsafe_allow_html=True)
        remarks = st.text_area("remarks_details", height=90, label_visibility="collapsed")
        submitted = st.form_submit_button("Save Inspection Record")

    if not submitted:
        return
    if selected_assembly == PLACEHOLDER:
        st.error("Please select an assembly before saving the inspection.")
        return
    if not clean(employee_no):
        st.error("Please enter the employee number.")
        return
    if not clean(supervisor_name):
        st.error("Please enter the supervisor name.")
        return

    transaction_payload = {
        "ia_code": selected_assembly,
        "inspect_date": inspection_date.isoformat(),
        "inspect_time": inspection_time.strftime("%H:%M:%S"),
        "employee_no": clean(employee_no),
        "supervisor_name": clean(supervisor_name),
        "inspection_status": inspection_status,
        "cw_height": float(contact_wire_height),
        "encumbrance": float(encumbrance),
        "runner_gap": float(runner_gap),
        "observation": clean(observations),
        "work_done": clean(work_done),
        "remarks": clean(remarks),
    }
    try:
        response = supabase.table(TRANSACTION_TABLE).insert(transaction_payload).execute()
        if response.data:
            st.success("Inspection transaction saved successfully!")
            if inspection_status == "Work in Progress":
                st.info("Status is Work in Progress. Email notification is not configured in this app yet; configure the approved KRCL email service and employee email lookup to enable it.")
            st.balloons()
        else:
            st.warning("No rows were returned after saving. Verify table permissions and database response.")
    except Exception as exc:
        show_database_error("Failed to save the inspection transaction. Verify that the transaction table contains the required columns.", exc)


# ============================================================
# VIEW AND EXPORT RECORDS
# ============================================================

def view_records():
    st.subheader("Data Record Explorer")

    selection = st.radio(
        "Choose records to view",
        options=[
            "Assembly Master Records",
            "Inspection Transactions",
        ],
        horizontal=True,
    )

    table_name = (
        ASSEMBLY_TABLE
        if selection == "Assembly Master Records"
        else TRANSACTION_TABLE
    )

    if st.button("Refresh Records", key="refresh_view_records"):
        st.rerun()

    try:
        records = fetch_records(table_name)

        if not records:
            st.info(f"No records found in {table_name}.")
            return

        dataframe = pd.DataFrame(records)

        st.caption(f"Source table: {table_name}")
        st.write(f"Total records: **{len(dataframe)}**")

        search_text = st.text_input(
            "Search records",
            placeholder="Enter an assembly code, station code, or value...",
        )

        filtered_df = dataframe.copy()

        if search_text.strip():
            search_text = search_text.strip()

            mask = filtered_df.astype(str).apply(
                lambda column: column.str.contains(
                    search_text,
                    case=False,
                    regex=False,
                    na=False,
                )
            ).any(axis=1)

            filtered_df = filtered_df[mask]

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
        )

        st.write(f"Matching records: **{len(filtered_df)}**")

        if not filtered_df.empty:
            show_export_buttons(
                filtered_df,
                f"{table_name}_export",
            )

    except Exception as exc:
        show_database_error("Unable to retrieve database records.", exc)


# ============================================================
# MODIFY ASSEMBLY MASTER
# ============================================================

def modify_assembly_records():
    st.subheader("Modify Assembly Master Records")

    try:
        records = fetch_records(ASSEMBLY_TABLE)
        if not records:
            st.info("No assembly records are available to modify.")
            return

        dataframe = pd.DataFrame(records)
        if "ia_code" not in dataframe.columns:
            st.error("The assembly table does not contain an ia_code column.")
            return

        codes = sorted(dataframe["ia_code"].dropna().astype(str).unique().tolist())
        if not codes:
            st.info("No assembly codes are available.")
            return

        selected_code = st.selectbox("Select Assembly Code", options=codes)
        matching_rows = dataframe[dataframe["ia_code"].astype(str) == selected_code]
        if matching_rows.empty:
            st.warning("The selected assembly was not found.")
            return
        row = matching_rows.iloc[0]

        st.text_input("Insulator Assembly Code (cannot be changed)", value=selected_code, disabled=True)
        st.text_input("Station Code (cannot be changed)", value=clean(row.get("stn_cd", "")), disabled=True)

        with st.form("edit_assembly_form"):
            new_location = st.text_input("Location Between", value=clean(row.get("loc_bet", "")))
            new_es = st.text_input("Elementary Section Between", value=clean(row.get("es_bet", "")))
            new_make = st.text_input("Make Insulator (9-ton)", value=clean(row.get("make_9", "")))
            new_make_status = st.text_input("Make Insulator (Core)", value=clean(row.get("make_status", "")))

            current_status = clean(row.get("status", "Active"))
            status_options = ["Active", "Inactive"]
            status_index = status_options.index(current_status) if current_status in status_options else 0
            new_status = st.selectbox("Status", options=status_options, index=status_index)
            submitted = st.form_submit_button("Save Assembly Changes")

        if submitted:
            payload = {
                "loc_bet": clean(new_location),
                "es_bet": clean(new_es),
                "make_9": clean(new_make),
                "make_status": clean(new_make_status),
                "status": new_status,
            }
            response = supabase.table(ASSEMBLY_TABLE).update(payload).eq("ia_code", selected_code).execute()
            if response.data:
                st.success("Assembly master updated successfully!")
                st.rerun()
            else:
                st.warning("The update returned no rows. Check database permissions and row-level security.")

    except Exception as exc:
        show_database_error("Unable to modify the assembly record.", exc)



# ============================================================
# VIEW ASSEMBLY MASTER (USED INSIDE MASTER SECTION)
# ============================================================

def view_assembly_master():
    st.subheader("View Insulator Assembly Master Records")
    if st.button("Refresh Assembly Records", key="refresh_assembly_master"):
        st.rerun()

    try:
        records = fetch_records(ASSEMBLY_TABLE)
        if not records:
            st.info("No assembly master records found.")
            return

        dataframe = pd.DataFrame(records)
        search_text = st.text_input(
            "Search assembly records",
            placeholder="Enter assembly code, station code, or location...",
            key="assembly_master_search",
        )
        filtered_df = dataframe.copy()
        if search_text.strip():
            query = search_text.strip()
            mask = filtered_df.astype(str).apply(
                lambda column: column.str.contains(
                    query, case=False, regex=False, na=False
                )
            ).any(axis=1)
            filtered_df = filtered_df[mask]

        st.write(f"Total assemblies: **{len(dataframe)}**")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        st.write(f"Matching assemblies: **{len(filtered_df)}**")
        if not filtered_df.empty:
            show_export_buttons(filtered_df, "assembly_master_records")
    except Exception as exc:
        show_database_error("Unable to retrieve assembly master records.", exc)


# ============================================================
# ASSEMBLY MASTER SECTION: ADD / VIEW / MODIFY
# ============================================================

def assembly_master_section():
    st.markdown(
        '<div class="form-section-header">'
        '<p class="form-section-hi">इंसुलेटर असेंबली मास्टर</p>'
        '<p class="form-section-en">Insulator Assembly Master</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    master_action = st.radio(
        "Assembly Master Options",
        options=["Add Assembly", "View Assemblies", "Modify Assembly"],
        horizontal=True,
        label_visibility="collapsed",
        key="assembly_master_action",
    )
    st.divider()
    if master_action == "Add Assembly":
        add_assembly_master()
    elif master_action == "View Assemblies":
        view_assembly_master()
    else:
        modify_assembly_records()

# ============================================================
# MODIFY INSPECTION TRANSACTIONS
# ============================================================

def modify_inspection_records():
    st.subheader("Modify Inspection Transactions")
    try:
        records = fetch_records(TRANSACTION_TABLE)
        if not records:
            st.info("No inspection transactions are available to modify.")
            return
        dataframe = pd.DataFrame(records)
        required_columns = ["id", "ia_code", "inspect_date"]
        missing_columns = [column for column in required_columns if column not in dataframe.columns]
        if missing_columns:
            st.error("The transaction table is missing columns required by this editor: " + ", ".join(missing_columns))
            st.info("This editor expects each transaction to have a unique id, an ia_code, and an inspect_date.")
            return

        dataframe["display_id"] = (
            dataframe["ia_code"].fillna("").astype(str) + " | "
            + dataframe["inspect_date"].fillna("").astype(str) + " | ID: "
            + dataframe["id"].astype(str)
        )
        selected_display = st.selectbox("Select Inspection Transaction", options=dataframe["display_id"].tolist())
        row = dataframe[dataframe["display_id"] == selected_display].iloc[0]
        record_id = row["id"]

        try:
            existing_date = datetime.date.fromisoformat(str(row.get("inspect_date", ""))[:10])
        except (ValueError, TypeError):
            existing_date = datetime.datetime.now(IST).date()
        try:
            existing_time = datetime.time.fromisoformat(str(row.get("inspect_time", "09:00:00"))[:8])
        except (ValueError, TypeError):
            existing_time = datetime.time(9, 0)

        with st.form("edit_inspection_form"):
            st.write(f"Transaction ID: **{record_id}**")
            st.write(f"Assembly Code: **{row['ia_code']}**")
            st.caption("Inspection date and time are editable. Assembly code is retained as originally recorded.")
            new_date = st.date_input("Inspection / Maintenance Date", value=existing_date)
            new_time = st.time_input("Inspection / Maintenance Time", value=existing_time)
            new_employee = st.text_input("Employee Number", value=clean(row.get("employee_no", "")))
            new_supervisor = st.text_input("Name of Supervisor", value=clean(row.get("supervisor_name", "")))
            status_options = ["Work in Progress", "Work Completed"]
            current_inspection_status = clean(row.get("inspection_status", "Work in Progress"))
            status_index = status_options.index(current_inspection_status) if current_inspection_status in status_options else 0
            new_inspection_status = st.selectbox("Inspection Status", options=status_options, index=status_index)
            new_cw = st.number_input("Contact Wire Height (mm)", min_value=0.0, value=float(row.get("cw_height", 0) or 0), step=1.0)
            new_enc = st.number_input("Encumbrance (mm)", min_value=0.0, value=float(row.get("encumbrance", 0) or 0), step=1.0)
            new_rg = st.number_input("Runner Gap (mm)", min_value=0.0, value=float(row.get("runner_gap", 0) or 0), step=1.0)
            new_obs = st.text_area("Observation Details", value=clean(row.get("observation", "")))
            new_work = st.text_area("Description / Work Done", value=clean(row.get("work_done", "")))
            new_remarks = st.text_area("Additional Remarks", value=clean(row.get("remarks", "")))
            submitted = st.form_submit_button("Save Inspection Changes")

        if submitted:
            if not clean(new_employee) or not clean(new_supervisor):
                st.error("Employee number and supervisor name are required.")
                return
            payload = {
                "inspect_date": new_date.isoformat(),
                "inspect_time": new_time.strftime("%H:%M:%S"),
                "employee_no": clean(new_employee),
                "supervisor_name": clean(new_supervisor),
                "inspection_status": new_inspection_status,
                "cw_height": float(new_cw),
                "encumbrance": float(new_enc),
                "runner_gap": float(new_rg),
                "observation": clean(new_obs),
                "work_done": clean(new_work),
                "remarks": clean(new_remarks),
            }
            response = supabase.table(TRANSACTION_TABLE).update(payload).eq("id", record_id).execute()
            if response.data:
                st.success(f"Inspection transaction {record_id} updated successfully!")
                if new_inspection_status == "Work in Progress":
                    st.info("Status is Work in Progress. Email notification is not configured in this app yet; configure the approved KRCL email service and employee email lookup to enable it.")
                st.rerun()
            else:
                st.warning("The update returned no rows. Check transaction ID, database permissions, and row-level security policies.")
    except Exception as exc:
        show_database_error("Unable to modify the inspection transaction. Verify that the transaction table contains the required columns.", exc)


# ============================================================
# MODIFY RECORDS ROUTER
# ============================================================

def modify_records():
    selection = st.radio(
        "Select record type to modify",
        options=[
            "Assembly Master",
            "Inspection Transactions",
        ],
        horizontal=True,
    )

    if selection == "Assembly Master":
        modify_assembly_records()
    else:
        modify_inspection_records()


# ============================================================
# MAIN APPLICATION ROUTER
# ============================================================

def main():
    st.markdown(
        '<p class="page-title">'
        'कोंकण रेलवे कॉर्पोरेशन लिमिटेड'
        '</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="page-subtitle">'
        'Assembly & Inspection Management System'
        '</p>',
        unsafe_allow_html=True,
    )

    current_tab = st.radio(
        "Application Section",
        options=[
            "New Inspection",
            "Insulator Assembly Master",
            "View Records",
            "Modify Inspection",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )

    st.divider()

    if current_tab == "New Inspection":
        add_inspection()

    elif current_tab == "Insulator Assembly Master":
        assembly_master_section()

    elif current_tab == "View Records":
        view_records()

    elif current_tab == "Modify Inspection":
        modify_inspection_records()

    st.markdown(
        '<div class="footer-credits">'
        'KONKAN RAILWAY CORPORATION LIMITED | '
        'ASSEMBLY & INSPECTION MANAGEMENT SYSTEM'
        '</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
