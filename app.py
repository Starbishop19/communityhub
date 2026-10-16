import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import os
import random

# page settings
st.set_page_config(page_title="CommunityHub | Diepsloot West", page_icon="🏘️", layout="wide")

# fix colors for both light and dark mode
st.markdown("""
<style>
    /* headings and body text follow the theme */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p {
        color: inherit !important;
    }

    /* cards get their own solid background so text is always readable */
    div[style*="background-color: white"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    div[style*="background-color: white"] h4,
    div[style*="background-color: white"] p,
    div[style*="background-color: white"] strong,
    div[style*="background-color: white"] small {
        color: #1a1a1a !important;
    }

    /* input fields keep dark text on light inputs */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)


# this function gives me a connection to the database whenever i need it
# using the same folder as the app so it works when deployed too
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "communityhub.db")

def get_db():
    os.makedirs(SCRIPT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# keeps track of if someone is logged in or not
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None


# ---------------- LOGIN AND REGISTER PAGE ----------------
def setup_tables():
    conn = get_db()

    # create all tables
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        user_type TEXT NOT NULL
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL, description TEXT, area TEXT,
        severity TEXT, alert_type TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL, description TEXT, area TEXT,
        category TEXT, status TEXT DEFAULT 'Open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL, description TEXT, type TEXT,
        category TEXT, quantity TEXT, contact TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS food_points (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, address TEXT, type TEXT,
        hours TEXT, contact TEXT, notes TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS businesses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, owner TEXT, address TEXT,
        services TEXT, category TEXT, contact TEXT, notes TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS meter_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT, reading REAL, date TEXT
    )''')
    conn.commit()

    # if there are no users yet then we add the demo stuff
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count == 0:

        # demo accounts so the judges can log in
        demos = [
            ("resident@diepsloot.demo", hashlib.sha256("demo123".encode()).hexdigest(), "Resident"),
            ("provider@diepsloot.demo", hashlib.sha256("demo123".encode()).hexdigest(), "Provider"),
            ("business@diepsloot.demo", hashlib.sha256("demo123".encode()).hexdigest(), "Business")
        ]
        conn.executemany("INSERT INTO users (email, password, user_type) VALUES (?, ?, ?)", demos)

        # sample alerts so the page is not empty
        alerts_data = [
            ("Water Outage in Block 7", "No water supply in Section B. Please store water.", "Block 7, Section B", "High", "Water Outage"),
            ("Road Closure at Taxi Rank", "Road blocked due to flooding. Use side road via Block 3.", "Taxi Rank, Section A", "High", "Road Closure"),
            ("Security Alert", "Increased burglary reports in Block 12. Be vigilant.", "Block 12, Section C", "Medium", "Security"),
            ("Eskom Load Shedding", "Transformers overloaded in Main Road area.", "Main Road, Section A", "Medium", "Power Outage"),
            ("Community Clean-Up", "Join us this Saturday near the clinic. Brooms provided.", "Community Clinic", "Low", "Event")
        ]
        conn.executemany("INSERT INTO alerts (title, description, area, severity, alert_type) VALUES (?, ?, ?, ?, ?)", alerts_data)

        # sample reports
        reports_data = [
            ("Water Leak near Clinic", "Large leak wasting water.", "Community Clinic", "Water Leak", "Open"),
            ("Broken Street Light", "Block 8 road is dark at night.", "Block 8, Section B", "Street Light", "Open"),
            ("Pothole on Main Road", "Damaging cars near taxi rank.", "Taxi Rank, Section A", "Pothole", "Open"),
            ("Trash Pileup", "Trash near spaza shop needs collection.", "Main Road, Section A", "Trash", "Open"),
            ("Broken Bus Stop", "Shelter broken in Block 5.", "Block 5, Section A", "Bus Stop", "Open"),
            ("Power Cut in Block 3", "Power out for 3 days.", "Block 3, Section A", "Power Cut", "Open")
        ]
        conn.executemany("INSERT INTO reports (title, description, area, category, status) VALUES (?, ?, ?, ?, ?)", reports_data)

        # sample sharing posts
        resources_data = [
            ("Offering: 20L Water Containers", "Available at Block 7 gate.", "Offering", "Water", "5 containers", "072-123-4567"),
            ("Requesting: Power Bank", "Need for job interview tomorrow.", "Requesting", "Power", "1", "073-456-7890"),
            ("Offering: Spare Bricks", "Free for anyone building.", "Offering", "Tools", "200 bricks", "071-234-5678"),
            ("Requesting: Lift to Sandton", "Job interview tomorrow morning. Can share costs.", "Requesting", "Transport", "1 person", "074-567-8901")
        ]
        conn.executemany("INSERT INTO resources (title, description, type, category, quantity, contact) VALUES (?, ?, ?, ?, ?, ?)", resources_data)

        # sample food points
        food_data = [
            ("Diepsloot Food Bank", "123 Main Road, Section A", "Food Bank", "Mon-Fri: 9am-3pm", "011-123-4567", "ID required. 1 bag per household."),
            ("Grace Community Church", "Block 2, Section B", "Church", "Sun: 12pm-2pm", "011-765-4321", "Free Sunday lunch for families."),
            ("Hope Community Fridge", "Block 9, Section B", "Community Fridge", "Open 24 hours", "076-111-2222", "Take what you need, leave what you can.")
        ]
        conn.executemany("INSERT INTO food_points (name, address, type, hours, contact, notes) VALUES (?, ?, ?, ?, ?, ?)", food_data)

        # sample local businesses
        business_data = [
            ("Thabo's Repairs", "Thabo Mokoena", "Block 4, Section A", "Phone, TV, Microwave repairs", "Repair", "072-987-6543", "Fair prices. Walk-ins welcome."),
            ("Lerato Solar Solutions", "Lerato Nkosi", "Main Road, Section A", "Solar panels, Battery backup", "Solar", "073-876-5432", "Free consultation."),
            ("Mpho's Grocery & Reuse", "Mpho Dlamini", "Block 6, Section B", "Groceries, Second-hand clothes", "Reuse", "074-765-4321", "Low prices. Trading accepted.")
        ]
        conn.executemany("INSERT INTO businesses (name, owner, address, services, category, contact, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", business_data)

        # fake meter readings for the last 6 months so the chart has something to show
        base_water = 5000
        base_electric = 15000
        for i in range(6):
            month = 10 - i
            base_water += random.randint(150, 200)
            base_electric += random.randint(300, 500)
            conn.execute("INSERT INTO meter_readings (type, reading, date) VALUES (?, ?, ?)", ('Water', base_water, f"2024-{month:02d}-01"))
            conn.execute("INSERT INTO meter_readings (type, reading, date) VALUES (?, ?, ?)", ('Electricity', base_electric, f"2024-{month:02d}-01"))

        conn.commit()

    # only close once at the very end
    conn.close()


def show_login():
    st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🏘️ CommunityHub</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Diepsloot West — Preparing together</p>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", type="primary"):
            if email == "" or password == "":
                st.warning("Please fill in both fields")
            else:
                hashed_pw = hashlib.sha256(password.encode()).hexdigest()
                conn = get_db()
                found = conn.execute("SELECT user_type FROM users WHERE email = ? AND password = ?", (email, hashed_pw)).fetchone()
                conn.close()

                if found:
                    st.session_state.logged_in = True
                    st.session_state.user_type = found["user_type"]
                    st.success("Logged in as " + found["user_type"] + "!")
                    st.rerun()
                else:
                    st.error("Wrong email or password")

        st.info("""
        **Demo Accounts for Judges:**
        - Resident: `resident@diepsloot.demo` / `demo123`
        - Provider: `provider@diepsloot.demo` / `demo123`
        - Business: `business@diepsloot.demo` / `demo123`
        """)

    with tab2:
        st.subheader("Register")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_pass")
        reg_type = st.selectbox("I am a...", ["Resident", "Provider", "Business"])

        if st.button("Register", type="primary"):
            if reg_email == "" or reg_password == "":
                st.warning("Please fill in both fields")
            else:
                hashed_pw = hashlib.sha256(reg_password.encode()).hexdigest()
                conn = get_db()
                try:
                    conn.execute("INSERT INTO users (email, password, user_type) VALUES (?, ?, ?)",
                                 (reg_email, hashed_pw, reg_type))
                    conn.commit()
                    st.success("Registered! Now go to the Login tab.")
                except sqlite3.IntegrityError:
                    st.error("That email is already registered")
                finally:
                    conn.close()


# ---------------- ALERTS PAGE ----------------
def show_alerts():
    st.header("🔔 Local Alerts")

    # providers can post new alerts
    if st.session_state.user_type == "Provider":
        with st.expander("+ Post a new alert"):
            title = st.text_input("Title")
            desc = st.text_area("Description")
            area = st.text_input("Area (example: Block 7, Section B)")
            sev = st.selectbox("Severity", ["Low", "Medium", "High"])
            atype = st.selectbox("Type", ["Water Outage", "Power Outage", "Security", "Flood", "Road Closure", "Event", "Other"])

            if st.button("Post Alert"):
                if title != "" and desc != "":
                    conn = get_db()
                    conn.execute("INSERT INTO alerts (title, description, area, severity, alert_type) VALUES (?, ?, ?, ?, ?)",
                                 (title, desc, area, sev, atype))
                    conn.commit()
                    conn.close()
                    st.success("Alert posted!")
                    st.rerun()
                else:
                    st.warning("Fill in the title and description")

    conn = get_db()
    alerts = conn.execute("SELECT * FROM alerts ORDER BY created_at DESC").fetchall()
    conn.close()

    for alert in alerts:
        if alert['severity'] == 'High':
            color = "#ffebee"
        elif alert['severity'] == 'Medium':
            color = "#fff3e0"
        else:
            color = "#e8f5e9"

        st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4>{alert['title']}</h4>
            <p>{alert['description']}</p>
            <span style="background-color: {color}; padding: 5px 10px; border-radius: 15px; font-size: 12px;">{alert['severity']}</span>
            <span style="background-color: #eceff1; padding: 5px 10px; border-radius: 15px; font-size: 12px;">{alert['alert_type']}</span>
            <span style="color: gray; font-size: 12px;"> 📍 {alert['area']}</span>
        </div>
        """, unsafe_allow_html=True)


