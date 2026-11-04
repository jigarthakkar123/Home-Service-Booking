import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  Calendar, Clock, MapPin, Tag, ShieldCheck, CheckCircle2, 
  AlertCircle, ArrowRight, ArrowLeft, Upload, Star, CreditCard 
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function BookingWizard() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated, quickSwitchRole } = useAuth();

  const [service, setService] = useState(null);
  const [providers, setProviders] = useState([]);
  const [addresses, setAddresses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Wizard Step: 1 = Provider & Slot, 2 = Address & Details, 3 = Payment & Confirm
  const [currentStep, setCurrentStep] = useState(1);

  // Form State
  const [selectedProviderId, setSelectedProviderId] = useState('');
  const [scheduledDate, setScheduledDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    return d.toISOString().split('T')[0];
  });
  const [scheduledSlot, setScheduledSlot] = useState('09:00 - 11:00');
  
  // Address
  const [selectedAddressId, setSelectedAddressId] = useState('');
  const [isNewAddress, setIsNewAddress] = useState(false);
  const [newAddress, setNewAddress] = useState({
    title: 'Home',
    address_line: '',
    city: 'Bengaluru',
    state: 'Karnataka',
    postal_code: '560034',
    landmark: ''
  });

  const [problemDescription, setProblemDescription] = useState('');
  const [uploadedImages, setUploadedImages] = useState([]);

  // Coupon & Pricing
  const [couponCode, setCouponCode] = useState('');
  const [appliedCoupon, setAppliedCoupon] = useState(null);
  const [priceBreakdown, setPriceBreakdown] = useState({
    service_price: 0,
    discount_amount: 0,
    platform_commission: 0,
    final_amount: 0
  });

  const timeSlots = [
    '09:00 - 11:00',
    '11:00 - 13:00',
    '14:00 - 16:00',
    '16:00 - 18:00',
    '18:00 - 20:00'
  ];

  useEffect(() => {
    async function loadService() {
      try {
        const data = await api.getServiceDetail(slug);
        setService(data);
        if (data.available_providers && data.available_providers.length > 0) {
          setProviders(data.available_providers);
          setSelectedProviderId(data.available_providers[0].provider_id);
        } else {
          // Fallback fetch approved providers
          const allProviders = await api.getProviders();
          setProviders(allProviders.map(p => ({
            provider_id: p.id,
            company_name: p.company_name,
            rating_avg: p.rating_avg,
            rating_count: p.rating_count,
            experience_years: p.experience_years,
            price: data.base_price
          })));
          if (allProviders.length > 0) setSelectedProviderId(allProviders[0].id);
        }

        // Initialize price breakdown
        setPriceBreakdown({
          service_price: data.base_price,
          discount_amount: 0,
          platform_commission: Math.round(data.base_price * 0.15),
          final_amount: data.base_price
        });
      } catch (err) {
        setErrorMsg(err.message || 'Failed to load service');
      } finally {
        setLoading(false);
      }
    }
    loadService();
  }, [slug]);

  useEffect(() => {
    async function loadAddresses() {
      if (isAuthenticated) {
        try {
          const list = await api.getAddresses();
          setAddresses(list || []);
          if (list && list.length > 0) {
            setSelectedAddressId(list[0].id);
          } else {
            setIsNewAddress(true);
          }
        } catch {
          // ignore
        }
      }
    }
    loadAddresses();
  }, [isAuthenticated]);

  const handleApplyCoupon = async (e) => {
    e.preventDefault();
    if (!couponCode.trim()) return;
    try {
      const res = await api.calculateCharges(service.id, couponCode.trim());
      setPriceBreakdown(res);
      setAppliedCoupon(res.coupon_applied);
      setErrorMsg('');
    } catch (err) {
      setErrorMsg(err.message || 'Invalid coupon code');
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const res = await api.uploadFile(file);
      setUploadedImages([...uploadedImages, res.url]);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to upload image');
    }
  };

  const handleCreateBooking = async () => {
    if (!isAuthenticated) {
      // Auto quick-login as customer for effortless testing
      await quickSwitchRole('customer');
    }

    setSubmitting(true);
    setErrorMsg('');

    try {
      const payload = {
        service_id: service.id,
        provider_id: Number(selectedProviderId),
        scheduled_date: scheduledDate,
        scheduled_slot: scheduledSlot,
        problem_description: problemDescription,
        reference_images: uploadedImages,
        coupon_code: appliedCoupon || undefined
      };

      if (isNewAddress || !selectedAddressId) {
        payload.new_address = newAddress;
      } else {
        payload.address_id = Number(selectedAddressId);
      }

      const booking = await api.createBooking(payload);

      // Trigger instant simulated payment
      try {
        await api.processPayment(booking.id, 'mock_sandbox');
      } catch (payErr) {
        console.warn('Auto-pay simulation notice:', payErr);
      }

      navigate(`/bookings/${booking.id}`);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to place booking. Please try another slot or check inputs.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!service) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
        <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center max-w-md">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-3" />
          <h2 className="text-lg font-bold text-slate-800">Service Not Found</h2>
          <p className="text-xs text-slate-500 mt-1">The requested service could not be retrieved.</p>
          <Link to="/services" className="mt-4 inline-block px-4 py-2 rounded-xl bg-blue-600 text-white text-xs font-semibold">
            Back to Services
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 py-10">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Wizard Steps Header */}
        <div className="mb-8">
          <Link to="/services" className="inline-flex items-center gap-1 text-xs text-slate-500 hover:text-slate-800 mb-3">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Services
          </Link>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900">Book {service.name}</h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-1">Complete your booking in 3 quick steps with instant confirmation</p>

          {/* Stepper Tabs */}
          <div className="flex items-center gap-3 mt-6">
            <div className={`flex items-center gap-2 text-xs font-bold px-3 py-1.5 rounded-lg ${currentStep === 1 ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border border-slate-200'}`}>
              <span>1</span> Schedule & Provider
            </div>
            <div className={`flex items-center gap-2 text-xs font-bold px-3 py-1.5 rounded-lg ${currentStep === 2 ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border border-slate-200'}`}>
              <span>2</span> Address & Issue
            </div>
            <div className={`flex items-center gap-2 text-xs font-bold px-3 py-1.5 rounded-lg ${currentStep === 3 ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border border-slate-200'}`}>
              <span>3</span> Payment & Review
            </div>
          </div>
        </div>

        {errorMsg && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Wizard Form Body */}
          <div className="lg:col-span-2 space-y-6">
            {/* STEP 1: Provider & Schedule */}
            {currentStep === 1 && (
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-6">
                <div>
                  <h3 className="font-bold text-base text-slate-900 mb-3 flex items-center gap-2">
                    <ShieldCheck className="w-5 h-5 text-blue-600" />
                    Select Verified Service Provider
                  </h3>
                  <div className="space-y-3">
                    {providers.map((p) => (
                      <label
                        key={p.provider_id}
                        className={`flex items-center justify-between p-4 rounded-xl border cursor-pointer transition ${
                          selectedProviderId === p.provider_id
                            ? 'border-blue-600 bg-blue-50/50 ring-1 ring-blue-600'
                            : 'border-slate-200 hover:border-slate-300'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <input
                            type="radio"
                            name="provider"
                            value={p.provider_id}
                            checked={selectedProviderId === p.provider_id}
                            onChange={() => setSelectedProviderId(p.provider_id)}
                            className="accent-blue-600"
                          />
                          <div>
                            <p className="text-sm font-bold text-slate-900">{p.company_name}</p>
                            <div className="flex items-center gap-2 text-xs text-slate-500 mt-0.5">
                              <span className="flex items-center gap-1 text-amber-500 font-semibold">
                                <Star className="w-3.5 h-3.5 fill-current" /> {p.rating_avg} ({p.rating_count} reviews)
                              </span>
                              <span>•</span>
                              <span>{p.experience_years} yrs exp</span>
                            </div>
                          </div>
                        </div>
                        <span className="text-sm font-black text-slate-900">₹{p.price || service.base_price}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-100">
                  <h3 className="font-bold text-base text-slate-900 mb-3 flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-blue-600" />
                    Select Date & Time Slot
                  </h3>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs font-semibold text-slate-700 block mb-1">Appointment Date</label>
                      <input
                        type="date"
                        value={scheduledDate}
                        min={new Date().toISOString().split('T')[0]}
                        onChange={(e) => setScheduledDate(e.target.value)}
                        className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-hidden focus:border-blue-600"
                      />
                    </div>

                    <div>
                      <label className="text-xs font-semibold text-slate-700 block mb-1">Time Slot</label>
                      <select
                        value={scheduledSlot}
                        onChange={(e) => setScheduledSlot(e.target.value)}
                        className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-hidden focus:border-blue-600"
                      >
                        {timeSlots.map((slot) => (
                          <option key={slot} value={slot}>
                            {slot}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setCurrentStep(2)}
                  className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs sm:text-sm flex items-center justify-center gap-2 shadow-md shadow-blue-500/20 cursor-pointer"
                >
                  Continue to Address & Details <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* STEP 2: Address & Issue Details */}
            {currentStep === 2 && (
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-6">
                <div>
                  <h3 className="font-bold text-base text-slate-900 mb-3 flex items-center gap-2">
                    <MapPin className="w-5 h-5 text-blue-600" />
                    Service Location
                  </h3>

                  {addresses.length > 0 && !isNewAddress ? (
                    <div className="space-y-3">
                      {addresses.map((addr) => (
                        <label
                          key={addr.id}
                          className={`flex items-start gap-3 p-3.5 rounded-xl border cursor-pointer ${
                            selectedAddressId === addr.id
                              ? 'border-blue-600 bg-blue-50/50 ring-1 ring-blue-600'
                              : 'border-slate-200'
                          }`}
                        >
                          <input
                            type="radio"
                            name="address"
                            value={addr.id}
                            checked={selectedAddressId === addr.id}
                            onChange={() => setSelectedAddressId(addr.id)}
                            className="mt-1 accent-blue-600"
                          />
                          <div className="text-xs">
                            <span className="font-bold text-slate-800 uppercase text-[10px] bg-slate-100 px-2 py-0.5 rounded">
                              {addr.title}
                            </span>
                            <p className="text-slate-700 mt-1 font-medium">{addr.address_line}</p>
                            <p className="text-slate-500">{addr.city}, {addr.state} - {addr.postal_code}</p>
                          </div>
                        </label>
                      ))}

                      <button
                        type="button"
                        onClick={() => setIsNewAddress(true)}
                        className="text-xs text-blue-600 font-semibold hover:underline block pt-1 cursor-pointer"
                      >
                        + Add a new address
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div>
                        <label className="text-xs font-semibold text-slate-700 block mb-1">Address Title</label>
                        <select
                          value={newAddress.title}
                          onChange={(e) => setNewAddress({ ...newAddress, title: e.target.value })}
                          className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                        >
                          <option value="Home">Home</option>
                          <option value="Office">Office</option>
                          <option value="Other">Other</option>
                        </select>
                      </div>

                      <div>
                        <label className="text-xs font-semibold text-slate-700 block mb-1">House / Flat / Street Line</label>
                        <input
                          type="text"
                          required
                          value={newAddress.address_line}
                          onChange={(e) => setNewAddress({ ...newAddress, address_line: e.target.value })}
                          placeholder="e.g. 402 Green Glen Heights, 14th Main"
                          className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="text-xs font-semibold text-slate-700 block mb-1">City</label>
                          <input
                            type="text"
                            value={newAddress.city}
                            onChange={(e) => setNewAddress({ ...newAddress, city: e.target.value })}
                            className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                          />
                        </div>
                        <div>
                          <label className="text-xs font-semibold text-slate-700 block mb-1">Postal Code</label>
                          <input
                            type="text"
                            value={newAddress.postal_code}
                            onChange={(e) => setNewAddress({ ...newAddress, postal_code: e.target.value })}
                            className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200"
                          />
                        </div>
                      </div>

                      {addresses.length > 0 && (
                        <button
                          type="button"
                          onClick={() => setIsNewAddress(false)}
                          className="text-xs text-slate-500 hover:underline block cursor-pointer"
                        >
                          Use existing saved address
                        </button>
                      )}
                    </div>
                  )}
                </div>

                <div className="pt-4 border-t border-slate-100">
                  <h3 className="font-bold text-base text-slate-900 mb-3">Problem Description & Photos</h3>
                  <textarea
                    rows="3"
                    value={problemDescription}
                    onChange={(e) => setProblemDescription(e.target.value)}
                    placeholder="Describe specific symptoms, machine model, or instructions for the technician..."
                    className="w-full p-3 text-xs rounded-xl border border-slate-200 focus:outline-hidden focus:border-blue-600"
                  />

                  <div className="mt-3">
                    <label className="inline-flex items-center gap-2 px-3 py-2 rounded-xl border border-dashed border-slate-300 text-xs text-slate-600 hover:border-blue-500 cursor-pointer">
                      <Upload className="w-4 h-4 text-slate-400" />
                      <span>Upload Issue Reference Photo (Optional)</span>
                      <input type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
                    </label>

                    {uploadedImages.length > 0 && (
                      <div className="flex gap-2 mt-2">
                        {uploadedImages.map((img, idx) => (
                          <img key={idx} src={img} alt="Uploaded" className="w-12 h-12 object-cover rounded-lg border border-slate-200" />
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setCurrentStep(1)}
                    className="w-1/3 py-3 rounded-xl border border-slate-200 text-slate-700 font-bold text-xs cursor-pointer"
                  >
                    Back
                  </button>
                  <button
                    type="button"
                    onClick={() => setCurrentStep(3)}
                    className="w-2/3 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs sm:text-sm flex items-center justify-center gap-2 cursor-pointer shadow-md shadow-blue-500/20"
                  >
                    Review Order & Pay <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}

            {/* STEP 3: Payment & Confirmation */}
            {currentStep === 3 && (
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-6">
                <div>
                  <h3 className="font-bold text-base text-slate-900 mb-3 flex items-center gap-2">
                    <CreditCard className="w-5 h-5 text-blue-600" />
                    Select Payment Method
                  </h3>

                  <div className="p-4 rounded-xl border-2 border-blue-600 bg-blue-50/50 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold">
                        ₹
                      </div>
                      <div>
                        <p className="text-xs font-bold text-slate-900">Instant Online Sandbox / Razorpay</p>
                        <p className="text-[11px] text-slate-500">Supports UPI, NetBanking, Credit/Debit Cards, Cash On Delivery</p>
                      </div>
                    </div>
                    <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full">
                      Verified Sandbox
                    </span>
                  </div>
                </div>

                {/* Booking Summary Box */}
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Service:</span>
                    <span className="font-bold text-slate-800">{service.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Scheduled:</span>
                    <span className="font-bold text-slate-800">{scheduledDate} at {scheduledSlot}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Service Guarantee:</span>
                    <span className="font-bold text-emerald-600">30 Days Rework Warranty Included</span>
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setCurrentStep(2)}
                    className="w-1/3 py-3 rounded-xl border border-slate-200 text-slate-700 font-bold text-xs cursor-pointer"
                  >
                    Back
                  </button>
                  <button
                    type="button"
                    disabled={submitting}
                    onClick={handleCreateBooking}
                    className="w-2/3 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs sm:text-sm flex items-center justify-center gap-2 cursor-pointer shadow-md shadow-emerald-500/20 disabled:opacity-50"
                  >
                    {submitting ? 'Confirming Booking...' : `Pay ₹${priceBreakdown.final_amount} & Confirm`}
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Right Sidebar: Price & Coupon Summary */}
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
              <h3 className="font-bold text-sm text-slate-900 pb-3 border-b border-slate-100">
                Payment Summary
              </h3>

              {/* Apply Coupon Form */}
              <form onSubmit={handleApplyCoupon} className="flex gap-2">
                <input
                  type="text"
                  value={couponCode}
                  onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
                  placeholder="Coupon (e.g. WELCOME50)"
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 uppercase font-bold focus:outline-hidden focus:border-blue-600"
                />
                <button
                  type="submit"
                  className="px-3 py-2 rounded-xl bg-slate-900 text-white text-xs font-bold hover:bg-slate-800 transition cursor-pointer"
                >
                  Apply
                </button>
              </form>

              {appliedCoupon && (
                <div className="text-[11px] text-emerald-600 font-bold bg-emerald-50 p-2 rounded-lg flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Coupon '{appliedCoupon}' applied successfully!
                </div>
              )}

              {/* Price Calculation List */}
              <div className="space-y-2.5 text-xs pt-2">
                <div className="flex justify-between text-slate-600">
                  <span>Item Base Price</span>
                  <span className="font-semibold text-slate-800">₹{priceBreakdown.service_price}</span>
                </div>

                {priceBreakdown.discount_amount > 0 && (
                  <div className="flex justify-between text-emerald-600 font-semibold">
                    <span>Discount</span>
                    <span>-₹{priceBreakdown.discount_amount}</span>
                  </div>
                )}

                <div className="flex justify-between text-slate-600">
                  <span>Platform Fee & Guarantee</span>
                  <span className="font-semibold text-slate-800">₹{priceBreakdown.platform_commission}</span>
                </div>

                <div className="pt-3 border-t border-slate-100 flex justify-between items-baseline">
                  <span className="font-bold text-slate-900 text-sm">Total Payable</span>
                  <span className="text-xl font-black text-slate-900">₹{priceBreakdown.final_amount}</span>
                </div>
              </div>
            </div>

            {/* Test Coupons helper */}
            <div className="p-4 rounded-xl bg-blue-50/70 border border-blue-200/60 text-xs text-blue-900 space-y-1">
              <span className="font-bold block">Available Promo Codes:</span>
              <p className="cursor-pointer hover:underline" onClick={() => setCouponCode('WELCOME50')}>
                • <strong className="font-mono">WELCOME50</strong> - 50% discount up to ₹300
              </p>
              <p className="cursor-pointer hover:underline" onClick={() => setCouponCode('HOMESERVE100')}>
                • <strong className="font-mono">HOMESERVE100</strong> - Flat ₹100 instant off
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
