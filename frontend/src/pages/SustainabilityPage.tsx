import { useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { ArrowRight, Cloud, Leaf, LoaderCircle, Recycle, Target } from 'lucide-react'
import { Area, AreaChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Badge, Button, DataTable, EmptyState, ErrorState, PageHeading, Panel, PanelHeading, SectionTitle, SelectField } from '../components/ui'
import type { SectionId } from '../components/Layout'
import { api, ApiError } from '../lib/api'
import { loadCsv, numeric } from '../lib/csv'
import type { DonationSimulation, IlluminationId, ProjectConfiguration } from '../lib/types'
import { SceneRender } from '../components/SceneRender'

const lightIds: IlluminationId[] = ['L1', 'L2', 'L3']
const modes = ['perfect', 'simulated_errors'] as const
const scenarioColor: Record<string, string> = { low_impact: '#80c6e2', central: '#a494f1', high_impact: '#e4a35f' }

export default function SustainabilityPage({ config, onNavigate }: { config: ProjectConfiguration; onNavigate: (page: SectionId) => void }) {
  const [latest, setLatest] = useState<DonationSimulation | null>(null)
  const [savedRows, setSavedRows] = useState<Record<string, unknown>[]>([])
  const [illumination, setIllumination] = useState<IlluminationId>('L1')
  const [recognition, setRecognition] = useState<typeof modes[number]>('simulated_errors')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  useEffect(() => {
    let alive = true
    Promise.all([api.get<{ items: DonationSimulation[] }>('/donation-simulations?limit=1&offset=0'), loadCsv<Record<string, unknown>>('sustainability_analysis.csv')]).then(([simulations, rows]) => {
      if (!alive) return
      setLatest(simulations.items[0] ?? null); setSavedRows(rows)
    }).catch((reason: unknown) => alive && setError(reason instanceof ApiError ? reason.message : 'Sustainability evidence could not be loaded.')).finally(() => alive && setLoading(false))
    return () => { alive = false }
  }, [])

  const saved = savedRows.filter((row) => row.illumination_id === illumination && row.recognition === recognition)
  const capacityRows = useMemo(() => {
    const byCapacity = new Map<number, Record<string, unknown>>()
    for (const row of saved) {
      const capacity = numeric(row.capacity_per_day)
      if (!byCapacity.has(capacity)) byCapacity.set(capacity, { capacity })
      byCapacity.get(capacity)![String(row.scenario)] = numeric(row.modeled_avoided_emissions_kgco2e)
    }
    return [...byCapacity.values()].sort((a, b) => numeric(a.capacity) - numeric(b.capacity))
  }, [saved])
  const latestResult = latest?.result
  const latestScenarioRows = latestResult ? Object.entries(latestResult.sustainability_scenarios ?? {}).map(([scenario, values]: [string, any]) => ({ scenario: scenario.replace('_', ' '), emissions_factor: values.emissions_factor_kgco2e_per_kg, mean_co2e: values.mean_avoided_emissions_kgco2e, ci_low: values.ci95_percentile_kgco2e?.[0], ci_high: values.ci95_percentile_kgco2e?.[1] })) : []
  const unitsSaved = numeric(latestResult?.mean?.units_saved)
  const central = latestResult?.sustainability_scenarios?.central
  const centralImpact = numeric(central?.mean_avoided_emissions_kgco2e)

  return <>
    <PageHeading kicker="Model 05 / Environmental sensitivity" title="Sustainability" description="Translate seeded near-expiry model outcomes into transparent food-mass and emissions-factor scenarios. All impact values are computational scenarios, not measured reductions." action={<Badge tone="green"><Leaf size={12} /> MODELLED IMPACT</Badge>} />
    <SceneRender id="06_supermarket_isometric" className="research-scene-banner" title="Retail system boundary · modelled store layout" note="A computational setting for donation scenarios; no live-store observations or measured waste data." />
    {error && <ErrorState title="Sustainability evidence is unavailable" message={error} onRetry={() => window.location.reload()} />}
    <div className="grid grid--4">
      <ImpactMetric label="Mean units saved" value={latest ? unitsSaved.toFixed(0) : '—'} note={latest ? `${latest.recognition} · ${latest.capacity_per_day} units/day` : 'Run a donation scenario'} accent="green" icon={<Recycle size={15} />} />
      <ImpactMetric label="Food mass saved" value={latest ? `${numeric(latestResult?.mean_food_mass_saved_kg).toFixed(0)} kg` : '—'} note={latest ? `${config.donation.average_product_kg} kg average mass assumption` : 'Run a donation scenario'} accent="cyan" icon={<Leaf size={15} />} />
      <ImpactMetric label="Central CO₂e scenario" value={latest ? `${(centralImpact / 1000).toFixed(2)} t` : '—'} note={latest ? `${numeric(central?.emissions_factor_kgco2e_per_kg).toFixed(1)} kg CO₂e/kg factor` : 'No persisted simulation yet'} accent="violet" icon={<Cloud size={15} />} />
      <ImpactMetric label="Simulation horizon" value={latest ? `${latestResult?.days ?? '—'} d` : '—'} note={latest ? `${latestResult?.replicates} Monte Carlo replicates` : 'No persisted simulation yet'} accent="yellow" icon={<Target size={15} />} />
    </div>

    {!latest && !loading && <Panel style={{ marginTop: 14 }}><PanelHeading title="No saved donation simulation" note="Sustainability estimates require a saved API simulation result." /><EmptyState title="Create a model run first" message="The dashboard does not substitute placeholder values for missing model outputs." /><Button onClick={() => onNavigate('donation')} icon={<ArrowRight size={14} />}>Configure donation scenario</Button></Panel>}
    {loading && <div className="loading-state"><LoaderCircle className="spin" size={17} />Reading saved scenarios…</div>}

    <SectionTitle eyebrow="Configured assumptions" title="Low, central and high impact factors" trailing={<span className="tagline">Per kg food mass · illustrative factors</span>} />
    <div className="grid grid--main">
      <Panel>
        <PanelHeading title="Sensitivity from latest simulation" note={latest ? `FastAPI simulation ${latest.id.slice(0, 8)} · ${latestResult?.replicates} replicates · seed ${latestResult?.seed}` : 'Live simulation factors appear here after a saved run.'} action={<Badge tone="violet">CO₂e / KG</Badge>} />
        {latestScenarioRows.length ? <div className="chart-wrap chart-wrap--short"><ResponsiveContainer width="100%" height="100%"><AreaChart data={latestScenarioRows} margin={{ top: 12, right: 12, left: 4, bottom: 0 }}><defs><linearGradient id="impactFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#a494f1" stopOpacity={0.19} /><stop offset="100%" stopColor="#a494f1" stopOpacity={0.015} /></linearGradient></defs><CartesianGrid stroke="rgba(153,176,212,.08)" vertical={false} /><XAxis dataKey="scenario" tick={{ fill: '#8997a9', fontSize: 9 }} axisLine={false} tickLine={false} /><YAxis domain={[0, 'auto']} tick={{ fill: '#79879b', fontSize: 9 }} axisLine={false} tickLine={false} /><Tooltip content={<ChartTooltip />} /><Area type="monotone" dataKey="mean_co2e" name="Modeled avoided CO₂e (kg)" stroke="#ab9af4" strokeWidth={2} fill="url(#impactFill)" activeDot={{ r: 4 }} /></AreaChart></ResponsiveContainer></div> : <EmptyState title="No scenario outcomes" message="Create a persisted donation simulation to see the emission-factor sensitivity." />}
        <div className="scenario-row"><strong>Low impact</strong><small>{config.sustainability.emissions_factor_scenarios_kgco2e_per_kg.low_impact} kg CO₂e / kg</small><span className="scenario-row__value">{latestScenarioRows[0] ? `${numeric(latestScenarioRows[0].mean_co2e).toFixed(0)} kg` : '—'}</span></div>
        <div className="scenario-row"><strong>Central</strong><small>{config.sustainability.emissions_factor_scenarios_kgco2e_per_kg.central} kg CO₂e / kg</small><span className="scenario-row__value">{latestScenarioRows[1] ? `${numeric(latestScenarioRows[1].mean_co2e).toFixed(0)} kg` : '—'}</span></div>
        <div className="scenario-row"><strong>High impact</strong><small>{config.sustainability.emissions_factor_scenarios_kgco2e_per_kg.high_impact} kg CO₂e / kg</small><span className="scenario-row__value">{latestScenarioRows[2] ? `${numeric(latestScenarioRows[2].mean_co2e).toFixed(0)} kg` : '—'}</span></div>
      </Panel>
      <Panel>
        <PanelHeading title="Scenario provenance" note="The API returns these values in each stored simulation result." action={<Badge tone="cyan">AUDITABLE</Badge>} />
        <div className="form-stack"><div className="result-detail"><span>Emissions-factor basis</span><strong>{config.sustainability.factor_source_note}</strong></div><div className="result-detail"><span>Model equation</span><strong>units saved × average product mass × scenario factor</strong></div><div className="result-detail"><span>Data source</span><strong>{latest ? `Simulation ${latest.id}` : 'No latest simulation'}</strong></div><div className="notice notice--warning"><Target size={14} /><span><strong>Interpretation.</strong> These factors are illustrative sensitivity assumptions, not product-specific life-cycle data, measured food waste, or avoided emissions.</span></div><Button variant="secondary" onClick={() => onNavigate('donation')} icon={<ArrowRight size={14} />}>Configure another simulation</Button></div>
      </Panel>
    </div>

    <SectionTitle eyebrow="Saved pipeline outputs" title="Capacity sensitivity" trailing={<span className="tagline">Generated by the Python evidence pipeline</span>} />
    <Panel>
      <div className="grid grid--main" style={{ alignItems: 'end', marginBottom: 15 }}><PanelHeading title="Modeled CO₂e by donation capacity" note={`${config.illuminations[illumination].name} · ${recognition.replace('_', ' ')} · three configured factors`} /><div className="field-grid"><SelectField label="Illumination" value={illumination} onChange={(value) => setIllumination(value as IlluminationId)} options={lightIds.map((id) => ({ value: id, label: `${id} · ${config.illuminations[id].name}` }))} /><SelectField label="Recognition model" value={recognition} onChange={(value) => setRecognition(value as typeof recognition)} options={[{ value: 'simulated_errors', label: 'Synthetic observer errors' }, { value: 'perfect', label: 'Perfect-recognition baseline' }]} /></div></div>
      {capacityRows.length ? <><div className="chart-wrap chart-wrap--tall"><ResponsiveContainer width="100%" height="100%"><AreaChart data={capacityRows} margin={{ top: 12, right: 18, left: 2, bottom: 0 }}><defs><linearGradient id="lowArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={scenarioColor.low_impact} stopOpacity={.12} /><stop offset="100%" stopColor={scenarioColor.low_impact} stopOpacity={0} /></linearGradient><linearGradient id="centralArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={scenarioColor.central} stopOpacity={.12} /><stop offset="100%" stopColor={scenarioColor.central} stopOpacity={0} /></linearGradient><linearGradient id="highArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={scenarioColor.high_impact} stopOpacity={.12} /><stop offset="100%" stopColor={scenarioColor.high_impact} stopOpacity={0} /></linearGradient></defs><CartesianGrid stroke="rgba(153,176,212,.08)" vertical={false} /><XAxis dataKey="capacity" tick={{ fill: '#8997a9', fontSize: 9 }} axisLine={false} tickLine={false} label={{ value: 'Donation capacity (units / day)', position: 'insideBottom', offset: -4, fill: '#748399', fontSize: 9 }} /><YAxis tick={{ fill: '#79879b', fontSize: 9 }} axisLine={false} tickLine={false} label={{ value: 'Modeled CO₂e avoided (kg)', angle: -90, position: 'insideLeft', fill: '#748399', fontSize: 9 }} /><Legend verticalAlign="top" align="right" height={28} wrapperStyle={{ color: '#8d9bae', fontSize: 9 }} /><Tooltip content={<ChartTooltip />} /><Area type="monotone" dataKey="low_impact" name="Low impact factor" stroke={scenarioColor.low_impact} strokeWidth={1.7} fill="url(#lowArea)" /><Area type="monotone" dataKey="central" name="Central factor" stroke={scenarioColor.central} strokeWidth={2} fill="url(#centralArea)" /><Area type="monotone" dataKey="high_impact" name="High impact factor" stroke={scenarioColor.high_impact} strokeWidth={1.7} fill="url(#highArea)" /></AreaChart></ResponsiveContainer></div>
        <div className="form-note">The vertical scale starts at zero. Curves reflect the existing fixed-seed sensitivity analysis CSV; changing filters reads the matching saved rows.</div></> : <EmptyState title="No matching capacity rows" message="Run the full analysis pipeline to generate the 500-replicate capacity sensitivity outputs." />}
    </Panel>

    <SectionTitle eyebrow="Research alignment" title="SDG outcome mapping" />
    <div className="grid grid--2"><GoalCard code="SDG 12.3" title="Food waste outcomes" text="Tracks simulated units saved, modeled food mass saved, expired stock, and donation capacity. The mapping is limited to computational inventory scenarios." /><GoalCard code="SDG 13" title="Climate sensitivity" text="Reports illustrative avoided-emissions sensitivity from simulated units saved and configured CO₂e factors. It is not an emissions inventory or verified climate contribution." /></div>

    <SectionTitle eyebrow="Source table" title="Saved sustainability outputs" />
    <Panel><PanelHeading title={`${saved.length} rows for the selected model`} note="Source: results/sustainability_analysis.csv served by the backend artifact route." action={<a className="button button--quiet" href={api.artifactUrl('sustainability_analysis.csv')} download="sustainability_analysis.csv">Download CSV</a>} />{loading ? <div className="loading-state"><LoaderCircle className="spin" size={16} />Loading source table…</div> : <DataTable rowKey="scenario" rows={saved.slice(0, 30)} columns={[{ key: 'illumination_id', label: 'Illumination' }, { key: 'recognition', label: 'Recognition' }, { key: 'capacity_per_day', label: 'Capacity/day' }, { key: 'scenario', label: 'Scenario' }, { key: 'mean_units_saved', label: 'Units saved', render: (row) => numeric(row.mean_units_saved).toFixed(1) }, { key: 'mean_food_mass_saved_kg', label: 'Food mass (kg)', render: (row) => numeric(row.mean_food_mass_saved_kg).toFixed(1) }, { key: 'emissions_factor_kgco2e_per_kg', label: 'Factor kg CO₂e/kg' }, { key: 'modeled_avoided_emissions_kgco2e', label: 'Modeled CO₂e (kg)', render: (row) => numeric(row.modeled_avoided_emissions_kgco2e).toFixed(1) }, { key: 'ci95_low_kgco2e', label: '95% CI low', render: (row) => numeric(row.ci95_low_kgco2e).toFixed(1) }, { key: 'ci95_high_kgco2e', label: '95% CI high', render: (row) => numeric(row.ci95_high_kgco2e).toFixed(1) }]} />}</Panel>
  </>
}

function ImpactMetric({ label, value, note, accent, icon }: { label: string; value: string; note: string; accent: string; icon: ReactNode }) { return <div className={`metric-card metric-card--${accent}`}><div className="metric-card__top">{label}<span className="metric-card__icon">{icon}</span></div><strong>{value}</strong><small>{note}</small></div> }
function GoalCard({ code, title, text }: { code: string; title: string; text: string }) { return <Panel><div className="form-section-heading"><Target size={14} />{title}<Badge tone="green">{code}</Badge></div><p className="form-note">{text}</p></Panel> }
function ChartTooltip({ active, payload, label }: any) { if (!active || !payload?.length) return null; return <div className="chart-tooltip"><div className="chart-tooltip__label">{label}</div>{payload.map((item: any) => <div key={item.dataKey} style={{ color: item.color, marginTop: 3 }}>{item.name}: {Number(item.value).toFixed(1)} kg CO₂e</div>)}</div> }
