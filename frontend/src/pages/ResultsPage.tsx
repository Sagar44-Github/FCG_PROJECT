import { useEffect, useMemo, useState } from 'react'
import { Archive, ChevronLeft, ChevronRight, Download, FileArchive, FileImage, FileSpreadsheet, FileText, LoaderCircle, Play, Search, ServerCog } from 'lucide-react'
import { Badge, Button, DataTable, EmptyState, ErrorState, Field, PageHeading, Panel, PanelHeading, SectionTitle } from '../components/ui'
import { api, ApiError } from '../lib/api'
import { loadCsv } from '../lib/csv'
import type { Artifact, DashboardSummary, JobRecord, Page } from '../lib/types'
import { SceneRender, type SceneRenderId } from '../components/SceneRender'

type HistoryKind = 'analysis-jobs' | 'render-jobs' | 'colour-comparisons' | 'donation-simulations'
type Row = Record<string, any>
const historyLabels: Record<HistoryKind, string> = { 'analysis-jobs': 'Analysis', 'render-jobs': 'Blender renders', 'colour-comparisons': 'Colour comparisons', 'donation-simulations': 'Donation simulations' }
const presentationRenders: SceneRenderId[] = ['01_supermarket_hero','02_shelf_detail','03_donate_now_macro','04_colour_status_system','05_illuminant_comparison','06_supermarket_isometric']

