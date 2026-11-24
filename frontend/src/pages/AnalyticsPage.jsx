import React, { useEffect, useState } from 'react';
import { BarChart3, CheckCircle2, ShieldAlert, Award } from 'lucide-react';
import { getMetadata, checkHealth } from '../services/api';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';

export function AnalyticsPage() {
  const [meta, setMeta] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metaData, healthData] = await Promise.all([
          getMetadata().catch(() => null),
          checkHealth().catch(() => null),
        ]);
        setMeta(metaData);
        setHealth(healthData);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const testMetrics = meta?.test_metrics || {
    threshold: 0.16,
    precision: 0.308988,
    recall: 0.811209,
    f1: 0.447518,
    pr_auc: 0.465708,
    brier: 0.128157,
    tn: 846,
    fp: 615,
    fn: 64,
    tp: 275,
    expected_cost: 1870.0,
  };

  return (
    <div className="space-y-4">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-teal-600" />
            Model Intelligence & Fairness Audit
          </h1>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
            Verified champion model metrics, asymmetric cost curve, and responsible AI demographic audits.
          </p>
        </div>

        <div>
          <Badge variant="teal" size="sm">
            Model: Logistic Regression + Isotonic Calibration
          </Badge>
        </div>
      </div>

      {/* KPI Cards Ribbon */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <Card className="p-3">
          <div className="text-[10px] text-slate-600 dark:text-slate-400 uppercase font-bold tracking-wider">
            Decision Threshold
          </div>
          <div className="text-xl font-black text-teal-700 dark:text-teal-400 mt-1">
            {meta?.threshold || 0.16}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Cost-optimal (10:2)</div>
        </Card>

        <Card className="p-3">
          <div className="text-[10px] text-slate-600 dark:text-slate-400 uppercase font-bold tracking-wider">
            Recall (Miss Catch)
          </div>
          <div className="text-xl font-black text-slate-900 dark:text-slate-100 mt-1">
            {(testMetrics.recall * 100).toFixed(1)}%
          </div>
          <div className="text-[10px] text-emerald-600 font-semibold mt-0.5">275 of 339 caught</div>
        </Card>

        <Card className="p-3">
          <div className="text-[10px] text-slate-600 dark:text-slate-400 uppercase font-bold tracking-wider">
            Precision
          </div>
          <div className="text-xl font-black text-slate-900 dark:text-slate-100 mt-1">
            {(testMetrics.precision * 100).toFixed(1)}%
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">30.9% confirmed misses</div>
        </Card>

        <Card className="p-3">
          <div className="text-[10px] text-slate-600 dark:text-slate-400 uppercase font-bold tracking-wider">
            F1-Score
          </div>
          <div className="text-xl font-black text-slate-900 dark:text-slate-100 mt-1">
            {testMetrics.f1.toFixed(3)}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Harmonic mean</div>
        </Card>

        <Card className="p-3">
          <div className="text-[10px] text-slate-600 dark:text-slate-400 uppercase font-bold tracking-wider">
            PR-AUC
          </div>
          <div className="text-xl font-black text-slate-900 dark:text-slate-100 mt-1">
            {testMetrics.pr_auc.toFixed(3)}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">vs 0.188 baseline</div>
        </Card>

        <Card className="p-3">
          <div className="text-[10px] text-slate-600 dark:text-slate-400 uppercase font-bold tracking-wider">
            Brier Score
          </div>
          <div className="text-xl font-black text-slate-900 dark:text-slate-100 mt-1">
            {testMetrics.brier.toFixed(3)}
          </div>
          <div className="text-[10px] text-teal-600 font-semibold mt-0.5">Calibrated probability</div>
        </Card>
      </div>

      {/* Confusion Matrix and Business Cost Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Confusion Matrix */}
        <div className="lg:col-span-6">
          <Card
            title="Test Set Confusion Matrix (n = 1,800)"
            subtitle="Evaluated on untouched chronological test split (Feb 2025 – Jun 2025)"
          >
            <div className="grid grid-cols-2 gap-2.5 p-3 bg-slate-50 dark:bg-slate-950/60 rounded-xl border border-slate-200 dark:border-slate-800">
              <div className="p-3.5 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">True Negatives (TN)</span>
                <div className="text-2xl font-black text-slate-900 dark:text-slate-100 mt-1">{testMetrics.tn}</div>
                <p className="text-[10px] text-slate-500 mt-0.5">Attended, unflagged</p>
              </div>

              <div className="p-3.5 rounded-lg bg-white dark:bg-slate-900 border border-amber-200 dark:border-amber-900/40 text-center">
                <span className="text-[10px] font-bold text-amber-600 uppercase tracking-wider">False Positives (FP)</span>
                <div className="text-2xl font-black text-amber-600 mt-1">{testMetrics.fp}</div>
                <p className="text-[10px] text-slate-500 mt-0.5">Attended, reminded</p>
              </div>

              <div className="p-3.5 rounded-lg bg-white dark:bg-slate-900 border border-rose-200 dark:border-rose-900/40 text-center">
                <span className="text-[10px] font-bold text-rose-600 uppercase tracking-wider">False Negatives (FN)</span>
                <div className="text-2xl font-black text-rose-600 mt-1">{testMetrics.fn}</div>
                <p className="text-[10px] text-slate-500 mt-0.5">Missed, lost slot</p>
              </div>

              <div className="p-3.5 rounded-lg bg-white dark:bg-slate-900 border border-emerald-200 dark:border-emerald-900/40 text-center">
                <span className="text-[10px] font-bold text-emerald-600 uppercase tracking-wider">True Positives (TP)</span>
                <div className="text-2xl font-black text-emerald-600 mt-1">{testMetrics.tp}</div>
                <p className="text-[10px] text-slate-500 mt-0.5">Missed, flagged</p>
              </div>
            </div>

            <p className="mt-3 text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              Operating threshold locked at <strong>0.16</strong> catches <strong>81.1% of all missed appointments</strong> (275/339),
              keeping unflagged missed appointments down to just 64.
            </p>
          </Card>
        </div>

        {/* Expected Business Cost */}
        <div className="lg:col-span-6">
          <Card
            title="Expected Business Cost Comparison"
            subtitle="Asymmetric clinical cost formula: Cost = (FN × 10.0) + (FP × 2.0)"
          >
            <div className="space-y-2.5">
              <div className="p-3 rounded-lg border border-teal-200 dark:border-teal-800 bg-teal-50/70 dark:bg-teal-950/40 flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-teal-900 dark:text-teal-200 flex items-center gap-1">
                    <Award className="w-3.5 h-3.5 text-teal-600" />
                    Champion (LogReg + Isotonic @ 0.16)
                  </div>
                  <div className="text-[11px] text-slate-600 dark:text-slate-400">
                    64 FN × 10 + 615 FP × 2
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-black text-teal-800 dark:text-teal-300">1,870.0</div>
                  <div className="text-[10px] font-semibold text-emerald-600">Lowest Total Cost</div>
                </div>
              </div>

              <div className="p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 flex items-center justify-between">
                <div>
                  <div className="text-xs font-semibold text-slate-800 dark:text-slate-200">
                    Heuristic Rule (lead &gt; 30d or past miss &ge; 1)
                  </div>
                  <div className="text-[11px] text-slate-500">144 FN × 10 + 417 FP × 2</div>
                </div>
                <div className="text-right">
                  <div className="text-base font-bold text-slate-700 dark:text-slate-300">2,274.0</div>
                  <div className="text-[10px] text-rose-500">+21.6% higher</div>
                </div>
              </div>

              <div className="p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 flex items-center justify-between">
                <div>
                  <div className="text-xs font-semibold text-slate-800 dark:text-slate-200">
                    Flag-Everyone (Blanket Reminders)
                  </div>
                  <div className="text-[11px] text-slate-500">0 FN × 10 + 1,461 FP × 2</div>
                </div>
                <div className="text-right">
                  <div className="text-base font-bold text-slate-700 dark:text-slate-300">2,922.0</div>
                  <div className="text-[10px] text-rose-500">+56.2% higher</div>
                </div>
              </div>
            </div>

            <p className="text-xs text-slate-600 dark:text-slate-400 mt-3 leading-relaxed">
              Model optimization saves <strong>404 cost units (17.8%)</strong> relative to manual clinic rules while preventing staff reminder fatigue.
            </p>
          </Card>
        </div>
      </div>

      {/* Subgroup Fairness Table */}
      <Card
        title="Subgroup Fairness & Demographic Audit"
        subtitle="Verification across protected demographic cohorts on the test split"
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 dark:bg-slate-950/40 text-slate-700 dark:text-slate-300 font-semibold border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th className="py-2 px-3">Demographic Group</th>
                <th className="py-2 px-3">Sample (n)</th>
                <th className="py-2 px-3">Observed Miss Rate</th>
                <th className="py-2 px-3">Flag Rate</th>
                <th className="py-2 px-3">Precision</th>
                <th className="py-2 px-3">Recall</th>
                <th className="py-2 px-3">Audit Outcome</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              <tr>
                <td className="py-2 px-3 font-semibold text-slate-900 dark:text-slate-100">Age: 0–17</td>
                <td className="py-2 px-3">208</td>
                <td className="py-2 px-3">26.9%</td>
                <td className="py-2 px-3">63.0%</td>
                <td className="py-2 px-3">38.9%</td>
                <td className="py-2 px-3 font-bold text-emerald-600">91.1%</td>
                <td className="py-2 px-3"><Badge variant="teal" size="xs">High Protection</Badge></td>
              </tr>
              <tr>
                <td className="py-2 px-3 font-semibold text-slate-900 dark:text-slate-100">Age: 18–39</td>
                <td className="py-2 px-3">663</td>
                <td className="py-2 px-3">20.5%</td>
                <td className="py-2 px-3">55.5%</td>
                <td className="py-2 px-3">32.9%</td>
                <td className="py-2 px-3 font-bold text-emerald-600">89.0%</td>
                <td className="py-2 px-3"><Badge variant="teal" size="xs">Equitable</Badge></td>
              </tr>
              <tr>
                <td className="py-2 px-3 font-semibold text-slate-900 dark:text-slate-100">Age: 40–59</td>
                <td className="py-2 px-3">670</td>
                <td className="py-2 px-3">17.3%</td>
                <td className="py-2 px-3">46.9%</td>
                <td className="py-2 px-3">28.0%</td>
                <td className="py-2 px-3 font-bold text-emerald-600">75.9%</td>
                <td className="py-2 px-3"><Badge variant="teal" size="xs">Equitable</Badge></td>
              </tr>
              <tr>
                <td className="py-2 px-3 font-semibold text-slate-900 dark:text-slate-100">Age: 60+ (Seniors)</td>
                <td className="py-2 px-3">259</td>
                <td className="py-2 px-3">12.0%</td>
                <td className="py-2 px-3">29.7%</td>
                <td className="py-2 px-3">19.5%</td>
                <td className="py-2 px-3 font-bold text-amber-600">48.4%</td>
                <td className="py-2 px-3"><Badge variant="medium" size="xs">Recall Disparity</Badge></td>
              </tr>
              <tr className="bg-slate-50/50 dark:bg-slate-900/50">
                <td className="py-2 px-3 font-semibold text-slate-900 dark:text-slate-100">Gender: Female</td>
                <td className="py-2 px-3">904</td>
                <td className="py-2 px-3">17.3%</td>
                <td className="py-2 px-3">47.5%</td>
                <td className="py-2 px-3">29.1%</td>
                <td className="py-2 px-3 font-bold text-emerald-600">80.1%</td>
                <td className="py-2 px-3"><Badge variant="low" size="xs">Parity</Badge></td>
              </tr>
              <tr className="bg-slate-50/50 dark:bg-slate-900/50">
                <td className="py-2 px-3 font-semibold text-slate-900 dark:text-slate-100">Gender: Male</td>
                <td className="py-2 px-3">896</td>
                <td className="py-2 px-3">20.4%</td>
                <td className="py-2 px-3">51.5%</td>
                <td className="py-2 px-3">32.5%</td>
                <td className="py-2 px-3 font-bold text-emerald-600">82.0%</td>
                <td className="py-2 px-3"><Badge variant="low" size="xs">Parity</Badge></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="mt-3 p-3 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl text-xs text-slate-600 dark:text-slate-400">
          <strong className="text-slate-800 dark:text-slate-200">Mitigation Protocol:</strong> Older demographics (60+) miss appointments significantly less often (12.0%) and have lower prior missed visits, leading to fewer automated flags (recall 48.4%). Standard clinic reminder policies should remain active for all seniors.
        </div>
      </Card>
    </div>
  );
}
