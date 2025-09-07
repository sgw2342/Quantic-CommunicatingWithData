
import sqlite3, pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from matplotlib import cm
from pathlib import Path
BASE = Path("/mnt/data"); DB = BASE/"retail_demo.sqlite"; OUT = BASE/"unified_assets"/"u7_pareto_tx.png"
conn = sqlite3.connect(DB)
df = pd.read_sql_query("""
SELECT p.product_id, p.product_detail AS product_name, COUNT(DISTINCT t.transaction_id) AS transactions
FROM transactions t
JOIN transaction_details td ON td.transaction_id = t.transaction_id
JOIN products p ON p.product_id = td.product_id
GROUP BY p.product_id, p.product_detail
""", conn); conn.close()
df = df.sort_values('transactions', ascending=False).reset_index(drop=True)
df['cum_tx'] = df['transactions'].cumsum(); df['cum_share'] = df['cum_tx']/df['transactions'].sum()
df['sku_pct'] = (np.arange(1, len(df)+1))/len(df)
x, y = df['sku_pct'].values, df['cum_share'].values
plt.figure(figsize=(9,6))
plt.plot(x, y, color=cm.Blues(0.85), marker='.'); plt.fill_between(x, 0, y, color=cm.Blues(0.4), alpha=0.2)
plt.axvline(0.2, linestyle='--', color=cm.Blues(0.6)); plt.axhline(0.8, linestyle='--', color=cm.Blues(0.6))
plt.title('U7 — SKU Pareto Curve (Cumulative Share of Transactions)'); plt.xlabel('% of SKUs'); plt.ylabel('Cumulative Share of Transactions')
plt.gca().xaxis.set_major_formatter(PercentFormatter(1.0)); plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))
plt.tight_layout(); plt.savefig(OUT, dpi=200, bbox_inches='tight')
