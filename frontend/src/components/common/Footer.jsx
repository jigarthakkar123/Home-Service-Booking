import React from 'react';
import { Link } from 'react-router-dom';
import { Wrench, Shield, CheckCircle, Clock, HeartHandshake, Phone, Mail } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-300 pt-16 pb-12 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Trust Badges */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pb-12 border-b border-slate-800">
          <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-800/50 border border-slate-800">
            <div className="w-12 h-12 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center shrink-0">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-semibold text-white text-sm">Verified Professionals</h4>
              <p className="text-xs text-slate-400 mt-0.5">Aadhaar & police background checked technicians</p>
            </div>
          </div>

          <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-800/50 border border-slate-800">
            <div className="w-12 h-12 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center shrink-0">
              <CheckCircle className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-semibold text-white text-sm">30-Day Service Warranty</h4>
              <p className="text-xs text-slate-400 mt-0.5">Free revisit if you face any issues post-service</p>
            </div>
          </div>

          <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-800/50 border border-slate-800">
            <div className="w-12 h-12 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center shrink-0">
              <Clock className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-semibold text-white text-sm">On-Time Guaranteed</h4>
              <p className="text-xs text-slate-400 mt-0.5">Dedicated slot arrival with live tracking</p>
            </div>
          </div>
        </div>

        {/* Links Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 py-12">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white">
                <Wrench className="w-4 h-4" />
              </div>
              <span className="font-bold text-lg text-white">HomeServe</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              India's premier on-demand home maintenance and services SaaS platform. Transparent pricing, verified experts, and instant booking.
            </p>
            <div className="mt-4 text-xs text-slate-400 space-y-1">
              <p className="flex items-center gap-2"><Phone className="w-3.5 h-3.5 text-blue-400" /> +91 800-4663-7378</p>
              <p className="flex items-center gap-2"><Mail className="w-3.5 h-3.5 text-blue-400" /> support@homeserve.com</p>
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-white text-sm mb-4">Core Categories</h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/services?category=ac-repair-and-maintenance" className="hover:text-blue-400 transition">AC Repair & Jet Servicing</Link></li>
              <li><Link to="/services?category=electrical-services" className="hover:text-blue-400 transition">Electrical Wiring & MCB</Link></li>
              <li><Link to="/services?category=plumbing-services" className="hover:text-blue-400 transition">Plumbing & Sanitary</Link></li>
              <li><Link to="/services?category=home-cleaning" className="hover:text-blue-400 transition">Deep Home & Sofa Cleaning</Link></li>
              <li><Link to="/services?category=carpentry-services" className="hover:text-blue-400 transition">Carpentry & Lock Fittings</Link></li>
              <li><Link to="/services?category=pest-control" className="hover:text-blue-400 transition">Eco Herbal Pest Control</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-white text-sm mb-4">Platform Portals</h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/admin" className="hover:text-blue-400 transition">Super Admin Dashboard</Link></li>
              <li><Link to="/provider" className="hover:text-blue-400 transition">Service Provider Portal</Link></li>
              <li><Link to="/customer" className="hover:text-blue-400 transition">Customer Account</Link></li>
              <li><Link to="/technician" className="hover:text-blue-400 transition">Technician Field App</Link></li>
              <li><Link to="/register?role=provider" className="text-blue-400 hover:underline">Register as Service Partner</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-white text-sm mb-4">Tech Architecture</h4>
            <div className="text-xs text-slate-400 space-y-2">
              <p className="bg-slate-800 p-2.5 rounded-lg border border-slate-700/60">
                <span className="text-blue-400 font-semibold">Backend:</span> FastAPI + Python 3.13 + SQLAlchemy + PyMySQL
              </p>
              <p className="bg-slate-800 p-2.5 rounded-lg border border-slate-700/60">
                <span className="text-blue-400 font-semibold">Frontend:</span> React 19 + Tailwind CSS + Lucide Icons
              </p>
              <p className="bg-slate-800 p-2.5 rounded-lg border border-slate-700/60">
                <span className="text-blue-400 font-semibold">Security:</span> JWT RBAC + Bcrypt + Double Booking Prevention
              </p>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
          <p>© 2026 HomeServe Technologies SaaS Platform. All rights reserved.</p>
          <p className="flex items-center gap-2">
            Built with AI-Powered Vibe Coding for Full Stack Capstone Competition
          </p>
        </div>
      </div>
    </footer>
  );
}
