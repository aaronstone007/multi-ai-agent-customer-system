# Munder Difflin Multi-Agent System — Workflow Diagram

This document describes the agent architecture and data flow for the Munder Difflin
paper-company multi-agent system. It uses [Mermaid](https://mermaid.js.org/) diagrams,
which render directly in GitHub and most Markdown viewers.

## Agent Roster (4 agents, under the 5-agent limit)

| Agent | Type | Responsibility |
| --- | --- | --- |
| Orchestrator | `CodeAgent` | Routes each request, sequences the specialized agents, assembles one customer-facing reply |
| Quoting Agent | `ToolCallingAgent` | Parses the request, consults history, prices items, applies bulk discounts |
| Inventory Agent | `ToolCallingAgent` | Checks stock as of the request date, restocks, estimates delivery |
| Ordering Agent | `ToolCallingAgent` | Records sales, covers shortfalls, guards cash, confirms fulfillment |

## Architecture

```mermaid
graph TD
    A[quote_requests_sample.csv] --> B[run_test_scenarios loop]
    B --> C[Orchestrator Agent - CodeAgent]

    C --> D[Quoting Agent]
    D --> D1["parse_request<br/>Purpose: extract item names and quantities<br/>Helper: custom parser + normalize_item_name"]
    D --> D2["get_historical_quotes<br/>Purpose: retrieve prior quote examples<br/>Helper: search_quote_history"]
    D --> D3["price_quote<br/>Purpose: calculate subtotal, discount, total<br/>Helper: PAPER_PRICE_MAP + _bulk_discount_rate"]

    C --> E[Inventory Agent]
    E --> E1["check_inventory<br/>Purpose: check one item stock<br/>Helper: get_stock_level"]
    E --> E2["check_all_inventory<br/>Purpose: list available stock<br/>Helper: get_all_inventory"]
    E --> E3["restock_item<br/>Purpose: buy stock shortfall<br/>Helpers: get_cash_balance, create_transaction, get_supplier_delivery_date"]

    C --> F[Ordering Agent]
    F --> F1["check_cash<br/>Purpose: verify available cash<br/>Helper: get_cash_balance"]
    F --> F2["fulfill_order<br/>Purpose: record sales and shortfall handling<br/>Helpers: get_stock_level, create_transaction, restock_item"]
    F --> F3["financial_report_tool<br/>Purpose: inspect cash, inventory value, assets, top sellers<br/>Helper: generate_financial_report"]

    D3 --> G[(munder_difflin.db)]
    E1 --> G
    E2 --> G
    E3 --> G
    F1 --> G
    F2 --> G
    F3 --> G

    C --> H[Single text response]
    H --> I[results list]
    I --> J[test_results.csv + financial report]
```

## Per-Request Data Flow

```mermaid
sequenceDiagram
    participant Runner as run_test_scenarios
    participant Orch as Orchestrator
    participant Q as Quoting Agent
    participant Inv as Inventory Agent
    participant Ord as Ordering Agent
    participant DB as munder_difflin.db

    Runner->>Orch: request_with_date
    Orch->>Q: quote this request with as_of_date
    Q->>Q: tool parse_request extract line_items
    Q->>DB: tool get_historical_quotes calls search_quote_history
    Q->>Q: tool price_quote uses PAPER_PRICE_MAP and bulk discount
    Q-->>Orch: line_items plus total plus explanation
    Orch->>Inv: check stock for line_items with as_of_date
    Inv->>DB: tool check_inventory calls get_stock_level
    Inv->>DB: tool restock_item calls get_cash_balance, create_transaction, get_supplier_delivery_date
    Inv-->>Orch: availability plus restock and delivery info
    Orch->>Ord: fulfill accepted items with as_of_date
    Ord->>DB: tool check_cash calls get_cash_balance
    Ord->>DB: tool fulfill_order calls get_stock_level and create_transaction
    Ord->>DB: tool financial_report_tool calls generate_financial_report
    Ord-->>Orch: sales recorded plus confirmation
    Orch-->>Runner: single text response with quote, availability and fulfillment
```

## Bulk Discount Rule

```
total units >= 1000  OR  subtotal >= $500  -> 10% discount
total units >=  500  OR  subtotal >= $200  ->  5% discount
otherwise                                  ->  no discount
```

## Notes

- Agents never touch the database directly; they call `@tool` wrappers that reuse the
  utility functions in `project_starter.py` and add business rules (name normalization,
  bulk discounts, affordability checks).
- The request date (`as_of_date`) is passed to every agent so inventory, stock, cash,
  and delivery calculations stay time-consistent.
- Item names are normalized to exact database names before any transaction, so
  `create_transaction` never fails on a name mismatch.
