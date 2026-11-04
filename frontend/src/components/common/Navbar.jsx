import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Wrench, ShieldCheck, User, LogOut, LayoutDashboard, 
  Menu, X, Sparkles, ChevronDown, CheckCircle2 
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import NotificationDropdown from './NotificationDropdown';

export default function Navbar() {
  const { user, role, isAuthenticated, logout, quickSwitchRole } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [roleSwitchOpen, setRoleSwitchOpen] = useState(false);
  const navigate = useNavigate();

  const handleQuickSwitch = async (targetRole) => {
    await quickSwitchRole(targetRole);
    setRoleSwitchOpen(false);
    if (targetRole === 'admin') navigate('/admin');
    else if (targetRole === 'provider') navigate('/provider');
    else if (targetRole === 'technician') navigate('/technician');
    else navigate('/customer');
  };

  const getDashboardPath = () => {
    switch (role) {
      case 'admin': return '/admin';
      case 'provider': return '/provider';
      case 'technician': return '/technician';
      default: return '/customer';
    }
  };

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-100 shadow-xs">
      {/* Top Demo Bar with 1-click Role Switching */}
      <div className="bg-slate-900 text-slate-300 text-xs py-1.5 px-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="flex h-2 w-2 rounded-full bg-emerald-400"></span>
            <span className="font-medium text-slate-200">Vibe Coding Capstone Live Demo:</span>
            <span className="hidden sm:inline text-slate-400">Quick Test 4 User Roles:</span>
          </div>

          <div className="flex items-center gap-1.5 overflow-x-auto py-0.5">
            <button
              onClick={() => handleQuickSwitch('admin')}
              className={`px-2 py-0.5 rounded text-[11px] font-semibold transition cursor-pointer ${
                role === 'admin' ? 'bg-purple-600 text-white shadow-xs' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              Super Admin
            </button>
            <button
              onClick={() => handleQuickSwitch('provider')}
              className={`px-2 py-0.5 rounded text-[11px] font-semibold transition cursor-pointer ${
                role === 'provider' ? 'bg-blue-600 text-white shadow-xs' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              Provider
            </button>
            <button
              onClick={() => handleQuickSwitch('customer')}
              className={`px-2 py-0.5 rounded text-[11px] font-semibold transition cursor-pointer ${
                role === 'customer' ? 'bg-emerald-600 text-white shadow-xs' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              Customer
            </button>
            <button
              onClick={() => handleQuickSwitch('technician')}
              className={`px-2 py-0.5 rounded text-[11px] font-semibold transition cursor-pointer ${
                role === 'technician' ? 'bg-amber-600 text-white shadow-xs' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              Technician
            </button>
          </div>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
              <Wrench className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-black text-xl text-slate-900 tracking-tight">HomeServe</span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-blue-100 text-blue-700 uppercase tracking-wider">SaaS</span>
              </div>
              <p className="text-[10px] text-slate-500 leading-none">Home Services Platform</p>
            </div>
          </Link>

          {/* Center Links */}
          <nav className="hidden md:flex items-center gap-8">
            <Link to="/services" className="text-sm font-medium text-slate-700 hover:text-blue-600 transition">
              Explore Services
            </Link>
            <Link to="/services?category=ac-repair-and-maintenance" className="text-sm font-medium text-slate-700 hover:text-blue-600 transition">
              AC & Heating
            </Link>
            <Link to="/services?category=electrical-services" className="text-sm font-medium text-slate-700 hover:text-blue-600 transition">
              Electrical
            </Link>
            <Link to="/services?category=home-cleaning" className="text-sm font-medium text-slate-700 hover:text-blue-600 transition">
              Cleaning
            </Link>
          </nav>

          {/* Right Actions */}
          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <div className="flex items-center gap-2 sm:gap-3">
                <NotificationDropdown />

                <Link
                  to={getDashboardPath()}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 font-medium text-xs sm:text-sm transition cursor-pointer"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  <span className="capitalize font-semibold">{role} Portal</span>
                </Link>

                <div className="hidden sm:flex flex-col text-right">
                  <span className="text-xs font-semibold text-slate-900 truncate max-w-28">
                    {user?.first_name} {user?.last_name}
                  </span>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                    {role}
                  </span>
                </div>

                <button
                  onClick={logout}
                  className="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition cursor-pointer"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2 sm:gap-3">
                <Link
                  to="/login"
                  className="text-xs sm:text-sm font-medium text-slate-700 hover:text-blue-600 px-3 py-1.5 transition"
                >
                  Sign In
                </Link>
                <Link
                  to="/register?role=customer"
                  className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs sm:text-sm shadow-xs transition shadow-blue-500/20"
                >
                  Book a Service
                </Link>
                <Link
                  to="/register?role=provider"
                  className="hidden lg:inline-flex px-3 py-1.5 rounded-lg border border-slate-200 hover:border-blue-600 hover:text-blue-600 text-slate-700 font-medium text-xs transition"
                >
                  Join as Partner
                </Link>
              </div>
            )}

            {/* Mobile menu toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-slate-600 hover:text-slate-900"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-100 bg-white px-4 pt-3 pb-6 space-y-3">
          <Link
            to="/services"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-base font-medium text-slate-800"
          >
            All Services
          </Link>
          <Link
            to="/services?category=ac-repair-and-maintenance"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-base font-medium text-slate-800"
          >
            AC Services
          </Link>
          <Link
            to="/services?category=electrical-services"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-base font-medium text-slate-800"
          >
            Electrical
          </Link>
          <Link
            to="/services?category=home-cleaning"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-base font-medium text-slate-800"
          >
            Cleaning
          </Link>
          {isAuthenticated && (
            <Link
              to={getDashboardPath()}
              onClick={() => setMobileMenuOpen(false)}
              className="block py-2 font-semibold text-blue-600"
            >
              Go to {role} Dashboard
            </Link>
          )}
        </div>
      )}
    </header>
  );
}
