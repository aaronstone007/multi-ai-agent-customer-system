import pandas as pd
import numpy as np
import os
import time
import dotenv
import ast
from sqlalchemy.sql import text
from datetime import datetime, timedelta
from typing import Dict, List, Union
from sqlalchemy import create_engine, Engine

# Create an SQLite database
db_engine = create_engine("sqlite:///munder_difflin.db")

# List containing the different kinds of papers 
paper_supplies = [
    # Paper Types (priced per sheet unless specified)
    {"item_name": "A4 paper",                         "category": "paper",        "unit_price": 0.05},
    {"item_name": "Letter-sized paper",              "category": "paper",        "unit_price": 0.06},
    {"item_name": "Cardstock",                        "category": "paper",        "unit_price": 0.15},
    {"item_name": "Colored paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Glossy paper",                     "category": "paper",        "unit_price": 0.20},
    {"item_name": "Matte paper",                      "category": "paper",        "unit_price": 0.18},
    {"item_name": "Recycled paper",                   "category": "paper",        "unit_price": 0.08},
    {"item_name": "Eco-friendly paper",               "category": "paper",        "unit_price": 0.12},
    {"item_name": "Poster paper",                     "category": "paper",        "unit_price": 0.25},
    {"item_name": "Banner paper",                     "category": "paper",        "unit_price": 0.30},
    {"item_name": "Kraft paper",                      "category": "paper",        "unit_price": 0.10},
    {"item_name": "Construction paper",               "category": "paper",        "unit_price": 0.07},
    {"item_name": "Wrapping paper",                   "category": "paper",        "unit_price": 0.15},
    {"item_name": "Glitter paper",                    "category": "paper",        "unit_price": 0.22},
    {"item_name": "Decorative paper",                 "category": "paper",        "unit_price": 0.18},
    {"item_name": "Letterhead paper",                 "category": "paper",        "unit_price": 0.12},
    {"item_name": "Legal-size paper",                 "category": "paper",        "unit_price": 0.08},
    {"item_name": "Crepe paper",                      "category": "paper",        "unit_price": 0.05},
    {"item_name": "Photo paper",                      "category": "paper",        "unit_price": 0.25},
    {"item_name": "Uncoated paper",                   "category": "paper",        "unit_price": 0.06},
    {"item_name": "Butcher paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Heavyweight paper",                "category": "paper",        "unit_price": 0.20},
    {"item_name": "Standard copy paper",              "category": "paper",        "unit_price": 0.04},
    {"item_name": "Bright-colored paper",             "category": "paper",        "unit_price": 0.12},
    {"item_name": "Patterned paper",                  "category": "paper",        "unit_price": 0.15},

    # Product Types (priced per unit)
    {"item_name": "Paper plates",                     "category": "product",      "unit_price": 0.10},  # per plate
    {"item_name": "Paper cups",                       "category": "product",      "unit_price": 0.08},  # per cup
    {"item_name": "Paper napkins",                    "category": "product",      "unit_price": 0.02},  # per napkin
    {"item_name": "Disposable cups",                  "category": "product",      "unit_price": 0.10},  # per cup
    {"item_name": "Table covers",                     "category": "product",      "unit_price": 1.50},  # per cover
    {"item_name": "Envelopes",                        "category": "product",      "unit_price": 0.05},  # per envelope
    {"item_name": "Sticky notes",                     "category": "product",      "unit_price": 0.03},  # per sheet
    {"item_name": "Notepads",                         "category": "product",      "unit_price": 2.00},  # per pad
    {"item_name": "Invitation cards",                 "category": "product",      "unit_price": 0.50},  # per card
    {"item_name": "Flyers",                           "category": "product",      "unit_price": 0.15},  # per flyer
    {"item_name": "Party streamers",                  "category": "product",      "unit_price": 0.05},  # per roll
    {"item_name": "Decorative adhesive tape (washi tape)", "category": "product", "unit_price": 0.20},  # per roll
    {"item_name": "Paper party bags",                 "category": "product",      "unit_price": 0.25},  # per bag
    {"item_name": "Name tags with lanyards",          "category": "product",      "unit_price": 0.75},  # per tag
    {"item_name": "Presentation folders",             "category": "product",      "unit_price": 0.50},  # per folder

    # Large-format items (priced per unit)
    {"item_name": "Large poster paper (24x36 inches)", "category": "large_format", "unit_price": 1.00},
    {"item_name": "Rolls of banner paper (36-inch width)", "category": "large_format", "unit_price": 2.50},

    # Specialty papers
    {"item_name": "100 lb cover stock",               "category": "specialty",    "unit_price": 0.50},
    {"item_name": "80 lb text paper",                 "category": "specialty",    "unit_price": 0.40},
    {"item_name": "250 gsm cardstock",                "category": "specialty",    "unit_price": 0.30},
    {"item_name": "220 gsm poster paper",             "category": "specialty",    "unit_price": 0.35},
]

