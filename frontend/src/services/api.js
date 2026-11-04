const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('homeserve_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const config = {
    ...options,
    headers,
  };

  if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
    config.body = JSON.stringify(options.body);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (response.status === 401) {
    // If token invalid, clear localStorage if desired
  }

  if (!response.ok) {
    let errorDetail = 'An unexpected error occurred';
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || errorDetail;
    } catch {
      // fallback
    }
    throw new Error(errorDetail);
  }

  if (response.headers.get('content-type')?.includes('text/csv')) {
    return response.blob();
  }

  return response.json();
}

export const api = {
  // Auth
  login: (email, password) => request('/auth/login', { method: 'POST', body: { email, password } }),
  register: (data) => request('/auth/register', { method: 'POST', body: data }),
  getProfile: () => request('/auth/me'),
  forgotPassword: (email) => request('/auth/forgot-password', { method: 'POST', body: { email } }),
  resetPassword: (data) => request('/auth/reset-password', { method: 'POST', body: data }),

  // Categories & Services
  getCategories: () => request('/categories'),
  getAdminCategories: () => request('/categories/all'),
  createCategory: (data) => request('/categories', { method: 'POST', body: data }),
  getServices: (params = '') => request(`/services${params ? `?${params}` : ''}`),
  getServiceDetail: (slugOrId) => request(`/services/${slugOrId}`),
  createService: (data) => request('/services', { method: 'POST', body: data }),

  // Providers & Technicians
  getProviders: (params = '') => request(`/providers${params ? `?${params}` : ''}`),
  getProviderDetail: (id) => request(`/providers/${id}`),
  getAllProvidersAdmin: (status = '') => request(`/providers/admin/all${status ? `?status_filter=${status}` : ''}`),
  verifyProvider: (id, data) => request(`/providers/admin/${id}/verify`, { method: 'PUT', body: data }),
  getTechnicians: () => request('/technicians'),
  createTechnician: (data) => request('/technicians', { method: 'POST', body: data }),
  getMyAssignedJobs: () => request('/technicians/me/jobs'),
  updateJobStatus: (assignmentId, data) => request(`/technicians/me/jobs/${assignmentId}/status`, { method: 'PUT', body: data }),

  // Bookings
  createBooking: (data) => request('/bookings', { method: 'POST', body: data }),
  getBookings: (status = '') => request(`/bookings${status ? `?status_filter=${status}` : ''}`),
  getBookingDetail: (id) => request(`/bookings/${id}`),
  updateBookingStatus: (id, status, reason = '') => request(`/bookings/${id}/status`, { method: 'PUT', body: { status, reason } }),
  rescheduleBooking: (id, data) => request(`/bookings/${id}/reschedule`, { method: 'PUT', body: data }),
  assignTechnician: (bookingId, technicianId, notes = '') => request(`/bookings/${bookingId}/assign-technician`, { method: 'POST', body: { technician_id: technicianId, notes } }),

  // Payments & Invoices
  calculateCharges: (serviceId, couponCode = '') => request('/payments/calculate', { method: 'POST', body: { service_id: serviceId, coupon_code: couponCode } }),
  processPayment: (bookingId, paymentGateway = 'mock_sandbox') => request('/payments/process', { method: 'POST', body: { booking_id: bookingId, payment_gateway: paymentGateway } }),
  getInvoice: (bookingId) => request(`/payments/invoices/${bookingId}`),

  // Coupons
  getCoupons: () => request('/coupons'),
  getAdminCoupons: () => request('/coupons/admin/all'),
  createCoupon: (data) => request('/coupons', { method: 'POST', body: data }),
  validateCoupon: (code, amount) => request(`/coupons/validate/${code}?amount=${amount}`),

  // Reviews & Complaints
  createReview: (data) => request('/reviews', { method: 'POST', body: data }),
  getProviderReviews: (providerId) => request(`/reviews/provider/${providerId}`),
  replyReview: (reviewId, reply) => request(`/reviews/${reviewId}/reply`, { method: 'PUT', body: { reply } }),
  raiseComplaint: (data) => request('/complaints', { method: 'POST', body: data }),
  getComplaints: (status = '') => request(`/complaints${status ? `?status_filter=${status}` : ''}`),
  resolveComplaint: (id, data) => request(`/complaints/admin/${id}/resolve`, { method: 'PUT', body: data }),

  // Notifications
  getNotifications: () => request('/notifications'),
  getUnreadCount: () => request('/notifications/unread-count'),
  markNotificationRead: (id) => request(`/notifications/${id}/read`, { method: 'PUT' }),
  markAllNotificationsRead: () => request('/notifications/mark-all-read', { method: 'PUT' }),

  // Analytics & Admin
  getAdminAnalytics: () => request('/analytics/admin'),
  getProviderAnalytics: () => request('/analytics/provider'),
  exportBookingsCSV: () => request('/analytics/export/bookings/csv'),
  getAdminCustomers: () => request('/users/admin/customers'),
  toggleUserStatus: (userId, isActive) => request(`/users/admin/${userId}/status?is_active=${isActive}`, { method: 'PUT' }),

  // Customer Addresses
  getAddresses: () => request('/users/addresses'),
  addAddress: (data) => request('/users/addresses', { method: 'POST', body: data }),
  deleteAddress: (id) => request(`/users/addresses/${id}`, { method: 'DELETE' }),

  // File Upload
  uploadFile: async (file) => {
    const token = localStorage.getItem('homeserve_token');
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${API_BASE_URL}/uploads`, {
      method: 'POST',
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: formData
    });
    if (!response.ok) {
      throw new Error('Upload failed');
    }
    return response.json();
  }
};
