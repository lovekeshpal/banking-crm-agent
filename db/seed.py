import sqlite3
import random
from datetime import datetime, timedelta
import os

# Build the database in the db/ folder
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = get_connection()
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("✅ Tables created")

def seed_customers():
    customers = [
        # High value — strong loan candidates
        ("Rajesh Kumar",    "rajesh@email.com",  "9810001001", 35, "Software Engineer",   95000,  780, 0, 450000,  "savings",  "Delhi"),
        ("Priya Sharma",    "priya@email.com",   "9810001002", 29, "Doctor",             120000,  810, 1, 620000,  "current",  "Mumbai"),
        ("Amit Verma",      "amit@email.com",    "9810001003", 42, "Business Owner",     200000,  750, 0, 980000,  "current",  "Noida"),
        ("Sneha Patel",     "sneha@email.com",   "9810001004", 31, "CA",                  85000,  790, 0, 380000,  "savings",  "Ahmedabad"),
        ("Vikram Singh",    "vikram@email.com",  "9810001005", 38, "Marketing Manager",   75000,  760, 1, 290000,  "savings",  "Gurgaon"),

        # Borderline — agent needs to reason carefully
        ("Neha Gupta",      "neha@email.com",    "9810001006", 27, "Teacher",             35000,  680, 1, 95000,   "savings",  "Delhi"),
        ("Rohit Jain",      "rohit@email.com",   "9810001007", 33, "Freelancer",          55000,  710, 2, 120000,  "savings",  "Pune"),
        ("Kavya Reddy",     "kavya@email.com",   "9810001008", 26, "HR Executive",        40000,  695, 0, 85000,   "savings",  "Hyderabad"),
        ("Arjun Nair",      "arjun@email.com",   "9810001009", 45, "Shop Owner",          60000,  670, 3, 150000,  "current",  "Chennai"),
        ("Pooja Mishra",    "pooja@email.com",   "9810001010", 30, "Nurse",               38000,  700, 1, 110000,  "savings",  "Lucknow"),

        # Low value — agent should filter out
        ("Suresh Yadav",    "suresh@email.com",  "9810001011", 52, "Daily Wage Worker",   12000,  580, 4, 8000,    "savings",  "Delhi"),
        ("Meena Kumari",    "meena@email.com",   "9810001012", 48, "Housewife",            8000,  540, 2, 15000,   "savings",  "Bihar"),
        ("Ravi Shankar",    "ravi@email.com",    "9810001013", 55, "Retired",             18000,  560, 3, 22000,   "savings",  "Varanasi"),
        ("Deepa Thomas",    "deepa@email.com",   "9810001014", 23, "Student",              5000,  600, 0, 12000,   "savings",  "Kochi"),
        ("Manoj Tiwari",    "manoj@email.com",   "9810001015", 41, "Unemployed",              0,  510, 5, 3000,    "savings",  "Kanpur"),
    ]

    with get_connection() as conn:
        conn.executemany("""
            INSERT INTO customers 
            (name, email, phone, age, occupation, monthly_income, 
             credit_score, existing_loans, account_balance, account_type, city)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, customers)
    print(f"✅ {len(customers)} customers seeded")

def seed_transactions():
    transaction_templates = {
        # customer_id: [(type, amount, category, description), ...]
        1:  [("credit", 95000, "salary", "Monthly salary"),
             ("debit",  15000, "emi", "Home loan EMI"),
             ("debit",  8000,  "shopping", "Online shopping"),
             ("credit", 5000,  "investment", "FD interest")],

        2:  [("credit", 120000, "salary", "Monthly salary"),
             ("debit",   25000, "emi", "Car loan EMI"),
             ("debit",   12000, "shopping", "Medical supplies"),
             ("credit",  8000,  "investment", "Mutual fund returns")],

        3:  [("credit", 200000, "salary", "Business revenue"),
             ("debit",   45000, "emi", "Office rent"),
             ("credit",  15000, "investment", "Stock dividends"),
             ("debit",   20000, "shopping", "Business expenses")],

        4:  [("credit", 85000, "salary", "Monthly salary"),
             ("debit",  10000, "emi", "Vehicle loan EMI"),
             ("debit",   5000, "shopping", "Groceries"),
             ("credit",  3000, "investment", "RD interest")],

        5:  [("credit", 75000, "salary", "Monthly salary"),
             ("debit",  18000, "emi", "Personal loan EMI"),
             ("debit",   7000, "shopping", "Online purchases"),
             ("credit",  2000, "investment", "Savings interest")],

        6:  [("credit", 35000, "salary", "Monthly salary"),
             ("debit",   8000, "emi", "Education loan EMI"),
             ("debit",   5000, "shopping", "Daily expenses")],

        7:  [("credit", 55000, "salary", "Freelance income"),
             ("debit",  12000, "emi", "Two wheeler EMI"),
             ("debit",   8000, "shopping", "Miscellaneous")],

        8:  [("credit", 40000, "salary", "Monthly salary"),
             ("debit",   6000, "shopping", "Shopping"),
             ("debit",   4000, "emi", "Mobile EMI")],

        9:  [("credit", 60000, "salary", "Shop income"),
             ("debit",  20000, "emi", "Multiple EMIs"),
             ("debit",  15000, "shopping", "Stock purchase")],

        10: [("credit", 38000, "salary", "Monthly salary"),
             ("debit",   7000, "emi", "Bike loan EMI"),
             ("debit",   5000, "shopping", "Household expenses")],

        11: [("credit", 12000, "salary", "Daily wages"),
             ("debit",   8000, "shopping", "Basic necessities")],

        12: [("credit",  8000, "salary", "Household income"),
             ("debit",   6000, "shopping", "Daily expenses")],

        13: [("credit", 18000, "salary", "Pension"),
             ("debit",  10000, "emi", "Old loan EMI"),
             ("debit",   5000, "shopping", "Medical expenses")],

        14: [("credit",  5000, "salary", "Part time income"),
             ("debit",   3000, "shopping", "College expenses")],

        15: [("credit",  3000, "salary", "Odd jobs"),
             ("debit",   2500, "shopping", "Basic needs")],
    }

    rows = []
    base_date = datetime.now()

    for customer_id, txns in transaction_templates.items():
        for i, (txn_type, amount, category, description) in enumerate(txns):
            date = base_date - timedelta(days=random.randint(1, 30))
            rows.append((
                customer_id,
                txn_type,
                amount,
                category,
                description,
                date.strftime("%Y-%m-%d")
            ))

    with get_connection() as conn:
        conn.executemany("""
            INSERT INTO transactions
            (customer_id, type, amount, category, description, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, rows)
    print(f"✅ {len(rows)} transactions seeded")

def seed_product_interests():
    interests = [
        (1,  "personal_loan",  "high",   "2026-05-15"),
        (2,  "personal_loan",  "medium", "2026-05-20"),
        (3,  "personal_loan",  "high",   "2026-06-01"),
        (4,  "credit_card",    "high",   "2026-05-10"),
        (5,  "personal_loan",  "medium", "2026-05-25"),
        (6,  "personal_loan",  "low",    "2026-04-10"),
        (7,  "credit_card",    "medium", "2026-05-01"),
        (8,  "mutual_fund",    "low",    "2026-03-15"),
        (9,  "personal_loan",  "low",    "2026-04-20"),
        (10, "personal_loan",  "medium", "2026-05-18"),
    ]

    with get_connection() as conn:
        conn.executemany("""
            INSERT INTO product_interests
            (customer_id, product, interest_level, last_enquiry_date)
            VALUES (?, ?, ?, ?)
        """, interests)
    print(f"✅ {len(interests)} product interests seeded")

if __name__ == "__main__":
    create_tables()
    seed_customers()
    seed_transactions()
    seed_product_interests()
    print("\n🎉 Database ready at db/database.db")