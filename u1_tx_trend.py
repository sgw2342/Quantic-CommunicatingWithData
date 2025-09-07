
import sqlite3, pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib import cm
from pathlib import Path
BASE = Path("/mnt/data"); DB = BASE/"retail_demo.sqlite"; OUT = BASE/"unified_assets"/"u1_tx_trend.png"
conn = sqlite3.connect(DB)
df = pd.read_sql_query("""
SELECT t.transaction_id, s.store_location AS store, t.transaction_date AS tx_date
FROM transactions t JOIN stores s ON s.store_id = t.store_id
""", conn); conn.close()
df['tx_date'] = pd.to_datetime(df['tx_date'], errors='coerce')
daily = df.groupby(['tx_date','store'])['transaction_id'].nunique().reset_index(name='transactions')
daily['tx_7d'] = daily.groupby('store')['transactions'].transform(lambda s: s.rolling(7, min_periods=1).mean())
stores = daily['store'].unique().tolist()
colors = [cm.Blues(x) for x in np.linspace(0.35, 0.95, len(stores))]
plt.figure(figsize=(12,7))
for st, c in zip(stores, colors):
    sub = daily[daily['store']==st]; plt.plot(sub['tx_date'], sub['tx_7d'], label=st, color=c)
plt.title('U1 — Transactions (7‑day Rolling) by Store'); plt.xlabel('Date'); plt.ylabel('# Transactions')
plt.legend(); plt.grid(True, axis='y', linestyle='--', linewidth=0.5); plt.tight_layout(); plt.savefig(OUT, dpi=200, bbox_inches='tight')
