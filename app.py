import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import datetime

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Sidharth Shutters - Operations Portal",
    page_icon="⚙️",
    layout="wide"
)

# --- GOOGLE AUTHENTICATION SETUP ---
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_gspread_client():
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPE)
    client = gspread.authorize(creds)
    return client, creds

try:
    gc, creds = get_gspread_client()
    SHEET_NAME = st.secrets.get("SHEET_NAME", "Sidharth Shutter CRM Master")
    sheet = gc.open(SHEET_NAME)
    
    # Worksheets
    master_ws = sheet.worksheet("Master Jobs")
    visit_ws = sheet.worksheet("Visit History")
except Exception as e:
    st.error(f"Google Sheet Connection Error: {e}")
    st.stop()

# --- DRIVE UPLOAD FUNCTION (FIXED FOR QUOTA ERROR) ---
def upload_photo_to_drive(uploaded_file, filename):
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        folder_id = st.secrets.get("FOLDER_ID", "")
        
        file_metadata = {
            'name': filename,
            'parents': [folder_id] if folder_id else []
        }
        
        media = MediaIoBaseUpload(io.BytesIO(uploaded_file.getvalue()), mimetype=uploaded_file.type)
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink',
            supportsAllDrives=True
        ).execute()
        
        # Make link viewable by anyone with link
        drive_service.permissions().create(
            fileId=file.get('id'),
            body={'role': 'reader', 'type': 'anyone'},
            supportsAllDrives=True
        ).execute()
        
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Drive Upload Error: {e}")
        return ""

# --- HELPER FUNCTIONS FOR GOOGLE SHEETS ---
def get_master_dataframe():
    data = master_ws.get_all_records()
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)

def get_visit_dataframe():
    data = visit_ws.get_all_records()
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)

def generate_next_js_id():
    df = get_master_dataframe()
    if df.empty or 'JS ID' not in df.columns:
        return "JS-101"
    
    existing_ids = df['JS ID'].astype(str).tolist()
    numeric_ids = []
    for item in existing_ids:
        if item.startswith("JS-"):
            try:
                numeric_ids.append(int(item.replace("JS-", "")))
            except ValueError:
                pass
    
    if not numeric_ids:
        return "JS-101"
    return f"JS-{max(numeric_ids) + 1}"

# --- NAVIGATION SIDEBAR ---
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Choose Portal / View:", [
    "Executive Dashboard",
    "Manager - Create / Edit Job",
    "Technician - Job Visit",
    "View All Jobs (Master Sheet)",
    "View Visit History Database"
])

# ==========================================
# PAGE 1: EXECUTIVE DASHBOARD
# ==========================================
if page == "Executive Dashboard":
    st.title("📊 Executive Operations Dashboard")
    df_master = get_master_dataframe()
    df_visit = get_visit_dataframe()
    
    if not df_master.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Complaint/Job Entries", len(df_master))
        col2.metric("Pending Jobs", len(df_master[df_master['Status'] != 'Completed']))
        col3.metric("Completed Jobs", len(df_master[df_master['Status'] == 'Completed']))
        col4.metric("Total Visit Logs", len(df_visit) if not df_visit.empty else 0)
        
        st.divider()
        st.subheader("📋 Recent Jobs Overview")
        st.dataframe(df_master, use_container_width=True)
    else:
        st.info("No data available in Master Sheet yet.")

