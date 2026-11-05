-- =============================================================================
-- HomeServe Technologies SaaS Platform
-- Relational Database Seed Data (DML Inserts)
-- =============================================================================

-- 1. Users (Passwords hashed using bcrypt with salt; All default to Password@123 / Admin@123 / etc.)
-- Note: Replace password hashes with output from bcrypt.hashpw(b"password", bcrypt.gensalt()).
INSERT INTO users (id, email, hashed_password, role, first_name, last_name, phone, is_active, is_verified) VALUES
(1, 'admin@homeserve.com', '$2b$12$ZqN99rT3uK4eK3Jb/g5Z9.X6tS6fOaA7o0bY7pD8c6gR1s5h6j9K2', 'admin', 'Super', 'Admin', '+91 98765 00001', TRUE, TRUE),
(2, 'provider@homeserve.com', '$2b$12$ZqN99rT3uK4eK3Jb/g5Z9.X6tS6fOaA7o0bY7pD8c6gR1s5h6j9K2', 'provider', 'Rajesh', 'Kumar', '+91 98765 00002', TRUE, TRUE),
(3, 'customer@homeserve.com', '$2b$12$ZqN99rT3uK4eK3Jb/g5Z9.X6tS6fOaA7o0bY7pD8c6gR1s5h6j9K2', 'customer', 'Jigar', 'Thakkar', '+91 98765 00003', TRUE, TRUE),
(4, 'technician@homeserve.com', '$2b$12$ZqN99rT3uK4eK3Jb/g5Z9.X6tS6fOaA7o0bY7pD8c6gR1s5h6j9K2', 'technician', 'Vikram', 'Singh', '+91 98765 00004', TRUE, TRUE)
ON DUPLICATE KEY UPDATE first_name=VALUES(first_name), last_name=VALUES(last_name);

-- 2. Role Profiles
INSERT INTO customers (id, user_id, alternate_phone, loyalty_points) VALUES
(1, 3, '+91 98765 99999', 120)
ON DUPLICATE KEY UPDATE loyalty_points=VALUES(loyalty_points);

INSERT INTO service_providers (id, user_id, company_name, business_registration_no, bio, experience_years, verification_status, commission_rate, average_rating, total_reviews) VALUES
(1, 2, 'UrbanPro Maintenance & HVAC Solutions', 'REG-KA-2024-8841', 'Premier certified home improvement and maintenance specialists serving Bengaluru and surrounding tech corridors.', 8, 'verified', 15.00, 4.90, 48)
ON DUPLICATE KEY UPDATE company_name=VALUES(company_name);

INSERT INTO technicians (id, user_id, provider_id, specialization, experience_years, status, rating) VALUES
(1, 4, 1, 'Senior HVAC & Electrical Specialist', 5, 'active', 4.95)
ON DUPLICATE KEY UPDATE specialization=VALUES(specialization);

-- 3. Customer Address
INSERT INTO addresses (id, customer_id, title, address_line, city, state, postal_code, landmark, is_default) VALUES
(1, 1, 'Home', 'Flat 402, Green Glen Heights, 14th Main', 'Bengaluru', 'Karnataka', '560034', 'Near Sony World Junction', TRUE),
(2, 1, 'Office', 'Indiqube Tech Park, 3rd Floor, Bellandur', 'Bengaluru', 'Karnataka', '560103', 'Opposite EcoSpace', FALSE)
ON DUPLICATE KEY UPDATE address_line=VALUES(address_line);

