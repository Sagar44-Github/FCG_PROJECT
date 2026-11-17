import { useState } from 'react'
import { Activity, Aperture, BarChart3, ChevronDown, FlaskConical, Menu, Orbit, PackageCheck, PanelLeftClose, RefreshCw, ShieldCheck, Sprout, X } from 'lucide-react'
import { AnimatePresence, motion } from 'framer-motion'
import type { ReactNode } from 'react'
import { Badge, Button } from './ui'

export type SectionId = 'overview' | 'digital-twin' | 'colour-lab' | 'donation' | 'sustainability' | 'results'
const navigation = [
  { id: 'overview', label: 'Overview', index: '01', icon: Aperture, group: 'OBSERVATORY' },
  { id: 'digital-twin', label: 'Digital twin', index: '02', icon: Orbit, group: 'INSTRUMENTS' },
  { id: 'colour-lab', label: 'Colour laboratory', index: '03', icon: FlaskConical, group: 'INSTRUMENTS' },
  { id: 'donation', label: 'Donation simulator', index: '04', icon: PackageCheck, group: 'MODELS' },
  { id: 'sustainability', label: 'Sustainability', index: '05', icon: Sprout, group: 'MODELS' },
  { id: 'results', label: 'Results & exports', index: '06', icon: BarChart3, group: 'EVIDENCE' },
] as const

export function Layout({ active, onNavigate, apiStatus, configHash, children, onRefresh, refreshing }: {
  active: SectionId; onNavigate: (page: SectionId) => void; apiStatus: string; configHash?: string; children: ReactNode; onRefresh: () => void; refreshing: boolean
}) {
  const [drawerOpen, setDrawerOpen] = useState(false)
  const activeItem = navigation.find((item) => item.id === active)!
  const navigate = (id: SectionId) => { onNavigate(id); setDrawerOpen(false) }
  return <div className="app-frame">
    <AnimatePresence>{drawerOpen && <motion.button className="mobile-scrim" aria-label="Close navigation" onClick={() => setDrawerOpen(false)} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} />}</AnimatePresence>
    <aside className={`sidebar ${drawerOpen ? 'sidebar--open' : ''}`}>
      <div className="brand-lockup"><div className="brand-mark"><Orbit size={22} strokeWidth={1.6} /></div><div><strong>SPECTRAL<span> / </span>LAB</strong><small>Q3 RESEARCH SYSTEM</small></div><button className="sidebar-close" onClick={() => setDrawerOpen(false)} aria-label="Close navigation"><X size={18} /></button></div>
      <div className="sidebar-context"><span className="status-pip" /><span>COMPUTATIONAL OBSERVATORY</span><span className="context-code">V{configHash?.slice(0, 3).toUpperCase() ?? '01'}</span></div>
      <nav className="primary-nav" aria-label="Research sections">
        {(['OBSERVATORY', 'INSTRUMENTS', 'MODELS', 'EVIDENCE']).map((group) => <div className="nav-group" key={group}><span className="nav-group__label">{group}</span>{navigation.filter((item) => item.group === group).map((item) => {
          const Icon = item.icon
          return <button key={item.id} className={`nav-item ${active === item.id ? 'nav-item--active' : ''}`} onClick={() => navigate(item.id)} aria-current={active === item.id ? 'page' : undefined}>
            <span className="nav-item__index">{item.index}</span><Icon size={17} strokeWidth={1.7} /><span>{item.label}</span>{active === item.id && <motion.i className="nav-active-indicator" layoutId="nav-indicator" />}
          </button>
        })}</div>)}
      </nav>
      <div className="sidebar-spacer" />
      <div className="sidebar-footnote"><div className="sidebar-footnote__icon"><ShieldCheck size={15} /></div><div><strong>Model provenance active</strong><small>Computed outputs · no human data</small></div></div>
      <a className="fallback-link" href="http://127.0.0.1:8501" target="_blank" rel="noreferrer"><PanelLeftClose size={14} /> Open Streamlit fallback <span>↗</span></a>
    </aside>
    <main className="main-shell">
      <header className="topbar"><div className="topbar__left"><button className="mobile-menu" onClick={() => setDrawerOpen(true)} aria-label="Open navigation"><Menu size={19} /></button><span className="breadcrumb-root">Q3 /</span><span>{activeItem.label}</span><ChevronDown className="breadcrumb-chevron" size={13} /></div>
        <div className="topbar__right"><Badge tone={apiStatus === 'ok' ? 'success' : 'warning'} dot>{apiStatus === 'ok' ? 'API CONNECTED' : 'API CHECK'}</Badge><span className="topbar-divider" /><span className="config-digest" title={configHash}>CFG · {configHash?.slice(0, 8) ?? 'loading'}</span><Button variant="quiet" icon={<RefreshCw className={refreshing ? 'spin' : ''} size={15} />} onClick={onRefresh} aria-label="Refresh backend data" title="Refresh backend data">Refresh</Button></div>
      </header>
      <div className="page-canvas"><div className="page-body">{children}</div><footer className="app-footer"><span><Activity size={13} /> SPECTRAL OBSERVATORY <i>·</i> COMPUTATIONAL RESEARCH INTERFACE</span><span>V0.1.0 <i>·</i> USER-SPACE MODELS</span></footer></div>
    </main>
  </div>
}
