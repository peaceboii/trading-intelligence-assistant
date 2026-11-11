import streamlit as st
import requests
import time

st.set_page_config(page_title="Trading Intelligence Dossier", layout="wide")

st.title("⚡ Trading Intelligence Assistant")
st.caption("Multi-Worker LangGraph Supervisor Engine")

# --- Sidebar Inputs ---
st.sidebar.header("Account & Execution Setup")
api_base_url = st.sidebar.text_input("FastAPI Base URL", value="http://127.0.0.1:8000")

symbol = st.sidebar.text_input("Asset Ticker / Pair", value="GBPJPY").upper().strip()
account_balance = st.sidebar.number_input("Account Balance ($)", min_value=100.0, value=10000.0, step=500.0)

# Intelligent default based on pair
is_jpy = symbol.endswith("JPY")
is_forex = len(symbol) == 6 and symbol.isalpha()
default_stop = 25.0 if is_forex else 2.50
help_text = "Enter stop distance in Pips for Forex (e.g. 25.0), or Dollars for Stocks (e.g. 2.50)."

stop_distance = st.sidebar.number_input("Stop Loss Distance", min_value=0.1, value=default_stop, step=1.0 if is_forex else 0.1, help=help_text)

# Target R:R Preference
target_rr = st.sidebar.select_slider("Target R:R Strategy", options=["1:1.5", "1:2.0", "1:2.5", "1:3.0"], value="1:2.0")

submit_btn = st.sidebar.button("Run Intelligence Workflow", type="primary", use_container_width=True)

# --- Workflow Execution & Polling ---
if submit_btn:
    payload = {
        "symbol": symbol,
        "query": None,
        "account_balance": account_balance,
        "stop_distance": stop_distance
    }

    try:
        with st.spinner("Submitting task to supervisor..."):
            post_res = requests.post(f"{api_base_url}/tasks/analyze", json=payload, timeout=5)

        if post_res.status_code != 202:
            st.error(f"Failed to create task: {post_res.text}")
            st.stop()

        task_id = post_res.json()["task_id"]
        poll_placeholder = st.empty()
        status = "PENDING"
        max_retries = 40
        attempt = 0

        while status.upper() in ["PENDING", "RUNNING", "RUNING"] and attempt < max_retries:
            time.sleep(2)
            attempt += 1

            get_res = requests.get(f"{api_base_url}/task/{task_id}", timeout=5)
            if get_res.status_code == 200:
                task_status_data = get_res.json()
                status = task_status_data.get("status", "FAILED")
                poll_placeholder.markdown(f"**Agent Status:** `{status}` (Auditing risk parameters & gathering news...)")
                if status.upper() == "COMPLETED":
                    break
            else:
                st.error("Failed to fetch task status.")
                st.stop()

        poll_placeholder.empty()

        if status.upper() == "COMPLETED":
            st.session_state["latest_dossier"] = task_status_data.get("result")
            st.session_state["task_symbol"] = symbol
            st.session_state["account_balance"] = account_balance
            st.session_state["target_rr"] = target_rr
            st.success("Workflow completed successfully!")
        else:
            st.error(f"Task ended with status: {status}. Error: {task_status_data.get('error')}")

    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to FastAPI server at `{api_base_url}`. Is Uvicorn running?")

# --- Display KPIs & Dossier ---
if "latest_dossier" in st.session_state and st.session_state["latest_dossier"]:
    dossier_text = st.session_state["latest_dossier"]
    active_sym = st.session_state.get("task_symbol", "ASSET")
    bal = st.session_state.get("account_balance", 10000.0)
    rr_choice = st.session_state.get("target_rr", "1:2.0")

    st.divider()

    # Dynamic KPI Cards
    risk_val = bal * 0.02
    rr_multiplier = float(rr_choice.split(":")[1])
    target_profit = risk_val * rr_multiplier

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Instrument", active_sym)
    with col2:
        bias = "BEARISH" if "BEARISH" in dossier_text else ("BULLISH" if "BULLISH" in dossier_text else "NEUTRAL")
        st.metric("Macro Bias", bias)
    with col3:
        st.metric("Risk Envelope (2%)", f"${risk_val:.2f}")
    with col4:
        st.metric(f"Suggested Target ({rr_choice})", f"+${target_profit:.2f}")

    tab_report, tab_raw = st.tabs(["📋 Formatted Dossier", "🔍 Raw Markdown"])
    with tab_report:
        st.markdown(dossier_text)
    with tab_raw:
        st.code(dossier_text, language="markdown")