-- 4. Service Categories (8 Core Categories)
INSERT INTO service_categories (id, name, slug, description, icon, is_active) VALUES
(1, 'AC Repair & Maintenance', 'ac-repair-and-maintenance', 'Deep cleaning, gas charging, jet wash, and compressor diagnostic services.', 'Wind', TRUE),
(2, 'Electrical Services', 'electrical-services', 'Switchboard wiring, MCB installation, chandelier setup, and fault detection.', 'Zap', TRUE),
(3, 'Plumbing Services', 'plumbing-services', 'Pipe leak fixes, tap replacement, drainage unclogging, and sanitary fitting.', 'Droplet', TRUE),
(4, 'Home Cleaning', 'home-cleaning', 'Deep bathroom sanitation, full kitchen degreasing, and sofa shampooing.', 'Sparkles', TRUE),
(5, 'Painting Services', 'painting-services', 'Waterproof exterior painting, interior luxury coats, and wall stencil art.', 'Paintbrush', TRUE),
(6, 'Carpentry Services', 'carpentry-services', 'Custom furniture assembly, lock replacement, wardrobe repair, and door hinges.', 'Hammer', TRUE),
(7, 'Appliance Repair', 'appliance-repair', 'Washing machine rotor repair, microwave heating fix, and refrigerator tune-up.', 'Cpu', TRUE),
(8, 'Pest Control', 'pest-control', 'Eco-friendly odorless cockroach, bed bug, and termite eradication.', 'ShieldAlert', TRUE)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 5. Services (15 Core Offerings)
INSERT INTO services (id, category_id, name, slug, description, duration_minutes, base_price, is_active) VALUES
(1, 1, 'AC Deep Jet Servicing', 'ac-deep-jet-servicing', 'High pressure foam jet wash of indoor and outdoor condenser units with gas pressure check.', 60, 699.00, TRUE),
(2, 1, 'AC Gas Refill & Leak Fix', 'ac-gas-refill-and-leak-fix', 'Nitrogen pressure testing, brazing of copper coil leaks, and genuine Freon refrigerant top-up.', 90, 1899.00, TRUE),
(3, 1, 'AC Installation & Uninstallation', 'ac-installation-uninstallation', 'Bracket mount installation, core cutting, pipe insulation, and vacuum testing.', 120, 1299.00, TRUE),
(4, 2, 'Complete House Wiring Inspection', 'complete-house-wiring-inspection', 'Thermal imaging of distribution box, earth leakage breaker verification, and loose connection fixes.', 90, 599.00, TRUE),
(5, 2, 'Ceiling Fan & Light Fixture Setup', 'ceiling-fan-light-fixture-setup', 'Precision mounting, balancing of ceiling fans, and modern aesthetic recessed LED wiring.', 45, 299.00, TRUE),
(6, 2, 'Inverter & Battery Setup', 'inverter-battery-setup', 'Heavy gauge wiring, tubular battery terminal grease coating, and inverter load testing.', 75, 799.00, TRUE),
(7, 3, 'Water Leakage & Pipe Repair', 'water-leakage-pipe-repair', 'Concealed pipe pressure testing, leak sealing, and damaged section PVC replacement.', 60, 449.00, TRUE),
(8, 3, 'Bathroom Sanitary & Tap Fitting', 'bathroom-sanitary-tap-fitting', 'Installation of luxury mixer taps, shower heads, angle valves, and flush cisterns.', 60, 399.00, TRUE),
(9, 3, 'Kitchen Sink & Drain Unclogging', 'kitchen-sink-drain-unclogging', 'Mechanical drain snake unclogging, grease trap flushing, and odorless chemical sanitization.', 45, 349.00, TRUE),
(10, 4, 'Full Deep Home Cleaning', 'full-deep-home-cleaning', 'Intensive single-disc machine floor scrubbing, bathroom descaling, balcony jet wash, and cobweb removal.', 240, 2499.00, TRUE),
(11, 4, 'Kitchen Degreasing & Sanitization', 'kitchen-degreasing-sanitization', 'Chimney filter hot chemical dip, countertop steam cleaning, and cabinet interior sanitization.', 120, 999.00, TRUE),
(12, 5, 'Single Room Waterproof Painting', 'single-room-waterproof-painting', 'Double coat acrylic emulsion with putty touchup and masking protection for furniture.', 180, 2999.00, TRUE),
(13, 6, 'Furniture Assembly & Hinge Repair', 'furniture-assembly-hinge-repair', 'IKEA/Engineered wood modular assembly, soft-close hydraulic hinge adjustments, and magnetic catches.', 90, 499.00, TRUE),
(14, 7, 'Washing Machine Diagnostic & Tuneup', 'washing-machine-diagnostic-tuneup', 'Drain pump lint clearance, drum belt tension calibration, and motherboard PCB diagnosis.', 60, 549.00, TRUE),
(15, 8, 'Full House Odorless Pest Control', 'full-house-odorless-pest-control', 'Gel baiting in electrical ducts, kitchen corners, and residual spray across boundary baseboards.', 60, 1199.00, TRUE)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 6. Coupons
INSERT INTO coupons (id, code, discount_type, discount_value, min_booking_amount, max_discount_amount, is_active) VALUES
(1, 'WELCOME50', 'percentage', 20.00, 399.00, 150.00, TRUE),
(2, 'SUMMER20', 'percentage', 15.00, 500.00, 200.00, TRUE),
(3, 'FLAT100', 'flat', 100.00, 600.00, 100.00, TRUE)
ON DUPLICATE KEY UPDATE discount_value=VALUES(discount_value);

