import { useEffect, useMemo, useState } from 'react'
import { AlertTriangle, ChevronDown, ChevronLeft, ChevronRight, CircleHelp, Cpu, FlaskConical, LoaderCircle, RotateCcw, Sparkles } from 'lucide-react'
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Badge, Button, DataTable, EmptyState, ErrorState, Field, PageHeading, Panel, PanelHeading, SectionTitle, SelectField } from '../components/ui'
import { api, ApiError } from '../lib/api'
import type { DonationSimulation, IlluminationId, Page, ProjectConfiguration } from '../lib/types'
import { numeric } from '../lib/csv'
import { SceneRender } from '../components/SceneRender'

const actionColors: Record<string, string> = { fresh: '#2E9E4F', watch: '#F5B700', discount: '#F07C1E', donate: '#D62828' }
const actionNames: Record<string, string> = { fresh: 'Fresh', watch: 'Watch', discount: 'Discount', donate: 'Donate now' }
const illuminants: IlluminationId[] = ['L1', 'L2', 'L3']
const configuredObserver = (config: ProjectConfiguration) => ({
  base_error_probability: config.observer.base_error_probability,
  maximum_additional_error_probability: config.observer.maximum_additional_error_probability,
  delta_e_midpoint: config.observer.delta_e_midpoint,
  delta_e_scale: config.observer.delta_e_scale,
  confusion_weights: { adjacent: config.observer.confusion_weights.adjacent, nonadjacent: config.observer.confusion_weights.nonadjacent },
})

