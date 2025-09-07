
import sqlite3, pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from matplotlib import cm
from pathlib import Path
BASE = Path("/mnt/data"); DB = BASE/"retail_demo.sqlite"; OUT = BASE/"ppt_assets"/"d6_hour_share.png"
conn = sqlite3.connect(DB)
df = pd.read_sql_query("""
SELECT s.store_location AS store, t.transaction_date AS tx_date,
       CAST(substr(t.transaction_time, 1, 2) AS INTEGER) AS hour,
       SUM(td.transaction_qty * COALESCE(td.unit_price, 0.0)) AS revenue
FROM stores s JOIN transactions t ON t.store_id = s.store_id
JOIN transaction_details td ON td.transaction_id = t.transaction_id
GROUP BY s.store_location, t.transaction_date, hour
""", conn); conn.close()
day_totals = df.groupby(['store','tx_date'])['revenue'].sum().rename('day_total').reset_index()
df = df.merge(day_totals, on=['store','tx_date'], how='left')
df['hour_share'] = (df['revenue']/df['day_total']).replace([np.inf,-np.inf,np.nan], 0.0)
piv = df.groupby(['hour','store'])['hour_share'].mean().unstack('store').reindex(range(24)).fillna(0.0)
colors = [cm.Blues(x) for x in np.linspace(0.35, 0.95, len(piv.columns))]
plt.figure(figsize=(12,7))
for st, c in zip(piv.columns, colors):
    plt.plot(piv.index, piv[st], marker='o', label=st, color=c)
plt.title('D6 — Avg Hourly Share of Daily Revenue (All Time)'); plt.xlabel('Hour of Day (0–23)'); plt.ylabel('Share of Daily Revenue')
plt.xticks(range(0,24,1)); plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))
plt.legend(); plt.grid(True, axis='y', linestyle='--', linewidth=0.5); plt.tight_layout(); plt.savefig(OUT, dpi=200, bbox_inches='tight')
