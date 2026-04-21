
import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import io
from supabase import create_client, Client

st.set_page_config(page_title="RapidSurge Ops Tracker", page_icon="💊", layout="wide")

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://nckatdryvhzvuegisdxb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_tGAKyEZwiINmFgO_KgcIhw_fssQ9f0a")
SUPABASE_SECRET = os.getenv("SUPABASE_SECRET", "sb_secret_HxDfyL-VNDQFGAa3jii43w_IJgyN3nN")

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_SECRET)

supabase = init_supabase()

USERS = {
    "ankit":      {"password": "ritika237", "name": "Ankit",      "role": "admin"},
    "rahul":      {"password": "rahul123",  "name": "Rahul",      "role": "user"},
    "dharmendra": {"password": "dhar123",   "name": "Dharmendra", "role": "user"},
    "anshul":     {"password": "ansh123",   "name": "Anshul",     "role": "user"},
    "Ritik":     {"password": "ritik123",   "name": "Ritik",     "role": "user"},
    "Naresh":     {"password": "naresh123",   "name": "Naresh",     "role": "user"},
    "Sandeep":     {"password": "sandeep123",   "name": "Sandeep",     "role": "user"},
     "Pooja":     {"password": "pooja123",   "name": "Pooja",     "role": "user"},
}

DISTRIBUTORS = [
    "Acorns Health Solutions Private Limited","Admire Enterprises",
    "Amar Drugs Distributors (a Unit Of Chhabra Healthcare Solutions Pvt Ltd)",
    "Amarjeet Medical Hall","Ankit Enterprises","Ar Kay Medicos Private Limited",
    "Bawa Medical Store","Bhakti Enterprises","D. C. Agencies Private Limited",
    "Digipharms","Evara Life Sciences Llp","Goel Medical Agencies","Guru Ji Medicos",
    "Harikul Pharma","Health And Wellness Pharmacy","Hindustan Pharma",
    "J B G Distributors","Jayanti Medical Agency Llp","Krishna Medical Agencies",
    "M/s  Jai Medical Agency","M/s  Shri Hari Pharma","M/s Bawa Medical Agencies",
    "M/s Medi Science","M/s Mediways Vaccine Company","M/s Premier Medical Agency",
    "M/s Satyam Medicos","M/s Sehgal Pharma","M/s Star Pharma","M/s Stupa Enterprises",
    "M/s Tirupati Distributors","M/s Universal Medical Agency",
    "Maypri Healthcare Private Limited","Mediways Agencies","Mediways Vaccine",
    "Mukesh Pharma Private Limited","Narayan Medical Agency",
    "Neelkanth Pharma Logistics Private Limited","New Brahmroop Medicare",
    "Olr Pharmacy","Om Distributors","Pawan Agencies","Pharmacype Enterprises",
    "Sastasundar Healthbuddy Limited","Satyam Distributors","Sharma Medical Agency",
    "Shivshakti Enterprises","Shree Maruti Nandan Pharmaceuticals Pvt, Ltd",
    "Shri Radhey Krishan Trading Co.","Shri Rudram Enterprises","Silvertone Networks",
    "Trisha Pharma","Vashudev Enterprises","Vijaydeep Medicose",
    "Vtc Tradewings Pvt Ltd","Xcelent Pharmaceuticals Private Limited",
]

IMG_FOLDER = "bill_images"
os.makedirs(IMG_FOLDER, exist_ok=True)

def load_data():
    try:
        response = supabase.table("ops_entries").select("*").execute()
        if response.data:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def save_row(row):
    try:
        # Convert all values to strings to avoid type issues
        clean_row = {k: str(v) if v is not None else "" for k, v in row.items()}
        supabase.table("ops_entries").insert(clean_row).execute()
    except Exception as e:
        st.error(f"Error saving data: {e}")

def to_excel(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="All")
        if "Team" in df.columns:
            for t in df["Team"].unique():
                df[df["Team"]==t].to_excel(writer, index=False, sheet_name=t[:31])
    return buf.getvalue()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.name = ""
    st.session_state.role = ""

def show_login():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("## 💊 RapidSurge Ops Tracker")
        st.markdown("#### Daily Operations Log")
        st.divider()
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True, type="primary"):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.name = USERS[username]["name"]
                st.session_state.role = USERS[username]["role"]
                st.rerun()
            else:
                st.error("Wrong username or password!")
        st.caption("Contact Ankit if you forgot your password.")