# ==========================================
# PAGE 2: MANAGER - CREATE / EDIT JOB
# ==========================================
elif page == "Manager - Create / Edit Job":
    st.title("👨‍💼 Manager Portal: Create & Edit Complaint/Job")
    
    mode = st.radio("Select Action:", ["➕ Create New Job / Complaint", "✏️ Edit Existing Job Details"], horizontal=True)
    
    df_master = get_master_dataframe()

    # --- SUB-MODE A: CREATE NEW JOB ---
    if mode == "➕ Create New Job / Complaint":
        st.subheader("📝 New Job Entry Form")
        
        new_js_id = generate_next_js_id()
        st.info(f"🔑 Auto-Generated **JS ID**: **`{new_js_id}`**")
        
        with st.form("create_job_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                client_name = st.text_input("Client / Customer Name*")
                contact_no = st.text_input("Contact Number*")
                location = st.text_input("Site Location / Address*")
            with col2:
                complaint_type = st.selectbox("Complaint / Job Type", ["Shutter Service", "Automation Issue", "New Installation", "General Repair", "Other", "Client"])
                assigned_tech = st.text_input("Assign Technician Name*")
                priority = st.selectbox("Priority Level", ["Normal", "High", "Urgent"])
            
            remarks = st.text_area("Initial Remarks / Issue Description")
            submit_btn = st.form_submit_button("💾 Save & Generate JS ID")
            
            if submit_btn:
                if not client_name or not contact_no or not assigned_tech:
                    st.error("Please fill in all mandatory fields (*)")
                else:
                    today_str = datetime.date.today().strftime("%Y-%m-%d")
                    new_row = [
                        new_js_id, today_str, client_name, contact_no, 
                        location, complaint_type, assigned_tech, priority, 
                        "Assigned", remarks
                    ]
                    master_ws.append_row(new_row)
                    
                    st.success(f"🎉 Job Successfully Created! **JS ID: `{new_js_id}`**")
                    st.balloons()

    # --- SUB-MODE B: EDIT EXISTING JOB ---
    elif mode == "✏️ Edit Existing Job Details":
        st.subheader("🔄 Update / Edit Existing Job Status")
        
        if df_master.empty:
            st.warning("No jobs found in the system to edit.")
        else:
            js_list = df_master['JS ID'].astype(str).tolist()
            selected_js = st.selectbox("Select JS ID to Edit:", js_list)
            
            job_data = df_master[df_master['JS ID'].astype(str) == selected_js].iloc[0]
            
            # Get Row Index in Sheet (Sheet 1-indexed, header is row 1)
            row_idx = df_master.index[df_master['JS ID'].astype(str) == selected_js][0] + 2
            
            st.write(f"**Client:** {job_data.get('Client Name', '')} | **Location:** {job_data.get('Location', '')}")
            
            with st.form("edit_job_form"):
                col1, col2 = st.columns(2)
                with col1:
                    status = st.selectbox("Update Job Status", ["Assigned", "In Progress", "On Hold", "Completed", "Cancelled"], 
                                          index=["Assigned", "In Progress", "On Hold", "Completed", "Cancelled"].index(job_data.get('Status', 'Assigned')) if job_data.get('Status') in ["Assigned", "In Progress", "On Hold", "Completed", "Cancelled"] else 0)
                    assigned_tech = st.text_input("Assigned Technician", value=str(job_data.get('Technician Name', '')))
                with col2:
                    priority = st.selectbox("Priority Level", ["Normal", "High", "Urgent"],
                                          index=["Normal", "High", "Urgent"].index(job_data.get('Priority', 'Normal')) if job_data.get('Priority') in ["Normal", "High", "Urgent"] else 0)
                    contact_no = st.text_input("Contact Number", value=str(job_data.get('Contact No', '')))
                
                remarks = st.text_area("Remarks / Updates", value=str(job_data.get('Remarks', '')))
                
                update_btn = st.form_submit_button("🔄 Update Job Details")
                
                if update_btn:
                    # Header Columns: JS ID, Date, Client Name, Contact No, Location, Complaint Type, Technician Name, Priority, Status, Remarks
                    master_ws.update_cell(row_idx, 4, contact_no)
                    master_ws.update_cell(row_idx, 7, assigned_tech)
                    master_ws.update_cell(row_idx, 8, priority)
                    master_ws.update_cell(row_idx, 9, status)
                    master_ws.update_cell(row_idx, 10, remarks)
                    
                    st.success(f"✅ Job `{selected_js}` successfully updated!")

# ==========================================
# PAGE 3: TECHNICIAN - JOB VISIT
# ==========================================
elif page == "Technician - Job Visit":
    st.title("👨‍🔧 Technician Visit Logging Portal")
    
    df_master = get_master_dataframe()
    
    if df_master.empty:
        st.warning("No jobs currently available.")
    else:
        active_jobs = df_master[df_master['Status'] != 'Completed']
        js_options = active_jobs['JS ID'].astype(str).tolist() if not active_jobs.empty else df_master['JS ID'].astype(str).tolist()
        
        selected_js = st.selectbox("Select JS ID for Visit:", js_options)
        
        job_info = df_master[df_master['JS ID'].astype(str) == selected_js].iloc[0]
        
        st.info(f"👤 **Client:** {job_info.get('Client Name', '')} | 📞 **Phone:** {job_info.get('Contact No', '')} | 📍 **Location:** {job_info.get('Location', '')}")
        
        with st.form("technician_visit_form", clear_on_submit=True):
            tech_name = st.text_input("Technician Name*", value=str(job_info.get('Technician Name', '')))
            visit_work_done = st.text_area("Work Done / Site Observations*")
            visit_status = st.selectbox("Current Visit Status", ["In Progress", "Completed", "Pending Parts/Follow-up"])
            
            uploaded_photo = st.file_uploader("📷 Upload Site Photo / Slip (Manual Choice)", type=['jpg', 'jpeg', 'png'])
            
            submit_visit = st.form_submit_button("💾 Submit Visit Log")
            
            if submit_visit:
                if not tech_name or not visit_work_done:
                    st.error("Please fill required fields (*)")
                else:
                    photo_url = ""
                    if uploaded_photo is not None:
                        st.info("Uploading photo to Google Drive...")
                        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{selected_js}_{timestamp_str}.png"
                        photo_url = upload_photo_to_drive(uploaded_photo, filename)
                    
                    visit_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Visit History Sheet Columns: Visit Date, JS ID, Technician Name, Work Done, Status, Photo Link
                    visit_row = [
                        visit_date, selected_js, tech_name, visit_work_done, visit_status, photo_url
                    ]
                    visit_ws.append_row(visit_row)
                    
                    # Update status in Master sheet if completed
                    if visit_status == "Completed":
                        row_idx = df_master.index[df_master['JS ID'].astype(str) == selected_js][0] + 2
                        master_ws.update_cell(row_idx, 9, "Completed")
                    
                    st.success(f"✅ Visit log for `{selected_js}` recorded successfully!")

# ==========================================
# PAGE 4: VIEW ALL JOBS
# ==========================================
elif page == "View All Jobs (Master Sheet)":
    st.title("📋 Master Sheet Database")
    df_master = get_master_dataframe()
    if not df_master.empty:
        st.dataframe(df_master, use_container_width=True)
    else:
        st.info("No Master Data Found.")

# ==========================================
# PAGE 5: VIEW VISIT HISTORY DATABASE
# ==========================================
elif page == "View Visit History Database":
    st.title("📜 Visit History & Photos Database")
    df_visit = get_visit_dataframe()
    if not df_visit.empty:
        st.dataframe(
            df_visit,
            column_config={
                "Photo Link": st.column_config.LinkColumn("Photo Link", display_text="🖼️ View Photo")
            },
            use_container_width=True
        )
    else:
        st.info("No Visit Logs Found.")
