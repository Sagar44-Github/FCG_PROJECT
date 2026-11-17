import { expect, test } from '@playwright/test'
import { mkdir } from 'node:fs/promises'
import { resolve } from 'node:path'

const shots = resolve(process.cwd(), '..', 'results', 'frontend_screenshots')

test('all six sections use the live research API and export real evidence', async ({ page }) => {
  test.setTimeout(180_000)
  await mkdir(shots, { recursive: true })
  const pageErrors: string[] = []
  page.on('pageerror', (error) => pageErrors.push(error.stack ?? error.message))
  await page.goto('/')
  await expect(page.getByText('Research at a glance')).toBeVisible()
  await expect(page.getByText('API LIVE')).toBeVisible()
  await expect(page.locator('.scene-canvas-wrap canvas')).toBeVisible({ timeout: 20_000 })
  const heroModelSignature = await page.evaluate(async () => {
    const response = await fetch('/assets/supermarket/verdant_market.glb')
    const bytes = new Uint8Array(await response.arrayBuffer())
    return { status: response.status, signature: String.fromCharCode(...bytes.slice(0, 4)) }
  })
  expect(heroModelSignature).toEqual({ status: 200, signature: 'glTF' })
  const heroIlluminants = page.getByRole('group', { name: 'Change supermarket visual illuminant' })
  await heroIlluminants.getByRole('button', { name: /L2/ }).click()
  await expect(heroIlluminants.getByRole('button', { name: /L2/ })).toHaveAttribute('aria-pressed', 'true')
  await heroIlluminants.getByRole('button', { name: /L1/ }).click()
  await page.screenshot({ path: resolve(shots, 'overview_desktop.png'), fullPage: true })

  await page.getByRole('button', { name: '02 Digital twin' }).click()
  await expect(page.getByRole('heading', { name: 'Digital twin' })).toBeVisible()
  expect(pageErrors, 'after Digital Twin navigation').toEqual([])
  const blenderImage = page.locator('.render-image').first()
  await expect(blenderImage).toBeVisible()
  await expect.poll(() => blenderImage.evaluate((image: HTMLImageElement) => image.naturalWidth)).toBeGreaterThan(0)
  await page.screenshot({ path: resolve(shots, 'digital_twin_desktop.png'), fullPage: true })

  await page.getByRole('button', { name: '03 Colour laboratory' }).click()
  await expect(page.getByRole('heading', { name: 'Colour laboratory' })).toBeVisible()
  await expect(page.locator('.research-scene-banner img')).toBeVisible()
  await expect.poll(() => page.locator('.research-scene-banner img').evaluate((image: HTMLImageElement) => image.naturalWidth)).toBeGreaterThan(0)
  expect(pageErrors, 'after Colour Laboratory navigation').toEqual([])
  await page.getByLabel('Shelf-label colour').selectOption('R')
  await page.getByLabel('Illumination model').selectOption('L1')
  await page.getByRole('button', { name: 'Compute comparison' }).click()
  await expect(page.getByText('New API computation persisted')).toBeVisible()
  await expect(page.getByText(/Comparison [0-9a-f-]{36}/i)).toBeVisible()
  await page.screenshot({ path: resolve(shots, 'colour_laboratory_desktop.png'), fullPage: true })

  await page.getByRole('button', { name: '04 Donation simulator' }).click()
  await expect(page.getByRole('heading', { name: 'Donation simulator' })).toBeVisible()
  await expect(page.locator('.research-scene-banner img')).toBeVisible()
  expect(pageErrors, 'after Donation Simulator navigation').toEqual([])
  await page.getByLabel('Horizon · days').fill('2')
  await page.getByLabel('Arrivals / day').fill('8')
  await page.getByLabel('Replicates').fill('2')
  await page.getByRole('button', { name: 'Run seeded simulation' }).click()
  await expect(page.getByText('Persisted result')).toBeVisible({ timeout: 20_000 })
  await expect(page.getByText('Confusion matrix')).toBeVisible()
  await page.screenshot({ path: resolve(shots, 'donation_simulator_desktop.png'), fullPage: true })

  await page.getByRole('button', { name: '05 Sustainability' }).click()
  await expect(page.getByRole('heading', { name: 'Sustainability', exact: true })).toBeVisible()
  await expect(page.locator('.research-scene-banner img')).toBeVisible()
  expect(pageErrors, 'after Sustainability navigation').toEqual([])
  await expect(page.getByText('Food mass saved', { exact: true })).toBeVisible()
  await expect(page.getByText(/illustrative sensitivity assumptions/i).first()).toBeVisible()
  await page.screenshot({ path: resolve(shots, 'sustainability_desktop.png'), fullPage: true })

  await page.getByRole('button', { name: '06 Results & exports' }).click()
  await expect(page.getByRole('heading', { name: 'Results & exports' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'VERDANT MARKET scene renders' })).toBeVisible()
  await expect(page.locator('.result-scene-grid .scene-render img')).toHaveCount(6)
  await page.getByRole('tab', { name: 'Donation simulations' }).click()
  await expect(page.getByText(/Simulation ID/i)).toBeVisible()
  await page.screenshot({ path: resolve(shots, 'results_exports_desktop.png'), fullPage: true })
  await page.getByRole('button', { name: 'CSV', exact: true }).click()
  const csvArtifact = page.locator('.artifact-row').first()
  await expect(csvArtifact).toBeVisible()
  const csvDownloadWait = page.waitForEvent('download')
  await csvArtifact.locator('.artifact-row__download').click()
  const csvDownload = await csvDownloadWait
  expect(csvDownload.suggestedFilename()).toMatch(/\.csv$/i)
  const downloadWait = page.waitForEvent('download')
  await page.getByRole('link', { name: /Download evidence ZIP/i }).click()
  const download = await downloadWait
  expect(download.suggestedFilename()).toBe('q3_research_evidence.zip')
  expect(pageErrors).toEqual([])

  for (const width of [1280, 1024, 768]) {
    await page.setViewportSize({ width, height: 900 })
    const dimensions = await page.evaluate(() => ({ viewport: window.innerWidth, document: document.documentElement.scrollWidth }))
    expect(dimensions.document, `document overflow at ${width}px`).toBeLessThanOrEqual(dimensions.viewport)
  }

  await page.setViewportSize({ width: 390, height: 844 })
  await page.getByRole('button', { name: 'Open navigation' }).click()
  await page.getByRole('button', { name: '01 Overview' }).click()
  await expect(page.getByText('Research at a glance')).toBeVisible()
  await page.screenshot({ path: resolve(shots, 'overview_mobile.png'), fullPage: true })
  const width = await page.evaluate(() => ({ viewport: window.innerWidth, document: document.documentElement.scrollWidth }))
  expect(width.document).toBeLessThanOrEqual(width.viewport)
})

