# HomeServe Technologies — Capstone Final Presentation Deck

## Slide 1: Title & Executive Overview
* **Project Name**: HomeServe Technologies
* **Sub-title**: Cloud-Native SaaS Home Services Booking Platform
* **Candidate**: Jigar Thakkar
* **Technology Snapshot**: React 19 • Tailwind CSS • Python FastAPI • MySQL 8.0 / SQLAlchemy • JWT Auth • Pytest • Playwright • Netlify + Render
* **Live URLs**:
  * Frontend: [https://homeservicebooking.netlify.app](https://homeservicebooking.netlify.app)
  * Backend API: [https://homeserve-backend-vxjb.onrender.com](https://homeserve-backend-vxjb.onrender.com)
  * Swagger Docs: [https://homeserve-backend-vxjb.onrender.com/api/v1/docs](https://homeserve-backend-vxjb.onrender.com/api/v1/docs)

---

## Slide 2: Problem Statement & Market Opportunity
* **Unorganized Market**: Over 80% of home repair services in urban centers operate through fragmented, unverified phone contacts.
* **Key Pain Points**:
  1. Customers cannot verify contractor identity or read authenticated reviews.
  2. Service contractors waste 30%+ of working hours on scheduling logistics.
  3. No live tracking of technician arrival or objective proof of work.
  4. Cash payments lack tax invoices, warranty protection, and transparent commission accounting.

---

## Slide 3: The HomeServe Solution
* A centralized multi-tenant SaaS platform connecting **Customers** with vetted **Service Providers** and dispatched **Technicians**, governed by a **Super Admin**.
* **Key Differentiators**:
  * 4-Step Booking Wizard with real-time slot availability.
  * Strict atomic double-booking prevention.
  * Razorpay Test Mode checkout simulation with automated 18% GST tax invoices.
  * Mobile-first technician field portal with work proof photo uploads.
  * Real-time business intelligence dashboard with 1-click CSV export.

---

## Slide 4: 4 User Roles & Access Architecture
* **1. Super Admin**: Platform KPIs, provider verification/rejection, dispute resolution, coupon management, and global audit exports.
* **2. Service Provider**: Business profile, catalog pricing, working hours, booking acceptance, technician delegation, and earnings ledger.
* **3. Field Technician**: Mobile-responsive job cards, transit/arrival time updates, completion remarks, and work proof photo uploads.
* **4. Customer**: Service discovery, multi-address book, promo code discounts, appointment tracking, invoices, and 5-star reviews.

---

## Slide 5: 10 Functional Modules Mapping
1. **Authentication & RBAC**: Salted bcrypt password hashing + JWT tokens.
2. **Customer Management**: Profile, multi-address book, and loyalty points.
3. **Category & Service Catalog**: 8 core categories, 15 service offerings.
4. **Service Provider Management**: KYC verification, working hours, and commission rates.
5. **Booking & Slot Engine**: 4-step wizard, double-booking prevention, status lifecycle.
6. **Technician Dispatch**: Assignment delegation, arrival timestamps, work proof.
7. **Payment & Invoicing**: Razorpay simulation, 18% GST tax invoice (`INV-2026-XXXX`).
8. **Notifications System**: In-app real-time alerts with unread badges.
9. **Reviews & Complaints**: Post-service 5-star ratings, provider replies, disputes.
10. **Analytics & Reporting**: Financial metrics, monthly booking graphs, CSV export.

---

## Slide 6: System Architecture & Technology Stack
* **Frontend**: React 19 SPA, Tailwind CSS v4, Lucide Icons, Vite 8 build tool. Deployed on **Netlify Edge CDN**.
* **Backend**: Python 3.13 FastAPI, OAuth2 Password Bearer with JWT, Pydantic V2 schemas. Deployed on **Render Cloud Container**.
* **Database & ORM**: SQLAlchemy 2.0 ORM with dual-engine architecture supporting embedded SQLite and Cloud MySQL 8.0.
* **Testing & CI/CD**: Pytest (25 test cases), Playwright (5 E2E scenarios), Postman API collection.

---

## Slide 7: Database Design (20 Relational Entities)
* 3NF Normalized schema with strict foreign keys, cascade deletes, and composite indexes:
  1. `users` • 2. `customers` • 3. `service_providers` • 4. `technicians` • 5. `addresses`
  6. `service_categories` • 7. `services` • 8. `provider_services` • 9. `service_areas`
  10. `availability_slots` • 11. `bookings` • 12. `booking_assignments` • 13. `booking_images`
  14. `payments` • 15. `invoices` • 16. `coupons` • 17. `reviews` • 18. `complaints`
  19. `notifications` • 20. `provider_earnings`
* Standalone SQL scripts provided in `database/schema.sql` and `database/seed_data.sql`.

---

## Slide 8: Core Workflow 1 — Customer Booking Journey
* **Step 1**: Discover service (e.g. AC Deep Jet Servicing, ₹699).
* **Step 2**: Select delivery address from saved address book.
* **Step 3**: Select scheduled date & available time slot (09:00 - 11:00 AM).
* **Step 4**: Apply coupon (`WELCOME50`), calculate GST & platform fee, complete Razorpay payment.
* **Result**: Unique booking code (`HSB-2026-XXXX`) generated, tax invoice issued, provider notified.

---

## Slide 9: Core Workflow 2 — Provider Dispatch & Technician Execution
* **Acceptance**: Provider reviews booking request in Provider Dashboard and clicks "Accept".
* **Dispatch**: Provider selects active technician (Vikram Singh) and assigns task.
* **Execution**: Technician views assigned job on mobile portal, clicks "Mark Arrived", executes maintenance, and uploads completion photo.
* **Completion**: Technician adds completion remarks ("Replaced washer, cleaned cooling coils"). Booking status updates to `completed`.

---

## Slide 10: Core Workflow 3 — Financial Settlement & Ratings
* **Financial Ledger**: System automatically deducts 15% platform commission (₹89.85) and credits 85% net earnings (₹509.15) to `provider_earnings`.
* **Review Cycle**: Customer receives prompt to rate experience (1-5 stars).
* **Provider Reply**: Provider responds to review ("Thank you Jigar! We are delighted...").
* **Disputes**: If unsatisfied, customer raises ticket in `complaints` table for Admin arbitration.

---

## Slide 11: Double Booking Prevention & Concurrency Control
* **Atomic Slot Check**: Before committing any booking, the backend queries active non-cancelled bookings for `(provider_id, scheduled_date, scheduled_slot)`.
* **Capacity Limit ($N=2$)**: If the slot is filled, transaction aborts and returns **HTTP 409 Conflict**:
  * `"Selected slot is fully booked. Please choose another slot."`
* **Rescheduling Protection**: Also enforced when rescheduling existing bookings.

---

## Slide 12: Quality Assurance & Automated Testing
* **Pytest Backend Suite**: **25 automated tests**, 100% passing in ~9.13s:
  * Health check, 4-role login, invalid login rejection, catalog retrieval, coupon thresholds, RBAC privilege isolation, double booking prevention, joinedload technician queries, and CSV exports.
* **Playwright E2E Suite**: **5 end-to-end user journeys** tested on Chromium & Mobile Viewport:
  * Landing page discovery, role sign-in, booking wizard, mobile technician view, and admin metrics.

---

## Slide 13: Security Implementation & OWASP Compliance
* **Password Security**: Salted bcrypt hashing (12 work factor rounds).
* **Token Security**: 24-hour HMAC-SHA256 JWT tokens with role claims.
* **Privilege Separation**: Horizontal isolation (users only access own data) and vertical isolation (RBAC guards block non-admins).
* **Injection Defense**: 100% parameterized queries via SQLAlchemy ORM.
* **File Security**: Strict 5MB limit and MIME-type whitelist for uploaded proof images.

---

## Slide 14: Vibe Coding Methodology & Prompt Engineering
* Followed complete SDLC with AI pairing across all 9 development phases:
  * Architectural decomposition and SRS generation.
  * Relational schema modeling and standalone SQL creation.
  * Component generation with React 19 and Tailwind CSS.
  * Human-in-the-loop debugging (diagnosed and resolved joinedload import defect).
  * Automated testing with Pytest and Playwright.
* All prompts, decisions, and iterations documented in `docs/VIBE_CODING_PROMPT_LOG.md`.

---

## Slide 15: Conclusion & Live Demonstration
* **Deliverables Checklist (100% Complete)**:
  * [x] Complete source code in GitHub (`main` & `develop` branches)
  * [x] Live Netlify Frontend & Render Backend
  * [x] Standalone SQL DDL & Seed Scripts (`database/`)
  * [x] 20 Relational Database Tables
  * [x] 25 Pytest Tests + 5 Playwright E2E Scenarios (100% Pass)
  * [x] Postman API Collection with 40+ endpoints
  * [x] SRS, User Stories, ERD, Security Checklist & Vibe Coding Prompt Log
* **Ready for Live Demo & Q&A!**
