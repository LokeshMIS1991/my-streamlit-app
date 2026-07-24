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
    
    # Corrected Worksheet Names from Google Sheet Tabs
    master_ws = sheet.worksheet("Master Sheet")
    visit_ws = sheet.worksheet("Visit History")
except Exception as e:
    st.error(f"Google Sheet Connection Error: {e}")
    st.stop()

# --- DRIVE UPLOAD FUNCTION ---
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
    today_prefix = f"JS-{datetime.date.today().strftime('%Y%m')}-"
    
    if df.empty or 'JS ID' not in df.columns:
        return f"{today_prefix}001"
    
    existing_ids = df['JS ID'].astype(str).tolist()
    matching_ids = [item for item in existing_ids if item.startswith("JS-")]
    
    if not matching_ids:
        return f"{today_prefix}001"
    
    # Get last number
    try:
        last_id = matching_ids[-1]
        last_num = int(last_id.split("-")[-1])
        new_num = last_num + 1
        return f"{today_prefix}{new_num:03d}"
    except Exception:
        return f"{today_prefix}{len(matching_ids) + 1:03d}"

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
        col1.metric("Total Jobs", len(df_master))
        
        status_col = 'Status' if 'Status' in df_master.columns else df_master.columns[0]
        pending_count = len(df_master[df_master[status_col] != 'Completed'])
        completed_count = len(df_master[df_master[status_col] == 'Completed'])
        
        col2.metric("Pending Jobs", pending_count)
        col3.metric("Completed Jobs", completed_count)
        col4.metric("Total Visit Logs", len(df_visit) if not df_visit.empty else 0)
        
        st.divider()
        st.subheader("📋 Master Sheet Overview")
        st.dataframe(df_master, use_container_width=True)
    else:
        st.info("No data available in Master Sheet yet.")

# ==========================================
# PAGE 2: MANAGER - CREATE / EDIT JOB
# ==========================================
elif page == "Manager - Create / Edit Job":
    st.title("👨‍💼 Manager Portal: Create & Edit Job")
    
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
                complaint_type = st.selectbox("Job / Complaint Type", ["Shutter Service", "Automation Issue", "New Installation", "General Repair", "Other"])
                assigned_tech = st.text_input("Assign Installer / Technician Name*")
                priority = st.selectbox("Priority Level", ["Normal", "High", "Urgent"])
            
            remarks = st.text_area("Initial Remarks / Issue Description")
            submit_btn = st.form_submit_button("💾 Save & Generate JS ID")
            
            if submit_btn:
                if not client_name or not contact_no or not assigned_tech:
                    st.error("Please fill in all mandatory fields (*)")
                else:
                    today_str = datetime.date.today().strftime("%Y-%m-%d")
                    # Append row to Master Sheet
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
        
        if df_master.empty or 'JS ID' not in df_master.columns:
            st.warning("No jobs found in Master Sheet to edit.")
        else:
            js_list = df_master['JS ID'].astype(str).unique().tolist()
            selected_js = st.selectbox("Select JS ID to Edit:", js_list)
            
            job_data = df_master[df_master['JS ID'].astype(str) == selected_js].iloc[0]
            row_idx = df_master.index[df_master['JS ID'].astype(str) == selected_js][0] + 2
            
            with st.form("edit_job_form"):
                col1, col2 = st.columns(2)
                with col1:
                    status = st.selectbox("Update Job Status", ["In Progress / Pending", "Completed", "On Hold", "Cancelled"])
                    assigned_tech = st.text_input("Installer / Technician Name", value=str(job_data.get('Installer Name', job_data.get('Technician Name', ''))))
                with col2:
                    doc_no = st.text_input("Doc No", value=str(job_data.get('Doc No', '')))
                    reason = st.text_input("Reason / Remarks", value=str(job_data.get('Reason', '')))
                
                remarks = st.text_area("Additional Remarks", value=str(job_data.get('Remarks', '')))
                
                update_btn = st.form_submit_button("🔄 Update Job Details")
                
                if update_btn:
                    # Updating status & remarks
                    master_ws.update_cell(row_idx, 5, status)  # Column E (Status)
                    master_ws.update_cell(row_idx, 10, remarks) # Column J (Remarks)
                    
                    st.success(f"✅ Job `{selected_js}` successfully updated!")

# ==========================================
# PAGE 3: TECHNICIAN - JOB VISIT
# ==========================================
elif page == "Technician - Job Visit":
    st.title("👨‍🔧 Technician Visit Logging Portal")
    
    df_master = get_master_dataframe()
    
    if df_master.empty or 'JS ID' not in df_master.columns:
        st.warning("No active jobs found.")
    else:
        js_options = df_master['JS ID'].astype(str).unique().tolist()
        selected_js = st.selectbox("Select JS ID for Visit:", js_options)
        
        # Auto calculate Visit No for this JS ID
        df_visit = get_visit_dataframe()
        visit_no = 1
        if not df_visit.empty and 'JS ID' in df_visit.columns:
            existing_visits = df_visit[df_visit['JS ID'].astype(str) == selected_js]
            visit_no = len(existing_visits) + 1
        
        st.info(f"📌 Logging **Visit No: {visit_no}** for **JS ID: {selected_js}**")
        
        with st.form("technician_visit_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                installer_name = st.text_input("Installer / Technician Name*")
                status = st.selectbox("Visit Status*", ["Completed", "In Progress / Pending", "On Hold"])
                reason = st.text_input("Reason / Service Type*", value="Regular Maintenance")
            with col2:
                payment_mode = st.selectbox("Payment Mode", ["Cash", "Online / UPI", "Credit", "N/A"])
                credit_person = st.text_input("Credit Person (If Credit)")
                doc_no = st.text_input("Doc No / Slip No")
            
            time_spent = st.text_input("Time Spent", value="300 Sec (0.08 Hrs)")
            remarks = st.text_area("Visit Remarks / Service Details")
            uploaded_photo = st.file_uploader("📷 Upload Site Photo / Slip", type=['jpg', 'jpeg', 'png'])
            
            submit_visit = st.form_submit_button("💾 Submit Visit Log")
            
            if submit_visit:
                if not installer_name or not reason:
                    st.error("Please fill required fields (*)")
                else:
                    photo_url = ""
                    if uploaded_photo is not None:
                        st.info("Uploading photo to Google Drive...")
                        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{selected_js}_V{visit_no}_{timestamp_str}.png"
                        photo_url = upload_photo_to_drive(uploaded_photo, filename)
                    
                    visit_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    
                    # Columns matching Visit History tab:
                    # JS ID, Visit No, Visit Date, Installer Name, Status, Reason, Time Spent (Seconds), Payment Mode, Credit Person, Remarks, Doc No, Photo URL
                    visit_row = [
                        selected_js, visit_no, visit_date, installer_name, status, 
                        reason, time_spent, payment_mode, credit_person, remarks, doc_no, photo_url
                    ]
                    
                    visit_ws.append_row(visit_row)
                    
                    st.success(f"✅ Visit No {visit_no} for `{selected_js}` recorded successfully!")

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
    st.title("📜 Visit History Database")
    df_visit = get_visit_dataframe()
    if not df_visit.empty:
        st.dataframe(
            df_visit,
            column_config={
                "Photo URL": st.column_config.LinkColumn("Photo URL", display_text="🖼️ View Photo")
            },
            use_container_width=True
        )
    else:
        st.info("No Visit Logs Found.")
