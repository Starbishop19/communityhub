import sqlite3
import hashlib
import random
import os 


# use the system temp folder — always writable
TEMP_DIR = os.environ.get('TEMP', '/tmp')
DB_PATH = os.path.join(TEMP_DIR, "communityhub.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


print("Setting up the database for Diepsloot West...")

# making all the tables we need
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    user_type TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    area TEXT,
    severity TEXT,
    alert_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    area TEXT,
    category TEXT,
    status TEXT DEFAULT 'Open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    type TEXT,
    category TEXT,
    quantity TEXT,
    contact TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS food_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT,
    type TEXT,
    hours TEXT,
    contact TEXT,
    notes TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    owner TEXT,
    address TEXT,
    services TEXT,
    category TEXT,
    contact TEXT,
    notes TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS meter_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    reading REAL,
    date TEXT
)
''')

# this makes sure passwords are not saved as normal text
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# making demo accounts so the judges can log in easily
print("Making demo accounts for the judges...")
demo_accounts = [
    ("resident@diepsloot.demo", "demo123", "Resident"),
    ("provider@diepsloot.demo", "demo123", "Provider"),
    ("business@diepsloot.demo", "demo123", "Business")
]

for email, password, user_type in demo_accounts:
    try:
        hashed_pw = hash_password(password)
        cursor.execute(
            "INSERT INTO users (email, password, user_type) VALUES (?, ?, ?)",
            (email, hashed_pw, user_type)
        )
        print("Created account: " + email)
    except sqlite3.IntegrityError:
        # means the account is already there so we just skip it
        pass

# adding sample data so the app is not empty when we demo it
print("Adding sample data for Diepsloot West...")

cursor.execute("SELECT COUNT(*) FROM alerts")
num_alerts = cursor.fetchone()[0]

if num_alerts == 0:

    alerts_data = [
        ("Water Outage in Block 7", "No water supply in Section B. Please store water.", "Block 7, Section B", "High", "Water Outage"),
        ("Road Closure at Taxi Rank", "Road blocked due to flooding. Use side road via Block 3.", "Taxi Rank, Section A", "High", "Road Closure"),
        ("Security Alert", "Increased burglary reports in Block 12. Be vigilant.", "Block 12, Section C", "Medium", "Security"),
        ("Eskom Load Shedding", "Transformers overloaded in Main Road area.", "Main Road, Section A", "Medium", "Power Outage"),
        ("Community Clean-Up", "Join us this Saturday near the clinic. Brooms provided.", "Community Clinic", "Low", "Event")
    ]
    cursor.executemany("INSERT INTO alerts (title, description, area, severity, alert_type) VALUES (?, ?, ?, ?, ?)", alerts_data)

    reports_data = [
        ("Water Leak near Clinic", "Large leak wasting water.", "Community Clinic", "Water Leak", "Open"),
        ("Broken Street Light", "Block 8 road is dark at night.", "Block 8, Section B", "Street Light", "Open"),
        ("Pothole on Main Road", "Damaging cars near taxi rank.", "Taxi Rank, Section A", "Pothole", "Open"),
        ("Trash Pileup", "Trash near spaza shop needs collection.", "Main Road, Section A", "Trash", "Open"),
        ("Broken Bus Stop", "Shelter broken in Block 5.", "Block 5, Section A", "Bus Stop", "Open"),
        ("Power Cut in Block 3", "Power out for 3 days.", "Block 3, Section A", "Power Cut", "Open")
    ]
    cursor.executemany("INSERT INTO reports (title, description, area, category, status) VALUES (?, ?, ?, ?, ?)", reports_data)

    resources_data = [
        ("Offering: 20L Water Containers", "Available at Block 7 gate.", "Offering", "Water", "5 containers", "072-123-4567"),
        ("Requesting: Power Bank", "Need for job interview tomorrow.", "Requesting", "Power", "1", "073-456-7890"),
        ("Offering: Spare Bricks", "Free for anyone building.", "Offering", "Tools", "200 bricks", "071-234-5678"),
        ("Requesting: Lift to Sandton", "Job interview tomorrow morning. Can share costs.", "Requesting", "Transport", "1 person", "074-567-8901")
    ]
    cursor.executemany("INSERT INTO resources (title, description, type, category, quantity, contact) VALUES (?, ?, ?, ?, ?, ?)", resources_data)

    food_data = [
        ("Diepsloot Food Bank", "123 Main Road, Section A", "Food Bank", "Mon-Fri: 9am-3pm", "011-123-4567", "ID required. 1 bag per household."),
        ("Grace Community Church", "Block 2, Section B", "Church", "Sun: 12pm-2pm", "011-765-4321", "Free Sunday lunch for families."),
        ("Hope Community Fridge", "Block 9, Section B", "Community Fridge", "Open 24 hours", "076-111-2222", "Take what you need, leave what you can.")
    ]
    cursor.executemany("INSERT INTO food_points (name, address, type, hours, contact, notes) VALUES (?, ?, ?, ?, ?, ?)", food_data)

    business_data = [
        ("Thabo's Repairs", "Thabo Mokoena", "Block 4, Section A", "Phone, TV, Microwave repairs", "Repair", "072-987-6543", "Fair prices. Walk-ins welcome."),
        ("Lerato Solar Solutions", "Lerato Nkosi", "Main Road, Section A", "Solar panels, Battery backup", "Solar", "073-876-5432", "Free consultation."),
        ("Mpho's Grocery & Reuse", "Mpho Dlamini", "Block 6, Section B", "Groceries, Second-hand clothes", "Reuse", "074-765-4321", "Low prices. Trading accepted.")
    ]
    cursor.executemany("INSERT INTO businesses (name, owner, address, services, category, contact, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", business_data)

    # fake meter readings for the last 6 months so the chart has something to show
    base_water = 5000
    base_electric = 15000
    for i in range(6):
        month = 10 - i
        water_reading = base_water + random.randint(150, 200)
        elec_reading = base_electric + random.randint(300, 500)
        cursor.execute("INSERT INTO meter_readings (type, reading, date) VALUES (?, ?, ?)", ('Water', water_reading, f"2024-{month:02d}-01"))
        cursor.execute("INSERT INTO meter_readings (type, reading, date) VALUES (?, ?, ?)", ('Electricity', elec_reading, f"2024-{month:02d}-01"))

# saving everything
conn.commit()
conn.close()

print("All done! Database ready ✅")