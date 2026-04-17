import streamlit as st
import pandas as pd
import requests

# 🔴 Your deployed Flask (Vercel)
API_URL = "https://digi-flask.vercel.app/api"

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
# API CALL
# =========================
def get_rul_series(df):

    if len(df) < 50:
        return None

    df_clean = df.fillna(0)

    try:
        response = requests.post(
            f"{API_URL}/predict",
            json=df_clean.to_dict(orient="records"),
            timeout=30
        )

        return response.json()["rul_series"]

    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4 = st.tabs(["RUL", "Graphs", "Table", "Input"])

# =========================
# TAB 4 — INPUT
# =========================
with tab4:

    st.subheader("Upload CSV")
    file = st.file_uploader("Upload CSV", type=["csv"])

    if file is not None:
        df = pd.read_csv(file)
        st.success("CSV Loaded ✅")
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
# TAB 1 — RUL
# =========================
with tab1:

    df = st.session_state.data
    rul_series = get_rul_series(df)

    if rul_series is None:
        st.warning("Need at least 50 rows")
    else:
        valid = [r for r in rul_series if r is not None]

        if len(valid) == 0:
            st.warning("Waiting for enough data...")
        else:
            latest = valid[-1]

            st.metric("RUL (Years)", f"{latest['years']:.2f}")
            st.metric("RUL (Hours)", f"{latest['hours']:.0f}")

# =========================
# TAB 2 — GRAPHS
# =========================
with tab2:

    df = st.session_state.data.tail(300)

    if not df.empty:

        st.subheader("Fan Speed")
        st.line_chart(df[["fan1","fan2"]])

        st.subheader("Temperature")
        st.line_chart(df[["cpu_temp","gpu_temp","nvidia_temp"]])

        st.subheader("Electrical")
        st.line_chart(df[["current","power"]])

        rul_series = get_rul_series(df)

        if rul_series:
            df_plot = df.copy()
            df_plot["RUL_years"] = [
                r["years"] if r else None for r in rul_series[-len(df):]
            ]

            st.subheader("RUL Over Time")
            st.line_chart(df_plot["RUL_years"])

# =========================
# TAB 3 — TABLE
# =========================
with tab3:
    st.dataframe(st.session_state.data.tail(300))
