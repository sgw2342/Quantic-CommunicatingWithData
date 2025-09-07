
import sqlite3, pandas as pd, numpy as np, matplotlib.pyplot as plt
from pathlib import Path
BASE = Path("/mnt/data"); DB = BASE/"retail_demo.sqlite"; OUT = BASE/"ppt_assets"/"d7_heatmap_lower.png"
conn = sqlite3.connect(DB)
cat_hour = pd.read_sql_query("""
SELECT CAST(substr(t.transaction_time, 1, 2) AS INTEGER) AS hour,
       pc.product_category_type AS category,
       SUM(td.transaction_qty * COALESCE(td.unit_price, 0.0)) AS revenue
FROM transactions t
JOIN transaction_details td ON td.transaction_id = t.transaction_id
JOIN products p             ON p.product_id = td.product_id
JOIN product_categories pc  ON pc.product_category_id = p.product_category_id
WHERE t.store_id = (SELECT store_id FROM stores WHERE store_location = 'Lower Manhattan' LIMIT 1)
GROUP BY hour, category
""", conn); conn.close()
hours = pd.Index(range(24), name="hour")
heat = cat_hour.pivot(index="hour", columns="category", values="revenue").reindex(hours).fillna(0.0)
plt.figure(figsize=(13,6))
plt.imshow(heat.T.values, aspect="auto", interpolation="nearest"); plt.title("D7 — Lower Manhattan: Revenue Heatmap by Hour × Category")
plt.xlabel("Hour of Day (0–23)"); plt.ylabel("Product Category")
plt.xticks(ticks=np.arange(0,24,1), labels=[str(h) for h in range(24)]); plt.yticks(ticks=np.arange(len(heat.columns)), labels=list(heat.columns))
plt.colorbar(label="Revenue"); plt.tight_layout(); plt.savefig(OUT, dpi=200, bbox_inches="tight")
