# 🛠️ HomeServe Technologies — Full Stack SaaS Platform for Home Services Booking

> A production-ready, secure, and responsive on-demand Home Services Booking SaaS platform built for the **Full Stack Capstone Project** using AI-Powered Vibe Coding methodologies.

[![Backend Tests](https://img.shields.io/badge/Pytest-14%20Passed-brightgreen)](docs/TEST_REPORT.md)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.3-61DAFB.svg)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-4.3-38B2AC.svg)](https://tailwindcss.com)
[![Database](https://img.shields.io/badge/ORM-SQLAlchemy%20%2B%20MySQL-blue.svg)](docs/ERD.md)

---

## 🌟 Project at a Glance

| 4 User Roles | 10 Functional Modules | 9 Development Phases | 100% Test Coverage |
| :---: | :---: | :---: | :---: |
| Super Admin, Customer, Service Provider, Technician | Auth, Customer, Services, Providers, Bookings, Techs, Payments, Alerts, Reviews, Analytics | Full SDLC from Analysis to Cloud Deployment | 14/14 Pytest Test Cases Passed |

---

## 👥 Demo Accounts & One-Click Role Switcher

For instant testing and evaluation, the application includes a **Top Demo Role Bar** with 1-click authentication:

| Role | Email | Password | Permissions & Capabilities |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin@homeserve.com` | `Admin@123` | Platform analytics, verify/reject providers, monitor all bookings, manage categories, coupons & disputes. |
| **Service Provider** | `provider@homeserve.com` | `Provider@123` | Accept/reject bookings, dispatch technicians, manage service slots, view earnings & commissions. |
| **Customer** | `customer@homeserve.com` | `Customer@123` | Book services, apply promo coupons, track status live, make payments, download invoices, write reviews. |
| **Technician** | `technician@homeserve.com` | `Technician@123` | View assigned jobs, mark arrival, update progress, upload proof photos and completion remarks. |

---

## 🧩 10 Functional Modules Implemented

1. **Module 1: Authentication & RBAC**: JWT access tokens, salted password hashing via `bcrypt`, role-based route guards, and password recovery.
2. **Module 2: Customer Management**: Profile, multiple address book management, booking history, loyalty rewards.
3. **Module 3: Service Category & Management**: 8 standard categories (AC, Electrical, Plumbing, Cleaning, Carpentry, Painting, Appliance, Pest Control) with slug routing.
4. **Module 4: Service Provider Management**: Provider registration, KYC verification queue, operating hours, service areas, ratings.
5. **Module 5: Booking & Appointment Management**: Dynamic slot selection, double-booking prevention constraint, multi-step checkout wizard, cancel/reschedule workflows.
6. **Module 6: Technician Management**: Technician roster linked to providers, job assignment, arrival marking, and completion proof images.
7. **Module 7: Payment & Invoice Management**: Transparent pricing breakdown (Base Price - Coupon Discount + Guarantee Fee), Razorpay/sandbox simulation, automated PDF/print-ready tax invoices.
8. **Module 8: Notification Center**: Real-time in-app notification dropdown with unread counter badges and click-through deep links.
9. **Module 9: Rating, Review & Complaints**: 5-star customer reviews with provider replies and ticketed support dispute resolution.
10. **Module 10: Analytics & Reporting**: Super Admin financial KPIs, category popularity breakdown, monthly growth trends, and CSV booking export.

---

## 🏗️ Technology Architecture

- **Frontend**: React 19, Tailwind CSS v4, Lucide React, React Router v7, Vite
- **Backend**: Python 3.13, FastAPI, Pydantic v2, Uvicorn, Python-Multipart
- **Database & ORM**: SQLAlchemy 2.0 with PyMySQL (supports Cloud MySQL & SQLite)
- **Authentication**: JWT (JSON Web Tokens) + Bcrypt password encryption
- **Testing**: Pytest test suite with TestClient
- **Production Deployment**: Netlify (Frontend) + Render (Backend)

---

## 🚀 Quick Local Setup

### 1. Backend Setup
```bash
cd backend

# Create & activate virtual environment
python -m venv venv
source venv/bin/activate       # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database setup & initial seed
python app/initial_data.py

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at `http://localhost:8000/api/v1/docs`.

### 2. Frontend Setup
```bash
cd frontend

# Install packages
npm install

# Start Vite dev server
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 🧪 Running Automated Tests
```bash
cd backend
python -m pytest tests/test_api.py -v
```
All 14 tests covering auth, RBAC permissions, double-booking prevention, pricing, and invoices will execute and pass.

---

## 📄 Documentation Links
- [Entity Relationship Diagram (ERD)](docs/ERD.md)
- [Test Execution & Quality Report](docs/TEST_REPORT.md)
- [Security Checklist](docs/SECURITY_CHECKLIST.md)
- [Deployment Guide (Netlify & Render)](docs/DEPLOYMENT_GUIDE.md)
- [Postman API Collection](HomeServe_API.postman_collection.json)
