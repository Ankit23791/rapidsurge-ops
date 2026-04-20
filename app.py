import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import io

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RapidSurge Ops Tracker",
    page_icon="💊",
    layout="wide"
)

# ── USERS ────────────────────────────────────────────────────────────────────
# To add/remove users: just edit this list
# Format: "username": {"password": "...", "name": "...", "role": "admin"/"user"}
USERS = {
    "ankit":   {"password": "ritika237", "name": "Ankit",          "role": "admin"},
    "user1":   {"password": "pass101",   "name": "Rahul Sharma",   "role": "user"},
    "user2":   {"password": "pass102",   "name": "Priya Singh",    "role": "user"},
    "user3":   {"password": "pass103",   "name": "Amit Kumar",     "role": "user"},
    "user4":   {"password": "pass104",   "name": "Sunita Devi",    "role": "user"},
    "user5":   {"password": "pass105",   "name": "Raju Verma",     "role": "user"},
    "user6":   {"password": "pass106",   "name": "Pooja Gupta",    "role": "user"},
    "user7":   {"password": "pass107",   "name": "Vikas Yadav",    "role": "user"},
    "user8":   {"password": "pass108",   "name": "Neha Patel",     "role": "user"},
    "user9":   {"password": "pass109",   "name": "Suresh Tiwari",  "role": "user"},
    "user10":  {"password": "pass110",   "name": "Kavita Mishra",  "role": "user"},
}

DATA_FILE = "ops_data.csv"

TEAM_COLORS = {
    "Purchase":       "#1D9E75",
    "Stock Check":    "#185FA5",
    "Bill Upload":    "#BA7517",
    "Placement":      "#993556",
    "Telecaller":     "#533AB7",
    "Delivery":       "#3B6D11",
}

# ── DATA HELPERS ─────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

def save_row(row: dict):
    df = load_data()
    new_row = pd.DataFrame([row])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def to_excel(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="All Entries")
        for team in df["Team"].unique() if "Team" in df.columns else []:
            df[df["Team"] == team].to_excel(writer, index=False, sheet_name=team[:31])
    return buf.getvalue()

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.name = ""
    st.session_state.role = ""

