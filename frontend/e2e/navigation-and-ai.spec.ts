import { test, expect } from '@playwright/test'
import { newAccount, signup, createCampaign } from './helpers'

test.describe('Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await signup(page, newAccount())
  })

  test('sidebar links navigate between sections', async ({ page }) => {
    await page.getByRole('link', { name: 'Templates' }).click()
    await expect(page).toHaveURL(/\/templates/)

    await page.getByRole('link', { name: 'Settings' }).click()
    await expect(page).toHaveURL(/\/settings/)

    await page.getByRole('link', { name: 'Campaigns' }).click()
    await expect(page).toHaveURL(/\/campaigns/)
  })
})

test.describe('AI panel', () => {
  test.beforeEach(async ({ page }) => {
    await signup(page, newAccount())
  })

  test('opens the AI assistant with all four tabs', async ({ page }) => {
    await createCampaign(page, 'AI Panel Campaign')
    await page.getByRole('button', { name: /AI Assist/ }).click()

    await expect(page.getByText('🤖 AI Assistant')).toBeVisible()
    // Four tabs
    for (const tab of ['Subject', 'Spam', 'Copy', 'CTA']) {
      await expect(page.getByRole('button', { name: tab, exact: true })).toBeVisible()
    }
    // Default tab action button
    await expect(
      page.getByRole('button', { name: /Generate 5 Subject Lines/ })
    ).toBeVisible()
  })

  test('switches AI tabs', async ({ page }) => {
    await createCampaign(page, 'AI Tabs Campaign')
    await page.getByRole('button', { name: /AI Assist/ }).click()
    await page.getByRole('button', { name: 'Spam', exact: true }).click()
    await expect(page.getByRole('button', { name: /Check Spam Score/ })).toBeVisible()
    await page.getByRole('button', { name: 'CTA', exact: true }).click()
    await expect(page.getByRole('button', { name: /Generate CTAs/ })).toBeVisible()
  })
})
