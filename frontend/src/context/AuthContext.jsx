import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('homeserve_token') || null);
  const [role, setRole] = useState(localStorage.getItem('homeserve_role') || null);
  const [loading, setLoading] = useState(true);

  const fetchProfile = async () => {
    try {
      const profile = await api.getProfile();
      setUser(profile);
      setRole(profile.role);
      localStorage.setItem('homeserve_role', profile.role);
    } catch (err) {
      console.error('Failed to fetch profile', err);
      logout();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (email, password) => {
    const data = await api.login(email, password);
    setToken(data.access_token);
    setRole(data.role);
    localStorage.setItem('homeserve_token', data.access_token);
    localStorage.setItem('homeserve_role', data.role);
    await fetchProfile();
    return data;
  };

  const register = async (userData) => {
    const data = await api.register(userData);
    setToken(data.access_token);
    setRole(data.role);
    localStorage.setItem('homeserve_token', data.access_token);
    localStorage.setItem('homeserve_role', data.role);
    await fetchProfile();
    return data;
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setRole(null);
    localStorage.removeItem('homeserve_token');
    localStorage.removeItem('homeserve_role');
  };

  const quickSwitchRole = async (targetRole) => {
    const credentials = {
      admin: { email: 'admin@homeserve.com', password: 'Admin@123' },
      provider: { email: 'provider@homeserve.com', password: 'Provider@123' },
      customer: { email: 'customer@homeserve.com', password: 'Customer@123' },
      technician: { email: 'technician@homeserve.com', password: 'Technician@123' },
    };

    if (credentials[targetRole]) {
      return await login(credentials[targetRole].email, credentials[targetRole].password);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        role,
        isAuthenticated: !!token,
        loading,
        login,
        register,
        logout,
        quickSwitchRole,
        refreshProfile: fetchProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
