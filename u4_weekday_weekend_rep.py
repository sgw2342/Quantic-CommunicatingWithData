
import sqlite3, pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib import cm
from pathlib import Path
BASE = Path("/mnt/data"); DB = BASE/"retail_demo.sqlite"; OUT = BASE/"unified_assets"/"u4_weekday_weekend_rep.png"
conn = sqlite3.connect(DB)
df = pd.read_sql_query("""
SELECT s.store_location AS store, t.transaction_date AS tx_date, CAST(substr(t.transaction_time, 1, 2) AS INTEGER) AS hour, t.transaction_id
FROM transactions t JOIN stores s ON s.store_id = t.store_id
""", conn); conn.close()
df['tx_date'] = pd.to_datetime(df['tx_date'], errors='coerce')
df['is_weekend'] = df['tx_date'].dt.dayofweek >= 5
rep_store = "Hell's Kitchen" if (df['store']=='Hell\'s Kitchen').any() else df['store'].iloc[0]
sub = df[df['store']==rep_store].groupby(['is_weekend','hour'])['transaction_id'].nunique().unstack('is_weekend').reindex(range(24)).fillna(0.0)
plt.figure(figsize=(12,6))
plt.plot(sub.index, sub.get(False, pd.Series(index=range(24))).values, marker='o', label='Weekday', color=cm.Blues(0.8))
plt.plot(sub.index, sub.get(True, pd.Series(index=range(24))).values, marker='o', label='Weekend', color=cm.Blues(0.5))
plt.title(f'U4 — {rep_store}: Weekday vs Weekend Transactions by Hour'); plt.xlabel('Hour of Day (0–23)'); plt.ylabel('# Transactions')
plt.xticks(range(0,24,1)); plt.legend(); plt.grid(True, axis='y', linestyle='--', linewidth=0.5); plt.tight_layout(); plt.savefig(OUT, dpi=200, bbox_inches='tight')
