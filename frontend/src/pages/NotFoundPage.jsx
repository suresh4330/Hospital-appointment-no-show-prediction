import React from 'react';
import { Link } from 'react-router-dom';
import { HelpCircle, ArrowLeft } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';

export function NotFoundPage() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center p-4">
      <Card className="max-w-md w-full text-center py-10">
        <HelpCircle className="w-12 h-12 text-slate-400 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100">Page Not Found</h2>
        <p className="text-xs text-slate-400 mt-1 mb-6">
          The requested triage view does not exist or has been relocated.
        </p>
        <Link to="/">
          <Button variant="primary" icon={ArrowLeft}>
            Return to Triage Calculator
          </Button>
        </Link>
      </Card>
    </div>
  );
}
