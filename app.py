import streamlit as st
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Sidharth Shutter & Automation CRM", 
    page_icon="🛠️", 
    layout="wide"
)

# ---------------------------------------------------------
# APP HEADER & BRANDING
# ---------------------------------------------------------
# Sidebar Branding
st.sidebar.title("🏢 Sidharth Shutter")
st.sidebar.subheader("& Automation")
st.sidebar.markdown("---")

user_role = st.sidebar.radio("Choose Section:", [
    "📈 Executive Dashboard",
    "👔 Manager - Create / Edit Job", 
    "🔧 Technician - Job Visit", 
    "📊 View All Jobs (Master Sheet)",
    "📜 View Visit History Database"
])

st.sidebar.markdown("---")
st.sidebar.caption("© Sidharth Shutter & Automation v1.0")

# Main Page Header
st.title("🛠️ Sidharth Shutter & Automation")
st.caption("Field Operations & Technician Service CRM Portal")
st.markdown("---")

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

# Payment Mode Options
PAYMENT_MODES = ["UPI", "Cash", "In Account", "Credit Care of"]

# ---------------------------------------------------------
# INITIALIZE SESSION DATABASES WITH SAMPLE ENTRIES
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

# Helper Function to Sync Master Sheet Status
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
# MODULE 0: EXECUTIVE DASHBOARD MODULE
# ---------------------------------------------------------
if user_role == "📈 Executive Dashboard":
    st.subheader("📊 Executive Operations & Performance Dashboard")
    
    m_df = st.session_state["master_data"]
    
    # 1. TOP METRICS CARDS
    total_jobs = len(m_df)
    completed_jobs = len(m_df[m_df["Current Status"] == "Completed"])
    pending_jobs = len(m_df[m_df["Current Status"] == "Pending"])
    completion_rate = round((completed_jobs / total_jobs * 100), 1) if total_jobs > 0 else 0
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("📌 Total JS IDs / Leads", total_jobs)
    kpi2.metric("🟢 Completed Jobs", completed_jobs, f"{completion_rate}% Done")
    kpi3.metric("🟡 Pending Jobs", pending_jobs, f"-{round(100 - completion_rate, 1)}%", delta_color="inverse")
    kpi4.metric("⚙️ Service Completion Rate", f"{completion_rate}%")
    
    st.markdown("---")
    
    # 2. ANALYTICAL CHARTS
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("### 🏷️ Jobs by Category")
        cat_counts = m_df["Job Category"].value_counts().reset_index()
        cat_counts.columns = ["Job Category", "Count"]
        st.bar_chart(cat_counts.set_index("Job Category"), color="#36A2EB")
        
        st.markdown("### 🗺️ State-wise Distribution")
        state_counts = m_df["State"].value_counts().reset_index()
        state_counts.columns = ["State", "Total Jobs"]
        st.bar_chart(state_counts.set_index("State"), color="#FFCE56")

    with chart_col2:
        st.markdown("### 🎯 Jobs by Service Scope")
        scope_counts = m_df["Service Scope"].value_counts().reset_index()
        scope_counts.columns = ["Service Scope", "Count"]
        st.bar_chart(scope_counts.set_index("Service Scope"), color="#4BC0C0")
        
        st.markdown("### 🛡️ Warranty Coverage Breakdown")
        war_counts = m_df["Warranty"].value_counts().reset_index()
        war_counts.columns = ["Under Warranty", "Count"]
        st.dataframe(war_counts, use_container_width=True)

