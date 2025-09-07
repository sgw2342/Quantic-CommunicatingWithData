
import sqlite3, pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib import cm
from pathlib import Path
BASE = Path("/mnt/data"); DB = BASE/"retail_demo.sqlite"; OUT = BASE/"unified_assets"/"u3_hour_tx.png"
conn = sqlite3.connect(DB)
df = pd.read_sql_query("""
SELECT s.store_location AS store, CAST(substr(t.transaction_time, 1, 2) AS INTEGER) AS hour, t.transaction_id
FROM transactions t JOIN stores s ON s.store_id = t.store_id
""", conn); conn.close()
piv = df.groupby(['hour','store'])['transaction_id'].nunique().unstack('store').reindex(range(24)).fillna(0.0)
colors = [cm.Blues(x) for x in np.linspace(0.35, 0.95, len(piv.columns))]
plt.figure(figsize=(12,7))
for st, c in zip(piv.columns, colors):
    plt.plot(piv.index, piv[st], marker='o', label=st, color=c)
plt.title('U3 — Avg Transactions by Hour (All Time, per Store)'); plt.xlabel('Hour of Day (0–23)'); plt.ylabel('# Transactions')
plt.xticks(range(0,24,1)); plt.legend(); plt.grid(True, axis='y', linestyle='--', linewidth=0.5); plt.tight_layout(); plt.savefig(OUT, dpi=200, bbox_inches='tight')
