import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Wrench, Shield, ArrowRight, AlertCircle, KeyRound, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const { login, quickSwitchRole } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const redirectAfterLogin = (role) => {
    if (role === 'admin') navigate('/admin');
    else if (role === 'provider') navigate('/provider');
    else if (role === 'technician') navigate('/technician');
    else navigate('/customer');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setErrorMsg('');
    try {
      const data = await login(email, password);
      redirectAfterLogin(data.role);
    } catch (err) {
      setErrorMsg(err.message || 'Invalid email or password');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDemoLogin = async (targetRole) => {
    setSubmitting(true);
    setErrorMsg('');
    try {
      const data = await quickSwitchRole(targetRole);
      redirectAfterLogin(data.role);
    } catch (err) {
      setErrorMsg(err.message || 'Demo login failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link to="/" className="inline-flex items-center gap-2 group">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <Wrench className="w-5 h-5" />
          </div>
          <span className="font-black text-2xl text-slate-900 tracking-tight">HomeServe</span>
        </Link>
        <h2 className="mt-4 text-2xl font-black text-slate-900">Sign in to your account</h2>
        <p className="mt-1 text-xs text-slate-500">Access your role-based portal & service appointments</p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0 space-y-6">
        {/* Quick 1-Click Demo Buttons */}
        <div className="bg-gradient-to-r from-blue-900 to-indigo-950 p-5 rounded-2xl text-white shadow-lg space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-blue-300">
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>Capstone Evaluator Quick 1-Click Sign-In:</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              type="button"
              onClick={() => handleDemoLogin('admin')}
              className="p-2.5 rounded-xl bg-purple-600/80 hover:bg-purple-600 font-bold transition text-left cursor-pointer"
            >
              👑 Super Admin
              <span className="block text-[10px] text-purple-200 font-normal">Full control & analytics</span>
            </button>
            <button
              type="button"
              onClick={() => handleDemoLogin('provider')}
              className="p-2.5 rounded-xl bg-blue-600/80 hover:bg-blue-600 font-bold transition text-left cursor-pointer"
            >
              🛠️ Service Provider
              <span className="block text-[10px] text-blue-200 font-normal">Jobs, slots & earnings</span>
            </button>
            <button
              type="button"
              onClick={() => handleDemoLogin('customer')}
              className="p-2.5 rounded-xl bg-emerald-600/80 hover:bg-emerald-600 font-bold transition text-left cursor-pointer"
            >
              👤 Customer
              <span className="block text-[10px] text-emerald-200 font-normal">Book, track & invoices</span>
            </button>
            <button
              type="button"
              onClick={() => handleDemoLogin('technician')}
              className="p-2.5 rounded-xl bg-amber-600/80 hover:bg-amber-600 font-bold transition text-left cursor-pointer"
            >
              ⚡ Field Technician
              <span className="block text-[10px] text-amber-200 font-normal">Arrival & work proof</span>
            </button>
          </div>
        </div>

        {/* Regular Sign In Card */}
        <div className="bg-white py-8 px-6 sm:px-8 shadow-xl rounded-2xl border border-slate-200/80">
          {errorMsg && (
            <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">Email address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@domain.com"
                className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-hidden focus:border-blue-600"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-semibold text-slate-700">Password</label>
                <Link to="/forgot-password" className="text-[11px] text-blue-600 hover:underline">
                  Forgot password?
                </Link>
              </div>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-hidden focus:border-blue-600"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs sm:text-sm transition shadow-md shadow-blue-500/20 cursor-pointer disabled:opacity-50"
            >
              {submitting ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-slate-100 text-center text-xs text-slate-500">
            Don't have an account?{' '}
            <Link to="/register" className="font-bold text-blue-600 hover:underline">
              Create one now
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
