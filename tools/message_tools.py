from dotenv import load_dotenv
load_dotenv()

import os
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


@tool
def generate_whatsapp_message(customer: dict) -> dict:
    """
    Generates a personalized WhatsApp outreach message for a single customer
    based on their profile, recommended product, and financial details.
    Use this AFTER recommend_product for each high or medium tier customer.
    Returns the customer profile with a whatsapp_message field added.
    """
    name = customer.get("name", "Customer")
    product = customer.get("recommended_product", "Personal Loan")
    income = customer.get("monthly_income", 0)
    credit = customer.get("credit_score", 0)
    occupation = customer.get("occupation", "")
    reason = customer.get("recommendation_reason", "")
    score = customer.get("conversion_score", 0)

    prompt = f"""
You are a professional Relationship Manager at a bank.
Write a short, warm, personalized WhatsApp message to a customer.

Customer details:
- Name: {name}
- Occupation: {occupation}
- Monthly Income: ₹{income:,.0f}
- Credit Score: {credit}
- Recommended Product: {product}
- Why they are a good fit: {reason}

Rules:
- Keep it under 100 words
- Sound human, warm, not salesy
- Mention their name
- Mention the product naturally
- End with a call to action
- Use Indian context (₹, Indian names feel)
- Do NOT use emojis excessively — max 1
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    return {
        **customer,
        "whatsapp_message": response.content
    }