export default function ResultsPage({ dashboard, refresh }: { dashboard: DashboardSummary; refresh: () => Promise<void> }) {
  const [kind, setKind] = useState<HistoryKind>('analysis-jobs')
  const [history, setHistory] = useState<Page<Row> | null>(null)
  const [offset, setOffset] = useState(0)
  const [illumination, setIllumination] = useState('all')
  const [recognition, setRecognition] = useState('all')
  const [status, setStatus] = useState('all')
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [artifacts, setArtifacts] = useState<Artifact[]>([])
  const [artifactSearch, setArtifactSearch] = useState('')
  const [artifactType, setArtifactType] = useState<'all' | 'csv' | 'png' | 'json'>('all')
  const [selectedArtifact, setSelectedArtifact] = useState('')
  const [csvRows, setCsvRows] = useState<Row[]>([])
  const [analysisJob, setAnalysisJob] = useState<JobRecord | null>(null)
  const [analysisError, setAnalysisError] = useState('')
  const [analysisRunning, setAnalysisRunning] = useState(false)
  const [pageError, setPageError] = useState('')

  async function fetchHistory(targetOffset = offset, selectedKind = kind) {
    setLoadingHistory(true); setPageError('')
    try {
      const query = new URLSearchParams({ limit: '6', offset: String(targetOffset) })
      if ((selectedKind === 'render-jobs' || selectedKind === 'analysis-jobs') && status !== 'all') query.set('status', status)
      if ((selectedKind === 'colour-comparisons' || selectedKind === 'donation-simulations') && illumination !== 'all') query.set('illumination_id', illumination)
      if (selectedKind === 'donation-simulations' && recognition !== 'all') query.set('recognition', recognition)
      const data = await api.get<Page<Row>>(`/${selectedKind}?${query}`)
      setHistory(data); setOffset(targetOffset)
    } catch (reason) { setPageError(reason instanceof Error ? reason.message : 'Persisted history could not be loaded.') }
    finally { setLoadingHistory(false) }
  }
  useEffect(() => { void fetchHistory(0, kind) }, [kind, illumination, recognition, status])
  useEffect(() => {
    let alive = true
    api.get<{ items: Artifact[] }>('/artifacts').then((data) => { if (!alive) return; const available = data.items.filter((item) => item.available); setArtifacts(available); if (available[0]) setSelectedArtifact((current) => current || available[0].name) }).catch((reason: unknown) => alive && setPageError(reason instanceof Error ? reason.message : 'Artifact index could not be loaded.'))
    return () => { alive = false }
  }, [])
  useEffect(() => {
    let alive = true
    setCsvRows([])
    if (selectedArtifact.endsWith('.csv')) loadCsv<Row>(selectedArtifact).then((rows) => alive && setCsvRows(rows.slice(0, 60))).catch((reason: unknown) => alive && setPageError(reason instanceof Error ? reason.message : `Could not preview ${selectedArtifact}.`))
    return () => { alive = false }
  }, [selectedArtifact])

  useEffect(() => {
    if (!analysisJob || !['queued', 'running'].includes(analysisJob.status)) return
    let alive = true
    const timer = window.setInterval(() => {
      api.get<JobRecord>(`/analysis-jobs/${analysisJob.id}`).then((job) => {
        if (!alive) return
        setAnalysisJob(job)
        if (job.status === 'completed' || job.status === 'failed') {
          window.clearInterval(timer); setAnalysisRunning(false)
          if (job.status === 'completed') { void refresh(); void fetchHistory(0, 'analysis-jobs') }
        }
      }).catch((reason: unknown) => alive && setAnalysisError(reason instanceof Error ? reason.message : 'Could not refresh analysis-job status.'))
    }, 1300)
    return () => { alive = false; window.clearInterval(timer) }
  }, [analysisJob?.id, analysisJob?.status, refresh])

  const filteredArtifacts = useMemo(() => artifacts.filter((item) => {
    const matchesSearch = item.name.toLowerCase().includes(artifactSearch.toLowerCase())
    const extension = item.name.split('.').pop()?.toLowerCase()
    return matchesSearch && (artifactType === 'all' || extension === artifactType)
  }), [artifacts, artifactSearch, artifactType])
  const chosen = artifacts.find((item) => item.name === selectedArtifact)

  async function runFullAnalysis() {
    setAnalysisRunning(true); setAnalysisError('')
    try { setAnalysisJob(await api.post<JobRecord>('/analysis-jobs', { donation_replicates: 500 })) }
    catch (reason) { setAnalysisRunning(false); setAnalysisError(reason instanceof ApiError ? reason.message : 'Full analysis could not be started.') }
  }

  async function previewCsv(name: string) { setSelectedArtifact(name) }

  const rows = history?.items ?? []
  const historyColumns = columnsFor(kind)
  const activeJobBusy = analysisRunning || (analysisJob && ['queued', 'running'].includes(analysisJob.status))

  return <>
    <PageHeading kicker="Evidence 06 / Persisted outputs" title="Results & exports" description="Browse database history, inspect pipeline artifacts, trigger a complete evidence run, and download the reproducibility package from the real FastAPI service." action={<Badge tone="cyan">{dashboard.artifact_count} PIPELINE ARTIFACTS</Badge>} />

    <SectionTitle eyebrow="Blender visual evidence · six authored views" title="VERDANT MARKET scene renders" trailing={<Badge tone="neutral">2560 × 1440 FINAL SET</Badge>} />
    <div className="result-scene-grid">{presentationRenders.map((id) => <div className="result-scene-item" key={id}><SceneRender id={id} /><a className="scene-download" href={`/assets/supermarket/${id}.png`} download={`${id}.png`}><Download size={13} /> Download PNG</a></div>)}</div>

    <Panel>
      <div className="export-hero"><div className="export-hero__icon"><FileArchive size={20} /></div><div><h3>Reproducible research evidence package</h3><p>Source code, model assumptions, CIE data, saved results, Blender evidence, diagrams, tests, figures, and the active configuration digest are assembled by the backend export route.</p></div><a className="zip-link" href={api.fileUrl('/api/v1/exports/evidence-package')} download="q3_research_evidence.zip"><Button icon={<Download size={14} />}>Download evidence ZIP</Button></a></div>
      <div className="form-actions" style={{ marginTop: 14 }}><Button onClick={() => void runFullAnalysis()} loading={Boolean(activeJobBusy)} icon={<Play size={14} />}>{activeJobBusy ? 'Analysis job in progress…' : 'Run full evidence analysis'}</Button><span className="form-note">Submits 500 donation Monte Carlo replicates to the full backend pipeline.</span></div>
      {analysisError && <div style={{ marginTop: 12 }}><ErrorState title="Analysis job request failed" message={analysisError} /></div>}
      {analysisJob && <div className="job-state" style={{ marginTop: 12 }}><div><span className="small-caps">ANALYSIS JOB</span><div className="job-state__meta mono">{analysisJob.id} · {analysisJob.status}</div>{analysisJob.error && <div className="form-note">{analysisJob.error}</div>}</div><Badge tone={analysisJob.status === 'completed' ? 'success' : analysisJob.status === 'failed' ? 'danger' : 'warning'} dot>{analysisJob.status.toUpperCase()}</Badge></div>}
    </Panel>

    <SectionTitle eyebrow="SQLite operation history" title="Previous processing runs" trailing={<span className="tagline"><ServerCog size={13} /> API-paginated collections</span>} />
    <Panel>
      <div className="history-tabs" role="tablist" aria-label="Processing history type">{(Object.keys(historyLabels) as HistoryKind[]).map((key) => <button type="button" key={key} role="tab" aria-selected={kind === key} aria-pressed={kind === key} onClick={() => { setKind(key); setOffset(0) }}>{historyLabels[key]}</button>)}</div>
      <div className="grid grid--main" style={{ alignItems: 'end', marginBottom: 13 }}><PanelHeading title={historyLabels[kind]} note="Filters are sent as backend query parameters; results are paginated by limit and offset." /><div className="field-grid">
        {(kind === 'render-jobs' || kind === 'analysis-jobs') && <Field label="Job status"><select value={status} onChange={(event) => setStatus(event.target.value)}><option value="all">All statuses</option><option value="queued">Queued</option><option value="running">Running</option><option value="completed">Completed</option><option value="failed">Failed</option></select></Field>}
        {(kind === 'colour-comparisons' || kind === 'donation-simulations') && <Field label="Illumination"><select value={illumination} onChange={(event) => setIllumination(event.target.value)}><option value="all">All illuminants</option><option value="L1">L1 · D65</option><option value="L2">L2 · Neutral LED</option><option value="L3">L3 · Warm LED</option></select></Field>}
        {kind === 'donation-simulations' && <Field label="Recognition mode"><select value={recognition} onChange={(event) => setRecognition(event.target.value)}><option value="all">All modes</option><option value="simulated_errors">Synthetic observer</option><option value="perfect">Perfect baseline</option></select></Field>}
      </div></div>
      {pageError && <ErrorState title="Could not load this collection" message={pageError} onRetry={() => void fetchHistory(offset, kind)} />}
      {loadingHistory ? <div className="loading-state"><LoaderCircle className="spin" size={17} />Requesting persisted rows…</div> : <DataTable rowKey="id" rows={rows} columns={historyColumns} />}
      <div className="pagination"><span>{history ? `Page offset ${history.offset} · ${rows.length} shown of ${history.total} records` : 'History not loaded'}</span><span className="pagination__controls"><button aria-label="Previous page" disabled={!history || history.offset === 0 || loadingHistory} onClick={() => void fetchHistory(Math.max(0, offset - 6), kind)}><ChevronLeft size={14} /></button><button aria-label="Next page" disabled={!history || history.offset + rows.length >= history.total || loadingHistory} onClick={() => void fetchHistory(offset + 6, kind)}><ChevronRight size={14} /></button></span></div>
    </Panel>

    <SectionTitle eyebrow="Downloadable evidence" title="Generated files" trailing={<Badge tone="neutral">{filteredArtifacts.length} SHOWN</Badge>} />
    <div className="export-grid">
      <Panel>
        <PanelHeading title="API allow-listed artifacts" note="Each item is read from its actual saved result file; unavailable files are omitted." action={<Archive size={15} className="muted" />} />
        <div className="grid grid--main" style={{ marginBottom: 12 }}><div className="search-field"><Search size={14} /><input aria-label="Search artifacts" value={artifactSearch} onChange={(event) => setArtifactSearch(event.target.value)} placeholder="Filter by filename…" /></div><div className="segmented" aria-label="Filter file types">{(['all', 'csv', 'png', 'json'] as const).map((type) => <button type="button" key={type} aria-pressed={artifactType === type} onClick={() => setArtifactType(type)}>{type.toUpperCase()}</button>)}</div></div>
        <div className="artifact-list">{filteredArtifacts.length ? filteredArtifacts.map((item) => <div key={item.name} className="artifact-row"><ArtifactIcon name={item.name} /><button className="artifact-row__name" onClick={() => void previewCsv(item.name)} title={item.name}>{item.name}</button><span className="artifact-row__size">{(item.bytes ?? 0).toLocaleString()} B</span><a className="artifact-row__download" href={api.artifactUrl(item.name)} download={item.name.split('/').pop()} title={`Download ${item.name}`}><Download size={13} /></a></div>) : <EmptyState title="No matching files" message="Change the filter or run the evidence pipeline." />}</div>
      </Panel>
      <Panel>
        <PanelHeading title="Artifact preview" note={chosen?.name ?? 'Select a generated file to inspect it.'} action={chosen && <a className="button button--quiet" href={api.artifactUrl(chosen.name)} download={chosen.name.split('/').pop()}><Download size={13} /> Download</a>} />
        {!chosen ? <EmptyState title="No file selected" message="Choose an available CSV, PNG, or metadata file." /> : chosen.name.endsWith('.png') ? <div className="file-preview"><a href={api.artifactUrl(chosen.name)} target="_blank" rel="noreferrer"><img className="render-image" src={api.artifactUrl(chosen.name)} alt={`Generated figure ${chosen.name}`} loading="lazy" /></a></div> : chosen.name.endsWith('.csv') ? csvRows.length ? <DataTable rowKey="id" rows={csvRows} columns={Object.keys(csvRows[0]).slice(0, 8).map((key) => ({ key, label: key }))} /> : <div className="loading-state"><LoaderCircle className="spin" size={15} />Loading CSV preview…</div> : <div className="result-detail"><span>File size</span><strong>{(chosen.bytes ?? 0).toLocaleString()} bytes · download for complete content</strong></div>}
        {chosen?.name.endsWith('.csv') && <div className="form-note" style={{ marginTop: 8 }}>Preview is limited to 60 rows and eight columns. Download retrieves the full CSV.</div>}
      </Panel>
    </div>
  </>
}

