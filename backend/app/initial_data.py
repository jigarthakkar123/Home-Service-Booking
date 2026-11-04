import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.models import (
    User, Customer, ServiceProvider, Technician, Address, ServiceCategory,
    Service, ProviderService, ServiceArea, AvailabilitySlot, Booking,
    BookingAssignment, BookingImage, Payment, Invoice, Coupon, Review,
    Complaint, Notification, ProviderEarning
)

def init_db():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        admin_check = db.query(User).filter(User.email == "admin@homeserve.com").first()
        if admin_check:
            print("Database already contains initial seed data.")
            return

        print("Seeding database with HomeServe initial data...")

        # 1. Users
        # Admin
        admin = User(
            email="admin@homeserve.com",
            hashed_password=get_password_hash("Admin@123"),
            role="admin",
            first_name="Super",
            last_name="Admin",
            phone="+91 98765 00001",
            is_active=True,
            is_verified=True
        )
        db.add(admin)

        # Provider
        provider_user = User(
            email="provider@homeserve.com",
            hashed_password=get_password_hash("Provider@123"),
            role="provider",
            first_name="Rajesh",
            last_name="Kumar",
            phone="+91 98765 00002",
            is_active=True,
            is_verified=True
        )
        db.add(provider_user)

        # Customer
        customer_user = User(
            email="customer@homeserve.com",
            hashed_password=get_password_hash("Customer@123"),
            role="customer",
            first_name="Rahul",
            last_name="Sharma",
            phone="+91 98765 00003",
            is_active=True,
            is_verified=True
        )
        db.add(customer_user)

        # Technician
        technician_user = User(
            email="technician@homeserve.com",
            hashed_password=get_password_hash("Technician@123"),
            role="technician",
            first_name="Vikram",
            last_name="Singh",
            phone="+91 98765 00004",
            is_active=True,
            is_verified=True
        )
        db.add(technician_user)

        db.flush()

        # 2. Profiles
        # Customer Profile
        customer_profile = Customer(
            user_id=customer_user.id,
            alternate_phone="+91 98765 99999",
            loyalty_points=120
        )
        db.add(customer_profile)
        db.flush()

        # Customer Address
        cust_address = Address(
            customer_id=customer_profile.id,
            title="Home",
            address_line="Flat 402, Green Glen Heights, 14th Main",
            city="Bengaluru",
            state="Karnataka",
            postal_code="560034",
            landmark="Near Sony World Junction",
            is_default=True
        )
        db.add(cust_address)

        # Provider Profile
        provider_profile = ServiceProvider(
            user_id=provider_user.id,
            company_name="QuickFix Home Solutions & Services",
            business_registration_no="REG-BLR-2023-8821",
            bio="Leading certified home repair and maintenance service providers with over 8 years of excellence across Bengaluru.",
            experience_years=8,
            verification_status="approved",
            verification_notes="Verified via GSTIN and Aadhaar business documents.",
            commission_rate=15.0,
            rating_avg=4.9,
            rating_count=38
        )
        db.add(provider_profile)
        db.flush()

        # Provider Area
        provider_area = ServiceArea(
            provider_id=provider_profile.id,
            city="Bengaluru",
            postal_code="560034",
            radius_km=25.0
        )
        db.add(provider_area)

        # Provider Slots (Monday to Sunday 09:00 - 18:00)
        for day in range(7):
            db.add(AvailabilitySlot(
                provider_id=provider_profile.id,
                day_of_week=day,
                start_time="09:00",
                end_time="12:00",
                slot_capacity=3
            ))
            db.add(AvailabilitySlot(
                provider_id=provider_profile.id,
                day_of_week=day,
                start_time="13:00",
                end_time="16:00",
                slot_capacity=3
            ))
            db.add(AvailabilitySlot(
                provider_id=provider_profile.id,
                day_of_week=day,
                start_time="16:00",
                end_time="19:00",
                slot_capacity=3
            ))

        # Technician Profile
        tech_profile = Technician(
            user_id=technician_user.id,
            provider_id=provider_profile.id,
            specialization="Master Electrician & AC Diagnostics",
            experience_years=5,
            status="available"
        )
        db.add(tech_profile)

        # 3. Categories
        categories_data = [
            ("Electrical Services", "electrical-services", "Wiring, switches, fuse board, fan repair and power installation.", "Zap", 1),
            ("Plumbing Services", "plumbing-services", "Pipe leakage, faucet replacement, water heater and sanitary fittings.", "Droplets", 2),
            ("AC Repair & Maintenance", "ac-repair-and-maintenance", "Deep jet cleaning, gas charging, cooling repair and installation.", "Wind", 3),
            ("Home Cleaning", "home-cleaning", "Deep villa/flat cleaning, bathroom sanitization and sofa shampooing.", "Sparkles", 4),
            ("Painting Services", "painting-services", "Interior wall painting, waterproof coating and texture designs.", "Paintbrush", 5),
            ("Carpentry Services", "carpentry-services", "Furniture assembly, door lock repairs and modular fittings.", "Hammer", 6),
            ("Appliance Repair", "appliance-repair", "Washing machine, microwave, refrigerator and TV maintenance.", "Tv", 7),
            ("Pest Control", "pest-control", "Termite treatment, cockroach herbal paste and bed bug control.", "ShieldAlert", 8),
        ]

        cat_map = {}
        for name, slug, desc, icon, order in categories_data:
            cat = ServiceCategory(
                name=name,
                slug=slug,
                description=desc,
                icon=icon,
                sort_order=order,
                is_active=True
            )
            db.add(cat)
            db.flush()
            cat_map[slug] = cat

        # 4. Services
        services_data = [
            ("AC Deep Jet Servicing", "ac-deep-jet-servicing", "ac-repair-and-maintenance", "Complete indoor and outdoor unit jet wash for superior cooling and power efficiency.", 699.0, 60),
            ("AC Gas Refilling & Leak Fix", "ac-gas-refilling", "ac-repair-and-maintenance", "Refrigerant recharge with pressure testing and valve fixing.", 1899.0, 90),
            ("Ceiling Fan Repair & Install", "ceiling-fan-repair-install", "electrical-services", "Motor bearing check, capacitor change and secure ceiling mounting.", 299.0, 45),
            ("Switchboard & MCB Troubleshooting", "switchboard-mcb-repair", "electrical-services", "Fix sparkings, loose wiring, short circuit isolation and MCB replacement.", 449.0, 60),
            ("Full Home Electrical Inspection", "home-electrical-safety-audit", "electrical-services", "Comprehensive earthing check, voltage balancing and load testing.", 899.0, 90),
            ("Pipe Leakage & Drainage Unclog", "pipe-leakage-drainage-unclog", "plumbing-services", "High pressure drain unclogging and PVC pipe replacement.", 549.0, 60),
            ("Tap & Shower Mixer Replacement", "tap-shower-replacement", "plumbing-services", "Premium sanitary faucet installation with zero water leakage guarantee.", 399.0, 45),
            ("Bathroom Deep Disinfection Clean", "bathroom-deep-cleaning", "home-cleaning", "Acid-free tile scrubbing, lime scale removal and sanitary shine.", 699.0, 75),
            ("Complete Full Home Deep Cleaning", "full-home-deep-cleaning", "home-cleaning", "Intensive multi-room floor buffing, window frames, kitchen and cobweb removal.", 2499.0, 240),
            ("Sofa & Mattress Foam Wash", "sofa-foam-shampooing", "home-cleaning", "Deep extraction wet shampooing removing dust mites, stains and odors.", 999.0, 90),
            ("Door Lock & Handle Replacement", "door-lock-replacement", "carpentry-services", "High security cylinder lock fitting, mortise latch and hinge alignment.", 499.0, 45),
            ("Wooden Furniture Assembly", "wooden-furniture-assembly", "carpentry-services", "Assembly of beds, wardrobe, study tables and shelving units.", 699.0, 90),
            ("Washing Machine Repair", "washing-machine-repair", "appliance-repair", "Drum noise check, inlet valve fix, motor belt and drain pump replacement.", 599.0, 60),
            ("Refrigerator Gas & Cooling Fix", "refrigerator-cooling-repair", "appliance-repair", "Thermostat calibration, compressor relay testing and cooling coil defrosting.", 799.0, 60),
            ("Whole House Pest Spray & Gel", "whole-house-pest-control", "pest-control", "Non-toxic odorless herbal gel and eco-friendly perimeter spray.", 1199.0, 90)
        ]

        all_created_services = []
        for name, slug, cat_slug, desc, price, dur in services_data:
            srv = Service(
                category_id=cat_map[cat_slug].id,
                name=name,
                slug=slug,
                short_description=desc[:120],
                full_description=desc,
                base_price=price,
                duration_minutes=dur,
                is_active=True
            )
            db.add(srv)
            db.flush()
            all_created_services.append(srv)

            # Link with QuickFix Provider
            db.add(ProviderService(
                provider_id=provider_profile.id,
                service_id=srv.id,
                custom_price=price,
                is_available=True
            ))

        # 5. Coupons
        coupons = [
            Coupon(
                code="WELCOME50",
                description="Flat 50% off on your first service booking up to ₹300",
                discount_type="percentage",
                discount_value=50.0,
                min_booking_amount=400.0,
                max_discount=300.0,
                usage_limit=500,
                is_active=True
            ),
            Coupon(
                code="HOMESERVE100",
                description="Flat ₹100 instant discount on bookings above ₹500",
                discount_type="fixed",
                discount_value=100.0,
                min_booking_amount=500.0,
                max_discount=100.0,
                usage_limit=1000,
                is_active=True
            ),
            Coupon(
                code="FESTIVE20",
                description="Special 20% discount on all home maintenance bookings",
                discount_type="percentage",
                discount_value=20.0,
                min_booking_amount=600.0,
                max_discount=500.0,
                usage_limit=200,
                is_active=True
            )
        ]
        db.add_all(coupons)

        # 6. Sample Bookings
        # Booking 1: Completed AC Servicing
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        b1 = Booking(
            booking_code="HSB-2026-0001-A1B2",
            customer_id=customer_profile.id,
            provider_id=provider_profile.id,
            service_id=all_created_services[0].id,  # AC Jet
            address_id=cust_address.id,
            scheduled_date="2026-11-01",
            scheduled_slot="10:00 - 12:00",
            status="completed",
            problem_description="AC cooling is low and making water dripping sounds.",
            service_price=699.0,
            discount_amount=100.0,
            platform_commission=89.85,
            final_amount=599.0
        )
        db.add(b1)
        db.flush()

        # Assignment for b1
        db.add(BookingAssignment(
            booking_id=b1.id,
            technician_id=tech_profile.id,
            status="completed",
            technician_notes="Cleaned filters, checked gas pressure, replaced drain pipe washer. Cooling restored."
        ))

        # Payment for b1
        p1 = Payment(
            booking_id=b1.id,
            transaction_id="TXN-HSB-984321A7",
            payment_gateway="razorpay",
            amount=599.0,
            currency="INR",
            status="paid",
            payment_method="UPI_PhonePe",
            paid_at=datetime.now(timezone.utc) - timedelta(days=3)
        )
        db.add(p1)
        db.flush()

        # Invoice for b1
        db.add(Invoice(
            invoice_number="INV-2026-0001-Q8F1",
            booking_id=b1.id,
            payment_id=p1.id,
            customer_name=f"{customer_user.first_name} {customer_user.last_name}",
            customer_email=customer_user.email,
            provider_name=provider_profile.company_name,
            service_name=all_created_services[0].name,
            subtotal=699.0,
            tax_amount=107.82,
            discount_amount=100.0,
            platform_fee=89.85,
            total_amount=599.0
        ))

        # Earning for b1
        db.add(ProviderEarning(
            provider_id=provider_profile.id,
            booking_id=b1.id,
            gross_amount=599.0,
            platform_commission_rate=15.0,
            platform_fee=89.85,
            net_earnings=509.15,
            payout_status="paid"
        ))

        # Review for b1
        db.add(Review(
            booking_id=b1.id,
            customer_id=customer_profile.id,
            provider_id=provider_profile.id,
            rating=5,
            comment="Excellent technician Vikram! Fixed the water dripping issue in 30 minutes. Super polite and professional.",
            provider_reply="Thank you Rahul! We are delighted you enjoyed our AC jet wash service."
        ))

        # Booking 2: Upcoming / Confirmed Electrical
        b2 = Booking(
            booking_code="HSB-2026-0002-C3D4",
            customer_id=customer_profile.id,
            provider_id=provider_profile.id,
            service_id=all_created_services[3].id,  # Switchboard
            address_id=cust_address.id,
            scheduled_date=today_str,
            scheduled_slot="14:00 - 16:00",
            status="confirmed",
            problem_description="Master bedroom switch sparking when geyser is switched on.",
            service_price=449.0,
            discount_amount=0.0,
            platform_commission=67.35,
            final_amount=449.0
        )
        db.add(b2)
        db.flush()

        # Notifications
        db.add(Notification(
            user_id=customer_user.id,
            title="Appointment Confirmed",
            message=f"Your electrical service booking {b2.booking_code} is confirmed for today at 14:00.",
            notification_type="booking",
            link=f"/bookings/{b2.id}"
        ))

        db.commit()
        print("Initial database seed completed successfully with all test accounts, categories, and services.")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
