# HomeServe Technologies — Vibe Coding AI Prompt & Development Log

## 1. Vibe Coding Methodology Overview
As mandated by **Rule 7 of the Full Stack Capstone Specification**, this document records the comprehensive prompt engineering methodology, AI architectural interactions, iterative refinement steps, and human-in-the-loop debugging conducted throughout the 9 development phases of the **HomeServe Technologies SaaS Platform**.

---

## 2. Chronological AI Prompt & Iteration Log

### Phase 1: Requirement Analysis & Architectural Planning
* **Prompt 1.1 (Business Domain Decomposition)**:
  > *"Act as a Principal Enterprise Architect. Analyze the HomeServe Technologies business case study for an on-demand home services booking SaaS. Decompose the business model into 4 primary user roles (Super Admin, Service Provider, Customer, Technician) and define 10 functional modules covering the complete booking lifecycle from catalog discovery to post-service invoicing and reviews. Output a Software Requirements Specification (SRS) table with priority and user stories."*
  * **AI Output Analysis**: Generated structured SRS matrix and identified potential race condition in concurrent slot booking.
  * **Human Refinement**: Added slot capacity parameters ($N=2$) and explicit double-booking prevention criteria.

* **Prompt 1.2 (Data Flow & State Machine Mapping)**:
  > *"Generate a Mermaid state diagram for the booking lifecycle with exact statuses: pending, confirmed, provider_assigned, in_progress, completed, cancelled, rejected. Map transition triggers for each role."*
  * **AI Output Analysis**: Successfully generated transition state machine matching business requirements.

---

### Phase 2: Database Design & 20 Relational Entities (Phase 3)
* **Prompt 2.1 (Relational Data Modeling)**:
  > *"Design a 3NF normalized relational database schema in SQLAlchemy for MySQL 8.0 containing exactly 20 relational entities: users, customers, service_providers, technicians, addresses, service_categories, services, provider_services, service_areas, availability_slots, bookings, booking_assignments, booking_images, payments, invoices, coupons, reviews, complaints, notifications, provider_earnings. Ensure proper primary keys, foreign keys, cascade deletes, and unique indexes."*
  * **AI Output Analysis**: Generated `models.py` with 20 SQLAlchemy declarative classes.
  * **Human Refinement**: Added composite unique constraint on `(provider_id, service_id)` in `provider_services` and composite index on `(provider_id, scheduled_date, scheduled_slot)` in `bookings`.

* **Prompt 2.2 (Standalone DDL & Seed Data Generation)**:
  > *"Generate pure standard SQL DDL (schema.sql) and DML insert scripts (seed_data.sql) compatible with MySQL Workbench and phpMyAdmin. Populate 8 core home service categories, 15 service offerings, verified provider profile, and demo users with realistic Indian home service data."*
  * **AI Output Analysis**: Generated `database/schema.sql` and `database/seed_data.sql`.

---

### Phase 3: Backend API Architecture & Security (Phase 4 & 7)
* **Prompt 3.1 (FastAPI Scaffold & RBAC Middleware)**:
  > *"Create a production-ready FastAPI application with modular APIRouter structure under `/api/v1`. Implement secure OAuth2PasswordBearer authentication using JWT tokens and bcrypt password hashing. Create role dependency guards: require_admin, require_provider, require_technician, require_customer."*
  * **AI Output Analysis**: Implemented `app/api/deps.py` and `app/core/security.py`.
  * **Human Refinement**: Audited token expiration to 24 hours and enforced subject encoding as integer user ID.

* **Prompt 3.2 (Double Booking Prevention & Transactions)**:
  > *"In `bookings.py`, write the `create_booking` endpoint with atomic transaction isolation. Before booking insertion, count active bookings for the specified provider, date, and slot. If count >= max_capacity, raise HTTP 409 Conflict. Calculate 18% GST tax, platform fee, and coupon discount."*
  * **AI Output Analysis**: Implemented robust capacity checks and billing calculations.

---

### Phase 4: UI/UX & Frontend Development (Phase 2 & 5)
* **Prompt 4.1 (React 19 & Tailwind Responsive SPA)**:
  > *"Develop a responsive React 19 single-page application using Vite and Tailwind CSS. Implement 4 dedicated dashboards: AdminDashboard (KPI metrics, provider verification, CSV export), CustomerDashboard (bookings, addresses, loyalty points), ProviderDashboard (dispatch, slot management, earnings), and TechnicianDashboard (mobile-first assigned job cards, arrival timestamps, work proof photo uploads)."*
  * **AI Output Analysis**: Generated complete responsive dashboard suite with Lucide icons.
  * **Human Refinement**: Designed top demo bar with evaluator role-switcher and enhanced the Login page with auto-fill credential chips.

* **Prompt 4.2 (Centralized API Client & Token Management)**:
  > *"Create `api.js` using fetch with dynamic environment variable base URL targeting the deployed Render backend in production. Attach Authorization Bearer token from localStorage to every outgoing request."*
  * **AI Output Analysis**: Implemented centralized API service with automatic JSON serialization and CSV blob handling.

---

### Phase 5: Debugging, Testing & Quality Assurance (Phase 6)
* **Prompt 5.1 (Pytest API Test Suite)**:
  > *"Write an automated Pytest test suite using FastAPI TestClient covering all 10 modules: authentication, invalid login, catalog retrieval, coupon calculation, RBAC isolation, double booking prevention, technician queries, and CSV export."*
  * **AI Output Analysis**: Generated 25 test functions achieving 100% pass rate.

* **Prompt 5.2 (Diagnosing Technician Joinedload Defect)**:
  > *"The technician jobs endpoint returned HTTP 500 when querying assigned jobs. Analyze `technicians.py`: `joinedload(BookingAssignment.booking).joinedload(Booking.customer).joinedload(Customer.user)`. Why is this throwing NameError?"*
  * **AI Output Analysis**: Identified that `Customer` was not imported in `technicians.py`.
  * **Human Action**: Imported `Customer` from `app.models.models` and confirmed resolution with live Pytest run.

* **Prompt 5.3 (Playwright E2E Automated Tests)**:
  > *"Create a Playwright E2E test suite in `frontend/tests/e2e.spec.js` testing desktop and mobile viewports. Cover public landing page exploration, role sign-in, booking wizard navigation, technician mobile view, and admin CSV export."*
  * **AI Output Analysis**: Generated `e2e.spec.js` and `playwright.config.js`.

---

## 3. Human-in-the-Loop Vibe Coding Best Practices Followed
1. **Never Blindly Accept AI Code**: Every model, route, and SQL query was reviewed, tested against live databases, and verified with automated test suites.
2. **Deterministic Security Controls**: Authentication, JWT decoding, and password hashing were rigorously validated with negative test cases (HTTP 401/403).
3. **Continuous Deployment Feedback**: Automated Git pushes to Render and Netlify allowed immediate real-world validation on cloud infrastructure.