# ---------------------------------------------------------
# MODULE 1: MANAGER PORTAL (Create & Edit Job Entry)
# ---------------------------------------------------------
elif user_role == "👔 Manager - Create / Edit Job":
    st.subheader("📋 Manager Operations Portal")
    
    tab1, tab2 = st.tabs(["➕ Create New JS ID", "✏️ Search & Edit Job Details"])
    
    # ------------------ TAB 1: CREATE JOB ------------------
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

            submit_job = st.form_submit_button("🚀 Generate JS ID")

            if submit_job:
                if not client_name or not contact_number or not address or not office_remark:
                    st.error("⚠️ Please fill all mandatory fields (Client Name, Contact, Address, Initial Remark)!")
                else:
                    new_row = {
                        "JS ID": auto_job_id,
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
                        "Warranty": warranty,
                        "Office Remark": office_remark,
                        "Current Status": "Pending",
                        "Total Visits": 0,
                        "Final Installer": "Not Assigned",
                        "Close Date": "N/A"
                    }
                    st.session_state["master_data"] = pd.concat([st.session_state["master_data"], pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"🎉 JS ID **{auto_job_id}** Successfully Created!")

    # ------------------ TAB 2: EDIT EXISTING JOB ------------------
    with tab2:
        search_edit_id = st.text_input("Enter JS ID to Edit (e.g. JS-101):").strip().upper()
        
        if search_edit_id:
            m_df = st.session_state["master_data"]
            match = m_df[m_df["JS ID"] == search_edit_id]
            
            if not match.empty:
                idx = match.index[0]
                job_row = match.iloc[0]
                st.warning(f"✏️ Editing Details for **{search_edit_id}** ({job_row['Client Name']})")
                
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
                        st.session_state["master_data"].at[idx, "Warranty"] = e_warranty
                        st.session_state["master_data"].at[idx, "Office Remark"] = e_remark
                        
                        st.success(f"✅ Details for **{search_edit_id}** updated successfully!")
                        st.rerun()
            else:
                st.error(f"❌ No record found with JS ID: '{search_edit_id}'")

# ---------------------------------------------------------
# MODULE 2: TECHNICIAN PORTAL (Job Search & Visit Entry)
# ---------------------------------------------------------
elif user_role == "🔧 Technician - Job Visit":
    st.subheader("🔍 Technician Job Search & Visit Update")
    
    search_job_id = st.text_input("Enter JS ID (e.g. JS-101):").strip().upper()
    
    if search_job_id:
        master_df = st.session_state["master_data"]
        job_match = master_df[master_df["JS ID"] == search_job_id]
        
        if not job_match.empty:
            job_details = job_match.iloc[0]
            current_job_status = job_details["Current Status"]
            
            st.success(f"Job Found: **{job_details['Client Name']}** ({job_details['JS ID']})")
            
            # Client & Job Details Header
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
            
            # PREVIOUS VISIT LOGS
            st.subheader("📜 Previous Visit Logs")
            v_df = st.session_state["visit_history"]
            previous_visits = v_df[v_df["JS ID"] == search_job_id].sort_values(by="Visit No", ascending=False)
            
            if not previous_visits.empty:
                for _, visit in previous_visits.iterrows():
                    v_no = visit["Visit No"]
                    v_status = visit["Status"]
                    v_date = visit["Visit Date"]
                    v_tech = visit["Installer Name"]
                    v_time = visit["Time Spent"]
                    v_remarks = visit["Remarks"]
                    
                    status_badge = "🟢 Completed" if v_status == "Completed" else "🟡 Pending"
                    
                    st.markdown(f"**# Visit #{v_no}** — **Status: {status_badge}**")
                    st.caption(f"📅 **Date:** {v_date} | 👤 **Tech:** {v_tech} | ⏱️ **Time Spent:** {v_time}")
                    if visit.get("Payment Mode") and visit["Payment Mode"] != "N/A":
                        pay_str = f"💳 **Payment Mode:** {visit['Payment Mode']}"
                        if visit.get("Credit Person") and visit["Credit Person"] != "N/A":
                            pay_str += f" *(Credit Given By: {visit['Credit Person']})*"
                        st.caption(pay_str)
                    if v_status == "Pending":
                        st.error(f"⚠️ **Reason for Pending:** {visit['Reason']}")
                    if visit["Doc No"] != "N/A":
                        st.caption(f"📑 **Paper Slip No:** {visit['Doc No']}")
                    st.write(f"💬 *Remarks:* {v_remarks}")
                    st.markdown("---")
            else:
                st.info("ℹ️ No previous visit logs found for this JS ID. This will be Visit #1.")
            
            # NEW VISIT REPORT ENTRY FORM
            if current_job_status == "Completed":
                st.success("🎉 **This Job Sheet is officially CLOSED & COMPLETED!** No further visits are required for this JS ID.")
            else:
                next_visit_no = len(previous_visits) + 1
                st.subheader(f"📝 Submit New Visit Report (Visit #{next_visit_no})")
                
                # Dynamic Status Selector Outside Form for Reactivity
                status_update = st.selectbox("Update Work Status*", ["Pending", "Completed"], key="live_status_select")

                # Dynamic Payment Mode Selector
                pay_col1, pay_col2 = st.columns(2)
                with pay_col1:
                    payment_mode = st.selectbox("Payment Mode*", PAYMENT_MODES, key="pay_mode_select")
                
                credit_person_name = "N/A"
                with pay_col2:
                    if payment_mode == "Credit Care of":
                        credit_person_name = st.text_input("Technician / Team Member Name (Credit Given By)*", placeholder="Enter team member name")

                with st.form("tech_visit_form"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        installer_name = st.text_input("Technician / Installer Name*")
                        time_spent = st.selectbox("Time Spent on Site*", ["30 Mins", "1 Hour", "1.5 Hours", "2 Hours", "3+ Hours", "Full Day"])
                    
                    with col_b:
                        pending_reason = "N/A"
                        if status_update == "Pending":
                            pending_reason = st.selectbox("Reason for Pending*", PENDING_REASONS)
                        else:
                            st.success("✅ Complete status selected. Fill slip & photo upload below.")

                    visit_remarks = st.text_area("Visit Remarks / Work Done Notes*")

                    physical_job_no = "N/A"
                    photo_file = None
                    photo_url = "N/A"
                    
                    if status_update == "Completed":
                        st.info("🔒 **Completion Protocol Active:** Physical Paper Slip No. & Photo Upload are required!")
                        col_c, col_d = st.columns(2)
                        with col_c:
                            physical_job_no = st.text_input("Physical Paper Job Sheet Slip No.*")
                        with col_d:
                            photo_file = st.file_uploader("Upload Job Sheet / Work Photo*", type=["jpg", "png", "jpeg"])

                    submit_visit = st.form_submit_button("📤 Submit Visit Report")

                    if submit_visit:
                        if not installer_name or not visit_remarks:
                            st.error("⚠️ Technician Name and Remarks are required!")
                        elif payment_mode == "Credit Care of" and not credit_person_name.strip():
                            st.error("⚠️ Please specify the Technician / Team Member name who authorized 'Credit Care of'!")
                        elif status_update == "Completed" and (not physical_job_no or photo_file is None):
                            st.error("❌ Cannot complete job! Physical Job Sheet Slip No. and Photo are mandatory for completed status.")
                        else:
                            today_str = datetime.now().strftime("%d-%b-%Y")
                            if photo_file is not None:
                                photo_url = f"https://drive.google.com/uploaded_file_{physical_job_no}.jpg"

                            new_visit_row = {
                                "JS ID": search_job_id,
                                "Visit No": next_visit_no,
                                "Visit Date": today_str,
                                "Installer Name": installer_name,
                                "Status": status_update,
                                "Reason": pending_reason,
                                "Time Spent": time_spent,
                                "Payment Mode": payment_mode,
                                "Credit Person": credit_person_name if payment_mode == "Credit Care of" else "N/A",
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
            st.error(f"❌ No record found with JS ID: '{search_job_id}'")

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
    st.subheader("📜 View Visit History Database")
    st.dataframe(st.session_state["visit_history"], use_container_width=True)
