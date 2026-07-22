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
user_role = st.sidebar.radio("Choose Section:", ["👔 Manager - Create Job", "🔧 Technician - Job Visit", "📊 View All Jobs (Master Sheet)"])

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

# Product List from Image + Other
PRODUCT_LIST = [
    "Automatic Rolling Shutters",
    "Dock Leveller",
    "Dock Shelter",
    "High-Speed Roll Up Door",
    "High-Speed Fold Up Door",
    "High-Speed Self Repairable Door",
    "Residential Sectional Doors",
    "Industrial Sectional Door",
    "Hermetic Doors",
    "Fire Exit Door",
    "Auto Sliding Door",
    "Motorised Swing Gates",
    "Motorised Sliding Gates",
    "Retractable Gates",
    "Boom Barriers",
    "Strong Life Shutter Motor",
    "Manual Shutters",
    "Wind Shutters",
    "Spare Part",
    "Service Charge",
    "Sensor / Automatic Glass Door",
    "Motors",
    "Dock Bumper",
    "Dock Edge",
    "Overhead Sectional Door",
    "Tank Door Shutter",
    "Gear Shutter",
    "General purpose Doors",
    "Hanger Door",
    "Impact Barrier",
    "Manual Swing Gate",
    "Manual Sliding Gate",
    "Other"
]

# Simulated Database with New Column Structure
if "master_data" not in st.session_state:
    st.session_state["master_data"] = pd.DataFrame([
        {
            "Job Sheet No": "JS-101",
            "Date": "22-Jul-2026",
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
            "Current Status": "Pending",
            "Total Visits": 1,
            "Final Installer": "Rahul Sharma",
            "Close Date": "N/A"
        }
    ])

# ---------------------------------------------------------
# MODULE 1: MANAGER PORTAL (Create New Job)
# ---------------------------------------------------------
if user_role == "👔 Manager - Create Job":
    st.subheader("📋 Create New Job / Complaint Entry")
    
    # Auto ID Generation Logic
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
                st.success(f"✅ Job Sheet **{auto_job_id}** created successfully for {client_name}!")

# ---------------------------------------------------------
# MODULE 2: TECHNICIAN PORTAL (Job Search & Visit Entry)
# ---------------------------------------------------------
elif user_role == "🔧 Technician - Job Visit":
    st.subheader("🔍 Technician Job Search & Visit Update")
    
    search_job_id = st.text_input("Enter Job Sheet No. (e.g. JS-101):").strip().upper()
    
    if search_job_id:
        df = st.session_state["master_data"]
        job_match = df[df["Job Sheet No"] == search_job_id]
        
        if not job_match.empty:
            job_details = job_match.iloc[0]
            st.success(f"Job Found: **{job_details['Client Name']}** ({job_details['Job Sheet No']})")
            
            # Display Client & Job Details Cards
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Client Name", job_details["Client Name"])
            c2.metric("Product (QTY)", f"{job_details['Product']} ({job_details['QTY']})")
            c3.metric("Type / Scope", f"{job_details['Job Category']} / {job_details['Service Scope']}")
            c4.metric("Status", job_details["Current Status"])
            
            st.write(f"📍 **Address:** {job_details['Address']}, {job_details['Location']}, {job_details['State']}")
            st.write(f"📞 **Contact:** {job_details['Contact Number']}")
            
            # Office Remark Displayed for Installer Info
            st.warning(f"📝 **Job Description / Issue Note:** {job_details['Office Remark']}")
            st.markdown("---")
            
            # Technician Report Form
            st.subheader("📝 Submit Visit Report")
            with st.form("tech_visit_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    installer_name = st.text_input("Technician / Installer Name*")
                    time_spent = st.selectbox("Time Spent on Site*", ["30 Mins", "1 Hour", "2 Hours", "3+ Hours", "Full Day"])
                
                with col_b:
                    status_update = st.selectbox("Update Work Status*", ["Pending", "Completed"])
                    visit_remarks = st.text_area("Visit Remarks / Work Done Notes*")

                physical_job_no = ""
                photo_file = None
                
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
                        idx = df[df["Job Sheet No"] == search_job_id].index[0]
                        st.session_state["master_data"].at[idx, "Current Status"] = status_update
                        st.session_state["master_data"].at[idx, "Final Installer"] = installer_name
                        st.session_state["master_data"].at[idx, "Total Visits"] += 1
                        
                        if status_update == "Completed":
                            st.session_state["master_data"].at[idx, "Close Date"] = datetime.now().strftime("%d-%b-%Y")
                        
                        st.balloons()
                        st.success(f"🎉 Visit Report submitted for {search_job_id}! Status updated to '{status_update}'.")
        else:
            st.error(f"❌ No job found with ID: '{search_job_id}'")

# ---------------------------------------------------------
# MODULE 3: MASTER DATABASE VIEW
# ---------------------------------------------------------
elif user_role == "📊 View All Jobs (Master Sheet)":
    st.subheader("📋 Master Job Sheet Database")
    st.dataframe(st.session_state["master_data"], use_container_width=True)
