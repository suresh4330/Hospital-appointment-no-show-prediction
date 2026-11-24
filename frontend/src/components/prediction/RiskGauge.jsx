import React from 'react';
import { getRiskBadge } from '../../utils/formatters';

export function RiskGauge({ probability, riskBand, threshold = 0.16 }) {
  const prob = Number(probability || 0);
  const percent = Math.min(Math.max(Math.round(prob * 100), 0), 100);
  const badge = getRiskBadge(riskBand);
  const isFlagged = prob >= threshold;

  // Colors reserved strictly for risk outcomes
  let barBg = 'bg-emerald-500';
  let textColor = 'text-emerald-600 dark:text-emerald-400';
  if (riskBand === 'high') {
    barBg = 'bg-rose-600';
    textColor = 'text-rose-600 dark:text-rose-400';
  } else if (riskBand === 'medium') {
    barBg = 'bg-amber-500';
    textColor = 'text-amber-600 dark:text-amber-400';
  }

  return (
    <div className="space-y-3">
      {/* Top probability display */}
      <div className="flex items-baseline justify-between">
        <div>
          <span className="text-xs uppercase font-bold tracking-wider text-slate-500 dark:text-slate-400">
            No-Show Probability
          </span>
          <div className={`text-3xl font-black tracking-tight ${textColor}`}>
            {(prob * 100).toFixed(1)}%
          </div>
        </div>

        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${badge.bg}`}>
          <span className={`w-2 h-2 rounded-full ${badge.dot}`} />
          {badge.label}
        </span>
      </div>

      {/* Horizontal progress meter with threshold marker */}
      <div className="relative pt-1">
        <div className="w-full bg-slate-100 dark:bg-slate-800 h-2.5 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${barBg}`}
            style={{ width: `${percent}%` }}
          />
        </div>

        {/* 16% Threshold tick mark */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-slate-400 dark:bg-slate-500 z-10"
          style={{ left: `${threshold * 100}%` }}
          title={`Decision Threshold: ${(threshold * 100).toFixed(0)}%`}
        />
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
        <span>0% Min</span>
        <span className="font-semibold text-slate-700 dark:text-slate-300">
          Threshold: {(threshold * 100).toFixed(0)}%
        </span>
        <span>100% Max</span>
      </div>
    </div>
  );
}
