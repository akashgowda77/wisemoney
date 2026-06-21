
import streamlit as st
import requests
import pandas as pd
import datetime
import subprocess
import sys
import time
import matplotlib.pyplot as plt

# --- Backend Auto-Start (For Streamlit Cloud) ---
# --- Backend Auto-Start (For Streamlit Cloud) ---
@st.cache_resource
def start_backend():
    # 1. Check if backend is ALREADY running (e.g. locally in terminal)
    try:
        requests.get("http://127.0.0.1:8000/")
        print("Backend is already running. Skipping auto-start.")
        return None
    except:
        pass

    # 2. If not, start Uvicorn (For Streamlit Cloud)
    print("Starting backend...")
    cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]
    process = subprocess.Popen(cmd)
    
    # Wait for server to start
    retries = 10
    while retries > 0:
        try:
            requests.get("http://127.0.0.1:8000/")
            print("Backend is running!")
            return process
        except:
            time.sleep(2)
            retries -= 1
    
    print("Backend failed to start.")
    return process

if not st.session_state.get("backend_started"):
    start_backend()
    st.session_state["backend_started"] = True

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="WiseMoney ML Tracker", page_icon="💰", layout="wide")

# --- Custom CSS for "Pro" Look ---
st.markdown("""
<style>
    .stMetric {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---

def login(email, password):
    try:
        res = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
        if res.status_code == 200:
            return True, res.json()
        return False, f"Error {res.status_code}: {res.text}"
    except Exception as e:
        return False, str(e)

def register(name, email, password):
    try:
        res = requests.post(f"{API_URL}/auth/register", json={"name": name, "email": email, "password": password})
        if res.status_code == 200:
            return True, "Success"
        try:
            msg = res.json().get("detail", "Registration failed")
        except:
            msg = f"Error {res.status_code}: {res.text[:200]}"
        return False, msg
    except Exception as e:
        return False, str(e)

def get_summary(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(f"{API_URL}/report/summary", headers=headers)
        return res.json() if res.status_code == 200 else {}
    except:
        return {}

def get_forecast(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(f"{API_URL}/report/forecast", headers=headers)
        if res.status_code == 200:
            return res.json().get("forecast", [])
        return []
    except:
        return []

def add_transaction(token, type_, amount, desc, date, wallet_id):
    headers = {"Authorization": f"Bearer {token}"}
    endpoint = "/income/" if type_ == "Income" else "/expense/"
    payload = {
        "amount": amount,
        "source" if type_ == "Income" else "category": desc,
        "date": date.isoformat(),
        "wallet_id": wallet_id
    }
    try:
        requests.post(f"{API_URL}{endpoint}", json=payload, headers=headers)
        return True
    except:
        return False

def parse_text(token, text):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.post(f"{API_URL}/nlp/parse", json={"text": text}, headers=headers)
        return res.json() if res.status_code == 200 else None
    except:
        return None

def create_wallet(token, name, balance):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        requests.post(f"{API_URL}/wallet/", json={"name": name, "balance": balance}, headers=headers)
        return True
    except:
        return False

# --- Main App Logic ---

if "token" not in st.session_state:
    st.session_state["token"] = None

if not st.session_state["token"]:
    st.title("WiseMoney Login")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            success, result = login(email, password)
            if success:
                st.session_state["token"] = result["access_token"]
                st.rerun()
            else:
                st.error(f"Login failed: {result}")

    with tab2:
        r_name = st.text_input("Name")
        r_email = st.text_input("Email", key="r_email")
        r_pass = st.text_input("Password", type="password", key="r_pass")
        if st.button("Register"):
            success, msg = register(r_name, r_email, r_pass)
            if success:
                st.success("Registration successful! Please sign in.")
                st.balloons()
            else:
                st.error(f"Registration failed: {msg}")

else:
    # Sidebar
    st.sidebar.title("WiseMoney Pro")
    if st.sidebar.button("Logout"):
        st.session_state["token"] = None
        st.rerun()
    
    page = st.sidebar.radio("Navigate", ["Dashboard", "Add Transaction", "ML Forecast"])
    
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}

    if page == "Dashboard":
        st.header("Financial Overview")
        
        # 1. AI Assistant
        with st.expander("🤖 AI Transaction Assistant (NLP)"):
            st.write("Type naturally, e.g., 'Spent 500 dollars on Pizza' or 'Received 5000 salary'")
            
            # Fetch wallets
            try:
                wallets_res = requests.get(f"{API_URL}/wallet/", headers=headers)
                wallets = wallets_res.json() if wallets_res.status_code == 200 else []
            except:
                wallets = []
            wallet_options = {w['name']: w['id'] for w in wallets}
            default_wallet_id = list(wallet_options.values())[0] if wallet_options else None

            nlp_text = st.text_input("Ask AI to add a transaction:")
            if st.button("Parse & Add"):
                parsed = parse_text(st.session_state["token"], nlp_text)
                if parsed and parsed.get("amount"):
                    st.info(f"AI Detected: {parsed['type']} of ₹{parsed['amount']} for '{parsed['category']}'")
                    if default_wallet_id:
                        add_transaction(st.session_state["token"], parsed['type'], parsed['amount'], parsed['category'], datetime.date.today(), default_wallet_id)
                        st.success("Transaction added successfully!")
                        st.rerun()
                    else:
                        st.error("No wallet found. Create one first.")
                else:
                    st.warning("Could not understand. Try 'Spent 100 on Food'.")

        # 2. Metrics
        summary = get_summary(st.session_state["token"])
        if summary:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Income", f"₹{summary.get('total_income', 0)}")
            c2.metric("Total Expense", f"₹{summary.get('total_expense', 0)}")
            c3.metric("Net Balance", f"₹{summary.get('net_balance', 0)}")
            c4.metric("Wallet Balance", f"₹{summary.get('total_wallet_balance', 0)}")
            
            st.markdown("---")
            
            # 3. Visualizations (Budget + Pie + Trend)
            col_a, col_b = st.columns(2)
            
            # A. Budget Progress
            with col_a:
                st.subheader("⚠️ Monthly Budget")
                budget = st.slider("Set Budget Limit", 1000, 100000, 20000)
                spent = summary.get('total_expense', 0)
                percent = min(spent / budget, 1.0)
                st.progress(percent)
                st.caption(f"Spent: ₹{spent} / ₹{budget}")
                if percent >= 1.0: st.error("Over Budget!")
                
                st.markdown("### 📊 Spending by Category")
                cat_data = summary.get("expense_by_category", [])
                if cat_data:
                    labels = [item['category'] for item in cat_data]
                    sizes = [item['amount'] for item in cat_data]
                    fig, ax = plt.subplots(figsize=(5, 3))
                    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                    ax.axis('equal')
                    fig.patch.set_alpha(0) # Transparent
                    st.pyplot(fig)
                else:
                    st.info("No expenses yet.")

            # B. Monthly Trend
            with col_b:
                st.subheader("📈 Monthly Trends")
                try:
                    trend_res = requests.get(f"{API_URL}/report/trend", headers=headers)
                    trend_data = trend_res.json() if trend_res.status_code == 200 else []
                except:
                    trend_data = []

                if trend_data:
                    df_trend = pd.DataFrame(trend_data)
                    st.bar_chart(df_trend.set_index("month")[["income", "expense"]])
                else:
                    st.info("Not enough data for trends.")

                # Export
                st.markdown("---")
                st.subheader("📂 Data Export")
                if st.button("Generate CSV Report"):
                    try:
                        export_res = requests.get(f"{API_URL}/report/export", headers=headers)
                        if export_res.status_code == 200:
                            df_export = pd.DataFrame(export_res.json())
                            csv = df_export.to_csv(index=False).encode('utf-8')
                            st.download_button("📥 Download CSV", csv, "wisemoney_data.csv", "text/csv")
                        else:
                            st.error("Export failed.")
                    except:
                        st.error("Server error.")

        else:
            st.info("Backend is fetching data...")
    
    elif page == "Add Transaction":
        st.header("Add New Transaction")
        try:
            wallets_res = requests.get(f"{API_URL}/wallet/", headers=headers)
            wallets = wallets_res.json() if wallets_res.status_code == 200 else []
        except:
            wallets = []
        wallet_options = {w['name']: w['id'] for w in wallets}
        
        c1, c2 = st.columns(2)
        with c1:
            t_type = st.selectbox("Type", ["Income", "Expense"])
            amount = st.number_input("Amount (₹)", min_value=1.0)
        with c2:
            desc = st.text_input("Source/Category")
            date = st.date_input("Date", datetime.date.today())
            
        w_name = st.selectbox("Wallet", list(wallet_options.keys())) if wallet_options else None
        
        if st.button("Save Transaction"):
            if w_name:
                add_transaction(st.session_state["token"], t_type, amount, desc, date, wallet_options[w_name])
                st.success("Saved!")
                st.balloons()
            else:
                st.error("Create a wallet first!")
        
        st.markdown("---")
        with st.expander("Create Wallet"):
             nw_name = st.text_input("New Wallet Name")
             nw_bal = st.number_input("Opening Balance (₹)", 0.0)
             if st.button("Create"):
                 create_wallet(st.session_state["token"], nw_name, nw_bal)
                 st.rerun()

    elif page == "ML Forecast":
        st.header("🔮 AI Spending Forecaster")
        st.write("Predicts your future daily spending based on historical regression.")
        if st.button("Run Forecast"):
            with st.spinner("Processing..."):
                f_data = get_forecast(st.session_state["token"])
            if f_data:
                df = pd.DataFrame(f_data)
                st.line_chart(df.set_index("date")["predicted_amount"])
                st.dataframe(df)
            else:
                st.warning("Need more data points for accurate prediction.")
