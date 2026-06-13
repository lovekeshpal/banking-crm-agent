from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    # The RM's original query
    user_query: str

    # Full conversation history with the LLM
    messages: List[BaseMessage]

    # Filled by get_customers tool
    customers: List[dict]

    # Filled by score_customers tool
    scored_customers: List[dict]

    # Filled by recommend_product tool
    customers_with_products: List[dict]

    # Filled by generate_whatsapp_message tool
    outreach_messages: List[dict]

    # Controls what the agent does next
    next_action: Optional[str]

    # Final response to send back to RM
    final_response: Optional[str]