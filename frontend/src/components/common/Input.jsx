import React from 'react';

export const Input = React.forwardRef(({
  label,
  error,
  helper,
  className = '',
  required = false,
  id,
  type = 'text',
  ...props
}, ref) => {
  const inputId = id || (label ? label.toLowerCase().replace(/[^a-z0-9]/g, '-') : undefined);

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={inputId} className="block text-xs font-semibold text-slate-800 dark:text-slate-200 mb-1">
          {label} {required && <span className="text-rose-600 font-bold">*</span>}
        </label>
      )}
      <input
        ref={ref}
        id={inputId}
        type={type}
        className={`w-full px-3 py-1.5 text-xs rounded-lg bg-white dark:bg-slate-950 border text-slate-900 dark:text-slate-100 placeholder:text-slate-500 dark:placeholder:text-slate-500 focus:outline-none focus:ring-1 transition-all ${
          error
            ? 'border-rose-500 focus:border-rose-500 focus:ring-rose-500/20 dark:border-rose-500'
            : 'border-slate-300 dark:border-slate-700 focus:border-teal-600 focus:ring-teal-600/20'
        } ${className}`}
        {...props}
      />
      {error ? (
        <p className="mt-1 text-[11px] text-rose-600 dark:text-rose-400 font-semibold">{error}</p>
      ) : helper ? (
        <p className="mt-1 text-[11px] text-slate-600 dark:text-slate-400">{helper}</p>
      ) : null}
    </div>
  );
});

Input.displayName = 'Input';