function columnsFor(kind: HistoryKind) {
  if (kind === 'analysis-jobs' || kind === 'render-jobs') return [
    { key: 'id', label: 'Job ID', render: (row: Row) => <span className="mono">{String(row.id).slice(0, 13)}…</span> },
    { key: 'status', label: 'Status', render: (row: Row) => <Badge tone={row.status === 'completed' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'} dot>{row.status}</Badge> },
    { key: 'created_at', label: 'Created', render: (row: Row) => row.created_at ? new Date(row.created_at).toLocaleString() : '—' },
    { key: 'samples', label: 'Request', render: (row: Row) => kind === 'render-jobs' ? `${row.request?.samples ?? '—'} samples` : `${row.request?.donation_replicates ?? '—'} replicates` },
    { key: 'outputs', label: 'Result', render: (row: Row) => row.status === 'failed' ? row.error : kind === 'render-jobs' ? `${row.result?.count ?? '—'} renders` : row.result?.donation_replicates_per_scenario ? `${row.result.donation_replicates_per_scenario} per scenario` : '—' },
  ]
  if (kind === 'colour-comparisons') return [
    { key: 'id', label: 'Comparison ID', render: (row: Row) => <span className="mono">{String(row.id).slice(0, 13)}…</span> }, { key: 'colour_id', label: 'Colour' }, { key: 'illumination_id', label: 'Illuminant' }, { key: 'created_at', label: 'Created', render: (row: Row) => row.created_at ? new Date(row.created_at).toLocaleString() : '—' }, { key: 'delta_e00', label: 'ΔE00', render: (row: Row) => row.result?.delta_e00 === undefined ? '—' : Number(row.result.delta_e00).toFixed(4) },
  ]
  return [
    { key: 'id', label: 'Simulation ID', render: (row: Row) => <span className="mono">{String(row.id).slice(0, 13)}…</span> }, { key: 'illumination_id', label: 'Illuminant' }, { key: 'recognition', label: 'Recognition' }, { key: 'capacity_per_day', label: 'Capacity/day' }, { key: 'created_at', label: 'Created', render: (row: Row) => row.created_at ? new Date(row.created_at).toLocaleString() : '—' }, { key: 'saved', label: 'Mean saved', render: (row: Row) => row.result?.mean?.units_saved === undefined ? '—' : Number(row.result.mean.units_saved).toFixed(1) },
  ]
}
function ArtifactIcon({ name }: { name: string }) { const ext = name.split('.').pop()?.toLowerCase(); if (ext === 'csv') return <FileSpreadsheet size={15} />; if (ext === 'png') return <FileImage size={15} />; if (ext === 'zip') return <FileArchive size={15} />; return <FileText size={15} /> }
