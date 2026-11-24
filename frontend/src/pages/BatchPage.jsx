import React, { useState, useEffect } from 'react';
import { Table, Search, Download, PhoneCall, CheckCircle, RefreshCw, ChevronDown } from 'lucide-react';
import { predictBatch } from '../services/api';
import { useToast } from '../context/ToastContext';
import { MOCK_CLINIC_DAY } from '../data/presets';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';

export function BatchPage() {
  const { success, error: toastError } = useToast();
  const [appointments] = useState(MOCK_CLINIC_DAY);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('ALL');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [actionsTaken, setActionsTaken] = useState({});

  const runBatchPrediction = async (dataList) => {
    setLoading(true);
    try {
      const payload = dataList.map(({ patient_name, ...rest }) => rest);
      const res = await predictBatch(payload);

      const ranked = res.ranked_by_risk || [];
      const combined = ranked.map((item) => {
        const orig = dataList[item.index] || {};
        return {
          ...item,
          patient_name: orig.patient_name || `Patient #${item.index + 1}`,
          department: orig.department,
          appt_hour: orig.appt_hour,
          appt_weekday: orig.appt_weekday,
          lead_time_days: orig.lead_time_days,
          reminder_scheduled: orig.reminder_scheduled,
        };
      });

      setResults(combined);
      success(`Triage queue ranked (${combined.length} appointments)`);
    } catch (err) {
      toastError(err.message || 'Batch prediction failed.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runBatchPrediction(appointments);
  }, []);

  const toggleAction = (idx, actionType) => {
    setActionsTaken((prev) => {
      const current = prev[idx] || {};
      return {
        ...prev,
        [idx]: {
          ...current,
          [actionType]: !current[actionType],
        },
      };
    });
  };

  const handleExportCSV = () => {
    if (!results.length) return;
    const headers = ['Index', 'Patient Name', 'Department', 'Hour', 'Lead Days', 'No-Show Probability', 'Risk Band', 'Flagged', 'Call Completed', 'SMS Sent'];
    const rows = results.map((r) => [
      r.index,
      `"${r.patient_name}"`,
      r.department,
      r.appt_hour,
      r.lead_time_days,
      (r.no_show_probability * 100).toFixed(1) + '%',
      r.risk_band,
      r.flagged_for_review ? 'YES' : 'NO',
      actionsTaken[r.index]?.call ? 'YES' : 'NO',
      actionsTaken[r.index]?.sms ? 'YES' : 'NO',
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `clinic_triage_queue_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    success('Exported triage queue CSV.');
  };

  const filtered = results.filter((item) => {
    const matchesSearch =
      item.patient_name.toLowerCase().includes(search.toLowerCase()) ||
      item.department.toLowerCase().includes(search.toLowerCase());
    const matchesDept = deptFilter === 'ALL' || item.department === deptFilter;
    const matchesRisk = riskFilter === 'ALL' || item.risk_band.toLowerCase() === riskFilter.toLowerCase();
    return matchesSearch && matchesDept && matchesRisk;
  });

  const totalCount = results.length;
  const highRiskCount = results.filter((r) => r.risk_band === 'high').length;
  const mediumRiskCount = results.filter((r) => r.risk_band === 'medium').length;
  const flaggedCount = results.filter((r) => r.flagged_for_review).length;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">
            Daily Clinic Triage Queue
          </h1>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
            Ranked highest to lowest risk to direct reminder calls and buffer reservations.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="secondary"
            onClick={() => runBatchPrediction(appointments)}
            loading={loading}
            icon={RefreshCw}
          >
            Refresh
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={handleExportCSV}
            icon={Download}
            disabled={!results.length}
          >
            Export CSV
          </Button>
        </div>
      </div>

      {/* Summary KPI Ribbon */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Card className="p-3.5">
          <div className="text-[11px] text-slate-600 dark:text-slate-400 font-semibold">Scheduled Appointments</div>
          <div className="text-2xl font-black text-slate-900 dark:text-slate-100 mt-1">{totalCount}</div>
        </Card>
        <Card className="p-3.5">
          <div className="text-[11px] text-rose-600 dark:text-rose-400 font-semibold">High Risk (&ge;50%)</div>
          <div className="text-2xl font-black text-rose-600 dark:text-rose-400 mt-1">{highRiskCount}</div>
        </Card>
        <Card className="p-3.5">
          <div className="text-[11px] text-amber-600 dark:text-amber-400 font-semibold">Medium Risk (&ge;16%)</div>
          <div className="text-2xl font-black text-amber-600 dark:text-amber-400 mt-1">{mediumRiskCount}</div>
        </Card>
        <Card className="p-3.5">
          <div className="text-[11px] text-teal-700 dark:text-teal-400 font-semibold">Staff Actions Flagged</div>
          <div className="text-2xl font-black text-teal-700 dark:text-teal-400 mt-1">{flaggedCount}</div>
        </Card>
      </div>

      {/* Table Card */}
      <Card className="p-0 overflow-hidden">
        <div className="p-3.5 flex flex-col md:flex-row gap-3 items-center justify-between border-b border-slate-100 dark:border-slate-800">
          <div className="relative w-full md:w-72">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Filter by patient name or clinic..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-teal-600"
            />
          </div>

          <div className="flex items-center gap-2 w-full md:w-auto">
            <div className="relative">
              <select
                value={deptFilter}
                onChange={(e) => setDeptFilter(e.target.value)}
                className="appearance-none text-xs pl-3 pr-8 py-1.5 rounded-lg bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none cursor-pointer"
              >
                <option value="ALL">All Departments</option>
                <option value="General Practice">General Practice</option>
                <option value="Dental">Dental</option>
                <option value="Eye Clinic">Eye Clinic</option>
                <option value="Pediatrics">Pediatrics</option>
                <option value="Physiotherapy">Physiotherapy</option>
              </select>
              <ChevronDown className="w-3 h-3 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>

            <div className="relative">
              <select
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
                className="appearance-none text-xs pl-3 pr-8 py-1.5 rounded-lg bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none cursor-pointer"
              >
                <option value="ALL">All Risk Bands</option>
                <option value="high">High Risk</option>
                <option value="medium">Medium Risk</option>
                <option value="low">Low Risk</option>
              </select>
              <ChevronDown className="w-3 h-3 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>
        </div>

        {/* Triage Queue Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 dark:bg-slate-950/40 text-slate-700 dark:text-slate-300 font-semibold border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th className="py-2.5 px-4">Rank / Patient</th>
                <th className="py-2.5 px-4">Department & Time</th>
                <th className="py-2.5 px-4">Lead Time</th>
                <th className="py-2.5 px-4">Predicted Risk</th>
                <th className="py-2.5 px-4">Operational Action</th>
                <th className="py-2.5 px-4 text-center">Staff Outreach</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {filtered.map((row, idx) => {
                const callDone = actionsTaken[row.index]?.call;
                const smsDone = actionsTaken[row.index]?.sms;

                return (
                  <tr
                    key={row.index}
                    className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors"
                  >
                    <td className="py-2.5 px-4">
                      <div className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
                        <span className="text-[10px] w-4.5 h-4.5 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center font-bold text-slate-600 dark:text-slate-300">
                          {idx + 1}
                        </span>
                        {row.patient_name}
                      </div>
                      <div className="text-[10px] text-slate-500 ml-6">ID: APP-{1000 + row.index}</div>
                    </td>

                    <td className="py-2.5 px-4">
                      <div className="font-medium text-slate-800 dark:text-slate-200">{row.department}</div>
                      <div className="text-[10px] text-slate-500">{row.appt_weekday} at {row.appt_hour}:00</div>
                    </td>

                    <td className="py-2.5 px-4">
                      <div className="font-medium text-slate-800 dark:text-slate-200">{row.lead_time_days} days</div>
                      <div className="text-[10px] text-slate-500">
                        {row.reminder_scheduled === 'yes' ? 'Reminder Set' : 'No Reminder'}
                      </div>
                    </td>

                    <td className="py-2.5 px-4">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-xs text-slate-900 dark:text-slate-100">
                          {(row.no_show_probability * 100).toFixed(1)}%
                        </span>
                        <Badge variant={row.risk_band} size="xs">
                          {row.risk_band}
                        </Badge>
                      </div>
                    </td>

                    <td className="py-2.5 px-4">
                      <div className="text-[11px] text-slate-600 dark:text-slate-400 max-w-xs truncate">
                        {row.suggested_action}
                      </div>
                    </td>

                    <td className="py-2.5 px-4">
                      <div className="flex items-center justify-center gap-1.5">
                        <button
                          type="button"
                          onClick={() => toggleAction(row.index, 'call')}
                          className={`px-2 py-1 rounded text-[10px] font-semibold border flex items-center gap-1 transition-all cursor-pointer ${
                            callDone
                              ? 'bg-emerald-600 text-white border-emerald-600'
                              : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:border-slate-400'
                          }`}
                        >
                          <PhoneCall className="w-3 h-3" />
                          {callDone ? 'Called' : 'Call'}
                        </button>

                        <button
                          type="button"
                          onClick={() => toggleAction(row.index, 'sms')}
                          className={`px-2 py-1 rounded text-[10px] font-semibold border flex items-center gap-1 transition-all cursor-pointer ${
                            smsDone
                              ? 'bg-teal-600 text-white border-teal-600'
                              : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:border-slate-400'
                          }`}
                        >
                          <CheckCircle className="w-3 h-3" />
                          {smsDone ? 'SMS Sent' : 'Send SMS'}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {!filtered.length && (
            <div className="text-center py-8 text-xs text-slate-500">
              No appointments match the selected filters.
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
