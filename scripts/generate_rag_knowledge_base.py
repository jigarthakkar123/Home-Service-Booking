import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Numbered canvas for "Page X of Y" footers
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running Header (Skip on Page 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "HomeServe Technologies SaaS — Corporate Policy, Architecture & Operational Knowledge Base")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 750, 558, 750)

        # Running Footer (On all pages)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)

        self.drawString(54, 32, "CONFIDENTIAL & PROPRIETARY — FOR RAG (RETRIEVAL-AUGMENTED GENERATION) SYSTEM EMBEDDINGS")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def build_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#475569'),
        spaceAfter=15
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#64748b')
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#0f766e'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletItem',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1e293b'),
        leftIndent=15,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#0f172a'),
        leftIndent=10,
        spaceAfter=4
    )

    tbl_hdr = ParagraphStyle(
        'TblHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    tbl_cell = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#1e293b')
    )

    tbl_cell_bold = ParagraphStyle(
        'TblCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#0f172a')
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor('#1e40af')
    )

    story = []

    # -------------------------------------------------------------
    # COVER / HEADER BLOCK
    # -------------------------------------------------------------
    story.append(Paragraph("HomeServe Technologies SaaS Platform", title_style))
    story.append(Paragraph("Master Corporate Policy, System Architecture, SLA Guarantees & Operational Knowledge Base", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=10))

    meta_table_data = [
        [
            Paragraph("<b>Document Version:</b> 2.4.0 (Production Release)", meta_style),
            Paragraph("<b>Target Domain:</b> On-Demand Home Services & Facility Management", meta_style)
        ],
        [
            Paragraph("<b>Effective Date:</b> 2026-2027 Calendar Years", meta_style),
            Paragraph("<b>RAG Embedding Vector ID:</b> <code>HOMESERVE-DOC-RAG-2026-V2</code>", meta_style)
        ],
        [
            Paragraph("<b>Authoritative Scope:</b> Customers, Service Providers, Technicians, Admin", meta_style),
            Paragraph("<b>Security Classification:</b> Corporate Operational Baseline & AI Context", meta_style)
        ]
    ]
    t_meta = Table(meta_table_data, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    # Executive Abstract Callout
    callout_data = [[
        Paragraph(
            "<b>RAG System Ingestion Note:</b> This document serves as the ground-truth corporate knowledge corpus "
            "for vector embeddings, semantic retrieval, and LLM-powered assistant workflows. It defines legal "
            "terms, cancellation fee tiers, payment flows, technician codes of conduct, system API schemas, "
            "and incident escalation matrices across the entire HomeServe multi-tenant ecosystem.",
            callout_style
        )
    ]]
    t_callout = Table(callout_data, colWidths=[504])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#93c5fd')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_callout)
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------
    # SECTION 1: CORPORATE GOVERNANCE & TERMS OF SERVICE
    # -------------------------------------------------------------
    story.append(Paragraph("1. Corporate Governance, Terms of Service & User Personas", h1_style))
    story.append(Paragraph(
        "HomeServe Technologies operates an on-demand marketplace connecting residential and commercial consumers "
        "with licensed, verified service providers and certified field technicians. Use of the platform constitutes "
        "acceptance of these binding governance standards.",
        body_style
    ))

    story.append(Paragraph("1.1 User Persona Definitions & Role Hierarchy", h2_style))
    story.append(Paragraph("• <b>Super Administrator (Admin):</b> Internal platform governance team responsible for reviewing provider business credentials, monitoring ecosystem health, enforcing financial reconciliations, arbitrating disputes, and managing service taxonomies.", bullet_style))
    story.append(Paragraph("• <b>Service Provider (Agency/Vendor):</b> Registered legal business entity employing certified technicians. Providers manage local service catalogs, set regional technician assignments, track commission payouts, and uphold warranty standards.", bullet_style))
    story.append(Paragraph("• <b>Field Technician:</b> Certified on-site specialist dispatched to execute physical home services (AC repair, plumbing, electrical, cleaning). Technicians view assigned jobs, update real-time progress, log diagnostic notes, and upload photo proof.", bullet_style))
    story.append(Paragraph("• <b>Customer:</b> Residential or commercial client who books scheduled slots, applies promotional discounts, makes digital payments into escrow, tracks service status, and evaluates provider performance.", bullet_style))

    story.append(Paragraph("1.2 User Registration & Identity Verification Policy", h2_style))
    story.append(Paragraph(
        "To preserve ecosystem trust, administrative accounts cannot be created via public sign-up endpoints. "
        "Any public registration attempt specifying <code>role: 'admin'</code> is rejected with <b>HTTP 403 Forbidden</b>. "
        "Service providers must submit business registration numbers, tax documents (GSTIN/PAN), and undergo a "
        "mandatory 48-hour compliance verification before appearing in customer search results.",
        body_style
    ))

    # -------------------------------------------------------------
    # SECTION 2: BOOKING, SCHEDULING & CANCELLATION POLICIES
    # -------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("2. Booking Lifecycle, Slot Concurrency & Cancellation Rules", h1_style))
    story.append(Paragraph(
        "HomeServe employs an atomic slot reservation engine to guarantee reliability and prevent overbooking across all service zones.",
        body_style
    ))

    story.append(Paragraph("2.1 Atomic Double-Booking Prevention & Concurrency Guarantees", h2_style))
    story.append(Paragraph(
        "Each service provider maintains designated 2-hour scheduling slots (e.g., '09:00 - 11:00', '11:00 - 13:00', '14:00 - 16:00'). "
        "The system enforces a strict concurrency ceiling of <b>two (2) active bookings per provider per slot</b>. "
        "Concurrent reservations are serialized using database-level pessimistic row locking (<code>SELECT ... FOR UPDATE</code>). "
        "When the slot capacity is reached, any simultaneous or subsequent booking attempt is immediately aborted with "
        "<b>HTTP 409 Conflict</b>, instructing the user to select an alternative slot.",
        body_style
    ))

    story.append(Paragraph("2.2 Cancellation Refund Matrix & Fee Schedule", h2_style))
    story.append(Paragraph(
        "Refund percentages are determined automatically based on the exact elapsed time between cancellation notice "
        "and scheduled appointment timestamp:",
        body_style
    ))

    cancel_table_data = [
        [
            Paragraph("Notice Window Prior to Slot", tbl_hdr),
            Paragraph("Customer Refund %", tbl_hdr),
            Paragraph("Deduction / Processing Fee", tbl_hdr),
            Paragraph("Rationale & Dispatch Impact", tbl_hdr)
        ],
        [
            Paragraph("<b>&gt; 12 Hours Prior</b>", tbl_cell),
            Paragraph("<b>100% Full Refund</b>", tbl_cell_bold),
            Paragraph("0% (Zero Fee)", tbl_cell),
            Paragraph("Full refund to original payment source. Zero operational loss.", tbl_cell)
        ],
        [
            Paragraph("<b>4 to 12 Hours Prior</b>", tbl_cell),
            Paragraph("<b>90% Refund</b>", tbl_cell_bold),
            Paragraph("10% Administrative Fee", tbl_cell),
            Paragraph("Covers cloud processing and schedule re-indexing.", tbl_cell)
        ],
        [
            Paragraph("<b>2 to 4 Hours Prior</b>", tbl_cell),
            Paragraph("<b>75% Refund</b>", tbl_cell_bold),
            Paragraph("25% Dispatch Preparation Fee", tbl_cell),
            Paragraph("Provider slot opportunity cost and schedule reallocation.", tbl_cell)
        ],
        [
            Paragraph("<b>&lt; 2 Hours or After Dispatch</b>", tbl_cell),
            Paragraph("<b>50% Refund</b>", tbl_cell_bold),
            Paragraph("50% Fuel & Travel Compensation", tbl_cell),
            Paragraph("Field technician transit and mobilization allowance.", tbl_cell)
        ],
        [
            Paragraph("<b>Provider-Initiated Cancellation</b>", tbl_cell),
            Paragraph("<b>100% Refund + 100 Bonus Credits</b>", tbl_cell_bold),
            Paragraph("0% Customer Deduction", tbl_cell),
            Paragraph("Immediate 100% reversal + courtesy convenience voucher.", tbl_cell)
        ]
    ]

    t_cancel = Table(cancel_table_data, colWidths=[110, 110, 110, 174])
    t_cancel.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_cancel)

    # -------------------------------------------------------------
    # SECTION 3: PRICING, PAYMENTS, COMMISSIONS & INVOICES
    # -------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("3. Pricing Model, Commission Structure & Financial Invoicing", h1_style))
    story.append(Paragraph(
        "The HomeServe financial engine automates transparent calculations, platform commission retention, "
        "promotional discounts, and regulatory tax compliance.",
        body_style
    ))

    story.append(Paragraph("3.1 Platform Commission & Provider Payout Formula", h2_style))
    story.append(Paragraph(
        "• <b>Base Platform Commission:</b> Fixed at <b>15.0%</b> across standard categories (custom enterprise rates available).<br/>"
        "• <b>Net Payout Calculation:</b> <code>Provider Payout = Final Customer Amount - Platform Commission</code>.<br/>"
        "• <b>Settlement Frequency:</b> Provider earnings are accumulated in platform escrow and disbursed weekly via "
        "automated batch NEFT/Razorpay transfers every Tuesday at 00:00 UTC.",
        body_style
    ))

    story.append(Paragraph("3.2 Coupon & Promotional Discount Verification Logic", h2_style))
    story.append(Paragraph(
        "Discounts are evaluated dynamically at billing initiation (<code>POST /api/v1/payments/calculate</code>). "
        "A coupon is valid only if: (1) <code>is_active == True</code>, (2) Current UTC date falls between <code>valid_from</code> "
        "and <code>valid_until</code>, and (3) Cart subtotal exceeds <code>min_booking_amount</code>. "
        "For percentage coupons, discounts are capped at <code>max_discount</code> to prevent platform margin loss.",
        body_style
    ))

    story.append(Paragraph("3.3 Automated Tax Invoice Standards (GST Compliance)", h2_style))
    story.append(Paragraph(
        "Upon successful payment receipt, an unalterable digital tax invoice is auto-generated with unique sequence number "
        "<code>INV-2026-XXXX-RAND</code>. Invoices detail the 18% GST breakdown, provider business details, customer name, "
        "and service timestamp. Invoices are strictly isolated: customers can only view invoices for their own bookings "
        "(access attempts by foreign users trigger <b>HTTP 403 Forbidden</b> or <b>HTTP 404 Not Found</b>).",
        body_style
    ))

    # -------------------------------------------------------------
    # SECTION 4: TECHNICIAN CODE OF CONDUCT & 30-DAY WARRANTY
    # -------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("4. Field Technician Code of Conduct & 30-Day Quality Guarantee", h1_style))
    story.append(Paragraph(
        "Field technicians act as front-line ambassadors of HomeServe. All technicians must strictly adhere to the following professional mandates:",
        body_style
    ))
    story.append(Paragraph("• <b>Punctuality & Status Communication:</b> Technicians must arrive within 15 minutes of the confirmed slot. Status transitions (<code>en_route</code>, <code>in_progress</code>, <code>completed</code>) must be updated in real time via the Technician Portal.", bullet_style))
    story.append(Paragraph("• <b>Identification & Professional Attire:</b> Clean uniform, visible digital photo ID badge, and safety footwear are mandatory on all assignments.", bullet_style))
    story.append(Paragraph("• <b>Work Proof Verification:</b> Technicians are required to capture before-service and after-service photographic evidence and upload it via <code>POST /api/v1/uploads</code> (enforcing 5MB image limit).", bullet_style))
    story.append(Paragraph("• <b>Zero-Tolerance Violations:</b> Soliciting off-platform cash transactions, unauthorized price modifications, verbal misconduct, or property damage results in immediate account deactivation and criminal reporting where applicable.", bullet_style))
    story.append(Paragraph("• <b>30-Day Quality Guarantee:</b> Every completed service is backed by a 30-day comprehensive re-work warranty. If the resolved fault reoccurs within 30 days, HomeServe dispatches a senior technician for a 100% complimentary re-inspection.", bullet_style))

    # -------------------------------------------------------------
    # SECTION 5: DISPUTE RESOLUTION & SLA ESCALATION
    # -------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("5. Customer Dispute Resolution & SLA Escalation Protocol", h1_style))
    story.append(Paragraph(
        "Customers may file formal dispute tickets via the platform dashboard within seven (7) days of service completion. "
        "Tickets are triaged by the automated routing engine based on severity:",
        body_style
    ))

    dispute_table_data = [
        [
            Paragraph("Severity Level", tbl_hdr),
            Paragraph("Incident Type & Trigger", tbl_hdr),
            Paragraph("Response SLA", tbl_hdr),
            Paragraph("Resolution Protocol & Authority", tbl_hdr)
        ],
        [
            Paragraph("<b>Tier 1: Critical</b>", tbl_cell),
            Paragraph("Property damage, safety hazard, ethical breach", tbl_cell),
            Paragraph("<b>&lt; 2 Hours</b>", tbl_cell_bold),
            Paragraph("Immediate provider suspension, claims investigator dispatch, full refund hold.", tbl_cell)
        ],
        [
            Paragraph("<b>Tier 2: High</b>", tbl_cell),
            Paragraph("Technician no-show, incomplete job, incorrect diagnosis", tbl_cell),
            Paragraph("<b>&lt; 4 Hours</b>", tbl_cell_bold),
            Paragraph("Re-assignment of priority technician or immediate slot cancellation with refund.", tbl_cell)
        ],
        [
            Paragraph("<b>Tier 3: Medium</b>", tbl_cell),
            Paragraph("Billing discrepancy, coupon error, warranty query", tbl_cell),
            Paragraph("<b>&lt; 12 Hours</b>", tbl_cell_bold),
            Paragraph("Financial ledger audit, invoice adjustment, credit voucher issuance.", tbl_cell)
        ],
        [
            Paragraph("<b>Tier 4: Low</b>", tbl_cell),
            Paragraph("General feedback, technician rating dispute, app inquiry", tbl_cell),
            Paragraph("<b>&lt; 24 Hours</b>", tbl_cell_bold),
            Paragraph("Provider feedback notification, customer support response.", tbl_cell)
        ]
    ]

    t_dispute = Table(dispute_table_data, colWidths=[90, 140, 74, 200])
    t_dispute.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f766e')),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_dispute)

    # -------------------------------------------------------------
    # SECTION 6: SYSTEM ARCHITECTURE & API REFERENCE
    # -------------------------------------------------------------
    story.append(PageBreak())  # Clean break to technical architecture
    story.append(Paragraph("6. System Architecture, Database Design & API Specifications", h1_style))
    story.append(Paragraph(
        "HomeServe is engineered as a cloud-native, high-throughput micro-service monolith combining asynchronous "
        "Python FastAPI with modern React 19 single-page application (SPA) architecture.",
        body_style
    ))

    story.append(Paragraph("6.1 Production Infrastructure Architecture", h2_style))
    story.append(Paragraph("• <b>Edge & Frontend Delivery:</b> Netlify Global Edge CDN serving pre-rendered React 19 + Tailwind CSS assets with automated Git push-to-deploy workflows.", bullet_style))
    story.append(Paragraph("• <b>Compute & Application Tier:</b> Containerized FastAPI application running on Render Cloud Linux environments with Uvicorn ASGI workers.", bullet_style))
    story.append(Paragraph("• <b>Relational Persistence Tier:</b> SQLAlchemy ORM managing 20 normalized relational entities supporting Cloud MySQL and local SQLite engines.", bullet_style))
    story.append(Paragraph("• <b>API Communication Standard:</b> RESTful JSON over TLS 1.3 with OpenAPI 3.0 / Swagger interactive documentation.", bullet_style))

    story.append(Paragraph("6.2 Relational Database Schema Entity Directory (20 Entities)", h2_style))
    story.append(Paragraph(
        "The relational schema encompasses 20 tables: <code>users</code>, <code>customers</code>, <code>service_providers</code>, "
        "<code>technicians</code>, <code>addresses</code>, <code>service_categories</code>, <code>services</code>, "
        "<code>provider_services</code>, <code>service_areas</code>, <code>availability_slots</code>, <code>bookings</code>, "
        "<code>booking_assignments</code>, <code>booking_images</code>, <code>payments</code>, <code>invoices</code>, "
        "<code>coupons</code>, <code>reviews</code>, <code>complaints</code>, <code>provider_earnings</code>, and <code>notifications</code>. "
        "Referential integrity is guaranteed through foreign key constraints, cascading deletions, and composite indexing "
        "(<code>idx_provider_date_slot</code>).",
        body_style
    ))

    story.append(Paragraph("6.3 Core REST API Endpoints Directory", h2_style))

    api_table_data = [
        [
            Paragraph("HTTP Verb & Endpoint", tbl_hdr),
            Paragraph("Authorized Roles", tbl_hdr),
            Paragraph("Functional Responsibility & Security Guarantees", tbl_hdr)
        ],
        [
            Paragraph("<code>POST /api/v1/auth/login</code>", tbl_cell),
            Paragraph("Public (All)", tbl_cell),
            Paragraph("Issues 24h JWT Bearer token upon bcrypt salted hash verification.", tbl_cell)
        ],
        [
            Paragraph("<code>POST /api/v1/auth/register</code>", tbl_cell),
            Paragraph("Public (Customer/Provider)", tbl_cell),
            Paragraph("Self-service sign-up. Strictly blocks admin roles with HTTP 403.", tbl_cell)
        ],
        [
            Paragraph("<code>POST /api/v1/auth/forgot-password</code>", tbl_cell),
            Paragraph("Public (All)", tbl_cell),
            Paragraph("Dispatches 15m single-use token via SMTP. Zero response leakage.", tbl_cell)
        ],
        [
            Paragraph("<code>POST /api/v1/auth/reset-password</code>", tbl_cell),
            Paragraph("Public (With Token)", tbl_cell),
            Paragraph("Validates token & 15m expiration. Zero backdoor bypass branches.", tbl_cell)
        ],
        [
            Paragraph("<code>POST /api/v1/bookings</code>", tbl_cell),
            Paragraph("Customer, Admin", tbl_cell),
            Paragraph("Creates booking with atomic pessimistic concurrency slot validation.", tbl_cell)
        ],
        [
            Paragraph("<code>PUT /api/v1/bookings/{id}/status</code>", tbl_cell),
            Paragraph("Customer, Provider, Admin", tbl_cell),
            Paragraph("Updates booking status. Technicians blocked with HTTP 403.", tbl_cell)
        ],
        [
            Paragraph("<code>POST /api/v1/payments/razorpay/verify</code>", tbl_cell),
            Paragraph("Customer, Admin", tbl_cell),
            Paragraph("Cryptographic HMAC-SHA256 signature verification. Zero bypass.", tbl_cell)
        ],
        [
            Paragraph("<code>GET /api/v1/payments/invoices/{id}</code>", tbl_cell),
            Paragraph("Customer, Provider, Admin", tbl_cell),
            Paragraph("Fetches tax invoice. Strictly enforces multi-tenant resource ownership.", tbl_cell)
        ],
        [
            Paragraph("<code>POST /api/v1/uploads</code>", tbl_cell),
            Paragraph("Authenticated Users", tbl_cell),
            Paragraph("Multipart photo upload. Requires login, blocks PDFs, caps at 5MB.", tbl_cell)
        ],
        [
            Paragraph("<code>GET /api/v1/analytics/admin/export-csv</code>", tbl_cell),
            Paragraph("Super Admin Only", tbl_cell),
            Paragraph("Streams text/csv audit attachment of all platform booking records.", tbl_cell)
        ]
    ]

    t_api = Table(api_table_data, colWidths=[150, 110, 244])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_api)

    # -------------------------------------------------------------
    # SECTION 7: SECURITY & OWASP TOP 10 DEFENSE CONTROLS
    # -------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("7. Information Security Architecture & OWASP Top 10 Defenses", h1_style))
    story.append(Paragraph("• <b>A01 Broken Access Control:</b> Strict role dependencies (<code>require_role</code>) and ownership checks prevent horizontal and vertical privilege escalation.", bullet_style))
    story.append(Paragraph("• <b>A02 Cryptographic Failures:</b> Salted passwords with bcrypt work-factor 12. Decoupled JWT secrets read strictly from environment variables without hardcoded fallbacks.", bullet_style))
    story.append(Paragraph("• <b>A03 Injection:</b> 100% parameterized SQLAlchemy ORM queries completely eliminate SQL injection.", bullet_style))
    story.append(Paragraph("• <b>A04 Insecure Design:</b> Pessimistic concurrency locking (<code>with_for_update()</code>) serializes slot reservations, preventing race-condition double bookings.", bullet_style))
    story.append(Paragraph("• <b>A05 Security Misconfiguration:</b> Strict CORS origin headers restricted exclusively to <code>https://homeservicebooking.netlify.app</code>.", bullet_style))
    story.append(Paragraph("• <b>A07 Auth Failures & Brute Force:</b> In-memory sliding window rate limiter middleware (HTTP 429 Too Many Requests). 15-minute expiration on password reset tokens with zero bypass backdoors.", bullet_style))
    story.append(Paragraph("• <b>A08 Software Integrity:</b> Razorpay payment callbacks verify HMAC-SHA256 signatures using constant-time comparison (<code>hmac.compare_digest</code>).", bullet_style))
    story.append(Paragraph("• <b>A10 SSRF & File Upload Security:</b> Uploads require authentication (<code>Depends(get_current_active_user)</code>), strictly enforce a 5MB payload limit, whitelist image extensions (<code>.jpg</code>, <code>.png</code>, <code>.webp</code>), and reject executable or document payloads (<code>.pdf</code>, <code>.exe</code>, <code>.sh</code>).", bullet_style))

    # -------------------------------------------------------------
    # SECTION 8: SOP & FAQ KNOWLEDGE BASE (OPTIMIZED FOR RAG)
    # -------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("8. Operational FAQs & Standard Operating Procedures (SOPs)", h1_style))
    story.append(Paragraph(
        "This section provides semantic question-and-answer pairs engineered for high-accuracy RAG vector embeddings:",
        body_style
    ))

    faqs = [
        ("Q: What is the cancellation policy if a customer cancels 3 hours before the scheduled service?",
         "A: Cancellations made between 2 and 4 hours prior to the scheduled slot receive a 75% refund. A 25% dispatch preparation fee is retained to compensate the service provider for slot reservation loss."),
        ("Q: Can a technician change the status of a booking directly via the general booking API?",
         "A: No. Technicians are strictly forbidden from modifying bookings directly via PUT /api/v1/bookings/{id}/status (returns HTTP 403 Forbidden). Technicians must use their dedicated job endpoint (/api/v1/technicians/me/jobs/{assignment_id}/status) to record legitimate progress."),
        ("Q: What happens if two customers simultaneously book the last available slot for a provider?",
         "A: The atomic reservation engine applies a pessimistic database lock (SELECT ... FOR UPDATE) on the provider record. The first transaction commits successfully; the concurrent transaction detects that slot capacity (2 bookings) has been reached and returns HTTP 409 Conflict."),
        ("Q: What is the warranty period for completed repairs?",
         "A: All completed home services are covered by a 30-Day Quality Guarantee. If the reported issue reoccurs within 30 calendar days, the customer can file a complaint to receive a free re-inspection and re-work by a senior technician."),
        ("Q: How does HomeServe protect against password reset token abuse?",
         "A: Reset tokens expire exactly 15 minutes after generation, are invalidated immediately upon first use, are never leaked in API response payloads, and are delivered strictly via secure email or application logs. Universal demo tokens are completely disallowed."),
        ("Q: How is the service provider payout calculated?",
         "A: HomeServe deducts a standard 15.0% platform commission from the final booking amount. The remaining 85.0% is credited to the provider's earnings ledger and settled weekly via automated bank transfer every Tuesday."),
        ("Q: What file formats are allowed for service completion proof uploads?",
         "A: Only image formats (.jpg, .jpeg, .png, .webp) up to 5MB in size are permitted. Uploads require active user authentication. PDF and executable formats are strictly blocked to prevent malicious payload uploads.")
    ]

    for q, a in faqs:
        story.append(Paragraph(f"<b>{q}</b>", h2_style))
        story.append(Paragraph(a, body_style))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated RAG Knowledge Base PDF at: {output_path}")


if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parent.parent
    output_pdf = root_dir / "HomeServe_Company_Policy_and_System_Knowledge_Base.pdf"
    build_pdf(str(output_pdf))
