# HomeServe Technologies — Master Corporate Policy & System Knowledge Base

> **RAG (Retrieval-Augmented Generation) System Knowledge Base Document**  
> **Metadata Tag**: `HOMESERVE-DOC-RAG-2026-V2`  
> **Authoritative Scope**: Super Admin, Service Providers, Technicians, Customers  
> **Primary PDF Artifact**: `HomeServe_Company_Policy_and_System_Knowledge_Base.pdf` (in project root)

---

## 1. Corporate Governance, Terms of Service & User Personas

HomeServe Technologies operates an on-demand marketplace connecting residential and commercial consumers with licensed, verified service providers and certified field technicians. Use of the platform constitutes acceptance of these binding governance standards.

### 1.1 User Persona Definitions & Role Hierarchy
- **Super Administrator (Admin)**: Internal platform governance team responsible for reviewing provider business credentials, monitoring ecosystem health, enforcing financial reconciliations, arbitrating disputes, and managing service taxonomies.
- **Service Provider (Agency/Vendor)**: Registered legal business entity employing certified technicians. Providers manage local service catalogs, set regional technician assignments, track commission payouts, and uphold warranty standards.
- **Field Technician**: Certified on-site specialist dispatched to execute physical home services (AC repair, plumbing, electrical, cleaning). Technicians view assigned jobs, update real-time progress, log diagnostic notes, and upload photo proof.
- **Customer**: Residential or commercial client who books scheduled slots, applies promotional discounts, makes digital payments into escrow, tracks service status, and evaluates provider performance.

### 1.2 User Registration & Identity Verification Policy
To preserve ecosystem trust, administrative accounts cannot be created via public sign-up endpoints. Any public registration attempt specifying `role: 'admin'` is rejected with **HTTP 403 Forbidden**. Service providers must submit business registration numbers, tax documents (GSTIN/PAN), and undergo a mandatory 48-hour compliance verification before appearing in customer search results.

---

## 2. Booking Lifecycle, Slot Concurrency & Cancellation Rules

### 2.1 Atomic Double-Booking Prevention & Concurrency Guarantees
Each service provider maintains designated 2-hour scheduling slots (e.g., "09:00 - 11:00", "11:00 - 13:00", "14:00 - 16:00"). The system enforces a strict concurrency ceiling of **two (2) active bookings per provider per slot**. Concurrent reservations are serialized using database-level pessimistic row locking (`SELECT ... FOR UPDATE`). When the slot capacity is reached, any simultaneous or subsequent booking attempt is immediately aborted with **HTTP 409 Conflict**, instructing the user to select an alternative slot.

### 2.2 Cancellation Refund Matrix & Fee Schedule
Refund percentages are determined automatically based on the exact elapsed time between cancellation notice and scheduled appointment timestamp:

| Notice Window Prior to Slot | Customer Refund % | Deduction / Processing Fee | Rationale & Dispatch Impact |
|:---|:---:|:---:|:---|
| **> 12 Hours Prior** | **100% Full Refund** | 0% (Zero Fee) | Full refund to original payment source. Zero operational loss. |
| **4 to 12 Hours Prior** | **90% Refund** | 10% Administrative Fee | Covers cloud processing and schedule re-indexing. |
| **2 to 4 Hours Prior** | **75% Refund** | 25% Dispatch Fee | Provider slot opportunity cost and schedule reallocation. |
| **< 2 Hours or After Dispatch** | **50% Refund** | 50% Travel Allowance | Field technician transit and mobilization compensation. |
| **Provider-Initiated Cancellation** | **100% Refund + 100 Credits** | 0% Customer Deduction | Immediate 100% reversal + courtesy convenience voucher. |

---

## 3. Pricing Model, Commission Structure & Financial Invoicing

### 3.1 Platform Commission & Provider Payout Formula
- **Base Platform Commission**: Fixed at **15.0%** across standard categories (custom enterprise rates available).
- **Net Payout Calculation**: `Provider Payout = Final Customer Amount - Platform Commission`.
- **Settlement Frequency**: Provider earnings are accumulated in platform escrow and disbursed weekly via automated batch NEFT/Razorpay transfers every Tuesday at 00:00 UTC.

### 3.2 Coupon & Promotional Discount Verification Logic
Discounts are evaluated dynamically at billing initiation (`POST /api/v1/payments/calculate`). A coupon is valid only if:
1. `is_active == True`
2. Current UTC date falls between `valid_from` and `valid_until`
3. Cart subtotal exceeds `min_booking_amount`
For percentage coupons, discounts are capped at `max_discount` to prevent platform margin loss.

