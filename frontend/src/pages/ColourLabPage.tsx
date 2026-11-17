import { useEffect, useMemo, useState } from 'react'
import { Activity, ArrowRight, CircleHelp, FlaskConical, LoaderCircle, ScanLine } from 'lucide-react'
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from 'recharts'
import { Badge, Button, DataTable, EmptyState, ErrorState, PageHeading, Panel, PanelHeading, SelectField, SectionTitle } from '../components/ui'
import type { SectionId } from '../components/Layout'
import { api, ApiError } from '../lib/api'
import { loadCsv, numeric } from '../lib/csv'
import type { ChromaRow, ColourId, Comparison, IlluminationId, Measurement, ProjectConfiguration } from '../lib/types'
import { SceneRender } from '../components/SceneRender'

const colours: ColourId[] = ['G', 'Y', 'O', 'R']
const lights: IlluminationId[] = ['L1', 'L2', 'L3']
const lightLine: Record<IlluminationId, string> = { L1: '#7ed9e9', L2: '#a28ef0', L3: '#eda66f' }

export default function ColourLabPage({ config, dashboard, onNavigate }: { config: ProjectConfiguration; dashboard: { delta_e_summary: Record<string, any>[]; red_trigger_summary: Record<string, any>[] }; onNavigate: (page: SectionId) => void }) {
  const [colourId, setColourId] = useState<ColourId>('R')
  const [illuminationId, setIlluminationId] = useState<IlluminationId>('L1')
  const [measurements, setMeasurements] = useState<Measurement[]>([])
  const [chromaticity, setChromaticity] = useState<ChromaRow[]>([])
  const [comparison, setComparison] = useState<Comparison | null>(null)
  const [loading, setLoading] = useState(true)
  const [computing, setComputing] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let alive = true
    Promise.all([loadCsv<Measurement>('colour_measurements.csv'), loadCsv<ChromaRow>('chromaticity_data.csv')]).then(([measureRows, chromaRows]) => {
      if (!alive) return
      setMeasurements(measureRows); setChromaticity(chromaRows); setError('')
    }).catch((reason: unknown) => alive && setError(reason instanceof Error ? reason.message : 'Colour evidence could not be loaded.')).finally(() => alive && setLoading(false))
    return () => { alive = false }
  }, [])

  const row = measurements.find((item) => item.colour_id === colourId && item.illumination_id === illuminationId)
  const chroma = chromaticity.find((item) => item.colour_id === colourId && item.illumination_id === illuminationId)
  const compareHistory = useMemo(() => comparison?.result ?? null, [comparison])

  async function computeComparison() {
    setComputing(true); setError('')
    try { setComparison(await api.post<Comparison>('/colour-comparisons', { colour_id: colourId, illumination_id: illuminationId })) }
    catch (reason) { setError(reason instanceof ApiError ? reason.message : 'The colour comparison failed.') }
    finally { setComputing(false) }
  }

  const resultFields = compareHistory ? Object.entries(compareHistory).filter(([, value]) => typeof value === 'number' && Number.isFinite(value)) : []
  const xyzFields = row ? Object.entries(row).filter(([key]) => /^(digital|print)_xyz_bradford_to_d65_[XYZ]$/.test(key)) : []

  return <>
    <PageHeading kicker="Instrument 03 / CIE colour science" title="Colour laboratory" description="Inspect the configured digital RGB colour against the synthetic virtual-print response using the backend’s spectral illumination and CIEDE2000 pipeline." action={<Badge tone="cyan">CIE 1931 · 2° OBSERVER</Badge>} />
    <SceneRender id="03_donate_now_macro" className="research-scene-banner" title="Near-expiry warning · physical shelf ticket assembly" note="Generated Blender visual asset; printed-response science remains the synthetic Python model." />
    <Panel>
      <PanelHeading title="Comparison controls" note="Each action calls POST /api/v1/colour-comparisons. Measurements below are loaded from persisted pipeline CSVs." action={<Badge tone="violet">{measurements.length || dashboard.delta_e_summary.length * 3} COMPUTED CONDITIONS</Badge>} />
      <div className="grid grid--main" style={{ alignItems: 'end' }}>
        <div className="field-grid"><SelectField label="Shelf-label colour" value={colourId} onChange={(value) => { setColourId(value as ColourId); setComparison(null) }} options={colours.map((id) => ({ value: id, label: `${id} · ${config.colours[id].name} · ${config.colours[id].hex}` }))} /><SelectField label="Illumination model" value={illuminationId} onChange={(value) => { setIlluminationId(value as IlluminationId); setComparison(null) }} options={lights.map((id) => ({ value: id, label: `${id} · ${config.illuminations[id].name}` }))} /><div className="form-actions"><Button onClick={() => void computeComparison()} loading={computing} icon={<FlaskConical size={15} />}>Compute comparison</Button></div></div>
        <div className="notice"><CircleHelp size={14} /><span><strong>Model boundary.</strong> The print response is synthetic reflectance transfer. L2/L3 are parameterized LED spectra, not measured store lamps. <a className="inline-link" href="/api/v1/configuration" target="_blank">View active configuration <ArrowRight size={12} /></a></span></div>
      </div>
      {error && <div style={{ marginTop: 12 }}><ErrorState title="Colour data request failed" message={error} onRetry={() => window.location.reload()} /></div>}
    </Panel>

    {colourId === 'R' && row && <div className="analysis-focus" style={{ marginTop: 13 }}><div className="analysis-focus__swatch"><span className="analysis-focus__color" style={{ background: config.colours.R.hex }} /><span><strong>Donate-now warning · red focus</strong><small>R · {config.colours.R.hex} · {config.illuminations[illuminationId].name}</small></span></div><div className="analysis-focus__metrics"><div><small>ΔE00</small><strong>{numeric(row.delta_e00).toFixed(3)}</strong></div><div><small>ΔL*</small><strong>{numeric(row.delta_l_star).toFixed(3)}</strong></div><div><small>ΔC*</small><strong>{numeric(row.delta_c_star).toFixed(3)}</strong></div><div><small>ΔH′</small><strong>{numeric(row.delta_h_prime).toFixed(3)}</strong></div></div></div>}

    {compareHistory && <Panel className="live-comparison" style={{ marginTop: 13 }}><PanelHeading title="New API computation persisted" note={`Comparison ${comparison?.id} · returned by FastAPI`} action={<Badge tone="success" dot>COMPUTED</Badge>} /><div className="result-detail-grid">{resultFields.slice(0, 10).map(([key, value]) => <div className="result-detail" key={key}><span>{key.replaceAll('_', ' ')}</span><strong>{numeric(value).toFixed(5)}</strong></div>)}</div></Panel>}

    <SectionTitle eyebrow="Saved evidence · backend generated" title="Difference across illumination" trailing={<Button variant="quiet" icon={<ArrowRight size={14} />} onClick={() => onNavigate('donation')}>Explore trigger sensitivity</Button>} />
    <div className="grid grid--main">
      <Panel>
        <PanelHeading title="ΔE00 by research colour" note="Twelve configured label / illumination comparisons. Axis begins at zero." action={<Badge tone="cyan">CIEDE2000</Badge>} />
        {loading ? <div className="loading-state"><LoaderCircle className="spin" size={17} />Loading colour measurements…</div> : measurements.length ? <div className="chart-wrap chart-wrap--tall"><ResponsiveContainer width="100%" height="100%"><LineChart data={colours.map((id) => {
          const item: Record<string, string | number> = { label: id }
          for (const light of lights) item[light] = numeric(measurements.find((measurement) => measurement.colour_id === id && measurement.illumination_id === light)?.delta_e00)
          return item
        })} margin={{ top: 10, right: 17, left: -10, bottom: 0 }}>
          <CartesianGrid stroke="rgba(153,176,212,.08)" vertical={false} /><XAxis dataKey="label" tickFormatter={(id) => `${id} · ${config.colours[id as ColourId].name}`} tick={{ fill: '#8795a8', fontSize: 9 }} axisLine={false} tickLine={false} /><YAxis domain={[0, 'auto']} tick={{ fill: '#7f8da0', fontSize: 9, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} /><Tooltip content={<ChartTooltip />} /><Line type="monotone" dataKey="L1" name="D65 · L1" stroke={lightLine.L1} strokeWidth={2} dot={{ r: 3, fill: lightLine.L1, strokeWidth: 0 }} activeDot={{ r: 5 }} /><Line type="monotone" dataKey="L2" name="Neutral LED · L2" stroke={lightLine.L2} strokeWidth={1.7} dot={{ r: 3, fill: lightLine.L2, strokeWidth: 0 }} activeDot={{ r: 5 }} /><Line type="monotone" dataKey="L3" name="Warm LED · L3" stroke={lightLine.L3} strokeWidth={1.7} dot={{ r: 3, fill: lightLine.L3, strokeWidth: 0 }} activeDot={{ r: 5 }} />
        </LineChart></ResponsiveContainer></div> : <EmptyState title="Colour measurements are missing" message="Run the full analysis pipeline from Results & exports to generate them." />}
        <div className="legend-row" style={{ marginTop: 10 }}><span><i style={{ background: lightLine.L1 }} />D65</span><span><i style={{ background: lightLine.L2 }} />Neutral LED approximation</span><span><i style={{ background: lightLine.L3 }} />Warm LED approximation</span></div>
      </Panel>
      <Panel>
        <PanelHeading title="Current measurement record" note={`${config.colours[colourId].name} under ${config.illuminations[illuminationId].name}`} action={<span className="color-chip"><i style={{ background: config.colours[colourId].hex }} />{colourId}</span>} />
        {loading ? <div className="loading-state"><LoaderCircle className="spin" size={17} />Loading saved row…</div> : row ? <div className="result-detail-grid">
          <Detail label="Digital CIELAB" value={`L* ${numeric(row.digital_L).toFixed(2)} · a* ${numeric(row.digital_a).toFixed(2)} · b* ${numeric(row.digital_b).toFixed(2)}`} />
          <Detail label="Virtual print CIELAB" value={`L* ${numeric(row.print_L).toFixed(2)} · a* ${numeric(row.print_a).toFixed(2)} · b* ${numeric(row.print_b).toFixed(2)}`} />
          <Detail label="CIEDE2000 difference" value={`ΔE00 ${numeric(row.delta_e00).toFixed(4)}`} />
          <Detail label="Difference components" value={`ΔL* ${numeric(row.delta_l_star).toFixed(3)} · ΔC* ${numeric(row.delta_c_star).toFixed(3)} · ΔH′ ${numeric(row.delta_h_prime).toFixed(3)}`} />
          <Detail label="Digital CIE XYZ · Bradford to D65" value={xyzFields.filter(([key]) => key.startsWith('digital')).map(([key, value]) => `${key.slice(-1)} ${numeric(value).toFixed(4)}`).join(' · ')} />
          <Detail label="Print CIE XYZ · Bradford to D65" value={xyzFields.filter(([key]) => key.startsWith('print')).map(([key, value]) => `${key.slice(-1)} ${numeric(value).toFixed(4)}`).join(' · ')} />
          <Detail label="Chromaticity · digital x,y" value={`(${numeric(row.digital_x).toFixed(4)}, ${numeric(row.digital_y).toFixed(4)})`} />
          <Detail label="Chromaticity · print x,y" value={`(${numeric(row.print_x).toFixed(4)}, ${numeric(row.print_y).toFixed(4)})`} />
          <Detail label="Spectral print model" value={row.print_model} />
          <Detail label="Reference observer" value={row.observer} />
        </div> : <EmptyState title="No row for this condition" message="Saved colour records will appear after the analysis pipeline completes." />}
        {row && <div className="form-actions" style={{ marginTop: 12 }}><a className="button button--secondary" href={api.artifactUrl('colour_measurements.csv')} download="colour_measurements.csv">Download measurements CSV</a></div>}
      </Panel>
    </div>

    <SectionTitle eyebrow="CIE 1931 · 2 degree observer" title="Chromaticity and spectral attributes" />
    <div className="grid grid--main">
      <Panel>
        <PanelHeading title="Measured xy points" note="Digital and virtual-print chromaticity from the saved Python computation." action={<Badge tone="violet">x,y COORDINATES</Badge>} />
        {row && <div className="chromaticity-card" style={{ marginBottom: 12 }}><div className="chroma-stat chroma-stat--digital"><small>Digital colour · xy</small><strong>{numeric(row.digital_x).toFixed(5)}, {numeric(row.digital_y).toFixed(5)}</strong></div><div className="chroma-stat chroma-stat--print"><small>Virtual print · xy</small><strong>{numeric(row.print_x).toFixed(5)}, {numeric(row.print_y).toFixed(5)}</strong></div></div>}
        {row ? <div className="chart-wrap chart-wrap--short"><ResponsiveContainer width="100%" height="100%"><ScatterChart margin={{ top: 10, right: 15, left: 5, bottom: 7 }}><CartesianGrid stroke="rgba(153,176,212,.08)" /><XAxis type="number" dataKey="x" name="x" domain={[0, 0.8]} tick={{ fill: '#7f8da0', fontSize: 9 }} label={{ value: 'CIE x', position: 'insideBottom', fill: '#8493a6', fontSize: 9, offset: -2 }} /><YAxis type="number" dataKey="y" name="y" domain={[0, 0.9]} tick={{ fill: '#7f8da0', fontSize: 9 }} label={{ value: 'CIE y', angle: -90, position: 'insideLeft', fill: '#8493a6', fontSize: 9 }} /><Tooltip cursor={{ strokeDasharray: '3 3' }} content={<ChartTooltip />} /><Scatter name="Digital RGB" data={[{ x: numeric(row.digital_x), y: numeric(row.digital_y) }]} fill="#7ed9e9" shape="circle" /><Scatter name="Virtual print" data={[{ x: numeric(row.print_x), y: numeric(row.print_y) }]} fill="#ad9af1" shape="diamond" /></ScatterChart></ResponsiveContainer></div> : <EmptyState title="Chromaticity row unavailable" message="No saved chromaticity record matches the current selection." />}
        <div className="legend-row" style={{ marginTop: 6 }}><span><i style={{ background: '#7ed9e9', borderRadius: '50%' }} />Digital RGB</span><span><i style={{ background: '#ad9af1', transform: 'rotate(45deg)' }} />Virtual print</span></div>
        {chroma && <div className="result-detail-grid" style={{ marginTop: 13 }}><Detail label="Digital dominant wavelength / purity" value={`${numeric(chroma.digital_dominant_or_complementary_wavelength_nm).toFixed(1)} nm · ${(numeric(chroma.digital_excitation_purity) * 100).toFixed(1)}% · ${chroma.digital_wavelength_type}`} /><Detail label="Print dominant wavelength / purity" value={`${numeric(chroma.print_dominant_or_complementary_wavelength_nm).toFixed(1)} nm · ${(numeric(chroma.print_excitation_purity) * 100).toFixed(1)}% · ${chroma.print_wavelength_type}`} /></div>}
      </Panel>
      <Panel>
        <PanelHeading title="CIE chromaticity reference" note="The full pipeline-generated diagram includes the spectral locus and the sRGB gamut." action={<ScanLine size={15} className="muted" />} />
        <a href={api.artifactUrl('figures/chromaticity_diagram.png')} target="_blank" rel="noreferrer"><img className="cie-diagram" src={api.artifactUrl('figures/chromaticity_diagram.png')} alt="CIE 1931 chromaticity diagram with configured colours" loading="lazy" /></a>
        <div className="divider" />
        <Detail label="Wavelength domain" value={`${config.project.wavelength_nm.start}–${config.project.wavelength_nm.end} nm · ${config.project.wavelength_nm.step} nm step`} />
        <Detail label="Illuminant provenance" value="CIE standard D65 plus parameterized 4000 K / 3000 K LED SPDs" />
        <Detail label="Virtual print transfer" value="Configured synthetic spectral absorbance-density model" />
        <div className="notice" style={{ marginTop: 12 }}><Activity size={14} /><span>Dominant wavelength is complemented for purple-region points where the ray meets the line of purples. Values are computation outputs, not instrument observations.</span></div>
      </Panel>
    </div>

    <SectionTitle eyebrow="Traceable records" title="Configured measurements" />
    <Panel>
      <PanelHeading title={`${measurements.length} saved colour records`} note="Filtered by current colour and illuminant selection. Values are served from the API artifact allow-list." action={<Badge tone="cyan">CSV SOURCE</Badge>} />
      {loading ? <div className="loading-state"><LoaderCircle className="spin" size={17} />Reading saved CSV…</div> : row ? <DataTable rowKey="colour_id" rows={[row]} columns={[
        { key: 'colour_id', label: 'ID' }, { key: 'colour_name', label: 'Retail meaning' }, { key: 'hex', label: 'sRGB' }, { key: 'illumination_id', label: 'Light' }, { key: 'source_model', label: 'Illuminant model' }, { key: 'delta_e00', label: 'ΔE00', render: (item) => <span className="mono">{numeric(item.delta_e00).toFixed(4)}</span> }, { key: 'delta_l_star', label: 'ΔL*', render: (item) => numeric(item.delta_l_star).toFixed(3) }, { key: 'delta_c_star', label: 'ΔC*', render: (item) => numeric(item.delta_c_star).toFixed(3) }, { key: 'delta_h_prime', label: 'ΔH′', render: (item) => numeric(item.delta_h_prime).toFixed(3) },
      ]} /> : <EmptyState title="No filtered record" message="Change the colour or illuminant selection, or run the full pipeline." />}
    </Panel>
  </>
}

function Detail({ label, value }: { label: string; value: unknown }) { return <div className="result-detail"><span>{label}</span><strong>{value === undefined || value === null || value === '' ? '—' : String(value)}</strong></div> }
function ChartTooltip({ active, payload, label }: any) { if (!active || !payload?.length) return null; return <div className="chart-tooltip"><div className="chart-tooltip__label">{label}</div>{payload.map((item: any) => <div key={item.dataKey} style={{ color: item.color, marginTop: 3 }}>{item.name}: {Number(item.value).toFixed(3)}</div>)}</div> }
