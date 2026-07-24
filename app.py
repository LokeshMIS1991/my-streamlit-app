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
    page_title="Sidharth Shutters - Operations Portal",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header {
        font-size: 28px;
        font-weight: bold;
        color: #1E3A8A;
        padding-bottom: 5px;
    }
    .sub-header {
        font-size: 14px;
        color: #6B7280;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# AUTHENTICATION & LOGIN SYSTEM
# ==========================================
USER_CREDENTIALS = {
    "Admin": "admin123",
    "HOD": "hod123",
    "Manager": "mgr123",
    "Technician": "tech123"
}

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None

def login_screen():
    st.markdown("<div class='main-header'>Sidharth Shutters & Automations Private Limited</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Operations Portal - Secure Access Login</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 User Login")
        role = st.selectbox("Select Your Role:", ["Admin", "HOD", "Manager", "Technician"])
        password = st.text_input("Enter Password:", type="password")
        
        if st.button("🔑 Login", use_container_width=True):
            if USER_CREDENTIALS.get(role) == password:
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = role
                st.success(f"Welcome {role}! Logging in...")
                st.rerun()
            else:
                st.error("❌ Incorrect Password. Please try again.")

if not st.session_state['logged_in']:
    login_screen()
    st.stop()

# ==========================================
# CONNECTIONS & AUTHENTICATION
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
        st.error(f"❌ GCP Credentials Error: {e}")
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
        
        file_metadata = {
            'name': filename,
            'parents': [folder_id] if folder_id else []
        }
        
        media = MediaIoBaseUpload(io.BytesIO(uploaded_file.getvalue()), mimetype=uploaded_file.type)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        
        # Make photo viewable via link
        drive_service.permissions().create(
            fileId=file.get('id'),
            body={'role': 'reader', 'type': 'anyone'}
        ).execute()
        
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Drive Upload Error: {e}")
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
        st.sidebar.error(f"Error fetching Sheets: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), False

def save_master_job(new_row_dict):
    try:
        client = get_gspread_client()
        sheet = client.open(SPREADSHEET_NAME)
        ws_master = sheet.worksheet("Master Sheet")
        ws_master.append_row(list(new_row_dict.values()))
        return True
    except Exception as e:
        st.error(f"Save Error: {e}")
        return False

def save_visit_entry(visit_dict):
    try:
        client = get_gspread_client()
        sheet = client.open(SPREADSHEET_NAME)
        ws_visit = sheet.worksheet("Visit History")
        ws_visit.append_row(list(visit_dict.values()))
        return True
    except Exception as e:
        st.error(f"Visit Save Error: {e}")
        return False

# Load Data
df_master, df_visit, connection_status = fetch_data()

# Parse Datetime for Filter Helper
if not df_master.empty and 'Date' in df_master.columns:
    df_master['Date_Parsed'] = pd.to_datetime(df_master['Date'], errors='coerce')

if not df_visit.empty and 'Visit Date' in df_visit.columns:
    df_visit['Visit_Date_Parsed'] = pd.to_datetime(df_visit['Visit Date'], errors='coerce')

# ==========================================
# SIDEBAR NAVIGATION & ROLE PERMISSIONS
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/000000/worker-male.png", width=60)
st.sidebar.title("SIDHARTH")
st.sidebar.caption("SHUTTER & AUTOMATION")

current_role = st.session_state['user_role']
st.sidebar.info(f"👤 Logged in as: **{current_role}**")

if st.sidebar.button("🚪 Logout"):
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
    st.rerun()

st.sidebar.markdown("---")

available_options = []
if current_role in ["Admin", "HOD"]:
    available_options = [
        "📈 Executive Dashboard",
        "👔 Manager - Create / Edit Job",
        "🔧 Technician - Job Visit",
        "📊 View All Jobs (Master Sheet)",
        "📜 View Visit History Database"
    ]
elif current_role == "Manager":
    available_options = [
        "👔 Manager - Create / Edit Job",
        "🔧 Technician - Job Visit"
    ]
elif current_role == "Technician":
    available_options = [
        "🔧 Technician - Job Visit"
    ]

nav_option = st.sidebar.radio("Navigation Options:", available_options)

st.sidebar.markdown("---")

# ALWAYS VISIBLE Date / Month Filter (If allowed for role)
if current_role in ["Admin", "HOD"]:
    st.sidebar.subheader("📅 Data Filters")
    filter_mode = st.sidebar.radio("Filter By:", ["All Data", "By Month & Year", "Date Range"])

    selected_month = "All"
    selected_year = "All"
    start_date = None
    end_date = None

    if filter_mode == "By Month & Year":
        selected_month = st.sidebar.selectbox("Select Month", ["All", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], index=datetime.now().month)
        selected_year = st.sidebar.selectbox("Select Year", ["All", 2024, 2025, 2026, 2027], index=3)

    elif filter_mode == "Date Range":
        date_range = st.sidebar.date_input("Select Start & End Date", [])
        if len(date_range) == 2:
            start_date, end_date = date_range[0], date_range[1]

    def filter_dataframe(df, date_col):
        if df.empty or date_col not in df.columns:
            return df
        filtered_df = df.copy()
        if filter_mode == "By Month & Year":
            if selected_month != "All" and 'Month' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Month'] == selected_month]
            if selected_year != "All":
                filtered_df = filtered_df[filtered_df[date_col].astype(str).str.contains(str(selected_year), na=False)]
        elif filter_mode == "Date Range" and start_date and end_date:
            parsed_col = date_col + '_Parsed'
            if parsed_col in filtered_df.columns:
                filtered_df = filtered_df[(filtered_df[parsed_col].dt.date >= start_date) & (filtered_df[parsed_col].dt.date <= end_date)]
        return filtered_df
else:
    def filter_dataframe(df, date_col):
        return df

st.sidebar.markdown("---")
if connection_status:
    st.sidebar.success("🟢 Google Sheets Connected")
else:
    st.sidebar.error("🔴 Connection Failed")

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption("© Sidharth Shutters & Automations Pvt. Ltd.")

# ==========================================
# MAIN INTERFACE LOGIC
# ==========================================

st.markdown("<div class='main-header'>Sidharth Shutters & Automations Private Limited</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Field Operations & Service Operations Portal</div>", unsafe_allow_html=True)

# 1. EXECUTIVE DASHBOARD
if nav_option == "📈 Executive Dashboard":
    st.subheader("📊 Executive Operations & Performance Dashboard")
    filtered_master = filter_dataframe(df_master, 'Date')
    
    total_jobs = len(filtered_master) if not filtered_master.empty else 0
    completed_jobs = len(filtered_master[filtered_master['Current Status'] == 'Completed']) if not filtered_master.empty and 'Current Status' in filtered_master.columns else 0
    pending_jobs = total_jobs - completed_jobs
    completion_rate = round((completed_jobs / total_jobs * 100), 1) if total_jobs > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📌 Total JS IDs Generated", total_jobs)
    col2.metric("🟢 Completed Jobs", completed_jobs, f"{completion_rate}% Done")
    col3.metric("🟡 Pending Jobs", pending_jobs)
    col4.metric("⚙️ Service Completion Rate", f"{completion_rate}%")
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.write("🏷️ **Jobs Breakdown by Category**")
        if not filtered_master.empty and 'Job Category' in filtered_master.columns:
            st.bar_chart(filtered_master['Job Category'].value_counts())
        else:
            st.info("No data available.")
            
    with c2:
        st.write("🎯 **Jobs Breakdown by Service Scope**")
        if not filtered_master.empty and 'Service Scope' in filtered_master.columns:
            st.bar_chart(filtered_master['Service Scope'].value_counts())
        else:
            st.info("No data available.")

# 2. MANAGER PORTAL
elif nav_option == "👔 Manager - Create / Edit Job":
    st.subheader("👔 Manager Portal: Generate Job Sheet")
    
    with st.form("create_job_form"):
        c1, c2 = st.columns(2)
        client_name = c1.text_input("Client Name *")
        project_name = c2.text_input("Project / Site Name")
        
        c3, c4 = st.columns(2)
        contact_no = c3.text_input("Contact Number *")
        location = c4.text_input("Location / City")
        
        address = st.text_area("Full Address")
        
        c5, c6, c7 = st.columns(3)
        state = c5.selectbox("State", ["Delhi", "Haryana", "UP", "Punjab", "Rajasthan", "Other"])
        product = c6.selectbox("Product", ["Rolling Shutter", "Motorized Shutter", "Sectional Door", "Automation Kit", "Other"])
        job_category = c7.selectbox("Job Category", ["New Installation", "Complaint / Repair", "AMC", "Inspection"])
        
        c8, c9, c10 = st.columns(3)
        service_scope = c8.selectbox("Service Scope", ["Under Warranty", "Chargeable Service", "FOC Visit", "Trial Visit"])
        qty = c9.number_input("Quantity", min_value=1, value=1)
        warranty = c10.selectbox("Warranty Status", ["In Warranty", "Out of Warranty", "Not Applicable"])
        
        office_remark = st.text_area("Office Remark / Special Instructions")
        
        submit_btn = st.form_submit_button("🚀 Generate & Save JS ID")
        
        if submit_btn:
            if not client_name or not contact_no:
                st.error("Please fill Client Name and Contact Number.")
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
                    st.success(f"🎉 Job Sheet **{js_id}** created successfully!")
                    st.rerun()

# 3. TECHNICIAN VISIT PORTAL
elif nav_option == "🔧 Technician - Job Visit":
    st.subheader("🔧 Technician Portal: Log Site Visit")
    
    if df_master.empty:
        st.warning("No Job IDs available. Please create a Job from Manager Portal first.")
    else:
        pending_js_ids = df_master['JS ID'].tolist()
        selected_js_id = st.selectbox("Select JS ID for Visit:", pending_js_ids)
        
        job_info = df_master[df_master['JS ID'] == selected_js_id].iloc[0]
        st.info(f"📍 **Client:** {job_info['Client Name']} | **Product:** {job_info['Product']} | **Created On:** {job_info['Date']}")
        
        with st.form("technician_visit_form"):
            c1, c2 = st.columns(2)
            installer_name = c1.text_input("Technician / Installer Name *")
            status = c2.selectbox("Visit Outcome Status", ["In Progress / Pending", "Completed", "Partially Done", "Cancelled"])
            
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
            selected_reason = st.selectbox("Reason / Work Done Category *", reasons_list)
            
            other_reason_text = ""
            if selected_reason == "Other":
                other_reason_text = st.text_input("Specify Other Reason *")
                
            final_reason = other_reason_text if selected_reason == "Other" else selected_reason
            
            c5, c6 = st.columns(2)
            payment_mode = c5.selectbox("Payment Mode", ["N/A", "None / Included", "Cash", "UPI / Digital", "Credit / Due"])
            credit_person = c6.text_input("If Credit, Person Name")
            
            remarks = st.text_area("Technician Remarks")
            
            st.markdown("---")
            st.caption("📷 **Optional Attachments / Photo Upload (Camera / Gallery):**")
            
            doc_c1, doc_c2 = st.columns(2)
            doc_no = doc_c1.text_input("Job Sheet Slip / Challan / Doc No. (Optional)")
            
            # CAMERA / GALLERY FILE UPLOADER
            uploaded_photo = doc_c2.file_uploader(
                "Upload Site Photo / Slip (Camera or Gallery)", 
                type=["png", "jpg", "jpeg"]
            )
            
            visit_submit = st.form_submit_button("💾 Submit Visit Log")
            
            if visit_submit:
                if not installer_name:
                    st.error("Please fill Technician Name.")
                else:
                    existing_visits = len(df_visit[df_visit['JS ID'] == selected_js_id]) if not df_visit.empty else 0
                    visit_no = existing_visits + 1
                    
                    visit_timestamp = datetime.now()
                    visit_time_str = visit_timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Upload Photo to Google Drive if selected
                    photo_url = ""
                    if uploaded_photo is not None:
                        photo_filename = f"{selected_js_id}_Visit{visit_no}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                        st.info("📤 Uploading photo to Google Drive...")
                        photo_url = upload_photo_to_drive(uploaded_photo, photo_filename)
                    
                    # Time Calculation
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
                        st.success(f"✅ Visit #{visit_no} Logged Successfully for **{selected_js_id}**! Total Duration: {duration_display}")
                        if photo_url:
                            st.success(f"📸 Photo Saved to Google Drive! Link: {photo_url}")
                        st.rerun()

# 4. VIEW MASTER SHEET
elif nav_option == "📊 View All Jobs (Master Sheet)":
    st.subheader("📊 Master Job Database (Read Only)")
    filtered_master = filter_dataframe(df_master, 'Date')
    
    if not filtered_master.empty:
        display_df = filtered_master.drop(columns=['Date_Parsed'], errors='ignore')
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No data matching selected filters.")

# 5. VIEW VISIT HISTORY
elif nav_option == "📜 View Visit History Database":
    st.subheader("📜 Technician Visit Logs (Read Only)")
    filtered_visit = filter_dataframe(df_visit, 'Visit Date')
    
    if not filtered_visit.empty:
        display_visit_df = filtered_visit.drop(columns=['Visit_Date_Parsed'], errors='ignore')
        st.dataframe(
            display_visit_df, 
            column_config={
                "Photo URL": st.column_config.LinkColumn("Photo Link")
            },
            use_container_width=True
        )
    else:
        st.info("No visit records matching selected filters.")
