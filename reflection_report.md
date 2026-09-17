# Reflection Report

## Architecture and Design Rationale
I implemented four agents: `orchestrator`, `quoting_agent`, `inventory_agent`, and `ordering_agent`. The orchestrator delegates each request through quoting, inventory, and fulfillment so that pricing, stock checks, and transaction recording remain separate.

## Evaluation Results
The system processed all 20 rows from `quote_requests_sample.csv`. The `cash_balance` changed on 5 of the 20 requests relative to the previous request, and all 5 recorded net sales revenue (cash increased), indicating fulfilled orders. The remaining requests were not fulfilled due to reasons such as insufficient stock or unrecognized products. No customer-facing response leaked internal errors or system output (0 rows contained HTML, tracebacks, or 404 text), confirming the output-sanitization safeguard. The run ended with a final cash balance of $45,413.75 and an inventory value of $4,586.25.

## Strengths
- Item-name normalization through `normalize_item_name` reduced database mismatches.
- Tool wrappers reused starter helpers such as `get_stock_level` and `create_transaction`.

## Future Improvements
1. Add deterministic quote-to-ledger reconciliation before calling `fulfill_order`.
2. Add safer customer-response formatting to prevent internal error leakage.
