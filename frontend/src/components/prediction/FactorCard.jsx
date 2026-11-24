import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

export function FactorCard({ feature, value, effect, direction }) {
  const isRaising = direction === 'raises risk' || effect > 0;
  const absEffect = Math.abs(effect);
  const percentEffect = (absEffect * 100).toFixed(1);

  // Maximum benchmark for effect bar is roughly 0.25 (25%)
  const barWidth = Math.min(Math.round((absEffect / 0.25) * 100), 100);

  const featureLabels = {
    reminder_scheduled: 'Reminder Scheduled',
    lead_time_days: 'Lead Time',
    prev_no_shows: 'Past Missed Visits',
    prev_visits: 'Total Past Visits',
    distance_km: 'Distance',
    department: 'Clinic Department',
    booking_channel: 'Booking Channel',
    appt_weekday: 'Day of Week',
    appt_hour: 'Appointment Hour',
    age: 'Patient Age',
    is_follow_up: 'Visit Type',
    prev_no_show_rate: 'Prior No-show Rate',
  };

  return (
    <div className="py-2 border-b border-slate-100 dark:border-slate-800 last:border-b-0">
      <div className="flex items-center justify-between text-xs mb-1">
        <div className="flex items-center gap-1.5 font-medium text-slate-800 dark:text-slate-200 truncate">
          {isRaising ? (
            <ArrowUpRight className="w-3.5 h-3.5 text-rose-600 shrink-0" />
          ) : (
            <ArrowDownRight className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
          )}
          <span className="truncate">{featureLabels[feature] || feature}</span>
          <span className="text-[10px] text-slate-500 font-normal">({String(value)})</span>
        </div>

        <div className="text-right shrink-0">
          <span
            className={`font-bold ${
              isRaising ? 'text-rose-600 dark:text-rose-400' : 'text-emerald-600 dark:text-emerald-400'
            }`}
          >
            {isRaising ? `+${percentEffect}%` : `-${percentEffect}%`}
          </span>
        </div>
      </div>

      {/* Visual horizontal mini-bar */}
      <div className="w-full bg-slate-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            isRaising ? 'bg-rose-500' : 'bg-emerald-500'
          }`}
          style={{ width: `${Math.max(barWidth, 6)}%` }}
        />
      </div>
    </div>
  );
}
