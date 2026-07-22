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
    "👔 Manager - Create Job", 
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

# ---------------------------------------------------------
# MODULE 1: MANAGER PORTAL (Create New Job)
# ---------------------------------------------------------
if user_role == "👔 Manager - Create Job":
    st.subheader("📋 Create New Job / Complaint Entry")
    
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
            service_scope = st.selectbox("Service Scope*", ["Installation", "Dealer", "General Service"])
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
                
                # Success Notification with Direct Shareable Copy Info
                st.success(f"🎉 Job Sheet Successfully Created!")
                st.code(f"Job Sheet ID: {auto_job_id}\nClient: {client_name}\nContact: {contact_number}\nProduct: {product}", language="markdown")

# ---------------------------------------------------------
# MODULE 2: TECHNICIAN PORTAL (Job Search & Visit Entry)
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
            # PREVIOUS VISIT LOGS DISPLAY (Matching Image 1 UI)
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
                    
                    if v_status == "Completed":
                        with st.container():
                            st.markdown(f"🟢 **# Visit #{v_no}** — **Status: Completed**")
                            st.caption(f"📅 **Date:** {v_date} | 👤 **Tech:** {v_tech} | ⏱️ **Time Spent:** {v_time}")
                            if visit["Doc No"] != "N/A":
                                st.caption(f"📑 **Paper Slip No:** {visit['Doc No']}")
                            st.write(f"💬 *Remarks:* {v_remarks}")
                            if visit["Photo URL"] != "N/A":
                                st.markdown(f"[📷 View Uploaded Photo]({visit['Photo URL']})")
                            st.markdown("---")
                    else:
                        with st.container():
                            st.markdown(f"🟡 **# Visit #{v_no}** — **Status: Pending**")
                            st.caption(f"📅 **Date:** {v_date} | 👤 **Tech:** {v_tech} | ⏱️ **Time Spent:** {v_time}")
                            st.error(f"⚠️ **Reason for Pending:** {visit['Reason']}")
                            st.write(f"💬 *Remarks:* {v_remarks}")
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

                        # 1. Add Entry to Visit History Database
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

                        # 2. Update Master Job Database
                        idx = master_df[master_df["Job Sheet No"] == search_job_id].index[0]
                        st.session_state["master_data"].at[idx, "Current Status"] = status_update
                        st.session_state["master_data"].at[idx, "Final Installer"] = installer_name
                        st.session_state["master_data"].at[idx, "Total Visits"] = next_visit_no
                        
                        if status_update == "Completed":
                            st.session_state["master_data"].at[idx, "Close Date"] = today_str
                        
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
# MODULE 4: VISIT HISTORY DATABASE VIEW (Matching Image 2 Table)
# ---------------------------------------------------------
elif user_role == "📜 View Visit History Database":
    st.subheader("📜 Visit History Database")
    st.dataframe(st.session_state["visit_history"], use_container_width=True)
