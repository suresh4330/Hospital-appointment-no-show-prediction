import React, { useState } from 'react';
import { Info, ChevronDown, ChevronUp } from 'lucide-react';

export function DisclaimerAlert({ className = '' }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className={`rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs text-xs transition-all ${className}`}
      role="note"
    >
      <div className="flex items-center justify-between px-3.5 py-2">
        <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
          <Info className="w-3.5 h-3.5 text-teal-600 dark:text-teal-400 shrink-0" />
          <span className="font-semibold text-slate-900 dark:text-slate-100">
            Administrative Decision Support:
          </span>
          <span className="hidden sm:inline text-slate-600 dark:text-slate-400">
            Estimates attendance likelihood to guide reminder outreach and scheduling buffers.
          </span>
          <span className="sm:hidden text-slate-600 dark:text-slate-400">
            Reminder prioritization support only.
          </span>
        </div>

        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className="inline-flex items-center gap-1 text-[11px] font-semibold text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 shrink-0 ml-2 cursor-pointer"
          aria-expanded={expanded}
        >
          {expanded ? 'Hide Details' : 'Details'}
          {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
      </div>

      {expanded && (
        <div className="px-3.5 pb-3 pt-1 border-t border-slate-100 dark:border-slate-800 text-slate-600 dark:text-slate-400 text-[11px] leading-relaxed animate-in fade-in duration-150">
          This system produces probabilistic estimates using non-clinical booking-time attributes. It is strictly forbidden from being used for clinical diagnosis, medical triage, or automated appointment cancellations. All high-risk alerts must be reviewed by hospital administrative or nursing staff prior to patient contact.
        </div>
      )}
    </div>
  );
}
