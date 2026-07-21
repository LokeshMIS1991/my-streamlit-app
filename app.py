import streamlit as st

# 1. Page Config & Titles
st.set_page_config(page_title="Mera Pehla App", page_icon="🚀")
st.title("👋 Namaste World!")
st.subheader("Streamlit se bana mera pehla live web page")

# 2. Interactive Input
name = st.text_input("Aapka naam kya hai?")

# 3. Logic: Welcome Message
if name:
    st.success(f"Welcome {name}!")

# 4. Interactive Button
if st.button("Mujhe Click Karo"):
    st.balloons()