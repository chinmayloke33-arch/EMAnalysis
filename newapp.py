
import datetime
import secrets
import string
import io

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

PLACEHOLDER = "-- असेंबली चुनें --"
STATION_PLACEHOLDER = "-- Select Station Code --"

USER_ID = "Omkar_Dev"
SUPERVISOR_NUMBER = 204
SUPERVISOR_NAME = "Supervisor_Alpha"

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


# ============================================================
# STATION LOOKUP HELPERS
# ============================================================

def clean(value):
    """Safely convert input to a trimmed string."""
    if value is None:
        return ""
    return str(value).strip()


STATION_CODES = list(
    dict.fromkeys(station["code"] for station in STATIONS)
)


def generate_assembly_code(station_code):
    """Generate a unique-looking assembly reference code."""
    clean_station = station_code.split("/")[0].strip().upper()

    random_suffix = "".join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(4)
    )

    return f"KRCL-{clean_station}-9T-{random_suffix}"


def station_name_from_code(code):
    """Find the station name associated with a station code."""
    for station in STATIONS:
        if station["code"] == code:
            return station["name"]
    return "Unknown"


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
    st.error("Unable to connect to Supabase.")
    st.caption(
        "Check the Supabase credentials in your Streamlit secrets."
    )
    with st.expander("Technical details"):
        st.code(str(exc))
    st.stop()


# ============================================================
# DATABASE HELPERS
# ============================================================

def fetch_all_records(table_name, page_size=1000, max_pages=100):
    """
    Fetch records in pages.

    Returns records collected from the accessible rows.
    The maximum scan is page_size * max_pages records.
    """
    records = []

    for page in range(max_pages):
        start = page * page_size
        end = start + page_size - 1

        response = (
            supabase.table(table_name)
            .select("*")
            .range(start, end)
            .execute()
        )

        batch = response.data or []
        records.extend(batch)

        if len(batch) < page_size:
            break

    return records


def dataframe_from_records(records):
    """Convert database records into a display-friendly DataFrame."""
    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)

    # Convert timezone-aware timestamps to readable strings.
    for column in df.columns:
        if (
            pd.api.types.is_datetime64_any_dtype(df[column])
            or column.lower() in {
                "created_at",
                "updated_at",
                "timestamp",
                "date",
                "datetime",
            }
        ):
            try:
                df[column] = df[column].astype(str)
            except Exception:
                pass

    return df


def export_to_excel(dataframe):
    """Create an Excel workbook in memory."""
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(
            writer,
            index=False,
            sheet_name="Records",
        )

    output.seek(0)
    return output.getvalue()


def export_to_csv(dataframe):
    """Create CSV data in memory."""
    return dataframe.to_csv(index=False).encode("utf-8-sig")


