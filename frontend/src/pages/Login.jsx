import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { 
  Wrench, Shield, ArrowRight, AlertCircle, KeyRound, Sparkles, 
  UserCheck, Briefcase, User, PenTool, CheckCircle2 
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [fillHint, setFillHint] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const { login, quickSwitchRole } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const demoAccounts = {
    admin: { label: 'Super Admin', email: 'admin@homeserve.com', password: 'Admin@123', desc: 'Full platform management & analytics' },
    provider: { label: 'Service Provider', email: 'provider@homeserve.com', password: 'Provider@123', desc: 'Accept bookings, assign technicians & track earnings' },
    customer: { label: 'Customer (Jigar Thakkar)', email: 'customer@homeserve.com', password: 'Customer@123', desc: 'Book services, live tracking & invoices' },
    technician: { label: 'Technician', email: 'technician@homeserve.com', password: 'Technician@123', desc: 'Accept tasks, update status & upload work photos' },
  };

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

  const handleFillCredentials = (targetRole) => {
    const acc = demoAccounts[targetRole];
    if (acc) {
      setEmail(acc.email);
      setPassword(acc.password);
      setErrorMsg('');
      setFillHint(`Filled credentials for ${acc.label}. Click 'Sign In' below or type your own!`);
    }
  };

  const handleDirectDemoLogin = async (targetRole) => {
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
        {/* Quick Demo Credentials Assistant */}
        <div className="bg-gradient-to-r from-slate-900 to-indigo-950 p-5 rounded-2xl text-white shadow-lg space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-bold text-blue-300">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span>Capstone Demo Credentials:</span>
            </div>
            <span className="text-[10px] text-slate-400">Click to fill form</span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              type="button"
              onClick={() => handleFillCredentials('admin')}
              className="p-2.5 rounded-xl bg-purple-900/60 hover:bg-purple-800/80 border border-purple-500/30 font-bold transition text-left cursor-pointer"
            >
              <div className="flex items-center gap-1.5 text-purple-300">
                <Shield className="w-3.5 h-3.5" />
                <span>Super Admin</span>
              </div>
              <span className="block text-[10px] text-purple-200/80 font-normal mt-0.5 truncate">admin@homeserve.com</span>
            </button>

            <button
              type="button"
              onClick={() => handleFillCredentials('provider')}
              className="p-2.5 rounded-xl bg-blue-900/60 hover:bg-blue-800/80 border border-blue-500/30 font-bold transition text-left cursor-pointer"
            >
              <div className="flex items-center gap-1.5 text-blue-300">
                <Briefcase className="w-3.5 h-3.5" />
                <span>Service Provider</span>
              </div>
              <span className="block text-[10px] text-blue-200/80 font-normal mt-0.5 truncate">provider@homeserve.com</span>
            </button>

            <button
              type="button"
              onClick={() => handleFillCredentials('customer')}
              className="p-2.5 rounded-xl bg-emerald-900/60 hover:bg-emerald-800/80 border border-emerald-500/30 font-bold transition text-left cursor-pointer"
            >
              <div className="flex items-center gap-1.5 text-emerald-300">
                <User className="w-3.5 h-3.5" />
                <span>Customer (Jigar)</span>
              </div>
              <span className="block text-[10px] text-emerald-200/80 font-normal mt-0.5 truncate">customer@homeserve.com</span>
            </button>

            <button
              type="button"
              onClick={() => handleFillCredentials('technician')}
              className="p-2.5 rounded-xl bg-amber-900/60 hover:bg-amber-800/80 border border-amber-500/30 font-bold transition text-left cursor-pointer"
            >
              <div className="flex items-center gap-1.5 text-amber-300">
                <PenTool className="w-3.5 h-3.5" />
                <span>Technician</span>
              </div>
              <span className="block text-[10px] text-amber-200/80 font-normal mt-0.5 truncate">technician@homeserve.com</span>
            </button>
          </div>

          <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-300">
            <span>Or 1-click direct sign-in:</span>
            <div className="flex gap-1.5">
              <button
                type="button"
                onClick={() => handleDirectDemoLogin('admin')}
                className="px-2 py-0.5 rounded bg-purple-700 hover:bg-purple-600 text-white font-semibold text-[10px] cursor-pointer"
              >
                Admin
              </button>
              <button
                type="button"
                onClick={() => handleDirectDemoLogin('provider')}
                className="px-2 py-0.5 rounded bg-blue-700 hover:bg-blue-600 text-white font-semibold text-[10px] cursor-pointer"
              >
                Provider
              </button>
              <button
                type="button"
                onClick={() => handleDirectDemoLogin('customer')}
                className="px-2 py-0.5 rounded bg-emerald-700 hover:bg-emerald-600 text-white font-semibold text-[10px] cursor-pointer"
              >
                Customer
              </button>
              <button
                type="button"
                onClick={() => handleDirectDemoLogin('technician')}
                className="px-2 py-0.5 rounded bg-amber-700 hover:bg-amber-600 text-white font-semibold text-[10px] cursor-pointer"
              >
                Tech
              </button>
            </div>
          </div>
        </div>

        {/* Regular Sign In Card */}
        <div className="bg-white py-8 px-6 sm:px-8 shadow-xl rounded-2xl border border-slate-200/80">
          <div className="mb-4">
            <h3 className="text-sm font-bold text-slate-900">Manual Account Sign-In</h3>
            <p className="text-[11px] text-slate-500">Type any registered username & password</p>
          </div>

          {fillHint && (
            <div className="mb-4 p-3 rounded-xl bg-blue-50 border border-blue-200 text-xs text-blue-700 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0 text-blue-600" />
              <span>{fillHint}</span>
            </div>
          )}

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
              {submitting ? 'Signing in...' : 'Sign In with Email & Password'}
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
