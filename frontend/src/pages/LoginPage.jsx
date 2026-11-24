import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, ShieldCheck, UserCheck, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Select } from '../components/common/Select';

export function LoginPage() {
  const { login } = useAuth();
  const { success } = useToast();
  const navigate = useNavigate();

  const [staffName, setStaffName] = useState('Nurse Sarah Connor');
  const [role, setRole] = useState('Clinical Receptionist');
  const [badgeId, setBadgeId] = useState('STAFF-4821');

  const handleQuickLogin = (name, userRole, badge) => {
    login({ name, role: userRole, department: 'Central Outpatients', badgeId: badge });
    success(`Signed in as ${name} (${userRole})`);
    navigate('/');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    login({ name: staffName, role, department: 'Outpatient Triage', badgeId });
    success(`Welcome, ${staffName}`);
    navigate('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-slate-50 dark:bg-slate-950">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-teal-600 rounded-2xl flex items-center justify-center text-white mx-auto shadow-lg shadow-teal-600/30 mb-3">
            <Activity className="w-7 h-7" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">CareAttend AI</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Clinical Decision-Support • Hospital Appointment Triage
          </p>
        </div>

        <Card className="shadow-lg">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100 dark:border-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300">
            <ShieldCheck className="w-4 h-4 text-teal-600" />
            Administrative Staff Sign In
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Staff Full Name"
              value={staffName}
              onChange={(e) => setStaffName(e.target.value)}
              required
            />

            <Select
              label="Assigned Clinical Role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              options={[
                'Clinical Receptionist',
                'Triage Coordinator',
                'Clinic Operations Manager',
                'Senior Nurse Lead',
              ]}
              required
            />

            <Input
              label="Badge / Employee ID"
              value={badgeId}
              onChange={(e) => setBadgeId(e.target.value)}
              required
            />

            <Button type="submit" variant="primary" className="w-full mt-2" icon={ArrowRight}>
              Enter Triage Portal
            </Button>
          </form>

          <div className="mt-6 pt-5 border-t border-slate-100 dark:border-slate-800">
            <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-2.5">
              Or quick select staff profile:
            </div>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleQuickLogin('Sarah Connor', 'Clinical Receptionist', 'STAFF-4821')}
                className="text-left p-2 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-teal-500 hover:bg-teal-50/50 dark:hover:bg-teal-950/30 text-xs transition-colors"
              >
                <div className="font-semibold text-slate-800 dark:text-slate-200">Sarah Connor</div>
                <div className="text-[10px] text-slate-400">Receptionist</div>
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('Dr. Alex Reed', 'Clinic Manager', 'ADMIN-1029')}
                className="text-left p-2 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-teal-500 hover:bg-teal-50/50 dark:hover:bg-teal-950/30 text-xs transition-colors"
              >
                <div className="font-semibold text-slate-800 dark:text-slate-200">Dr. Alex Reed</div>
                <div className="text-[10px] text-slate-400">Operations Lead</div>
              </button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