export default function DonationPage({ config }: { config: ProjectConfiguration }) {
  const [illumination, setIllumination] = useState<IlluminationId>('L1')
  const [recognition, setRecognition] = useState<'simulated_errors' | 'perfect'>('simulated_errors')
  const [capacity, setCapacity] = useState(25)
  const [days, setDays] = useState(30)
  const [arrivals, setArrivals] = useState(80)
  const [replicates, setReplicates] = useState(100)
  const [seed, setSeed] = useState(config.project.random_seed)
  const [observer, setObserver] = useState(() => configuredObserver(config))
  const [advancedOpen, setAdvancedOpen] = useState(false)
  const [result, setResult] = useState<DonationSimulation | null>(null)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')
  const [history, setHistory] = useState<Page<DonationSimulation> | null>(null)
  const [page, setPage] = useState(0)
  const [historyFilter, setHistoryFilter] = useState<'all' | 'simulated_errors' | 'perfect'>('all')

  useEffect(() => { void loadHistory(0, historyFilter) }, [])
  async function loadHistory(offset: number, filter: string) {
    try {
      const query = new URLSearchParams({ limit: '6', offset: String(offset) })
      if (filter !== 'all') query.set('recognition', filter)
      const value = await api.get<Page<DonationSimulation>>(`/donation-simulations?${query}`)
      setHistory(value); setPage(offset)
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Simulation history could not be loaded.') }
  }

  const simulatedArrivalBudget = days * replicates * arrivals
  const budgetInvalid = days * replicates > 100_000 || simulatedArrivalBudget > 20_000_000
  const inputInvalid = ![capacity, days, arrivals, replicates, seed].every(Number.isFinite) || capacity < 0 || capacity > 100_000 || days < 1 || days > 3650 || arrivals < 0 || arrivals > 100_000 || replicates < 1 || replicates > 2000 || seed < 0
  const observerInvalid = observer.base_error_probability + observer.maximum_additional_error_probability > 1 || observer.delta_e_scale <= 0 || observer.confusion_weights.adjacent <= 0 || observer.confusion_weights.nonadjacent <= 0

  async function runSimulation(event: { preventDefault: () => void }) {
    event.preventDefault(); setError('')
    if (budgetInvalid || inputInvalid || observerInvalid) { setError('Correct the validation message before starting this bounded Monte Carlo request.'); return }
    setRunning(true)
    try {
      const response = await api.post<DonationSimulation>('/donation-simulations', {
        illumination_id: illumination, recognition, capacity_per_day: capacity, days, mean_arrivals_per_day: arrivals, replicates, seed,
        observer_parameters: observer,
      })
      setResult(response)
      await loadHistory(0, historyFilter)
    } catch (reason) { setError(reason instanceof ApiError ? reason.message : 'Donation simulation request failed.') }
    finally { setRunning(false) }
  }

  function updateObserver(key: 'base_error_probability' | 'maximum_additional_error_probability' | 'delta_e_midpoint' | 'delta_e_scale', value: number) { setObserver((current) => ({ ...current, [key]: value })) }

  const data = result?.result
  const means = data?.mean ?? {}
  const intervals = data?.ci95_percentile ?? {}
  const matrix = data?.confusion_matrix
  const matrixActions: string[] = matrix?.actions ?? ['fresh', 'watch', 'discount', 'donate']
  const outcomes = useMemo(() => data ? [
    { label: 'Correctly donated', value: numeric(means.true_donated_units), color: '#69c997' },
    { label: 'All donated', value: numeric(means.donated_units), color: '#8ab6de' },
    { label: 'Discount recovered', value: numeric(means.discount_recovered_units), color: '#e3b45c' },
    { label: 'Expired stock', value: numeric(means.expired_stock), color: '#d87579' },
    { label: 'Missed donate triggers', value: numeric(means.missed_donation_triggers), color: '#ee8a7d' },
    { label: 'Capacity overflow', value: numeric(means.capacity_overflow_units), color: '#9e8fe5' },
  ] : [], [data, means])

  return <>
    <PageHeading kicker="Model 04 / Observer and inventory" title="Donation simulator" description="Connect the configured ΔE00 sensitivity assumption to a seeded near-expiry inventory scenario. Every submitted run is validated and persisted by FastAPI." action={<span className="simulation-badge"><Sparkles size={12} /> MONTE CARLO · SIMULATED</span>} />
    <SceneRender id="02_shelf_detail" className="research-scene-banner" title="Retail context · near-expiry shelf labels" note="Visual scene only. Simulated recognition and inventory outcomes come from the backend." />
    <div className="simulation-grid">
      <Panel>
        <PanelHeading title="Scenario design" note="Parameters passed to POST /api/v1/donation-simulations." action={<Badge tone="cyan">SEEDED RUN</Badge>} />
        <form className="form-stack" onSubmit={(event) => void runSimulation(event)}>
          <div className="field-grid"><SelectField label="Illumination" value={illumination} onChange={(value) => setIllumination(value as IlluminationId)} options={illuminants.map((id) => ({ value: id, label: `${id} · ${config.illuminations[id].name}` }))} /><SelectField label="Recognition model" value={recognition} onChange={(value) => setRecognition(value as typeof recognition)} options={[{ value: 'simulated_errors', label: 'Synthetic observer errors' }, { value: 'perfect', label: 'Perfect recognition baseline' }]} /><Field label="Donation capacity / day"><input type="number" min={0} max={100000} step={5} value={capacity} onChange={(event) => setCapacity(Number(event.target.value))} /></Field></div>
          <div className="field-grid field-grid--4"><Field label="Horizon · days"><input type="number" min={1} max={3650} value={days} onChange={(event) => setDays(Number(event.target.value))} /></Field><Field label="Arrivals / day"><input type="number" min={0} max={100000} step={1} value={arrivals} onChange={(event) => setArrivals(Number(event.target.value))} /></Field><Field label="Replicates"><input type="number" min={1} max={2000} value={replicates} onChange={(event) => setReplicates(Number(event.target.value))} /></Field><Field label="Random seed"><input type="number" min={0} max={2147483647} value={seed} onChange={(event) => setSeed(Number(event.target.value))} /></Field></div>
          {(budgetInvalid || inputInvalid) && <div className="notice notice--warning"><AlertTriangle size={14} /><span>Request budget exceeded. Keep days × replicates ≤ 100,000 and expected arrivals ≤ 20,000,000; field ranges are enforced by the backend as well.</span></div>}
          <div className="divider" />
          <button type="button" className="advanced-toggle" aria-expanded={advancedOpen} onClick={() => setAdvancedOpen((current) => !current)}><span className="form-section-heading" style={{ margin: 0 }}><Cpu size={14} /> Observer sensitivity assumptions</span><ChevronDown size={14} /></button>
          {advancedOpen && <div className="form-stack advanced-panel">
            <div className="notice"><CircleHelp size={14} /><span>Monotone ΔE00-to-error curve; parameters remain uncalibrated to human participants. Values are stored with each output.</span></div>
            <div className="field-grid field-grid--4"><Field label="Base error probability"><input type="number" min={0} max={1} step={0.01} value={observer.base_error_probability} onChange={(event) => updateObserver('base_error_probability', Number(event.target.value))} /></Field><Field label="Maximum added error"><input type="number" min={0} max={1} step={0.01} value={observer.maximum_additional_error_probability} onChange={(event) => updateObserver('maximum_additional_error_probability', Number(event.target.value))} /></Field><Field label="ΔE midpoint"><input type="number" min={0} max={100} step={0.5} value={observer.delta_e_midpoint} onChange={(event) => updateObserver('delta_e_midpoint', Number(event.target.value))} /></Field><Field label="ΔE scale"><input type="number" min={0.01} max={100} step={0.25} value={observer.delta_e_scale} onChange={(event) => updateObserver('delta_e_scale', Number(event.target.value))} /></Field></div>
            <div className="field-grid"><Field label="Adjacent-action confusion weight"><input type="number" min={0.001} max={1} step={0.05} value={observer.confusion_weights.adjacent} onChange={(event) => setObserver((current) => ({ ...current, confusion_weights: { ...current.confusion_weights, adjacent: Number(event.target.value) } }))} /></Field><Field label="Non-adjacent-action confusion weight"><input type="number" min={0.001} max={1} step={0.05} value={observer.confusion_weights.nonadjacent} onChange={(event) => setObserver((current) => ({ ...current, confusion_weights: { ...current.confusion_weights, nonadjacent: Number(event.target.value) } }))} /></Field></div>
            {observerInvalid && <div className="form-note" role="alert">Base plus maximum error must not exceed 1. Scale and confusion weights must be positive.</div>}
          </div>}
          {error && <ErrorState title="Simulation request failed" message={error} />}
          <div className="form-actions"><Button type="submit" loading={running} icon={<FlaskConical size={15} />}>{running ? 'Simulation running…' : 'Run seeded simulation'}</Button><Button type="button" variant="quiet" icon={<RotateCcw size={14} />} onClick={() => { setCapacity(25); setDays(30); setArrivals(80); setReplicates(100); setSeed(config.project.random_seed); setRecognition('simulated_errors'); setObserver(configuredObserver(config)) }}>Reset values</Button></div>
          <div className="form-note">Expected computational workload: {Math.round(simulatedArrivalBudget).toLocaleString()} modeled arrivals across {replicates.toLocaleString()} replicates. Execution duration depends on the configured scenario.</div>
        </form>
      </Panel>

      <div className="simulation-results">
        {!result && <Panel><PanelHeading title="Simulation output" note="Results appear only after the backend completes a submitted run." action={<Badge tone="neutral">NO LOCAL ESTIMATE</Badge>} /><EmptyState title="Configure and run a scenario" message="Recognition outcomes, confidence intervals, and sustainability factors will be returned by the API for this exact request." /></Panel>}
        {data && <>
          <Panel>
            <PanelHeading title="Persisted result" note={`ID ${result.id} · ${data.replicates} replicates · seed ${data.seed} · ${data.recognition} mode`} action={<Badge tone="success" dot>API RESPONSE</Badge>} />
            <div className="grid grid--4">
              <Metric label="Recognition accuracy" value={`${(numeric(means.recognition_accuracy) * 100).toFixed(1)}%`} note="Modeled arrivals" accent="cyan" />
              <Metric label="Miss probability · red" value={`${(numeric(matrix?.missed_donation_probability_given_red) * 100).toFixed(1)}%`} note="Conditioned on true red" accent="red" />
              <Metric label="Units saved" value={numeric(means.units_saved).toFixed(0)} note={`95% CI ${formatInterval(intervals.units_saved)}`} accent="green" />
              <Metric label="Waste rate" value={`${(numeric(means.waste_rate) * 100).toFixed(1)}%`} note="Expired stock / arrivals" accent="yellow" />
            </div>
            <div className="divider" />
            <div className="outcome-list">{outcomes.map((item) => <div className="outcome-row" key={item.label}><span>{item.label}</span><span className="outcome-row__bar"><i style={{ width: `${Math.max(item.value > 0 ? 2 : 0, (item.value / Math.max(...outcomes.map((row) => row.value), 1)) * 100)}%`, background: item.color }} /></span><span className="outcome-row__value">{item.value.toFixed(1)}</span></div>)}</div>
          </Panel>
          <Panel><PanelHeading title="Confusion matrix" note="Rows show configured action; columns show modeled perceived action." action={<Badge tone={data.confusion_matrix.applied_to_inventory ? 'warning' : 'neutral'}>{data.confusion_matrix.applied_to_inventory ? 'APPLIED TO INVENTORY' : 'DIAGNOSTIC ONLY'}</Badge>} />
            <div className="matrix-grid"><div /><div className="matrix-grid__head">Fresh</div><div className="matrix-grid__head">Watch</div><div className="matrix-grid__head">Discount</div><div className="matrix-grid__head">Donate</div>{matrixActions.map((actual) => <MatrixRow key={actual} action={actual} values={matrix.probabilities_by_true_action[actual]} actions={matrixActions} />)}</div>
            <div className="form-note" style={{ marginTop: 10 }}>{data.recognition === 'perfect' ? 'Perfect-recognition mode bypasses this observer matrix for inventory outcomes.' : 'Synthetic observer matrix was applied to the inventory simulation; it is not empirically calibrated.'}</div>
          </Panel>
          <Panel><PanelHeading title="Outcome profile" note="Monte Carlo means returned for the selected request." action={<Badge tone="violet">{data.days} DAYS · {data.capacity_per_day}/DAY</Badge>} />
            <div className="chart-wrap chart-wrap--short"><ResponsiveContainer width="100%" height="100%"><BarChart data={outcomes} layout="vertical" margin={{ top: 3, right: 12, left: 12, bottom: 0 }}><CartesianGrid stroke="rgba(153,176,212,.08)" horizontal={false} /><XAxis type="number" tick={{ fill: '#7f8da0', fontSize: 8 }} axisLine={false} tickLine={false} /><YAxis type="category" dataKey="label" width={118} tick={{ fill: '#9aa8b9', fontSize: 8 }} axisLine={false} tickLine={false} /><Tooltip content={<ChartTooltip />} /><Bar dataKey="value" name="Mean units" radius={[0, 4, 4, 0]}>{outcomes.map((item) => <Cell key={item.label} fill={item.color} />)}</Bar></BarChart></ResponsiveContainer></div>
          </Panel>
          <Panel><PanelHeading title="Sustainability scenarios" note={data.sustainability_scenarios_source_note} action={<Badge tone="green">ILLUSTRATIVE FACTORS</Badge>} />{Object.entries(data.sustainability_scenarios).map(([name, scenario]: [string, any]) => <div className="scenario-row" key={name}><strong>{name.replace('_', ' ')}</strong><small>{scenario.emissions_factor_kgco2e_per_kg} kg CO₂e / kg</small><span className="scenario-row__value">{numeric(scenario.mean_avoided_emissions_kgco2e).toFixed(0)} kg CO₂e</span></div>)}<div className="form-note" style={{ marginTop: 8 }}>Calculated from simulated units saved × configured product mass × scenario emissions factor. Not measured reductions.</div></Panel>
          <Panel><PanelHeading title="Stored model assumptions" note="Exact parameters and config digest submitted with this result." action={<Badge tone="cyan">PROVENANCE</Badge>} /><details className="provenance-details"><summary>Show request-specific observer parameters</summary><pre>{JSON.stringify({ ...data.observer_parameters, configuration_sha256: data.configuration_sha256 }, null, 2)}</pre></details></Panel>
        </>}
      </div>
    </div>

    <SectionTitle eyebrow="Persisted API history" title="Previous donation simulations" trailing={<Badge tone="neutral">{history?.total ?? 0} RECORDS</Badge>} />
    <Panel>
      <div className="panel-heading"><div><h2>Simulation history</h2><p>Filter and page through runs retained in SQLite.</p></div><div className="panel-heading__right"><SelectField label="Recognition filter" value={historyFilter} onChange={(value) => { setHistoryFilter(value as typeof historyFilter); void loadHistory(0, value) }} options={[{ value: 'all', label: 'All models' }, { value: 'simulated_errors', label: 'Synthetic errors' }, { value: 'perfect', label: 'Perfect baseline' }]} /></div></div>
      {history ? <DataTable rowKey="id" rows={history.items} columns={[{ key: 'id', label: 'Simulation ID', render: (item) => <span className="mono">{String(item.id).slice(0, 11)}…</span> }, { key: 'illumination_id', label: 'Illuminant' }, { key: 'recognition', label: 'Recognition' }, { key: 'capacity_per_day', label: 'Capacity/day' }, { key: 'created_at', label: 'Created', render: (item) => item.created_at ? new Date(item.created_at).toLocaleString() : '—' }, { key: 'mean_saved', label: 'Mean units saved', render: (item) => numeric(item.result?.mean?.units_saved).toFixed(1) }]} /> : <div className="loading-state"><LoaderCircle className="spin" size={16} />Loading simulation history…</div>}
      <div className="pagination"><span>Showing {history?.items.length ?? 0} · {history?.total ?? 0} total · offset {page}</span><span className="pagination__controls"><button aria-label="Previous page" disabled={page === 0} onClick={() => void loadHistory(Math.max(0, page - 6), historyFilter)}><ChevronLeft size={14} /></button><button aria-label="Next page" disabled={!history || page + history.items.length >= history.total} onClick={() => void loadHistory(page + 6, historyFilter)}><ChevronRight size={14} /></button></span></div>
    </Panel>
  </>
}

function Metric({ label, value, note, accent }: { label: string; value: string; note: string; accent: string }) { return <div className={`metric-card metric-card--${accent}`}><div className="metric-card__top">{label}</div><strong>{value}</strong><small>{note}</small></div> }
function MatrixRow({ action, values, actions }: { action: string; values: Record<string, number>; actions: string[] }) { return <><div className="matrix-grid__row"><i style={{ background: actionColors[action] }} />{actionNames[action]}</div>{actions.map((predicted) => { const value = numeric(values[predicted]); const emphasis = Math.round(value * 100); return <div key={predicted} className="matrix-grid__cell" title={`${actionNames[action]} → ${actionNames[predicted]}: ${(value * 100).toFixed(2)}%`} style={{ background: `rgba(${predicted === action ? '87,197,141' : '237,100,104'}, ${Math.max(0.045, value * 0.3)})` }}>{emphasis}%</div> })}</> }
function formatInterval(value: unknown) { return Array.isArray(value) ? `${numeric(value[0]).toFixed(0)}–${numeric(value[1]).toFixed(0)}` : '—' }
function ChartTooltip({ active, payload, label }: any) { if (!active || !payload?.length) return null; return <div className="chart-tooltip"><div className="chart-tooltip__label">{label}</div>{payload.map((item: any) => <div key={item.dataKey} style={{ color: item.color, marginTop: 3 }}>{item.name}: {Number(item.value).toFixed(1)}</div>)}</div> }
