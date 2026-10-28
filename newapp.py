
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
STATION_PLACEHOLDER = "Select City..."

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
    st.error("Supabase connection failed.")

    with st.expander("Technical details"):
        st.code(str(exc))

    st.stop()


# ============================================================
# GENERAL HELPERS
# ============================================================

def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def label(hindi_text, english_text):
    return (
        f'<div><p class="field-label-hi">{hindi_text}</p>'
        f'<p class="field-label-en">{english_text}</p></div>'
    )


def generate_assembly_code(station_code):
    station = station_code.split("/")[0].strip().upper()

    suffix = "".join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(4)
    )

    return f"KRCL-{station}-9T-{suffix}"


def station_name_from_code(code):
    for station in STATIONS:
        if station["code"] == code:
            return station["name"]

    return "Unknown"


def fetch_records(table_name, page_size=1000, max_pages=100):
    """
    Retrieve records in pages.

    Results are limited to max_pages * page_size records.
    Database permissions still determine which rows are accessible.
    """
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
    return dataframe.to_csv(index=False).encode("utf-8-sig")


def export_excel(dataframe):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(
            writer,
            index=False,
            sheet_name="Records",
        )

    output.seek(0)
    return output.getvalue()


def show_table_error(message, exc):
    st.error(message)

    with st.expander("Technical details", expanded=True):
        st.code(str(exc))


def get_record_identifier(record):
    """
    Find a likely primary-key column for an update operation.

    This does not guarantee uniqueness. The selected column must
    actually be unique in the database for safe updates.
    """
    preferred = [
        "id",
        "ia_id",
        "transaction_id",
        "inspection_id",
    ]

    for column in preferred:
        if column in record and record[column] is not None:
            return column

    return None


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1200px;
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

    .form-container-box {
        border: 1px solid #ccd5e0;
        border-radius: 12px;
        padding: 20px;
        background-color: #ffffff;
        margin-top: 15px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
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
        min-height: 45px;
        background-color: #0076ba;
        color: white;
        font-weight: 700;
        width: 100%;
        border: 0;
        border-radius: 6px;
        font-size: 16px;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #005c91;
        color: white;
    }

    .footer-credits {
        text-align: center;
        font-size: 11px;
        color: white;
        background-color: #0c3c6c;
        padding: 8px;
        border-radius: 0 0 8px 8px;
        margin-top: 40px;
        letter-spacing: 0.5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# ADD ASSEMBLY
# ============================================================

def add_assembly():
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
                label("इंसुलेटर असेंबली कोड", "Insulator Assembly Code"),
                unsafe_allow_html=True,
            )

            code_display = st.text_input(
                "ia_code_display",
                value="Generated automatically after submission",
                disabled=True,
                label_visibility="collapsed",
            )

        with col2:
            st.markdown(
                label("स्टेशन कोड", "Station Code"),
                unsafe_allow_html=True,
            )

            selected_stn = st.selectbox(
                "stn_cd_select",
                options=[STATION_PLACEHOLDER] + STATION_CODES,
                label_visibility="collapsed",
            )

        with col3:
            st.markdown(
                label("लोकेशन के बीच", "Location Between"),
                unsafe_allow_html=True,
            )

            loc_bet = st.text_input(
                "loc_bet_input",
                placeholder="e.g. Km 42/1-3",
                label_visibility="collapsed",
            )

        col4, col5, col6 = st.columns(3)

        with col4:
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

        with col5:
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

        with col6:
            st.markdown(
                label(
                    "इंसुलेटर का मेक स्थिति",
                    "Make Insulator Status",
                ),
                unsafe_allow_html=True,
            )

            make_status = st.text_input(
                "make_status_input",
                label_visibility="collapsed",
            )

        st.markdown(label("स्थिति", "Status"), unsafe_allow_html=True)

        status = st.selectbox(
            "status_select",
            options=["Active", "Inactive"],
            label_visibility="collapsed",
        )

        submit = st.form_submit_button(
            "Generate Assembly Code and Save",
            use_container_width=True,
        )

    if not submit:
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
        st.error("All assembly fields are required.")
        return

    short_station = selected_stn.split("/")[0].strip()

    try:
        # Retry if a generated code conflicts with a unique constraint.
        for attempt in range(5):
            code = generate_assembly_code(selected_stn)

            payload = {
                "ia_code": code,
                "stn_cd": short_station,
                "loc_bet": clean(loc_bet),
                "es_bet": clean(es_bet),
                "make_9": clean(make_9t),
                "status": status,

                # This assumes emm_ins_asmbly has a make_status column.
                "make_status": clean(make_status),
            }

            try:
                response = (
                    supabase.table(ASSEMBLY_TABLE)
                    .insert(payload)
                    .execute()
                )

                if response.data:
                    st.success("Assembly saved successfully.")
                    st.code(code)
                    st.write(
                        f"**Station:** "
                        f"{station_name_from_code(selected_stn)}"
                    )
                    st.balloons()
                    return

                st.error("Supabase did not confirm the insertion.")
                return

            except Exception as exc:
                error = str(exc).lower()

                if (
                    "23505" in error
                    or "duplicate key" in error
                    or "unique constraint" in error
                ):
                    continue

                raise exc

        st.error(
            "Could not generate a unique assembly code. "
            "Please try again."
        )

    except Exception as exc:
        show_table_error(
            "Failed to save the assembly. "
            "Check the table columns and Supabase permissions.",
            exc,
        )


