import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  CheckCircle2, Clock, MapPin, User, FileText, Star, 
  AlertTriangle, Phone, Calendar, ArrowLeft, ShieldCheck, X
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function BookingTracking() {
  const { id } = useParams();
  const { user } = useAuth();
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  // Modals
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [showComplaintModal, setShowComplaintModal] = useState(false);
  const [showRescheduleModal, setShowRescheduleModal] = useState(false);

  // Review Form
  const [rating, setRating] = useState(5);
  const [reviewComment, setReviewComment] = useState('');

  // Complaint Form
  const [complaintSubject, setComplaintSubject] = useState('');
  const [complaintDesc, setComplaintDesc] = useState('');
  const [complaintPriority, setComplaintPriority] = useState('medium');

  // Reschedule Form
  const [rescheduleDate, setRescheduleDate] = useState('');
  const [rescheduleSlot, setRescheduleSlot] = useState('14:00 - 16:00');

  const loadBooking = async () => {
    try {
      const data = await api.getBookingDetail(id);
      setBooking(data);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to load booking');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBooking();
    const timer = setInterval(loadBooking, 10000); // 10s live polling
    return () => clearInterval(timer);
  }, [id]);

  const handleCancelBooking = async () => {
    if (!window.confirm('Are you sure you want to cancel this booking?')) return;
    try {
      await api.updateBookingStatus(id, 'cancelled', 'Cancelled by customer');
      loadBooking();
    } catch (err) {
      alert(err.message || 'Could not cancel booking');
    }
  };

  const handleReschedule = async (e) => {
    e.preventDefault();
    try {
      await api.rescheduleBooking(id, {
        scheduled_date: rescheduleDate,
        scheduled_slot: rescheduleSlot
      });
      setShowRescheduleModal(false);
      loadBooking();
    } catch (err) {
      alert(err.message || 'Reschedule failed');
    }
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    try {
      await api.createReview({
        booking_id: Number(id),
        rating,
        comment: reviewComment
      });
      setShowReviewModal(false);
      loadBooking();
    } catch (err) {
      alert(err.message || 'Failed to submit review');
    }
  };

  const handleSubmitComplaint = async (e) => {
    e.preventDefault();
    try {
      await api.raiseComplaint({
        booking_id: Number(id),
        subject: complaintSubject,
        description: complaintDesc,
        priority: complaintPriority
      });
      setShowComplaintModal(false);
      alert('Support ticket submitted successfully. Our team will review shortly.');
      loadBooking();
    } catch (err) {
      alert(err.message || 'Failed to submit ticket');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!booking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
        <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center max-w-md">
          <p className="text-sm text-red-600 font-semibold">{errorMsg || 'Booking not found'}</p>
          <Link to="/" className="mt-4 inline-block text-xs text-blue-600 hover:underline">
            Go Home
          </Link>
        </div>
      </div>
    );
  }

  const steps = [
    { key: 'pending', label: 'Booking Placed', desc: 'Awaiting provider confirmation' },
    { key: 'confirmed', label: 'Confirmed', desc: 'Slot locked with provider' },
    { key: 'provider_assigned', label: 'Technician Assigned', desc: 'Specialist dispatched' },
    { key: 'in_progress', label: 'In Progress', desc: 'Technician arrived & working' },
    { key: 'completed', label: 'Completed', desc: 'Work done & verified' }
  ];

  const statusOrder = ['pending', 'confirmed', 'provider_assigned', 'in_progress', 'completed'];
  const currentIndex = statusOrder.indexOf(booking.status);
  const isCancelled = booking.status === 'cancelled' || booking.status === 'rejected';

  // Find assigned technician
  const activeAssignment = booking.assignments && booking.assignments.length > 0 ? booking.assignments[0] : null;

  return (
    <div className="min-h-screen bg-slate-50 py-10">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Navigation & Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-200 gap-4">
          <div>
            <Link to="/customer" className="inline-flex items-center gap-1 text-xs text-slate-500 hover:text-slate-800 mb-2">
              <ArrowLeft className="w-3.5 h-3.5" /> Back to My Bookings
            </Link>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-black text-slate-900">{booking.booking_code}</h1>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${
                booking.status === 'completed' ? 'bg-emerald-100 text-emerald-800' :
                booking.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                'bg-blue-100 text-blue-800'
              }`}>
                {booking.status.replace('_', ' ')}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">Booked on {new Date(booking.created_at).toLocaleDateString()}</p>
          </div>

          <div className="flex items-center gap-2">
            <Link
              to={`/invoices/${booking.id}`}
              className="px-3.5 py-2 rounded-xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-bold flex items-center gap-1.5 shadow-xs"
            >
              <FileText className="w-4 h-4 text-slate-500" />
              View Invoice
            </Link>

            {booking.status === 'completed' && !booking.review && (
              <button
                onClick={() => setShowReviewModal(true)}
                className="px-3.5 py-2 rounded-xl bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold flex items-center gap-1.5 shadow-xs cursor-pointer"
              >
                <Star className="w-4 h-4" />
                Write Review
              </button>
            )}

            <button
              onClick={() => setShowComplaintModal(true)}
              className="px-3 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold flex items-center gap-1 cursor-pointer"
            >
              <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
              Support
            </button>
          </div>
        </div>

        {/* Status Tracker Bar */}
        <div className="my-8 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
          <h2 className="text-sm font-bold text-slate-800 mb-6">Service Progress</h2>

          {isCancelled ? (
            <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700">
              <span className="font-bold block text-sm">Booking Cancelled / Rejected</span>
              <p className="mt-1">{booking.cancellation_reason || 'This service request was cancelled.'}</p>
            </div>
          ) : (
            <div className="relative">
              <div className="hidden sm:block absolute top-4 left-6 right-6 h-0.5 bg-slate-100 -z-0">
                <div
                  className="h-full bg-blue-600 transition-all duration-500"
                  style={{ width: `${Math.max(0, (currentIndex / (steps.length - 1)) * 100)}%` }}
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-5 gap-4 relative z-10">
                {steps.map((st, idx) => {
                  const isPassed = idx <= currentIndex;
                  const isCurrent = idx === currentIndex;
                  return (
                    <div key={st.key} className="flex sm:flex-col items-center sm:items-center gap-3 sm:gap-2">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs shrink-0 transition-colors ${
                        isPassed ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-400'
                      }`}>
                        {isPassed ? <CheckCircle2 className="w-4 h-4" /> : idx + 1}
                      </div>
                      <div className="sm:text-center">
                        <p className={`text-xs font-bold ${isCurrent ? 'text-blue-600' : 'text-slate-800'}`}>
                          {st.label}
                        </p>
                        <p className="text-[10px] text-slate-400 hidden sm:block">{st.desc}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Booking Details Card */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
              <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-3">
                Service & Appointment Information
              </h3>

              <div className="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="text-slate-400 block font-semibold">Service</span>
                  <p className="font-bold text-slate-800 mt-0.5">{booking.service?.name}</p>
                </div>
                <div>
                  <span className="text-slate-400 block font-semibold">Scheduled Date & Slot</span>
                  <p className="font-bold text-slate-800 mt-0.5">{booking.scheduled_date} ({booking.scheduled_slot})</p>
                </div>
                <div>
                  <span className="text-slate-400 block font-semibold">Service Provider</span>
                  <p className="font-bold text-slate-800 mt-0.5">{booking.provider?.company_name}</p>
                </div>
                <div>
                  <span className="text-slate-400 block font-semibold">Payment Status</span>
                  <p className="font-bold text-emerald-600 uppercase mt-0.5">
                    {booking.payment?.status || 'Paid Online'}
                  </p>
                </div>
              </div>

              {booking.address && (
                <div className="pt-3 border-t border-slate-100 text-xs">
                  <span className="text-slate-400 block font-semibold mb-1">Service Address</span>
                  <p className="text-slate-800 font-medium">
                    {booking.address.address_line}, {booking.address.city}, {booking.address.state} - {booking.address.postal_code}
                  </p>
                </div>
              )}

              {booking.problem_description && (
                <div className="pt-3 border-t border-slate-100 text-xs">
                  <span className="text-slate-400 block font-semibold mb-1">Problem Remarks</span>
                  <p className="text-slate-600 bg-slate-50 p-3 rounded-xl">{booking.problem_description}</p>
                </div>
              )}
            </div>

            {/* Actions: Cancel & Reschedule */}
            {!isCancelled && booking.status !== 'completed' && (
              <div className="flex gap-3">
                <button
                  onClick={() => setShowRescheduleModal(true)}
                  className="px-4 py-2.5 rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-bold cursor-pointer"
                >
                  Reschedule Appointment
                </button>
                <button
                  onClick={handleCancelBooking}
                  className="px-4 py-2.5 rounded-xl border border-red-200 text-red-600 hover:bg-red-50 text-xs font-bold cursor-pointer"
                >
                  Cancel Booking
                </button>
              </div>
            )}
          </div>

          {/* Assigned Technician Card */}
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
              <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-3 mb-3">
                Assigned Specialist
              </h3>

              {activeAssignment && activeAssignment.technician ? (
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-sm">
                      {activeAssignment.technician.user?.first_name?.[0] || 'T'}
                    </div>
                    <div>
                      <p className="text-xs font-bold text-slate-900">
                        {activeAssignment.technician.user?.first_name} {activeAssignment.technician.user?.last_name}
                      </p>
                      <p className="text-[11px] text-slate-500">
                        {activeAssignment.technician.specialization || 'Certified Field Tech'}
                      </p>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-50 text-xs text-slate-600 space-y-1">
                    <p className="flex items-center gap-2">
                      <Phone className="w-3.5 h-3.5 text-blue-600" />
                      {activeAssignment.technician.user?.phone || '+91 98765 00004'}
                    </p>
                    <p className="flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5 text-blue-600" />
                      Status: <strong className="capitalize">{activeAssignment.status}</strong>
                    </p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-6 text-xs text-slate-400">
                  <Clock className="w-8 h-8 mx-auto mb-2 text-slate-300 animate-pulse" />
                  Provider will assign a technician shortly
                </div>
              )}
            </div>

            {/* Price breakdown pill */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-500">Service Base:</span>
                <span className="font-semibold text-slate-800">₹{booking.service_price}</span>
              </div>
              {booking.discount_amount > 0 && (
                <div className="flex justify-between text-emerald-600">
                  <span>Discount:</span>
                  <span className="font-semibold">-₹{booking.discount_amount}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-slate-500">Platform Guarantee:</span>
                <span className="font-semibold text-slate-800">₹{booking.platform_commission}</span>
              </div>
              <div className="pt-2 border-t border-slate-100 flex justify-between font-bold text-sm text-slate-900">
                <span>Total Amount:</span>
                <span>₹{booking.final_amount}</span>
              </div>
            </div>
          </div>
        </div>

        {/* MODAL: Reschedule */}
        {showRescheduleModal && (
          <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-slate-200">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h3 className="font-bold text-sm text-slate-900">Reschedule Appointment</h3>
                <button onClick={() => setShowRescheduleModal(false)}><X className="w-4 h-4 text-slate-400" /></button>
              </div>
              <form onSubmit={handleReschedule} className="mt-4 space-y-4">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">New Date</label>
                  <input
                    type="date"
                    required
                    value={rescheduleDate}
                    min={new Date().toISOString().split('T')[0]}
                    onChange={(e) => setRescheduleDate(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">New Time Slot</label>
                  <select
                    value={rescheduleSlot}
                    onChange={(e) => setRescheduleSlot(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                  >
                    <option value="09:00 - 11:00">09:00 - 11:00</option>
                    <option value="11:00 - 13:00">11:00 - 13:00</option>
                    <option value="14:00 - 16:00">14:00 - 16:00</option>
                    <option value="16:00 - 18:00">16:00 - 18:00</option>
                    <option value="18:00 - 20:00">18:00 - 20:00</option>
                  </select>
                </div>
                <div className="flex gap-2 pt-2">
                  <button type="button" onClick={() => setShowRescheduleModal(false)} className="w-1/2 py-2 rounded-xl border text-xs font-bold text-slate-700">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold">Confirm Reschedule</button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* MODAL: Review */}
        {showReviewModal && (
          <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-slate-200">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h3 className="font-bold text-sm text-slate-900">Rate & Review Service</h3>
                <button onClick={() => setShowReviewModal(false)}><X className="w-4 h-4 text-slate-400" /></button>
              </div>
              <form onSubmit={handleSubmitReview} className="mt-4 space-y-4">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Rating</label>
                  <div className="flex gap-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => setRating(star)}
                        className={`p-2 rounded-lg ${rating >= star ? 'text-amber-500' : 'text-slate-300'}`}
                      >
                        <Star className="w-6 h-6 fill-current" />
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Your Feedback</label>
                  <textarea
                    rows="3"
                    value={reviewComment}
                    onChange={(e) => setReviewComment(e.target.value)}
                    placeholder="Tell us about the punctuality, cleanliness, and work quality..."
                    className="w-full p-3 text-xs rounded-xl border border-slate-200"
                  />
                </div>
                <button type="submit" className="w-full py-2.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold">
                  Submit Review
                </button>
              </form>
            </div>
          </div>
        )}

        {/* MODAL: Complaint */}
        {showComplaintModal && (
          <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-slate-200">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h3 className="font-bold text-sm text-slate-900">Raise Support Ticket</h3>
                <button onClick={() => setShowComplaintModal(false)}><X className="w-4 h-4 text-slate-400" /></button>
              </div>
              <form onSubmit={handleSubmitComplaint} className="mt-4 space-y-4">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Subject</label>
                  <input
                    type="text"
                    required
                    value={complaintSubject}
                    onChange={(e) => setComplaintSubject(e.target.value)}
                    placeholder="e.g. Technician delayed, Issue not resolved..."
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Priority</label>
                  <select
                    value={complaintPriority}
                    onChange={(e) => setComplaintPriority(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Details</label>
                  <textarea
                    rows="3"
                    required
                    value={complaintDesc}
                    onChange={(e) => setComplaintDesc(e.target.value)}
                    placeholder="Provide detailed information for our resolution team..."
                    className="w-full p-3 text-xs rounded-xl border border-slate-200"
                  />
                </div>
                <button type="submit" className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold">
                  Submit Complaint
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
