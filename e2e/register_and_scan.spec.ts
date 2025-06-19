import { test, expect } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:3000';
const TEST_EMAIL = `testuser_${Date.now()}@example.com`;
const TEST_PASSWORD = 'TestPassword123!';
const TEST_ORG = `TestOrg${Date.now()}`;
const TEST_DOMAIN = 'https://example.com';

test('registers, scans, and sees score', async ({ page }) => {
  // 1. Go to registration page and create account
  await page.goto(`${BASE_URL}/register`);
  await page.fill('input[name="first_name"]', 'Test');
  await page.fill('input[name="last_name"]', 'User');
  await page.fill('input[name="email"]', TEST_EMAIL);
  await page.fill('input[name="password"]', TEST_PASSWORD);
  await page.fill('input[name="organisation_name"]', TEST_ORG);
  await page.click('button[type="submit"]');

  // 2. Enter domain for scan (assume redirected to dashboard)
  await page.waitForURL(`${BASE_URL}/dashboard`);
  await page.fill('input[name="domain"]', TEST_DOMAIN);
  await page.click('button:has-text("Scan")');

  // 3. Wait for scan result (assume some loading indicator or result area)
  await page.waitForSelector('.scan-result, .score, [data-testid="scan-result"]', { timeout: 60000 });

  // 4. Assert score is displayed
  const score = await page.textContent('.score, [data-testid="score"]');
  expect(score).toBeTruthy();
}); 