# Given below are some utility functions you can use to implement your multi-agent system

def generate_sample_inventory(paper_supplies: list, coverage: float = 0.4, seed: int = 137) -> pd.DataFrame:
    """
    Generate inventory for exactly a specified percentage of items from the full paper supply list.

    This function randomly selects exactly `coverage` × N items from the `paper_supplies` list,
    and assigns each selected item:
    - a random stock quantity between 200 and 800,
    - a minimum stock level between 50 and 150.

    The random seed ensures reproducibility of selection and stock levels.

    Args:
        paper_supplies (list): A list of dictionaries, each representing a paper item with
                               keys 'item_name', 'category', and 'unit_price'.
        coverage (float, optional): Fraction of items to include in the inventory (default is 0.4, or 40%).
        seed (int, optional): Random seed for reproducibility (default is 137).

    Returns:
        pd.DataFrame: A DataFrame with the selected items and assigned inventory values, including:
                      - item_name
                      - category
                      - unit_price
                      - current_stock
                      - min_stock_level
    """
    # Ensure reproducible random output
    np.random.seed(seed)

    # Calculate number of items to include based on coverage
    num_items = int(len(paper_supplies) * coverage)

    # Randomly select item indices without replacement
    selected_indices = np.random.choice(
        range(len(paper_supplies)),
        size=num_items,
        replace=False
    )

    # Extract selected items from paper_supplies list
    selected_items = [paper_supplies[i] for i in selected_indices]

    # Construct inventory records
    inventory = []
    for item in selected_items:
        inventory.append({
            "item_name": item["item_name"],
            "category": item["category"],
            "unit_price": item["unit_price"],
            "current_stock": np.random.randint(200, 800),  # Realistic stock range
            "min_stock_level": np.random.randint(50, 150)  # Reasonable threshold for reordering
        })

    # Return inventory as a pandas DataFrame
    return pd.DataFrame(inventory)

