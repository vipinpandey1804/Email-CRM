import { type Page, expect } from '@playwright/test'

export const DEFAULT_PASSWORD = 'supersecret1'

/** Unique email per call so re-runs never collide in the shared dev DB. */
export function uniqueEmail(prefix = 'e2e'): string {
  return `${prefix}-${Date.now()}-${Math.floor(Math.random() * 1e6)}@example.com`
}

export function uniqueOrg(prefix = 'E2E Org'): string {
  return `${prefix} ${Date.now()}-${Math.floor(Math.random() * 1e4)}`
}

export interface Account {
  email: string
  password: string
  fullName: string
  orgName: string
}

export function newAccount(): Account {
  return {
    email: uniqueEmail(),
    password: DEFAULT_PASSWORD,
    fullName: 'E2E Tester',
    orgName: uniqueOrg(),
  }
}

/** Register a fresh account via the signup page and land on /campaigns. */
export async function signup(page: Page, account: Account): Promise<void> {
  await page.goto('/signup')
  await page.getByPlaceholder('Ada Lovelace').fill(account.fullName)
  await page.getByPlaceholder('Maven Labs').fill(account.orgName)
  await page.getByPlaceholder('you@company.com').fill(account.email)
  await page.getByPlaceholder('At least 8 characters').fill(account.password)
  await page.getByRole('button', { name: 'Create Account' }).click()
  await expect(page).toHaveURL(/\/campaigns/, { timeout: 15_000 })
}

/** Log in an existing account via the login page. */
export async function login(page: Page, account: Account): Promise<void> {
  await page.goto('/login')
  await page.getByPlaceholder('you@company.com').fill(account.email)
  await page.getByPlaceholder('••••••••').fill(account.password)
  await page.getByRole('button', { name: 'Sign In' }).click()
  await expect(page).toHaveURL(/\/campaigns/, { timeout: 15_000 })
}

/** Create a campaign from scratch (no template) and land on its detail page. */
export async function createCampaign(page: Page, name: string, subject = 'Hello from E2E'): Promise<void> {
  await page.goto('/campaigns/new')
  await page.getByPlaceholder('e.g. Cloud Transformation Q1 2026').fill(name)
  await page.getByPlaceholder('Transform Your Enterprise Operations').fill(subject)
  await page.getByRole('button', { name: 'Create Campaign' }).click()
  // Lands on /campaigns/:id
  await expect(page).toHaveURL(/\/campaigns\/[0-9a-f-]{36}/, { timeout: 15_000 })
}
