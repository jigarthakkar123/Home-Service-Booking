import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Wrench, Zap, Droplets, Wind, Sparkles, Paintbrush, Hammer, Tv, ShieldAlert,
  Search, Star, CheckCircle2, ArrowRight, ShieldCheck, Clock, Award, Users
} from 'lucide-react';
import { api } from '../services/api';

const categoryIcons = {
  Zap: Zap,
  Droplets: Droplets,
  Wind: Wind,
  Sparkles: Sparkles,
  Paintbrush: Paintbrush,
  Hammer: Hammer,
  Tv: Tv,
  ShieldAlert: ShieldAlert,
};

export default function Home() {
  const [categories, setCategories] = useState([]);
  const [services, setServices] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadData() {
      try {
        const [cats, srvs] = await Promise.all([
          api.getCategories(),
          api.getServices('limit=8')
        ]);
        setCategories(cats || []);
        setServices(srvs || []);
      } catch (err) {
        console.error('Failed to load home data', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/services?search=${encodeURIComponent(searchQuery.trim())}`);
    } else {
      navigate('/services');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-blue-900 via-indigo-950 to-slate-900 text-white py-20 lg:py-28">
        {/* Background glow effects */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-blue-500/10 blur-3xl pointer-events-none rounded-full" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-400/20 text-blue-300 text-xs font-semibold uppercase tracking-wider mb-6">
              <Sparkles className="w-3.5 h-3.5" />
              SaaS Home Services Platform
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-tight sm:leading-none text-white">
              Professional Home Services, <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300">Simplified.</span>
            </h1>

            <p className="mt-6 text-base sm:text-lg text-slate-300 leading-relaxed">
              Connect with top-rated, police-verified electricians, AC technicians, plumbers, and cleaning specialists in your neighborhood.
            </p>

            {/* Search Box */}
            <form onSubmit={handleSearch} className="mt-8 max-w-2xl mx-auto flex items-center bg-white rounded-2xl p-2 shadow-2xl border border-slate-200">
              <div className="flex items-center gap-3 pl-3 flex-1">
                <Search className="w-5 h-5 text-slate-400 shrink-0" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search AC servicing, electrical, plumbing, deep cleaning..."
                  className="w-full text-sm text-slate-900 placeholder-slate-400 focus:outline-hidden"
                />
              </div>
              <button
                type="submit"
                className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm transition shadow-md shadow-blue-500/20 cursor-pointer"
              >
                Search
              </button>
            </form>

            {/* Quick Metrics */}
            <div className="mt-12 grid grid-cols-2 sm:grid-cols-4 gap-4 text-center border-t border-slate-800/80 pt-8">
              <div>
                <div className="text-2xl font-bold text-white">4.9 / 5.0</div>
                <div className="text-xs text-slate-400 mt-1">Average Customer Rating</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-white">100%</div>
                <div className="text-xs text-slate-400 mt-1">Verified Technicians</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-white">30 Days</div>
                <div className="text-xs text-slate-400 mt-1">Service Guarantee</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-white">60 Min</div>
                <div className="text-xs text-slate-400 mt-1">Express Slot Booking</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Service Categories Section */}
      <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between mb-10 gap-4">
          <div>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">Explore by Category</h2>
            <p className="text-slate-600 text-sm mt-1">Choose from our 8 verified home care disciplines</p>
          </div>
          <Link
            to="/services"
            className="text-sm font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1 group"
          >
            View All Services <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-4">
          {categories.map((cat) => {
            const IconComponent = categoryIcons[cat.icon] || Wrench;
            return (
              <Link
                key={cat.id}
                to={`/services?category=${cat.slug}`}
                className="flex flex-col items-center p-4 rounded-2xl bg-white border border-slate-200/80 hover:border-blue-500 hover:shadow-lg hover:-translate-y-1 transition duration-200 text-center group"
              >
                <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 group-hover:bg-blue-600 group-hover:text-white flex items-center justify-center transition mb-3">
                  <IconComponent className="w-6 h-6" />
                </div>
                <span className="text-xs font-semibold text-slate-800 line-clamp-2">
                  {cat.name}
                </span>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Featured Services Grid */}
      <section className="py-12 bg-slate-100/70 border-y border-slate-200/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">Popular Home Services</h2>
            <p className="text-slate-600 text-sm mt-2">Book instant doorstep assistance from certified professionals</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {services.map((srv) => (
              <div
                key={srv.id}
                className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-xs hover:shadow-xl transition-all duration-300 flex flex-col"
              >
                <div className="p-5 flex-1 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between text-xs mb-2">
                      <span className="px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 font-semibold uppercase tracking-wider text-[10px]">
                        {srv.category?.name || 'General'}
                      </span>
                      <div className="flex items-center gap-1 text-amber-500 font-bold">
                        <Star className="w-3.5 h-3.5 fill-current" />
                        <span>4.9</span>
                      </div>
                    </div>

                    <h3 className="font-bold text-slate-900 text-base line-clamp-1">{srv.name}</h3>
                    <p className="text-xs text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                      {srv.short_description}
                    </p>
                  </div>

                  <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between">
                    <div>
                      <span className="text-[10px] text-slate-400 block uppercase font-bold">Starting from</span>
                      <span className="text-lg font-black text-slate-900">₹{srv.base_price}</span>
                    </div>

                    <Link
                      to={`/book/${srv.slug}`}
                      className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-xs transition"
                    >
                      Book Now
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">How HomeServe Works</h2>
          <p className="text-slate-600 text-sm mt-2">Hassle-free booking to doorstep delivery in 4 simple steps</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="w-16 h-16 rounded-2xl bg-blue-100 text-blue-700 flex items-center justify-center font-black text-xl mx-auto mb-4">
              1
            </div>
            <h3 className="font-bold text-slate-900 text-base">Select Service</h3>
            <p className="text-xs text-slate-500 mt-2 leading-relaxed">
              Browse 80+ home repair services and select a verified provider with transparent rates.
            </p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 rounded-2xl bg-blue-100 text-blue-700 flex items-center justify-center font-black text-xl mx-auto mb-4">
              2
            </div>
            <h3 className="font-bold text-slate-900 text-base">Choose Schedule</h3>
            <p className="text-xs text-slate-500 mt-2 leading-relaxed">
              Pick your preferred date and time slot. Our double-booking protection guarantees availability.
            </p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 rounded-2xl bg-blue-100 text-blue-700 flex items-center justify-center font-black text-xl mx-auto mb-4">
              3
            </div>
            <h3 className="font-bold text-slate-900 text-base">Technician Arrives</h3>
            <p className="text-xs text-slate-500 mt-2 leading-relaxed">
              Certified technician arrives on time equipped with high-grade tools and parts.
            </p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 rounded-2xl bg-blue-100 text-blue-700 flex items-center justify-center font-black text-xl mx-auto mb-4">
              4
            </div>
            <h3 className="font-bold text-slate-900 text-base">Pay & Relax</h3>
            <p className="text-xs text-slate-500 mt-2 leading-relaxed">
              Pay securely via UPI, Card or Cash. Enjoy our 30-day rework warranty.
            </p>
          </div>
        </div>
      </section>

      {/* Provider Call to Action Banner */}
      <section className="bg-gradient-to-r from-blue-700 to-indigo-800 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="max-w-xl">
            <h2 className="text-3xl font-black">Are you a Home Service Professional?</h2>
            <p className="text-blue-100 text-sm mt-3 leading-relaxed">
              Grow your business with HomeServe. Get daily verified customer leads, manage your technicians, and receive direct bank payouts with guaranteed commissions.
            </p>
          </div>
          <div className="flex items-center gap-4 shrink-0">
            <Link
              to="/register?role=provider"
              className="px-6 py-3.5 rounded-xl bg-white text-blue-700 font-bold text-sm hover:bg-blue-50 transition shadow-lg cursor-pointer"
            >
              Register as Service Partner
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
