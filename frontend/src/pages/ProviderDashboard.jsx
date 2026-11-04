import React, { useState, useEffect } from 'react';
import { 
  Briefcase, IndianRupee, Star, Users, CheckCircle, Clock, 
  UserCheck, Plus, AlertCircle, X, ShieldCheck 
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function ProviderDashboard() {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [bookings, setBookings] = useState([]);
  const [technicians, setTechnicians] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modal: Assign Technician
  const [assignModal, setAssignModal] = useState({ open: false, booking: null, technicianId: '', notes: '' });
  // Modal: Add Technician
  const [techModal, setTechModal] = useState({ open: false, email: '', password: '', first_name: '', last_name: '', phone: '', specialization: 'Electrician' });

  const loadData = async () => {
    try {
      const [anly, bks, techs] = await Promise.all([
        api.getProviderAnalytics(),
        api.getBookings(),
        api.getTechnicians()
      ]);
      setAnalytics(anly);
      setBookings(bks || []);
      setTechnicians(techs || []);
      if (techs && techs.length > 0) {
        setAssignModal(prev => ({ ...prev, technicianId: techs[0].id }));
      }
    } catch (err) {
      console.error('Failed to load provider data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleUpdateStatus = async (bookingId, status) => {
    try {
      await api.updateBookingStatus(bookingId, status);
      loadData();
    } catch (err) {
      alert(err.message || 'Status update failed');
    }
  };

  const handleAssignTechnician = async (e) => {
    e.preventDefault();
    if (!assignModal.technicianId) {
      alert('Please select a technician');
      return;
    }
    try {
      await api.assignTechnician(assignModal.booking.id, Number(assignModal.technicianId), assignModal.notes);
      setAssignModal({ open: false, booking: null, technicianId: '', notes: '' });
      loadData();
    } catch (err) {
      alert(err.message || 'Assignment failed');
    }
  };

  const handleCreateTechnician = async (e) => {
    e.preventDefault();
    try {
      await api.createTechnician(techModal);
      setTechModal({ open: false, email: '', password: '', first_name: '', last_name: '', phone: '', specialization: 'Electrician' });
      loadData();
    } catch (err) {
      alert(err.message || 'Failed to add technician');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Verification Status Banner */}
        <div className={`p-4 rounded-2xl border flex items-center justify-between text-xs font-semibold ${
          analytics?.verification_status === 'approved'
            ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
            : 'bg-amber-50 border-amber-200 text-amber-800'
        }`}>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5" />
            <span>
              Provider Status: <strong className="uppercase">{analytics?.verification_status || 'Approved'}</strong> • 
              Verified Company: {analytics?.company_name}
            </span>
          </div>
          <span className="font-mono bg-white px-2.5 py-1 rounded-md border border-slate-200">
            Commission Rate: 15%
          </span>
        </div>

        {/* Top KPIs */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <div className="text-xs text-slate-500 font-bold mb-1">Net Earnings (After Commission)</div>
            <p className="text-2xl font-black text-slate-900">₹{analytics?.total_earnings || 0}</p>
            <p className="text-[11px] text-slate-400 mt-1">Gross Invoiced: ₹{analytics?.gross_revenue || 0}</p>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <div className="text-xs text-slate-500 font-bold mb-1">Customer Rating</div>
            <div className="flex items-center gap-1.5 mt-1">
              <Star className="w-5 h-5 text-amber-500 fill-current" />
              <span className="text-2xl font-black text-slate-900">{analytics?.rating_avg || 4.9}</span>
              <span className="text-xs text-slate-400">({analytics?.rating_count || 38})</span>
            </div>
            <p className="text-[11px] text-emerald-600 font-bold mt-1">Top Rated Partner</p>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <div className="text-xs text-slate-500 font-bold mb-1">Pending Job Requests</div>
            <p className="text-2xl font-black text-amber-600">{analytics?.pending_bookings || 0}</p>
            <p className="text-[11px] text-slate-400 mt-1">Action required</p>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <div className="text-xs text-slate-500 font-bold mb-1">Field Technicians</div>
            <p className="text-2xl font-black text-slate-900">{technicians.length}</p>
            <p className="text-[11px] text-slate-400 mt-1">Ready for dispatch</p>
          </div>
        </div>

        {/* Incoming & Active Bookings Table */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="p-5 border-b border-slate-100 flex items-center justify-between">
            <h2 className="font-bold text-sm text-slate-900">Manage Service Bookings & Dispatch</h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 border-b border-slate-100 text-slate-500 uppercase font-bold text-[10px]">
                <tr>
                  <th className="p-4">Code</th>
                  <th className="p-4">Service</th>
                  <th className="p-4">Schedule</th>
                  <th className="p-4">Customer</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Assigned Tech</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {bookings.length === 0 ? (
                  <tr><td colSpan="7" className="p-6 text-center text-slate-400">No bookings available</td></tr>
                ) : (
                  bookings.map((b) => {
                    const assigned = b.assignments?.[0]?.technician;
                    return (
                      <tr key={b.id} className="hover:bg-slate-50">
                        <td className="p-4 font-mono font-bold text-slate-900">{b.booking_code}</td>
                        <td className="p-4 font-semibold text-slate-800">{b.service?.name}</td>
                        <td className="p-4">{b.scheduled_date} ({b.scheduled_slot})</td>
                        <td className="p-4">{b.customer?.user?.first_name} {b.customer?.user?.last_name}</td>
                        <td className="p-4">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                            b.status === 'completed' ? 'bg-emerald-100 text-emerald-800' :
                            b.status === 'pending' ? 'bg-amber-100 text-amber-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {b.status.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="p-4">
                          {assigned ? (
                            <span className="font-medium text-slate-700">{assigned.user?.first_name} {assigned.user?.last_name}</span>
                          ) : (
                            <span className="text-slate-400 italic">Unassigned</span>
                          )}
                        </td>
                        <td className="p-4 text-right space-x-1.5">
                          {b.status === 'pending' && (
                            <>
                              <button
                                onClick={() => handleUpdateStatus(b.id, 'confirmed')}
                                className="px-2.5 py-1 rounded-lg bg-emerald-600 text-white font-bold cursor-pointer hover:bg-emerald-700"
                              >
                                Accept
                              </button>
                              <button
                                onClick={() => handleUpdateStatus(b.id, 'rejected')}
                                className="px-2.5 py-1 rounded-lg bg-red-50 text-red-600 font-bold cursor-pointer hover:bg-red-100"
                              >
                                Reject
                              </button>
                            </>
                          )}

                          {['confirmed', 'provider_assigned'].includes(b.status) && (
                            <button
                              onClick={() => setAssignModal({ open: true, booking: b, technicianId: technicians[0]?.id || '', notes: '' })}
                              className="px-2.5 py-1 rounded-lg bg-blue-600 text-white font-bold cursor-pointer hover:bg-blue-700"
                            >
                              {assigned ? 'Reassign Tech' : 'Assign Tech'}
                            </button>
                          )}

                          <a href={`/bookings/${b.id}`} className="px-2.5 py-1 rounded-lg border text-slate-600 font-bold hover:bg-slate-50">
                            Details
                          </a>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Technicians Manager Grid */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h3 className="font-bold text-sm text-slate-900">Field Technicians Roster</h3>
              <p className="text-xs text-slate-500">Manage technicians assigned to your service company</p>
            </div>
            <button
              onClick={() => setTechModal({ ...techModal, open: true })}
              className="px-3.5 py-1.5 rounded-xl bg-blue-600 text-white font-bold text-xs flex items-center gap-1.5 cursor-pointer shadow-xs"
            >
              <Plus className="w-4 h-4" /> Add Technician
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {technicians.map((t) => (
              <div key={t.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex items-center justify-between">
                <div>
                  <p className="font-bold text-xs text-slate-900">{t.user?.first_name} {t.user?.last_name}</p>
                  <p className="text-[11px] text-blue-600 font-semibold">{t.specialization}</p>
                  <p className="text-[11px] text-slate-400 mt-1">{t.user?.email}</p>
                </div>
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                  t.status === 'available' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                }`}>
                  {t.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* MODAL: Assign Technician */}
        {assignModal.open && (
          <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-slate-200">
              <h3 className="font-bold text-sm text-slate-900 mb-1">Assign Technician</h3>
              <p className="text-xs text-slate-500 mb-4">{assignModal.booking?.booking_code} - {assignModal.booking?.service?.name}</p>

              <form onSubmit={handleAssignTechnician} className="space-y-4">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Select Field Technician</label>
                  <select
                    value={assignModal.technicianId}
                    onChange={(e) => setAssignModal({ ...assignModal, technicianId: e.target.value })}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                  >
                    {technicians.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.user?.first_name} {t.user?.last_name} ({t.specialization}) - {t.status}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Job Instructions / Notes</label>
                  <textarea
                    rows="2"
                    value={assignModal.notes}
                    onChange={(e) => setAssignModal({ ...assignModal, notes: e.target.value })}
                    placeholder="Carry spare capacitor and safety gloves..."
                    className="w-full p-2.5 text-xs rounded-xl border border-slate-200"
                  />
                </div>

                <div className="flex gap-2">
                  <button type="button" onClick={() => setAssignModal({ open: false, booking: null })} className="w-1/2 py-2 rounded-xl border text-xs font-bold">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold">Dispatch Technician</button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* MODAL: Add Technician */}
        {techModal.open && (
          <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-slate-200">
              <h3 className="font-bold text-sm text-slate-900 mb-3">Add New Technician</h3>
              <form onSubmit={handleCreateTechnician} className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-semibold text-slate-700 block mb-1">First Name</label>
                    <input
                      type="text"
                      required
                      value={techModal.first_name}
                      onChange={(e) => setTechModal({ ...techModal, first_name: e.target.value })}
                      className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-700 block mb-1">Last Name</label>
                    <input
                      type="text"
                      required
                      value={techModal.last_name}
                      onChange={(e) => setTechModal({ ...techModal, last_name: e.target.value })}
                      className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Email</label>
                  <input
                    type="email"
                    required
                    value={techModal.email}
                    onChange={(e) => setTechModal({ ...techModal, email: e.target.value })}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Password</label>
                  <input
                    type="password"
                    required
                    value={techModal.password}
                    onChange={(e) => setTechModal({ ...techModal, password: e.target.value })}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Specialization</label>
                  <input
                    type="text"
                    required
                    value={techModal.specialization}
                    onChange={(e) => setTechModal({ ...techModal, specialization: e.target.value })}
                    placeholder="e.g. Master AC Electrician"
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                  />
                </div>

                <div className="flex gap-2 pt-2">
                  <button type="button" onClick={() => setTechModal({ ...techModal, open: false })} className="w-1/2 py-2 rounded-xl border text-xs font-bold">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold">Save Technician</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
