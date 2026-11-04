import React, { useState, useEffect } from 'react';
import { 
  Users, Briefcase, CalendarCheck, IndianRupee, ShieldCheck, 
  CheckCircle, XCircle, AlertCircle, Download, Plus, Filter, Tag, MessageSquare
} from 'lucide-react';
import { api } from '../services/api';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview'); // overview, providers, bookings, categories, coupons, complaints
  const [analytics, setAnalytics] = useState(null);
  const [providers, setProviders] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [categories, setCategories] = useState([]);
  const [coupons, setCoupons] = useState([]);
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);

  // Verification modal
  const [verifModal, setVerifModal] = useState({ open: false, provider: null, status: 'approved', notes: '', commission: 15 });
  // Add category modal
  const [catModal, setCatModal] = useState({ open: false, name: '', description: '', icon: 'Wrench' });
  // Add coupon modal
  const [couponModal, setCouponModal] = useState({ open: false, code: '', discount_value: 20, discount_type: 'percentage', min_booking_amount: 500, max_discount: 200 });

  const loadAllAdminData = async () => {
    try {
      const [anly, provs, bks, cats, cpn, comps] = await Promise.all([
        api.getAdminAnalytics(),
        api.getAllProvidersAdmin(),
        api.getBookings(),
        api.getAdminCategories(),
        api.getAdminCoupons(),
        api.getComplaints()
      ]);
      setAnalytics(anly);
      setProviders(provs || []);
      setBookings(bks || []);
      setCategories(cats || []);
      setCoupons(cpn || []);
      setComplaints(comps || []);
    } catch (err) {
      console.error('Failed to load admin data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllAdminData();
  }, []);

  const handleVerifyProvider = async (e) => {
    e.preventDefault();
    try {
      await api.verifyProvider(verifModal.provider.id, {
        status: verifModal.status,
        notes: verifModal.notes,
        commission_rate: Number(verifModal.commission)
      });
      setVerifModal({ open: false, provider: null, status: 'approved', notes: '', commission: 15 });
      loadAllAdminData();
    } catch (err) {
      alert(err.message || 'Verification update failed');
    }
  };

  const handleCreateCategory = async (e) => {
    e.preventDefault();
    try {
      await api.createCategory({
        name: catModal.name,
        description: catModal.description,
        icon: catModal.icon
      });
      setCatModal({ open: false, name: '', description: '', icon: 'Wrench' });
      loadAllAdminData();
    } catch (err) {
      alert(err.message || 'Category creation failed');
    }
  };

  const handleCreateCoupon = async (e) => {
    e.preventDefault();
    try {
      await api.createCoupon({
        code: couponModal.code,
        discount_type: couponModal.discount_type,
        discount_value: Number(couponModal.discount_value),
        min_booking_amount: Number(couponModal.min_booking_amount),
        max_discount: Number(couponModal.max_discount),
        usage_limit: 500,
        is_active: true
      });
      setCouponModal({ open: false, code: '', discount_value: 20, discount_type: 'percentage', min_booking_amount: 500, max_discount: 200 });
      loadAllAdminData();
    } catch (err) {
      alert(err.message || 'Coupon creation failed');
    }
  };

  const handleExportCSV = async () => {
    try {
      const blob = await api.exportBookingsCSV();
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'homeserve_bookings_report.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('CSV export failed');
    }
  };

  const handleResolveComplaint = async (complaintId, status) => {
    const notes = prompt('Enter resolution notes for the customer:');
    if (!notes) return;
    try {
      await api.resolveComplaint(complaintId, { status, resolution_notes: notes });
      loadAllAdminData();
    } catch (err) {
      alert('Failed to resolve complaint');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-10 h-10 border-4 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const kpis = analytics?.kpis || {};

  return (
    <div className="min-h-screen bg-slate-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full bg-purple-100 text-purple-800 text-[11px] font-bold uppercase tracking-wider">
                Super Admin
              </span>
              <h1 className="text-2xl sm:text-3xl font-black text-slate-900">Control Center</h1>
            </div>
            <p className="text-xs text-slate-500 mt-1">Platform operations, provider approvals, and financial overview</p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleExportCSV}
              className="px-3.5 py-2 rounded-xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-bold flex items-center gap-1.5 shadow-xs cursor-pointer"
            >
              <Download className="w-4 h-4 text-slate-500" /> Export Bookings CSV
            </button>
          </div>
        </div>

        {/* Top KPI Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 mb-2">
              <span className="text-xs font-bold">Total Platform Revenue</span>
              <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
                <IndianRupee className="w-4 h-4" />
              </div>
            </div>
            <p className="text-2xl font-black text-slate-900">₹{kpis.total_revenue || 0}</p>
            <p className="text-[11px] text-emerald-600 font-semibold mt-1">Platform Commission: ₹{kpis.platform_commission || 0}</p>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 mb-2">
              <span className="text-xs font-bold">Total Bookings</span>
              <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                <CalendarCheck className="w-4 h-4" />
              </div>
            </div>
            <p className="text-2xl font-black text-slate-900">{kpis.total_bookings || 0}</p>
            <p className="text-[11px] text-slate-500 mt-1">{kpis.completed_bookings || 0} completed • {kpis.pending_bookings || 0} active</p>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 mb-2">
              <span className="text-xs font-bold">Registered Providers</span>
              <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
                <Briefcase className="w-4 h-4" />
              </div>
            </div>
            <p className="text-2xl font-black text-slate-900">{kpis.total_providers || 0}</p>
            <p className="text-[11px] text-amber-600 font-bold mt-1">{kpis.pending_verifications || 0} pending verification</p>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 mb-2">
              <span className="text-xs font-bold">Total Customers</span>
              <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center">
                <Users className="w-4 h-4" />
              </div>
            </div>
            <p className="text-2xl font-black text-slate-900">{kpis.total_customers || 0}</p>
            <p className="text-[11px] text-slate-500 mt-1">{kpis.total_technicians || 0} certified technicians</p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 gap-6 overflow-x-auto text-xs font-bold">
          <button
            onClick={() => setActiveTab('overview')}
            className={`pb-3 cursor-pointer whitespace-nowrap ${activeTab === 'overview' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-slate-500 hover:text-slate-800'}`}
          >
            Overview & Analytics
          </button>
          <button
            onClick={() => setActiveTab('providers')}
            className={`pb-3 cursor-pointer whitespace-nowrap relative ${activeTab === 'providers' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-slate-500 hover:text-slate-800'}`}
          >
            Providers Verification Queue
            {kpis.pending_verifications > 0 && (
              <span className="ml-1.5 px-1.5 py-0.5 rounded-full bg-amber-500 text-white text-[10px]">
                {kpis.pending_verifications}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('bookings')}
            className={`pb-3 cursor-pointer whitespace-nowrap ${activeTab === 'bookings' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-slate-500 hover:text-slate-800'}`}
          >
            All Bookings ({bookings.length})
          </button>
          <button
            onClick={() => setActiveTab('categories')}
            className={`pb-3 cursor-pointer whitespace-nowrap ${activeTab === 'categories' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-slate-500 hover:text-slate-800'}`}
          >
            Categories & Catalog
          </button>
          <button
            onClick={() => setActiveTab('coupons')}
            className={`pb-3 cursor-pointer whitespace-nowrap ${activeTab === 'coupons' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-slate-500 hover:text-slate-800'}`}
          >
            Coupons & Discounts
          </button>
          <button
            onClick={() => setActiveTab('complaints')}
            className={`pb-3 cursor-pointer whitespace-nowrap ${activeTab === 'complaints' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-slate-500 hover:text-slate-800'}`}
          >
            Support Complaints ({complaints.length})
          </button>
        </div>

        {/* TAB 1: OVERVIEW & ANALYTICS */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Category popularity */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
              <h3 className="font-bold text-sm text-slate-900 mb-4">Category Booking Breakdown</h3>
              <div className="space-y-3">
                {analytics?.category_analytics?.map((c, idx) => (
                  <div key={idx}>
                    <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                      <span>{c.category_name}</span>
                      <span>{c.booking_count} bookings</span>
                    </div>
                    <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-purple-600 rounded-full"
                        style={{ width: `${Math.min(100, (c.booking_count / Math.max(1, kpis.total_bookings)) * 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Monthly Trend Simulation Chart */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
              <h3 className="font-bold text-sm text-slate-900 mb-4">Monthly Booking & Revenue Growth</h3>
              <div className="space-y-4">
                {analytics?.monthly_trends?.map((m, idx) => (
                  <div key={idx} className="flex items-center gap-4 text-xs">
                    <span className="w-10 font-bold text-slate-500">{m.month}</span>
                    <div className="flex-1 h-6 bg-slate-100 rounded-lg overflow-hidden flex items-center px-3">
                      <div
                        className="h-full bg-blue-500 rounded-md"
                        style={{ width: `${Math.min(100, (m.bookings / 100) * 100)}%` }}
                      />
                    </div>
                    <span className="font-black text-slate-800 w-20 text-right">₹{m.revenue}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: PROVIDERS VERIFICATION QUEUE */}
        {activeTab === 'providers' && (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
            <div className="p-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="font-bold text-sm text-slate-900">Service Provider Verification Directory</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 border-b border-slate-100 text-slate-500 uppercase font-bold text-[10px]">
                  <tr>
                    <th className="p-4">Company / Trade</th>
                    <th className="p-4">Owner Name</th>
                    <th className="p-4">Registration #</th>
                    <th className="p-4">Experience</th>
                    <th className="p-4">Commission %</th>
                    <th className="p-4">Verification Status</th>
                    <th className="p-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {providers.map((p) => (
                    <tr key={p.id} className="hover:bg-slate-50">
                      <td className="p-4 font-bold text-slate-900">{p.company_name}</td>
                      <td className="p-4">{p.user?.first_name} {p.user?.last_name}</td>
                      <td className="p-4 font-mono text-slate-500">{p.business_registration_no || 'N/A'}</td>
                      <td className="p-4">{p.experience_years} years</td>
                      <td className="p-4 font-bold">{p.commission_rate}%</td>
                      <td className="p-4">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                          p.verification_status === 'approved' ? 'bg-emerald-100 text-emerald-800' :
                          p.verification_status === 'rejected' ? 'bg-red-100 text-red-800' :
                          'bg-amber-100 text-amber-800'
                        }`}>
                          {p.verification_status}
                        </span>
                      </td>
                      <td className="p-4 text-right">
                        <button
                          onClick={() => setVerifModal({ open: true, provider: p, status: p.verification_status, notes: p.verification_notes || '', commission: p.commission_rate })}
                          className="px-3 py-1 rounded-lg bg-purple-600 text-white font-bold text-xs hover:bg-purple-700 cursor-pointer"
                        >
                          Review & Verify
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 3: ALL BOOKINGS */}
        {activeTab === 'bookings' && (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 border-b border-slate-100 text-slate-500 uppercase font-bold text-[10px]">
                  <tr>
                    <th className="p-4">Code</th>
                    <th className="p-4">Service</th>
                    <th className="p-4">Customer</th>
                    <th className="p-4">Date & Slot</th>
                    <th className="p-4">Amount</th>
                    <th className="p-4">Status</th>
                    <th className="p-4 text-right">Tracking</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {bookings.map((b) => (
                    <tr key={b.id} className="hover:bg-slate-50">
                      <td className="p-4 font-mono font-bold text-slate-900">{b.booking_code}</td>
                      <td className="p-4 font-medium">{b.service?.name}</td>
                      <td className="p-4">{b.customer?.user?.first_name} {b.customer?.user?.last_name}</td>
                      <td className="p-4">{b.scheduled_date} ({b.scheduled_slot})</td>
                      <td className="p-4 font-bold text-slate-900">₹{b.final_amount}</td>
                      <td className="p-4">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                          b.status === 'completed' ? 'bg-emerald-100 text-emerald-800' :
                          b.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {b.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="p-4 text-right">
                        <a href={`/bookings/${b.id}`} className="text-blue-600 font-bold hover:underline">
                          View
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 4: CATEGORIES */}
        {activeTab === 'categories' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="font-bold text-sm text-slate-900">Active Service Categories</h3>
              <button
                onClick={() => setCatModal({ open: true, name: '', description: '', icon: 'Wrench' })}
                className="px-3.5 py-1.5 rounded-xl bg-purple-600 text-white font-bold text-xs flex items-center gap-1.5 shadow-xs cursor-pointer"
              >
                <Plus className="w-4 h-4" /> Add Category
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {categories.map((c) => (
                <div key={c.id} className="bg-white p-4 rounded-xl border border-slate-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-slate-900 text-sm">{c.name}</span>
                    <span className="text-[10px] font-mono text-slate-400">#{c.sort_order}</span>
                  </div>
                  <p className="text-xs text-slate-500 line-clamp-2">{c.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 5: COUPONS */}
        {activeTab === 'coupons' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="font-bold text-sm text-slate-900">Discount Coupons & Offers</h3>
              <button
                onClick={() => setCouponModal({ open: true, code: '', discount_value: 20, discount_type: 'percentage', min_booking_amount: 500, max_discount: 200 })}
                className="px-3.5 py-1.5 rounded-xl bg-purple-600 text-white font-bold text-xs flex items-center gap-1.5 shadow-xs cursor-pointer"
              >
                <Plus className="w-4 h-4" /> Create Coupon
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {coupons.map((cp) => (
                <div key={cp.id} className="bg-white p-5 rounded-xl border border-slate-200 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-black text-sm text-purple-700 bg-purple-50 px-2 py-0.5 rounded">
                      {cp.code}
                    </span>
                    <span className="text-xs text-emerald-600 font-bold">
                      {cp.discount_type === 'percentage' ? `${cp.discount_value}% OFF` : `₹${cp.discount_value} FLAT`}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500">{cp.description || 'Promotional Discount'}</p>
                  <div className="pt-2 border-t border-slate-100 flex justify-between text-[11px] text-slate-400">
                    <span>Min Booking: ₹{cp.min_booking_amount}</span>
                    <span>Used: {cp.times_used} times</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 6: SUPPORT COMPLAINTS */}
        {activeTab === 'complaints' && (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 border-b border-slate-100 text-slate-500 uppercase font-bold text-[10px]">
                  <tr>
                    <th className="p-4">Ticket #</th>
                    <th className="p-4">Subject</th>
                    <th className="p-4">Booking</th>
                    <th className="p-4">Priority</th>
                    <th className="p-4">Status</th>
                    <th className="p-4">Notes</th>
                    <th className="p-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {complaints.length === 0 ? (
                    <tr><td colSpan="7" className="p-6 text-center text-slate-400">No support complaints registered</td></tr>
                  ) : (
                    complaints.map((comp) => (
                      <tr key={comp.id} className="hover:bg-slate-50">
                        <td className="p-4 font-mono font-bold">#{comp.id}</td>
                        <td className="p-4 font-semibold text-slate-800">{comp.subject}</td>
                        <td className="p-4">Booking #{comp.booking_id}</td>
                        <td className="p-4">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                            comp.priority === 'critical' ? 'bg-red-100 text-red-800' :
                            comp.priority === 'high' ? 'bg-amber-100 text-amber-800' :
                            'bg-slate-100 text-slate-700'
                          }`}>
                            {comp.priority}
                          </span>
                        </td>
                        <td className="p-4 font-bold capitalize">{comp.status}</td>
                        <td className="p-4 text-slate-500">{comp.resolution_notes || 'Pending resolution'}</td>
                        <td className="p-4 text-right space-x-2">
                          <button
                            onClick={() => handleResolveComplaint(comp.id, 'resolved')}
                            className="px-2.5 py-1 rounded-lg bg-emerald-600 text-white font-bold hover:bg-emerald-700 cursor-pointer"
                          >
                            Resolve
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* MODAL: Provider Verification */}
        {verifModal.open && (
          <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-slate-200">
              <h3 className="font-bold text-sm text-slate-900 mb-2">Review Provider Verification</h3>
              <p className="text-xs text-slate-500 mb-4">{verifModal.provider?.company_name}</p>

              <form onSubmit={handleVerifyProvider} className="space-y-4">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Status Decision</label>
                  <select
                    value={verifModal.status}
                    onChange={(e) => setVerifModal({ ...verifModal, status: e.target.value })}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                  >
                    <option value="approved">Approved</option>
                    <option value="rejected">Rejected</option>
                    <option value="pending">Pending</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Commission Rate (%)</label>
                  <input
                    type="number"
                    value={verifModal.commission}
                    onChange={(e) => setVerifModal({ ...verifModal, commission: e.target.value })}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Verification Remarks</label>
                  <textarea
                    rows="3"
                    value={verifModal.notes}
                    onChange={(e) => setVerifModal({ ...verifModal, notes: e.target.value })}
                    placeholder="Enter compliance and KYC verification notes..."
                    className="w-full p-3 text-xs rounded-xl border border-slate-200"
                  />
                </div>

                <div className="flex gap-2">
                  <button type="button" onClick={() => setVerifModal({ open: false, provider: null })} className="w-1/2 py-2 rounded-xl border text-xs font-bold">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 rounded-xl bg-purple-600 text-white text-xs font-bold">Save Decision</button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* MODAL: Create Category */}
        {catModal.open && (
          <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-slate-200">
              <h3 className="font-bold text-sm text-slate-900 mb-3">Add Service Category</h3>
              <form onSubmit={handleCreateCategory} className="space-y-4">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Category Name</label>
                  <input
                    type="text"
                    required
                    value={catModal.name}
                    onChange={(e) => setCatModal({ ...catModal, name: e.target.value })}
                    placeholder="e.g. Smart Home Installation"
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Description</label>
                  <textarea
                    rows="2"
                    value={catModal.description}
                    onChange={(e) => setCatModal({ ...catModal, description: e.target.value })}
                    className="w-full p-2.5 text-xs rounded-xl border border-slate-200"
                  />
                </div>
                <div className="flex gap-2">
                  <button type="button" onClick={() => setCatModal({ open: false })} className="w-1/2 py-2 rounded-xl border text-xs font-bold">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 rounded-xl bg-purple-600 text-white text-xs font-bold">Save Category</button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* MODAL: Create Coupon */}
        {couponModal.open && (
          <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-slate-200">
              <h3 className="font-bold text-sm text-slate-900 mb-3">Create Promo Coupon</h3>
              <form onSubmit={handleCreateCoupon} className="space-y-4">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Coupon Code</label>
                  <input
                    type="text"
                    required
                    value={couponModal.code}
                    onChange={(e) => setCouponModal({ ...couponModal, code: e.target.value.toUpperCase() })}
                    placeholder="e.g. FLASH30"
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 uppercase font-mono font-bold"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-semibold text-slate-700 block mb-1">Discount Type</label>
                    <select
                      value={couponModal.discount_type}
                      onChange={(e) => setCouponModal({ ...couponModal, discount_type: e.target.value })}
                      className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                    >
                      <option value="percentage">Percentage (%)</option>
                      <option value="fixed">Fixed (₹)</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-700 block mb-1">Discount Value</label>
                    <input
                      type="number"
                      required
                      value={couponModal.discount_value}
                      onChange={(e) => setCouponModal({ ...couponModal, discount_value: e.target.value })}
                      className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <button type="button" onClick={() => setCouponModal({ open: false })} className="w-1/2 py-2 rounded-xl border text-xs font-bold">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 rounded-xl bg-purple-600 text-white text-xs font-bold">Create Coupon</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
