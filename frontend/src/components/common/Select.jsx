import React from 'react';
import { ChevronDown } from 'lucide-react';

export const Select = React.forwardRef(({
  label,
  error,
  options = [],
  className = '',
  required = false,
  id,
  helper,
  ...props
}, ref) => {
  const selectId = id || (label ? label.toLowerCase().replace(/[^a-z0-9]/g, '-') : undefined);

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={selectId} className="block text-xs font-semibold text-slate-800 dark:text-slate-200 mb-1">
          {label} {required && <span className="text-rose-600 font-bold">*</span>}
        </label>
      )}
      <div className="relative">
        <select
          ref={ref}
          id={selectId}
          className={`w-full appearance-none px-3 py-1.5 pr-8 text-xs rounded-lg bg-white dark:bg-slate-950 border text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 transition-all cursor-pointer ${
            error
              ? 'border-rose-500 focus:border-rose-500 focus:ring-rose-500/20 dark:border-rose-500'
              : 'border-slate-300 dark:border-slate-700 focus:border-teal-600 focus:ring-teal-600/20'
          } ${className}`}
          {...props}
        >
          {options.map((opt) => {
            const val = typeof opt === 'object' ? opt.value : opt;
            const lbl = typeof opt === 'object' ? opt.label : opt;
            return (
              <option key={val} value={val} className="dark:bg-slate-900 text-slate-900 dark:text-slate-100">
                {lbl}
              </option>
            );
          })}
        </select>
        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2.5 text-slate-500 dark:text-slate-400">
          <ChevronDown className="w-3.5 h-3.5" />
        </div>
      </div>
      {error ? (
        <p className="mt-1 text-[11px] text-rose-600 dark:text-rose-400 font-semibold">{error}</p>
      ) : helper ? (
        <p className="mt-1 text-[11px] text-slate-600 dark:text-slate-400">{helper}</p>
      ) : null}
    </div>
  );
});

Select.displayName = 'Select';