def show_database_error(title, exc):
    st.error(title)

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
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    .page-title {
        text-align: center;
        font-size: 26px;
        font-weight: 750;
        color: #172033;
    }

    .page-subtitle {
        text-align: center;
        font-size: 15px;
        color: #475467;
        font-weight: 600;
        margin-bottom: 24px;
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
        margin-bottom: 6px;
    }

    div[data-testid="stFormSubmitButton"] button {
        min-height: 43px;
        background-color: #0ba779;
        color: white;
        font-weight: 700;
        width: 100%;
        border: 0;
        border-radius: 7px;
    }

    div[data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #eaecf0;
        padding: 12px;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def label(hindi_text, english_text):
    return (
        f'<div><p class="field-label-hi">{hindi_text}</p>'
        f'<p class="field-label-en">{english_text}</p></div>'
    )


# ============================================================
# PAGE HEADER
# ============================================================

def show_header():
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


# ============================================================
# ASSEMBLY REGISTRATION FORM
# ============================================================

def assembly_registration():
    st.subheader("📝 Register New Assembly")

    st.info(
        "Enter the assembly details below. "
        "A generated assembly code will be saved to Supabase."
    )

    with st.form("assembly_form", clear_on_submit=False):

        # Row 1
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                label(
                    "इंसुलेटर का मेक (9-टन)",
                    "Make Insulator (9-ton)",
                ),
                unsafe_allow_html=True,
            )

            make_9t = st.text_input(
                "make_9t_input",
                placeholder="Enter make",
                label_visibility="collapsed",
            )

        with col2:
            st.markdown(
                label(
                    "इंसुलेटर का मेक स्थिति",
                    "Make Insulator Status",
                ),
                unsafe_allow_html=True,
            )

            make_status = st.text_input(
                "make_status_input",
                placeholder="Enter make status",
                label_visibility="collapsed",
            )

        with col3:
            st.markdown(
                label("स्थिति", "Status"),
                unsafe_allow_html=True,
            )

            status = st.selectbox(
                "status_input",
                options=["Active", "Inactive"],
                label_visibility="collapsed",
            )

        st.divider()
        st.markdown("### 📍 Location Parameters")

        # Row 2
        col_stn, col_loc, col_es = st.columns(3)

        with col_stn:
            st.markdown(
                label(
                    "स्टेशन कोड चुनें",
                    "Select Station Code",
                ),
                unsafe_allow_html=True,
            )

            selected_stn = st.selectbox(
                "stn_routing",
                options=[STATION_PLACEHOLDER] + STATION_CODES,
                label_visibility="collapsed",
            )

        with col_loc:
            st.markdown(
                label(
                    "लोकेशन के बीच",
                    "Location Between (loc_bet)",
                ),
                unsafe_allow_html=True,
            )

            loc_bet = st.text_input(
                "loc_bet_input",
                placeholder="e.g. Km 42/1-3",
                label_visibility="collapsed",
            )

        with col_es:
            st.markdown(
                label(
                    "एस्केप / स्टेशन के बीच",
                    "ES Between (es_bet)",
                ),
                unsafe_allow_html=True,
            )

            es_bet = st.text_input(
                "es_bet_input",
                placeholder="e.g. ES1-ES2",
                label_visibility="collapsed",
            )

        submitted = st.form_submit_button(
            "Generate and Save Assembly",
            use_container_width=True,
        )

    if submitted:

        # Validation
        if selected_stn == STATION_PLACEHOLDER:
            st.error("Please choose a valid station code.")
            return

        if not clean(make_9t):
            st.error("Please enter Make Insulator (9-ton).")
            return

        if not clean(make_status):
            st.error("Please enter Make Insulator Status.")
            return

        if not clean(loc_bet):
            st.error("Please enter Location Between (loc_bet).")
            return

        if not clean(es_bet):
            st.error("Please enter ES Between (es_bet).")
            return

        short_station_code = selected_stn.split("/")[0].strip()

        # Generate a code and retry if a duplicate is found.
        generated_code = None
        saved = False

        for attempt in range(5):
            candidate = generate_assembly_code(selected_stn)

            payload = {
                "ia_code": candidate,
                "stn_cd": short_station_code,
                "make_9": clean(make_9t),
                "loc_bet": clean(loc_bet),
                "es_bet": clean(es_bet),
                "status": status,
                "make_status": clean(make_status),
            }

            try:
                response = (
                    supabase.table(ASSEMBLY_TABLE)
                    .insert(payload)
                    .execute()
                )

                if response.data:
                    generated_code = candidate
                    saved = True
                    break

                st.error(
                    "Supabase did not confirm the assembly insertion."
                )
                return

            except Exception as exc:
                error_text = str(exc).lower()

                # Retry only when the database reports a duplicate.
                if (
                    "duplicate key" in error_text
                    or "23505" in error_text
                    or "unique constraint" in error_text
                ):
                    continue

                show_database_error(
                    "Unable to save assembly. "
                    "Check the table schema and permissions.",
                    exc,
                )
                return

        if saved:
            st.success("Assembly successfully saved!")
            st.markdown(
                f"**Generated Assembly Code:** `{generated_code}`"
            )
            st.markdown(
                f"**Station:** {station_name_from_code(selected_stn)} "
                f"({short_station_code})"
            )
            st.balloons()

        else:
            st.error(
                "Could not generate a unique assembly code after "
                "multiple attempts. Please try again."
            )


# ============================================================
# ASSEMBLY DATABASE DASHBOARD
# ============================================================

