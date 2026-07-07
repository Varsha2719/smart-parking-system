import streamlit as st
import mysql.connector
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import time

st.set_page_config(page_title="Smart Parking System", layout="wide", page_icon="🅿️")

RATES = {"Car": 10, "Bike": 5}  # ₹ per hour
OVERSTAY_HOURS = 5  # alert if parked more than this

# ---------------- STYLING ----------------
st.markdown("""
<style>
.main { background-color: #0e1117; }
.big-title {
    font-size: 42px; font-weight: 800;
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.slot-card {
    border-radius: 14px; padding: 14px; text-align: center;
    font-weight: 700; color: white; margin-bottom: 10px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
.available { background: linear-gradient(135deg, #11998e, #38ef7d); }
.occupied { background: linear-gradient(135deg, #ee0979, #ff6a00); }
.reserved { background: linear-gradient(135deg, #654ea3, #eaafc8); }
</style>
""", unsafe_allow_html=True)

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="varsha09",   
        database="parking_system"
    )

st.markdown('<p class="big-title">🅿️ Smart Parking Management System</p>', unsafe_allow_html=True)

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT * FROM slots ORDER BY slot_number")
slots = cursor.fetchall()

total_slots = len(slots)
occupied = sum(1 for s in slots if s[1] == 'Occupied')
reserved = sum(1 for s in slots if s[1] == 'Reserved')
available = total_slots - occupied - reserved

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Slots", total_slots)
col2.metric("🟢 Available", available)
col3.metric("🔴 Occupied", occupied)
col4.metric("🟣 Reserved", reserved)

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["🚦 Live Status", "🚗 Entry / Exit", "🔍 Search Vehicle", "📜 History & Revenue", "⚠️ Overstay Alerts"]
)

# ---------------- TAB 1: LIVE STATUS ----------------
with tab1:
    st.subheader("Live Slot Status")
    cols = st.columns(6)
    for i, slot in enumerate(slots):
        slot_number, status, vehicle_number, entry_time = slot[0], slot[1], slot[2], slot[3]
        css_class = "available" if status == "Available" else ("reserved" if status == "Reserved" else "occupied")
        emoji = "🟢" if status == "Available" else ("🟣" if status == "Reserved" else "🔴")
        with cols[i % 6]:
            st.markdown(f"""
            <div class="slot-card {css_class}">
                {emoji} Slot {slot_number}<br><span style="font-size:13px;">{status}</span>
            </div>
            """, unsafe_allow_html=True)

    if st.button("🔄 Refresh Now"):
        st.rerun()

# ---------------- TAB 2: ENTRY / EXIT ----------------
with tab2:
    st.subheader("🚗 Vehicle Entry")
    available_slots = [s[0] for s in slots if s[1] == "Available"]
    with st.form("entry_form"):
        slot_choice = st.selectbox("Select Slot", available_slots if available_slots else ["No slots available"])
        vehicle_type = st.selectbox("Vehicle Type", ["Car", "Bike"])
        vehicle_number = st.text_input("Vehicle Number")
        submitted = st.form_submit_button("Park Vehicle")

        if submitted and available_slots and vehicle_number:
            # Duplicate check
            cursor.execute("SELECT slot_number FROM slots WHERE vehicle_number=%s AND status='Occupied'", (vehicle_number,))
            dup = cursor.fetchone()
            if dup:
                st.error(f"This vehicle is already parked in Slot {dup[0]}!")
            else:
                now = datetime.now()
                cursor.execute(
                    "UPDATE slots SET status='Occupied', vehicle_number=%s, entry_time=%s, vehicle_type=%s WHERE slot_number=%s",
                    (vehicle_number, now, vehicle_type, slot_choice)
                )
                conn.commit()
                st.success(f"{vehicle_type} {vehicle_number} parked in Slot {slot_choice}")
                st.rerun()

    st.subheader("🚙 Vehicle Exit (with Billing)")
    occupied_slots = [s[0] for s in slots if s[1] == "Occupied"]
    with st.form("exit_form"):
        exit_slot = st.selectbox("Select Slot to Vacate", occupied_slots if occupied_slots else ["No occupied slots"])
        exit_submitted = st.form_submit_button("Remove Vehicle")

        if exit_submitted and occupied_slots:
            cursor.execute("SELECT vehicle_number, entry_time, vehicle_type FROM slots WHERE slot_number=%s", (exit_slot,))
            vehicle_number, entry_time, vehicle_type = cursor.fetchone()

            exit_time = datetime.now()
            duration_hours = max((exit_time - entry_time).total_seconds() / 3600, 0.01)
            rate = RATES.get(vehicle_type, 10)
            amount = round(duration_hours * rate, 2)

            cursor.execute(
                "INSERT INTO parking_history (slot_number, vehicle_number, entry_time, exit_time, amount, vehicle_type) VALUES (%s,%s,%s,%s,%s,%s)",
                (exit_slot, vehicle_number, entry_time, exit_time, amount, vehicle_type)
            )
            cursor.execute(
                "UPDATE slots SET status='Available', vehicle_number=NULL, entry_time=NULL, vehicle_type=NULL WHERE slot_number=%s",
                (exit_slot,)
            )
            conn.commit()

            st.success(f"✅ {vehicle_type} {vehicle_number} removed from Slot {exit_slot}")
            st.info(f"🧾 Receipt — Duration: {round(duration_hours,2)} hrs | Rate: ₹{rate}/hr | **Total: ₹{amount}**")
            st.rerun()

