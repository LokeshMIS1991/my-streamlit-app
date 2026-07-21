import streamlit as st
import pandas as pd

# Page Configuration - Odoo/Zoho Style
st.set_page_config(page_title="Company CRM", layout="wide")

# Sidebar - CRM Navigation
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60)
st.sidebar.title("Company CRM")
menu = st.sidebar.radio("Navigation", ["📊 Dashboard", "➕ Add New Lead", "📁 All Leads / Database"])

st.sidebar.markdown("---")
st.sidebar.caption("Logged in as: Admin")

# --- 1. DASHBOARD VIEW ---
if menu == "📊 Dashboard":
    st.title("CRM Overview")
    
    # Top KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Leads", "128", "+12%")
    col2.metric("New Enquiries", "24", "+5")
    col3.metric("Deals Closed", "18", "INR 4.5L")
    col4.metric("Pending Follow-ups", "9", "-2")
    
    st.markdown("---")
    st.subheader("Recent Leads Overview")
    
    # Dummy Data Table
    dummy_data = pd.DataFrame({
        "Client Name": ["Rahul Sharma", "Priya Verma", "Amit Patel"],
        "Company": ["TechCorp", "Design Studio", "Logistics Ltd"],
        "Phone": ["9876543210", "9812345678", "9900112233"],
        "Status": ["New", "In Progress", "Closed/Won"],
        "Value (INR)": ["50,000", "1,20,000", "2,00,000"]
    })
    st.dataframe(dummy_data, use_container_width=True)

# --- 2. ADD NEW LEAD FORM ---
elif menu == "➕ Add New Lead":
    st.title("Create New Lead")
    
    with st.form("crm_lead_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Client Full Name*")
            email = st.text_input("Email Address")
            source = st.selectbox("Lead Source", ["Website", "Call", "Referral", "LinkedIn"])
        with c2:
            phone = st.text_input("Phone Number*")
            company = st.text_input("Company Name")
            value = st.number_input("Expected Deal Value (INR)", min_value=0)
            
        status = st.selectbox("Lead Status", ["New Enquiry", "Contacted", "Proposal Sent", "Closed - Won", "Closed - Lost"])
        notes = st.text_area("Remarks / Follow-up Notes")
        
        submitted = st.form_submit_button("Save Lead to CRM 🚀")
        if submitted:
            st.success(f"Lead for '{name}' successfully created!")

# --- 3. ALL LEADS DATABASE VIEW ---
elif menu == "📁 All Leads / Database":
    st.title("Lead Database")
    st.text_input("🔍 Search Leads by Name, Phone, or Company...")
    
    # Filter Tabs
    tab1, tab2, tab3 = st.tabs(["All", "Hot Leads", "Closed Deals"])
    with tab1:
        st.info("Yahan aapki poori Google Sheet/Database ka data load hoga.")
