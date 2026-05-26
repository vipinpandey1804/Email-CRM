import { test, expect } from '@playwright/test'
import { newAccount, signup, login } from './helpers'

test.describe('Authentication', () => {
  test('redirects an unauthenticated user to /login', async ({ page }) => {
    await page.goto('/campaigns')
    await expect(page).toHaveURL(/\/login/)
    await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible()
  })

  test('signs up a new user and lands on the dashboard', async ({ page }) => {
    const account = newAccount()
    await signup(page, account)
    // Sidebar + topbar present
    await expect(page.getByRole('link', { name: 'Campaigns' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Campaigns' })).toBeVisible()
  })

  test('rejects signup with a too-short password', async ({ page }) => {
    const account = newAccount()
    await page.goto('/signup')
    await page.getByPlaceholder('Ada Lovelace').fill(account.fullName)
    await page.getByPlaceholder('Maven Labs').fill(account.orgName)
    await page.getByPlaceholder('you@company.com').fill(account.email)
    // The field has minLength=8; use 7 chars and bypass native validation by
    // asserting we never leave /signup.
    await page.getByPlaceholder('At least 8 characters').fill('short12')
    await page.getByRole('button', { name: 'Create Account' }).click()
    await expect(page).toHaveURL(/\/signup/)
  })

  test('logs in an existing user', async ({ page }) => {
    const account = newAccount()
    await signup(page, account)
    // Log out, then back in
    await page.getByRole('button', { name: 'Logout' }).click()
    await expect(page).toHaveURL(/\/login/)
    await login(page, account)
    await expect(page.getByRole('heading', { name: 'Campaigns' })).toBeVisible()
  })

  test('shows an error on wrong password', async ({ page }) => {
    const account = newAccount()
    await signup(page, account)
    await page.getByRole('button', { name: 'Logout' }).click()
    await expect(page).toHaveURL(/\/login/)
    await page.getByPlaceholder('you@company.com').fill(account.email)
    await page.getByPlaceholder('••••••••').fill('wrong-password')
    await page.getByRole('button', { name: 'Sign In' }).click()
    await expect(page.getByText(/invalid/i)).toBeVisible()
    await expect(page).toHaveURL(/\/login/)
  })

  test('logs out back to the login page', async ({ page }) => {
    const account = newAccount()
    await signup(page, account)
    await page.getByRole('button', { name: 'Logout' }).click()
    await expect(page).toHaveURL(/\/login/)
  })
})