# ---------------- TAB 3: SEARCH VEHICLE ----------------
with tab3:
    st.subheader("🔍 Search Vehicle by Number")
    search_number = st.text_input("Enter Vehicle Number to Search")
    if search_number:
        cursor.execute("SELECT slot_number, status, entry_time, vehicle_type FROM slots WHERE vehicle_number=%s", (search_number,))
        result = cursor.fetchone()
        if result:
            st.success(f"🚘 {result[3]} **{search_number}** is currently in **Slot {result[0]}** (Parked at {result[2]})")
        else:
            st.warning("Not currently parked. Checking history...")
            cursor.execute(
                "SELECT slot_number, entry_time, exit_time, amount FROM parking_history WHERE vehicle_number=%s ORDER BY exit_time DESC LIMIT 1",
                (search_number,)
            )
            hist = cursor.fetchone()
            if hist:
                st.info(f"Last seen in Slot {hist[0]}, from {hist[1]} to {hist[2]}, Amount paid: ₹{hist[3]}")
            else:
                st.error("No record found for this vehicle.")

# ---------------- TAB 4: HISTORY & REVENUE ----------------
with tab4:
    st.subheader("📜 Parking History")
    cursor.execute("SELECT slot_number, vehicle_number, vehicle_type, entry_time, exit_time, amount FROM parking_history ORDER BY exit_time DESC")
    history = cursor.fetchall()

    if history:
        df = pd.DataFrame(history, columns=["Slot", "Vehicle Number", "Type", "Entry Time", "Exit Time", "Amount (₹)"])
        st.dataframe(df, use_container_width=True)

        total_revenue = df["Amount (₹)"].sum()
        st.metric("💰 Total Revenue Collected", f"₹{total_revenue:.2f}")

        st.subheader("📊 Revenue by Day")
        df["Date"] = pd.to_datetime(df["Exit Time"]).dt.date
        daily_revenue = df.groupby("Date")["Amount (₹)"].sum().reset_index()
        fig1 = px.bar(daily_revenue, x="Date", y="Amount (₹)", color="Amount (₹)", color_continuous_scale="Tealgrn")
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("⏰ Peak Hours (Entries by Hour)")
        df["Hour"] = pd.to_datetime(df["Entry Time"]).dt.hour
        hourly = df.groupby("Hour").size().reset_index(name="Entries")
        fig2 = px.line(hourly, x="Hour", y="Entries", markers=True)
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("🅿️ Most Used Slots")
        slot_usage = df.groupby("Slot").size().reset_index(name="Times Used").sort_values("Times Used", ascending=False)
        fig3 = px.bar(slot_usage, x="Slot", y="Times Used", color="Times Used", color_continuous_scale="Sunset")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No history yet. Park and remove a vehicle to see records here.")

# ---------------- TAB 5: OVERSTAY ALERTS ----------------
with tab5:
    st.subheader("⚠️ Vehicles Parked Too Long")
    now = datetime.now()
    overstays = []
    for s in slots:
        slot_number, status, vehicle_number, entry_time = s[0], s[1], s[2], s[3]
        if status == "Occupied" and entry_time:
            hours_parked = (now - entry_time).total_seconds() / 3600
            if hours_parked > OVERSTAY_HOURS:
                overstays.append((slot_number, vehicle_number, round(hours_parked, 2)))

    if overstays:
        for slot_number, vehicle_number, hours in overstays:
            st.error(f"🚨 Slot {slot_number} — {vehicle_number} parked for {hours} hours (limit: {OVERSTAY_HOURS} hrs)")
    else:
        st.success("No overstaying vehicles right now. ✅")

cursor.close()
conn.close()