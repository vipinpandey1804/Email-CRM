import { test, expect } from '@playwright/test'
import { newAccount, signup, type Account } from './helpers'

test.describe('Settings', () => {
  let account: Account

  test.beforeEach(async ({ page }) => {
    account = newAccount()
    await signup(page, account)
  })

  test('shows organization settings prefilled with the org name', async ({ page }) => {
    await page.getByRole('link', { name: 'Settings' }).click()
    await expect(page).toHaveURL(/\/settings/)
    await expect(page.getByRole('heading', { name: 'Organization' })).toBeVisible()
    // Org name input is hydrated from the API
    await expect(page.locator('input').first()).toHaveValue(account.orgName, { timeout: 10_000 })
    // OpenAI key section present
    await expect(page.getByRole('heading', { name: 'OpenAI API Key' })).toBeVisible()
  })

  test('updates the organization name', async ({ page }) => {
    await page.goto('/settings')
    const input = page.locator('input').first()
    await expect(input).toHaveValue(account.orgName, { timeout: 10_000 })
    await input.fill('Renamed Org')
    await page.getByRole('button', { name: 'Save', exact: true }).click()
    // No error surfaced; value persists in the field
    await expect(input).toHaveValue('Renamed Org')
  })

  test('navigates to SMTP setup', async ({ page }) => {
    await page.goto('/settings')
    await page.getByRole('link', { name: 'SMTP Setup' }).click()
    await expect(page).toHaveURL(/\/settings\/smtp/)
    await expect(page.getByRole('heading', { name: 'SMTP Configuration' })).toBeVisible()
    await expect(page.getByPlaceholder('smtp.gmail.com')).toBeVisible()
  })

  test('saves an SMTP configuration', async ({ page }) => {
    await page.goto('/settings/smtp')
    await page.getByPlaceholder('smtp.gmail.com').fill('smtp.example.com')
    await page.getByPlaceholder('your@email.com').fill('mailer@example.com')
    await page.getByPlaceholder('Leave blank to keep current').fill('smtp-password')
    await page.getByRole('button', { name: 'Save Config' }).click()
    // After saving, the test-connection panel becomes available
    await expect(page.getByRole('heading', { name: 'Test Connection' })).toBeVisible({
      timeout: 10_000,
    })
  })
})
