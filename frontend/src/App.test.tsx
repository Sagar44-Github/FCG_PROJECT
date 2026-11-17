import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import App from './App'
import { ApiError } from './lib/api'

const apiMocks = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('./lib/api', () => ({
  api: { get: apiMocks.get, post: apiMocks.post, fileUrl: (path: string) => path, artifactUrl: (path: string) => path },
  ApiError: class ApiError extends Error { status?: number },
}))
vi.mock('./pages/OverviewPage', () => ({ default: () => <div>Overview page body</div> }))
vi.mock('./pages/DigitalTwinPage', () => ({ default: () => <div>Digital twin page body</div> }))
vi.mock('./pages/ColourLabPage', () => ({ default: () => <div>Colour laboratory page body</div> }))
vi.mock('./pages/DonationPage', () => ({ default: () => <div>Donation simulator page body</div> }))
vi.mock('./pages/SustainabilityPage', () => ({ default: () => <div>Sustainability page body</div> }))
vi.mock('./pages/ResultsPage', () => ({ default: () => <div>Results and exports page body</div> }))

const configuration = {
  project: { title: 'Q3 research', version: '0.1.0' }, colours: {}, illuminations: {},
} as any
const dashboard = {
  project_title: 'Q3 research', configuration_sha256: 'a'.repeat(64), render_status: 'complete', render_count: 12,
  baseline_render_count: 12, render_job_count: 0, latest_render_job_status: null, render_catalog: [],
  colour_analysis_status: 'complete', colour_measurement_count: 12, delta_e_summary: [], red_trigger_summary: [],
  donation_summary: [], sustainability_summary: [], generated_at: null, software: {}, recent_jobs: [], artifact_count: 27,
} as any

describe('research application shell', () => {
  afterEach(() => cleanup())
  beforeEach(() => {
    apiMocks.get.mockReset()
    apiMocks.get.mockImplementation((path: string) => {
      if (path === '/health') return Promise.resolve({ status: 'ok' })
      if (path === '/configuration') return Promise.resolve({ configuration, sha256: 'a'.repeat(64) })
      if (path === '/dashboard') return Promise.resolve(dashboard)
      return Promise.resolve({})
    })
  })

  test('loads the real API shell and navigates between all sections', async () => {
    render(<App />)
    expect(await screen.findByText('Overview page body')).toBeTruthy()
    expect(screen.getByText('API CONNECTED')).toBeTruthy()

    fireEvent.click(screen.getByRole('button', { name: /Digital twin/i }))
    expect(await screen.findByText('Digital twin page body')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: /Colour laboratory/i }))
    expect(await screen.findByText('Colour laboratory page body')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: /Donation simulator/i }))
    expect(await screen.findByText('Donation simulator page body')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: /Sustainability/i }))
    expect(await screen.findByText('Sustainability page body')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: /Results & exports/i }))
    expect(await screen.findByText('Results and exports page body')).toBeTruthy()
  })

  test('shows an honest API outage state and fallback link', async () => {
    apiMocks.get.mockRejectedValueOnce(new ApiError('connection refused'))
    render(<App />)
    expect(await screen.findByText('Research API unavailable')).toBeTruthy()
    expect(screen.getByRole('link', { name: 'Open the Streamlit fallback' })).toBeTruthy()
    expect(screen.getByText(/connection refused/i)).toBeTruthy()
  })

  test('refresh control requests current backend configuration and summary', async () => {
    render(<App />)
    await screen.findByText('Overview page body')
    const refresh = screen.getByRole('button', { name: 'Refresh backend data' })
    fireEvent.click(refresh)
    await waitFor(() => expect(apiMocks.get).toHaveBeenCalledTimes(6))
  })
})