# ---------------- REPORTS PAGE ----------------
def show_reports():
    st.header("📋 Service Reports")

    if st.session_state.user_type == "Resident":
        with st.expander("+ Report a problem"):
            title = st.text_input("Title")
            desc = st.text_area("Description")
            area = st.text_input("Area")
            cat = st.selectbox("Category", ["Water Leak", "Power Cut", "Pothole", "Trash", "Street Light", "Bus Stop", "Other"])

            if st.button("Submit Report"):
                if title != "" and desc != "":
                    conn = get_db()
                    conn.execute("INSERT INTO reports (title, description, area, category) VALUES (?, ?, ?, ?)",
                                 (title, desc, area, cat))
                    conn.commit()
                    conn.close()
                    st.success("Report submitted!")
                    st.rerun()
                else:
                    st.warning("Fill in the title and description")

    conn = get_db()
    reports = conn.execute("SELECT * FROM reports ORDER BY created_at DESC").fetchall()

    for report in reports:
        st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <strong>{report['title']}</strong>
            <p style="margin: 5px 0;">{report['description']}</p>
            <small>📍 {report['area']} | Category: {report['category']} | Status: {report['status']}</small>
        </div>
        """, unsafe_allow_html=True)

        # providers can change the status
        if st.session_state.user_type == "Provider":
            choice = st.selectbox("Change status", ["Open", "In Progress", "Resolved"], key=f"st_{report['id']}")
            if st.button("Update", key=f"btn_{report['id']}"):
                conn.execute("UPDATE reports SET status = ? WHERE id = ?", (choice, report['id']))
                conn.commit()
                st.success("Status updated!")
                st.rerun()

    conn.close()
        # ---------------- REPORTS PAGE ----------------
def show_reports():
    st.header("📋 Service Reports")

    if st.session_state.user_type == "Resident":
        with st.expander("+ Report a problem"):
            title = st.text_input("Title")
            desc = st.text_area("Description")
            area = st.text_input("Area")
            cat = st.selectbox("Category", ["Water Leak", "Power Cut", "Pothole", "Trash", "Street Light", "Bus Stop", "Other"])

            if st.button("Submit Report"):
                if title != "" and desc != "":
                    conn = get_db()
                    conn.execute("INSERT INTO reports (title, description, area, category) VALUES (?, ?, ?, ?)",
                                 (title, desc, area, cat))
                    conn.commit()
                    conn.close()
                    st.success("Report submitted!")
                    st.rerun()
                else:
                    st.warning("Fill in the title and description")

    conn = get_db()
    reports = conn.execute("SELECT * FROM reports ORDER BY created_at DESC").fetchall()

    for report in reports:
        st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <strong>{report['title']}</strong>
            <p style="margin: 5px 0;">{report['description']}</p>
            <small>📍 {report['area']} | Category: {report['category']} | Status: {report['status']}</small>
        </div>
        """, unsafe_allow_html=True)

        # providers can change the status
        if st.session_state.user_type == "Provider":
            choice = st.selectbox("Change status", ["Open", "In Progress", "Resolved"], key=f"st_{report['id']}")
            if st.button("Update", key=f"btn_{report['id']}"):
                conn.execute("UPDATE reports SET status = ? WHERE id = ?", (choice, report['id']))
                conn.commit()
                st.success("Status updated!")
                st.rerun()

    conn.close()


