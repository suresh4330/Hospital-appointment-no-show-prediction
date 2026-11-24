import React from 'react';
import { Navbar } from './Navbar';
import { DisclaimerAlert } from '../prediction/DisclaimerAlert';

export function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col bg-slate-100/70 dark:bg-slate-950 text-slate-900 dark:text-slate-100 antialiased">
      <Navbar />
      <div className="flex-1 max-w-[1200px] w-full mx-auto px-4 sm:px-6 py-5">
        <DisclaimerAlert className="mb-5" />
        <main>{children}</main>
      </div>
    </div>
  );
}
