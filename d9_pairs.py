
import sqlite3, pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize
from pathlib import Path

BASE = Path("/mnt/data"); DB = BASE/"retail_demo.sqlite"; OUT = BASE/"ppt_assets"/"d9_pairs.png"
conn = sqlite3.connect(DB)
basket_lines = pd.read_sql_query("""
SELECT s.store_location AS store, t.transaction_date AS tx_date, t.transaction_time AS tx_time,
       td.product_id, p.product_detail AS product_name,
       (td.transaction_qty * COALESCE(td.unit_price, 0.0)) AS revenue
FROM transactions t
JOIN stores s ON s.store_id = t.store_id
JOIN transaction_details td ON td.transaction_id = t.transaction_id
JOIN products p ON p.product_id = td.product_id
""", conn); conn.close()

basket_lines["basket_id"] = (basket_lines["store"].astype(str) + "|" +
                             basket_lines["tx_date"].astype(str) + "|" +
                             basket_lines["tx_time"].astype(str))
items = (basket_lines.groupby(["basket_id","product_id","product_name"], as_index=False)["revenue"].sum())
basket_sizes = items.groupby("basket_id")["product_id"].nunique().reset_index(name="basket_size")
valid_ids = basket_sizes[basket_sizes["basket_size"]>=2]["basket_id"]
items = items[items["basket_id"].isin(valid_ids)]
pairs = items.merge(items, on="basket_id", suffixes=("_a","_b"))
pairs = pairs[pairs["product_id_a"] < pairs["product_id_b"]]
pairs["pair"] = pairs["product_name_a"] + " + " + pairs["product_name_b"]
pairs["pair_revenue"] = pairs["revenue_a"] + pairs["revenue_b"]
top_pairs = (pairs.groupby("pair", as_index=False)["pair_revenue"].sum()
             .sort_values("pair_revenue", ascending=False).head(10))

labels = list(reversed(top_pairs["pair"].tolist()))
vals = np.array(list(reversed(top_pairs["pair_revenue"].tolist())))
norm = Normalize(vmin=float(vals.min()), vmax=float(vals.max()) if len(vals) else 1.0)
colors = cm.Blues(norm(vals))

plt.figure(figsize=(12, max(6, 0.5*len(vals))))
plt.barh(labels, vals, color=colors, edgecolor="none")
plt.xlabel("Pair Revenue (proxy)")
plt.title("D9 — Top Product Pairs by Revenue (Timestamp Baskets)")
plt.tight_layout(); plt.savefig(OUT, dpi=200, bbox_inches="tight")
