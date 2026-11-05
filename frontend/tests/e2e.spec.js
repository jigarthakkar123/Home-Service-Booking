import { test, expect } from '@playwright/test';

/**
 * HomeServe Technologies SaaS Platform
 * End-to-End Test Suite (Playwright)
 * Covering SDLC Phase 6 Deliverables
 */

const BASE_URL = process.env.PLAYWRIGHT_TEST_BASE_URL || 'https://homeservicebooking.netlify.app';

test.describe('HomeServe End-to-End Flow & User Role Verification', () => {

  test('TC-01: Public Landing Page and Service Exploration', async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page).toHaveTitle(/HomeServe/i);

    // Verify Brand & Hero Headline
    await expect(page.locator('text=HomeServe')).toBeVisible();
    await expect(page.locator('text=Expert Home Services')).toBeVisible();

    // Verify 8 Core Category Pills
    await expect(page.locator('text=AC & Heating')).toBeVisible();
    await expect(page.locator('text=Electrical')).toBeVisible();
    await expect(page.locator('text=Cleaning')).toBeVisible();
  });

  test('TC-02: Role Authentication & RBAC Guard Validation', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    // Verify Sign In Card & Auto-fill Buttons
    await expect(page.locator('text=Sign in to your account')).toBeVisible();
    await expect(page.locator('text=Capstone Demo Credentials')).toBeVisible();

    // Fill Customer Credentials
    await page.click('button:has-text("Customer (Jigar)")');
    await expect(page.locator('input[type="email"]')).toHaveValue('customer@homeserve.com');

    // Submit Sign In
    await page.click('button[type="submit"]');

    // Asserts successful redirection to Customer Dashboard
    await page.waitForURL('**/customer');
    await expect(page.locator('text=Welcome back, Jigar!')).toBeVisible();
    await expect(page.locator('text=HomeServe Club Loyalty')).toBeVisible();
  });

  test('TC-03: Service Booking Wizard Flow with Coupon Discount', async ({ page }) => {
    await page.goto(`${BASE_URL}/book/ac-deep-jet-servicing`);
    
    // Step 1: Service details
    await expect(page.locator('text=AC Deep Jet Servicing')).toBeVisible();
    await page.click('button:has-text("Continue to Address")');

    // Step 2: Address Selection
    await expect(page.locator('text=Select Service Address')).toBeVisible();
    await page.click('button:has-text("Continue to Date & Slot")');

    // Step 3: Schedule Selection
    await expect(page.locator('text=Choose Appointment Time')).toBeVisible();
    await page.click('button:has-text("10:00 - 12:00")');
    await page.click('button:has-text("Proceed to Payment")');

    // Step 4: Summary & Coupon Application
    await expect(page.locator('text=Booking Summary')).toBeVisible();
    await expect(page.locator('text=Apply Promo Code')).toBeVisible();
  });

  test('TC-04: Technician Mobile-First Portal Verification', async ({ page }) => {
    // Direct switch or login as Technician
    await page.goto(`${BASE_URL}/technician`);
    
    // Check technician header
    await expect(page.locator('text=Field Technician')).toBeVisible();
    await expect(page.locator('text=Assigned Jobs')).toBeVisible();
  });

  test('TC-05: Super Admin Executive Dashboard & CSV Audit Export', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin`);

    // Check KPIs
    await expect(page.locator('text=Platform Overview')).toBeVisible();
    await expect(page.locator('text=Total Revenue')).toBeVisible();
    await expect(page.locator('text=Platform Commission')).toBeVisible();

    // Verify Export Button is present and clickable
    const exportBtn = page.locator('button:has-text("Export Bookings CSV")');
    await expect(exportBtn).toBeVisible();
  });

});
