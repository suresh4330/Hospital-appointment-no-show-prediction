export function formatPercent(value, decimals = 1) {
  if (value === null || value === undefined || isNaN(value)) return '0.0%';
  return `${(Number(value) * 100).toFixed(decimals)}%`;
}

export function getRiskBadge(band) {
  switch ((band || '').toLowerCase()) {
    case 'high':
      return {
        label: 'High Risk',
        bg: 'bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300 border-rose-200 dark:border-rose-800',
        dot: 'bg-rose-500'
      };
    case 'medium':
      return {
        label: 'Medium Risk',
        bg: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300 border-amber-200 dark:border-amber-800',
        dot: 'bg-amber-500'
      };
    case 'low':
    default:
      return {
        label: 'Low Risk',
        bg: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800',
        dot: 'bg-emerald-500'
      };
  }
}
