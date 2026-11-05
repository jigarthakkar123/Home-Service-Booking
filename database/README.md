# HomeServe Technologies — Database Setup & SQL Scripts

This directory contains standalone, production-ready SQL scripts for all **20 Relational Database Tables** specified in the Vibe Coding Capstone Specification.

## Files
1. `schema.sql`: Full DDL script defining tables, primary keys, foreign key constraints, default values, and indexes (MySQL 8.0+ and SQLite compatible).
2. `seed_data.sql`: DML script populating all 8 categories, 15 core services, verified users, coupons, sample bookings, payments, and invoices.

---

## How to Run in MySQL Workbench / phpMyAdmin / Terminal

### Option 1: MySQL CLI
```bash
# 1. Log in to your MySQL server
mysql -u root -p

# 2. Create the database
CREATE DATABASE homeserve_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE homeserve_db;

# 3. Import Schema & Seed Data
SOURCE schema.sql;
SOURCE seed_data.sql;
```

### Option 2: MySQL Workbench
1. Open MySQL Workbench and connect to your instance.
2. Click **File -> Open SQL Script...** and select `schema.sql`.
3. Click the **Execute (Lightning bolt)** button.
4. Repeat for `seed_data.sql`.

### Option 3: Docker (1-Command MySQL Setup)
```bash
docker run --name homeserve-mysql -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=homeserve_db -p 3306:3306 -d mysql:8.0
docker exec -i homeserve-mysql mysql -uroot -proot homeserve_db < schema.sql
docker exec -i homeserve-mysql mysql -uroot -proot homeserve_db < seed_data.sql
```

---

## 20 Relational Entities Verification Matrix

| Table # | Table Name | Purpose | Primary Key | Foreign Keys |
|:---:|:---|:---|:---|:---|
| 1 | `users` | User identity & authentication | `id` | - |
| 2 | `customers` | Customer loyalty & profile | `id` | `user_id -> users(id)` |
| 3 | `service_providers` | Contractor KYC & business profiles | `id` | `user_id -> users(id)` |
| 4 | `technicians` | Field workforce records | `id` | `user_id -> users(id)`, `provider_id -> service_providers(id)` |
| 5 | `addresses` | Multi-address customer records | `id` | `customer_id -> customers(id)` |
| 6 | `service_categories` | 8 core home service categories | `id` | - |
| 7 | `services` | 15 detailed service offerings | `id` | `category_id -> service_categories(id)` |
| 8 | `provider_services` | M:N provider service catalog | `id` | `provider_id`, `service_id` |
| 9 | `service_areas` | Geographical radius & postal boundaries | `id` | `provider_id -> service_providers(id)` |
| 10 | `availability_slots` | Working hours & capacity slots | `id` | `provider_id -> service_providers(id)` |
| 11 | `bookings` | Booking lifecycle & pricing | `id` | `customer_id`, `provider_id`, `service_id`, `address_id` |
| 12 | `booking_assignments` | Dispatch delegation to technicians | `id` | `booking_id -> bookings(id)`, `technician_id -> technicians(id)` |
| 13 | `booking_images` | Before/after work proof photos | `id` | `booking_id -> bookings(id)` |
| 14 | `payments` | Transaction ledger & gateway tokens | `id` | `booking_id -> bookings(id)` |
| 15 | `invoices` | Automated 18% GST tax invoices | `id` | `booking_id -> bookings(id)`, `payment_id -> payments(id)` |
| 16 | `coupons` | Promo codes & discount logic | `id` | - |
| 17 | `reviews` | 5-star ratings & provider replies | `id` | `booking_id`, `customer_id`, `provider_id` |
| 18 | `complaints` | Dispute resolution tickets | `id` | `booking_id`, `customer_id` |
| 19 | `notifications` | In-app transactional alerts | `id` | `user_id -> users(id)` |
| 20 | `provider_earnings` | Payout ledger & 15% platform commission | `id` | `provider_id`, `booking_id` |
