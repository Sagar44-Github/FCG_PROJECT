import { lazy, Suspense, useEffect, useState } from 'react'
import { Activity, ArrowRight, ArrowUpRight, Beaker, Boxes, CircleHelp, Clock3, FlaskConical, Leaf, LoaderCircle, ShieldCheck } from 'lucide-react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Badge, Button, EmptyState, MetricCard, Panel, PanelHeading, SectionTitle } from '../components/ui'
import type { SectionId } from '../components/Layout'
import { api } from '../lib/api'
import type { ColourId, DashboardSummary, DonationSimulation, IlluminationId, ProjectConfiguration } from '../lib/types'
import { numeric } from '../lib/csv'

const SpectralScene = lazy(() => import('../components/SpectralScene').then((module) => ({ default: module.SpectralScene })))

export default function OverviewPage({ config, dashboard, onNavigate, selectedColor, onSelectColor, selectedIllumination, onSelectIllumination }: { config: ProjectConfiguration; dashboard: DashboardSummary; onNavigate: (page: SectionId) => void; selectedColor: ColourId; onSelectColor: (id: ColourId) => void; selectedIllumination: IlluminationId; onSelectIllumination: (id: IlluminationId) => void }) {
  const [latest, setLatest] = useState<DonationSimulation | null>(null)
  useEffect(() => {
    let alive = true
    api.get<{ items: DonationSimulation[] }>('/donation-simulations?limit=1&offset=0').then((simulations) => {
      if (!alive) return
      setLatest(simulations.items[0] ?? null)
    }).catch(() => undefined)
    return () => { alive = false }
  }, [])

  const redRows = dashboard.red_trigger_summary.filter((row) => row.colour_id === 'R')
  const l1Red = dashboard.red_trigger_summary.find((row) => row.colour_id === 'R' && row.illumination_id === 'L1')
  const capacity = latest?.capacity_per_day ?? config.donation.donation_capacities_per_day[1] ?? 25
  const centralImpact = latest?.result?.sustainability_scenarios?.central?.mean_avoided_emissions_kgco2e
  const activeRender = dashboard.render_catalog.find((item) => item.colour_id === selectedColor && item.illumination_id === selectedIllumination)
  const conditionCount = Object.keys(config.colours).length * Object.keys(config.illuminations).length
  const recent = dashboard.recent_jobs.slice(0, 4)

  return <>
    <section className="overview-hero">
      <div className="overview-hero__copy">
        <div className="hero-orbit-label">CHROMATIC OBSERVATORY <Badge tone="violet">SIMULATION ENVIRONMENT</Badge></div>
        <h1>Colour signals,<br /><span>measured in light.</span></h1>
        <p>A computational observatory for how virtual shelf-label colours shift under daylight and retail LED spectra — and how those shifts shape near-expiry donation decisions.</p>
        <div className="hero-actions"><Button onClick={() => onNavigate('digital-twin')} icon={<ArrowRight size={15} />}>Explore digital twin</Button><Button variant="secondary" onClick={() => onNavigate('colour-lab')} icon={<FlaskConical size={15} />}>Open colour laboratory</Button></div>
        <div className="hero-condition-switch" role="group" aria-label="Change supermarket visual illuminant">{(['L1','L2','L3'] as IlluminationId[]).map((id) => <button key={id} aria-pressed={selectedIllumination === id} onClick={() => onSelectIllumination(id)}><span>{id}</span>{id === 'L1' ? 'D65' : `${config.illuminations[id].cct_kelvin} K`}</button>)}</div>
        <div className="hero-illumination-note">Visual RGB lighting preview · Python spectral model remains authoritative.</div>
        <div className="hero-under-note"><ShieldCheck size={13} /> Scientific outputs come from the FastAPI spectral and simulation pipeline.</div>
      </div>
      <div className="hero-visual"><Suspense fallback={<div className="scene-fallback__placeholder"><LoaderCircle className="spin" size={18} /> Initialising observatory…</div>}><SpectralScene config={config} selectedColor={selectedColor} selectedIllumination={selectedIllumination} onSelect={onSelectColor} fallbackUrl={activeRender ? api.fileUrl(activeRender.url) : '/assets/supermarket/01_supermarket_hero.png'} /></Suspense><span className="overview-hero__watermark">SP–04</span></div>
    </section>

    <div className="research-status"><div className="research-status__left"><Activity size={15} /><span><strong>{dashboard.project_title}</strong> · model provenance is active</span></div><div className="research-status__right"><Badge tone="success" dot>API LIVE</Badge><span>CFG {dashboard.configuration_sha256.slice(0, 8)}</span><span>{config.project.observer}</span></div></div>

    <SectionTitle eyebrow="Live system readout" title="Research at a glance" trailing={<span className="tagline"><Clock3 size={13} /> {dashboard.generated_at ? new Date(dashboard.generated_at).toLocaleString() : 'No full analysis run saved'}</span>} />
    <div className="grid grid--4">
      <MetricCard label="Rendering conditions" value={String(conditionCount)} note={`${dashboard.baseline_render_count}/${conditionCount} baseline renders · ${dashboard.render_count} total case images`} accent="cyan" icon={<Boxes size={15} />} />
      <MetricCard label="Red warning · ΔE00" value={l1Red ? numeric(l1Red.delta_e00).toFixed(2) : '—'} note="R donate-now · D65 vs virtual print" accent="red" icon={<Beaker size={15} />} />
      <MetricCard label="Missed donation trigger" value={l1Red ? `${(numeric(l1Red.simulated_missed_donation_rate) * 100).toFixed(1)}%` : '—'} note="Synthetic observer · D65 · 10,000 trials" accent="yellow" icon={<CircleHelp size={15} />} />
      <MetricCard label="Potential CO₂e avoided" value={centralImpact === undefined ? '—' : `${(numeric(centralImpact) / 1000).toFixed(2)} t`} note={centralImpact === undefined ? 'Run a donation simulation to calculate' : `Central sensitivity scenario · ${latest?.result?.mean?.units_saved?.toFixed?.(0) ?? '—'} simulated units saved`} accent="green" icon={<Leaf size={15} />} />
    </div>

    <SectionTitle eyebrow="Configured signal set" title="Four actions. Three illumination models." />
    <div className="color-roster">{Object.entries(config.colours).map(([id, colour]) => <button key={id} className="color-roster__item" onClick={() => { onSelectColor(id as ColourId); onNavigate('digital-twin') }} aria-label={`Inspect ${colour.name} label in the digital twin`}><span className="color-roster__swatch" style={{ background: colour.hex }} /><span><span className="color-roster__name">{colour.name}</span><span className="color-roster__id">{id} · {colour.action.replace('_', ' ')}</span></span><ArrowUpRight size={13} className="muted" /></button>)}</div>

    <div className="grid grid--main" style={{ marginTop: 14 }}>
      <Panel>
        <PanelHeading title="Red warning response" note="Backend-computed ΔE00 and simulated missed-trigger rate by configured illuminant." action={<Badge tone="danger">R · DONATE NOW</Badge>} />
        {redRows.length ? <div className="chart-wrap chart-wrap--short"><ResponsiveContainer width="100%" height="100%"><AreaChart data={redRows.map((row) => ({ illuminant: String(row.illumination_id), deltaE: numeric(row.delta_e00), miss: numeric(row.simulated_missed_donation_rate) * 100 }))} margin={{ top: 10, right: 12, left: -19, bottom: 0 }}>
          <defs><linearGradient id="missFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#e86a70" stopOpacity={0.2} /><stop offset="95%" stopColor="#e86a70" stopOpacity={0} /></linearGradient></defs><CartesianGrid stroke="rgba(153,176,212,.08)" vertical={false} /><XAxis dataKey="illuminant" tick={{ fill: '#7f8da0', fontSize: 9, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} /><YAxis yAxisId="left" tick={{ fill: '#7f8da0', fontSize: 9, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} /><YAxis yAxisId="right" orientation="right" unit="%" tick={{ fill: '#7f8da0', fontSize: 9, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} /><Tooltip content={<ChartTooltip />} /><Area yAxisId="left" type="monotone" dataKey="deltaE" name="ΔE00" stroke="#89cfe0" strokeWidth={2} fill="url(#missFill)" activeDot={{ r: 4 }} /><Area yAxisId="right" type="monotone" dataKey="miss" name="Miss probability (%)" stroke="#e9797d" strokeWidth={1.7} fill="transparent" activeDot={{ r: 4 }} />
        </AreaChart></ResponsiveContainer></div> : <EmptyState title="No trigger analysis yet" message="The graph appears after the full colour pipeline writes its result tables." />}
        <div className="legend-row" style={{ marginTop: 9 }}><span><i style={{ background: '#89cfe0' }} />Red-label ΔE00</span><span><i style={{ background: '#e9797d' }} />Synthetic miss probability</span></div>
        <div className="research-warning">The observer curve is a declared computational assumption. It is not calibrated to participants or measured retail recognition.</div>
      </Panel>
      <Panel>
        <PanelHeading title="Recent computation" note="Persisted backend jobs and simulation records." action={<Badge tone="cyan" dot>SQLITE</Badge>} />
        {recent.length ? <div className="activity-list">{recent.map((job) => <div className="activity-item" key={`${job.type}-${job.id}`}><span className="activity-icon">{job.type === 'render' ? <Boxes size={14} /> : job.type === 'donation_simulation' ? <Leaf size={14} /> : <FlaskConical size={14} />}</span><span><strong>{job.type?.replaceAll('_', ' ') ?? 'computation'}</strong><small>{job.id.slice(0, 8)} · {job.status}</small></span><span className="activity-time">{job.created_at ? new Date(job.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—'}</span></div>)}</div> : <EmptyState title="No recent computations" message="Start a render, comparison, or simulation to populate activity." />}
        <div className="divider" />
        <div className="result-detail-grid"><div className="result-detail"><span>Latest full analysis</span><strong>{dashboard.generated_at ? new Date(dashboard.generated_at).toLocaleDateString() : 'Not run'}</strong></div><div className="result-detail"><span>Donation capacity</span><strong>{capacity} units / day</strong></div><div className="result-detail"><span>Measurement rows</span><strong>{dashboard.colour_measurement_count} / 12</strong></div><div className="result-detail"><span>Completed Blender jobs</span><strong>{dashboard.render_job_count}</strong></div></div>
      </Panel>
    </div>
    <div className="notice" style={{ marginTop: 14 }}><ShieldCheck size={15} /><span><strong>Evidence boundary.</strong> Blender renders are visual RGB scenes; spectral computations use the Python CIE pipeline. Donation and sustainability values are seeded model results with explicit synthetic assumptions.</span></div>
  </>
}

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return <div className="chart-tooltip"><div className="chart-tooltip__label">{label}</div>{payload.map((item: any) => <div key={item.dataKey} style={{ color: item.color, marginTop: 3 }}>{item.name}: {Number(item.value).toFixed(2)}{item.dataKey === 'miss' ? '%' : ''}</div>)}</div>
}
