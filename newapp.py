
import datetime
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

PLACEHOLDER = "-- असेंबली चुनें --"
STATION_PLACEHOLDER = "-- Select Station --"

USER_ID = "Omkar_Dev"
SUPERVISOR_NUMBER = 204
SUPERVISOR_NAME = "Supervisor_Alpha"

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


# ============================================================
# COMPLETE STATION MASTER
# Names and codes are based on the list supplied by the user.
# Duplicate station codes are retained as supplied.
# ============================================================

STATIONS = [
    # Maharashtra
    {"name": "Roha", "code": "ROHA / RN", "state": "Maharashtra"},
    {"name": "Kolad", "code": "KOL", "state": "Maharashtra"},
    {"name": "Indapur", "code": "INP", "state": "Maharashtra"},
    {"name": "Mangaon", "code": "MNI", "state": "Maharashtra"},
    {"name": "Goregaon Road", "code": "GNO", "state": "Maharashtra"},
    {"name": "Veer", "code": "VEER", "state": "Maharashtra"},
    {"name": "Sape Wamane", "code": "SAPE", "state": "Maharashtra"},
    {"name": "Karanjadi", "code": "KFD", "state": "Maharashtra"},
    {"name": "Vinhere", "code": "VINH", "state": "Maharashtra"},
    {"name": "Diwankhavati", "code": "DWV", "state": "Maharashtra"},
    {"name": "Khed", "code": "KHED", "state": "Maharashtra"},
    {"name": "Anjani", "code": "ANJ", "state": "Maharashtra"},
    {"name": "Chiplun", "code": "CHI", "state": "Maharashtra"},
    {"name": "Kamathe", "code": "KMT", "state": "Maharashtra"},
    {"name": "Sawarda", "code": "SGR / SWA", "state": "Maharashtra"},
    {"name": "Aravali Road", "code": "AVRD", "state": "Maharashtra"},
    {"name": "Sangameshwar Road", "code": "SGR", "state": "Maharashtra"},
    {"name": "Ratnagiri", "code": "RN", "state": "Maharashtra"},
    {"name": "Nivasar", "code": "NVR", "state": "Maharashtra"},
    {"name": "Adavali", "code": "ADVI", "state": "Maharashtra"},
    {"name": "Vilavade", "code": "VID", "state": "Maharashtra"},
    {"name": "Rajapur Road", "code": "RAJP", "state": "Maharashtra"},
    {"name": "Vaibhavwadi Road", "code": "VBW", "state": "Maharashtra"},
    {"name": "Nandgaon Road", "code": "NDD", "state": "Maharashtra"},
    {"name": "Kankavali", "code": "KKW", "state": "Maharashtra"},
    {"name": "Sindhudurg", "code": "SNDD", "state": "Maharashtra"},
    {"name": "Kudal", "code": "KUDL", "state": "Maharashtra"},
    {"name": "Zarap", "code": "ZARP", "state": "Maharashtra"},
    {"name": "Sawantwadi Road", "code": "SWV", "state": "Maharashtra"},
    {"name": "Madure", "code": "MADR", "state": "Maharashtra"},

    # Goa
    {"name": "Pernem", "code": "PERN", "state": "Goa"},
    {"name": "Thivim", "code": "THVM", "state": "Goa"},
    {"name": "Karmali", "code": "KRMI", "state": "Goa"},
    {"name": "Verna", "code": "VNA", "state": "Goa"},
    {"name": "Madgaon Junction", "code": "MAO", "state": "Goa"},
    {"name": "Suravali", "code": "SRI", "state": "Goa"},
    {"name": "Majorda", "code": "MJO", "state": "Goa"},
    {"name": "Balli", "code": "BLLI", "state": "Goa"},
    {"name": "Canacona", "code": "CNO", "state": "Goa"},
    {"name": "Loliem", "code": "LOL", "state": "Goa"},

    # Karnataka
    {"name": "Asnoti", "code": "AT", "state": "Karnataka"},
    {"name": "Karwar", "code": "KAWR", "state": "Karnataka"},
    {"name": "Harwada", "code": "HVRD", "state": "Karnataka"},
    {"name": "Ankola", "code": "ANKL", "state": "Karnataka"},
    {"name": "Gokarna Road", "code": "GOK", "state": "Karnataka"},
    {"name": "Kumta", "code": "KT", "state": "Karnataka"},
    {"name": "Honnavar", "code": "HNA", "state": "Karnataka"},
    {"name": "Manki", "code": "HIL", "state": "Karnataka"},
    {"name": "Murdeshwar", "code": "MRDW", "state": "Karnataka"},
    {"name": "Bhatkal", "code": "BTJL", "state": "Karnataka"},
    {
        "name": "Mookambika Road Byndoor (H)",
        "code": "BYNR",
        "state": "Karnataka",
    },
    {"name": "Bijoor", "code": "BJNR", "state": "Karnataka"},
    {"name": "Senapura", "code": "SEN", "state": "Karnataka"},
    {"name": "Kundapura", "code": "KUDA", "state": "Karnataka"},
    {"name": "Barkur", "code": "BKJ", "state": "Karnataka"},
    {"name": "Udupi", "code": "UD", "state": "Karnataka"},
    {"name": "Innanje", "code": "INJ", "state": "Karnataka"},
    {"name": "Padubidri", "code": "PUD", "state": "Karnataka"},
    {"name": "Nandikoor", "code": "NDKD", "state": "Karnataka"},
    {"name": "Mulki", "code": "MULK", "state": "Karnataka"},
    {"name": "Surathkal", "code": "SLK", "state": "Karnataka"},
    {"name": "Thokur", "code": "TKPK", "state": "Karnataka"},
]


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
    st.error(
        "Supabase connection failed. "
        "Check your Streamlit Secrets configuration."
    )

    with st.expander("Connection details"):
        st.code(str(exc))

    st.stop()


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1100px;
        padding-top: 1.2rem;
        padding-bottom: 3rem;
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

    .field-label-hi {
        font-size: 14px;
        font-weight: 650;
        color: #222;
        margin-bottom: 0;
    }

    .field-label-en {
        font-size: 12px;
        color: #667085;
        margin-bottom: 6px;
    }

    div.stButton > button {
        min-height: 40px;
        border-radius: 7px;
        font-weight: 600;
    }

    div[data-testid="stFormSubmitButton"] button {
        min-height: 43px;
        border-radius: 7px;
        background-color: #0ba779;
        border: 0;
        color: white;
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
# COMMON HELPERS
# ============================================================

def label(hindi, english):
    st.markdown(
        f'<div class="field-label-hi">{hindi}</div>'
        f'<div class="field-label-en">{english}</div>',
        unsafe_allow_html=True,
    )


def heading(hindi, english):
    st.markdown(
        f'<div class="page-title">{hindi}</div>'
        f'<div class="page-subtitle">{english}</div>',
        unsafe_allow_html=True,
    )


def clean(value):
    return "" if value is None else str(value).strip()


def show_db_error(message, exc):
    st.error(message)

    with st.expander("Technical details"):
        st.code(str(exc))


def get_assemblies():
    response = (
        supabase.table(ASSEMBLY_TABLE)
        .select("*")
        .order("ia_code")
        .limit(1000)
        .execute()
    )

    return response.data or []


def get_transactions():
    response = (
        supabase.table(TRANSACTION_TABLE)
        .select("*")
        .order("timestamp", desc=True)
        .limit(1000)
        .execute()
    )

    return response.data or []


def assembly_codes():
    return sorted({
        clean(row.get("ia_code"))
        for row in get_assemblies()
        if clean(row.get("ia_code"))
    })


def station_codes():
    """Return station codes already present in the assembly master."""

    return sorted({
        clean(row.get("stn_cd"))
        for row in get_assemblies()
        if clean(row.get("stn_cd"))
    })


def generate_assembly_code(station):
    station = "".join(
        ch for ch in clean(station).upper() if ch.isalnum()
    ) or "KRCL"

    date_part = datetime.datetime.now(IST).strftime("%Y%m%d")

    suffix = "".join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(6)
    )

    return f"IA-{station[:8]}-{date_part}-{suffix}"


