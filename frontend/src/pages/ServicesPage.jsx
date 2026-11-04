import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Search, Filter, Clock, Star, ArrowRight, Wrench, X } from 'lucide-react';
import { api } from '../services/api';

export default function ServicesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [categories, setCategories] = useState([]);
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get('category') || '');
  const [searchKeyword, setSearchKeyword] = useState(searchParams.get('search') || '');
  const [maxPrice, setMaxPrice] = useState(3000);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [cats, srvs] = await Promise.all([
          api.getCategories(),
          api.getServices()
        ]);
        setCategories(cats || []);
        setServices(srvs || []);
      } catch (err) {
        console.error('Failed to load services', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  // Sync category param
  useEffect(() => {
    const cat = searchParams.get('category');
    if (cat) setSelectedCategory(cat);
    const q = searchParams.get('search');
    if (q) setSearchKeyword(q);
  }, [searchParams]);

  const filteredServices = services.filter((srv) => {
    // Category match
    if (selectedCategory && srv.category?.slug !== selectedCategory) {
      return false;
    }
    // Price match
    if (srv.base_price > maxPrice) {
      return false;
    }
    // Search keyword match
    if (searchKeyword.trim()) {
      const q = searchKeyword.toLowerCase();
      const matchName = srv.name.toLowerCase().includes(q);
      const matchDesc = srv.short_description?.toLowerCase().includes(q) || false;
      if (!matchName && !matchDesc) return false;
    }
    return true;
  });

  const clearFilters = () => {
    setSelectedCategory('');
    setSearchKeyword('');
    setMaxPrice(3000);
    setSearchParams({});
  };

  return (
    <div className="min-h-screen bg-slate-50 py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-black text-slate-900">Explore Home Services</h1>
          <p className="text-sm text-slate-600 mt-1">Browse, filter, and book verified professionals for your home needs</p>
        </div>

        {/* Layout: Sidebar + Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Filters Sidebar */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs h-fit space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center gap-2 font-bold text-slate-900 text-sm">
                <Filter className="w-4 h-4 text-blue-600" />
                <span>Filters</span>
              </div>
              {(selectedCategory || searchKeyword || maxPrice < 3000) && (
                <button
                  onClick={clearFilters}
                  className="text-xs text-blue-600 hover:underline flex items-center gap-1 cursor-pointer"
                >
                  <X className="w-3.5 h-3.5" /> Clear all
                </button>
              )}
            </div>

            {/* Keyword Search */}
            <div>
              <label className="text-xs font-bold text-slate-700 block mb-2">Search Service</label>
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  value={searchKeyword}
                  onChange={(e) => setSearchKeyword(e.target.value)}
                  placeholder="e.g. AC Jet, Switchboard..."
                  className="w-full pl-9 pr-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-hidden focus:border-blue-600"
                />
              </div>
            </div>

            {/* Categories */}
            <div>
              <label className="text-xs font-bold text-slate-700 block mb-2">Categories</label>
              <div className="space-y-1.5 max-h-60 overflow-y-auto pr-1">
                <button
                  onClick={() => {
                    setSelectedCategory('');
                    searchParams.delete('category');
                    setSearchParams(searchParams);
                  }}
                  className={`w-full text-left px-3 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer flex items-center justify-between ${
                    selectedCategory === '' ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <span>All Categories</span>
                  <span className="text-[10px] opacity-80">{services.length}</span>
                </button>
                {categories.map((c) => {
                  const count = services.filter((s) => s.category?.id === c.id).length;
                  return (
                    <button
                      key={c.id}
                      onClick={() => {
                        setSelectedCategory(c.slug);
                        setSearchParams({ category: c.slug });
                      }}
                      className={`w-full text-left px-3 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer flex items-center justify-between ${
                        selectedCategory === c.slug ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-100'
                      }`}
                    >
                      <span className="truncate">{c.name}</span>
                      <span className="text-[10px] opacity-80">{count}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Price Range Slider */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-bold text-slate-700">Max Budget</label>
                <span className="text-xs font-black text-blue-600">Up to ₹{maxPrice}</span>
              </div>
              <input
                type="range"
                min="200"
                max="3000"
                step="100"
                value={maxPrice}
                onChange={(e) => setMaxPrice(Number(e.target.value))}
                className="w-full accent-blue-600 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                <span>₹200</span>
                <span>₹3,000+</span>
              </div>
            </div>
          </div>

          {/* Service Cards Grid */}
          <div className="lg:col-span-3">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs text-slate-500 font-medium">
                Showing <strong className="text-slate-800">{filteredServices.length}</strong> available services
              </span>
            </div>

            {filteredServices.length === 0 ? (
              <div className="bg-white rounded-2xl p-12 text-center border border-slate-200">
                <Wrench className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                <h3 className="text-base font-bold text-slate-800">No matching services found</h3>
                <p className="text-xs text-slate-500 mt-1">Try adjusting your filters or keyword query.</p>
                <button
                  onClick={clearFilters}
                  className="mt-4 px-4 py-2 rounded-xl bg-blue-600 text-white text-xs font-semibold cursor-pointer"
                >
                  Reset Filters
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {filteredServices.map((srv) => (
                  <div
                    key={srv.id}
                    className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-xs hover:shadow-lg transition flex flex-col justify-between"
                  >
                    <div className="p-5">
                      <div className="flex items-center justify-between text-xs mb-3">
                        <span className="px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 font-bold uppercase tracking-wider text-[10px]">
                          {srv.category?.name || 'Home Care'}
                        </span>
                        <div className="flex items-center gap-1 text-slate-500 text-xs">
                          <Clock className="w-3.5 h-3.5" />
                          <span>{srv.duration_minutes} mins</span>
                        </div>
                      </div>

                      <h3 className="font-bold text-slate-900 text-base mb-1.5">{srv.name}</h3>
                      <p className="text-xs text-slate-500 line-clamp-3 leading-relaxed">
                        {srv.short_description || srv.full_description}
                      </p>
                    </div>

                    <div className="p-5 pt-0">
                      <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
                        <div>
                          <span className="text-[10px] text-slate-400 font-bold uppercase block">Price</span>
                          <span className="text-lg font-black text-slate-900">₹{srv.base_price}</span>
                        </div>

                        <Link
                          to={`/book/${srv.slug}`}
                          className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold transition shadow-xs cursor-pointer"
                        >
                          Book Slot
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