### 3.3 Automated Tax Invoice Standards (GST Compliance)
Upon successful payment receipt, an unalterable digital tax invoice is auto-generated with unique sequence number `INV-2026-XXXX-RAND`. Invoices detail the 18% GST breakdown, provider business details, customer name, and service timestamp. Invoices are strictly isolated: customers can only view invoices for their own bookings (access attempts by foreign users trigger **HTTP 403 Forbidden** or **HTTP 404 Not Found**).

---

## 4. Field Technician Code of Conduct & 30-Day Quality Guarantee

Field technicians act as front-line ambassadors of HomeServe. All technicians must strictly adhere to the following professional mandates:
- **Punctuality & Status Communication**: Technicians must arrive within 15 minutes of the confirmed slot. Status transitions (`en_route`, `in_progress`, `completed`) must be updated in real time via the Technician Portal.
- **Identification & Professional Attire**: Clean uniform, visible digital photo ID badge, and safety footwear are mandatory on all assignments.
- **Work Proof Verification**: Technicians are required to capture before-service and after-service photographic evidence and upload it via `POST /api/v1/uploads` (enforcing 5MB image limit).
- **Zero-Tolerance Violations**: Soliciting off-platform cash transactions, unauthorized price modifications, verbal misconduct, or property damage results in immediate account deactivation and criminal reporting where applicable.
- **30-Day Quality Guarantee**: Every completed service is backed by a 30-day comprehensive re-work warranty. If the resolved fault reoccurs within 30 days, HomeServe dispatches a senior technician for a 100% complimentary re-inspection.

---

## 5. Customer Dispute Resolution & SLA Escalation Protocol

Customers may file formal dispute tickets via the platform dashboard within seven (7) days of service completion. Tickets are triaged by the automated routing engine based on severity:

| Severity Level | Incident Type & Trigger | Response SLA | Resolution Protocol & Authority |
|:---|:---|:---:|:---|
| **Tier 1: Critical** | Property damage, safety hazard, ethical breach | **< 2 Hours** | Immediate provider suspension, claims investigator dispatch, full refund hold. |
| **Tier 2: High** | Technician no-show, incomplete job, incorrect diagnosis | **< 4 Hours** | Re-assignment of priority technician or immediate slot cancellation with refund. |
| **Tier 3: Medium** | Billing discrepancy, coupon error, warranty query | **< 12 Hours** | Financial ledger audit, invoice adjustment, credit voucher issuance. |
| **Tier 4: Low** | General feedback, technician rating dispute, app inquiry | **< 24 Hours** | Provider feedback notification, customer support response. |

---

## 6. System Architecture, Database Design & API Specifications

HomeServe is engineered as a cloud-native, high-throughput micro-service monolith combining asynchronous Python FastAPI with modern React 19 single-page application (SPA) architecture.

### 6.1 Production Infrastructure Architecture
- **Edge & Frontend Delivery**: Netlify Global Edge CDN serving pre-rendered React 19 + Tailwind CSS assets with automated Git push-to-deploy workflows.
- **Compute & Application Tier**: Containerized FastAPI application running on Render Cloud Linux environments with Uvicorn ASGI workers.
- **Relational Persistence Tier**: SQLAlchemy ORM managing 20 normalized relational entities supporting Cloud MySQL and local SQLite engines.
- **API Communication Standard**: RESTful JSON over TLS 1.3 with OpenAPI 3.0 / Swagger interactive documentation.

### 6.2 Relational Database Schema Entity Directory (20 Entities)
The relational schema encompasses 20 tables: `users`, `customers`, `service_providers`, `technicians`, `addresses`, `service_categories`, `services`, `provider_services`, `service_areas`, `availability_slots`, `bookings`, `booking_assignments`, `booking_images`, `payments`, `invoices`, `coupons`, `reviews`, `complaints`, `provider_earnings`, and `notifications`. Referential integrity is guaranteed through foreign key constraints, cascading deletions, and composite indexing (`idx_provider_date_slot`).

### 6.3 Core REST API Endpoints Directory

