
import sqlite3, pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib import cm
from pathlib import Path
BASE = Path("/mnt/data"); DB = BASE/"retail_demo.sqlite"; OUT = BASE/"ppt_assets"/"d8_sim.png"
conn = sqlite3.connect(DB)
line_items = pd.read_sql_query("""
SELECT t.transaction_id, s.store_location AS store, pc.product_category_type AS category,
       (td.transaction_qty * COALESCE(td.unit_price, 0.0)) AS revenue
FROM transactions t
JOIN stores s              ON s.store_id = t.store_id
JOIN transaction_details td ON td.transaction_id = t.transaction_id
JOIN products p            ON p.product_id = td.product_id
JOIN product_categories pc ON pc.product_category_id = p.product_category_id
""", conn); conn.close()
base = line_items.groupby('store', as_index=False)['revenue'].sum().rename(columns={'revenue':'baseline'})
cat = line_items.groupby(['store','category'], as_index=False)['revenue'].sum().rename(columns={'revenue':'cat_rev'})
df = cat.merge(base, on='store', how='left'); df['share'] = np.where(df['baseline']>0, df['cat_rev']/df['baseline'], 0.0)
cand = []
for st, g in df.groupby('store'):
    pcut = np.percentile(g['cat_rev'], 10) if len(g) else 0.0
    cand.append(g[(g['share']<0.02) & (g['cat_rev']<=pcut)])
cand = pd.concat(cand, ignore_index=True) if cand else pd.DataFrame(columns=df.columns)
def attached_loss_component(store, category):
    tx = line_items[(line_items['store']==store) & (line_items['category']==category)]['transaction_id'].drop_duplicates()
    if tx.empty: return 0.0
    attach = line_items[(line_items['store']==store) & (line_items['transaction_id'].isin(tx)) & (line_items['category']!=category)]['revenue'].sum()
    return float(attach) * 0.30
rows = []
for _, r in cand.iterrows():
    st, direct, baseline = r['store'], float(r['cat_rev']), float(base[base['store']==r['store']]['baseline'].iloc[0])
    attach_loss = attached_loss_component(st, r['category']); sub_recovery = direct * 0.20
    rows.append({'store':st, 'baseline':baseline, 'after':baseline - direct - attach_loss + sub_recovery})
if rows:
    plot = pd.DataFrame(rows).groupby('store', as_index=False).agg(baseline=('baseline','first'), after=('after','first'))
    x = np.arange(len(plot)); w = 0.35; plt.figure(figsize=(9,6))
    plt.bar(x - w/2, plot['baseline'], w, label='Baseline', color=cm.Blues(0.6))
    plt.bar(x + w/2, plot['after'], w, label='After (Balanced)', color=cm.Blues(0.85))
    plt.xticks(x, plot['store']); plt.title('Simulated Removal Impact (Balanced Scenario)'); plt.ylabel('Revenue'); plt.legend()
    plt.tight_layout(); plt.savefig(OUT, dpi=200, bbox_inches='tight')