# ── LOGIN PAGE ────────────────────────────────────────────────────────────────
def show_login():
    st.markdown("""
    <style>
    .login-box {
        max-width: 400px;
        margin: 80px auto;
        padding: 2rem;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        background: white;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 💊 RapidSurge Ops")
        st.markdown("#### Daily Operations Tracker")
        st.divider()

        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if st.button("Login →", use_container_width=True, type="primary"):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.name = USERS[username]["name"]
                st.session_state.role = USERS[username]["role"]
                st.rerun()
            else:
                st.error("Wrong username or password. Please try again.")

        st.caption("Contact Ankit if you forgot your password.")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
def show_sidebar():
    with st.sidebar:
        st.markdown(f"### 👋 Hello, {st.session_state.name}!")
        if st.session_state.role == "admin":
            st.success("👑 Admin Access")
        st.divider()
        st.markdown(f"📅 **{date.today().strftime('%d %B %Y')}**")
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.name = ""
            st.session_state.role = ""
            st.rerun()

# ── SUBMIT HELPER ─────────────────────────────────────────────────────────────
def submit_entry(team, fields: dict):
    row = {
        "Date": date.today().strftime("%Y-%m-%d"),
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Team": team,
        "Person": st.session_state.name,
        **fields
    }
    save_row(row)
    st.success(f"✅ {team} entry submitted successfully!")
    st.balloons()

# ── FORMS ─────────────────────────────────────────────────────────────────────
def form_purchase():
    st.subheader("🛒 Purchase Team Log")
    with st.form("form_purchase", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            distributor = st.text_input("Distributor Name *")
            amount = st.number_input("Bill Amount (₹)", min_value=0.0, step=100.0)
            bill_no = st.text_input("Bill Number")
        with col2:
            payment = st.selectbox("Payment Mode", ["Cash", "Credit", "UPI", "Cheque"])
            status = st.selectbox("Status", ["Completed", "Pending", "Partial"])
        items = st.text_area("Items Purchased *", placeholder="List the items...")
        remarks = st.text_input("Remarks", placeholder="Any notes...")
        submitted = st.form_submit_button("Submit Entry", type="primary", use_container_width=True)
        if submitted:
            if not distributor or not items:
                st.error("Please fill Distributor Name and Items.")
            else:
                submit_entry("Purchase", {
                    "Distributor": distributor,
                    "Items": items,
                    "Amount (₹)": amount,
                    "Payment Mode": payment,
                    "Bill No": bill_no,
                    "Status": status,
                    "Remarks": remarks,
                })

def form_stockcheck():
    st.subheader("📦 Stock Check Log")
    with st.form("form_stockcheck", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("Location / Rack No. *", placeholder="e.g. Rack A3")
            status = st.selectbox("Stock Status", ["All Good", "Short Stock", "Critical"])
        with col2:
            expiry_found = st.selectbox("Expiry Items Found?", ["No", "Yes"])
            expiry_items = st.text_input("Expiry Item Names (if any)")
        items = st.text_area("Items Checked", placeholder="List items checked...")
        short_items = st.text_input("Short Stock Items", placeholder="Items running low...")
        remarks = st.text_input("Remarks")
        submitted = st.form_submit_button("Submit Entry", type="primary", use_container_width=True)
        if submitted:
            if not location:
                st.error("Please fill Location / Rack No.")
            else:
                submit_entry("Stock Check", {
                    "Location": location,
                    "Items Checked": items,
                    "Short Stock Items": short_items,
                    "Expiry Found": expiry_found,
                    "Expiry Items": expiry_items,
                    "Status": status,
                    "Remarks": remarks,
                })

def form_billupload():
    st.subheader("🧾 Bill Upload Log")
    with st.form("form_billupload", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            distributor = st.text_input("Distributor Name *")
            bill_no = st.text_input("Bill Number *")
            bill_date = st.date_input("Bill Date")
        with col2:
            amount = st.number_input("Bill Amount (₹)", min_value=0.0, step=100.0)
            num_items = st.number_input("Number of Items", min_value=0, step=1)
            category = st.selectbox("Category", ["", "Tablets", "Syrup", "Injection", "Surgical", "Other"])
        status = st.selectbox("Upload Status", ["Uploaded", "Pending", "Failed"])
        remarks = st.text_input("Remarks")
        submitted = st.form_submit_button("Submit Entry", type="primary", use_container_width=True)
        if submitted:
            if not distributor or not bill_no:
                st.error("Please fill Distributor Name and Bill Number.")
            else:
                submit_entry("Bill Upload", {
                    "Distributor": distributor,
                    "Bill No": bill_no,
                    "Bill Date": str(bill_date),
                    "Amount (₹)": amount,
                    "No of Items": num_items,
                    "Category": category,
                    "Upload Status": status,
                    "Remarks": remarks,
                })

def form_placement():
    st.subheader("📍 Stock Placement Log")
    with st.form("form_placement", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            item = st.text_input("Item Name *", placeholder="Medicine / item")
            quantity = st.number_input("Quantity", min_value=0, step=1)
            location = st.text_input("Location / Rack No. *", placeholder="e.g. Rack B2")
        with col2:
            placed_by = st.text_input("Placed By")
            verified_by = st.text_input("Verified By")
            distributor = st.text_input("Distributor")
        status = st.selectbox("Status", ["Placed", "Pending", "Partial"])
        remarks = st.text_input("Remarks")
        submitted = st.form_submit_button("Submit Entry", type="primary", use_container_width=True)
        if submitted:
            if not item or not location:
                st.error("Please fill Item Name and Location.")
            else:
                submit_entry("Placement", {
                    "Item": item,
                    "Quantity": quantity,
                    "Location": location,
                    "Placed By": placed_by,
                    "Verified By": verified_by,
                    "Distributor": distributor,
                    "Status": status,
                    "Remarks": remarks,
                })

def form_telecaller():
    st.subheader("📞 Telecaller Log")
    with st.form("form_telecaller", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            calls = st.number_input("Calls Made", min_value=0, step=1)
            orders = st.number_input("Orders Received", min_value=0, step=1)
            order_value = st.number_input("Order Value (₹)", min_value=0.0, step=100.0)
        with col2:
            customer = st.text_input("Customer Name")
            address = st.text_input("Delivery Address")
            priority = st.selectbox("Priority", ["Normal", "Urgent", "Low"])
        items = st.text_area("Items Ordered", placeholder="List items ordered...")
        status = st.selectbox("Status", ["Confirmed", "Pending", "Cancelled"])
        remarks = st.text_input("Remarks")
        submitted = st.form_submit_button("Submit Entry", type="primary", use_container_width=True)
        if submitted:
            submit_entry("Telecaller", {
                "Calls Made": calls,
                "Orders Received": orders,
                "Order Value (₹)": order_value,
                "Customer": customer,
                "Items Ordered": items,
                "Delivery Address": address,
                "Priority": priority,
                "Status": status,
                "Remarks": remarks,
            })

def form_delivery():
    st.subheader("🚚 Delivery / Porter Log")
    with st.form("form_delivery", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            mode = st.selectbox("Mode", ["Own Delivery", "Porter", "Other"])
            pickup = st.text_input("Pickup Location *", placeholder="From where")
            destination = st.text_input("Destination *", placeholder="Warehouse / Customer")
        with col2:
            quantity = st.number_input("Quantity", min_value=0, step=1)
            cost = st.number_input("Cost (₹)", min_value=0.0, step=10.0)
            status = st.selectbox("Status", ["Delivered", "In Transit", "Pending", "Failed"])
        items = st.text_area("Items Carried", placeholder="List items...")
        col3, col4 = st.columns(2)
        with col3:
            dep_time = st.time_input("Departure Time")
        with col4:
            arr_time = st.time_input("Arrival Time")
        remarks = st.text_input("Remarks")
        submitted = st.form_submit_button("Submit Entry", type="primary", use_container_width=True)
        if submitted:
            if not pickup or not destination:
                st.error("Please fill Pickup Location and Destination.")
            else:
                submit_entry("Delivery", {
                    "Mode": mode,
                    "Pickup": pickup,
                    "Destination": destination,
                    "Items": items,
                    "Quantity": quantity,
                    "Departure": str(dep_time),
                    "Arrival": str(arr_time),
                    "Cost (₹)": cost,
                    "Status": status,
                    "Remarks": remarks,
                })

# ── USER PAGE ─────────────────────────────────────────────────────────────────
def show_user_page():
    st.title(f"💊 RapidSurge Ops Tracker")
    st.caption(f"Logged in as: **{st.session_state.name}**  |  {date.today().strftime('%A, %d %B %Y')}")
    st.divider()

    tabs = st.tabs(["🛒 Purchase", "📦 Stock Check", "🧾 Bill Upload", "📍 Placement", "📞 Telecaller", "🚚 Delivery"])
    with tabs[0]: form_purchase()
    with tabs[1]: form_stockcheck()
    with tabs[2]: form_billupload()
    with tabs[3]: form_placement()
    with tabs[4]: form_telecaller()
    with tabs[5]: form_delivery()

    st.divider()
    st.subheader("📋 My Entries Today")
    df = load_data()
    if not df.empty and "Person" in df.columns:
        today_str = date.today().strftime("%Y-%m-%d")
        my_today = df[(df["Person"] == st.session_state.name) & (df["Date"] == today_str)]
        if my_today.empty:
            st.info("You have no entries today yet.")
        else:
            st.dataframe(my_today[["Time", "Team", "Status"] if "Status" in my_today.columns else ["Time", "Team"]], use_container_width=True)
    else:
        st.info("No entries yet today.")

# ── ADMIN DASHBOARD ───────────────────────────────────────────────────────────
def show_admin_page():
    st.title("👑 Admin Dashboard — RapidSurge Ops")
    st.caption(f"Welcome, **{st.session_state.name}**  |  {date.today().strftime('%A, %d %B %Y')}")
    st.divider()

    df = load_data()

    if df.empty:
        st.warning("No data yet. Team members need to start submitting entries.")
        return

    df["Date"] = pd.to_datetime(df["Date"])
    today_str = date.today().strftime("%Y-%m-%d")
    today_df = df[df["Date"] == pd.to_datetime(today_str)]

    # ── TODAY'S STATS ─────────────────────────────────────────────────────────
    st.subheader("📊 Today's Summary")
    teams = ["Purchase", "Stock Check", "Bill Upload", "Placement", "Telecaller", "Delivery"]
    cols = st.columns(6)
    for i, team in enumerate(teams):
        count = len(today_df[today_df["Team"] == team]) if not today_df.empty else 0
        with cols[i]:
            st.metric(team, count, "entries")

    st.divider()

    # ── CHARTS ────────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Entries by Team (Today)")
        if not today_df.empty:
            team_counts = today_df["Team"].value_counts().reset_index()
            team_counts.columns = ["Team", "Count"]
            st.bar_chart(team_counts.set_index("Team"))
        else:
            st.info("No entries today yet.")

    with col2:
        st.subheader("👤 Entries by Person (Today)")
        if not today_df.empty:
            person_counts = today_df["Person"].value_counts().reset_index()
            person_counts.columns = ["Person", "Count"]
            st.bar_chart(person_counts.set_index("Person"))
        else:
            st.info("No entries today yet.")

    st.divider()

    # ── FILTERS ───────────────────────────────────────────────────────────────
    st.subheader("🔍 Filter & View All Entries")
    col1, col2, col3 = st.columns(3)

    with col1:
        all_teams = ["All"] + sorted(df["Team"].unique().tolist())
        selected_team = st.selectbox("Filter by Team", all_teams)

    with col2:
        all_persons = ["All"] + sorted(df["Person"].unique().tolist()) if "Person" in df.columns else ["All"]
        selected_person = st.selectbox("Filter by Person", all_persons)

    with col3:
        date_filter = st.selectbox("Filter by Date", ["Today", "Last 7 Days", "Last 30 Days", "All Time"])

    filtered = df.copy()
    if selected_team != "All":
        filtered = filtered[filtered["Team"] == selected_team]
    if selected_person != "All":
        filtered = filtered[filtered["Person"] == selected_person]
    if date_filter == "Today":
        filtered = filtered[filtered["Date"] == pd.to_datetime(today_str)]
    elif date_filter == "Last 7 Days":
        filtered = filtered[filtered["Date"] >= pd.Timestamp.now() - pd.Timedelta(days=7)]
    elif date_filter == "Last 30 Days":
        filtered = filtered[filtered["Date"] >= pd.Timestamp.now() - pd.Timedelta(days=30)]

    st.markdown(f"**{len(filtered)} entries found**")
    st.dataframe(filtered.sort_values("Date", ascending=False), use_container_width=True)

    st.divider()

    # ── DOWNLOAD ──────────────────────────────────────────────────────────────
    st.subheader("📥 Download Reports")
    col1, col2 = st.columns(2)
    with col1:
        excel_data = to_excel(filtered)
        st.download_button(
            label="⬇️ Download Filtered Data (Excel)",
            data=excel_data,
            file_name=f"rapidsurge_ops_{today_str}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with col2:
        csv_data = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Filtered Data (CSV)",
            data=csv_data,
            file_name=f"rapidsurge_ops_{today_str}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.divider()

    # ── MANAGE USERS ──────────────────────────────────────────────────────────
    st.subheader("👥 Team Members")
    user_data = [{"Username": u, "Name": v["name"], "Role": v["role"]} for u, v in USERS.items()]
    st.dataframe(pd.DataFrame(user_data), use_container_width=True)
    st.caption("To add/change users, edit the USERS section at the top of app.py")

    # ── ADMIN CAN ALSO SUBMIT FORMS ───────────────────────────────────────────
    st.divider()
    st.subheader("📝 Submit Entry (as Admin)")
    tabs = st.tabs(["🛒 Purchase", "📦 Stock Check", "🧾 Bill Upload", "📍 Placement", "📞 Telecaller", "🚚 Delivery"])
    with tabs[0]: form_purchase()
    with tabs[1]: form_stockcheck()
    with tabs[2]: form_billupload()
    with tabs[3]: form_placement()
    with tabs[4]: form_telecaller()
    with tabs[5]: form_delivery()

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        show_login()
    else:
        show_sidebar()
        if st.session_state.role == "admin":
            show_admin_page()
        else:
            show_user_page()

if __name__ == "__main__":
    main()
