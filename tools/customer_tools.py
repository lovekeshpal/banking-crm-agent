import sqlite3
import os
from langchain_core.tools import tool

DB_PATH = os.path.join(os.path.dirname(__file__), "../db/database.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


@tool
def get_customers(
    min_income: float = 0,
    min_credit_score: int = 0,
    city: str = None,
    limit: int = 20
) -> list:
    """
    Fetches customers from the database with optional filters.
    Use this tool FIRST before any scoring or messaging.
    Filters available: min_income, min_credit_score, city, limit.
    Returns a list of customer profiles.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            c.*,
            pi.product as interested_product,
            pi.interest_level,
            pi.last_enquiry_date
        FROM customers c
        LEFT JOIN product_interests pi ON c.id = pi.customer_id
        WHERE c.monthly_income >= ?
        AND c.credit_score >= ?
    """

    params = [min_income, min_credit_score]

    if city:
        query += " AND c.city = ?"
        params.append(city)

    query += " LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    customers = [dict(row) for row in rows]
    return customers


@tool
def get_customer_transactions(customer_id: int) -> list:
    """
    Fetches transaction history for a specific customer by their ID.
    Use this to understand spending behavior, salary credits, and EMI patterns.
    Helps assess loan repayment capability.
    Returns a list of transactions.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM transactions
        WHERE customer_id = ?
        ORDER BY date DESC
    """, (customer_id,))

    rows = cursor.fetchall()
    conn.close()

    transactions = [dict(row) for row in rows]
    return transactions