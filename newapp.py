import streamlit as st
import pandas as pd
import string
import secrets
from datetime import date, datetime
from supabase import create_client


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="KRCL Inspection Management System",
    page_icon="🚆",
    layout="wide"
)

st.title("🚆 KRCL Inspection Management System")
st.caption("Konkan Railway Corporation Limited | Inspection Management")


# ============================================================
# SUPABASE CONFIGURATION
# ============================================================

@st.cache_resource
def get_supabase_client():
    """Create a cached Supabase client."""

    supabase_url = st.secrets["supabase"]["SUPABASE_URL"]
    supabase_key = st.secrets["supabase"]["SUPABASE_KEY"]

    return create_client(supabase_url, supabase_key)


try:
    supabase = get_supabase_client()
    database_ready = True

except Exception as error:
    database_ready = False
    supabase = None

    st.error("Unable to connect to Supabase.")
    st.caption(str(error))


# ============================================================
# TABLE NAMES
# ============================================================

ASSEMBLY_TABLE = "emm_ins_asmbly"
TRANSACTION_TABLE = "emt_ia_maintain"


# ============================================================
# STATION CODES
# Codes only — no station names are stored.
# ============================================================

STATION_CODES = [
    # Maharashtra
    "ROHA / RN",
    "KOL",
    "INP",
    "MNI",
    "GNO",
    "VEER",
    "SAPE",
    "KFD",
    "VINH",
    "DWV",
    "KHED",
    "ANJ",
    "CHI",
    "KMT",
    "SGR / SWA",
    "AVRD",
    "SGR",
    "RN",
    "NVR",
    "ADVI",
    "VID",
    "RAJP",
    "VBW",
    "NDD",
    "KKW",
    "SNDD",
    "KUDL",
    "ZARP",
    "SWV",
    "MADR",

    # Goa
    "PERN",
    "THVM",
    "KRMI",
    "VNA",
    "MAO",
    "SRI",
    "MJO",
    "BLLI",
    "CNO",
    "LOL",

    # Karnataka
    "AT",
    "KAWR",
    "HVRD",
    "ANKL",
    "GOK",
    "KT",
    "HNA",
    "HIL",
    "MRDW",
    "BTJL",
    "BYNR",
    "BJNR",
    "SEN",
    "KUDA",
    "BKJ",
    "UD",
    "INJ",
    "PUD",
    "NDKD",
    "MULK",
    "SLK",
    "TKPK",
]


def station_codes():
    """Return the predefined station-code list."""
    return STATION_CODES.copy()


# ============================================================
# DATABASE HELPER FUNCTIONS
# ============================================================

def clean(value):
    """Convert empty values to None and trim text."""
    if value is None:
        return None

    value = str(value).strip()

    return value if value else None


def get_assemblies():
    """Retrieve assembly master records."""

    response = (
        supabase
        .table(ASSEMBLY_TABLE)
        .select("*")
        .order("ia_code")
        .execute()
    )

    return response.data or []


def get_transactions():
    """Retrieve transaction records."""

    response = (
        supabase
        .table(TRANSACTION_TABLE)
        .select("*")
        .execute()
    )

    return response.data or []


def assembly_codes():
    """Get existing assembly codes."""

    records = get_assemblies()

    return sorted(
        {
            str(record["ia_code"])
            for record in records
            if record.get("ia_code") is not None
        }
    )


def generate_assembly_code():
    """Generate a proposed assembly code."""

    letters = string.ascii_uppercase
    random_part = "".join(
        secrets.choice(letters + string.digits)
        for _ in range(5)
    )

    return f"IA-{datetime.now().strftime('%y%m%d')}-{random_part}"


