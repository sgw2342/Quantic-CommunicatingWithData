
import sqlite3, pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from matplotlib import cm
from matplotlib.colors import Normalize
from pathlib import Path
BASE = Path("/mnt/data"); DB = BASE/"retail_demo.sqlite"; OUTDIR = BASE/"unified_assets"
OUTDIR.mkdir(exist_ok=True, parents=True)
def safe_name(s): return s.replace(" ", "_").replace("'", "").replace("/", "_")
conn = sqlite3.connect(DB)
df = pd.read_sql_query("""
SELECT s.store_location AS store, pc.product_category_type AS category, COUNT(DISTINCT t.transaction_id) AS transactions
FROM transactions t
JOIN stores s ON s.store_id = t.store_id
JOIN transaction_details td ON td.transaction_id = t.transaction_id
JOIN products p ON p.product_id = td.product_id
JOIN product_categories pc ON pc.product_category_id = p.product_category_id
GROUP BY s.store_location, pc.product_category_type
""", conn); conn.close()
tot = df.groupby('store')['transactions'].sum().rename('store_tx').reset_index()
df = df.merge(tot, on='store', how='left'); df['tx_share'] = np.where(df['store_tx']>0, df['transactions']/df['store_tx'], 0.0)
for st, g in df.groupby('store'):
    g2 = g.sort_values('tx_share', ascending=True); vals = g2['tx_share'].values
    import numpy as np
    from matplotlib.colors import Normalize
    colors = cm.Blues(Normalize(vmin=float(vals.min()), vmax=float(vals.max()) if vals.max()>vals.min() else float(vals.min())+1.0)(vals))
    plt.figure(figsize=(10, max(4, 0.4*len(g2))))
    plt.barh(g2['category'], vals, color=colors, edgecolor='none')
    plt.gca().xaxis.set_major_formatter(PercentFormatter(1.0))
    plt.title(f"U6 — {st}: Category Share of Transactions"); plt.xlabel("Share of Store Transactions")
    plt.tight_layout(); plt.savefig(OUTDIR/("u6_cat_share_" + safe_name(st) + ".png"), dpi=200, bbox_inches='tight'); plt.close()
