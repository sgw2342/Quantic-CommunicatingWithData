# Own the Morning → Win the Day: Communicating with Data

This bundle contains:
- **Python analysis scripts** (`*.py`) to recreate all dashboards and figures.
- **Database DDL** (`CreateDB.sql`) to create the SQLite schema.
- This **README** with setup and run instructions.

## 1) Environment
- Python 3.9+
- Packages: `pandas`, `numpy`, `matplotlib`, `python-pptx` (optional, for deck creation), `reportlab` (optional, for PDF export)
- SQLite 3 (CLI) or Python's built-in `sqlite3` module

## 2) Data expectations
The scripts read from a SQLite DB at:
```
/mnt/data/retail_demo.sqlite
```
If your DB is elsewhere, edit the `BASE` / `DB` paths at the top of each `*.py` file.

### Creating the database
Use the provided DDL to create an empty schema:
```bash
sqlite3 /mnt/data/retail_demo.sqlite < /mnt/data/CreateDB.sql
```

Then load your CSVs into the corresponding tables **treating the first row as data (no header)**.
Typical mapping used in the analysis (adjust if your source names differ):

- `cs_locations.csv` → `stores`
- `cs_transactions.csv` → `transactions`
- `cs_transaction_details.csv` → `transaction_details`
- `cs_products.csv` → `products`
- `cs_prod_types.csv` → `product_categories`
- `cs_cats.csv` → (if present, category helper table; not required by charts)

> Ensure column order matches the schema in `CreateDB.sql`. If your CSVs have a different order, load via a small Python script and pass columns explicitly.

**Example Python loader (no headers):**
```python
import pandas as pd, sqlite3
DB = "/mnt/data/retail_demo.sqlite"
conn = sqlite3.connect(DB)

# Example: stores
stores = pd.read_csv("/mnt/data/cs_locations.csv", header=None)
stores.columns = ["store_id","store_location"]   # adjust to your DDL
stores.to_sql("stores", conn, if_exists="append", index=False)

# Example: transactions
tx = pd.read_csv("/mnt/data/cs_transactions.csv", header=None)
tx.columns = ["transaction_id","store_id","transaction_date","transaction_time"]
tx.to_sql("transactions", conn, if_exists="append", index=False)

# Example: transaction_details
td = pd.read_csv("/mnt/data/cs_transaction_details.csv", header=None)
td.columns = ["transaction_id","product_id","transaction_qty","unit_price"]
td.to_sql("transaction_details", conn, if_exists="append", index=False)

# Example: products
prods = pd.read_csv("/mnt/data/cs_products.csv", header=None)
prods.columns = ["product_id","product_detail","product_category_id"]
prods.to_sql("products", conn, if_exists="append", index=False)

# Example: product_categories
pc = pd.read_csv("/mnt/data/cs_prod_types.csv", header=None)
pc.columns = ["product_category_id","product_category_type"]
pc.to_sql("product_categories", conn, if_exists="append", index=False)

conn.close()
```

## 3) Recreating the dashboards
Run any of the scripts below. Each script writes its PNG(s) to `/mnt/data/unified_assets` or `/mnt/data/ppt_assets`.

- `u1_tx_trend.py` — Transactions (7‑day rolling) by store
- `u3_hour_tx.py` — Avg transactions by hour (per store)
- `u4_weekday_weekend_rep.py` — Weekday vs weekend (rep store)
- `d2_hour_rev.py` — Total revenue by hour per store
- `d6_hour_share.py` — Average hourly share of daily revenue
- `d7_heatmaps_all_stores.py` — Hour × Category heatmaps (global blue scale; 1k ticks)
- `u5_share_multi_units.py` — Share of multi‑item activity (per transaction vs timestamp event)
- `d9_pairs.py` — Top product pairs (timestamp-collision heuristic)
- `u7_pareto_tx.py` — SKU Pareto (by transactions)
- `u6_category_shares.py` — Category shares per store

**Example:**
```bash
python /mnt/data/d7_heatmaps_all_stores.py
```

## 4) Notes & assumptions
- Receipts are **single-line items**; where a “basket” is needed, we use **timestamp collisions** (same store+second).
- Heatmaps use a **global blue color scale** across stores with **1k-step** colorbar ticks (no explicit max tick).