# ---------------- SHARING PAGE ----------------
def show_sharing():
    st.header("🤝 Resource Sharing")

    with st.expander("+ Post something"):
        title = st.text_input("Title")
        desc = st.text_area("Description")
        rtype = st.selectbox("Are you offering or requesting?", ["Offering", "Requesting"])
        cat = st.selectbox("Category", ["Water", "Food", "Power", "Transport", "Tools", "Other"])
        qty = st.text_input("Quantity (example: 5 containers)")
        contact = st.text_input("Contact number")

        if st.button("Post"):
            if title != "" and desc != "":
                conn = get_db()
                conn.execute("INSERT INTO resources (title, description, type, category, quantity, contact) VALUES (?, ?, ?, ?, ?, ?)",
                             (title, desc, rtype, cat, qty, contact))
                conn.commit()
                conn.close()
                st.success("Posted!")
                st.rerun()
            else:
                st.warning("Fill in the title and description")

    conn = get_db()
    resources = conn.execute("SELECT * FROM resources ORDER BY created_at DESC").fetchall()
    conn.close()

    for res in resources:
        if res['type'] == 'Offering':
            badge_color = "#e8f5e9"
        else:
            badge_color = "#e3f2fd"

        st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4>{res['title']}</h4>
            <p>{res['description']}</p>
            <span style="background-color: {badge_color}; padding: 5px 10px; border-radius: 15px; font-size: 12px;">{res['type'].upper()}</span>
            <span style="background-color: #eceff1; padding: 5px 10px; border-radius: 15px; font-size: 12px;">{res['category']}</span>
            <p style="font-size: 12px; color: gray; margin-top: 8px;">📞 {res['contact']} | Qty: {res['quantity']}</p>
        </div>
        """, unsafe_allow_html=True)


# ---------------- FOOD AND BUSINESS PAGE ----------------
def show_food_biz():
    st.header("🍞 Food Points & Local Businesses")

    tab1, tab2 = st.tabs(["Food Points", "Local Businesses"])

    with tab1:
        conn = get_db()
        food = conn.execute("SELECT * FROM food_points").fetchall()
        conn.close()

        for f in food:
            st.markdown(f"""
            <div style="background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4>{f['name']}</h4>
                <p>📍 {f['address']}</p>
                <p>🕒 {f['hours']}</p>
                <p>📞 {f['contact']}</p>
                <p style="color: gray;">{f['notes']}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        conn = get_db()
        biz = conn.execute("SELECT * FROM businesses").fetchall()
        conn.close()

        for b in biz:
            st.markdown(f"""
            <div style="background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4>{b['name']}</h4>
                <p><strong>Owner:</strong> {b['owner']}</p>
                <p>🔧 {b['services']}</p>
                <p>📍 {b['address']}</p>
                <p>📞 {b['contact']}</p>
                <p style="color: gray;">{b['notes']}</p>
            </div>
            """, unsafe_allow_html=True)


