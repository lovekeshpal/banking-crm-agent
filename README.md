# 🏦 Banking CRM Agent — Agentic AI for Relationship Managers

An agentic AI system that helps Relationship Managers (RMs) identify high-potential customers and generate personalized WhatsApp outreach messages — powered by LangGraph, OpenAI, and FastAPI.

---

## 🎯 Problem Statement

A Relationship Manager asks:

> "Find high-value customers likely to convert for a personal loan this month and generate personalized WhatsApp messages."

This system autonomously:

1. Retrieves relevant customer and transaction data
2. Scores and ranks customers by loan conversion likelihood
3. Recommends the right product per customer profile
4. Generates personalized WhatsApp messages for each high-value customer

---

## 🏗 Architecture

```
RM (Angular UI)
      ↓  HTTP POST /chat
FastAPI Backend
      ↓
LangGraph Agent
      ↓
┌─────────────────────────────────────┐
│           Orchestrator Node          │
│  LLM reads state → decides next      │
│  tool to call via conditional edge   │
└────────────────┬────────────────────┘
                 ↓ (conditional routing)
    ┌────────────┬────────────┬────────────┐
    ↓            ↓            ↓            ↓
fetch_        score_      recommend_   generate_
customers    customers    products     messages
    ↓            ↓            ↓            ↓
SQLite DB    Scoring      Product      OpenAI
             Engine       Rules        GPT-4o-mini
    └────────────┴────────────┴────────────┘
                 ↓
         Final Response
                 ↓
        Angular Chat UI
```

---

## 🔄 Execution Flow

1. RM types a natural language query in the Angular chat UI
2. Angular sends HTTP POST to FastAPI `/chat` endpoint
3. FastAPI creates/retrieves a session and invokes the LangGraph agent
4. **Orchestrator node** — LLM reads the query and current state, sets `next_action`
5. **Router** — conditional edge reads `next_action`, routes to correct node
6. **fetch_customers node** — calls `get_customers` tool, queries SQLite, writes to state
7. **Orchestrator** — sees customers in state, sets `next_action = score_customers`
8. **score_customers node** — scores all customers 0-100, filters high/medium tier
9. **Orchestrator** — sees scores, sets `next_action = recommend_products`
10. **recommend_products node** — assigns right product per customer profile
11. **Orchestrator** — sets `next_action = generate_messages`
12. **generate_messages node** — calls OpenAI for each customer, generates personalized WhatsApp message
13. Final structured response returned to Angular UI

---

## 🛠 Tool Design

| Tool | File | Purpose | Called By |
|---|---|---|---|
| `get_customers` | `tools/customer_tools.py` | Fetch customers from SQLite with filters | fetch_customers node |
| `get_customer_transactions` | `tools/customer_tools.py` | Fetch transaction history per customer | Available for deep analysis |
| `score_customers` | `tools/scoring_tools.py` | Score 0-100 by conversion likelihood | score_customers node |
| `recommend_product` | `tools/scoring_tools.py` | Recommend right product per profile | recommend_products node |
| `generate_whatsapp_message` | `tools/message_tools.py` | Generate personalized WhatsApp message via LLM | generate_messages node |

### Scoring Engine — How it works

Each customer is scored out of 100 across 5 signals:

| Signal | Max Points | Logic |
|---|---|---|
| Credit Score | 30 | 800+ = 30pts, 750+ = 25pts, 700+ = 18pts |
| Monthly Income | 25 | 1.5L+ = 25pts, 80k+ = 20pts, 50k+ = 14pts |
| Account Balance | 20 | 5L+ = 20pts, 2L+ = 15pts, 1L+ = 10pts |
| Existing Loans | 15 | 0 loans = 15pts, 1 = 10pts, 2 = 5pts |
| Product Interest | 10 | High interest = 10pts, Medium = 5pts |

Tier classification:

- **High** — score ≥ 60
- **Medium** — score ≥ 35
- **Low** — score < 35

---

## 🧠 Key Design Decisions

### 1. LangGraph over plain LangChain

Plain LangChain agents are a black box — you can't inspect state mid-run, add conditional logic cleanly, or extend the flow without rewriting. LangGraph makes the agent's reasoning explicit as a state graph — every node, every edge, every routing decision is visible and modifiable independently.

