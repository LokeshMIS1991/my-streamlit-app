import streamlit as st
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="TechFlow CRM - FieldOps", layout="wide")

# App Header & Branding
st.title("🛠️ TechFlow CRM — Field Operations Portal")

# Sidebar Navigation
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1055/1055644.png", width=70)
st.sidebar.title("Navigation")
user_role = st.sidebar.radio("Choose Section:", [
    "👔 Manager - Create / Edit Job", 
    "🔧 Technician - Job Visit", 
    "📊 View All Jobs (Master Sheet)",
    "📜 View Visit History Database"
])

st.sidebar.markdown("---")
st.sidebar.caption("TechFlow CRM v1.0")

# Indian States List
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", 
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", 
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", 
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", 
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", 
    "Delhi NCR", "Other"
]

# Product List
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

# Pending Reason Options
PENDING_REASONS = [
    "Material Not Available", "Power Outage / Technical Issue", 
    "Customer Not Available", "Site Not Ready", "Other"
]

# ---------------------------------------------------------
# INITIALIZE SESSION DATABASES
# ---------------------------------------------------------
if "master_data" not in st.session_state:
    st.session_state["master_data"] = pd.DataFrame([
        {
            "Job Sheet No": "JS-101",
            "Date": "17-Jul-2026",
            "Month": "July",
            "Client Name": "Lokesh Enterprises",
            "Project Name": "CRM Office Setup",
            "Contact Number": "9876543210",
            "Address": "Malviya Nagar, Jaipur",
            "Location": "Jaipur",
            "State": "Rajasthan",
            "Product": "Automatic Rolling Shutters",
            "Job Category": "Complaint",
            "Service Scope": "General Service",
            "QTY": 1,
            "Office Remark": "Remote control frequency issue and motor sensor jamming.",
            "Current Status": "Completed",
            "Total Visits": 2,
            "Final Installer": "Hariom",
            "Close Date": "18-Jul-2026"
        }
    ])

if "visit_history" not in st.session_state:
    st.session_state["visit_history"] = pd.DataFrame([
        {
            "Job Sheet No": "JS-101",
            "Visit No": 1,
            "Visit Date": "17-Jul-2026",
            "Installer Name": "Lokesh Kumar",
            "Status": "Pending",
            "Reason": "Power Outage / Technical Issue",
            "Time Spent": "2 Hours",
            "Remarks": "There is some power outage on site.",
            "Doc No": "N/A",
            "Photo URL": "N/A"
        },
        {
            "Job Sheet No": "JS-101",
            "Visit No": 2,
            "Visit Date": "18-Jul-2026",
            "Installer Name": "Hariom",
            "Status": "Completed",
            "Reason": "N/A",
            "Time Spent": "1 Hour",
            "Remarks": "Work is completed successfully.",
            "Doc No": "1234",
            "Photo URL": "https://drive.google.com/file/d/sample_photo/view"
        }
    ])

# Helper Function to Sync Master Sheet Status
def sync_master_status(job_id):
    v_df = st.session_state["visit_history"]
    m_df = st.session_state["master_data"]
    
    job_visits = v_df[v_df["Job Sheet No"] == job_id]
    if not job_visits.empty:
        last_visit = job_visits.iloc[-1]
        m_idx = m_df[m_df["Job Sheet No"] == job_id].index[0]
        
        st.session_state["master_data"].at[m_idx, "Current Status"] = last_visit["Status"]
        st.session_state["master_data"].at[m_idx, "Final Installer"] = last_visit["Installer Name"]
        st.session_state["master_data"].at[m_idx, "Total Visits"] = len(job_visits)
        
        if last_visit["Status"] == "Completed":
            st.session_state["master_data"].at[m_idx, "Close Date"] = last_visit["Visit Date"]
        else:
            st.session_state["master_data"].at[m_idx, "Close Date"] = "N/A"

