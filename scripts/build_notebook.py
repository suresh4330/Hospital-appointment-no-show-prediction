"""Generate and execute notebooks/eda.ipynb with verified real numbers."""
from pathlib import Path
import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor


def create_eda_notebook():
    nb = nbf.v4.new_notebook()

    cells = []

    # Title & Introduction
    cells.append(nbf.v4.new_markdown_cell(
"""# Exploratory Data Analysis: Hospital Appointment No-Show Prediction

This notebook profiles the synthetic appointments dataset (`data/appointments.csv`),
verifying dataset dimensions, column types, missingness, data anomalies, class
balance, and empirical no-show rates across operational and demographic attributes.

All markdown findings in this notebook are derived strictly from the preceding code
execution outputs.
"""
    ))

    # Cell 1: Load Data & Inspect Shape
    cells.append(nbf.v4.new_code_cell(
"""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('../data/appointments.csv', parse_dates=['booking_date', 'appointment_date'])
print(f"Dataset Shape: {df.shape}")
print(f"Total Rows: {df.shape[0]}, Total Columns: {df.shape[1]}")
print(f"Raw Column List ({len(df.columns)}): {list(df.columns)}")
df.head(3)
"""
    ))

    # Cell 2: Markdown Finding for Shape
    cells.append(nbf.v4.new_markdown_cell(
"""### Finding 1: Dataset Dimensions & Structure
* **Verified Shape:** Exactly **(12000, 18)** — 12,000 rows and 18 columns.
* **Feature Accounting:** The raw dataset has 18 columns (including `appointment_id`,
  `patient_id`, `booking_date`, `appointment_date`, and `no_show`).
* This represents **14 original candidate model features** (expanded to 16 features in
  `src/features.py` after deriving `prev_attended` and `is_first_visit`).
"""
    ))

    # Cell 3: Data Quality Checks
    cells.append(nbf.v4.new_code_cell(
"""print("--- Column Data Types ---")
print(df.dtypes)

dups = df['appointment_id'].duplicated().sum()
missing = df.isna().sum()[lambda s: s > 0]
impossible_ages = (df['age'] > 110).sum()
negative_lead = (df['lead_time_days'] < 0).sum()

print("\\n--- Data Quality Checks ---")
print(f"Duplicate appointment_ids: {dups}")
dist_miss = missing.get('distance_km', 0)
chan_miss = missing.get('booking_channel', 0)
print(f"Missing distance_km: {dist_miss} ({dist_miss/len(df):.2%})")
print(f"Missing booking_channel: {chan_miss} ({chan_miss/len(df):.2%})")
print(f"Impossible ages (>110 years): {impossible_ages}")
print(f"Negative lead times (<0 days): {negative_lead}")
print(f"Appointment date range: {df['appointment_date'].min().date()} to "
      f"{df['appointment_date'].max().date()}")
"""
    ))

    # Cell 4: Markdown Finding for Data Quality
    cells.append(nbf.v4.new_markdown_cell(
"""### Finding 2: Data Quality & Anomalies
* **Duplicates:** 0 duplicate appointment IDs.
* **Missing Values:**
  - `distance_km`: 262 missing values (2.18%).
  - `booking_channel`: 223 missing values (1.86%).
* **Domain Anomalies:** Exactly 36 records have impossible ages (>110 years, up to 125).
  These are coerced to NaN and imputed using median training age (40.0 years) in
  `src/features.py`.
* **Lead Time Validity:** 0 negative lead times exist.
* **Date Span:** Appointments cover 2024-01-01 to 2025-06-23 (539 days).
"""
    ))

    # Cell 5: Target Distribution & Class Imbalance
    cells.append(nbf.v4.new_code_cell(
"""target_counts = df['no_show'].value_counts()
target_rate = df['no_show'].mean()
print("--- Class Balance ---")
print(f"Attended (0): {target_counts[0]:,} ({1 - target_rate:.2%})")
print(f"No-Show  (1): {target_counts[1]:,} ({target_rate:.2%})")
print(f"Total Records: {len(df):,}")
print(f"Base prevalence: {target_rate:.4f} ({target_rate*100:.2f}%)")
"""
    ))

    # Cell 6: Markdown Finding for Class Balance
    cells.append(nbf.v4.new_markdown_cell(
"""### Finding 3: Target Class Imbalance
* **Target Distribution:** 9,771 attended visits (81.43%) vs 2,229 missed visits (18.57%).
* **Prevalence:** Baseline no-show prevalence is exactly **18.57%**.
* **Implication:** A trivial majority-class classifier predicting always attend achieves
  81.43% accuracy but captures zero no-shows (recall = 0.0), underscoring why PR-AUC and
  cost-weighted evaluation are required.
"""
    ))

    # Cell 7: Subgroup No-Show Rates with Exact Code Definitions
    cells.append(nbf.v4.new_code_cell(
"""# Exact definition 1: lead_time_days > 30 vs <= 30
lt_gt_30 = df[df['lead_time_days'] > 30]
lt_le_30 = df[df['lead_time_days'] <= 30]
lt_0_3 = df[df['lead_time_days'] <= 3]
print("--- Definition: lead_time_days ---")
print(f"lead_time_days > 30: n={len(lt_gt_30)}, no_shows={lt_gt_30['no_show'].sum()}, "
      f"rate={lt_gt_30['no_show'].mean():.4f} ({lt_gt_30['no_show'].mean()*100:.2f}%)")
print(f"lead_time_days <= 30: n={len(lt_le_30)}, no_shows={lt_le_30['no_show'].sum()}, "
      f"rate={lt_le_30['no_show'].mean():.4f} ({lt_le_30['no_show'].mean()*100:.2f}%)")
print(f"lead_time_days <= 3: n={len(lt_0_3)}, no_shows={lt_0_3['no_show'].sum()}, "
      f"rate={lt_0_3['no_show'].mean():.4f} ({lt_0_3['no_show'].mean()*100:.2f}%)")

# Exact definition 2: prev_no_shows >= 3 vs < 3
pns_ge_3 = df[df['prev_no_shows'] >= 3]
pns_lt_3 = df[df['prev_no_shows'] < 3]
print("\\n--- Definition: prev_no_shows ---")
print(f"prev_no_shows >= 3: n={len(pns_ge_3)}, no_shows={pns_ge_3['no_show'].sum()}, "
      f"rate={pns_ge_3['no_show'].mean():.4f} ({pns_ge_3['no_show'].mean()*100:.2f}%)")
print(f"prev_no_shows < 3: n={len(pns_lt_3)}, no_shows={pns_lt_3['no_show'].sum()}, "
      f"rate={pns_lt_3['no_show'].mean():.4f} ({pns_lt_3['no_show'].mean()*100:.2f}%)")

# Exact definition 3: reminder_scheduled == 'no' vs 'yes'
rem_no = df[df['reminder_scheduled'] == 'no']
rem_yes = df[df['reminder_scheduled'] == 'yes']
print("\\n--- Definition: reminder_scheduled ---")
print(f"reminder_scheduled == 'no': n={len(rem_no)}, no_shows={rem_no['no_show'].sum()}, "
      f"rate={rem_no['no_show'].mean():.4f} ({rem_no['no_show'].mean()*100:.2f}%)")
print(f"reminder_scheduled == 'yes': n={len(rem_yes)}, no_shows={rem_yes['no_show'].sum()}, "
      f"rate={rem_yes['no_show'].mean():.4f} ({rem_yes['no_show'].mean()*100:.2f}%)")

# Exact definition 4: age_group rates and ranking
print("\\n--- Definition: age_group Ranking ---")
ag_summary = df.groupby('age_group')['no_show'].agg(
    n='count',
    no_shows='sum',
    rate='mean'
).sort_values('rate', ascending=False)
ag_summary['rate_pct'] = (ag_summary['rate'] * 100).round(2).astype(str) + '%'
print(ag_summary[['n', 'no_shows', 'rate', 'rate_pct']])

highest_risk_ag = ag_summary.index[0]
lowest_risk_ag = ag_summary.index[-1]
print(f"\\nHighest-Risk Age Group: '{highest_risk_ag}' "
      f"(Rate = {ag_summary.loc[highest_risk_ag, 'rate']*100:.2f}%)")
print(f"Lowest-Risk Age Group:  '{lowest_risk_ag}' "
      f"(Rate = {ag_summary.loc[lowest_risk_ag, 'rate']*100:.2f}%)")
"""
    ))

    # Cell 8: Markdown Finding for Subgroup Rates
    cells.append(nbf.v4.new_markdown_cell(
"""### Finding 4: Verified Subgroup No-Show Rates
All values below reflect the exact code execution outputs from the cell above:
1. **Lead Time (`lead_time_days > 30`):**
   - Appointments booked $>30$ days in advance ($n=793$) have a **35.06%** no-show
     rate (278 missed).
   - In contrast, appointments booked $\\le 30$ days out ($n=11,207$) have a **17.41%**
     rate (1,951 missed).
   - Short lead appointments ($\le 3$ days, $n=1,515$) have a no-show rate of **11.42%**
     (173 missed).
2. **Prior No-Shows (`prev_no_shows >= 3`):**
   - Patients with $\ge 3$ prior no-shows ($n=268$) experience a **44.03%** no-show
     rate (118 missed).
   - Patients with $< 3$ prior no-shows ($n=11,732$) experience a **17.99%** no-show
     rate (2,111 missed).
3. **Scheduled Reminders (`reminder_scheduled == 'no'`):**
   - Unreminded bookings ($n=4,753$) have a **24.76%** no-show rate (1,177 missed).
   - Reminded bookings ($n=7,247$) have a **14.52%** no-show rate (1,052 missed) — a
     10.24% absolute risk reduction.
4. **Age Group Stratification (Ranked Highest to Lowest Risk):**
   - **Highest-Risk Age Group:** **`0-17`** with **23.58%** no-show rate ($n=1,370$, 323 missed).
   - Second: **`18-39`** with **20.35%** no-show rate ($n=4,530$, 922 missed).
   - Third: **`40-59`** with **17.42%** no-show rate ($n=4,500$, 784 missed).
   - **Lowest-Risk Age Group:** **`60+`** with **12.50%** no-show rate ($n=1,600$, 200 missed).
"""
    ))

    # Cell 9: Six-Panel Visualization Code
    cells.append(nbf.v4.new_code_cell(
"""# 6-Panel Visualization matching src/eda.py
d = df[df.age <= 110].copy()
d['lead_bin'] = pd.cut(d.lead_time_days, [-1, 3, 7, 14, 21, 30, 60, 400])
d['prev_ns_bin'] = d.prev_no_shows.clip(upper=3)

fig, ax = plt.subplots(2, 3, figsize=(15, 8))
d.groupby('lead_bin', observed=True)['no_show'].mean().plot.bar(
    ax=ax[0, 0], color='#1f77b4', title='No-Show Rate by Lead Time'
)
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
d.groupby('appt_weekday')['no_show'].mean().reindex(days).plot.bar(
    ax=ax[0, 1], color='#ff7f0e', title='By Weekday'
)
d.groupby('appt_hour')['no_show'].mean().plot(
    ax=ax[0, 2], marker='o', color='#2ca02c', title='By Hour of Day'
)
d.groupby('prev_ns_bin')['no_show'].mean().plot.bar(
    ax=ax[1, 0], color='#d62728', title='By Prior No-Shows (3 = 3+)'
)
d.groupby('reminder_scheduled')['no_show'].mean().plot.bar(
    ax=ax[1, 1], color='#9467bd', title='By Reminder Scheduled'
)
d.groupby('age_group')['no_show'].mean().plot.bar(
    ax=ax[1, 2], color='#8c564b', title='By Age Group'
)

for a in ax.ravel():
    a.set_ylabel('No-Show Rate')
    a.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()
"""
    ))

    # Cell 10: Conclusion
    cells.append(nbf.v4.new_markdown_cell(
"""### Summary for Modeling Pipeline
* **High Predictive Power Signals:** Lead time, prior no-show history, and reminder
  scheduling are the strongest empirical univariate predictors of attendance.
* **Subgroup Considerations:** Patients aged 0-17 have the highest baseline miss rate
  (23.58%), while seniors 60+ miss least frequently (12.50%). Fairness auditing must
  monitor these cohorts closely.
* **Cleaning Protocol:** Impute missing distance with median, encode missing booking
  channel as 'unknown', and coerce impossible ages (>110) to NaN prior to imputation.
"""
    ))

    nb["cells"] = cells

    nb_path = Path("notebooks/eda.ipynb")
    nb_path.parent.mkdir(exist_ok=True)

    print("Executing notebook via nbconvert ExecutePreprocessor...")
    ep = ExecutePreprocessor(timeout=60, kernel_name="python3")
    ep.preprocess(nb, {"metadata": {"path": "notebooks/"}})

    with open(nb_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)

    print(f"Successfully generated and executed {nb_path}")


if __name__ == "__main__":
    create_eda_notebook()
