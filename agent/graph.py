from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import (
    orchestrator_node,
    fetch_customers_node,
    score_customers_node,
    recommend_products_node,
    generate_messages_node
)

load_dotenv()


# ─── Router ───────────────────────────────────────────────────────────────────
def router(state: AgentState) -> str:
    """
    Reads next_action from state and returns which node to run next.
    """
    return state.get("next_action", "done")


# ─── Build Graph ──────────────────────────────────────────────────────────────
def build_graph():
    graph = StateGraph(AgentState)

    # Register all nodes
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("fetch_customers", fetch_customers_node)
    graph.add_node("score_customers", score_customers_node)
    graph.add_node("recommend_products", recommend_products_node)
    graph.add_node("generate_messages", generate_messages_node)

    # Entry point
    graph.set_entry_point("orchestrator")

    # Conditional routing from orchestrator
    graph.add_conditional_edges("orchestrator", router, {
        "fetch_customers":    "fetch_customers",
        "score_customers":    "score_customers",
        "recommend_products": "recommend_products",
        "generate_messages":  "generate_messages",
        "done":               END
    })

    # After each tool node — return to orchestrator
    graph.add_edge("fetch_customers",    "orchestrator")
    graph.add_edge("score_customers",    "orchestrator")
    graph.add_edge("recommend_products", "orchestrator")
    graph.add_edge("generate_messages",  END)

    return graph.compile()


# ─── Run Agent ────────────────────────────────────────────────────────────────
agent = build_graph()


def run_agent(query: str) -> str:
    print(f"\n🤖 Agent started for query: '{query}'\n")

    result = agent.invoke({
        "user_query": query,
        "messages": [],
        "customers": [],
        "scored_customers": [],
        "customers_with_products": [],
        "outreach_messages": [],
        "next_action": None,
        "final_response": None
    })

    return result["final_response"]