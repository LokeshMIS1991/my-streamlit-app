import streamlit as st
import pandas as pd
from datetime import datetime
import gspread

# ---------------------------------------------------------
# PAGE CONFIGURATION & INITIAL SETUP
# ---------------------------------------------------------
st.set_page_config(
    page_title="Sidharth Shutter & Automation CRM", 
    page_icon="🛠️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# GOOGLE SHEETS LIVE CONNECTION SETUP
# ---------------------------------------------------------
@st.cache_resource
def get_gspread_client():
    """Google Cloud Credentials ko Streamlit Secrets se load karta hai"""
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        return gspread.service_account_from_dict(creds_dict)
    except Exception as e:
        st.error(f"⚠️ Credentials Parsing Error: {e}")
        return None

sheet_connected = False
ws_master = None
ws_visit = None

try:
    gc = get_gspread_client()
    if gc:
        SHEET_ID = "1UwEGSLm2utcd4asWIRlylf3e11O-lI9OR0j3ptaBSWM"
        sh = gc.open_by_key(SHEET_ID)
        ws_master = sh.worksheet("Master Sheet")
        ws_visit = sh.worksheet("Visit History")
        sheet_connected = True
except Exception as e:
    sheet_connected = False
    st.error(f"⚠️ Google Sheets Connection Issue: {type(e).__name__} - {str(e)}")

# Helper Function: Google Sheets se Live Data Sync/Load karna
def load_data_from_sheets():
    if sheet_connected:
        try:
            m_data = ws_master.get_all_records()
            v_data = ws_visit.get_all_records()
            st.session_state["master_data"] = pd.DataFrame(m_data) if m_data else pd.DataFrame()
            st.session_state["visit_history"] = pd.DataFrame(v_data) if v_data else pd.DataFrame()
        except Exception as err:
            st.warning(f"Could not load sheets automatically: {err}")

# ---------------------------------------------------------
# CUSTOM BRANDING CSS STYLING
# ---------------------------------------------------------
custom_css = """
<style>
    .stApp {
        background-color: #F8FAFC;
    }
    .brand-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #FFFFFF;
        padding: 20px 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border-left: 6px solid #0B3C5D;
        margin-bottom: 25px;
    }
    .brand-title {
        font-size: 26px;
        font-weight: 800;
        color: #0B3C5D;
        margin: 0;
        line-height: 1.2;
    }
    .brand-subtitle {
        font-size: 14px;
        color: #64748B;
        margin-top: 4px;
        margin-bottom: 0;
        font-weight: 500;
    }
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }
    .stButton>button {
        background-color: #0B3C5D;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1D5D8A;
        color: white;
    }
    .job-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        margin-bottom: 15px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# CONSTANTS & LISTS
# ---------------------------------------------------------
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", 
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", 
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", 
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi NCR", "Other"
]

PRODUCT_LIST = [
    "Automatic Rolling Shutters", "Dock Leveller", "Dock Shelter", "High-Speed Roll Up Door", 
    "High-Speed Fold Up Door", "High-Speed Self Repairable Door", "Residential Sectional Doors", 
    "Industrial Sectional Door", "Hermetic Doors", "Fire Exit Door", "Auto Sliding Door", 
    "Motorised Swing Gates", "Motorised Sliding Gates", "Retractable Gates", "Boom Barriers", 
    "Strong Life Shutter Motor", "Manual Shutters", "Wind Shutters", "Spare Part", 
    "Service Charge", "Sensor / Automatic Glass Door", "Motors", "Dock Bumper", "Dock Edge", 
    "Overhead Sectional Door", "Tank Door Shutter", "Gear Shutter", "General purpose Doors", 
    "Hanger Door", "Impact Barrier", "Manual Swing Gate", "Manual Sliding Gate", "Other"
]

PENDING_REASONS = [
    "Material Not Available", "Power Outage / Technical Issue", 
    "Customer Not Available", "Site Not Ready", "Other"
]

PAYMENT_MODES = ["UPI", "Cash", "In Account", "Credit Care of"]

# ---------------------------------------------------------
# INITIALIZE DUMMY SESSION STATE DATA (Fallback)
# ---------------------------------------------------------
if "master_data" not in st.session_state:
    st.session_state["master_data"] = pd.DataFrame([
        {"JS ID": "JS-101", "Date": "01-Jul-2026", "Month": "July", "Client Name": "Lokesh Enterprises", "Project Name": "Warehouse Gate", "Contact Number": "9876543210", "Address": "Malviya Nagar", "Location": "Jaipur", "State": "Rajasthan", "Product": "Automatic Rolling Shutters", "Job Category": "Complaint", "Service Scope": "General Service", "QTY": 2, "Warranty": "Yes", "Office Remark": "Motor sensor issue", "Current Status": "Completed", "Total Visits": 2, "Final Installer": "Hariom", "Close Date": "02-Jul-2026"},
        {"JS ID": "JS-102", "Date": "03-Jul-2026", "Month": "July", "Client Name": "Reliance Retail", "Project Name": "Store Front Entry", "Contact Number": "9823411122", "Address": "Connaught Place", "Location": "Delhi NCR", "State": "Delhi NCR", "Product": "Auto Sliding Door", "Job Category": "New Installation", "Service Scope": "Installation", "QTY": 4, "Warranty": "No", "Office Remark": "Fresh glass door setup", "Current Status": "Completed", "Total Visits": 1, "Final Installer": "Rajesh Sharma", "Close Date": "04-Jul-2026"},
        {"JS ID": "JS-103", "Date": "05-Jul-2026", "Month": "July", "Client Name": "Tata Steel Logistics", "Project Name": "Dock Loading Bay", "Contact Number": "9988776655", "Address": "Sanand Industrial Area", "Location": "Ahmedabad", "State": "Gujarat", "Product": "Dock Leveller", "Job Category": "Complaint", "Service Scope": "General Service", "QTY": 3, "Warranty": "Yes", "Office Remark": "Hydraulic oil leak", "Current Status": "Pending", "Total Visits": 1, "Final Installer": "Suresh Patel", "Close Date": "N/A"},
        {"JS ID": "JS-104", "Date": "06-Jul-2026", "Month": "July", "Client Name": "DLF Cybercity", "Project Name": "Tower B Security Gate", "Contact Number": "9711223344", "Address": "Cyber City Phase 2", "Location": "Gurugram", "State": "Haryana", "Product": "Boom Barriers", "Job Category": "New Installation", "Service Scope": "Dealer", "QTY": 2, "Warranty": "Yes", "Office Remark": "RFID Barrier setup", "Current Status": "Completed", "Total Visits": 1, "Final Installer": "Amit Kumar", "Close Date": "07-Jul-2026"},
        {"JS ID": "JS-105", "Date": "08-Jul-2026", "Month": "July", "Client Name": "Fortis Hospital", "Project Name": "ICU Emergency Wing", "Contact Number": "9123456780", "Address": "Bannnerghatta Road", "Location": "Bengaluru", "State": "Karnataka", "Product": "Hermetic Doors", "Job Category": "Complaint", "Service Scope": "General Service", "QTY": 1, "Warranty": "No", "Office Remark": "Air seal leakage", "Current Status": "Completed", "Total Visits": 2, "Final Installer": "Pradeep Verma", "Close Date": "10-Jul-2026"}
    ])

if "visit_history" not in st.session_state:
    st.session_state["visit_history"] = pd.DataFrame([
        {"JS ID": "JS-101", "Visit No": 1, "Visit Date": "01-Jul-2026", "Installer Name": "Lokesh Kumar", "Status": "Pending", "Reason": "Material Not Available", "Time Spent": "2 Hours", "Payment Mode": "N/A", "Credit Person": "N/A", "Remarks": "Sensor spare part required.", "Doc No": "N/A", "Photo URL": "N/A"},
        {"JS ID": "JS-101", "Visit No": 2, "Visit Date": "02-Jul-2026", "Installer Name": "Hariom", "Status": "Completed", "Reason": "N/A", "Time Spent": "1.5 Hours", "Payment Mode": "UPI", "Credit Person": "N/A", "Remarks": "Replaced sensor, working fine.", "Doc No": "1001", "Photo URL": "https://drive.google.com/sample1.jpg"},
        {"JS ID": "JS-102", "Visit No": 1, "Visit Date": "04-Jul-2026", "Installer Name": "Rajesh Sharma", "Status": "Completed", "Reason": "N/A", "Time Spent": "Full Day", "Payment Mode": "In Account", "Credit Person": "N/A", "Remarks": "Installed 4 glass doors smoothly.", "Doc No": "1002", "Photo URL": "https://drive.google.com/sample2.jpg"},
        {"JS ID": "JS-103", "Visit No": 1, "Visit Date": "05-Jul-2026", "Installer Name": "Suresh Patel", "Status": "Pending", "Reason": "Material Not Available", "Time Spent": "3+ Hours", "Payment Mode": "N/A", "Credit Person": "N/A", "Remarks": "Hydraulic oil seal ordered.", "Doc No": "N/A", "Photo URL": "N/A"}
    ])

if sheet_connected:
    load_data_from_sheets()

# Master Sheet updates automatically when visits change
def sync_master_status(job_id):
    v_df = st.session_state["visit_history"]
    m_df = st.session_state["master_data"]
    job_visits = v_df[v_df["JS ID"] == job_id]
    if not job_visits.empty:
        last_visit = job_visits.iloc[-1]
        m_idx = m_df[m_df["JS ID"] == job_id].index[0]
        st.session_state["master_data"].at[m_idx, "Current Status"] = last_visit["Status"]
        st.session_state["master_data"].at[m_idx, "Final Installer"] = last_visit["Installer Name"]
        st.session_state["master_data"].at[m_idx, "Total Visits"] = len(job_visits)
        if last_visit["Status"] == "Completed":
            st.session_state["master_data"].at[m_idx, "Close Date"] = last_visit["Visit Date"]
        else:
            st.session_state["master_data"].at[m_idx, "Close Date"] = "N/A"

# ---------------------------------------------------------
# SIDEBAR NAVIGATION & BRANDING
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 10px 0;">
            <h2 style="color: #0B3C5D; font-size: 20px; margin: 0; font-weight: 800;">SIDHARTH</h2>
            <p style="color: #32A852; font-size: 11px; margin: 0; font-weight: 700; letter-spacing: 1px;">SHUTTER & AUTOMATION</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    user_role = st.radio(
        "Navigation Options:", 
        [
            "📈 Executive Dashboard",
            "👔 Manager - Create / Edit Job", 
            "🔧 Technician - Job Visit", 
            "📊 View All Jobs (Master Sheet)",
            "📜 View Visit History Database"
        ]
    )
    
    st.markdown("---")
    
    if sheet_connected:
        st.success("🟢 Google Sheets Connected")
    else:
        st.error("🔴 Offline / Local Mode")
        
    if st.button("🔄 Refresh Data from Sheets"):
        load_data_from_sheets()
        st.success("Refreshed with Google Sheets!")
        st.rerun()
        
    st.caption("© Sidharth Shutters & Automations Pvt. Ltd. v1.0")

# ---------------------------------------------------------
# TOP APP HEADER
# ---------------------------------------------------------
st.markdown("""
    <div class="brand-header">
        <div>
            <h1 class="brand-title">Sidharth Shutters & Automations Private Limited</h1>
            <p class="brand-subtitle">Field Operations & Technician Service Operations Portal</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MODULE 1: EXECUTIVE DASHBOARD
# ---------------------------------------------------------
if user_role == "📈 Executive Dashboard":
    st.subheader("📊 Executive Operations & Performance Dashboard")
    
    m_df = st.session_state["master_data"]
    total_jobs = len(m_df)
    completed_jobs = len(m_df[m_df["Current Status"] == "Completed"]) if not m_df.empty and "Current Status" in m_df else 0
    pending_jobs = len(m_df[m_df["Current Status"] == "Pending"]) if not m_df.empty and "Current Status" in m_df else 0
    completion_rate = round((completed_jobs / total_jobs * 100), 1) if total_jobs > 0 else 0
    
    # Key Performance Indicators (KPIs)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("📌 Total JS IDs Generated", total_jobs)
    kpi2.metric("🟢 Completed Jobs", completed_jobs, f"{completion_rate}% Done")
    kpi3.metric("🟡 Pending Jobs", pending_jobs, f"-{round(100 - completion_rate, 1)}%", delta_color="inverse")
    kpi4.metric("⚙️ Service Completion Rate", f"{completion_rate}%")
    
    st.markdown("---")
    
    # Analytics Charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("### 🏷️ Jobs Breakdown by Category")
        if not m_df.empty and "Job Category" in m_df:
            cat_counts = m_df["Job Category"].value_counts().reset_index()
            cat_counts.columns = ["Job Category", "Count"]
            st.bar_chart(cat_counts.set_index("Job Category"), color="#0B3C5D")
            
        st.markdown("### 🗺️ State-wise Operations Distribution")
        if not m_df.empty and "State" in m_df:
            state_counts = m_df["State"].value_counts().reset_index()
            state_counts.columns = ["State", "Total Jobs"]
            st.bar_chart(state_counts.set_index("State"), color="#32A852")

    with chart_col2:
        st.markdown("### 🎯 Jobs Breakdown by Service Scope")
        if not m_df.empty and "Service Scope" in m_df:
            scope_counts = m_df["Service Scope"].value_counts().reset_index()
            scope_counts.columns = ["Service Scope", "Count"]
            st.bar_chart(scope_counts.set_index("Service Scope"), color="#1D5D8A")
            
        st.markdown("### 🛡️ Warranty Coverage Breakdown")
        if not m_df.empty and "Warranty" in m_df:
            war_counts = m_df["Warranty"].value_counts().reset_index()
            war_counts.columns = ["Under Warranty", "Count"]
            st.dataframe(war_counts, use_container_width=True)

# ---------------------------------------------------------
# MODULE 2: MANAGER PORTAL (CREATE / EDIT JOB)
# ---------------------------------------------------------
elif user_role == "👔 Manager - Create / Edit Job":
    st.subheader("📋 Manager Operations Portal")
    
    tab1, tab2 = st.tabs(["➕ Create New JS ID / Job Sheet", "✏️ Search & Edit Job Details"])
    
    # Tab 1: Create New JS ID
    with tab1:
        existing_jobs = len(st.session_state["master_data"])
        auto_job_id = f"JS-{101 + existing_jobs}"
        current_now = datetime.now()
        auto_date = current_now.strftime("%d-%b-%Y")
        auto_month = current_now.strftime("%B")

        st.info(f"⚡ **Auto Generated Details:** JS ID: **{auto_job_id}** | Date: **{auto_date}** | Month: **{auto_month}**")

        with st.form("new_job_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                client_name = st.text_input("Client Name*")
                project_name = st.text_input("Project Name (Optional)", value="N/A")
                contact_number = st.text_input("Contact Number*")
                address = st.text_area("Full Address*")
                location = st.text_input("City / Zone Location*")
                state = st.selectbox("State*", INDIAN_STATES, index=INDIAN_STATES.index("Rajasthan") if "Rajasthan" in INDIAN_STATES else 0)
                
            with col2:
                product = st.selectbox("Product Category*", PRODUCT_LIST)
                job_category = st.selectbox("Job Category (Service Type)*", ["Complaint", "New Installation"])
                service_scope = st.selectbox("Service Scope*", ["Installation", "Dealer", "General Service"])
                qty = st.number_input("Quantity (QTY)*", min_value=1, value=1, step=1)
                warranty = st.selectbox("Warranty*", ["Yes", "No"])
                office_remark = st.text_area("Initial Job Remark / Issue Description (For Installer)*")

            submit_job = st.form_submit_button("🚀 Generate & Save JS ID")
            
            if submit_job:
                if not client_name or not contact_number or not address or not office_remark:
                    st.error("⚠️ Please fill all mandatory fields!")
                else:
                    new_row = {
                        "JS ID": auto_job_id, "Date": auto_date, "Month": auto_month,
                        "Client Name": client_name, "Project Name": project_name, "Contact Number": contact_number,
                        "Address": address, "Location": location, "State": state, "Product": product,
                        "Job Category": job_category, "Service Scope": service_scope, "QTY": qty,
                        "Warranty": warranty, "Office Remark": office_remark, "Current Status": "Pending",
                        "Total Visits": 0, "Final Installer": "Not Assigned", "Close Date": "N/A"
                    }
                    st.session_state["master_data"] = pd.concat([st.session_state["master_data"], pd.DataFrame([new_row])], ignore_index=True)
                    
                    if sheet_connected and ws_master:
                        try:
                            ws_master.append_row(list(new_row.values()))
                        except Exception as e:
                            st.warning(f"Failed to sync to Google Sheet: {e}")
                            
                    st.success(f"🎉 JS ID **{auto_job_id}** Successfully Created & Saved!")

    # Tab 2: Edit Existing Job
    with tab2:
        search_edit_id = st.text_input("Enter JS ID to Search & Edit (e.g. JS-101):").strip().upper()
        if search_edit_id:
            m_df = st.session_state["master_data"]
            match = m_df[m_df["JS ID"] == search_edit_id]
            if not match.empty:
                idx = match.index[0]
                job_row = match.iloc[0]
                
                st.markdown(f"### Editing Job Sheet: **{search_edit_id}**")
                
                with st.form("edit_job_sheet_form"):
                    e_col1, e_col2 = st.columns(2)
                    with e_col1:
                        e_client = st.text_input("Client Name", value=job_row["Client Name"])
                        e_project = st.text_input("Project Name", value=job_row["Project Name"])
                        e_contact = st.text_input("Contact Number", value=job_row["Contact Number"])
                        e_address = st.text_area("Full Address", value=job_row["Address"])
                        e_location = st.text_input("City / Zone Location", value=job_row["Location"])
                        curr_state_idx = INDIAN_STATES.index(job_row["State"]) if job_row["State"] in INDIAN_STATES else 0
                        e_state = st.selectbox("State", INDIAN_STATES, index=curr_state_idx)
                        
                    with e_col2:
                        curr_prod_idx = PRODUCT_LIST.index(job_row["Product"]) if job_row["Product"] in PRODUCT_LIST else 0
                        e_product = st.selectbox("Product Category", PRODUCT_LIST, index=curr_prod_idx)
                        e_cat = st.selectbox("Job Category", ["Complaint", "New Installation"], index=0 if job_row["Job Category"]=="Complaint" else 1)
                        scopes = ["Installation", "Dealer", "General Service"]
                        curr_scope_idx = scopes.index(job_row["Service Scope"]) if job_row["Service Scope"] in scopes else 0
                        e_scope = st.selectbox("Service Scope", scopes, index=curr_scope_idx)
                        e_qty = st.number_input("Quantity", min_value=1, value=int(job_row["QTY"]), step=1)
                        e_warranty = st.selectbox("Warranty", ["Yes", "No"], index=0 if job_row.get("Warranty", "Yes") == "Yes" else 1)
                        e_remark = st.text_area("Office Remark", value=job_row["Office Remark"])

                    if st.form_submit_button("💾 Save Updated Job Details"):
                        st.session_state["master_data"].at[idx, "Client Name"] = e_client
                        st.session_state["master_data"].at[idx, "Project Name"] = e_project
                        st.session_state["master_data"].at[idx, "Contact Number"] = e_contact
                        st.session_state["master_data"].at[idx, "Address"] = e_address
                        st.session_state["master_data"].at[idx, "Location"] = e_location
                        st.session_state["master_data"].at[idx, "State"] = e_state
                        st.session_state["master_data"].at[idx, "Product"] = e_product
                        st.session_state["master_data"].at[idx, "Job Category"] = e_cat
                        st.session_state["master_data"].at[idx, "Service Scope"] = e_scope
                        st.session_state["master_data"].at[idx, "QTY"] = e_qty
                        st.session_state["master_data"].at[idx, "Warranty"] = e_warranty
                        st.session_state["master_data"].at[idx, "Office Remark"] = e_remark
                        st.success(f"✅ Details for **{search_edit_id}** updated successfully!")
                        st.rerun()
            else:
                st.warning(f"❌ No JS ID matching '{search_edit_id}' found.")

# ---------------------------------------------------------
# MODULE 3: TECHNICIAN JOB VISIT UPDATE
# ---------------------------------------------------------
elif user_role == "🔧 Technician - Job Visit":
    st.subheader("🔍 Technician Job Search & Visit Report Update")
    
    search_job_id = st.text_input("Enter JS ID to Search (e.g. JS-101):").strip().upper()
    
    if search_job_id:
        master_df = st.session_state["master_data"]
        job_match = master_df[master_df["JS ID"] == search_job_id]
        
        if not job_match.empty:
            job_details = job_match.iloc[0]
            current_job_status = job_details["Current Status"]
            
            # Summary Metrics for Technician
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Client Name", job_details["Client Name"])
            c2.metric("Product (QTY)", f"{job_details['Product']} ({job_details['QTY']})")
            c3.metric("Type / Scope", f"{job_details['Job Category']} / {job_details['Service Scope']}")
            c4.metric("Warranty", job_details.get("Warranty", "N/A"))
            c5.metric("Total Visits", job_details["Total Visits"])
            
            st.write(f"📍 **Address:** {job_details['Address']}, {job_details['Location']}, {job_details['State']}")
            st.write(f"📞 **Contact:** {job_details['Contact Number']}")
            st.warning(f"📝 **Job Description / Issue Note:** {job_details['Office Remark']}")
            st.markdown("---")
            
            # Show History of Previous Visits
            st.subheader("📜 Visit History for this JS ID")
            v_df = st.session_state["visit_history"]
            previous_visits = v_df[v_df["JS ID"] == search_job_id].sort_values(by="Visit No", ascending=False) if not v_df.empty else pd.DataFrame()
            
            if not previous_visits.empty:
                for _, visit in previous_visits.iterrows():
                    with st.expander(f"📍 Visit #{visit['Visit No']} — Status: {visit['Status']} ({visit['Visit Date']})"):
                        st.write(f"**Installer:** {visit['Installer Name']} | **Time Spent:** {visit['Time Spent']}")
                        st.write(f"**Remarks:** {visit['Remarks']}")
                        if visit["Status"] == "Pending":
                            st.write(f"**Pending Reason:** {visit['Reason']}")
                        else:
                            st.write(f"**Paper Job Sheet No:** {visit['Doc No']}")
                            st.write(f"**Payment Mode:** {visit['Payment Mode']} (Credit Person: {visit['Credit Person']})")
            else:
                st.info("No previous visits logged for this JS ID.")

            st.markdown("---")

            # Form to Submit New Visit
            if current_job_status == "Completed":
                st.success("🎉 **This Job Sheet is officially CLOSED & COMPLETED! No further visits required.**")
            else:
                next_visit_no = len(previous_visits) + 1
                st.subheader(f"📝 Submit New Visit Report (Visit #{next_visit_no})")
                
                status_update = st.selectbox("Update Work Status*", ["Pending", "Completed"])
                
                pay_col1, pay_col2 = st.columns(2)
                with pay_col1:
                    payment_mode = st.selectbox("Payment Mode*", PAYMENT_MODES)
                credit_person_name = "N/A"
                with pay_col2:
                    if payment_mode == "Credit Care of":
                        credit_person_name = st.text_input("Technician / Team Member Name (Credit Given By)*")

                with st.form("tech_visit_form"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        installer_name = st.text_input("Technician / Installer Name*")
                        time_spent = st.selectbox("Time Spent on Site*", ["30 Mins", "1 Hour", "1.5 Hours", "2 Hours", "3+ Hours", "Full Day"])
                    with col_b:
                        pending_reason = st.selectbox("Reason for Pending*", PENDING_REASONS) if status_update == "Pending" else "N/A"

                    visit_remarks = st.text_area("Visit Remarks / Work Done Notes*")
                    physical_job_no = "N/A"
                    photo_file = None
                    
                    if status_update == "Completed":
                        col_c, col_d = st.columns(2)
                        with col_c:
                            physical_job_no = st.text_input("Physical Paper Job Sheet Slip No.*")
                        with col_d:
                            photo_file = st.file_uploader("Upload Job Sheet / Work Photo*", type=["jpg", "png", "jpeg"])

                    if st.form_submit_button("📤 Submit Visit Report"):
                        if not installer_name or not visit_remarks:
                            st.error("⚠️ Technician Name and Remarks are required!")
                        elif status_update == "Completed" and (not physical_job_no or photo_file is None):
                            st.error("❌ Physical Job Sheet Slip No. and Photo are mandatory for completed status.")
                        else:
                            today_str = datetime.now().strftime("%d-%b-%Y")
                            photo_url = f"https://drive.google.com/uploaded_file_{physical_job_no}.jpg" if photo_file else "N/A"

                            new_visit_row = {
                                "JS ID": search_job_id, "Visit No": next_visit_no, "Visit Date": today_str,
                                "Installer Name": installer_name, "Status": status_update, "Reason": pending_reason,
                                "Time Spent": time_spent, "Payment Mode": payment_mode,
                                "Credit Person": credit_person_name if payment_mode == "Credit Care of" else "N/A",
                                "Remarks": visit_remarks, "Doc No": physical_job_no, "Photo URL": photo_url
                            }
                            st.session_state["visit_history"] = pd.concat([st.session_state["visit_history"], pd.DataFrame([new_visit_row])], ignore_index=True)
                            
                            if sheet_connected and ws_visit:
                                try:
                                    ws_visit.append_row(list(new_visit_row.values()))
                                except Exception as e:
                                    st.warning(f"Failed to sync visit to Google Sheet: {e}")

                            sync_master_status(search_job_id)
                            st.balloons()
                            st.success(f"🎉 Visit Report #{next_visit_no} successfully submitted!")
                            st.rerun()

        else:
            st.error(f"❌ JS ID '{search_job_id}' not found in database. Please verify.")

# ---------------------------------------------------------
# MODULE 4: MASTER SHEET DATABASE VIEW
# ---------------------------------------------------------
elif user_role == "📊 View All Jobs (Master Sheet)":
    st.subheader("📋 Master Job Sheet Database View")
    st.dataframe(st.session_state["master_data"], use_container_width=True)

# ---------------------------------------------------------
# MODULE 5: VISIT HISTORY DATABASE VIEW
# ---------------------------------------------------------
elif user_role == "📜 View Visit History Database":
    st.subheader("📜 Visit History Database View")
    st.dataframe(st.session_state["visit_history"], use_container_width=True)
