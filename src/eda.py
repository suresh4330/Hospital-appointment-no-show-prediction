"""EDA + data-quality report.  python -m src.eda   ->  reports/eda_*.png, reports/data_quality.txt
(Paste/convert these cells into notebooks/eda.ipynb with Jupyter if you want a notebook.)"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from src.config import DATA_PATH, REPORTS, TARGET

def main():
    REPORTS.mkdir(exist_ok=True)
    df = pd.read_csv(DATA_PATH, parse_dates=["booking_date", "appointment_date"])
    q = []
    dups = df.appointment_id.duplicated().sum()
    q.append(f"rows={len(df)}  columns={df.shape[1]}  duplicates(appointment_id)={dups}")
    q.append(f"no-show rate = {df[TARGET].mean():.2%}  (class imbalance)")
    q.append("missing values:\n" + df.isna().sum()[lambda s: s > 0].to_string())
    q.append(f"impossible ages (>110): {(df.age > 110).sum()} | "
             f"negative lead time: {(df.lead_time_days < 0).sum()}")
    q.append(f"date range: {df.appointment_date.min().date()} -> {df.appointment_date.max().date()}")
    (REPORTS / "data_quality.txt").write_text("\n\n".join(q))
    print("\n\n".join(q))
    d = df[df.age <= 110].copy()
    d["lead_bin"] = pd.cut(d.lead_time_days, [-1, 3, 7, 14, 21, 30, 60, 400])
    d["prev_ns_bin"] = d.prev_no_shows.clip(upper=3)
    fig, ax = plt.subplots(2, 3, figsize=(15, 8))
    d.groupby("lead_bin", observed=True)[TARGET].mean().plot.bar(
        ax=ax[0, 0], title="No-show rate by lead time")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    d.groupby("appt_weekday")[TARGET].mean().reindex(days).plot.bar(ax=ax[0, 1], title="by weekday")
    d.groupby("appt_hour")[TARGET].mean().plot(ax=ax[0, 2], marker="o", title="by hour")
    d.groupby("prev_ns_bin")[TARGET].mean().plot.bar(ax=ax[1, 0], title="by previous no-shows (3 = 3+)")
    d.groupby("reminder_scheduled")[TARGET].mean().plot.bar(ax=ax[1, 1], title="by reminder scheduled")
    d.groupby("age_group")[TARGET].mean().plot.bar(ax=ax[1, 2], title="by age group")
    for a in ax.ravel():
        a.set_ylabel("no-show rate")
    fig.tight_layout(); fig.savefig(REPORTS / "eda_no_show_rates.png", dpi=120)
    print("saved reports/eda_no_show_rates.png")

if __name__ == "__main__":
    main()