# ---------------- SAVINGS PAGE ----------------
def show_savings():
    st.header("💡 Energy & Water Savings")

    # lets residents add their own meter reading
    with st.expander("+ Log a new meter reading"):
        meter_type = st.selectbox("Meter type", ["Water", "Electricity"])
        reading = st.number_input("Current reading", min_value=0.0)
        date_val = st.date_input("Date")

        if st.button("Save Reading"):
            conn = get_db()
            conn.execute("INSERT INTO meter_readings (type, reading, date) VALUES (?, ?, ?)",
                         (meter_type, float(reading), str(date_val)))
            conn.commit()
            conn.close()
            st.success("Reading saved!")
            st.rerun()

    # getting all readings for the charts
    conn = get_db()
    rows = conn.execute("SELECT type, date, reading FROM meter_readings ORDER BY date").fetchall()
    conn.close()

    # turning database rows into something pandas can use
    data = [dict(r) for r in rows]
    df = pd.DataFrame(data)

    if not df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💧 Water Usage")
            water_df = df[df['type'] == 'Water']
            if not water_df.empty:
                st.line_chart(water_df.set_index('date')['reading'])

        with col2:
            st.subheader("⚡ Electricity Usage")
            elec_df = df[df['type'] == 'Electricity']
            if not elec_df.empty:
                st.line_chart(elec_df.set_index('date')['reading'])

    st.markdown("---")
    st.subheader("💰 Tips to save money at home")
    st.write("""
    - **Fix leaks fast:** A dripping tap wastes about 20L per day. That adds up on your bill.
    - **Store water early:** Fill containers when supply is back so you are ready for the next outage.
    - **Switch off during load shedding:** Unplug heaters and geysers so surges don't damage them.
    - **Borrow instead of buying:** Use the Sharing page to borrow tools instead of spending money.
    """)


# ---------------- MAIN APP LOGIC ----------------
# make sure tables and demo data exist before anything else runs
setup_tables()

if not st.session_state.logged_in:
    show_login()
else:
    st.title("🏘️ CommunityHub: Diepsloot West")
    st.write("Welcome, " + st.session_state.user_type + "!")

    menu = st.sidebar.radio("Go to", ["Alerts", "Reports", "Sharing", "Food & Biz", "Savings"])

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.rerun()

    if menu == "Alerts":
        show_alerts()
    elif menu == "Reports":
        show_reports()
    elif menu == "Sharing":
        show_sharing()
    elif menu == "Food & Biz":
        show_food_biz()
    elif menu == "Savings":
        show_savings()