test('uses a Blender PNG when WebGL is unavailable', async ({ browser }) => {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } })
  await context.addInitScript(() => {
    const original = HTMLCanvasElement.prototype.getContext
    HTMLCanvasElement.prototype.getContext = function (kind: string, ...args: unknown[]) {
      if (kind === 'webgl' || kind === 'webgl2' || kind === 'experimental-webgl') return null
      return original.call(this, kind, ...(args as []))
    } as typeof HTMLCanvasElement.prototype.getContext
  })
  const page = await context.newPage()
  await page.goto('/')
  await expect(page.getByText('Research at a glance')).toBeVisible()
  await expect(page.locator('.scene-fallback img').first()).toBeVisible()
  await expect.poll(() => page.locator('.scene-fallback img').first().evaluate((image: HTMLImageElement) => image.naturalWidth)).toBeGreaterThan(0)
  await context.close()
})

test('submits and completes an actual twelve-condition Blender render job', async ({ page }) => {
  test.setTimeout(180_000)
  await page.goto('/')
  await expect(page.getByText('API LIVE')).toBeVisible()
  await page.getByRole('button', { name: '02 Digital twin' }).click()
  await page.getByLabel('Cycles samples').selectOption('1')
  const renderResponse = page.waitForResponse((response) => response.url().includes('/api/v1/render-jobs') && response.request().method() === 'POST')
  await page.getByRole('button', { name: 'Render all 12 conditions' }).click()
  expect((await renderResponse).status()).toBe(202)
  await expect(page.getByText(/Blender completed 12 case renders/i)).toBeVisible({ timeout: 150_000 })
})