### 2. Separate tools from nodes

Tools are pure functions that do one job (hit the DB, score a list, call OpenAI). Nodes are the orchestration layer that decide when to call which tool. This separation means you can swap the scoring logic without touching the agent wiring, and vice versa.

### 3. SQLite for mock data

SQLite requires zero setup — no credentials, no cloud dependency, no network. Any evaluator can clone and run in under 2 minutes. In production this would be PostgreSQL on Neon or AWS RDS.

### 4. Session management in FastAPI

Each conversation gets a `session_id`. State is preserved across messages so the RM can ask follow-up questions in the same context. This makes the system truly conversation-based as required.

### 5. GPT-4o-mini for message generation

Fast, cost-effective, and more than capable for structured outreach message generation. GPT-4o would produce marginally better messages at 10x the cost — not justified for this use case.

---

## ⚖️ Trade-offs and Limitations

| Decision | Trade-off |
|---|---|
| SQLite | Simple setup but not production-scale. Would use PostgreSQL for real deployment |
| Rule-based scoring | Explainable and fast but less accurate than an ML model trained on historical conversion data |
| In-memory sessions | Fast but sessions lost on server restart. Would use Redis for production |
| No Vector DB | Semantic search not implemented. Would add Chroma/Pinecone for similarity-based customer discovery |
| GPT-4o-mini | Cost-efficient but GPT-4o would produce more nuanced messages |
| Top 5 customers only | Messages generated for top 5 to manage API costs. Configurable via code |

---

## 🚀 Setup and Run Instructions

### Prerequisites

- Python 3.11+
- Node.js 22+
- Angular CLI
- OpenAI API Key

### 1. Clone the repository

```bash
git clone https://github.com/lovekeshpal/banking-crm-agent.git
cd banking-crm-agent
```

### 2. Set up Python environment

```bash
python3.11 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Add your OpenAI API key to .env
OPENAI_API_KEY=your_key_here
```

### 4. Set up the database

```bash
python3.11 db/seed.py
```

### 5. Start the FastAPI backend

```bash
uvicorn api.main:app --reload --port 8000
```

### 6. Start the Angular frontend

```bash
cd frontend/crm-agent-ui
npm install
ng serve
```

### 7. Open the app

```
http://localhost:4200
```

---

## 💬 Example Queries

```
Find high-value customers likely to convert for a personal loan this month
```

```
Find customers in Delhi with high credit scores for loan outreach
```

```
Which customers are good candidates for a credit card?
```

---

## 🗂 Project Structure

```
banking-crm-agent/
├── agent/
│   ├── state.py          ← AgentState TypedDict
│   ├── nodes.py          ← All node functions
│   └── graph.py          ← LangGraph wiring + router
├── tools/
│   ├── customer_tools.py ← get_customers, get_transactions
│   ├── scoring_tools.py  ← score_customers, recommend_product
│   └── message_tools.py  ← generate_whatsapp_message
├── db/
│   ├── schema.sql        ← Table definitions
│   └── seed.py           ← Mock data generator
├── api/
│   └── main.py           ← FastAPI app + session management
├── frontend/
│   └── crm-agent-ui/     ← Angular chat UI
├── .env.example          ← Environment variable template
├── requirements.txt      ← Python dependencies
└── README.md
```

---

## 🔮 Future Improvements

- **PostgreSQL + Neon** — production-grade database
- **Chroma Vector DB** — semantic similarity search for customer discovery
- **Redis sessions** — persistent conversation memory across restarts
- **ML scoring model** — trained on historical conversion data, more accurate than rules
- **GPT-4o upgrade** — more nuanced, higher quality message generation
- **Multi-language messages** — Hindi, Tamil, Bengali outreach
- **WhatsApp Business API integration** — send messages directly from the UI
- **Analytics dashboard** — track outreach performance and conversion rates

---

## 👨‍💻 Built By

Lovekesh Pal — Full Stack AI Engineer

[lovekeshpal.com](https://lovekeshpal.com) | [@specsycoder](https://x.com/specsycoder)
