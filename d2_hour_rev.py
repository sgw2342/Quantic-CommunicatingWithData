
import sqlite3, pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib import cm
from pathlib import Path
BASE = Path("/mnt/data"); DB = BASE/"retail_demo.sqlite"; OUT = BASE/"ppt_assets"/"d2_hour_rev.png"
conn = sqlite3.connect(DB)
df = pd.read_sql_query("""
SELECT s.store_location AS store, CAST(substr(t.transaction_time, 1, 2) AS INTEGER) AS hour,
       SUM(td.transaction_qty * COALESCE(td.unit_price, 0.0)) AS revenue
FROM stores s JOIN transactions t ON t.store_id = s.store_id
JOIN transaction_details td ON td.transaction_id = t.transaction_id
GROUP BY s.store_location, hour
""", conn); conn.close()
piv = df.groupby(['hour','store'])['revenue'].sum().unstack('store').reindex(range(24)).fillna(0.0)
colors = [cm.Blues(x) for x in np.linspace(0.35, 0.95, len(piv.columns))]
plt.figure(figsize=(12,7))
for st, c in zip(piv.columns, colors):
    plt.plot(piv.index, piv[st], marker='o', label=st, color=c)
plt.title('D2 — Total Revenue by Time of Day per Store (All Time)'); plt.xlabel('Hour of Day (0–23)'); plt.ylabel('Revenue')
plt.xticks(range(0,24,1)); plt.legend(); plt.grid(True, axis='y', linestyle='--', linewidth=0.5); plt.tight_layout(); plt.savefig(OUT, dpi=200, bbox_inches='tight')