def init_database(db_engine: Engine, seed: int = 137) -> Engine:    
    """
    Set up the Munder Difflin database with all required tables and initial records.

    This function performs the following tasks:
    - Creates the 'transactions' table for logging stock orders and sales
    - Loads customer inquiries from 'quote_requests.csv' into a 'quote_requests' table
    - Loads previous quotes from 'quotes.csv' into a 'quotes' table, extracting useful metadata
    - Generates a random subset of paper inventory using `generate_sample_inventory`
    - Inserts initial financial records including available cash and starting stock levels

    Args:
        db_engine (Engine): A SQLAlchemy engine connected to the SQLite database.
        seed (int, optional): A random seed used to control reproducibility of inventory stock levels.
                              Default is 137.

    Returns:
        Engine: The same SQLAlchemy engine, after initializing all necessary tables and records.

    Raises:
        Exception: If an error occurs during setup, the exception is printed and raised.
    """
    try:
        # ----------------------------
        # 1. Create an empty 'transactions' table schema
        # ----------------------------
        transactions_schema = pd.DataFrame({
            "id": [],
            "item_name": [],
            "transaction_type": [],  # 'stock_orders' or 'sales'
            "units": [],             # Quantity involved
            "price": [],             # Total price for the transaction
            "transaction_date": [],  # ISO-formatted date
        })
        transactions_schema.to_sql("transactions", db_engine, if_exists="replace", index=False)

        # Set a consistent starting date
        initial_date = datetime(2025, 1, 1).isoformat()

        # ----------------------------
        # 2. Load and initialize 'quote_requests' table
        # ----------------------------
        quote_requests_df = pd.read_csv("quote_requests.csv")
        quote_requests_df["id"] = range(1, len(quote_requests_df) + 1)
        quote_requests_df.to_sql("quote_requests", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 3. Load and transform 'quotes' table
        # ----------------------------
        quotes_df = pd.read_csv("quotes.csv")
        quotes_df["request_id"] = range(1, len(quotes_df) + 1)
        quotes_df["order_date"] = initial_date

        # Unpack metadata fields (job_type, order_size, event_type) if present
        if "request_metadata" in quotes_df.columns:
            quotes_df["request_metadata"] = quotes_df["request_metadata"].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x
            )
            quotes_df["job_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("job_type", ""))
            quotes_df["order_size"] = quotes_df["request_metadata"].apply(lambda x: x.get("order_size", ""))
            quotes_df["event_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("event_type", ""))

        # Retain only relevant columns
        quotes_df = quotes_df[[
            "request_id",
            "total_amount",
            "quote_explanation",
            "order_date",
            "job_type",
            "order_size",
            "event_type"
        ]]
        quotes_df.to_sql("quotes", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 4. Generate inventory and seed stock
        # ----------------------------
        inventory_df = generate_sample_inventory(paper_supplies, seed=seed)

        # Seed initial transactions
        initial_transactions = []

        # Add a starting cash balance via a dummy sales transaction
        initial_transactions.append({
            "item_name": None,
            "transaction_type": "sales",
            "units": None,
            "price": 50000.0,
            "transaction_date": initial_date,
        })

        # Add one stock order transaction per inventory item
        for _, item in inventory_df.iterrows():
            initial_transactions.append({
                "item_name": item["item_name"],
                "transaction_type": "stock_orders",
                "units": item["current_stock"],
                "price": item["current_stock"] * item["unit_price"],
                "transaction_date": initial_date,
            })

        # Commit transactions to database
        pd.DataFrame(initial_transactions).to_sql("transactions", db_engine, if_exists="append", index=False)

        # Save the inventory reference table
        inventory_df.to_sql("inventory", db_engine, if_exists="replace", index=False)

        return db_engine

    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def create_transaction(
    item_name: str,
    transaction_type: str,
    quantity: int,
    price: float,
    date: Union[str, datetime],
) -> int:
    """
    This function records a transaction of type 'stock_orders' or 'sales' with a specified
    item name, quantity, total price, and transaction date into the 'transactions' table of the database.

    Args:
        item_name (str): The name of the item involved in the transaction.
        transaction_type (str): Either 'stock_orders' or 'sales'.
        quantity (int): Number of units involved in the transaction.
        price (float): Total price of the transaction.
        date (str or datetime): Date of the transaction in ISO 8601 format.

    Returns:
        int: The ID of the newly inserted transaction.

    Raises:
        ValueError: If `transaction_type` is not 'stock_orders' or 'sales'.
        Exception: For other database or execution errors.
    """
    try:
        # Convert datetime to ISO string if necessary
        date_str = date.isoformat() if isinstance(date, datetime) else date

        # Validate transaction type
        if transaction_type not in {"stock_orders", "sales"}:
            raise ValueError("Transaction type must be 'stock_orders' or 'sales'")

        # Prepare transaction record as a single-row DataFrame
        transaction = pd.DataFrame([{
            "item_name": item_name,
            "transaction_type": transaction_type,
            "units": quantity,
            "price": price,
            "transaction_date": date_str,
        }])

        # Insert the record into the database
        transaction.to_sql("transactions", db_engine, if_exists="append", index=False)

        # Fetch and return the ID of the inserted row
        result = pd.read_sql("SELECT last_insert_rowid() as id", db_engine)
        return int(result.iloc[0]["id"])

    except Exception as e:
        print(f"Error creating transaction: {e}")
        raise

def get_all_inventory(as_of_date: str) -> Dict[str, int]:
    """
    Retrieve a snapshot of available inventory as of a specific date.

    This function calculates the net quantity of each item by summing 
    all stock orders and subtracting all sales up to and including the given date.

    Only items with positive stock are included in the result.

    Args:
        as_of_date (str): ISO-formatted date string (YYYY-MM-DD) representing the inventory cutoff.

    Returns:
        Dict[str, int]: A dictionary mapping item names to their current stock levels.
    """
    # SQL query to compute stock levels per item as of the given date
    query = """
        SELECT
            item_name,
            SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END) as stock
        FROM transactions
        WHERE item_name IS NOT NULL
        AND transaction_date <= :as_of_date
        GROUP BY item_name
        HAVING stock > 0
    """

    # Execute the query with the date parameter
    result = pd.read_sql(query, db_engine, params={"as_of_date": as_of_date})

    # Convert the result into a dictionary {item_name: stock}
    return dict(zip(result["item_name"], result["stock"]))

def get_stock_level(item_name: str, as_of_date: Union[str, datetime]) -> pd.DataFrame:
    """
    Retrieve the stock level of a specific item as of a given date.

    This function calculates the net stock by summing all 'stock_orders' and 
    subtracting all 'sales' transactions for the specified item up to the given date.

    Args:
        item_name (str): The name of the item to look up.
        as_of_date (str or datetime): The cutoff date (inclusive) for calculating stock.

    Returns:
        pd.DataFrame: A single-row DataFrame with columns 'item_name' and 'current_stock'.
    """
    # Convert date to ISO string format if it's a datetime object
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    # SQL query to compute net stock level for the item
    stock_query = """
        SELECT
            item_name,
            COALESCE(SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END), 0) AS current_stock
        FROM transactions
        WHERE item_name = :item_name
        AND transaction_date <= :as_of_date
    """

    # Execute query and return result as a DataFrame
    return pd.read_sql(
        stock_query,
        db_engine,
        params={"item_name": item_name, "as_of_date": as_of_date},
    )

def get_supplier_delivery_date(input_date_str: str, quantity: int) -> str:
    """
    Estimate the supplier delivery date based on the requested order quantity and a starting date.

    Delivery lead time increases with order size:
        - ≤10 units: same day
        - 11–100 units: 1 day
        - 101–1000 units: 4 days
        - >1000 units: 7 days

    Args:
        input_date_str (str): The starting date in ISO format (YYYY-MM-DD).
        quantity (int): The number of units in the order.

    Returns:
        str: Estimated delivery date in ISO format (YYYY-MM-DD).
    """
    # Debug log (comment out in production if needed)
    print(f"FUNC (get_supplier_delivery_date): Calculating for qty {quantity} from date string '{input_date_str}'")

    # Attempt to parse the input date
    try:
        input_date_dt = datetime.fromisoformat(input_date_str.split("T")[0])
    except (ValueError, TypeError):
        # Fallback to current date on format error
        print(f"WARN (get_supplier_delivery_date): Invalid date format '{input_date_str}', using today as base.")
        input_date_dt = datetime.now()

    # Determine delivery delay based on quantity
    if quantity <= 10:
        days = 0
    elif quantity <= 100:
        days = 1
    elif quantity <= 1000:
        days = 4
    else:
        days = 7

    # Add delivery days to the starting date
    delivery_date_dt = input_date_dt + timedelta(days=days)

    # Return formatted delivery date
    return delivery_date_dt.strftime("%Y-%m-%d")

def get_cash_balance(as_of_date: Union[str, datetime]) -> float:
    """
    Calculate the current cash balance as of a specified date.

    The balance is computed by subtracting total stock purchase costs ('stock_orders')
    from total revenue ('sales') recorded in the transactions table up to the given date.

    Args:
        as_of_date (str or datetime): The cutoff date (inclusive) in ISO format or as a datetime object.

    Returns:
        float: Net cash balance as of the given date. Returns 0.0 if no transactions exist or an error occurs.
    """
    try:
        # Convert date to ISO format if it's a datetime object
        if isinstance(as_of_date, datetime):
            as_of_date = as_of_date.isoformat()

        # Query all transactions on or before the specified date
        transactions = pd.read_sql(
            "SELECT * FROM transactions WHERE transaction_date <= :as_of_date",
            db_engine,
            params={"as_of_date": as_of_date},
        )

        # Compute the difference between sales and stock purchases
        if not transactions.empty:
            total_sales = transactions.loc[transactions["transaction_type"] == "sales", "price"].sum()
            total_purchases = transactions.loc[transactions["transaction_type"] == "stock_orders", "price"].sum()
            return float(total_sales - total_purchases)

        return 0.0

    except Exception as e:
        print(f"Error getting cash balance: {e}")
        return 0.0


def generate_financial_report(as_of_date: Union[str, datetime]) -> Dict:
    """
    Generate a complete financial report for the company as of a specific date.

    This includes:
    - Cash balance
    - Inventory valuation
    - Combined asset total
    - Itemized inventory breakdown
    - Top 5 best-selling products

    Args:
        as_of_date (str or datetime): The date (inclusive) for which to generate the report.

    Returns:
        Dict: A dictionary containing the financial report fields:
            - 'as_of_date': The date of the report
            - 'cash_balance': Total cash available
            - 'inventory_value': Total value of inventory
            - 'total_assets': Combined cash and inventory value
            - 'inventory_summary': List of items with stock and valuation details
            - 'top_selling_products': List of top 5 products by revenue
    """
    # Normalize date input
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    # Get current cash balance
    cash = get_cash_balance(as_of_date)

    # Get current inventory snapshot
    inventory_df = pd.read_sql("SELECT * FROM inventory", db_engine)
    inventory_value = 0.0
    inventory_summary = []

    # Compute total inventory value and summary by item
    for _, item in inventory_df.iterrows():
        stock_info = get_stock_level(item["item_name"], as_of_date)
        stock = stock_info["current_stock"].iloc[0]
        item_value = stock * item["unit_price"]
        inventory_value += item_value

        inventory_summary.append({
            "item_name": item["item_name"],
            "stock": stock,
            "unit_price": item["unit_price"],
            "value": item_value,
        })

    # Identify top-selling products by revenue
    top_sales_query = """
        SELECT item_name, SUM(units) as total_units, SUM(price) as total_revenue
        FROM transactions
        WHERE transaction_type = 'sales' AND transaction_date <= :date
        GROUP BY item_name
        ORDER BY total_revenue DESC
        LIMIT 5
    """
    top_sales = pd.read_sql(top_sales_query, db_engine, params={"date": as_of_date})
    top_selling_products = top_sales.to_dict(orient="records")

    return {
        "as_of_date": as_of_date,
        "cash_balance": cash,
        "inventory_value": inventory_value,
        "total_assets": cash + inventory_value,
        "inventory_summary": inventory_summary,
        "top_selling_products": top_selling_products,
    }


def search_quote_history(search_terms: List[str], limit: int = 5) -> List[Dict]:
    """
    Retrieve a list of historical quotes that match any of the provided search terms.

    The function searches both the original customer request (from `quote_requests`) and
    the explanation for the quote (from `quotes`) for each keyword. Results are sorted by
    most recent order date and limited by the `limit` parameter.

    Args:
        search_terms (List[str]): List of terms to match against customer requests and explanations.
        limit (int, optional): Maximum number of quote records to return. Default is 5.

    Returns:
        List[Dict]: A list of matching quotes, each represented as a dictionary with fields:
            - original_request
            - total_amount
            - quote_explanation
            - job_type
            - order_size
            - event_type
            - order_date
    """
    conditions = []
    params = {}

    # Build SQL WHERE clause using LIKE filters for each search term
    for i, term in enumerate(search_terms):
        param_name = f"term_{i}"
        conditions.append(
            f"(LOWER(qr.response) LIKE :{param_name} OR "
            f"LOWER(q.quote_explanation) LIKE :{param_name})"
        )
        params[param_name] = f"%{term.lower()}%"

    # Combine conditions; fallback to always-true if no terms provided
    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Final SQL query to join quotes with quote_requests
    query = f"""
        SELECT
            qr.response AS original_request,
            q.total_amount,
            q.quote_explanation,
            q.job_type,
            q.order_size,
            q.event_type,
            q.order_date
        FROM quotes q
        JOIN quote_requests qr ON q.request_id = qr.id
        WHERE {where_clause}
        ORDER BY q.order_date DESC
        LIMIT {limit}
    """

    # Execute parameterized query
    with db_engine.connect() as conn:
        result = conn.execute(text(query), params)
        return [dict(row._mapping) for row in result]

########################
########################
########################
# YOUR MULTI AGENT STARTS HERE
########################
########################
########################

import json
import re
from difflib import get_close_matches

from smolagents import CodeAgent, ToolCallingAgent, OpenAIServerModel, tool

# ----------------------------------------------------------------------------
# 1. Environment and model setup
# ----------------------------------------------------------------------------
dotenv.load_dotenv()

API_KEY = os.getenv("UDACITY_OPENAI_API_KEY")
if not API_KEY or API_KEY == "your_openai_key_here":
    raise RuntimeError(
        "UDACITY_OPENAI_API_KEY is not set. Add your key to the .env file "
        "(UDACITY_OPENAI_API_KEY=...) before running."
    )

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openai.vocareum.com/v1")
MODEL_ID = os.getenv("MODEL_ID", "gpt-4o-mini")

model = OpenAIServerModel(
    model_id=MODEL_ID,
    api_base=OPENAI_BASE_URL,
    api_key=API_KEY,
)

# ----------------------------------------------------------------------------
# Shared helpers: price map and item-name normalization
# ----------------------------------------------------------------------------
# O(1) unit-price lookup keyed by the exact database item name.
PAPER_PRICE_MAP: Dict[str, float] = {
    item["item_name"]: item["unit_price"] for item in paper_supplies
}
# Lowercase index for fuzzy matching loose customer wording -> exact DB name.
_ITEM_NAMES = list(PAPER_PRICE_MAP.keys())
_ITEM_NAMES_LOWER = {name.lower(): name for name in _ITEM_NAMES}


def normalize_item_name(raw: str) -> Union[str, None]:
    """
    Resolve a loosely-worded item description to an exact database item name.

    Strategy (in order):
      1. Exact case-insensitive match.
      2. Substring containment either direction (e.g. "cardstock" -> "Cardstock").
      3. Fuzzy close match on token overlap using difflib.

    Returns the exact DB item name, or None if no confident match is found.
    """
    if not raw or not isinstance(raw, str):
        return None

    cleaned = raw.strip().lower()
    # Drop common qualifiers that are not part of DB names.
    cleaned = re.sub(r"\b(sheets?|reams?|boxes?|of|white|assorted|heavy|high[- ]quality)\b", " ", cleaned)
    cleaned = re.sub(r"[^a-z0-9\s\(\)\-]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if not cleaned:
        return None

    # 1. Exact match.
    if cleaned in _ITEM_NAMES_LOWER:
        return _ITEM_NAMES_LOWER[cleaned]

    # 2. Substring containment.
    candidates = []
    for lower_name, exact_name in _ITEM_NAMES_LOWER.items():
        if cleaned in lower_name or lower_name in cleaned:
            candidates.append((len(lower_name), exact_name))
    if candidates:
        # Prefer the longest (most specific) match.
        candidates.sort(reverse=True)
        return candidates[0][1]

    # 3. Fuzzy match.
    match = get_close_matches(cleaned, list(_ITEM_NAMES_LOWER.keys()), n=1, cutoff=0.7)
    if match:
        return _ITEM_NAMES_LOWER[match[0]]

    return None


def _parse_line_items(line_items: Union[str, list]) -> List[Dict]:
    """Coerce line_items passed by an agent (JSON string or list) into a list of dicts."""
    if isinstance(line_items, str):
        try:
            line_items = json.loads(line_items)
        except json.JSONDecodeError:
            try:
                line_items = ast.literal_eval(line_items)
            except (ValueError, SyntaxError):
                return []
    if isinstance(line_items, dict):
        line_items = [line_items]
    return line_items if isinstance(line_items, list) else []


# Bulk-discount tiers: (min_units, min_subtotal, discount_rate)
def _bulk_discount_rate(total_units: int, subtotal: float) -> float:
    if total_units >= 1000 or subtotal >= 500:
        return 0.10
    if total_units >= 500 or subtotal >= 200:
        return 0.05
    return 0.0


# ----------------------------------------------------------------------------
# 2. Tools for the inventory agent
# ----------------------------------------------------------------------------
@tool
def check_inventory(item_name: str, as_of_date: str) -> str:
    """
    Report the current stock level of a single item as of a given date.

    Args:
        item_name: The item to look up (loose wording is resolved to the exact DB name).
        as_of_date: ISO date (YYYY-MM-DD) used as the inventory cutoff.
    """
    resolved = normalize_item_name(item_name)
    if resolved is None:
        return f"Item '{item_name}' is not a recognized product and cannot be stocked."
    df = get_stock_level(resolved, as_of_date)
    stock = int(df["current_stock"].iloc[0]) if not df.empty else 0
    return f"{resolved}: {stock} units in stock as of {as_of_date}."


@tool
def check_all_inventory(as_of_date: str) -> str:
    """
    Return a snapshot of all in-stock items as of a given date.

    Args:
        as_of_date: ISO date (YYYY-MM-DD) used as the inventory cutoff.
    """
    inv = get_all_inventory(as_of_date)
    if not inv:
        return "No items are currently in stock."
    return json.dumps(inv)


@tool
def restock_item(item_name: str, quantity: int, as_of_date: str) -> str:
    """
    Place a supplier stock order for an item if affordable, and report the delivery date.

    Args:
        item_name: The item to restock (resolved to the exact DB name).
        quantity: Number of units to order (must be positive).
        as_of_date: ISO date (YYYY-MM-DD) the order is placed on.
    """
    resolved = normalize_item_name(item_name)
    if resolved is None:
        return f"Item '{item_name}' is not a recognized product; cannot restock."
    if quantity <= 0:
        return "Restock quantity must be positive."

    unit_price = PAPER_PRICE_MAP[resolved]
    cost = quantity * unit_price
    cash = get_cash_balance(as_of_date)
    if cost > cash:
        return (
            f"Cannot restock {quantity} units of {resolved}: cost ${cost:.2f} "
            f"exceeds available cash ${cash:.2f}."
        )

    create_transaction(resolved, "stock_orders", quantity, cost, as_of_date)
    delivery = get_supplier_delivery_date(as_of_date, quantity)
    return (
        f"Ordered {quantity} units of {resolved} for ${cost:.2f}. "
        f"Estimated delivery date: {delivery}."
    )


# ----------------------------------------------------------------------------
# 3. Tools for the quoting agent
# ----------------------------------------------------------------------------
@tool
def parse_request(request_text: str) -> str:
    """
    Extract structured line items (item_name, quantity) from a customer request.

    Args:
        request_text: The raw natural-language customer request.
    """
    items = []
    # Match patterns like "200 sheets of A4 glossy paper" or "10 reams of standard copy paper".
    pattern = re.compile(r"(\d[\d,]*)\s+(?:sheets?|reams?|boxes?|rolls?|units?|pads?|cards?|of)?\s*([A-Za-z][A-Za-z0-9\s\-\(\)]+)")
    for match in pattern.finditer(request_text):
        qty = int(match.group(1).replace(",", ""))
        raw_name = match.group(2).strip()
        resolved = normalize_item_name(raw_name)
        items.append({
            "raw": raw_name,
            "item_name": resolved,
            "quantity": qty,
            "recognized": resolved is not None,
        })
    return json.dumps(items)


@tool
def get_historical_quotes(search_terms: List[str]) -> str:
    """
    Look up past quotes matching any of the given search terms to inform pricing.

    Args:
        search_terms: Keywords to match against past requests and quote explanations.
    """
    results = search_quote_history(search_terms, limit=5)
    if not results:
        return "No matching historical quotes found."
    return json.dumps(results, default=str)


@tool
def price_quote(line_items: str, as_of_date: str) -> str:
    """
    Price a set of line items, apply a bulk discount, and return a detailed quote.

    Args:
        line_items: JSON list of objects with 'item_name' and 'quantity'.
        as_of_date: ISO date (YYYY-MM-DD) of the quote.
    """
    items = _parse_line_items(line_items)
    if not items:
        return "No valid line items to price."

    priced = []
    unavailable = []
    subtotal = 0.0
    total_units = 0

    for entry in items:
        resolved = normalize_item_name(entry.get("item_name") or entry.get("raw", ""))
        qty = int(entry.get("quantity", 0))
        if resolved is None or qty <= 0:
            unavailable.append(entry.get("item_name") or entry.get("raw", "unknown"))
            continue
        unit_price = PAPER_PRICE_MAP[resolved]
        line_total = qty * unit_price
        subtotal += line_total
        total_units += qty
        priced.append({
            "item_name": resolved,
            "quantity": qty,
            "unit_price": unit_price,
            "line_total": round(line_total, 2),
        })

    discount_rate = _bulk_discount_rate(total_units, subtotal)
    discount_amount = round(subtotal * discount_rate, 2)
    total = round(subtotal - discount_amount, 2)

    explanation_parts = [f"Subtotal: ${subtotal:.2f} across {total_units} units."]
    if discount_rate > 0:
        explanation_parts.append(
            f"Applied a {int(discount_rate * 100)}% bulk discount (-${discount_amount:.2f})."
        )
    else:
        explanation_parts.append("No bulk discount applies to this order size.")
    if unavailable:
        explanation_parts.append(f"Unavailable/unrecognized items: {', '.join(unavailable)}.")

    return json.dumps({
        "line_items": priced,
        "subtotal": round(subtotal, 2),
        "discount_rate": discount_rate,
        "discount_amount": discount_amount,
        "total_amount": total,
        "unavailable_items": unavailable,
        "explanation": " ".join(explanation_parts),
    })


# ----------------------------------------------------------------------------
# 4. Tools for the ordering agent
# ----------------------------------------------------------------------------
@tool
def check_cash(as_of_date: str) -> str:
    """
    Report the company's cash balance as of a given date.

    Args:
        as_of_date: ISO date (YYYY-MM-DD) cutoff.
    """
    return f"Cash balance as of {as_of_date}: ${get_cash_balance(as_of_date):.2f}"


@tool
def fulfill_order(line_items: str, as_of_date: str) -> str:
    """
    Fulfill an accepted order: record sales, restock short items, and confirm.

    For each item, verifies available stock. If stock is sufficient a 'sales'
    transaction is recorded. If stock is short, a restock is attempted first
    (subject to affordability) and the delivery date is reported.

    Args:
        line_items: JSON list of objects with 'item_name', 'quantity', and 'unit_price'.
        as_of_date: ISO date (YYYY-MM-DD) of fulfillment.
    """
    items = _parse_line_items(line_items)
    if not items:
        return "No valid line items to fulfill."

    lines = []
    for entry in items:
        resolved = normalize_item_name(entry.get("item_name") or entry.get("raw", ""))
        qty = int(entry.get("quantity", 0))
        if resolved is None or qty <= 0:
            lines.append(f"Skipped unrecognized item '{entry.get('item_name')}'.")
            continue

        unit_price = float(entry.get("unit_price", PAPER_PRICE_MAP[resolved]))
        stock_df = get_stock_level(resolved, as_of_date)
        stock = int(stock_df["current_stock"].iloc[0]) if not stock_df.empty else 0

        if stock < qty:
            shortfall = qty - stock
            restock_msg = restock_item(resolved, shortfall, as_of_date)
            lines.append(
                f"{resolved}: only {stock} in stock for {qty} requested. {restock_msg}"
            )
            # After restocking, only sell what is now available (stock + delivered shortfall).
            available_now = get_stock_level(resolved, as_of_date)
            stock = int(available_now["current_stock"].iloc[0]) if not available_now.empty else stock

        sell_qty = min(qty, stock)
        if sell_qty > 0:
            revenue = round(sell_qty * unit_price, 2)
            create_transaction(resolved, "sales", sell_qty, revenue, as_of_date)
            lines.append(f"Sold {sell_qty} units of {resolved} for ${revenue:.2f}.")
        else:
            lines.append(f"{resolved}: unable to fulfill immediately; awaiting restock.")

    return " ".join(lines)


# ----------------------------------------------------------------------------
# 5. Specialized agents
# ----------------------------------------------------------------------------
inventory_agent = ToolCallingAgent(
    tools=[check_inventory, check_all_inventory, restock_item],
    model=model,
    name="inventory_agent",
    description=(
        "Checks stock levels and restocks items. Always pass the request date as the "
        "as_of_date. Use exact database item names."
    ),
    max_steps=6,
)

quoting_agent = ToolCallingAgent(
    tools=[parse_request, get_historical_quotes, price_quote],
    model=model,
    name="quoting_agent",
    description=(
        "Parses customer requests into line items, consults historical quotes, and "
        "produces a priced quote with bulk discounts. Always uses exact database item names."
    ),
    max_steps=8,
)

ordering_agent = ToolCallingAgent(
    tools=[check_cash, fulfill_order],
    model=model,
    name="ordering_agent",
    description=(
        "Finalizes accepted orders by recording sales, restocking shortfalls, and "
        "confirming fulfillment with delivery dates. Always pass the request date."
    ),
    max_steps=6,
)

# ----------------------------------------------------------------------------
# 6. Orchestrator agent (manages the three specialized agents; 4 agents total)
# ----------------------------------------------------------------------------
orchestrator = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[quoting_agent, inventory_agent, ordering_agent],
    name="orchestrator",
    description="Coordinates quoting, inventory, and ordering agents for paper supply requests.",
    max_steps=12,
)

ORCHESTRATOR_INSTRUCTIONS = (
    "You are the sales operations orchestrator for Munder Difflin Paper Company. "
    "For each customer request:\n"
    "1. Use quoting_agent to parse the request and produce a priced quote (with bulk discounts).\n"
    "2. Use inventory_agent to check stock for the quoted items as of the request date.\n"
    "3. Use ordering_agent to fulfill available items (recording sales) and restock any shortfall.\n"
    "Always pass the exact request date (as_of_date) to every agent. Use exact database item "
    "item names. Return ONE concise customer-facing message that states the quoted total, the "
    "discount applied, item availability, and the fulfillment/delivery outcome.\n\n"
    "Customer request: {request}"
)


def call_your_multi_agent_system(request_with_date: str) -> str:
    """Run the orchestrator on a single request and return its final text response."""
    task = ORCHESTRATOR_INSTRUCTIONS.format(request=request_with_date)
    result = orchestrator.run(task)
    return str(result)


# Run your test scenarios by writing them here. Make sure to keep track of them.

def run_test_scenarios():
    
    print("Initializing Database...")
    init_database(db_engine)
    try:
        quote_requests_sample = pd.read_csv("quote_requests_sample.csv")
        quote_requests_sample["request_date"] = pd.to_datetime(
            quote_requests_sample["request_date"], format="%m/%d/%y", errors="coerce"
        )
        quote_requests_sample.dropna(subset=["request_date"], inplace=True)
        quote_requests_sample = quote_requests_sample.sort_values("request_date")
    except Exception as e:
        print(f"FATAL: Error loading test data: {e}")
        return

    # Get initial state
    initial_date = quote_requests_sample["request_date"].min().strftime("%Y-%m-%d")
    report = generate_financial_report(initial_date)
    current_cash = report["cash_balance"]
    current_inventory = report["inventory_value"]

    ############
    ############
    ############
    # INITIALIZE YOUR MULTI AGENT SYSTEM HERE
    ############
    ############
    ############
    # The orchestrator and its managed agents are constructed once at module load
    # (see the "YOUR MULTI AGENT STARTS HERE" section above). Nothing further to
    # initialize here.
    print(f"Starting cash: ${current_cash:.2f} | Starting inventory value: ${current_inventory:.2f}")

    results = []
    for idx, row in quote_requests_sample.iterrows():
        request_date = row["request_date"].strftime("%Y-%m-%d")

        print(f"\n=== Request {idx+1} ===")
        print(f"Context: {row['job']} organizing {row['event']}")
        print(f"Request Date: {request_date}")
        print(f"Cash Balance: ${current_cash:.2f}")
        print(f"Inventory Value: ${current_inventory:.2f}")

        # Process request
        request_with_date = f"{row['request']} (Date of request: {request_date})"

        ############
        ############
        ############
        # USE YOUR MULTI AGENT SYSTEM TO HANDLE THE REQUEST
        ############
        ############
        ############
        try:
            response = call_your_multi_agent_system(request_with_date)
        except Exception as e:
            # Never let one bad request crash the whole run; ensure `response`
            # is always defined for printing and the results log.
            print(f"ERROR processing request {idx + 1}: {e}")
            response = f"ERROR: unable to process this request ({e})"

        # Update state
        report = generate_financial_report(request_date)
        current_cash = report["cash_balance"]
        current_inventory = report["inventory_value"]

        print(f"Response: {response}")
        print(f"Updated Cash: ${current_cash:.2f}")
        print(f"Updated Inventory: ${current_inventory:.2f}")

        results.append(
            {
                "request_id": idx + 1,
                "request_date": request_date,
                "cash_balance": current_cash,
                "inventory_value": current_inventory,
                "response": response,
            }
        )

        time.sleep(1)

    # Final report
    final_date = quote_requests_sample["request_date"].max().strftime("%Y-%m-%d")
    final_report = generate_financial_report(final_date)
    print("\n===== FINAL FINANCIAL REPORT =====")
    print(f"Final Cash: ${final_report['cash_balance']:.2f}")
    print(f"Final Inventory: ${final_report['inventory_value']:.2f}")

    # Save results
    pd.DataFrame(results).to_csv("test_results.csv", index=False)
    return results


if __name__ == "__main__":
    results = run_test_scenarios()
