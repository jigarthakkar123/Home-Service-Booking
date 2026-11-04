import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Calendar, MapPin, Award, FileText, Plus, Trash2, CheckCircle2, Clock, Star 
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function CustomerDashboard() {
  const { user } = useAuth();
  const [bookings, setBookings] = useState([]);
  const [addresses, setAddresses] = useState([]);
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);

  // Address modal
  const [showAddressModal, setShowAddressModal] = useState(false);
  const [newAddr, setNewAddr] = useState({
    title: 'Home',
    address_line: '',
    city: 'Bengaluru',
    state: 'Karnataka',
    postal_code: '560034',
    landmark: '',
    is_default: true
  });

  const loadData = async () => {
    try {
      const [bks, addrs, comps] = await Promise.all([
        api.getBookings(),
        api.getAddresses(),
        api.getComplaints()
      ]);
      setBookings(bks || []);
      setAddresses(addrs || []);
      setComplaints(comps || []);
    } catch (err) {
      console.error('Failed to load customer dashboard', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAddAddress = async (e) => {
    e.preventDefault();
    try {
      await api.addAddress(newAddr);
      setShowAddressModal(false);
      setNewAddr({ title: 'Home', address_line: '', city: 'Bengaluru', state: 'Karnataka', postal_code: '560034', landmark: '', is_default: false });
      loadData();
    } catch (err) {
      alert(err.message || 'Failed to add address');
    }
  };

  const handleDeleteAddress = async (id) => {
    if (!window.confirm('Delete this address?')) return;
    try {
      await api.deleteAddress(id);
      loadData();
    } catch (err) {
      alert(err.message || 'Failed to delete address');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const activeBookings = bookings.filter(b => !['completed', 'cancelled', 'rejected'].includes(b.status));
  const completedBookings = bookings.filter(b => b.status === 'completed');

  return (
    <div className="min-h-screen bg-slate-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Welcome Banner */}
        <div className="bg-gradient-to-r from-blue-700 to-indigo-800 rounded-3xl p-6 sm:p-8 text-white shadow-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="px-2.5 py-0.5 rounded-full bg-blue-500/20 border border-blue-400/30 text-[11px] font-bold uppercase tracking-wider">
              Customer Account
            </span>
            <h1 className="text-2xl sm:text-3xl font-black mt-2">
              Welcome back, {user?.first_name}!
            </h1>
            <p className="text-blue-100 text-xs sm:text-sm mt-1">
              Track appointments, manage addresses, and view your service guarantee invoices.
            </p>
          </div>

          <div className="flex items-center gap-4 bg-white/10 backdrop-blur-md p-4 rounded-2xl border border-white/15">
            <Award className="w-8 h-8 text-amber-300" />
            <div>
              <div className="text-xl font-black">{user?.customer?.loyalty_points || 120} pts</div>
              <div className="text-[11px] text-blue-200">HomeServe Club Loyalty</div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <Calendar className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-black text-slate-900">{activeBookings.length}</div>
              <div className="text-xs text-slate-500 font-semibold">Active Bookings</div>
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-black text-slate-900">{completedBookings.length}</div>
              <div className="text-xs text-slate-500 font-semibold">Completed Services</div>
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
              <MapPin className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-black text-slate-900">{addresses.length}</div>
              <div className="text-xs text-slate-500 font-semibold">Saved Addresses</div>
            </div>
          </div>
        </div>

        {/* Bookings Section */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="p-5 border-b border-slate-100 flex items-center justify-between">
            <h2 className="font-bold text-sm text-slate-900">My Appointments & Bookings</h2>
            <Link to="/services" className="px-3.5 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs flex items-center gap-1.5 shadow-xs">
              <Plus className="w-3.5 h-3.5" /> Book New Service
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 border-b border-slate-100 text-slate-500 uppercase font-bold text-[10px]">
                <tr>
                  <th className="p-4">Booking ID</th>
                  <th className="p-4">Service</th>
                  <th className="p-4">Provider</th>
                  <th className="p-4">Date & Slot</th>
                  <th className="p-4">Amount</th>
                  <th className="p-4">Status</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {bookings.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="p-8 text-center text-slate-400">
                      You haven't placed any bookings yet.
                    </td>
                  </tr>
                ) : (
                  bookings.map((b) => (
                    <tr key={b.id} className="hover:bg-slate-50">
                      <td className="p-4 font-mono font-bold text-slate-900">{b.booking_code}</td>
                      <td className="p-4 font-bold text-slate-800">{b.service?.name}</td>
                      <td className="p-4 text-slate-600">{b.provider?.company_name}</td>
                      <td className="p-4 text-slate-600">{b.scheduled_date} ({b.scheduled_slot})</td>
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
                      <td className="p-4 text-right space-x-2">
                        <Link
                          to={`/bookings/${b.id}`}
                          className="px-2.5 py-1 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 font-bold"
                        >
                          Track
                        </Link>
                        <Link
                          to={`/invoices/${b.id}`}
                          className="px-2.5 py-1 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 font-bold"
                        >
                          Invoice
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Addresses & Support Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Saved Addresses */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-bold text-sm text-slate-900">Saved Service Addresses</h3>
              <button
                onClick={() => setShowAddressModal(true)}
                className="text-xs text-blue-600 font-bold hover:underline flex items-center gap-1 cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5" /> Add Address
              </button>
            </div>

            <div className="space-y-3">
              {addresses.map((addr) => (
                <div key={addr.id} className="p-3.5 rounded-xl border border-slate-100 bg-slate-50 flex items-start justify-between">
                  <div className="text-xs">
                    <span className="font-bold text-slate-800 uppercase text-[10px] bg-white border border-slate-200 px-2 py-0.5 rounded">
                      {addr.title}
                    </span>
                    <p className="font-medium text-slate-800 mt-1">{addr.address_line}</p>
                    <p className="text-slate-500">{addr.city}, {addr.state} - {addr.postal_code}</p>
                  </div>
                  <button
                    onClick={() => handleDeleteAddress(addr.id)}
                    className="p-1.5 text-slate-400 hover:text-red-600 rounded-lg cursor-pointer"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Support Tickets */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
            <h3 className="font-bold text-sm text-slate-900 pb-3 border-b border-slate-100">
              Recent Support Tickets & Complaints
            </h3>
            {complaints.length === 0 ? (
              <p className="text-xs text-slate-400 py-4 text-center">No active support requests</p>
            ) : (
              <div className="space-y-3">
                {complaints.map((comp) => (
                  <div key={comp.id} className="p-3 rounded-xl border border-slate-100 text-xs space-y-1">
                    <div className="flex justify-between font-bold">
                      <span className="text-slate-900">#{comp.id} - {comp.subject}</span>
                      <span className="capitalize text-blue-600 font-bold">{comp.status}</span>
                    </div>
                    <p className="text-slate-500 text-[11px]">{comp.description}</p>
                    {comp.resolution_notes && (
                      <p className="text-[11px] text-emerald-700 font-semibold bg-emerald-50 p-1.5 rounded">
                        Resolution: {comp.resolution_notes}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* MODAL: Add Address */}
        {showAddressModal && (
          <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-slate-200">
              <h3 className="font-bold text-sm text-slate-900 mb-3">Add Service Address</h3>
              <form onSubmit={handleAddAddress} className="space-y-4">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Title</label>
                  <select
                    value={newAddr.title}
                    onChange={(e) => setNewAddr({ ...newAddr, title: e.target.value })}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                  >
                    <option value="Home">Home</option>
                    <option value="Office">Office</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Address Line</label>
                  <input
                    type="text"
                    required
                    value={newAddr.address_line}
                    onChange={(e) => setNewAddr({ ...newAddr, address_line: e.target.value })}
                    placeholder="Flat / Building / Street"
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-semibold text-slate-700 block mb-1">City</label>
                    <input
                      type="text"
                      required
                      value={newAddr.city}
                      onChange={(e) => setNewAddr({ ...newAddr, city: e.target.value })}
                      className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-700 block mb-1">Postal Code</label>
                    <input
                      type="text"
                      required
                      value={newAddr.postal_code}
                      onChange={(e) => setNewAddr({ ...newAddr, postal_code: e.target.value })}
                      className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <button type="button" onClick={() => setShowAddressModal(false)} className="w-1/2 py-2 rounded-xl border text-xs font-bold">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold">Save Address</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
