import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Printer, ArrowLeft, CheckCircle, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';

export default function InvoiceView() {
  const { bookingId } = useParams();
  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    async function loadInvoice() {
      try {
        const data = await api.getInvoice(bookingId);
        setInvoice(data);
      } catch (err) {
        setErrorMsg(err.message || 'Invoice not found');
      } finally {
        setLoading(false);
      }
    }
    loadInvoice();
  }, [bookingId]);

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!invoice) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
        <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center max-w-md">
          <p className="text-sm text-red-600 font-semibold">{errorMsg || 'Invoice not generated yet'}</p>
          <Link to={`/bookings/${bookingId}`} className="mt-4 inline-block text-xs text-blue-600 hover:underline">
            Back to Booking
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100 py-10 print:py-0 print:bg-white">
      <div className="max-w-3xl mx-auto px-4">
        {/* Top Action Bar (hidden when printing) */}
        <div className="flex items-center justify-between mb-6 print:hidden">
          <Link
            to={`/bookings/${bookingId}`}
            className="inline-flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 font-semibold"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Booking Tracking
          </Link>
          <button
            onClick={handlePrint}
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs flex items-center gap-2 shadow-md shadow-blue-500/20 cursor-pointer"
          >
            <Printer className="w-4 h-4" /> Print / Save PDF
          </button>
        </div>

        {/* Invoice Paper Document */}
        <div className="bg-white rounded-3xl p-8 sm:p-12 border border-slate-200/80 shadow-xl print:border-none print:shadow-none print:p-0">
          {/* Header */}
          <div className="flex flex-col sm:flex-row justify-between pb-8 border-b border-slate-100 gap-4">
            <div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-sm">
                  HS
                </div>
                <h1 className="text-xl font-black text-slate-900 tracking-tight">HomeServe Technologies</h1>
              </div>
              <p className="text-xs text-slate-500 mt-1">Tax Invoice & Official Payment Receipt</p>
              <p className="text-[11px] text-slate-400">GSTIN: 29AABCH2026R1ZM • Bengaluru, Karnataka</p>
            </div>

            <div className="sm:text-right text-xs">
              <span className="font-mono font-bold text-sm text-slate-900">{invoice.invoice_number}</span>
              <p className="text-slate-500 mt-1">Date: {new Date(invoice.invoice_date).toLocaleDateString()}</p>
              <div className="inline-flex items-center gap-1 mt-2 text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full">
                <CheckCircle className="w-3 h-3" /> Payment Paid & Confirmed
              </div>
            </div>
          </div>

          {/* Billed To / From */}
          <div className="grid grid-cols-2 gap-8 py-8 border-b border-slate-100 text-xs">
            <div>
              <span className="text-slate-400 font-bold uppercase block mb-1">Customer Details</span>
              <p className="font-bold text-slate-800 text-sm">{invoice.customer_name}</p>
              <p className="text-slate-500 mt-0.5">{invoice.customer_email}</p>
            </div>

            <div>
              <span className="text-slate-400 font-bold uppercase block mb-1">Service Partner</span>
              <p className="font-bold text-slate-800 text-sm">{invoice.provider_name}</p>
              <p className="text-slate-500 mt-0.5">Verified HomeServe Partner</p>
            </div>
          </div>

          {/* Items Table */}
          <div className="py-6">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="border-b border-slate-200 text-slate-400 uppercase font-bold text-[10px]">
                  <th className="pb-3">Description</th>
                  <th className="pb-3 text-right">Duration</th>
                  <th className="pb-3 text-right">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                <tr>
                  <td className="py-4">
                    <p className="font-bold text-slate-900">{invoice.service_name}</p>
                    <p className="text-[11px] text-slate-400">Doorstep service execution with 30-day warranty</p>
                  </td>
                  <td className="py-4 text-right">60 Mins</td>
                  <td className="py-4 text-right font-bold text-slate-900">₹{invoice.subtotal}</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Totals Breakdown */}
          <div className="pt-4 border-t border-slate-100 flex justify-end">
            <div className="w-64 space-y-2 text-xs">
              <div className="flex justify-between text-slate-600">
                <span>Subtotal</span>
                <span>₹{invoice.subtotal}</span>
              </div>
              {invoice.discount_amount > 0 && (
                <div className="flex justify-between text-emerald-600 font-semibold">
                  <span>Coupon Discount</span>
                  <span>-₹{invoice.discount_amount}</span>
                </div>
              )}
              <div className="flex justify-between text-slate-600">
                <span>Platform Fee & Guarantee</span>
                <span>₹{invoice.platform_fee}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Applicable GST (18% display)</span>
                <span>₹{invoice.tax_amount}</span>
              </div>
              <div className="pt-2 border-t border-slate-200 flex justify-between font-black text-sm text-slate-900">
                <span>Total Paid</span>
                <span className="text-blue-600">₹{invoice.total_amount}</span>
              </div>
            </div>
          </div>

          {/* Footer Note */}
          <div className="mt-12 pt-6 border-t border-slate-100 text-[11px] text-slate-400 flex items-center justify-between">
            <p>Thank you for choosing HomeServe Technologies SaaS Platform.</p>
            <div className="flex items-center gap-1 text-slate-500 font-medium">
              <ShieldCheck className="w-4 h-4 text-emerald-500" /> Authorized Electronic Receipt
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