def show_sidebar():
    with st.sidebar:
        st.markdown(f"### 👋 Hello, {st.session_state.name}!")
        if st.session_state.role == "admin":
            st.success("👑 Admin")
        st.divider()
        st.markdown(f"📅 **{date.today().strftime('%d %B %Y')}**")
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            for k in ["logged_in","username","name","role"]:
                st.session_state[k] = False if k=="logged_in" else ""
            st.rerun()

def submit_entry(team, fields):
    row = {"date": date.today().strftime("%Y-%m-%d"),
           "time": datetime.now().strftime("%H:%M:%S"),
           "team": team, "person": st.session_state.name}
    row.update({k.lower().replace(" ","_").replace("(","").replace(")","").replace("/","_"): str(v) for k,v in fields.items()})
    save_row(row)
    st.success(f"✅ {team} entry saved permanently!")
    st.balloons()

def timer_button(key):
    sk = f"{key}_start"
    if sk not in st.session_state:
        st.session_state[sk] = None
    if st.session_state[sk] is None:
        st.info("👆 Click START TIMER when you begin")
        if st.button("▶️ Start Timer", key=f"btn_{key}", type="primary"):
            st.session_state[sk] = datetime.now().strftime("%H:%M:%S")
            st.rerun()
        return None
    else:
        st.success(f"⏱️ Timer started at: {st.session_state[sk]}")
        return st.session_state[sk]

def calc_duration(start_str):
    try:
        s = datetime.strptime(start_str, "%H:%M:%S")
        e = datetime.now()
        return int((e.replace(year=e.year,month=e.month,day=e.day) - s.replace(year=e.year,month=e.month,day=e.day)).total_seconds() / 60)
    except:
        return 0

def save_image(file, bill_no):
    if file is None:
        return ""
    try:
        name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{bill_no}.jpg"
        file_bytes = file.getbuffer().tobytes()
        supabase.storage.from_("bill-images").upload(
            path=name,
            file=file_bytes,
            file_options={"content-type": "image/jpeg"}
        )
        return name
    except Exception as e:
        st.error(f"Image upload error: {e}")
        return ""

def get_image(filename):
    try:
        response = supabase.storage.from_("bill-images").download(filename)
        return response
    except:
        return None