| HTTP Verb & Endpoint | Authorized Roles | Functional Responsibility & Security Guarantees |
|:---|:---|:---|
| `POST /api/v1/auth/login` | Public (All) | Issues 24h JWT Bearer token upon bcrypt salted hash verification. |
| `POST /api/v1/auth/register` | Public (Customer/Provider) | Self-service sign-up. Strictly blocks admin roles with HTTP 403. |
| `POST /api/v1/auth/forgot-password` | Public (All) | Dispatches 15m single-use token via SMTP. Zero response leakage. |
| `POST /api/v1/auth/reset-password` | Public (With Token) | Validates token & 15m expiration. Zero backdoor bypass branches. |
| `POST /api/v1/bookings` | Customer, Admin | Creates booking with atomic pessimistic concurrency slot validation. |
| `PUT /api/v1/bookings/{id}/status` | Customer, Provider, Admin | Updates booking status. Technicians blocked with HTTP 403. |
| `POST /api/v1/payments/razorpay/verify` | Customer, Admin | Cryptographic HMAC-SHA256 signature verification. Zero bypass. |
| `GET /api/v1/payments/invoices/{id}` | Customer, Provider, Admin | Fetches tax invoice. Strictly enforces multi-tenant resource ownership. |
| `POST /api/v1/uploads` | Authenticated Users | Multipart photo upload. Requires login, blocks PDFs, caps at 5MB. |
| `GET /api/v1/analytics/admin/export-csv` | Super Admin Only | Streams text/csv audit attachment of all platform booking records. |

---

## 7. Information Security Architecture & OWASP Top 10 Defenses

- **A01 Broken Access Control**: Strict role dependencies (`require_role`) and ownership checks prevent horizontal and vertical privilege escalation.
- **A02 Cryptographic Failures**: Salted passwords with bcrypt work-factor 12. Decoupled JWT secrets read strictly from environment variables without hardcoded fallbacks.
- **A03 Injection**: 100% parameterized SQLAlchemy ORM queries completely eliminate SQL injection.
- **A04 Insecure Design**: Pessimistic concurrency locking (`with_for_update()`) serializes slot reservations, preventing race-condition double bookings.
- **A05 Security Misconfiguration**: Strict CORS origin headers restricted exclusively to `https://homeservicebooking.netlify.app`.
- **A07 Auth Failures & Brute Force**: In-memory sliding window rate limiter middleware (HTTP 429 Too Many Requests). 15-minute expiration on password reset tokens with zero bypass backdoors.
- **A08 Software Integrity**: Razorpay payment callbacks verify HMAC-SHA256 signatures using constant-time comparison (`hmac.compare_digest`).
- **A10 SSRF & File Upload Security**: Uploads require authentication (`Depends(get_current_active_user)`), strictly enforce a 5MB payload limit, whitelist image extensions (`.jpg`, `.png`, `.webp`), and reject executable or document payloads (`.pdf`, `.exe`, `.sh`).

---

## 8. Operational FAQs & Standard Operating Procedures (SOPs)

This section provides semantic question-and-answer pairs engineered for high-accuracy RAG vector embeddings:

- **Q: What is the cancellation policy if a customer cancels 3 hours before the scheduled service?**  
  *A: Cancellations made between 2 and 4 hours prior to the scheduled slot receive a 75% refund. A 25% dispatch preparation fee is retained to compensate the service provider for slot reservation loss.*

- **Q: Can a technician change the status of a booking directly via the general booking API?**  
  *A: No. Technicians are strictly forbidden from modifying bookings directly via `PUT /api/v1/bookings/{id}/status` (returns HTTP 403 Forbidden). Technicians must use their dedicated job endpoint (`/api/v1/technicians/me/jobs/{assignment_id}/status`) to record legitimate progress.*

- **Q: What happens if two customers simultaneously book the last available slot for a provider?**  
  *A: The atomic reservation engine applies a pessimistic database lock (`SELECT ... FOR UPDATE`) on the provider record. The first transaction commits successfully; the concurrent transaction detects that slot capacity (2 bookings) has been reached and returns HTTP 409 Conflict.*

- **Q: What is the warranty period for completed repairs?**  
  *A: All completed home services are covered by a 30-Day Quality Guarantee. If the reported issue reoccurs within 30 calendar days, the customer can file a complaint to receive a free re-inspection and re-work by a senior technician.*

- **Q: How does HomeServe protect against password reset token abuse?**  
  *A: Reset tokens expire exactly 15 minutes after generation, are invalidated immediately upon first use, are never leaked in API response payloads, and are delivered strictly via secure email or application logs. Universal demo tokens are completely disallowed.*

- **Q: How is the service provider payout calculated?**  
  *A: HomeServe deducts a standard 15.0% platform commission from the final booking amount. The remaining 85.0% is credited to the provider's earnings ledger and settled weekly via automated bank transfer every Tuesday.*

- **Q: What file formats are allowed for service completion proof uploads?**  
  *A: Only image formats (`.jpg`, `.jpeg`, `.png`, `.webp`) up to 5MB in size are permitted. Uploads require active user authentication. PDF and executable formats are strictly blocked to prevent malicious payload uploads.*
