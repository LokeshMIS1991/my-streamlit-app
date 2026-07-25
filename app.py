import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime
import io

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Sidharth Shutters - Enterprise Portal",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM CSS & ENTERPRISE STYLING
# ==========================================
st.markdown("""
    <style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Overall App Background Gradient */
    .stApp {
        background: linear-gradient(180deg, #F8FAFC 0%, #E2E8F0 100%);
    }

    /* Modern Login Container */
    .login-wrapper {
        max-width: 420px;
        margin: 40px auto 0 auto;
        background: #FFFFFF;
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04);
        border: 1px solid #CBD5E1;
    }

    /* Corporate Brand Header */
    .brand-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        border-radius: 12px;
        padding: 24px 20px;
        text-align: center;
        color: #FFFFFF;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(30, 58, 138, 0.3);
    }
    .brand-card h2 {
        font-size: 20px;
        font-weight: 700;
        margin: 0;
        color: #FFFFFF !important;
        letter-spacing: 0.5px;
    }
    .brand-card p {
        font-size: 12px;
        color: #93C5FD;
        margin: 4px 0 0 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Custom Button Styling */
    div.stButton > button {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.35) !important;
    }

    /* Field Info Card Styling */
    .client-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #E2E8F0;
        border-left: 6px solid #1E3A8A;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 24px;
    }

    /* Section Divider Line */
    hr {
        border-top: 1px solid #CBD5E1 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# CONSTANTS & MASTER LISTS
# ==========================================
ALL_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", 
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", 
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", 
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", 
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", 
    "Delhi NCR", "Chandigarh", "Jammu & Kashmir", "Ladakh", "Other"
]

ALL_PRODUCTS = [
    "Rolling Shutter", 
    "Motorized Shutter", 
    "Sectional Door", 
    "Automation Kit", 
    "High Speed Door", 
    "Fire Rated Shutter", 
    "Boom Barrier", 
    "Automatic Sliding Gate", 
    "Automatic Swing Gate", 
    "Dock Leveler", 
    "Other"
]

ALL_SERVICE_SCOPES = [
    "Dealer Complaint", 
    "Client Complaint", 
    "General Complaint", 
    "Under Warranty", 
    "Chargeable Service", 
    "FOC Visit", 
    "Trial Visit"
]

USER_CREDENTIALS = {
    "Admin": "admin123",
    "HOD": "hod123",
    "Manager": "mgr123",
    "Technician": "tech123"
}

# ==========================================
# AUTHENTICATION & LOGIN UI
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None

def render_login_screen():
    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        st.markdown("""
            <div class="login-wrapper">
                <div class="brand-card">
                    <div style="font-size: 32px; margin-bottom: 6px;">⚙️</div>
                    <h2>Sidharth Shutters</h2>
                    <p>Field Operations Portal</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            role = st.selectbox("👤 Select Designation / Role", ["Admin", "HOD", "Manager", "Technician"], index=3)
            password = st.text_input("🔑 Passcode", type="password", placeholder="Enter authorization key")
            st.markdown("<br>", unsafe_allow_html=True)
            
            submit_login = st.form_submit_button("🔒 Authorize Access", use_container_width=True)
            if submit_login:
                if USER_CREDENTIALS.get(role) == password:
                    st.session_state['logged_in'] = True
                    st.session_state['user_role'] = role
                    st.success(f"Welcome {role}! Loading environment...")
                    st.rerun()
                else:
                    st.error("❌ Invalid Passcode. Access Denied.")

if not st.session_state['logged_in']:
    render_login_screen()
    st.stop()

# ==========================================
# GOOGLE SHEETS & DRIVE API CONNECTION
# ==========================================
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_service_account_credentials():
    try:
        secret_dict = dict(st.secrets["gcp_service_account"])
        if "private_key" in secret_dict:
            secret_dict["private_key"] = secret_dict["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(secret_dict, scopes=SCOPE)
        return creds
    except Exception as e:
        st.error(f"❌ GCP Credentials Configuration Error: {e}")
        return None

creds = get_service_account_credentials()

def get_gspread_client():
    if creds:
        return gspread.authorize(creds)
    return None

def upload_photo_to_drive(uploaded_file, filename):
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        folder_id = st.secrets.get("FOLDER_ID", "")
        
        if not folder_id:
            st.error("❌ Drive FOLDER_ID configuration missing!")
            return ""

        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        
        media = MediaIoBaseUpload(io.BytesIO(uploaded_file.getvalue()), mimetype=uploaded_file.type)
        
        file = drive_service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id, webViewLink',
            supportsAllDrives=True,
            supportsTeamDrives=True
        ).execute()
        
        drive_service.permissions().create(
            fileId=file.get('id'),
            body={'role': 'reader', 'type': 'anyone'},
            supportsAllDrives=True,
            supportsTeamDrives=True
        ).execute()
        
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Drive Cloud Upload Exception: {e}")
        return ""

SPREADSHEET_NAME = "Sidharth Shutter CRM Master"

def fetch_data():
    client = get_gspread_client()
    if not client:
        return pd.DataFrame(), pd.DataFrame(), False

    try:
        sheet = client.open(SPREADSHEET_NAME)
        
        ws_master = sheet.worksheet("Master Sheet")
        master_data = ws_master.get_all_records()
        df_master = pd.DataFrame(master_data) if master_data else pd.DataFrame()
        
        ws_visit = sheet.worksheet("Visit History")
        visit_data = ws_visit.get_all_records()
        df_visit = pd.DataFrame(visit_data) if visit_data else pd.DataFrame()
        
        return df_master, df_visit, True
    except Exception as e:
        st.sidebar.error(f"Database Fetch Failed: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), False

def save_master_job(new_row_dict):
    try:
        client = get_gspread_client()
        sheet = client.open(SPREADSHEET_NAME)
        ws_master = sheet.worksheet("Master Sheet")
        ws_master.append_row(list(new_row_dict.values()))
        return True
    except Exception as e:
        st.error(f"Job Creation Failed: {e}")
        return False

def save_visit_entry(visit_dict):
    try:
        client = get_gspread_client()
        sheet = client.open(SPREADSHEET_NAME)
        ws_visit = sheet.worksheet("Visit History")
        ws_visit.append_row(list(visit_dict.values()))
        return True
    except Exception as e:
        st.error(f"Visit Log Failed: {e}")
        return False

def update_master_on_visit(js_id, visit_count, status, installer_name, close_time):
    try:
        client = get_gspread_client()
        sheet = client.open(SPREADSHEET_NAME)
        ws_master = sheet.worksheet("Master Sheet")
        
        cell = ws_master.find(str(js_id))
        if cell:
            row_idx = cell.row
            ws_master.update_cell(row_idx, 17, visit_count)
            
            if status == "Completed":
                ws_master.update_cell(row_idx, 16, "Completed")
                ws_master.update_cell(row_idx, 18, installer_name)
                ws_master.update_cell(row_idx, 19, close_time)
            elif status == "In Progress / Pending":
                ws_master.update_cell(row_idx, 16, "In Progress")
        return True
    except Exception as e:
        st.warning(f"Auto-Sync Warning: {e}")
        return False

# Data Initialization
df_master, df_visit, connection_status = fetch_data()

if not df_master.empty and 'Date' in df_master.columns:
    df_master['Date_Parsed'] = pd.to_datetime(df_master['Date'], errors='coerce')

if not df_visit.empty and 'Visit Date' in df_visit.columns:
    df_visit['Visit_Date_Parsed'] = pd.to_datetime(df_visit['Visit Date'], errors='coerce')

# ==========================================
# SIDEBAR NAVIGATION & FILTERS
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/000000/worker-male.png", width=50)
st.sidebar.markdown("### **SIDHARTH SHUTTERS**")
st.sidebar.caption("Automation & Security Systems")

current_role = st.session_state['user_role']
st.sidebar.info(f"👤 Account Role: **{current_role}**")

if st.sidebar.button("🚪 Terminate Session"):
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
    st.rerun()

st.sidebar.markdown("---")

available_options = []
if current_role in ["Admin", "HOD"]:
    available_options = [
        "📈 Executive Dashboard",
        "👔 Manager - Job Operations",
        "🔧 Technician - Field Visit",
        "📊 Master Jobs Database",
        "📜 Visit History Database"
    ]
elif current_role == "Manager":
    available_options = [
        "👔 Manager - Job Operations",
        "🔧 Technician - Field Visit"
    ]
elif current_role == "Technician":
    available_options = [
        "🔧 Technician - Field Visit"
    ]

nav_option = st.sidebar.radio("Navigation Menu:", available_options)

st.sidebar.markdown("---")

def filter_dataframe(df, date_col):
    return df

if connection_status:
    st.sidebar.success("🟢 Cloud Sync Active")
else:
    st.sidebar.error("🔴 Connection Failed")

if st.sidebar.button("🔄 Force Data Refresh"):
    st.cache_data.clear()
    st.rerun()

# ==========================================
# MAIN INTERFACE CONTROLLER
# ==========================================
st.markdown("<h2 style='color: #0F172A; margin-bottom: 2px;'>Sidharth Shutters & Automations Pvt. Ltd.</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-size: 14px; margin-bottom: 25px;'>Enterprise Operations & Field Service Portal</p>", unsafe_allow_html=True)

# 1. EXECUTIVE DASHBOARD
if nav_option == "📈 Executive Dashboard":
    st.subheader("📊 Operational Analytics & Performance Overview")
    filtered_master = filter_dataframe(df_master, 'Date')
    
    total_jobs = len(filtered_master) if not filtered_master.empty else 0
    completed_jobs = len(filtered_master[filtered_master['Current Status'] == 'Completed']) if not filtered_master.empty and 'Current Status' in filtered_master.columns else 0
    pending_jobs = total_jobs - completed_jobs
    completion_rate = round((completed_jobs / total_jobs * 100), 1) if total_jobs > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📌 Job Sheets Generated", total_jobs)
    col2.metric("🟢 Completed Projects", completed_jobs, f"{completion_rate}% Efficiency")
    col3.metric("🟡 Pending / In Progress", pending_jobs)
    col4.metric("⚙️ SLA Resolution Rate", f"{completion_rate}%")
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.write("🏷️ **Categorical Distribution**")
        if not filtered_master.empty and 'Job Category' in filtered_master.columns:
            st.bar_chart(filtered_master['Job Category'].value_counts())
        else:
            st.info("No records to visualize.")
            
    with c2:
        st.write("🎯 **Service Scope Classification**")
        if not filtered_master.empty and 'Service Scope' in filtered_master.columns:
            st.bar_chart(filtered_master['Service Scope'].value_counts())
        else:
            st.info("No records to visualize.")

# 2. MANAGER PORTAL
elif nav_option == "👔 Manager - Job Operations":
    st.subheader("👔 Job Sheet Creation & Lifecycle Control")
    
    manager_action = st.radio("Select Workflow:", ["➕ Generate New Job Sheet", "✏️ Modify Existing Order"], horizontal=True)
    
    if manager_action == "➕ Generate New Job Sheet":
        with st.form("create_job_form"):
            c1, c2 = st.columns(2)
            client_name = c1.text_input("Client Entity / Name *")
            project_name = c2.text_input("Project / Site Location Label")
            
            c3, c4 = st.columns(2)
            contact_no = c3.text_input("Primary Contact Number *")
            location = c4.text_input("City / District")
            
            address = st.text_area("Complete Site Address")
            
            c5, c6, c7 = st.columns(3)
            state = c5.selectbox("State Territory", ALL_STATES)
            product = c6.selectbox("Product Line", ALL_PRODUCTS)
            job_category = c7.selectbox("Order Category", ["New Installation", "Complaint / Repair", "AMC", "Inspection"])
            
            c8, c9, c10 = st.columns(3)
            service_scope = c8.selectbox("Service Scope", ALL_SERVICE_SCOPES)
            qty = c9.number_input("Unit Quantity", min_value=1, value=1)
            warranty = c10.selectbox("Warranty Terms", ["In Warranty", "Out of Warranty", "Not Applicable"])
            
            office_remark = st.text_area("Operations / Technical Directives")
            
            submit_btn = st.form_submit_button("🚀 Dispatch & Generate Job Sheet ID")
            
            if submit_btn:
                if not client_name or not contact_no:
                    st.error("Client Name and Primary Contact details are mandatory.")
                else:
                    next_id_num = len(df_master) + 1 if not df_master.empty else 1
                    js_id = f"JS-{datetime.now().strftime('%Y%m')}-{next_id_num:03d}"
                    today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    month_str = datetime.now().strftime("%B")
                    
                    new_job = {
                        "JS ID": js_id,
                        "Date": today_str,
                        "Month": month_str,
                        "Client Name": client_name,
                        "Project Name": project_name,
                        "Contact Number": contact_no,
                        "Address": address,
                        "Location": location,
                        "State": state,
                        "Product": product,
                        "Job Category": job_category,
                        "Service Scope": service_scope,
                        "QTY": qty,
                        "Warranty": warranty,
                        "Office Remark": office_remark,
                        "Current Status": "Pending",
                        "Total Visits": 0,
                        "Final Installer": "",
                        "Close Date": ""
                    }
                    
                    if save_master_job(new_job):
                        st.success(f"🎉 Job Sheet **{js_id}** committed to database.")
                        st.balloons()
                        st.cache_data.clear()

    elif manager_action == "✏️ Modify Existing Order":
        if df_master.empty or 'JS ID' not in df_master.columns:
            st.warning("No recorded jobs found in database.")
        else:
            js_list = df_master['JS ID'].astype(str).tolist()
            selected_edit_js = st.selectbox("Select Target Job ID:", js_list)
            
            job_data = df_master[df_master['JS ID'].astype(str) == selected_edit_js].iloc[0]
            
            st.info(f"👤 **Client:** {job_data.get('Client Name', '')} | 📍 **Location:** {job_data.get('Location', '')} | 📅 **Creation Date:** {job_data.get('Date', '')}")
            
            with st.form("edit_job_manager_form"):
                ec1, ec2 = st.columns(2)
                updated_status = ec1.selectbox("Updated Status Flag", ["Pending", "In Progress", "Completed", "On Hold", "Cancelled"], 
                                               index=["Pending", "In Progress", "Completed", "On Hold", "Cancelled"].index(job_data.get('Current Status', 'Pending')) if job_data.get('Current Status') in ["Pending", "In Progress", "Completed", "On Hold", "Cancelled"] else 0)
                updated_installer = ec2.text_input("Lead Lead Lead Technician / Engineer", value=str(job_data.get('Final Installer', '')))
                
                updated_office_remark = st.text_area("Updated Directive Notes", value=str(job_data.get('Office Remark', '')))
                
                edit_submit = st.form_submit_button("🔄 Commit Order Updates")
                
                if edit_submit:
                    try:
                        client = get_gspread_client()
                        sheet = client.open(SPREADSHEET_NAME)
                        ws_master = sheet.worksheet("Master Sheet")
                        
                        row_idx = df_master.index[df_master['JS ID'].astype(str) == selected_edit_js][0] + 2
                        
                        ws_master.update_cell(row_idx, 15, updated_office_remark)
                        ws_master.update_cell(row_idx, 16, updated_status)
                        ws_master.update_cell(row_idx, 18, updated_installer)
                        
                        if updated_status == "Completed":
                            ws_master.update_cell(row_idx, 19, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            
                        st.success(f"✅ Job Record **{selected_edit_js}** updated.")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Sync Failure: {e}")

# 3. TECHNICIAN FIELD VISIT PORTAL
elif nav_option == "🔧 Technician - Field Visit":
    st.subheader("🔧 Field Operations: Log Site Inspection & Service")
    
    if df_master.empty or 'JS ID' not in df_master.columns:
        st.warning("No Job IDs logged. Manager action required.")
    else:
        pending_js_ids = df_master['JS ID'].astype(str).tolist()
        selected_js_id = st.selectbox("Select Assigned JS ID:", pending_js_ids)
        
        job_info = df_master[df_master['JS ID'].astype(str) == selected_js_id].iloc[0]
        
        # Customer Card Summary
        st.markdown(f"""
            <div class="client-card">
                <h4 style="margin: 0 0 10px 0; color: #0F172A;">📌 Order Specification: {selected_js_id}</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; font-size: 14px;">
                    <div><b>Client:</b> {job_info.get('Client Name', 'N/A')}</div>
                    <div><b>Contact:</b> {job_info.get('Contact Number', 'N/A')}</div>
                    <div><b>Location:</b> {job_info.get('Location', 'N/A')} ({job_info.get('State', 'N/A')})</div>
                    <div><b>Product:</b> {job_info.get('Product', 'N/A')}</div>
                    <div><b>Category:</b> {job_info.get('Job Category', 'N/A')}</div>
                    <div><b>Scope:</b> {job_info.get('Service Scope', 'N/A')}</div>
                </div>
                <div style="margin-top: 10px; font-size: 13px;"><b>Address:</b> {job_info.get('Address', 'N/A')}</div>
                <div style="margin-top: 6px; font-size: 13px; color: #D97706;"><b>Instructions:</b> {job_info.get('Office Remark', 'None')}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Log Site Entry Form
        st.markdown("##### 📝 Submit Service Visit Report")
        c1, c2 = st.columns(2)
        installer_name = c1.text_input("Lead Technician Name *")
        status = c2.selectbox("Site Work Outcome", ["In Progress / Pending", "Completed", "Partially Done", "Cancelled"])
        
        reasons_list = [
            "Site Not Ready",
            "Motor / Automation Fault",
            "Alignment & Mechanical Issue",
            "Power Supply / Electrical Issue",
            "Remote / Sensor Programming",
            "Material Missing / Pending from Client",
            "Payment Issue / On Hold",
            "Regular Maintenance / Service Complete",
            "Installation Complete",
            "Other"
        ]
        selected_reason = st.selectbox("Work Category / Resolution *", reasons_list)
        
        other_reason_text = ""
        if selected_reason == "Other":
            other_reason_text = st.text_input("Specify Work Category *")
            
        final_reason = other_reason_text if selected_reason == "Other" else selected_reason
        
        c5, c6 = st.columns(2)
        payment_mode = c5.selectbox("Payment Collection Channel", ["N/A", "None / Included", "Cash", "UPI / Digital", "Credit / Due"])
        
        credit_person = "N/A"
        if payment_mode == "Credit / Due":
            credit_person = c6.text_input("Credit Authorized Person (Care Of) *")
        else:
            c6.text_input("Credit Authorized Person", value="N/A", disabled=True)
        
        remarks = st.text_area("Field Remarks / Observations")
        
        st.markdown("---")
        doc_c1, doc_c2 = st.columns(2)
        doc_no = doc_c1.text_input("Service Slip / Challan ID (Optional)")
        uploaded_photo = doc_c2.file_uploader("Upload Verification Image (Slip/Site)", type=["png", "jpg", "jpeg"])
        
        if st.button("💾 Submit Visit Report", use_container_width=True):
            if not installer_name:
                st.error("Please specify Technician Name.")
            elif payment_mode == "Credit / Due" and (not credit_person or credit_person == "N/A"):
                st.error("Please enter the name of the Credit Authorized Person.")
            else:
                existing_visits = len(df_visit[df_visit['JS ID'].astype(str) == selected_js_id]) if not df_visit.empty else 0
                visit_no = existing_visits + 1
                
                visit_timestamp = datetime.now()
                visit_time_str = visit_timestamp.strftime("%Y-%m-%d %H:%M:%S")
                
                photo_url = ""
                if uploaded_photo is not None:
                    photo_filename = f"{selected_js_id}_Visit{visit_no}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    st.info("📤 Syncing image artifact with Google Drive...")
                    photo_url = upload_photo_to_drive(uploaded_photo, photo_filename)
                
                js_created_str = str(job_info['Date'])
                try:
                    js_created_dt = pd.to_datetime(js_created_str)
                    time_diff_seconds = int((visit_timestamp - js_created_dt).total_seconds())
                    duration_display = f"{time_diff_seconds} Sec ({round(time_diff_seconds/3600, 2)} Hrs)"
                except:
                    duration_display = "N/A"

                visit_log = {
                    "JS ID": selected_js_id,
                    "Visit No": visit_no,
                    "Visit Date": visit_time_str,
                    "Installer Name": installer_name,
                    "Status": status,
                    "Reason": final_reason,
                    "Time Spent (Seconds)": duration_display,
                    "Payment Mode": payment_mode,
                    "Credit Person": credit_person,
                    "Remarks": remarks,
                    "Doc No": doc_no,
                    "Photo URL": photo_url
                }
                
                if save_visit_entry(visit_log):
                    update_master_on_visit(
                        js_id=selected_js_id, 
                        visit_count=visit_no, 
                        status=status, 
                        installer_name=installer_name, 
                        close_time=visit_time_str
                    )
                    
                    st.success(f"✅ Visit Entry #{visit_no} recorded for **{selected_js_id}**.")
                    if photo_url:
                        st.success(f"📸 Image Documented: {photo_url}")
                    st.cache_data.clear()

# 4. VIEW MASTER DATABASE
elif nav_option == "📊 Master Jobs Database":
    st.subheader("📊 Central Master Orders Sheet")
    filtered_master = filter_dataframe(df_master, 'Date')
    
    if not filtered_master.empty:
        display_df = filtered_master.drop(columns=['Date_Parsed'], errors='ignore')
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No records present.")

# 5. VIEW VISIT HISTORY
elif nav_option == "📜 Visit History Database":
    st.subheader("📜 Complete Technician Visit History")
    filtered_visit = filter_dataframe(df_visit, 'Visit Date')
    
    if not filtered_visit.empty:
        display_visit_df = filtered_visit.drop(columns=['Visit_Date_Parsed'], errors='ignore')
        st.dataframe(
            display_visit_df, 
            column_config={"Photo URL": st.column_config.LinkColumn("Artifact Link")},
            use_container_width=True
        )
    else:
        st.info("No records present.")