# ---------------------------------------------------------
# MODULE 1: MANAGER PORTAL (Create & Edit Job Entry)
# ---------------------------------------------------------
if user_role == "👔 Manager - Create / Edit Job":
    st.subheader("📋 Manager Operations Portal")
    
    tab1, tab2 = st.tabs(["➕ Create New Job Sheet", "✏️ Search & Edit Job Details"])
    
    # ------------------ TAB 1: CREATE JOB ------------------
    with tab1:
        existing_jobs = len(st.session_state["master_data"])
        auto_job_id = f"JS-{101 + existing_jobs}"
        current_now = datetime.now()
        auto_date = current_now.strftime("%d-%b-%Y")
        auto_month = current_now.strftime("%B")

        st.info(f"⚡ **Auto Generated Details:** Job ID: **{auto_job_id}** | Date: **{auto_date}** | Month: **{auto_month}**")

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
                service_scope = st.selectbox("Service Scope*", ["Installation", "Dealer", "General Service","Sidharth"])
                qty = st.number_input("Quantity (QTY)*", min_value=1, value=1, step=1)
                office_remark = st.text_area("Initial Job Remark / Issue Description (For Installer)*")

            submit_job = st.form_submit_button("🚀 Generate Job Sheet")

            if submit_job:
                if not client_name or not contact_number or not address or not office_remark:
                    st.error("⚠️ Please fill all mandatory fields (Client Name, Contact, Address, Initial Remark)!")
                else:
                    new_row = {
                        "Job Sheet No": auto_job_id,
                        "Date": auto_date,
                        "Month": auto_month,
                        "Client Name": client_name,
                        "Project Name": project_name,
                        "Contact Number": contact_number,
                        "Address": address,
                        "Location": location,
                        "State": state,
                        "Product": product,
                        "Job Category": job_category,
                        "Service Scope": service_scope,
                        "QTY": qty,
                        "Office Remark": office_remark,
                        "Current Status": "Pending",
                        "Total Visits": 0,
                        "Final Installer": "Not Assigned",
                        "Close Date": "N/A"
                    }
                    st.session_state["master_data"] = pd.concat([st.session_state["master_data"], pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"🎉 Job Sheet **{auto_job_id}** Successfully Created!")
                    st.code(f"Job Sheet ID: {auto_job_id}\nClient: {client_name}\nContact: {contact_number}\nProduct: {product}", language="markdown")

    # ------------------ TAB 2: EDIT EXISTING JOB ------------------
    with tab2:
        search_edit_id = st.text_input("Enter Job Sheet No to Edit (e.g. JS-101):").strip().upper()
        
        if search_edit_id:
            m_df = st.session_state["master_data"]
            match = m_df[m_df["Job Sheet No"] == search_edit_id]
            
            if not match.empty:
                idx = match.index[0]
                job_row = match.iloc[0]
                st.warning(f"✏️ Editing Job Sheet: **{search_edit_id}** ({job_row['Client Name']})")
                
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
                        e_remark = st.text_area("Office Remark", value=job_row["Office Remark"])

                    update_master_btn = st.form_submit_button("💾 Save Updated Job Details")

                    if update_master_btn:
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
                        st.session_state["master_data"].at[idx, "Office Remark"] = e_remark
                        
                        st.success(f"✅ Job Details for **{search_edit_id}** updated successfully!")
                        st.rerun()
            else:
                st.error(f"❌ No Job Sheet found with ID: '{search_edit_id}'")

# ---------------------------------------------------------
# MODULE 2: TECHNICIAN PORTAL (Job Search, Visit Entry & Edit)
# ---------------------------------------------------------
elif user_role == "🔧 Technician - Job Visit":
    st.subheader("🔍 Technician Job Search & Visit Update")
    
    search_job_id = st.text_input("Enter Job Sheet No. (e.g. JS-101):").strip().upper()
    
    if search_job_id:
        master_df = st.session_state["master_data"]
        job_match = master_df[master_df["Job Sheet No"] == search_job_id]
        
        if not job_match.empty:
            job_details = job_match.iloc[0]
            st.success(f"Job Found: **{job_details['Client Name']}** ({job_details['Job Sheet No']})")
            
            # Client & Job Details Header
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Client Name", job_details["Client Name"])
            c2.metric("Product (QTY)", f"{job_details['Product']} ({job_details['QTY']})")
            c3.metric("Type / Scope", f"{job_details['Job Category']} / {job_details['Service Scope']}")
            c4.metric("Total Visits", job_details["Total Visits"])
            
            st.write(f"📍 **Address:** {job_details['Address']}, {job_details['Location']}, {job_details['State']}")
            st.write(f"📞 **Contact:** {job_details['Contact Number']}")
            st.warning(f"📝 **Job Description / Issue Note:** {job_details['Office Remark']}")
            
            st.markdown("---")
            
            # -------------------------------------------------
            # PREVIOUS VISIT LOGS WITH EDIT FEATURE
            # -------------------------------------------------
            st.subheader("📜 Previous Visit Logs")
            v_df = st.session_state["visit_history"]
            previous_visits = v_df[v_df["Job Sheet No"] == search_job_id].sort_values(by="Visit No", ascending=False)
            
            if not previous_visits.empty:
                for _, visit in previous_visits.iterrows():
                    v_no = visit["Visit No"]
                    v_status = visit["Status"]
                    v_date = visit["Visit Date"]
                    v_tech = visit["Installer Name"]
                    v_time = visit["Time Spent"]
                    v_remarks = visit["Remarks"]
                    
                    status_badge = "🟢 Completed" if v_status == "Completed" else "🟡 Pending"
                    
                    col_log1, col_log2 = st.columns([4, 1])
                    with col_log1:
                        st.markdown(f"**# Visit #{v_no}** — **Status: {status_badge}**")
                        st.caption(f"📅 **Date:** {v_date} | 👤 **Tech:** {v_tech} | ⏱️ **Time Spent:** {v_time}")
                        if v_status == "Pending":
                            st.error(f"⚠️ **Reason for Pending:** {visit['Reason']}")
                        if visit["Doc No"] != "N/A":
                            st.caption(f"📑 **Paper Slip No:** {visit['Doc No']}")
                        st.write(f"💬 *Remarks:* {v_remarks}")
                    
                    with col_log2:
                        edit_btn = st.button(f"✏️ Edit Visit #{v_no}", key=f"edit_btn_{v_no}")
                        if edit_btn:
                            st.session_state["editing_visit_no"] = v_no

                    # EDIT FORM EXPANDER
                    if st.session_state.get("editing_visit_no") == v_no:
                        with st.expander(f"🛠️ Edit Details for Visit #{v_no}", expanded=True):
                            with st.form(f"edit_form_{v_no}"):
                                edit_tech = st.text_input("Installer Name", value=v_tech)
                                edit_time = st.selectbox("Time Spent", ["30 Mins", "1 Hour", "1.5 Hours", "2 Hours", "3+ Hours", "Full Day"], index=0)
                                edit_status = st.selectbox("Status", ["Pending", "Completed"], index=0 if v_status=="Pending" else 1)
                                
                                edit_reason = visit["Reason"]
                                if edit_status == "Pending":
                                    edit_reason = st.selectbox("Reason for Pending", PENDING_REASONS)
                                else:
                                    edit_reason = "N/A"
                                    
                                edit_doc = st.text_input("Paper Slip No", value=visit["Doc No"])
                                edit_remarks = st.text_area("Remarks", value=v_remarks)
                                
                                save_edit = st.form_submit_button("💾 Update Visit Entry")
                                if save_edit:
                                    v_idx = v_df[(v_df["Job Sheet No"] == search_job_id) & (v_df["Visit No"] == v_no)].index[0]
                                    st.session_state["visit_history"].at[v_idx, "Installer Name"] = edit_tech
                                    st.session_state["visit_history"].at[v_idx, "Time Spent"] = edit_time
                                    st.session_state["visit_history"].at[v_idx, "Status"] = edit_status
                                    st.session_state["visit_history"].at[v_idx, "Reason"] = edit_reason
                                    st.session_state["visit_history"].at[v_idx, "Doc No"] = edit_doc
                                    st.session_state["visit_history"].at[v_idx, "Remarks"] = edit_remarks
                                    
                                    sync_master_status(search_job_id)
                                    
                                    st.session_state["editing_visit_no"] = None
                                    st.success(f"✅ Visit #{v_no} successfully updated!")
                                    st.rerun()

                    st.markdown("---")
            else:
                st.info("ℹ️ No previous visit logs found for this Job Sheet. This will be Visit #1.")
            
            # -------------------------------------------------
            # NEW VISIT REPORT ENTRY FORM
            # -------------------------------------------------
            next_visit_no = len(previous_visits) + 1
            st.subheader(f"📝 Submit New Visit Report (Visit #{next_visit_no})")
            
            with st.form("tech_visit_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    installer_name = st.text_input("Technician / Installer Name*")
                    time_spent = st.selectbox("Time Spent on Site*", ["30 Mins", "1 Hour", "1.5 Hours", "2 Hours", "3+ Hours", "Full Day"])
                
                with col_b:
                    status_update = st.selectbox("Update Work Status*", ["Pending", "Completed"])
                    
                pending_reason = "N/A"
                if status_update == "Pending":
                    pending_reason = st.selectbox("Reason for Pending*", PENDING_REASONS)
                    
                visit_remarks = st.text_area("Visit Remarks / Work Done Notes*")

                physical_job_no = "N/A"
                photo_file = None
                photo_url = "N/A"
                
                if status_update == "Completed":
                    st.info("🔒 **Completion Protocol Active:** Physical Job Sheet No. & Photo Upload are required!")
                    col_c, col_d = st.columns(2)
                    with col_c:
                        physical_job_no = st.text_input("Physical Paper Job Sheet Slip No.*")
                    with col_d:
                        photo_file = st.file_uploader("Upload Job Sheet / Work Photo*", type=["jpg", "png", "jpeg"])

                submit_visit = st.form_submit_button("📤 Submit Visit Report")

                if submit_visit:
                    if not installer_name or not visit_remarks:
                        st.error("⚠️ Technician Name and Remarks are required!")
                    elif status_update == "Completed" and (not physical_job_no or photo_file is None):
                        st.error("❌ Cannot complete job! Physical Job Sheet No. and Photo are mandatory for completed status.")
                    else:
                        today_str = datetime.now().strftime("%d-%b-%Y")
                        if photo_file is not None:
                            photo_url = f"https://drive.google.com/uploaded_file_{physical_job_no}.jpg"

                        new_visit_row = {
                            "Job Sheet No": search_job_id,
                            "Visit No": next_visit_no,
                            "Visit Date": today_str,
                            "Installer Name": installer_name,
                            "Status": status_update,
                            "Reason": pending_reason,
                            "Time Spent": time_spent,
                            "Remarks": visit_remarks,
                            "Doc No": physical_job_no,
                            "Photo URL": photo_url
                        }
                        st.session_state["visit_history"] = pd.concat([st.session_state["visit_history"], pd.DataFrame([new_visit_row])], ignore_index=True)

                        sync_master_status(search_job_id)
                        
                        st.balloons()
                        st.success(f"🎉 Visit #{next_visit_no} Report submitted for {search_job_id}!")
                        st.rerun()
        else:
            st.error(f"❌ No job found with ID: '{search_job_id}'")

# ---------------------------------------------------------
# MODULE 3: MASTER JOB SHEET DATABASE VIEW
# ---------------------------------------------------------
elif user_role == "📊 View All Jobs (Master Sheet)":
    st.subheader("📋 Master Job Sheet Database")
    st.dataframe(st.session_state["master_data"], use_container_width=True)

# ---------------------------------------------------------
# MODULE 4: VISIT HISTORY DATABASE VIEW
# ---------------------------------------------------------
elif user_role == "📜 View Visit History Database":
    st.subheader("📜 Visit History Database")
    st.dataframe(st.session_state["visit_history"], use_container_width=True)
