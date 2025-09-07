
import sqlite3, pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from pathlib import Path
BASE = Path("/mnt/data"); DB = BASE/"retail_demo.sqlite"; OUTDIR = BASE/"ppt_assets"
OUTDIR.mkdir(exist_ok=True, parents=True)
def safe_name(s): return s.replace(" ", "_").replace("'", "").replace("/", "_")
conn = sqlite3.connect(DB)
df = pd.read_sql_query("""
SELECT s.store_location AS store,
       CAST(substr(t.transaction_time, 1, 2) AS INTEGER) AS hour,
       pc.product_category_type AS category,
       SUM(td.transaction_qty * COALESCE(td.unit_price, 0.0)) AS revenue
FROM transactions t
JOIN stores s              ON s.store_id = t.store_id
JOIN transaction_details td ON td.transaction_id = t.transaction_id
JOIN products p            ON p.product_id = td.product_id
JOIN product_categories pc ON pc.product_category_id = p.product_category_id
GROUP BY s.store_location, hour, category
""", conn); conn.close()
vmax = float(df['revenue'].max()) if len(df) else 1.0
norm = Normalize(vmin=0.0, vmax=vmax)
kmax = int(np.floor(vmax/1000.0))
ticks = [0.0] + [1000.0*i for i in range(1, kmax+1)]
labels = [("0k" if t==0 else f"{int(t/1000)}k") for t in ticks]
for st, g in df.groupby("store"):
    heat = g.pivot(index="hour", columns="category", values="revenue").reindex(range(24)).fillna(0.0)
    plt.figure(figsize=(13,6))
    im = plt.imshow(heat.T.values, aspect="auto", interpolation="nearest", cmap="Blues", norm=norm)
    plt.title(f"D7 — {st}: Revenue Heatmap by Hour × Category (Global Scale)")
    plt.xlabel("Hour of Day (0–23)"); plt.ylabel("Product Category")
    plt.xticks(ticks=np.arange(0,24,1), labels=[str(h) for h in range(24)])
    plt.yticks(ticks=np.arange(len(heat.columns)), labels=list(heat.columns))
    cbar = plt.colorbar(im, label="Revenue (global scale)")
    cbar.set_ticks(ticks); cbar.set_ticklabels(labels)
    plt.tight_layout(); plt.savefig(OUTDIR/("d7_heatmap_" + safe_name(st) + ".png"), dpi=200, bbox_inches="tight"); plt.close()