def form_purchase():
    st.subheader("🛒 Purchase Team Log")
    start = timer_button("purchase")
    if start is None:
        return
    with st.form("form_purchase", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            distributor = st.selectbox("Distributor Name *", DISTRIBUTORS, key="p_dist")
            order_type  = st.selectbox("Type of Order", ["Regular","Arrangement"], key="p_type")
        with c2:
            sku   = st.number_input("No. of SKUs", min_value=0, step=1)
            mode  = st.selectbox("Mode of Order", ["Through Call","Pharma Rack","Excel Send"], key="p_mode")
        if st.form_submit_button("Submit ✅", type="primary", use_container_width=True):
            end = datetime.now().strftime("%H:%M:%S")
            submit_entry("Purchase", {"Distributor":distributor,"Order Type":order_type,
                "No of SKUs":sku,"Mode":mode,"Start Time":start,
                "End Time":end,"Duration mins":calc_duration(start)})
            st.session_state["purchase_start"] = None

def form_stockcheck():
    st.subheader("📦 Stock Check Log")

    # Load unchecked bills from last 2 days
    try:
        from datetime import timedelta
        two_days_ago = (date.today() - timedelta(days=2)).strftime("%Y-%m-%d")
        response = supabase.table("ops_entries")\
            .select("*")\
            .eq("team", "Bill Upload")\
            .eq("check_status", "Unchecked")\
            .gte("date", two_days_ago)\
            .execute()
        pending_bills = response.data if response.data else []
    except Exception as e:
        st.error(f"Error: {e}")
        pending_bills = []

    if not pending_bills:
        st.warning("⚠️ No pending unchecked bills found in last 2 days!")
        st.info("Bill Upload team needs to upload bills first.")
        return

    bill_options = {
        f"Bill: {b.get('bill_number','N/A')} | {b.get('distributor','N/A')} | {b.get('date','N/A')}": b
        for b in pending_bills
    }

    start = timer_button("stockcheck")
    if start is None:
        return

    with st.form("form_stockcheck", clear_on_submit=True):
        selected_bill_label = st.selectbox(
            "Select Bill to Check *",
            list(bill_options.keys()),
            key="sc_bill_select"
        )
        selected_bill = bill_options[selected_bill_label]

        st.info(f"📋 Distributor: **{selected_bill.get('distributor','N/A')}** | Bill No: **{selected_bill.get('bill_number','N/A')}** | Date: **{selected_bill.get('date','N/A')}**")

        c3, c4, c5 = st.columns(3)
        with c3: sku = st.number_input("No. of SKUs", min_value=0, step=1)
        with c4: total = st.number_input("Total Medicine", min_value=0, step=1)
        with c5: near_expiry = st.number_input("Near Expiry", min_value=0, step=1)

        c6, c7 = st.columns(2)
        with c6: shortage = st.number_input("Shortage", min_value=0, step=1)
        with c7: wrong_batch = st.number_input("Wrong Batch", min_value=0, step=1)

        st.markdown("📸 **Bill Image**")
        upload_opt = st.radio("Select Option", ["Upload from Gallery", "Take Photo"],
            horizontal=True, key="sc_radio", label_visibility="collapsed")
        if upload_opt == "Upload from Gallery":
            bill_img = st.file_uploader("Select Image", type=["jpg","jpeg","png","pdf"], key="sc_upload")
        else:
            bill_img = st.camera_input("Take Photo", key="sc_cam")

        remarks = st.text_input("Remarks")

        if st.form_submit_button("Submit ✅", type="primary", use_container_width=True):
            end_time = datetime.now().strftime("%H:%M:%S")
            img_name = save_image(bill_img, selected_bill.get('bill_number','')) if bill_img else ""

            # Update SAME row instead of creating new one
            try:
                update_data = {
                    "check_status": "Checked",
                    "no_of_skus": str(sku),
                    "total_medicine": str(total),
                    "near_expiry": str(near_expiry),
                    "shortage": str(shortage),
                    "wrong_batch": str(wrong_batch),
                    "stock_check_time": datetime.now().strftime("%H:%M:%S"),
                    "stock_check_by": st.session_state.name,
                    "stock_check_duration": str(calc_duration(start)),
                    "stock_check_image": img_name,
                    "stock_check_remarks": remarks,
                }
                supabase.table("ops_entries")\
                    .update(update_data)\
                    .eq("id", selected_bill['id'])\
                    .execute()
                st.success("✅ Stock Check completed! Bill marked as Checked!")
                st.balloons()
                st.session_state["stockcheck_start"] = None
            except Exception as e:
                st.error(f"Error updating bill: {e}")

def form_billupload():
    st.subheader("🧾 Bill Upload Log")
    DELIVERY_BY = ["Porter", "Naresh", "Sandeep", "Distributor"]
    with st.form("form_billupload", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            distributor = st.selectbox("Distributor Name *", DISTRIBUTORS, key="bu_dist")
            bill_no = st.text_input("Bill Number *")
        with c2:
            bill_date = st.date_input("Bill Date")
            delivery_by = st.selectbox("Delivery By", DELIVERY_BY, key="bu_delivery")
        st.markdown("📸 **Bill Image**")
        upload_opt = st.radio("Select Option", ["Upload from Gallery", "Take Photo"], horizontal=True, key="bu_radio", label_visibility="collapsed")
        if upload_opt == "Upload from Gallery":
            bill_img = st.file_uploader("Select Bill Image", type=["jpg","jpeg","png","pdf"], key="bu_upload")
        else:
            bill_img = st.camera_input("Take Photo of Bill", key="bu_cam")
        order_type = st.selectbox("Order Type", ["Regular", "Arrangement"], key="bu_order_type")
        remarks = st.text_input("Remarks")
        if st.form_submit_button("Submit ✅", type="primary", use_container_width=True):
            if not bill_no:
                st.error("Please fill Bill Number!")
            else:
                warehouse_time = datetime.now().strftime("%H:%M:%S")
                img_name = save_image(bill_img, bill_no) if bill_img else ""
                submit_entry("Bill Upload", {
                    "Distributor": distributor,
                    "Bill Number": bill_no,
                    "Bill Date": str(bill_date),
                    "Bill Image": img_name,
                    "Warehouse Reached Time": warehouse_time,
                    "Delivery By": delivery_by,
                    "Remarks": remarks,
                })

def form_placement():
    st.subheader("📍 Stock Placement Log")

    # Load checked bills that are not yet placed
    try:
        from datetime import timedelta
        two_days_ago = (date.today() - timedelta(days=2)).strftime("%Y-%m-%d")
        response = supabase.table("ops_entries")\
            .select("*")\
            .eq("team", "Bill Upload")\
            .eq("check_status", "Checked")\
            .is_("placement_status", "null")\
            .gte("date", two_days_ago)\
            .execute()
        checked_bills = response.data if response.data else []
    except Exception as e:
        st.error(f"Error: {e}")
        checked_bills = []

    if not checked_bills:
        st.warning("⚠️ No checked bills pending for placement!")
        st.info("Stock Check team needs to check bills first.")
        return

    bill_options = {
        f"Bill: {b.get('bill_number','N/A')} | {b.get('distributor','N/A')} | {b.get('date','N/A')}": b
        for b in checked_bills
    }

    start = timer_button("placement")
    if start is None:
        return

    with st.form("form_placement", clear_on_submit=True):
        selected_bill_label = st.selectbox(
            "Select Bill for Placement *",
            list(bill_options.keys()),
            key="sp_bill_select"
        )
        selected_bill = bill_options[selected_bill_label]

        st.info(f"📋 Distributor: **{selected_bill.get('distributor','N/A')}** | Bill No: **{selected_bill.get('bill_number','N/A')}** | Date: **{selected_bill.get('date','N/A')}**")
        st.info(f"👤 Placed By: **{st.session_state.name}**")

        remarks = st.text_input("Remarks")

        if st.form_submit_button("Submit ✅", type="primary", use_container_width=True):
            end_time = datetime.now().strftime("%H:%M:%S")
            try:
                update_data = {
                    "placement_status": "Placed",
                    "placement_start_time": start,
                    "placement_end_time": end_time,
                    "placement_duration": str(calc_duration(start)),
                    "placement_by": st.session_state.name,
                    "placement_remarks": remarks,
                }
                supabase.table("ops_entries")\
                    .update(update_data)\
                    .eq("id", selected_bill['id'])\
                    .execute()
                st.success("✅ Stock Placement completed!")
                st.balloons()
                st.session_state["placement_start"] = None
            except Exception as e:
                st.error(f"Error: {e}")

def form_telecaller():
    st.subheader("📞 Telecaller Log")
    with st.form("form_telecaller", clear_on_submit=True):
        st.markdown("#### Daily Call Summary")
        c1, c2 = st.columns(2)
        with c1:
            calls_made = st.number_input("Total Calls Made", min_value=0, step=1)
            calls_picked = st.number_input("Calls Picked", min_value=0, step=1)
        with c2:
            orders_delivered = st.number_input("Orders Delivered", min_value=0, step=1)
            remarks = st.text_input("Remarks")

        c3, c4 = st.columns(2)
        with c3:
            start_time = st.time_input("Start Time")
        with c4:
            end_time = st.time_input("End Time")

        if st.form_submit_button("Submit ✅", type="primary", use_container_width=True):
            if calls_picked > calls_made:
                st.error("Calls Picked cannot be more than Calls Made!")
            else:
                calls_not_picked = calls_made - calls_picked
                st.info(f"📵 Calls Not Picked: **{calls_not_picked}**")
                submit_entry("Telecaller", {
                    "Calls Made": calls_made,
                    "Calls Picked": calls_picked,
                    "Calls Not Picked": calls_not_picked,
                    "Orders Delivered": orders_delivered,
                    "Start Time": str(start_time),
                    "End Time": str(end_time),
                    "Remarks": remarks,
                })

def form_delivery():
    st.subheader("🚚 Delivery Trip Log")

    LOCATIONS = [
        "Warehouse 1", "Warehouse 2", "Warehouse 3",
        "Acorns Health Solutions Private Limited","Admire Enterprises",
        "Amar Drugs Distributors (a Unit Of Chhabra Healthcare Solutions Pvt Ltd)",
        "Amarjeet Medical Hall","Ankit Enterprises","Ar Kay Medicos Private Limited",
        "Bawa Medical Store","Bhakti Enterprises","D. C. Agencies Private Limited",
        "Digipharms","Evara Life Sciences Llp","Goel Medical Agencies","Guru Ji Medicos",
        "Harikul Pharma","Health And Wellness Pharmacy","Hindustan Pharma",
        "J B G Distributors","Jayanti Medical Agency Llp","Krishna Medical Agencies",
        "M/s  Jai Medical Agency","M/s  Shri Hari Pharma","M/s Bawa Medical Agencies",
        "M/s Medi Science","M/s Mediways Vaccine Company","M/s Premier Medical Agency",
        "M/s Satyam Medicos","M/s Sehgal Pharma","M/s Star Pharma","M/s Stupa Enterprises",
        "M/s Tirupati Distributors","M/s Universal Medical Agency",
        "Maypri Healthcare Private Limited","Mediways Agencies","Mediways Vaccine",
        "Mukesh Pharma Private Limited","Narayan Medical Agency",
        "Neelkanth Pharma Logistics Private Limited","New Brahmroop Medicare",
        "Olr Pharmacy","Om Distributors","Pawan Agencies","Pharmacype Enterprises",
        "Sastasundar Healthbuddy Limited","Satyam Distributors","Sharma Medical Agency",
        "Shivshakti Enterprises","Shree Maruti Nandan Pharmaceuticals Pvt, Ltd",
        "Shri Radhey Krishan Trading Co.","Shri Rudram Enterprises","Silvertone Networks",
        "Trisha Pharma","Vashudev Enterprises","Vijaydeep Medicose",
        "Vtc Tradewings Pvt Ltd","Xcelent Pharmaceuticals Private Limited",
    ]

    TRIP_TYPES = [
        "Waiting for Medicine",
        "Picked and Going to Another Distributor",
        "Picked and Going to Warehouse",
        "Going to Distributor",
        "Waiting for Porter",
    ]

    # Step 1 - Select location and type then start trip
    if "delivery_trip_id" not in st.session_state:
        st.session_state.delivery_trip_id = None
    if "delivery_start" not in st.session_state:
        st.session_state.delivery_start = None

    if st.session_state.delivery_trip_id is None:
        st.info("📍 Select your current location and activity, then click Start Trip")
        with st.form("form_delivery_start", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                location_a = st.selectbox("Current Location *", LOCATIONS, key="d_loc_a")
            with c2:
                trip_type = st.selectbox("Activity Type *", TRIP_TYPES, key="d_type")

            if trip_type == "Waiting for Medicine":
                c3, c4 = st.columns(2)
                with c3:
                    no_bills = st.number_input("No of Bills", min_value=0, step=1)
                with c4:
                    no_sku = st.number_input("No of SKUs", min_value=0, step=1)
            else:
                no_bills = 0
                no_sku = 0

            location_b = st.selectbox("Going To (Location B)", ["—"] + LOCATIONS, key="d_loc_b")
            remarks = st.text_input("Remarks")

            if st.form_submit_button("▶️ Start Trip", type="primary", use_container_width=True):
                start_time = datetime.now().strftime("%I:%M %p")
                # Save to Supabase immediately
                row = {
                    "date": date.today().strftime("%Y-%m-%d"),
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "team": "Delivery",
                    "person": st.session_state.name,
                    "location_a": location_a,
                    "trip_type": trip_type,
                    "no_of_bills": str(no_bills),
                    "no_of_skus": str(no_sku),
                    "location_b": location_b,
                    "start_time": start_time,
                    "end_time": "In Progress...",
                    "duration_mins": "",
                    "remarks": remarks,
                    "status": "In Progress"
                }
                try:
                    result = supabase.table("ops_entries").insert(row).execute()
                    st.session_state.delivery_trip_id = result.data[0]['id']
                    st.session_state.delivery_start = datetime.now()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        # Trip is in progress
        elapsed = int((datetime.now() - st.session_state.delivery_start).total_seconds() / 60)
        st.success(f"⏱️ Trip in progress — {elapsed} minutes elapsed")
        st.info("Click Submit when activity is complete")

        if st.button("Submit ✅ — Complete This Activity", type="primary", use_container_width=True):
            end_time = datetime.now().strftime("%I:%M %p")
            duration = int((datetime.now() - st.session_state.delivery_start).total_seconds() / 60)
            try:
                supabase.table("ops_entries")\
                    .update({
                        "end_time": end_time,
                        "duration_mins": str(duration),
                        "status": "Completed"
                    })\
                    .eq("id", st.session_state.delivery_trip_id)\
                    .execute()
                st.session_state.delivery_trip_id = None
                st.session_state.delivery_start = None
                st.success("✅ Trip completed!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

def show_user_page():
    st.title("💊 RapidSurge Ops Tracker")
    st.caption(f"Logged in as: **{st.session_state.name}** | {date.today().strftime('%A, %d %B %Y')}")
    st.divider()
    tabs = st.tabs(["🛒 Purchase","📦 Stock Check","🧾 Bill Upload","📍 Placement","📞 Telecaller","🚚 Delivery"])
    with tabs[0]: form_purchase()
    with tabs[1]: form_stockcheck()
    with tabs[2]: form_billupload()
    with tabs[3]: form_placement()
    with tabs[4]: form_telecaller()
    with tabs[5]: form_delivery()
    st.divider()
    st.subheader("📋 My Entries Today")
    df = load_data()
    if not df.empty and "person" in df.columns:
        today_str = date.today().strftime("%Y-%m-%d")
        my_df = df[(df["person"]==st.session_state.name) & (df["date"]==today_str)]
        if not my_df.empty:
            display_cols = [c for c in my_df.columns if c != "id"]
            st.dataframe(my_df[display_cols], use_container_width=True)
        else:
            st.info("No entries today yet.")
    else:
        st.info("No entries today yet.")

def show_admin_page():
    st.title("👑 Admin Dashboard — RapidSurge Ops")
    st.caption(f"Welcome **{st.session_state.name}** | {date.today().strftime('%A, %d %B %Y')}")
    st.divider()
    df = load_data()
    if df.empty:
        st.warning("No data yet!")
        show_forms_section()
        return
    df["date"] = pd.to_datetime(df["date"])
    today_str = date.today().strftime("%Y-%m-%d")
    today_df  = df[df["date"]==pd.to_datetime(today_str)]

    st.subheader("📊 Today Summary")
    teams = ["Purchase","Stock Check","Bill Upload","Placement","Telecaller","Delivery"]
    cols  = st.columns(6)
    for i,t in enumerate(teams):
        with cols[i]:
            st.metric(t, len(today_df[today_df["team"]==t]) if not today_df.empty else 0)

    st.divider()
    c1,c2 = st.columns(2)
    with c1:
        st.subheader("📈 By Team (Today)")
        if not today_df.empty: st.bar_chart(today_df["team"].value_counts())
        else: st.info("No data today.")
    with c2:
        st.subheader("👤 By Person (Today)")
        if not today_df.empty: st.bar_chart(today_df["person"].value_counts())
        else: st.info("No data today.")

    st.divider()
    st.subheader("🔍 Filter & View All Entries")
    c1,c2,c3 = st.columns(3)
    with c1: sel_team   = st.selectbox("Team",   ["All"]+sorted(df["team"].unique().tolist()), key="f1")
    with c2: sel_person = st.selectbox("Person", ["All"]+sorted(df["person"].unique().tolist()), key="f2")
    with c3: date_f     = st.selectbox("Period", ["Today","Yesterday","Last 7 Days","Last 30 Days","All Time"], key="f3")

    filtered = df.copy()
    if sel_team   != "All": filtered = filtered[filtered["team"]==sel_team]
    if sel_person != "All": filtered = filtered[filtered["person"]==sel_person]
    if date_f=="Today":
        filtered = filtered[filtered["date"]==pd.to_datetime(today_str)]
    elif date_f=="Yesterday":
        yesterday = pd.to_datetime(today_str) - pd.Timedelta(days=1)
        filtered = filtered[filtered["date"]==yesterday]
    elif date_f=="Last 7 Days":
        filtered = filtered[filtered["date"]>=pd.Timestamp.now()-pd.Timedelta(days=7)]
    elif date_f=="Last 30 Days":
        filtered = filtered[filtered["date"]>=pd.Timestamp.now()-pd.Timedelta(days=30)]

    st.markdown(f"**{len(filtered)} entries found**")
    st.dataframe(filtered.sort_values("date",ascending=False))

    st.divider()
    st.subheader("📥 Download Reports")
    c1,c2 = st.columns(2)
    with c1:
        st.download_button("⬇️ Download Excel", to_excel(filtered),
            f"rapidsurge_{today_str}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_excel")
    with c2:
        st.download_button("⬇️ Download CSV", filtered.to_csv(index=False).encode(),
            f"rapidsurge_{today_str}.csv", "text/csv", key="dl_csv")

    st.divider()
    show_forms_section()

def show_forms_section():
    st.subheader("📝 Submit Entry")
    tabs = st.tabs(["🛒 Purchase","📦 Stock Check","🧾 Bill Upload","📍 Placement","📞 Telecaller","🚚 Delivery"])
    with tabs[0]: form_purchase()
    with tabs[1]: form_stockcheck()
    with tabs[2]: form_billupload()
    with tabs[3]: form_placement()
    with tabs[4]: form_telecaller()
    with tabs[5]: form_delivery()

def main():
    if not st.session_state.logged_in:
        show_login()
    else:
        show_sidebar()
        if st.session_state.role=="admin":
            show_admin_page()
        else:
            show_user_page()

if __name__ == "__main__":
    main()