def record_label(record):
    return (
        f"{clean(record.get('ia_code'))} | "
        f"{clean(record.get('date'))} | "
        f"{clean(record.get('timestamp'))}"
    )


def station_display(station):
    """Display the station name, station code, and state."""

    return (
        f"{station['name']} | {station['code']} "
        f"| {station['state']}"
    )


def get_station_by_display(display):
    for station in STATIONS:
        if station_display(station) == display:
            return station

    return None


# ============================================================
# APP HEADER AND TWO MAIN MODULES
# ============================================================

st.title("KRCL | Inspection Management System")

st.caption(
    "Insulator Assembly Master • Transaction / Inspection Records"
)

main_module = st.radio(
    "Choose module",
    [
        "Insulator Assembly Master",
        "Transaction / Inspection Records",
    ],
    horizontal=True,
    key="main_module",
)

st.divider()


# ============================================================
# MODULE 1: INSULATOR ASSEMBLY MASTER
# ============================================================

if main_module == "Insulator Assembly Master":

    master_action = st.radio(
        "Assembly Master",
        ["➕ Add", "📋 View"],
        horizontal=True,
        key="master_action",
    )

    st.divider()

    # --------------------------------------------------------
    # MASTER: ADD
    # --------------------------------------------------------

    if master_action == "➕ Add":

        heading(
            "इंसुलेटर असेंबली मास्टर",
            "Insulator Assembly Master",
        )

        st.info(
            f"Station directory loaded: {len(STATIONS)} stations "
            "across Maharashtra, Goa, and Karnataka."
        )

        with st.form("assembly_add_form", clear_on_submit=False):

            # STATION DETAILS

            st.markdown("### Station Details")

            c1, c2 = st.columns(2)

            station_options = [
                station_display(station)
                for station in STATIONS
            ]

            with c1:
                label("स्टेशन का नाम", "Station Name")

                station_choice = st.selectbox(
                    "Station",
                    [STATION_PLACEHOLDER] + station_options,
                    label_visibility="collapsed",
                )

            selected_station = get_station_by_display(station_choice)

            with c2:
                label("राज्य", "State")

                st.text_input(
                    "State",
                    value=(
                        selected_station["state"]
                        if selected_station
                        else ""
                    ),
                    disabled=True,
                    label_visibility="collapsed",
                )

            # AUTOMATICALLY POPULATED STATION CODE

            c3, c4 = st.columns(2)

            with c3:
                label("स्टेशन कोड", "Station Code")

                st.text_input(
                    "Station Code",
                    value=(
                        selected_station["code"]
                        if selected_station
                        else ""
                    ),
                    disabled=True,
                    label_visibility="collapsed",
                )

            with c4:
                label("लोकेशन के बीच", "Location Between")

                loc_bet = st.text_input(
                    "Location Between",
                    max_chars=30,
                    label_visibility="collapsed",
                )

            # ASSEMBLY DETAILS

            st.markdown("### Assembly Details")

            c5, c6, c7 = st.columns(3)

            with c5:
                label(
                    "एल्बो-टू-सेक्शन के बीच",
                    "Elbow-to-Section Between",
                )

                es_bet = st.text_input(
                    "Elbow-to-Section Between",
                    max_chars=30,
                    label_visibility="collapsed",
                )

            with c6:
                label(
                    "इंसुलेटर का मेक (9-टन)",
                    "Make Insulator (9-ton)",
                )

                make_9 = st.text_input(
                    "Make Insulator 9-ton",
                    max_chars=30,
                    label_visibility="collapsed",
                )

            with c7:
                label(
                    "इंसुलेटर का मेक स्थिति",
                    "Make Insulator Status",
                )

                make_s = st.text_input(
                    "Make Insulator Status",
                    max_chars=20,
                    label_visibility="collapsed",
                )

            c8, c9 = st.columns(2)

            with c8:
                label("स्थिति", "Status")

                status = st.selectbox(
                    "Status",
                    ["Active", "Inactive"],
                    label_visibility="collapsed",
                )

            with c9:
                label(
                    "इंसुलेटर असेंबली कोड",
                    "Generated Assembly Code",
                )

                generated_code = st.text_input(
                    "Generated Assembly Code",
                    value="Generated automatically after selecting a station",
                    disabled=True,
                    label_visibility="collapsed",
                )

            # BUTTON

            submitted = st.form_submit_button(
                "Generate and Save Assembly",
                use_container_width=True,
            )

        # PROCESS FORM SUBMISSION

        if submitted:

            if not selected_station:
                st.error("Please select a valid station.")

            elif not loc_bet.strip():
                st.error("Please enter Location Between.")

            elif not es_bet.strip():
                st.error("Please enter Elbow-to-Section Between.")

            elif not make_9.strip():
                st.error("Please enter Make Insulator (9-ton).")

            elif not make_s.strip():
                st.error("Please enter Make Insulator Status.")

            else:

                # Use the full station name for code generation.
                new_assembly_code = generate_assembly_code(
                    selected_station["name"]
                )

                payload = {
                    "ia_code": new_assembly_code,
                    "stn_cd": selected_station["code"],
                    "loc_bet": loc_bet.strip(),
                    "es_bet": es_bet.strip(),
                    "make_9": make_9.strip(),
                    "make_s": make_s.strip(),
                    "status": status,
                }

                try:
                    result = (
                        supabase.table(ASSEMBLY_TABLE)
                        .insert(payload)
                        .execute()
                    )

                    if result.data:
                        st.success(
                            "Assembly saved successfully."
                        )

                        st.code(
                            f"Assembly Code: {new_assembly_code}\n"
                            f"Station: {selected_station['name']}\n"
                            f"Station Code: {selected_station['code']}\n"
                            f"State: {selected_station['state']}"
                        )

                    else:
                        st.warning(
                            "No inserted record was returned. "
                            "Please check database permissions."
                        )

                except Exception as exc:
                    show_db_error(
                        "Unable to save assembly.",
                        exc,
                    )

    # --------------------------------------------------------
    # MASTER: VIEW
    # --------------------------------------------------------

    else:

        heading(
            "इंसुलेटर असेंबली रिकॉर्ड",
            "Insulator Assembly Master Records",
        )

        col_refresh, col_filter = st.columns([1, 2])

        with col_refresh:
            if st.button(
                "🔄 Refresh Assemblies",
                use_container_width=True,
            ):
                st.rerun()

        try:
            rows = get_assemblies()

            if not rows:
                st.info("No assembly records found.")

            else:
                df = pd.DataFrame(rows)

                with col_filter:

                    filters = ["All Stations"]

                    if "stn_cd" in df.columns:
                        filters += sorted(
                            df["stn_cd"]
                            .fillna("")
                            .astype(str)
                            .str.strip()
                            .unique()
                            .tolist()
                        )

                    chosen_station = st.selectbox(
                        "Filter by station code",
                        filters,
                    )

                if (
                    chosen_station != "All Stations"
                    and "stn_cd" in df.columns
                ):
                    df = df[
                        df["stn_cd"]
                        .fillna("")
                        .astype(str)
                        .str.strip()
                        == chosen_station
                    ]

                # Add station name and state for display.
                station_lookup = {
                    station["code"]: station
                    for station in STATIONS
                }

                if "stn_cd" in df.columns:

                    df.insert(
                        1,
                        "station_name",
                        df["stn_cd"].apply(
                            lambda code: (
                                station_lookup.get(
                                    clean(code), {}
                                ).get("name", "Unknown station")
                            )
                        ),
                    )

                    df.insert(
                        2,
                        "station_state",
                        df["stn_cd"].apply(
                            lambda code: (
                                station_lookup.get(
                                    clean(code), {}
                                ).get("state", "Unknown")
                            )
                        ),
                    )

                st.success(
                    f"{len(df)} assembly record(s)"
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )

                st.download_button(
                    "⬇️ Download Assembly Records CSV",
                    data=df.to_csv(index=False).encode("utf-8"),
                    file_name="assembly_master.csv",
                    mime="text/csv",
                )

        except Exception as exc:
            show_db_error(
                "Unable to retrieve assembly records.",
                exc,
            )