-- 7. Availability Slots
INSERT INTO availability_slots (provider_id, day_of_week, start_time, end_time, slot_label, max_capacity, is_active) VALUES
(1, 1, '09:00', '11:00', '09:00 AM - 11:00 AM', 1, TRUE),
(1, 1, '11:30', '13:30', '11:30 AM - 01:30 PM', 1, TRUE),
(1, 1, '14:30', '16:30', '02:30 PM - 04:30 PM', 1, TRUE),
(1, 1, '17:00', '19:00', '05:00 PM - 07:00 PM', 1, TRUE)
ON DUPLICATE KEY UPDATE max_capacity=VALUES(max_capacity);

-- 8. Sample Booking & Complete Lifecycle Audit
INSERT INTO bookings (id, booking_code, customer_id, provider_id, service_id, address_id, scheduled_date, scheduled_slot, status, problem_description, base_amount, discount_amount, platform_fee, final_amount) VALUES
(1, 'HSB-2026-0001-A1B2', 1, 1, 1, 1, '2026-11-01', '10:00 - 12:00', 'completed', 'AC cooling is low and making water dripping sounds.', 699.00, 100.00, 0.00, 599.00),
(2, 'HSB-2026-0002-C3D4', 1, 1, 4, 1, '2026-11-10', '14:00 - 16:00', 'confirmed', 'Trip switch trips frequently when microwave runs.', 599.00, 50.00, 0.00, 549.00)
ON DUPLICATE KEY UPDATE status=VALUES(status);

-- 9. Assignments
INSERT INTO booking_assignments (id, booking_id, technician_id, status, technician_notes) VALUES
(1, 1, 1, 'completed', 'Cleaned filters, checked gas pressure, replaced drain pipe washer. Cooling restored.')
ON DUPLICATE KEY UPDATE status=VALUES(status);

-- 10. Payments & Tax Invoices
INSERT INTO payments (id, booking_id, payment_method, transaction_id, amount, status) VALUES
(1, 1, 'razorpay', 'pay_test_0001_mock_hsb', 599.00, 'paid')
ON DUPLICATE KEY UPDATE status=VALUES(status);

INSERT INTO invoices (id, invoice_number, booking_id, payment_id, customer_name, customer_email, provider_name, service_name, subtotal, tax_rate, tax_amount, discount_amount, total_amount) VALUES
(1, 'INV-2026-0001-Q8F1', 1, 1, 'Jigar Thakkar', 'customer@homeserve.com', 'UrbanPro Maintenance & HVAC Solutions', 'AC Deep Jet Servicing', 699.00, 18.00, 91.37, 100.00, 599.00)
ON DUPLICATE KEY UPDATE customer_name=VALUES(customer_name);

-- 11. Reviews
INSERT INTO reviews (id, booking_id, customer_id, provider_id, rating, comment, provider_reply) VALUES
(1, 1, 1, 1, 5, 'Excellent technician Vikram! Fixed the water dripping issue in 30 minutes. Super polite and professional.', 'Thank you Jigar! We are delighted you enjoyed our AC jet wash service.')
ON DUPLICATE KEY UPDATE rating=VALUES(rating);
