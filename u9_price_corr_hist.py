
import sqlite3, pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize
from pathlib import Path

BASE = Path("/mnt/data"); DB = BASE/"retail_demo.sqlite"; OUT = BASE/"unified_assets"/"u9_price_corr_hist.png"
conn = sqlite3.connect(DB)
daily_prod = pd.read_sql_query("""
SELECT p.product_id, p.product_detail AS product_name, t.transaction_date AS tx_date,
       AVG(td.unit_price) AS avg_price, SUM(td.transaction_qty) AS qty
FROM transactions t
JOIN transaction_details td ON td.transaction_id = t.transaction_id
JOIN products p ON p.product_id = td.product_id
GROUP BY p.product_id, p.product_detail, t.transaction_date
""", conn); conn.close()

elig = (daily_prod.groupby(["product_id","product_name"]).agg(n_days=("tx_date","nunique"), n_prices=("avg_price","nunique")).reset_index())
eligible = elig[(elig["n_days"]>=14) & (elig["n_prices"]>=3)][["product_id","product_name"]]
merged = daily_prod.merge(eligible, on=["product_id","product_name"], how="inner")

rows = []
for pid, g in merged.groupby("product_id"):
    if g["avg_price"].nunique()>=3 and g["tx_date"].nunique()>=14:
        r = g["avg_price"].corr(g["qty"])
        if pd.notnull(r):
            rows.append((int(pid), g["product_name"].iloc[0], float(r)))
corr_df = pd.DataFrame(rows, columns=["product_id","product_name","price_qty_corr"]).dropna()

plt.figure(figsize=(9,5))
counts, bins, patches = plt.hist(corr_df["price_qty_corr"], bins=20)
norm = Normalize(vmin=np.min(counts), vmax=np.max(counts) if np.max(counts)>0 else 1.0)
for c, p in zip(counts, patches):
    p.set_facecolor(cm.Blues(norm(c)))
plt.title("U9 — Distribution of Price–Quantity Correlation (Eligible SKUs)")
plt.xlabel("Correlation (avg price vs total qty)"); plt.ylabel("# SKUs")
plt.tight_layout(); plt.savefig(OUT, dpi=200, bbox_inches="tight")