# ============================================================
# MODULE 2: TRANSACTION / INSPECTION RECORDS
# ============================================================

else:

    transaction_action = st.radio(
        "Transaction",
        [
            "➕ New Inspection",
            "📚 View Records",
            "✏️ Modify",
        ],
        horizontal=True,
        key="transaction_action",
    )

    st.divider()

    # --------------------------------------------------------
    # TRANSACTION: NEW INSPECTION
    # --------------------------------------------------------

    if transaction_action == "➕ New Inspection":

        heading(
            "निरीक्षण रिकॉर्ड जोड़ें",
            "Add Inspection Record",
        )

        try:
            codes = assembly_codes()

        except Exception as exc:
            show_db_error(
                "Unable to load assembly codes.",
                exc,
            )
            codes = []

        if not codes:

            st.warning(
                "No assembly codes found. Open Insulator Assembly "
                "Master and add an assembly before creating an "
                "inspection record."
            )

        else:

            with st.form(
                "new_inspection_form",
                clear_on_submit=False,
            ):

                c1, c2 = st.columns(2)

                with c1:
                    label(
                        "सिलेक्ट इंसुलेटर असेंबली",
                        "Select Insulator Assembly",
                    )

                    ia_code = st.selectbox(
                        "Assembly",
                        [PLACEHOLDER] + codes,
                        label_visibility="collapsed",
                    )

                with c2:
                    label("तारीख", "Inspection Date")

                    inspection_date = st.date_input(
                        "Inspection Date",
                        value=datetime.datetime.now(IST).date(),
                        label_visibility="collapsed",
                    )

                # Show station details for selected assembly.
                assembly_rows = get_assemblies()

                selected_assembly = next(
                    (
                        row
                        for row in assembly_rows
                        if clean(row.get("ia_code")) == ia_code
                    ),
                    {},
                )

                station_code = clean(
                    selected_assembly.get("stn_cd")
                )

                station_details = next(
                    (
                        station
                        for station in STATIONS
                        if station["code"] == station_code
                    ),
                    None,
                )

                if ia_code != PLACEHOLDER:

                    if station_details:

                        st.info(
                            f"Station: {station_details['name']} | "
                            f"Code: {station_details['code']} | "
                            f"State: {station_details['state']}"
                        )

                    else:

                        st.info(
                            f"Station Code: {station_code or 'Not recorded'}"
                        )

                st.markdown("#### Measurements")

                c3, c4, c5 = st.columns(3)

                with c3:
                    label(
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

                with c4:
                    label(
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

                with c5:
                    label(
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

                st.markdown(
                    "#### Observations and Remarks"
                )

                c6, c7, c8 = st.columns(3)

                with c6:
                    label(
                        "ऑब्जर्वेशन",
                        "Observation Details",
                    )

                    observation = st.text_area(
                        "Observation",
                        max_chars=100,
                        height=100,
                        label_visibility="collapsed",
                    )

                with c7:
                    label(
                        "किये गये कार्य का विवरण",
                        "Description / Work Done",
                    )

                    description = st.text_area(
                        "Description",
                        max_chars=100,
                        height=100,
                        label_visibility="collapsed",
                    )

                with c8:
                    label(
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

                    st.error(
                        "Please select an Insulator Assembly."
                    )

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
                        ).isoformat(),
                        "sup_emp_no": SUPERVISOR_NUMBER,
                        "sup_emp_name": SUPERVISOR_NAME,
                    }

                    try:

                        result = (
                            supabase.table(TRANSACTION_TABLE)
                            .insert(payload)
                            .execute()
                        )

                        if result.data:

                            st.success(
                                "Inspection record saved successfully."
                            )

                        else:

                            st.warning(
                                "No inserted record was returned. "
                                "Check database permissions."
                            )

                    except Exception as exc:

                        show_db_error(
                            "Unable to save inspection record.",
                            exc,
                        )

    # --------------------------------------------------------
    # TRANSACTION: VIEW RECORDS
    # --------------------------------------------------------

    elif transaction_action == "📚 View Records":

        heading(
            "ऐतिहासिक निरीक्षण रिकॉर्ड",
            "Historical Inspection Records",
        )

        col_search, col_refresh = st.columns([3, 1])

        with col_search:

            search = st.text_input(
                "Search by Assembly Code",
                placeholder="Enter assembly code...",
            ).strip().lower()

        with col_refresh:

            st.write("")

            if st.button(
                "🔄 Refresh",
                use_container_width=True,
            ):
                st.rerun()

        try:

            rows = get_transactions()

            if not rows:

                st.info("No inspection records found.")

            else:

                df = pd.DataFrame(rows)

                if search:

                    df = df[
                        df["ia_code"]
                        .fillna("")
                        .astype(str)
                        .str.strip()
                        .str.lower()
                        .str.contains(search, regex=False)
                    ]

                # Add station details to historical records.
                assembly_rows = get_assemblies()

                assembly_lookup = {
                    clean(row.get("ia_code")): clean(
                        row.get("stn_cd")
                    )
                    for row in assembly_rows
                }

                station_lookup = {
                    station["code"]: station
                    for station in STATIONS
                }

                if "ia_code" in df.columns:

                    df.insert(
                        1,
                        "station_code",
                        df["ia_code"].apply(
                            lambda code: assembly_lookup.get(
                                clean(code), ""
                            )
                        ),
                    )

                    df.insert(
                        2,
                        "station_name",
                        df["station_code"].apply(
                            lambda code: station_lookup.get(
                                clean(code), {}
                            ).get("name", "Unknown station")
                        ),
                    )

                    df.insert(
                        3,
                        "station_state",
                        df["station_code"].apply(
                            lambda code: station_lookup.get(
                                clean(code), {}
                            ).get("state", "Unknown")
                        ),
                    )

                st.success(
                    f"{len(df)} inspection record(s) found."
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )

                st.download_button(
                    "⬇️ Download Inspection Records CSV",
                    data=df.to_csv(index=False).encode("utf-8"),
                    file_name=(
                        "inspection_records_"
                        + datetime.date.today().isoformat()
                        + ".csv"
                    ),
                    mime="text/csv",
                )

        except Exception as exc:

            show_db_error(
                "Unable to retrieve inspection records.",
                exc,
            )

    # --------------------------------------------------------
    # TRANSACTION: MODIFY
    # --------------------------------------------------------

    else:

        heading(
            "निरीक्षण रिकॉर्ड संशोधित करें",
            "Modify Inspection Record",
        )

        try:
            rows = get_transactions()

        except Exception as exc:
            show_db_error(
                "Unable to load inspection records.",
                exc,
            )
            rows = []

        if not rows:

            st.info(
                "No inspection records are available to modify."
            )

        else:

            options = {}

            for index, row in enumerate(rows):

                key = record_label(row)

                if key in options:
                    key = f"{key} | row {index + 1}"

                options[key] = row

            selected_key = st.selectbox(
                "Select inspection record",
                list(options.keys()),
            )

            record = options[selected_key]

            st.info(
                "The assembly code cannot be changed here. "
                "The selected record is matched using assembly "
                "code and timestamp."
            )

            try:

                current_date = datetime.date.fromisoformat(
                    clean(record.get("date"))[:10]
                )

            except (ValueError, TypeError):

                current_date = datetime.datetime.now(IST).date()

            try:

                current_cw = int(record.get("c_w_ht") or 0)
                current_encum = int(record.get("encum") or 0)
                current_gap = int(record.get("run_gap") or 0)

            except (TypeError, ValueError):

                current_cw, current_encum, current_gap = 0, 0, 0

            with st.form("modify_inspection_form"):

                c1, c2 = st.columns(2)

                with c1:

                    label(
                        "इंसुलेटर असेंबली कोड",
                        "Insulator Assembly Code",
                    )

                    st.text_input(
                        "Assembly Code",
                        value=clean(record.get("ia_code")),
                        disabled=True,
                        label_visibility="collapsed",
                    )

                with c2:

                    label("तारीख", "Inspection Date")

                    new_date = st.date_input(
                        "Inspection Date",
                        value=current_date,
                        label_visibility="collapsed",
                    )

                c3, c4, c5 = st.columns(3)

                with c3:

                    label(
                        "कॉन्टैक्ट वायर हाइट (मिमी)",
                        "Contact Wire Height (mm)",
                    )

                    new_cw = st.number_input(
                        "Contact Wire Height",
                        min_value=0,
                        value=current_cw,
                        step=1,
                        label_visibility="collapsed",
                    )

                with c4:

                    label(
                        "एनकम्ब्रन्स (मिमी)",
                        "Encumbrance (mm)",
                    )

                    new_encum = st.number_input(
                        "Encumbrance",
                        min_value=0,
                        value=current_encum,
                        step=1,
                        label_visibility="collapsed",
                    )

                with c5:

                    label(
                        "रनर गैप (मिमी)",
                        "Runner Gap (mm)",
                    )

                    new_gap = st.number_input(
                        "Runner Gap",
                        min_value=0,
                        value=current_gap,
                        step=1,
                        label_visibility="collapsed",
                    )

                c6, c7, c8 = st.columns(3)

                with c6:

                    label(
                        "ऑब्जर्वेशन",
                        "Observation Details",
                    )

                    new_observation = st.text_area(
                        "Observation",
                        value=clean(record.get("observation")),
                        max_chars=100,
                        height=100,
                        label_visibility="collapsed",
                    )

                with c7:

                    label(
                        "किये गये कार्य का विवरण",
                        "Description / Work Done",
                    )

                    new_description = st.text_area(
                        "Description",
                        value=clean(record.get("description")),
                        max_chars=100,
                        height=100,
                        label_visibility="collapsed",
                    )

                with c8:

                    label(
                        "टिप्पणी",
                        "Additional Remarks",
                    )

                    new_remarks = st.text_area(
                        "Remarks",
                        value=clean(record.get("remarks")),
                        max_chars=100,
                        height=100,
                        label_visibility="collapsed",
                    )

                modify_reason = st.text_input(
                    "Modification Reason",
                    value="System UI Parameter Correction",
                    max_chars=30,
                )

                update_clicked = st.form_submit_button(
                    "Update Inspection Record",
                    use_container_width=True,
                )

            if update_clicked:

                ia_value = clean(record.get("ia_code"))
                timestamp_value = record.get("timestamp")

                if not ia_value or not timestamp_value:

                    st.error(
                        "The selected record is missing its assembly "
                        "code or timestamp; it cannot be safely updated."
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

                        result = (
                            supabase.table(TRANSACTION_TABLE)
                            .update(update_payload)
                            .eq("ia_code", ia_value)
                            .eq("timestamp", timestamp_value)
                            .execute()
                        )

                        if result.data:

                            st.success(
                                "Inspection record updated successfully."
                            )

                            st.rerun()

                        else:

                            st.warning(
                                "No row was returned as updated. "
                                "Check permissions and the timestamp match."
                            )

                    except Exception as exc:

                        show_db_error(
                            "Unable to update inspection record.",
                            exc,
                        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "KRCL | Insulator Assembly Master & Transaction Management System"
)