def assembly_dashboard():
    st.subheader("📊 Saved Assembly Records")

    st.caption(
        "View, search, filter and export assemblies stored "
        "in the emm_ins_asmbly table."
    )

    if st.button(
        "🔄 Refresh Assembly Records",
        key="refresh_assemblies",
    ):
        st.cache_data.clear()
        st.rerun()

    try:
        with st.spinner("Loading assembly records..."):
            records = fetch_all_records(ASSEMBLY_TABLE)

        if not records:
            st.warning(
                "No assembly records were returned. "
                "The table may be empty, or your database permissions "
                "may restrict access."
            )
            return

        df = dataframe_from_records(records)

        # Metrics
        total = len(df)

        if "status" in df.columns:
            active_count = (
                df["status"]
                .astype(str)
                .str.strip()
                .str.lower()
                .eq("active")
                .sum()
            )

            inactive_count = (
                df["status"]
                .astype(str)
                .str.strip()
                .str.lower()
                .eq("inactive")
                .sum()
            )
        else:
            active_count = 0
            inactive_count = 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Records Loaded", total)
        c2.metric("Active Assemblies", int(active_count))
        c3.metric("Inactive Assemblies", int(inactive_count))

        st.divider()
        st.markdown("### 🔎 Search and Filters")

        # Search
        search_text = st.text_input(
            "Search assembly records",
            placeholder=(
                "Search assembly code, station code, "
                "location or any displayed field..."
            ),
            key="assembly_search",
        )

        col1, col2 = st.columns(2)

        with col1:
            if "stn_cd" in df.columns:
                station_options = sorted(
                    df["stn_cd"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )
            else:
                station_options = []

            selected_stations = st.multiselect(
                "Filter by station code",
                options=station_options,
                key="assembly_station_filter",
            )

        with col2:
            if "status" in df.columns:
                status_options = sorted(
                    df["status"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )
            else:
                status_options = []

            selected_statuses = st.multiselect(
                "Filter by status",
                options=status_options,
                key="assembly_status_filter",
            )

        filtered_df = df.copy()

        # Apply station filter
        if selected_stations and "stn_cd" in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df["stn_cd"].astype(str).isin(
                    selected_stations
                )
            ]

        # Apply status filter
        if selected_statuses and "status" in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df["status"].astype(str).isin(
                    selected_statuses
                )
            ]

        # Search across all available columns
        if search_text.strip():
            mask = filtered_df.apply(
                lambda column: column.astype(str).str.contains(
                    search_text.strip(),
                    case=False,
                    na=False,
                    regex=False,
                )
            ).any(axis=1)

            filtered_df = filtered_df[mask]

        st.markdown(
            f"**Matching records:** {len(filtered_df)}"
        )

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
        )

        # Export buttons
        st.markdown("### 📥 Export Records")

        exp1, exp2 = st.columns(2)

        with exp1:
            st.download_button(
                "Download CSV",
                data=export_to_csv(filtered_df),
                file_name="krcl_assembly_records.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with exp2:
            try:
                excel_data = export_to_excel(filtered_df)

                st.download_button(
                    "Download Excel",
                    data=excel_data,
                    file_name="krcl_assembly_records.xlsx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    use_container_width=True,
                )

            except Exception as exc:
                st.warning(
                    "Excel export is unavailable. "
                    "Install openpyxl to enable it."
                )

                with st.expander("Technical details"):
                    st.code(str(exc))

    except Exception as exc:
        show_database_error(
            "Could not retrieve assembly records.",
            exc,
        )


# ============================================================
# MAINTENANCE TRANSACTION LOOKUP
# ============================================================

def transaction_dashboard():
    st.subheader("🛠️ Maintenance Transaction Records")

    st.caption(
        "Read-only lookup of records from the emt_ia_maintain table."
    )

    if st.button(
        "🔄 Refresh Maintenance Records",
        key="refresh_transactions",
    ):
        st.cache_data.clear()
        st.rerun()

    try:
        with st.spinner("Loading maintenance transactions..."):
            records = fetch_all_records(TRANSACTION_TABLE)

        if not records:
            st.warning(
                "No maintenance transaction records were returned. "
                "The table may be empty, or your database permissions "
                "may restrict access."
            )
            return

        df = dataframe_from_records(records)

        st.metric("Transaction Records Loaded", len(df))

        st.markdown("### 🔎 Search Transactions")

        search_text = st.text_input(
            "Search maintenance records",
            placeholder=(
                "Enter an assembly code, transaction ID, "
                "station code or another known value..."
            ),
            key="transaction_search",
        )

        filtered_df = df.copy()

        if search_text.strip():
            mask = filtered_df.apply(
                lambda column: column.astype(str).str.contains(
                    search_text.strip(),
                    case=False,
                    na=False,
                    regex=False,
                )
            ).any(axis=1)

            filtered_df = filtered_df[mask]

        st.markdown(
            f"**Matching transactions:** {len(filtered_df)}"
        )

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### 📥 Export Transactions")

        exp1, exp2 = st.columns(2)

        with exp1:
            st.download_button(
                "Download CSV",
                data=export_to_csv(filtered_df),
                file_name="krcl_maintenance_transactions.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with exp2:
            try:
                excel_data = export_to_excel(filtered_df)

                st.download_button(
                    "Download Excel",
                    data=excel_data,
                    file_name="krcl_maintenance_transactions.xlsx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    use_container_width=True,
                )

            except Exception as exc:
                st.warning(
                    "Excel export is unavailable. "
                    "Install openpyxl to enable it."
                )

                with st.expander("Technical details"):
                    st.code(str(exc))

    except Exception as exc:
        show_database_error(
            "Could not retrieve maintenance transaction records.",
            exc,
        )


# ============================================================
# APPLICATION NAVIGATION
# ============================================================

def main():
    show_header()

    st.markdown(
        """
        Use the navigation below to register assemblies,
        view existing records, or search maintenance transactions.
        """
    )

    page = st.radio(
        "Application Navigation",
        options=[
            "Register Assembly",
            "Assembly Database",
            "Maintenance Transactions",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )

    st.divider()

    if page == "Register Assembly":
        assembly_registration()

    elif page == "Assembly Database":
        assembly_dashboard()

    elif page == "Maintenance Transactions":
        transaction_dashboard()

    st.divider()

    st.caption(
        "Konkan Railway Corporation Limited | "
        "Assembly & Inspection Management System"
    )


if __name__ == "__main__":
    main()


