# Munder Difflin Multi-Agent System Project

A text-based **multi-agent system** that automates core business operations for the fictional Munder Difflin Paper Company. It is built on the [`smolagents`](https://github.com/huggingface/smolagents) framework and coordinates a small team of agents to handle incoming customer requests end to end.

## Project Context

Munder Difflin Paper Company needs a smart, modular multi-agent system to automate:

- **Inventory checks** and restocking decisions
- **Quote generation** for incoming sales inquiries
- **Order fulfillment** including supplier logistics and transactions

The system uses a maximum of **5 agents** (this implementation uses 4) and processes inputs and outputs entirely via **text-based communication**. It combines `smolagents` for orchestration with `sqlite3`/SQLAlchemy and `pandas` for data, plus LLM prompt engineering.

---

## Run Output Results

The latest end-to-end run of `run_test_scenarios()` processed all **20 requests** from
`quote_requests_sample.csv`. Key artifacts produced by the run:

- **`test_results.csv`** — per-request log (`request_id`, `request_date`, `cash_balance`,
  `inventory_value`, `response`). In the latest run, cash changed on 5 requests (all recorded
  sales), and **0 responses leaked internal errors** (no HTML, tracebacks, or 404 text).
- **`run_output.log`** — full console transcript of the run: per-request context, agent
  reasoning/tool calls, running cash and inventory, and the final financial report.
- **`reflection_report.md`** — a short write-up of the architecture rationale, evaluation
  results (with exact counts from `test_results.csv`), strengths, and future improvements.

Latest run summary: final cash **$45,413.75**, final inventory value **$4,586.25**.

---

## Architecture

Four agents, well under the 5-agent limit:

```
Orchestrator (CodeAgent)
  ├── Quoting Agent    (ToolCallingAgent)  — parse request, price items, apply bulk discounts
  ├── Inventory Agent  (ToolCallingAgent)  — check stock, restock, estimate delivery dates
  └── Ordering Agent   (ToolCallingAgent)  — record sales, cover shortfalls, confirm fulfillment
```

The orchestrator receives each customer request plus its request date, routes it through the
specialized agents, and returns a single customer-facing message. Agents never touch the database
directly — they call tool wrappers that reuse the utility functions in `project_starter.py` and add
business rules (item-name normalization, bulk discounts, affordability checks).

See `workflow_diagram.md` for the architecture and data-flow diagrams.

---

## Project Structure

```
project4/
├── project_starter.py          # Utility functions + the complete multi-agent system
├── quotes.csv                  # Historical quote data (reference for quoting)
├── quote_requests.csv          # Incoming customer requests
├── quote_requests_sample.csv   # Simulated test cases used to evaluate the system
├── requirements.txt            # Python dependencies (includes smolagents)
├── workflow_diagram.md         # Agent architecture + data-flow diagrams (Mermaid)
├── reflection_report.md        # Architecture rationale + evaluation results write-up
├── README.md                   # This file
├── .env                        # API key + config (create from template; gitignored)
├── .gitignore
├── test_results.csv            # Run output: per-request results log
├── run_output.log              # Run output: full console transcript of the latest run
└── munder_difflin.db           # SQLite database, generated on run (gitignored)
```

---

## Local Setup

### 1. Python version

`smolagents` requires **Python 3.10+**. This project was built and tested with Python 3.12.

### 2. Create a virtual environment and install dependencies

```bash
python3.12 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Create your `.env` file

Add your OpenAI-compatible API key (replace the placeholder):

```
UDACITY_OPENAI_API_KEY=your_openai_key_here
OPENAI_BASE_URL=https://openai.vocareum.com/v1
MODEL_ID=gpt-4o-mini
```

This project uses a custom OpenAI-compatible proxy hosted at `https://openai.vocareum.com/v1`.
`OPENAI_BASE_URL` and `MODEL_ID` are optional and default to the values above.

---

## How to Run

```bash
python project_starter.py
```

This calls `run_test_scenarios()`, which:

1. Initializes the SQLite database (`init_database(db_engine)`).
2. Loads and sorts the sample requests from `quote_requests_sample.csv`.
3. Sends each request (with its date) through the multi-agent system.
4. Coordinates inventory checks, quote generation, and order processing.

Output includes:

- Per-request agent responses
- Running cash and inventory updates
- A final financial report
- A `test_results.csv` file logging `request_id`, `request_date`, `cash_balance`, `inventory_value`, and `response` for every request

---

## Tips for Success

- Item names are normalized to the **exact database names** before any transaction, avoiding failures.
- Every quote includes applicable **bulk discounts** (10% for large orders, 5% for medium) and can draw on past quote data.
- **Dates** are always passed between agents so inventory, stock, and cash calculations stay time-consistent.
- Each request is processed in a `try/except`, so one failing request never crashes the full run.

---

## Submission Checklist

1. `project_starter.py` with the completed agent logic
2. A **workflow diagram** describing the agent architecture and data flow (`workflow_diagram.md`)
3. Outputs from your test run (`test_results.csv` and `run_output.log`)
4. `reflection_report.md` with the design rationale and evaluation results

---
