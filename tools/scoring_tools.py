from langchain_core.tools import tool


def calculate_score(customer: dict) -> dict:
    """
    Internal scoring logic — not exposed as a tool directly.
    Scores a customer 0-100 based on loan conversion likelihood.
    """
    score = 0
    reasons = []

    # Credit score (max 30 points)
    credit = customer.get("credit_score", 0)
    if credit >= 800:
        score += 30
        reasons.append("Excellent credit score")
    elif credit >= 750:
        score += 25
        reasons.append("Very good credit score")
    elif credit >= 700:
        score += 18
        reasons.append("Good credit score")
    elif credit >= 650:
        score += 10
        reasons.append("Average credit score")
    else:
        score += 0
        reasons.append("Poor credit score")

    # Monthly income (max 25 points)
    income = customer.get("monthly_income", 0)
    if income >= 150000:
        score += 25
        reasons.append("Very high income")
    elif income >= 80000:
        score += 20
        reasons.append("High income")
    elif income >= 50000:
        score += 14
        reasons.append("Moderate income")
    elif income >= 25000:
        score += 7
        reasons.append("Low income")
    else:
        score += 0
        reasons.append("Insufficient income")

    # Account balance (max 20 points)
    balance = customer.get("account_balance", 0)
    if balance >= 500000:
        score += 20
        reasons.append("High account balance")
    elif balance >= 200000:
        score += 15
        reasons.append("Good account balance")
    elif balance >= 100000:
        score += 10
        reasons.append("Moderate account balance")
    elif balance >= 50000:
        score += 5
        reasons.append("Low account balance")
    else:
        score += 0
        reasons.append("Very low balance")

    # Existing loans (max 15 points — fewer is better)
    existing_loans = customer.get("existing_loans", 0)
    if existing_loans == 0:
        score += 15
        reasons.append("No existing loans")
    elif existing_loans == 1:
        score += 10
        reasons.append("One existing loan")
    elif existing_loans == 2:
        score += 5
        reasons.append("Two existing loans")
    else:
        score += 0
        reasons.append("Too many existing loans")

    # Product interest signal (max 10 points)
    interest = customer.get("interest_level", None)
    if interest == "high":
        score += 10
        reasons.append("Has shown high interest in product")
    elif interest == "medium":
        score += 5
        reasons.append("Has shown medium interest in product")

    return {
        **customer,
        "conversion_score": score,
        "score_reasons": reasons,
        "tier": "high" if score >= 60 else "medium" if score >= 35 else "low"
    }


@tool
def score_customers(customers: list) -> list:
    """
    Scores and ranks a list of customers by their likelihood to convert
    for a personal loan. Use this AFTER get_customers.
    Returns customers sorted by conversion_score descending,
    with a tier label: high, medium, or low.
    """
    scored = [calculate_score(c) for c in customers]
    scored.sort(key=lambda x: x["conversion_score"], reverse=True)
    return scored


@tool
def recommend_product(customer: dict) -> dict:
    """
    Recommends the most suitable banking product for a single customer
    based on their profile. Use this after scoring to personalize
    the product recommendation before generating outreach messages.
    Returns the customer profile with a recommended_product field added.
    """
    income = customer.get("monthly_income", 0)
    credit = customer.get("credit_score", 0)
    balance = customer.get("account_balance", 0)
    existing_loans = customer.get("existing_loans", 0)
    interested_product = customer.get("interested_product", None)

    # If customer already showed interest — respect that signal
    if interested_product == "personal_loan" and credit >= 700:
        product = "Personal Loan"
        reason = "Customer has shown interest and meets eligibility"

    elif credit >= 780 and income >= 80000 and existing_loans == 0:
        product = "Premium Personal Loan"
        reason = "Excellent profile — eligible for premium rate loan"

    elif credit >= 700 and income >= 50000 and existing_loans <= 1:
        product = "Personal Loan"
        reason = "Good profile — strong loan candidate"

    elif balance >= 300000 and existing_loans == 0:
        product = "Fixed Deposit"
        reason = "High balance with no loans — ideal for FD investment"

    elif credit >= 720 and income >= 40000:
        product = "Credit Card"
        reason = "Stable income and good credit — suitable for credit card"

    else:
        product = "Savings Plan"
        reason = "Build financial profile before loan eligibility"

    return {
        **customer,
        "recommended_product": product,
        "recommendation_reason": reason
    }