def record_label(record):
    """Build a readable transaction label."""

    return (
        f"Assembly: {record.get('ia_code', 'N/A')} | "
        f"Date: {record.get('date', 'N/A')} | "
        f"ID: {record.get('id', 'N/A')}"
    )


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Insulator Assembly Master",
        "Transaction / Inspection Records",
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.header("Dashboard")

    if not database_ready:
        st.warning("Dashboard data is unavailable until Supabase connects.")

    else:
        try:
            assemblies = get_assemblies()
            transactions = get_transactions()

            col1, col2 = st.columns(2)

            col1.metric(
                "Total Assemblies",
                len(assemblies)
            )

            col2.metric(
                "Total Inspection Records",
                len(transactions)
            )

            st.subheader("Recent Assembly Records")

            if assemblies:
                st.dataframe(
                    pd.DataFrame(assemblies),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No assembly records found.")

            st.subheader("Recent Inspection Records")

            if transactions:
                st.dataframe(
                    pd.DataFrame(transactions),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No inspection records found.")

        except Exception as error:
            st.error(f"Could not load dashboard: {error}")


# ============================================================
# INSULATOR ASSEMBLY MASTER
# ============================================================

elif page == "Insulator Assembly Master":

    st.header("Insulator Assembly Master")

    mode = st.radio(
        "Select Operation",
        ["Add Assembly", "View Assemblies"],
        horizontal=True
    )

    # --------------------------------------------------------
    # ADD ASSEMBLY
    # --------------------------------------------------------

    if mode == "Add Assembly":

        st.subheader("Add New Assembly")

        if not database_ready:
            st.error("Supabase is unavailable.")

        else:
            # Station selection is outside the form so the
            # selected code can be handled reliably.
            selected_station_code = st.selectbox(
                "Station Code",
                options=["Select Station Code"] + station_codes(),
                index=0,
                key="assembly_station_code"
            )

            st.caption(
                "Only the selected station code is stored "
                "in the existing stn_cd database column."
            )

            with st.form("add_assembly_form"):

                col1, col2 = st.columns(2)

                with col1:

                    ia_code = st.text_input(
                        "Assembly Code",
                        placeholder="Enter assembly code"
                    )

                    loc_bet = st.text_input(
                        "Location Between"
                    )

                    make_9 = st.text_input(
                        "Make 9"
                    )

                with col2:

                    es_bet = st.text_input(
                        "ES Between"
                    )

                    make_s = st.text_input(
                        "Make S"
                    )

                    status = st.selectbox(
                        "Status",
                        ["Active", "Inactive"]
                    )

                generate_clicked = st.form_submit_button(
                    "Generate Assembly Code"
                )

                save_clicked = st.form_submit_button(
                    "Save Assembly",
                    type="primary"
                )

            if generate_clicked:

                st.session_state["generated_ia_code"] = (
                    generate_assembly_code()
                )

                st.info(
                    "Generated assembly code: "
                    + st.session_state["generated_ia_code"]
                )

            if save_clicked:

                if selected_station_code == "Select Station Code":
                    st.error("Please select a station code.")

                elif not clean(ia_code):
                    st.error("Please enter an assembly code.")

                else:
                    try:

                        existing_codes = assembly_codes()

                        if ia_code.strip() in existing_codes:
                            st.error(
                                "This assembly code already exists."
                            )

                        else:

                            assembly_data = {
                                "ia_code": ia_code.strip(),
                                "stn_cd": selected_station_code,
                                "loc_bet": clean(loc_bet),
                                "es_bet": clean(es_bet),
                                "make_9": clean(make_9),
                                "make_s": clean(make_s),
                                "status": status,
                            }

                            supabase.table(
                                ASSEMBLY_TABLE
                            ).insert(
                                assembly_data
                            ).execute()

                            st.success(
                                "Assembly saved successfully."
                            )

                            st.write(
                                "**Saved station code:**",
                                selected_station_code
                            )

                    except Exception as error:
                        st.error(
                            f"Could not save assembly: {error}"
                        )

    # --------------------------------------------------------
    # VIEW ASSEMBLIES
    # --------------------------------------------------------

    elif mode == "View Assemblies":

        st.subheader("Assembly Records")

        if not database_ready:
            st.error("Supabase is unavailable.")

        else:
            try:

                assemblies = get_assemblies()

                if assemblies:

                    assembly_df = pd.DataFrame(assemblies)

                    st.dataframe(
                        assembly_df,
                        use_container_width=True,
                        hide_index=True
                    )

                    st.download_button(
                        "Download Assembly Records CSV",
                        data=assembly_df.to_csv(
                            index=False
                        ).encode("utf-8"),
                        file_name="KRCL_Assembly_Master.csv",
                        mime="text/csv"
                    )

                else:
                    st.info("No assembly records found.")

            except Exception as error:
                st.error(
                    f"Could not retrieve assemblies: {error}"
                )


# ============================================================
# TRANSACTION / INSPECTION RECORDS
# ============================================================

elif page == "Transaction / Inspection Records":

    st.header("Transaction / Inspection Records")

    mode = st.radio(
        "Select Operation",
        [
            "New Inspection",
            "View Inspections",
            "Modify Inspection",
        ],
        horizontal=True
    )

    # --------------------------------------------------------
    # NEW INSPECTION
    # --------------------------------------------------------

    if mode == "New Inspection":

        st.subheader("Create Inspection Record")

        if not database_ready:
            st.error("Supabase is unavailable.")

        else:

            try:
                codes = assembly_codes()

            except Exception as error:
                codes = []
                st.error(
                    f"Could not retrieve assembly codes: {error}"
                )

            if not codes:

                st.warning(
                    "No assembly codes are available. "
                    "Add an assembly first."
                )

            else:

                with st.form("new_inspection_form"):

                    ia_code = st.selectbox(
                        "Assembly Code",
                        options=codes
                    )

                    inspection_date = st.date_input(
                        "Inspection Date",
                        value=date.today()
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        c_w_ht = st.text_input(
                            "C/W Height"
                        )

                        encum = st.text_input(
                            "Encumbrance"
                        )

                        run_gap = st.text_input(
                            "Running Gap"
                        )

                    with col2:

                        sup_emp_no = st.text_input(
                            "Supervisor Employee Number"
                        )

                        sup_emp_name = st.text_input(
                            "Supervisor Name"
                        )

                        user_id = st.text_input(
                            "User ID"
                        )

                    observation = st.text_area(
                        "Observation"
                    )

                    description = st.text_area(
                        "Description"
                    )

                    remarks = st.text_area(
                        "Remarks"
                    )

                    submit_inspection = st.form_submit_button(
                        "Save Inspection",
                        type="primary"
                    )

                if submit_inspection:

                    try:

                        transaction_data = {
                            "ia_code": ia_code,
                            "date": inspection_date.isoformat(),
                            "c_w_ht": clean(c_w_ht),
                            "encum": clean(encum),
                            "run_gap": clean(run_gap),
                            "observation": clean(observation),
                            "description": clean(description),
                            "remarks": clean(remarks),
                            "user_id": clean(user_id),
                            "timestamp": datetime.now().isoformat(),
                            "sup_emp_no": clean(sup_emp_no),
                            "sup_emp_name": clean(sup_emp_name),
                        }

                        supabase.table(
                            TRANSACTION_TABLE
                        ).insert(
                            transaction_data
                        ).execute()

                        st.success(
                            "Inspection record saved successfully."
                        )

                    except Exception as error:
                        st.error(
                            f"Could not save inspection: {error}"
                        )

    # --------------------------------------------------------
    # VIEW INSPECTIONS
    # --------------------------------------------------------

    elif mode == "View Inspections":

        st.subheader("Inspection Records")

        if not database_ready:
            st.error("Supabase is unavailable.")

        else:
            try:

                transactions = get_transactions()

                if transactions:

                    transaction_df = pd.DataFrame(
                        transactions
                    )

                    st.dataframe(
                        transaction_df,
                        use_container_width=True,
                        hide_index=True
                    )

                    st.download_button(
                        "Download Inspection Records CSV",
                        data=transaction_df.to_csv(
                            index=False
                        ).encode("utf-8"),
                        file_name="KRCL_Inspection_Records.csv",
                        mime="text/csv"
                    )

                else:
                    st.info("No inspection records found.")

            except Exception as error:
                st.error(
                    f"Could not retrieve inspection records: {error}"
                )

    # --------------------------------------------------------
    # MODIFY INSPECTION
    # --------------------------------------------------------

    elif mode == "Modify Inspection":

        st.subheader("Modify Inspection Record")

        if not database_ready:
            st.error("Supabase is unavailable.")

        else:

            try:

                transactions = get_transactions()

                if not transactions:

                    st.info("No inspection records are available.")

                else:

                    selected_record = st.selectbox(
                        "Select Inspection Record",
                        options=transactions,
                        format_func=record_label
                    )

                    st.write("### Current Record")

                    st.json(selected_record)

                    record_id = selected_record.get("id")

                    if record_id is None:

                        st.error(
                            "The selected record has no 'id' field. "
                            "Check your transaction table schema."
                        )

                    else:

                        with st.form("modify_inspection_form"):

                            modify_observation = st.text_area(
                                "Observation",
                                value=str(
                                    selected_record.get(
                                        "observation"
                                    ) or ""
                                )
                            )

                            modify_description = st.text_area(
                                "Description",
                                value=str(
                                    selected_record.get(
                                        "description"
                                    ) or ""
                                )
                            )

                            modify_remarks = st.text_area(
                                "Remarks",
                                value=str(
                                    selected_record.get(
                                        "remarks"
                                    ) or ""
                                )
                            )

                            modify_reason = st.text_area(
                                "Reason for Modification"
                            )

                            modify_user = st.text_input(
                                "Modified By (User ID)"
                            )

                            save_modification = st.form_submit_button(
                                "Save Changes",
                                type="primary"
                            )

                        if save_modification:

                            if not clean(modify_reason):

                                st.error(
                                    "Please enter the reason "
                                    "for modification."
                                )

                            else:

                                update_data = {
                                    "observation": clean(
                                        modify_observation
                                    ),
                                    "description": clean(
                                        modify_description
                                    ),
                                    "remarks": clean(
                                        modify_remarks
                                    ),
                                    "modify_rea": clean(
                                        modify_reason
                                    ),
                                    "modify_id": clean(
                                        modify_user
                                    ),
                                }

                                try:

                                    supabase.table(
                                        TRANSACTION_TABLE
                                    ).update(
                                        update_data
                                    ).eq(
                                        "id",
                                        record_id
                                    ).execute()

                                    st.success(
                                        "Inspection record updated."
                                    )

                                except Exception as error:

                                    st.error(
                                        "Could not modify the record: "
                                        + str(error)
                                    )

            except Exception as error:

                st.error(
                    f"Could not load records for modification: {error}"
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "KRCL Inspection Management System | "
    "Station selection stores only the station code in stn_cd."
)
