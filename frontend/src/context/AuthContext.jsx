import React, { createContext, useContext, useState } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('hospital_staff_user');
    return saved ? JSON.parse(saved) : {
      name: 'Nurse Sarah Connor',
      role: 'Clinical Receptionist',
      department: 'Central Triage',
      badgeId: 'STAFF-4821',
    };
  });

  const login = (userData) => {
    setUser(userData);
    localStorage.setItem('hospital_staff_user', JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('hospital_staff_user');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