# ============================================================
# ADD INSPECTION
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
        st.warning(
            "No assembly codes are available. "
            "Register an assembly first."
        )
        return

    with st.form("new_inspection_form"):

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                label(
                    "सिलेक्ट इंसुलेटर असेंबली",
                    "Select Insulator Assembly",
                ),
                unsafe_allow_html=True,
            )

            selected_assembly = st.selectbox(
                "assembly_select",
                options=[PLACEHOLDER] + available_assemblies,
                label_visibility="collapsed",
            )

        with col2:
            st.markdown(
                label("तारीख", "Inspection Date"),
                unsafe_allow_html=True,
            )

            inspection_date = st.date_input(
                "inspection_date_input",
                value=datetime.date.today(),
                label_visibility="collapsed",
            )

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(
                label(
                    "कॉन्टैक्ट वायर हाईट (मिमी)",
                    "Contact Wire Height (mm)",
                ),
                unsafe_allow_html=True,
            )

            contact_wire_height = st.number_input(
                "contact_height",
                min_value=0.0,
                step=1.0,
                label_visibility="collapsed",
            )

        with c2:
            st.markdown(
                label("एन्कम्ब्रन्स (मिमी)", "Encumbrance (mm)"),
                unsafe_allow_html=True,
            )

            encumbrance = st.number_input(
                "encumbrance_val",
                min_value=0.0,
                step=1.0,
                label_visibility="collapsed",
            )

        with c3:
            st.markdown(
                label("रनर गैप (मिमी)", "Runner Gap (mm)"),
                unsafe_allow_html=True,
            )

            runner_gap = st.number_input(
                "runner_gap_val",
                min_value=0.0,
                step=1.0,
                label_visibility="collapsed",
            )

        c4, c5, c6 = st.columns(3)

        with c4:
            st.markdown(
                label("ऑब्जर्वेशन", "Observation Details"),
                unsafe_allow_html=True,
            )

            observations = st.text_area(
                "obs_details",
                height=100,
                label_visibility="collapsed",
            )

        with c5:
            st.markdown(
                label("किये गये कार्य का विवरण", "Description / Work Done"),
                unsafe_allow_html=True,
            )

            work_done = st.text_area(
                "work_details",
                height=100,
                label_visibility="collapsed",
            )

        with c6:
            st.markdown(
                label("टिप्पणी", "Additional Remarks"),
                unsafe_allow_html=True,
            )

            remarks = st.text_area(
                "remarks_details",
                height=100,
                label_visibility="collapsed",
            )

        submit = st.form_submit_button(
            "Save Inspection Record",
            use_container_width=True,
        )

    if not submit:
        return

    if selected_assembly == PLACEHOLDER:
        st.error("Please select an assembly.")
        return

    # These database column names are assumptions based on the form.
    payload = {
        "ia_code": selected_assembly,
        "inspection_date": inspection_date.isoformat(),
        "contact_wire_height": contact_wire_height,
        "encumbrance": encumbrance,
        "runner_gap": runner_gap,
        "observations": clean(observations),
        "work_done": clean(work_done),
        "remarks": clean(remarks),
    }

    try:
        response = (
            supabase.table(TRANSACTION_TABLE)
            .insert(payload)
            .execute()
        )

        if response.data:
            st.success("Inspection record saved successfully.")
            st.json(response.data[0])
            st.balloons()
        else:
            st.error(
                "Supabase did not confirm the inspection insertion."
            )

    except Exception as exc:
        show_table_error(
            "Failed to save the inspection record. "
            "Verify the actual columns in emt_ia_maintain.",
            exc,
        )


