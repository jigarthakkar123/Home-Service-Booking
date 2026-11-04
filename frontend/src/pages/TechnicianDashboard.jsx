import React, { useState, useEffect } from 'react';
import { 
  Wrench, MapPin, Phone, Clock, CheckCircle2, 
  Upload, AlertCircle, Calendar 
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function TechnicianDashboard() {
  const { user } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  // Status update modal
  const [statusModal, setStatusModal] = useState({
    open: false,
    assignmentId: null,
    status: 'arrived',
    remarks: '',
    images: []
  });

  const loadJobs = async () => {
    try {
      const data = await api.getMyAssignedJobs();
      setJobs(data || []);
    } catch (err) {
      console.error('Failed to load technician jobs', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
    const interval = setInterval(loadJobs, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleUpdateStatus = async (e) => {
    e.preventDefault();
    try {
      await api.updateJobStatus(statusModal.assignmentId, {
        status: statusModal.status,
        remarks: statusModal.remarks,
        completion_images: statusModal.images
      });
      setStatusModal({ open: false, assignmentId: null, status: 'arrived', remarks: '', images: [] });
      loadJobs();
    } catch (err) {
      alert(err.message || 'Status update failed');
    }
  };

  const handleUploadProof = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const res = await api.uploadFile(file);
      setStatusModal(prev => ({ ...prev, images: [...prev.images, res.url] }));
    } catch (err) {
      alert('Upload failed');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-10 h-10 border-4 border-amber-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const activeJobs = jobs.filter(j => j.assignment_status !== 'completed');
  const finishedJobs = jobs.filter(j => j.assignment_status === 'completed');

  return (
    <div className="min-h-screen bg-slate-50 py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-200 gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 text-[11px] font-bold uppercase tracking-wider">
                Field Technician
              </span>
              <h1 className="text-2xl sm:text-3xl font-black text-slate-900">
                Hi, {user?.first_name}!
              </h1>
            </div>
            <p className="text-xs text-slate-500 mt-1">Specialization: {user?.technician?.specialization || 'Master Technician'}</p>
          </div>

          <div className="flex items-center gap-3">
            <div className="px-4 py-2 rounded-xl bg-white border border-slate-200 shadow-xs text-xs">
              <span className="text-slate-400 font-bold block uppercase text-[10px]">Active Jobs</span>
              <span className="text-lg font-black text-slate-900">{activeJobs.length}</span>
            </div>
            <div className="px-4 py-2 rounded-xl bg-white border border-slate-200 shadow-xs text-xs">
              <span className="text-slate-400 font-bold block uppercase text-[10px]">Completed</span>
              <span className="text-lg font-black text-emerald-600">{finishedJobs.length}</span>
            </div>
          </div>
        </div>

        {/* Active Assignments */}
        <div className="space-y-4">
          <h2 className="text-base font-bold text-slate-900">Current Job Assignments</h2>

          {activeJobs.length === 0 ? (
            <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center text-xs text-slate-400">
              No active jobs assigned at the moment. Stand by for new dispatches.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {activeJobs.map((j) => (
                <div key={j.assignment_id} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-black text-sm text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                      {j.booking.booking_code}
                    </span>
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                      j.assignment_status === 'in_progress' ? 'bg-amber-100 text-amber-800' :
                      j.assignment_status === 'arrived' ? 'bg-purple-100 text-purple-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {j.assignment_status}
                    </span>
                  </div>

                  <div>
                    <h3 className="font-bold text-base text-slate-900">{j.booking.service_name}</h3>
                    <p className="text-xs text-slate-500 mt-1 flex items-center gap-2">
                      <Calendar className="w-3.5 h-3.5" />
                      {j.booking.scheduled_date} ({j.booking.scheduled_slot})
                    </p>
                  </div>

                  {/* Customer details */}
                  <div className="p-3 rounded-xl bg-slate-50 text-xs text-slate-700 space-y-1">
                    <p className="font-bold">{j.booking.customer_name}</p>
                    <p className="flex items-center gap-1.5 text-blue-600 font-semibold">
                      <Phone className="w-3.5 h-3.5" /> {j.booking.customer_phone || '+91 98765 00003'}
                    </p>
                    {j.booking.address && (
                      <p className="flex items-start gap-1.5 text-slate-500 pt-1 border-t border-slate-200">
                        <MapPin className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                        <span>{j.booking.address.line}, {j.booking.address.city} - {j.booking.address.postal_code}</span>
                      </p>
                    )}
                  </div>

                  {j.booking.problem_description && (
                    <div className="text-xs text-slate-500">
                      <span className="font-bold block text-slate-700">Issue Notes:</span>
                      <p className="italic mt-0.5">{j.booking.problem_description}</p>
                    </div>
                  )}

                  {/* Action buttons */}
                  <div className="flex gap-2 pt-2 border-t border-slate-100">
                    <button
                      onClick={() => setStatusModal({ open: true, assignmentId: j.assignment_id, status: 'arrived', remarks: '', images: [] })}
                      className="w-1/2 py-2 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs cursor-pointer"
                    >
                      Mark Arrival
                    </button>
                    <button
                      onClick={() => setStatusModal({ open: true, assignmentId: j.assignment_id, status: 'completed', remarks: '', images: [] })}
                      className="w-1/2 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs cursor-pointer"
                    >
                      Complete Work
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Finished Jobs History */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 space-y-4">
          <h2 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-3">Completed Job History</h2>
          <div className="space-y-3">
            {finishedJobs.length === 0 ? (
              <p className="text-xs text-slate-400 py-3 text-center">No completed jobs yet</p>
            ) : (
              finishedJobs.map((j) => (
                <div key={j.assignment_id} className="p-3.5 rounded-xl border border-slate-100 bg-slate-50 flex items-center justify-between text-xs">
                  <div>
                    <span className="font-mono font-bold text-slate-900">{j.booking.booking_code}</span>
                    <p className="font-semibold text-slate-800 mt-0.5">{j.booking.service_name}</p>
                    <p className="text-slate-400 text-[11px]">{j.booking.customer_name} • {j.booking.scheduled_date}</p>
                  </div>
                  <span className="px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[10px] uppercase">
                    Completed
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* MODAL: Update Status & Upload Proof */}
        {statusModal.open && (
          <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-slate-200">
              <h3 className="font-bold text-sm text-slate-900 mb-3">Update Job Status</h3>
              <form onSubmit={handleUpdateStatus} className="space-y-4">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Status</label>
                  <select
                    value={statusModal.status}
                    onChange={(e) => setStatusModal({ ...statusModal, status: e.target.value })}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                  >
                    <option value="arrived">Mark Arrived at Location</option>
                    <option value="in_progress">Work In Progress</option>
                    <option value="completed">Work Completed</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Work Remarks / Parts Replaced</label>
                  <textarea
                    rows="3"
                    value={statusModal.remarks}
                    onChange={(e) => setStatusModal({ ...statusModal, remarks: e.target.value })}
                    placeholder="e.g. Replaced capacitor, cleaned AC copper coils, tested fan spin..."
                    className="w-full p-2.5 text-xs rounded-xl border border-slate-200"
                  />
                </div>

                <div>
                  <label className="inline-flex items-center gap-2 px-3 py-2 rounded-xl border border-dashed border-slate-300 text-xs text-slate-600 hover:border-blue-500 cursor-pointer">
                    <Upload className="w-4 h-4 text-slate-400" />
                    <span>Upload Proof Photo (Optional)</span>
                    <input type="file" accept="image/*" onChange={handleUploadProof} className="hidden" />
                  </label>
                  {statusModal.images.length > 0 && (
                    <div className="flex gap-2 mt-2">
                      {statusModal.images.map((img, idx) => (
                        <img key={idx} src={img} alt="Proof" className="w-12 h-12 rounded-lg object-cover border" />
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex gap-2 pt-2">
                  <button type="button" onClick={() => setStatusModal({ ...statusModal, open: false })} className="w-1/2 py-2 rounded-xl border text-xs font-bold">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 rounded-xl bg-amber-600 text-white text-xs font-bold">Save Status</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
