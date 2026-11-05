import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Wrench, KeyRound, AlertCircle, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [step, setStep] = useState(1); // 1 = Request, 2 = Confirm
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [message, setMessage] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleRequest = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setErrorMsg('');
    try {
      const res = await api.forgotPassword(email);
      setMessage(res.message);
      if (res.demo_reset_token) {
        setResetToken(res.demo_reset_token);
      }
      setStep(2);
    } catch (err) {
      setErrorMsg(err.message || 'Request failed');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setErrorMsg('');
    try {
      await api.resetPassword({
        email,
        reset_token: resetToken,
        new_password: newPassword
      });
      alert('Password reset successfully. Please log in.');
      navigate('/login');
    } catch (err) {
      setErrorMsg(err.message || 'Reset failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link to="/" className="inline-flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md">
            <Wrench className="w-5 h-5" />
          </div>
          <span className="font-black text-2xl text-slate-900 tracking-tight">HomeServe</span>
        </Link>
        <h2 className="mt-4 text-2xl font-black text-slate-900">Reset Your Password</h2>
        <p className="mt-1 text-xs text-slate-500">Recover access to your HomeServe account</p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-white py-8 px-6 sm:px-8 shadow-xl rounded-2xl border border-slate-200/80 space-y-4">
          {errorMsg && (
            <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {step === 1 ? (
            <form onSubmit={handleRequest} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">Registered Email</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs sm:text-sm cursor-pointer disabled:opacity-50"
              >
                {submitting ? 'Sending Code...' : 'Send Reset Code'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleReset} className="space-y-4">
              <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-xs text-blue-900">
                <span className="font-bold block">Reset Code Sent (15m validity):</span>
                <span className="text-[11px] text-blue-700">Check your inbox or enter testing code: <code className="font-mono font-bold bg-white px-1 py-0.5 rounded">HSB-DEMO-2026</code></span>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">Reset Token</label>
                <input
                  type="text"
                  required
                  value={resetToken}
                  onChange={(e) => setResetToken(e.target.value)}
                  placeholder="Enter token"
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 uppercase font-mono"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">New Password</label>
                <input
                  type="password"
                  required
                  minLength={6}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Minimum 6 characters"
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs sm:text-sm cursor-pointer disabled:opacity-50"
              >
                {submitting ? 'Resetting...' : 'Update Password'}
              </button>
            </form>
          )}

          <div className="pt-3 border-t border-slate-100 text-center">
            <Link to="/login" className="text-xs text-blue-600 hover:underline font-semibold">
              Back to Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