# ============================================================
# VIEW RECORDS
# ============================================================

def view_records():
    st.subheader("📚 Database Records")

    record_type = st.radio(
        "Select record type",
        options=["Assemblies", "Inspections"],
        horizontal=True,
        key="view_record_type",
    )

    table_name = (
        ASSEMBLY_TABLE
        if record_type == "Assemblies"
        else TRANSACTION_TABLE
    )

    if st.button("Refresh Records", key="refresh_view_records"):
        st.rerun()

    try:
        with st.spinner("Loading records..."):
            records = fetch_records(table_name)

        if not records:
            st.info(
                "No records were returned from the selected table."
            )
            return

        df = pd.DataFrame(records)

        st.metric("Records Loaded", len(df))

        search = st.text_input(
            "Search all fields",
            placeholder="Enter an assembly code, station or value...",
            key="view_records_search",
        )

        filtered = df.copy()

        if search.strip():
            mask = filtered.apply(
                lambda column: column.astype(str).str.contains(
                    search.strip(),
                    case=False,
                    regex=False,
                    na=False,
                )
            ).any(axis=1)

            filtered = filtered[mask]

        if "stn_cd" in filtered.columns:
            stations = sorted(
                filtered["stn_cd"].dropna().astype(str).unique()
            )

            selected_stations = st.multiselect(
                "Filter by station",
                stations,
                key="view_records_station",
            )

            if selected_stations:
                filtered = filtered[
                    filtered["stn_cd"].astype(str).isin(
                        selected_stations
                    )
                ]

        if "status" in filtered.columns:
            statuses = sorted(
                filtered["status"].dropna().astype(str).unique()
            )

            selected_statuses = st.multiselect(
                "Filter by status",
                statuses,
                key="view_records_status",
            )

            if selected_statuses:
                filtered = filtered[
                    filtered["status"].astype(str).isin(
                        selected_statuses
                    )
                ]

        st.write(f"**Matching records:** {len(filtered)}")

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "Download CSV",
                data=export_csv(filtered),
                file_name=(
                    "krcl_assemblies.csv"
                    if record_type == "Assemblies"
                    else "krcl_inspections.csv"
                ),
                mime="text/csv",
                use_container_width=True,
            )

        with col2:
            try:
                excel_bytes = export_excel(filtered)

                st.download_button(
                    "Download Excel",
                    data=excel_bytes,
                    file_name=(
                        "krcl_assemblies.xlsx"
                        if record_type == "Assemblies"
                        else "krcl_inspections.xlsx"
                    ),
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    use_container_width=True,
                )

            except Exception as exc:
                st.warning("Excel export is unavailable.")
                with st.expander("Technical details"):
                    st.code(str(exc))

    except Exception as exc:
        show_table_error("Could not retrieve database records.", exc)


# ============================================================
# MODIFY DATA
# ============================================================

