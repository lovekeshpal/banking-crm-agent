import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from agent.state import AgentState
from tools.customer_tools import get_customers, get_customer_transactions
from tools.scoring_tools import score_customers, recommend_product
from tools.message_tools import generate_whatsapp_message

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ─── System prompt the LLM always sees ───────────────────────────────────────
SYSTEM_PROMPT = """
You are an intelligent Relationship Manager assistant for a bank.
Your job is to help RMs identify high-value customers and generate
personalized outreach messages.

You have access to these tools:
- get_customers: fetch customers from database with filters
- get_customer_transactions: fetch transaction history for a customer
- score_customers: score and rank customers by loan conversion likelihood
- recommend_product: recommend the right product for a customer
- generate_whatsapp_message: generate personalized WhatsApp message

Always follow this sequence:
1. Fetch customers using get_customers
2. Score them using score_customers
3. Recommend products using recommend_product for top customers
4. Generate messages using generate_whatsapp_message for each

Be concise, data-driven, and focus on high and medium tier customers only.
"""


# ─── Node 1: Orchestrator ─────────────────────────────────────────────────────
def orchestrator_node(state: AgentState) -> dict:
    """
    The brain of the agent. LLM reads the current state
    and decides what to do next.
    """
    messages = state.get("messages", [])

    # First call — add system prompt + user query
    if not messages:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=state["user_query"])
        ]

    response = llm.invoke(messages)

    # Determine next action based on current state
    if not state.get("customers"):
        next_action = "fetch_customers"
    elif not state.get("scored_customers"):
        next_action = "score_customers"
    elif not state.get("customers_with_products"):
        next_action = "recommend_products"
    elif not state.get("outreach_messages"):
        next_action = "generate_messages"
    else:
        next_action = "done"

    return {
        "messages": messages + [response],
        "next_action": next_action
    }


# ─── Node 2: Fetch Customers ──────────────────────────────────────────────────
def fetch_customers_node(state: AgentState) -> dict:
    """
    Calls get_customers tool and writes results to state.
    """
    print("🔍 Fetching customers from database...")

    customers = get_customers.invoke({
        "min_income": 0,
        "min_credit_score": 0,
        "limit": 20
    })

    print(f"   Found {len(customers)} customers")

    return {"customers": customers}


# ─── Node 3: Score Customers ──────────────────────────────────────────────────
def score_customers_node(state: AgentState) -> dict:
    """
    Calls score_customers tool on the fetched customers.
    Filters to only high and medium tier.
    """
    print("📊 Scoring customers...")

    scored = score_customers.invoke({
        "customers": state["customers"]
    })

    # Keep only high and medium tier
    filtered = [c for c in scored if c["tier"] in ["high", "medium"]]

    print(f"   {len(filtered)} high/medium tier customers identified")

    return {"scored_customers": filtered}


# ─── Node 4: Recommend Products ───────────────────────────────────────────────
def recommend_products_node(state: AgentState) -> dict:
    """
    Calls recommend_product for each scored customer.
    """
    print("🎯 Recommending products...")

    customers_with_products = []
    for customer in state["scored_customers"]:
        result = recommend_product.invoke({"customer": customer})
        customers_with_products.append(result)

    print(f"   Products recommended for {len(customers_with_products)} customers")

    return {"customers_with_products": customers_with_products}


# ─── Node 5: Generate Messages ────────────────────────────────────────────────
def generate_messages_node(state: AgentState) -> dict:
    """
    Calls generate_whatsapp_message for each customer.
    Builds the final response summary.
    """
    print("✉️  Generating personalized WhatsApp messages...")

    outreach_messages = []

    # Only generate for top 5 to save API calls
    top_customers = state["customers_with_products"][:5]

    for customer in top_customers:
        result = generate_whatsapp_message.invoke({"customer": customer})
        outreach_messages.append(result)
        print(f"   ✅ Message generated for {customer['name']}")

    # Build final response
    final_response = build_final_response(outreach_messages)

    return {
        "outreach_messages": outreach_messages,
        "final_response": final_response
    }


# ─── Helper: Build Final Response ────────────────────────────────────────────
def build_final_response(customers: list) -> str:
    lines = []
    lines.append(f"✅ Found {len(customers)} high-potential customers for personal loan outreach.\n")

    for i, c in enumerate(customers, 1):
        lines.append(f"{'─'*50}")
        lines.append(f"👤 {i}. {c['name']}")
        lines.append(f"   Occupation  : {c['occupation']}")
        lines.append(f"   Income      : ₹{c['monthly_income']:,.0f}/month")
        lines.append(f"   Credit Score: {c['credit_score']}")
        lines.append(f"   Score       : {c['conversion_score']}/100 ({c['tier'].upper()} tier)")
        lines.append(f"   Product     : {c['recommended_product']}")
        lines.append(f"   Reason      : {c['recommendation_reason']}")
        lines.append(f"\n   📱 WhatsApp Message:")
        lines.append(f"   {c['whatsapp_message']}\n")

    return "\n".join(lines)