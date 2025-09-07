
import sqlite3, pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from matplotlib import cm
from pathlib import Path

BASE = Path("/mnt/data"); DB = BASE/"retail_demo.sqlite"; OUT = BASE/"unified_assets"/"u5_share_multi_units.png"
conn = sqlite3.connect(DB)
df = pd.read_sql_query("""
SELECT s.store_location AS store, t.transaction_date AS tx_date, t.transaction_time AS tx_time,
       t.transaction_id, td.transaction_qty AS qty
FROM transactions t
JOIN stores s               ON s.store_id = t.store_id
JOIN transaction_details td ON td.transaction_id = t.transaction_id
""", conn); conn.close()

tx_level = (df.groupby(["store","transaction_id"], as_index=False)["qty"].sum()
              .assign(multi_tx=lambda d: d["qty"]>=2))
tx_summary = (tx_level.groupby("store", as_index=False)
              .agg(transactions=("transaction_id","nunique"),
                   multi_tx=("multi_tx","sum")))
tx_summary["share_multi_tx"] = tx_summary["multi_tx"] / tx_summary["transactions"]

df["event_id"] = df["store"].astype(str) + "|" + df["tx_date"].astype(str) + "|" + df["tx_time"].astype(str)
event_level = df.groupby(["store","event_id"], as_index=False)["qty"].sum().rename(columns={"qty":"units"})
event_summary = (event_level.assign(multi_event=lambda d: d["units"]>=2)
                 .groupby("store", as_index=False)
                 .agg(events=("event_id","nunique"),
                      multi_events=("multi_event","sum")))
event_summary["share_multi_event"] = event_summary["multi_events"] / event_summary["events"]

res = pd.merge(tx_summary[["store","share_multi_tx"]],
               event_summary[["store","share_multi_event"]],
               on="store", how="outer").fillna(0.0)

stores = res["store"].tolist(); x = np.arange(len(stores)); w = 0.38
plt.figure(figsize=(12,6))
plt.bar(x - w/2, res["share_multi_tx"].values, width=w, label="Per Transaction (qty≥2)", color=cm.Blues(0.55), edgecolor="none")
plt.bar(x + w/2, res["share_multi_event"].values, width=w, label="Per Event (timestamp basket units≥2)", color=cm.Blues(0.85), edgecolor="none")
plt.title("U5 — Share of Multi-Item Activity by Store\n(Per-Transaction vs Timestamp-Collision Events)")
plt.xticks(x, stores, rotation=0); plt.ylabel("Share"); plt.xlabel("Store")
plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0)); plt.legend(frameon=False)
plt.tight_layout(); plt.savefig(OUT, dpi=200, bbox_inches="tight")
