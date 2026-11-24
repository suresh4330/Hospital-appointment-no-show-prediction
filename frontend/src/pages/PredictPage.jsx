import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import {
  Sparkles,
  RefreshCw,
  Send,
  PhoneCall,
  CheckCircle2,
  Copy,
  Check,
  AlertCircle,
  HelpCircle,
  User,
  Calendar,
  History
} from 'lucide-react';
import { predictOne } from '../services/api';
import { useToast } from '../context/ToastContext';
import { SAMPLE_PRESETS } from '../data/presets';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Select } from '../components/common/Select';
import { RiskGauge } from '../components/prediction/RiskGauge';
import { FactorCard } from '../components/prediction/FactorCard';

export function PredictPage() {
  const { success, error: toastError } = useToast();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);
  const [apiError, setApiError] = useState(null);

  const defaultValues = {
    age: 27,
    distance_km: 18.5,
    lead_time_days: 34,
    appt_weekday: 'Monday',
    appt_hour: 8,
    department: 'Dental',
    booking_channel: 'phone',
    reminder_scheduled: 'no',
    is_follow_up: 'no',
    prev_visits: 4,
    prev_no_shows: 2,
  };

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    watch,
    formState: { errors },
  } = useForm({ defaultValues });

  const prevVisits = Number(watch('prev_visits') || 0);

  const applyPreset = (presetData) => {
    Object.entries(presetData).forEach(([k, v]) => setValue(k, v));
    setApiError(null);
    success('Loaded clinical preset');
  };

  const onSubmit = async (formData) => {
    if (Number(formData.prev_no_shows) > Number(formData.prev_visits)) {
      toastError('Past no-shows cannot exceed total past visits.');
      return;
    }

    setLoading(true);
    setApiError(null);
    try {
      const payload = {
        age: parseInt(formData.age, 10),
        distance_km: formData.distance_km ? parseFloat(formData.distance_km) : null,
        lead_time_days: parseInt(formData.lead_time_days, 10),
        appt_weekday: formData.appt_weekday,
        appt_hour: parseInt(formData.appt_hour, 10),
        department: formData.department,
        booking_channel: formData.booking_channel,
        reminder_scheduled: formData.reminder_scheduled,
        is_follow_up: formData.is_follow_up,
        prev_visits: parseInt(formData.prev_visits, 10),
        prev_no_shows: parseInt(formData.prev_no_shows, 10),
      };

      const res = await predictOne(payload);
      setResult(res);
      success('Triage prediction ready');
    } catch (err) {
      setApiError(err.message || 'Unable to compute prediction.');
      toastError(err.message || 'Failed to calculate prediction.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopySummary = () => {
    if (!result) return;
    const summary = `CareAttend Triage Assessment:\n• Probability: ${(result.no_show_probability * 100).toFixed(1)}% (${result.risk_band.toUpperCase()})\n• Action: ${result.suggested_action}\n• Note: Staff review required.`;
    navigator.clipboard.writeText(summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    success('Summary copied');
  };

  return (
    <div className="space-y-4">
      {/* Preset Chips Bar (Single Location Above Form) */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-1 mr-1">
            <Sparkles className="w-3.5 h-3.5 text-teal-600" /> Presets:
          </span>
          {SAMPLE_PRESETS.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => applyPreset(p.data)}
              className="text-xs px-2.5 py-1 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:border-teal-600 hover:text-teal-700 dark:hover:text-teal-300 font-medium transition-colors shadow-2xs cursor-pointer"
            >
              {p.name.split(' (')[0]}
            </button>
          ))}
        </div>

        <button
          type="button"
          onClick={() => {
            reset(defaultValues);
            setResult(null);
            setApiError(null);
          }}
          className="text-xs text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 flex items-center gap-1 font-medium cursor-pointer"
        >
          <RefreshCw className="w-3 h-3" /> Reset Defaults
        </button>
      </div>

      {/* Main 2-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left Column: Compact Form (7 cols) */}
        <div className="lg:col-span-7">
          <Card className="shadow-xs">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {/* Section 1: Patient Information */}
              <div>
                <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900 dark:text-slate-100 uppercase tracking-wider mb-2 pb-1 border-b border-slate-100 dark:border-slate-800">
                  <User className="w-3.5 h-3.5 text-teal-600" />
                  Patient Details
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <Input
                    label="Patient Age"
                    type="number"
                    min="0"
                    max="110"
                    required
                    error={errors.age?.message}
                    {...register('age', { required: 'Required', min: 0, max: 110 })}
                  />
                  <Input
                    label="Distance (km)"
                    type="number"
                    step="0.1"
                    min="0"
                    max="500"
                    helper="Estimated distance"
                    {...register('distance_km')}
                  />
                  <Select
                    label="Visit Type"
                    options={[
                      { value: 'no', label: 'First / New Visit' },
                      { value: 'yes', label: 'Follow-up Visit' },
                    ]}
                    required
                    {...register('is_follow_up')}
                  />
                </div>
              </div>

              {/* Section 2: Appointment Details */}
              <div>
                <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900 dark:text-slate-100 uppercase tracking-wider mb-2 pb-1 border-b border-slate-100 dark:border-slate-800">
                  <Calendar className="w-3.5 h-3.5 text-teal-600" />
                  Appointment Scheduling
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <Input
                    label="Lead Time (Days)"
                    type="number"
                    min="0"
                    max="365"
                    required
                    helper="Days until visit"
                    error={errors.lead_time_days?.message}
                    {...register('lead_time_days', { required: 'Required', min: 0, max: 365 })}
                  />
                  <Select
                    label="Day of Week"
                    options={['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}
                    required
                    {...register('appt_weekday')}
                  />
                  <Input
                    label="Hour (24h)"
                    type="number"
                    min="7"
                    max="18"
                    required
                    helper="e.g. 8 for 8:00 AM"
                    error={errors.appt_hour?.message}
                    {...register('appt_hour', { required: 'Required', min: 7, max: 18 })}
                  />
                  <div className="sm:col-span-2">
                    <Select
                      label="Clinic Department"
                      options={['General Practice', 'Dental', 'Eye Clinic', 'Pediatrics', 'Physiotherapy']}
                      required
                      {...register('department')}
                    />
                  </div>
                  <div>
                    <Select
                      label="Booking Channel"
                      options={[
                        { value: 'phone', label: 'Phone Call' },
                        { value: 'online', label: 'Online Portal' },
                        { value: 'front_desk', label: 'Front Desk' },
                      ]}
                      required
                      {...register('booking_channel')}
                    />
                  </div>
                </div>
              </div>

              {/* Section 3: Attendance History & Reminder */}
              <div>
                <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900 dark:text-slate-100 uppercase tracking-wider mb-2 pb-1 border-b border-slate-100 dark:border-slate-800">
                  <History className="w-3.5 h-3.5 text-teal-600" />
                  Attendance History & Reminder
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <Select
                    label="Reminder Scheduled?"
                    options={[
                      { value: 'yes', label: 'Yes (Reminder Set)' },
                      { value: 'no', label: 'No Reminder' },
                    ]}
                    required
                    {...register('reminder_scheduled')}
                  />
                  <Input
                    label="Past Total Visits"
                    type="number"
                    min="0"
                    max="100"
                    required
                    error={errors.prev_visits?.message}
                    {...register('prev_visits', { required: 'Required', min: 0 })}
                  />
                  <Input
                    label="Past Missed Visits"
                    type="number"
                    min="0"
                    max="100"
                    required
                    helper={`Max: ${prevVisits}`}
                    error={errors.prev_no_shows?.message}
                    {...register('prev_no_shows', {
                      required: 'Required',
                      min: 0,
                      validate: (v) => Number(v) <= prevVisits || 'Cannot exceed visits',
                    })}
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-2">
                <Button
                  type="submit"
                  variant="primary"
                  loading={loading}
                  icon={Send}
                  className="w-full text-xs font-semibold py-2"
                >
                  Run Triage Risk Prediction
                </Button>
              </div>
            </form>
          </Card>
        </div>

        {/* Right Column: Sticky Result Panel (5 cols) */}
        <div className="lg:col-span-5 sticky top-18 space-y-4">
          <Card
            title="Triage Assessment"
            subtitle="Champion calibrated model (0.16 threshold)"
            action={
              result && (
                <Button size="sm" variant="ghost" onClick={handleCopySummary} icon={copied ? Check : Copy}>
                  {copied ? 'Copied' : 'Copy'}
                </Button>
              )
            }
          >
            {/* Loading State */}
            {loading && (
              <div className="py-12 text-center space-y-3">
                <div className="w-8 h-8 border-2 border-teal-600 border-t-transparent rounded-full animate-spin mx-auto" />
                <div className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                  Calculating calibrated risk...
                </div>
                <p className="text-[11px] text-slate-400">Evaluating occlusion driving factors</p>
              </div>
            )}

            {/* Error State */}
            {!loading && apiError && (
              <div className="py-8 text-center space-y-2">
                <AlertCircle className="w-8 h-8 text-rose-500 mx-auto" />
                <div className="text-xs font-bold text-rose-600 dark:text-rose-400">
                  Calculation Failed
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 max-w-xs mx-auto">
                  {apiError}
                </p>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleSubmit(onSubmit)}
                  className="mt-2 text-xs"
                >
                  Retry Prediction
                </Button>
              </div>
            )}

            {/* Success Result State */}
            {!loading && !apiError && result && (
              <div className="space-y-4">
                <RiskGauge
                  probability={result.no_show_probability}
                  riskBand={result.risk_band}
                  threshold={0.16}
                />

                {/* Operational Recommendation Box */}
                <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 space-y-1">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800 dark:text-slate-200">
                    {result.flagged_for_review ? (
                      <PhoneCall className="w-3.5 h-3.5 text-teal-600" />
                    ) : (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    )}
                    Staff Recommendation
                  </div>
                  <p className="text-xs font-medium text-slate-700 dark:text-slate-300 leading-snug">
                    {result.suggested_action}
                  </p>
                </div>

                {/* Top Driving Factors Horizontal Bars */}
                {result.top_factors && result.top_factors.length > 0 && (
                  <div>
                    <div className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider mb-2 pb-1 border-b border-slate-100 dark:border-slate-800">
                      Top Driving Factors
                    </div>
                    <div className="space-y-1">
                      {result.top_factors.map((factor, idx) => (
                        <FactorCard key={idx} {...factor} />
                      ))}
                    </div>
                    <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-2">
                      Bars indicate shift in predicted probability vs typical reference value.
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Empty State */}
            {!loading && !apiError && !result && (
              <div className="py-12 text-center space-y-2">
                <div className="w-10 h-10 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto">
                  <HelpCircle className="w-5 h-5 text-slate-400" />
                </div>
                <div className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                  No Prediction Yet
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 max-w-[220px] mx-auto">
                  Fill in the booking form on the left or select a preset chip above to see risk assessment.
                </p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
