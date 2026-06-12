CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    age INTEGER,
    occupation TEXT,
    monthly_income REAL,
    credit_score INTEGER,
    existing_loans INTEGER DEFAULT 0,
    account_balance REAL,
    account_type TEXT,
    city TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    type TEXT,
    amount REAL,
    category TEXT,
    description TEXT,
    date TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS product_interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    product TEXT,
    interest_level TEXT,
    last_enquiry_date TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);