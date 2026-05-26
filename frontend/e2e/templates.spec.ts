import { test, expect } from '@playwright/test'
import { newAccount, signup } from './helpers'

test.describe('Templates', () => {
  test.beforeEach(async ({ page }) => {
    await signup(page, newAccount())
  })

  test('renders the template library', async ({ page }) => {
    await page.getByRole('link', { name: 'Templates' }).click()
    await expect(page).toHaveURL(/\/templates/)
    await expect(page.getByRole('heading', { name: 'Email Templates' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'New Template' })).toBeVisible()
    // Category filter chips
    await expect(page.getByRole('button', { name: 'newsletter' })).toBeVisible()
  })

  test('creates a new template and opens the editor', async ({ page }) => {
    await page.goto('/templates')
    await page.getByRole('button', { name: 'New Template' }).click()
    // Navigates to the full-screen editor
    await expect(page).toHaveURL(/\/editor\/[0-9a-f-]{36}/, { timeout: 15_000 })
    // Editor chrome is present
    await expect(page.getByRole('button', { name: 'Save' })).toBeVisible({ timeout: 20_000 })
    await expect(page.getByRole('button', { name: 'Back' })).toBeVisible()
  })

  test('filters templates by category without error', async ({ page }) => {
    await page.goto('/templates')
    await page.getByRole('button', { name: 'webinar' }).click()
    // The grid should still render (no crash); heading stays visible
    await expect(page.getByRole('heading', { name: 'Email Templates' })).toBeVisible()
  })
})
