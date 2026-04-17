import streamlit as st
import pandas as pd
import requests

API_URL = "http://127.0.0.1:5000"

features = [
    "fan1","fan2",
    "cpu_temp","gpu_temp","nvidia_temp",
    "cpu_usage",
    "current","power"
]

st.set_page_config(layout="wide")
st.title("🌀 Fan RUL Dashboard")

# =========================
# SESSION STATE
# =========================
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=features)

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4 = st.tabs(["RUL", "Graphs", "Table", "Input"])

# =========================
# TAB 4 — INPUT
# =========================
with tab4:

    st.subheader("Upload CSV")
    file = st.file_uploader("Upload CSV")

    if file:
        df = pd.read_csv(file)
        st.session_state.data = df

    st.subheader("Manual Input")

    input_data = {}

    for f in features:
        input_data[f] = st.slider(f, 0.0, 200.0, 50.0)

    if st.button("Add Row"):
        st.session_state.data = pd.concat(
            [st.session_state.data, pd.DataFrame([input_data])],
            ignore_index=True
        )

    if st.button("Add 50 Rows"):
        rows = pd.DataFrame([input_data]*50)
        st.session_state.data = pd.concat(
            [st.session_state.data, rows],
            ignore_index=True
        )

# =========================
# CALL API
# =========================
def get_rul(df):

    if len(df) < 50:
        return None

    response = requests.post(
        f"{API_URL}/predict_batch",
        json=df.to_dict(orient="records")
    )

    return response.json()["RUL"]


# =========================
# TAB 1 — RUL
# =========================
with tab1:

    rul = get_rul(st.session_state.data)

    if rul is None:
        st.warning("Need at least 50 rows")
    else:
        st.metric("RUL", f"{rul:.4f}")

        if rul > 0.7:
            st.success("Fan is Healthy ✅")
        elif rul > 0.4:
            st.warning("Moderate Wear ⚠️")
        else:
            st.error("Critical Condition 🚨")


# =========================
# TAB 2 — GRAPHS
# =========================
with tab2:

    df = st.session_state.data

    if not df.empty:
        st.line_chart(df[["fan1","fan2"]])
        st.line_chart(df[["cpu_temp","gpu_temp"]])
        st.line_chart(df[["current","power"]])

        rul = get_rul(df)

        if rul:
            df_plot = df.copy()
            df_plot["RUL"] = rul
            st.line_chart(df_plot["RUL"])

# =========================
# TAB 3 — TABLE
# =========================
with tab3:

    df = st.session_state.data.tail(300)
    st.dataframe(df)