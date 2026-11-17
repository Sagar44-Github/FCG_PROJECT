import { Suspense, lazy, useCallback, useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Activity, LoaderCircle } from 'lucide-react'
import { Layout, type SectionId } from './components/Layout'
import { ErrorState, LoadingState } from './components/ui'
import { api, ApiError } from './lib/api'
import type { ColourId, ConfigurationResponse, DashboardSummary, IlluminationId } from './lib/types'

const OverviewPage = lazy(() => import('./pages/OverviewPage'))
const DigitalTwinPage = lazy(() => import('./pages/DigitalTwinPage'))
const ColourLabPage = lazy(() => import('./pages/ColourLabPage'))
const DonationPage = lazy(() => import('./pages/DonationPage'))
const SustainabilityPage = lazy(() => import('./pages/SustainabilityPage'))
const ResultsPage = lazy(() => import('./pages/ResultsPage'))

export default function App() {
  const [active, setActive] = useState<SectionId>('overview')
  const [config, setConfig] = useState<ConfigurationResponse | null>(null)
  const [dashboard, setDashboard] = useState<DashboardSummary | null>(null)
  const [apiStatus, setApiStatus] = useState('checking')
  const [selectedColor, setSelectedColor] = useState<ColourId>('R')
  const [selectedIllumination, setSelectedIllumination] = useState<IlluminationId>('L1')
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)

  const refresh = useCallback(async () => {
    setRefreshing(true)
    setError(null)
    try {
      const [health, configuration, summary] = await Promise.all([
        api.get<{ status: string }>('/health'),
        api.get<ConfigurationResponse>('/configuration'),
        api.get<DashboardSummary>('/dashboard'),
      ])
      setApiStatus(health.status)
      setConfig(configuration)
      setDashboard(summary)
    } catch (reason) {
      const message = reason instanceof ApiError ? reason.message : 'The API request failed.'
      setApiStatus('offline')
      setError(message)
    } finally { setRefreshing(false) }
  }, [])

  useEffect(() => { void refresh() }, [refresh])

  if (!config || !dashboard) return <div className="boot-screen"><div className="boot-brand"><Activity size={22} /> SPECTRAL / LAB</div>{error ? <div className="boot-error"><ErrorState title="Research API unavailable" message={`${error} Start FastAPI on port 8000, then retry.`} onRetry={() => void refresh()} /><a href="http://127.0.0.1:8501">Open the Streamlit fallback</a></div> : <div className="boot-loading"><LoaderCircle className="spin" size={20} /><LoadingState label="Connecting to the research API and saved outputs…" /></div>}</div>

  const pageProps = { config: config.configuration, dashboard, refresh, selectedColor, onSelectColor: setSelectedColor, selectedIllumination, onSelectIllumination: setSelectedIllumination }
  return <Layout active={active} onNavigate={setActive} apiStatus={apiStatus} configHash={config.sha256} onRefresh={() => void refresh()} refreshing={refreshing}>
    <motion.div key={active} className="route-content" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.18, ease: 'easeOut' }}>
      <Suspense fallback={<div className="route-loading"><LoaderCircle className="spin" size={18} />Loading research view…</div>}>
        {active === 'overview' && <OverviewPage {...pageProps} onNavigate={setActive} />}
        {active === 'digital-twin' && <DigitalTwinPage {...pageProps} onNavigate={setActive} />}
        {active === 'colour-lab' && <ColourLabPage {...pageProps} onNavigate={setActive} />}
        {active === 'donation' && <DonationPage {...pageProps} />}
        {active === 'sustainability' && <SustainabilityPage {...pageProps} onNavigate={setActive} />}
        {active === 'results' && <ResultsPage {...pageProps} />}
      </Suspense>
    </motion.div>
  </Layout>
}