def modify_data():
    st.subheader("✏️ Modify Existing Records")

    st.warning(
        "Updates are permanent. Confirm the selected record and "
        "the database's unique identifier before submitting changes."
    )

    record_type = st.selectbox(
        "Select table",
        options=["Assemblies", "Inspections"],
        key="modify_record_type",
    )

    table_name = (
        ASSEMBLY_TABLE
        if record_type == "Assemblies"
        else TRANSACTION_TABLE
    )

    try:
        records = fetch_records(table_name)

        if not records:
            st.info("No records are available to modify.")
            return

        df = pd.DataFrame(records)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        # Use an actual unique primary key rather than updating
        # by assembly code or date, which may not be unique.
        candidate_keys = [
            column
            for column in [
                "id",
                "ia_id",
                "transaction_id",
                "inspection_id",
            ]
            if column in df.columns
        ]

        if not candidate_keys:
            st.error(
                "A known unique ID column was not found. "
                "For safety, updates are disabled until the actual "
                "primary-key column is configured."
            )
            st.caption(
                "Check the table's primary key in Supabase and add "
                "its exact column name to candidate_keys."
            )
            return

        id_column = st.selectbox(
            "Unique record ID column",
            options=candidate_keys,
            key="modify_id_column",
        )

        id_values = (
            df[id_column]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_id = st.selectbox(
            "Select record ID",
            options=id_values,
            key="modify_selected_id",
        )

        matching = df[
            df[id_column].astype(str) == selected_id
        ]

        if len(matching) != 1:
            st.error(
                "The selected identifier does not identify exactly "
                "one record. No update will be performed."
            )
            return

        record = matching.iloc[0].to_dict()

        st.markdown("### Current Record")
        st.json(record)

        editable_columns = [
            column
            for column in df.columns
            if column != id_column
            and column not in {"created_at", "updated_at"}
        ]

        selected_column = st.selectbox(
            "Select field to update",
            options=editable_columns,
            key="modify_field",
        )

        current_value = record.get(selected_column)

        st.caption(f"Current value: {current_value}")

        new_value = st.text_area(
            "Enter new value",
            value=(
                ""
                if current_value is None
                else str(current_value)
            ),
            key="modify_new_value",
        )

        confirm = st.checkbox(
            "I confirm that this record and change are correct.",
            key="modify_confirm",
        )

        if st.button(
            "Update Record",
            type="primary",
            key="modify_submit",
        ):
            if not confirm:
                st.error("Please confirm the update.")
                return

            # Avoid silently changing numeric columns into strings.
            if pd.api.types.is_numeric_dtype(df[selected_column]):
                try:
                    if new_value.strip() == "":
                        st.error(
                            "A numeric field cannot be left empty "
                            "using this editor."
                        )
                        return

                    if pd.api.types.is_integer_dtype(
                        df[selected_column]
                    ):
                        converted_value = int(new_value)
                    else:
                        converted_value = float(new_value)

                except ValueError:
                    st.error("Enter a valid numeric value.")
                    return
            else:
                converted_value = new_value

            try:
                response = (
                    supabase.table(table_name)
                    .update({selected_column: converted_value})
                    .eq(id_column, record[id_column])
                    .execute()
                )

                if response.data:
                    st.success("Record updated successfully.")
                    st.json(response.data[0])
                else:
                    st.error(
                        "No updated record was returned. "
                        "The row may not be accessible or the "
                        "update may have been blocked by RLS."
                    )

            except Exception as exc:
                show_table_error(
                    "The database rejected the update.",
                    exc,
                )

    except Exception as exc:
        show_table_error("Unable to load records for modification.", exc)


# ============================================================
# MAIN APPLICATION
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
        "Application Navigation",
        options=[
            "Add Assembly",
            "Add Inspection",
            "View Records",
            "Modify Data",
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="main_navigation",
    )

    st.divider()

    if current_tab == "Add Assembly":
        st.markdown(
            '<div class="form-container-box">',
            unsafe_allow_html=True,
        )
        add_assembly()
        st.markdown("</div>", unsafe_allow_html=True)

    elif current_tab == "Add Inspection":
        st.markdown(
            '<div class="form-container-box">',
            unsafe_allow_html=True,
        )
        add_inspection()
        st.markdown("</div>", unsafe_allow_html=True)

    elif current_tab == "View Records":
        view_records()

    elif current_tab == "Modify Data":
        modify_data()

    st.markdown(
        '<div class="footer-credits">'
        'KONKAN RAILWAY CORPORATION LIMITED | '
        'ASSEMBLY & INSPECTION MANAGEMENT SYSTEM'
        '</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()


