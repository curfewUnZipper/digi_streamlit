import streamlit as st
import requests

API = "http://YOUR_IP:8000"

st.title("🔥 Remote Fan Controller")

# Control
stage = st.slider("Target Stage", 0, 10, 7)

if st.button("Set"):
    requests.post(f"{API}/set/{stage}")

# Status
res = requests.get(f"{API}/status").json()

st.metric("Stage", res["stage"])
st.metric("Fan1", res["fan1"])
st.metric("Fan2", res["fan2"])
st.metric("Workers", res["workers"])