import { test, expect } from '@playwright/test'
import { newAccount, signup, createCampaign } from './helpers'

test.describe('Campaigns', () => {
  test.beforeEach(async ({ page }) => {
    await signup(page, newAccount())
  })

  test('shows an empty state with no campaigns', async ({ page }) => {
    await expect(page.getByText('No campaigns yet')).toBeVisible()
  })

  test('creates a campaign from scratch', async ({ page }) => {
    await createCampaign(page, 'Launch Campaign', 'Big news inside')
    await expect(page.getByRole('heading', { name: 'Launch Campaign' })).toBeVisible()
    await expect(page.getByText('Big news inside')).toBeVisible()
    // Back to list shows the campaign
    await page.getByRole('link', { name: 'Campaigns' }).click()
    await expect(page.getByText('Launch Campaign')).toBeVisible()
  })

  test('blocks sending until at least one recipient exists', async ({ page }) => {
    await createCampaign(page, 'No Recipients Yet')
    await expect(
      page.getByText(/Add at least one recipient/i)
    ).toBeVisible()
    await expect(page.getByRole('button', { name: 'Send Now' })).toBeDisabled()
  })

  test('adds recipients then enables and performs send', async ({ page }) => {
    await createCampaign(page, 'Send Test Campaign')

    // Add two recipients via the paste box
    await page
      .getByPlaceholder(/Paste emails/)
      .fill('alice@example.com, bob@example.com')
    await page.getByRole('button', { name: 'Add Recipients' }).click()

    // They appear in the list
    await expect(page.getByText('alice@example.com')).toBeVisible()
    await expect(page.getByText('bob@example.com')).toBeVisible()

    // Send is now enabled
    const sendBtn = page.getByRole('button', { name: 'Send Now' })
    await expect(sendBtn).toBeEnabled()
    await sendBtn.click()

    // Status flips to SENDING (no worker running, so it stays queued/sending)
    await expect(page.getByText('SENDING')).toBeVisible({ timeout: 15_000 })
  })

  test('removes a recipient', async ({ page }) => {
    await createCampaign(page, 'Remove Recipient Campaign')
    await page.getByPlaceholder(/Paste emails/).fill('carol@example.com')
    await page.getByRole('button', { name: 'Add Recipients' }).click()
    await expect(page.getByText('carol@example.com')).toBeVisible()

    // The single trash button in the recipients table
    await page.getByRole('row', { name: /carol@example.com/ }).getByRole('button').click()
    await expect(page.getByText('carol@example.com')).toHaveCount(0)
  })
})
