import { lazy, Suspense, useEffect, useMemo, useState } from 'react'
import { Camera, CheckCircle2, ChevronRight, CircleHelp, Clock3, Download, Focus, LoaderCircle, Orbit, Play } from 'lucide-react'
import { Badge, Button, EmptyState, ErrorState, PageHeading, Panel, PanelHeading, SelectField, SectionTitle } from '../components/ui'
import type { SectionId } from '../components/Layout'
import { api, ApiError } from '../lib/api'
import type { ColourId, DashboardSummary, IlluminationId, JobRecord, ProjectConfiguration } from '../lib/types'
import { SceneRender } from '../components/SceneRender'

const SpectralScene = lazy(() => import('../components/SpectralScene').then((module) => ({ default: module.SpectralScene })))
const colourIds: ColourId[] = ['G', 'Y', 'O', 'R']
const illuminationIds: IlluminationId[] = ['L1', 'L2', 'L3']

export default function DigitalTwinPage({ config, dashboard, refresh, onNavigate, selectedColor, onSelectColor, selectedIllumination, onSelectIllumination }: { config: ProjectConfiguration; dashboard: DashboardSummary; refresh: () => Promise<void>; onNavigate: (page: SectionId) => void; selectedColor: ColourId; onSelectColor: (id: ColourId) => void; selectedIllumination: IlluminationId; onSelectIllumination: (id: IlluminationId) => void }) {
  const [renderJobs, setRenderJobs] = useState<JobRecord[]>([])
  const [activeJob, setActiveJob] = useState<JobRecord | null>(null)
  const [samples, setSamples] = useState('16')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const matchingRenders = dashboard.render_catalog.filter((render) => render.colour_id === selectedColor && render.illumination_id === selectedIllumination)
  const selectedRender = matchingRenders.find((render) => render.render_id !== 'baseline') ?? matchingRenders[0]
  const lightingComparisons = illuminationIds.map((illuminationId) => dashboard.render_catalog.find((render) => render.colour_id === selectedColor && render.illumination_id === illuminationId && render.render_id === selectedRender?.render_id)
    ?? dashboard.render_catalog.find((render) => render.colour_id === selectedColor && render.illumination_id === illuminationId && render.render_id === 'baseline'))
  const availableBatch = useMemo(() => {
    const items = dashboard.render_catalog.filter((render) => render.colour_id && render.render_id === selectedRender?.render_id)
    return items.length ? items : dashboard.render_catalog.filter((render) => render.colour_id && render.render_id === 'baseline')
  }, [dashboard.render_catalog, selectedRender?.render_id])
  const contactSheet = dashboard.render_catalog.find((render) => render.render_id === selectedRender?.render_id && render.kind === 'contact_sheet') ?? dashboard.render_catalog.find((render) => render.render_id === 'baseline' && render.kind === 'contact_sheet')

  useEffect(() => {
    let alive = true
    api.get<{ items: JobRecord[] }>('/render-jobs?limit=8&offset=0').then((result) => alive && setRenderJobs(result.items)).catch((reason: unknown) => alive && setError(reason instanceof Error ? reason.message : 'Render history could not be loaded.'))
    return () => { alive = false }
  }, [dashboard.render_job_count])

  useEffect(() => {
    if (!activeJob || !['queued', 'running'].includes(activeJob.status)) return
    let alive = true
    const timer = window.setInterval(() => {
      api.get<JobRecord>(`/render-jobs/${activeJob.id}`).then((job) => {
        if (!alive) return
        setActiveJob(job)
        if (job.status === 'completed' || job.status === 'failed') {
          window.clearInterval(timer)
          setRenderJobs((current) => [job, ...current.filter((item) => item.id !== job.id)])
          if (job.status === 'completed') void refresh()
        }
      }).catch((reason: unknown) => { if (alive) setError(reason instanceof Error ? reason.message : 'Could not refresh the Blender job status.') })
    }, 1800)
    return () => { alive = false; window.clearInterval(timer) }
  }, [activeJob?.id, activeJob?.status, refresh])

  async function startRender() {
    setError(''); setSubmitting(true)
    try {
      const job = await api.post<JobRecord>('/render-jobs', { render_all: true, samples: Number(samples) })
      setActiveJob(job)
      setRenderJobs((current) => [job, ...current.filter((item) => item.id !== job.id)])
    } catch (reason) { setError(reason instanceof ApiError ? reason.message : 'Blender render request failed.') }
    finally { setSubmitting(false) }
  }

  const jobBusy = activeJob && ['queued', 'running'].includes(activeJob.status)
  const jobError = activeJob?.status === 'failed' ? activeJob.error : null
  const totalConditions = Object.keys(config.colours).length * Object.keys(config.illuminations).length

  return <>
    <PageHeading kicker="Instrument 02 / Blender digital twin" title="Digital twin" description="Explore the shelf-label scene interactively. Blender Cycles renders remain the authoritative visual outputs; this real-time Three.js model is a navigation and inspection aid." action={<Badge tone="success" dot>{dashboard.baseline_render_count}/{totalConditions} BASELINE RENDERS</Badge>} />
    <div className="digital-twin-layout">
      <div>
        <div className="digital-twin-viewer"><Suspense fallback={<div className="loading-state"><LoaderCircle className="spin" size={18} />Loading 3D shelf scene…</div>}><SpectralScene config={config} selectedColor={selectedColor} selectedIllumination={selectedIllumination} onSelect={onSelectColor} fallbackUrl={selectedRender ? api.fileUrl(selectedRender.url) : undefined} /></Suspense></div>
        <div className="scene-detail"><div><div className="scene-detail__name">{config.colours[selectedColor].name} · {config.illuminations[selectedIllumination].name}</div><div className="scene-detail__note">Clickable labels · orbit and zoom enabled · selected light is highlighted</div></div><span className="scene-detail__value">{selectedColor} / {selectedIllumination}</span></div>
        <Panel className="lighting-comparison">
          <PanelHeading title="See the light change" note={`${config.colours[selectedColor].name} · three actual Blender RGB condition renders`} action={<Badge tone="warning">VISUAL PREVIEW</Badge>} />
          <div className="lighting-comparison__grid">{lightingComparisons.map((render, index) => {
            const illuminationId = illuminationIds[index]
            return render ? <button type="button" key={illuminationId} className={`lighting-comparison__item ${selectedIllumination === illuminationId ? 'is-active' : ''}`} onClick={() => onSelectIllumination(illuminationId)} aria-pressed={selectedIllumination === illuminationId}>
              <img src={api.fileUrl(render.url)} alt={`${config.colours[selectedColor].name} label render under ${config.illuminations[illuminationId].name}`} loading="lazy" />
              <span><strong>{illuminationId} · {illuminationId === 'L1' ? 'D65' : `${config.illuminations[illuminationId].cct_kelvin} K`}</strong><small>{illuminationId === 'L1' ? 'Neutral daylight view' : illuminationId === 'L2' ? 'Warmer neutral view' : 'Warm amber view'}</small></span>
            </button> : null
          })}</div>
          <div className="research-warning">These Cycles images show RGB appearance proxies. CIE spectral values are calculated separately by the Python model; the LED scenes are not measured lamp spectra.</div>
        </Panel>
        <SceneRender id="02_shelf_detail" className="digital-twin-photo" title="Cycles source scene · shelf merchandising detail" note="Presentation render from HERO_SUPERMARKET · visual RGB output" />
        <div className="grid grid--2" style={{ marginTop: 12 }}>
          <Panel>
            <PanelHeading title="Authoritative Blender render" note={`${selectedRender?.render_id === 'baseline' ? 'Baseline' : `Render job ${selectedRender?.render_id?.slice(0, 8) ?? ''}`} · configured label and illuminant`} action={selectedRender && <a className="button button--quiet" href={api.fileUrl(selectedRender.url)} download={selectedRender.filename}><Download size={14} /> PNG</a>} />
            {selectedRender ? <img className="render-image" src={api.fileUrl(selectedRender.url)} alt={`Blender render ${selectedColor} under ${selectedIllumination}`} loading="lazy" /> : <EmptyState title="Render not available" message="Run a 12-condition Blender batch to generate the render." />}
            {selectedRender && <div className="form-note" style={{ marginTop: 8 }}>RGB Cycles preview. Spectral reflectance is evaluated separately in the Python colour engine.</div>}
          </Panel>
          <Panel>
            <PanelHeading title="Twelve-condition contact sheet" note="The complete colour × illuminant matrix from one Blender batch." action={<Badge tone="cyan">4 × 3 MATRIX</Badge>} />
            {contactSheet ? <img className="render-image" src={api.fileUrl(contactSheet.url)} alt="Twelve Blender render conditions contact sheet" loading="lazy" /> : <EmptyState title="Contact sheet not generated" message="A contact sheet is created when a Blender batch completes." />}
          </Panel>
        </div>
      </div>

      <div className="twin-controls">
        <Panel>
          <PanelHeading title="Scene configuration" note="Selections read from the research configuration." action={<Badge tone="violet">{totalConditions} CONDITIONS</Badge>} />
          <div className="form-stack">
            <div><div className="form-section-heading"><Focus size={14} />Label response</div><div className="label-select-grid">{colourIds.map((id) => {
              const item = config.colours[id]
              return <button className={`label-select ${selectedColor === id ? 'label-select--selected' : ''}`} key={id} aria-pressed={selectedColor === id} onClick={() => onSelectColor(id)}><span className="label-select__swatch" style={{ background: item.hex }} /><span><strong>{item.name}</strong><small>{id} · {item.action.replace('_', ' ')}</small></span></button>
            })}</div></div>
            <div><div className="form-section-heading"><Orbit size={14} />Illumination field</div><div className="condition-strip">{illuminationIds.map((id) => <button key={id} className={`condition-button ${selectedIllumination === id ? 'condition-button--active' : ''}`} aria-pressed={selectedIllumination === id} onClick={() => onSelectIllumination(id)}><strong>{id} · {config.illuminations[id].cct_kelvin} K</strong><small>{id === 'L1' ? 'Standard D65' : 'LED approximation'}</small></button>)}</div></div>
          </div>
        </Panel>
        <Panel>
          <PanelHeading title="Generate Blender batch" note="Starts the real Blender Python automation on the backend." action={<Camera size={15} className="muted" />} />
          <div className="form-stack"><SelectField label="Cycles samples" value={samples} onChange={setSamples} options={[1, 8, 16, 32, 64, 128].map((value) => ({ value: String(value), label: `${value} samples` }))} help="Higher samples reduce noise and take longer. The backend renders all 12 cases." />
            <Button onClick={() => void startRender()} loading={submitting || Boolean(jobBusy)} icon={<Play size={15} />}>{jobBusy ? 'Blender is rendering…' : 'Render all 12 conditions'}</Button>
            <div className="notice"><CircleHelp size={14} /><span>The API uses a server-selected Blender executable, fixed arguments, and a per-job output folder. No frontend output path is accepted.</span></div>
            {error && <ErrorState title="Render request error" message={error} />}{jobError && <ErrorState title="Blender reported a failed job" message={jobError} />}
            {activeJob && <div className="job-state"><div><span className="small-caps">ACTIVE JOB</span><div className="job-state__meta mono">{activeJob.id.slice(0, 14)}… · {activeJob.status}</div></div><Badge tone={activeJob.status === 'completed' ? 'success' : activeJob.status === 'failed' ? 'danger' : 'warning'} dot>{activeJob.status.toUpperCase()}</Badge></div>}
            {activeJob?.status === 'completed' && <div className="notice"><CheckCircle2 size={14} /><span>Blender completed {activeJob.result?.count ?? 12} case renders. The image catalog has been refreshed from the API.</span></div>}
          </div>
        </Panel>
        <Panel>
          <PanelHeading title="Render batch history" note="Persisted records from SQLite." action={<Clock3 size={14} className="muted" />} />
          {renderJobs.length ? <div className="activity-list">{renderJobs.slice(0, 5).map((job) => <div className="activity-item" key={job.id}><span className="activity-icon"><Camera size={14} /></span><span><strong>{job.request?.samples ?? '—'} Cycles samples · {job.result?.count ?? 0} images</strong><small>{job.id.slice(0, 8)} · {job.created_at ? new Date(job.created_at).toLocaleString() : ''}</small></span><Badge tone={job.status === 'completed' ? 'success' : job.status === 'failed' ? 'danger' : 'warning'}>{job.status}</Badge></div>)}</div> : <EmptyState title="No API render jobs yet" message="The saved 12 baseline renders are available above; new render jobs will appear here." />}
          <div className="divider" /><div className="inline-status"><i />{dashboard.render_count} case PNGs listed · configuration {dashboard.configuration_sha256.slice(0, 8)}</div>
        </Panel>
      </div>
    </div>

    <SectionTitle eyebrow="Selected render batch" title={`${selectedColor} · ${selectedIllumination} inspection`} trailing={<Button variant="quiet" icon={<ChevronRight size={14} />} onClick={() => onNavigate('colour-lab')}>Open colour analysis</Button>} />
    <div className="render-catalog">{availableBatch.map((render) => <button key={`${render.render_id}-${render.filename}`} className={`render-thumb ${render.colour_id === selectedColor && render.illumination_id === selectedIllumination ? 'render-thumb--active' : ''}`} onClick={() => { if (render.colour_id) onSelectColor(render.colour_id); if (render.illumination_id) onSelectIllumination(render.illumination_id) }}><img src={api.fileUrl(render.url)} alt={`${render.colour_name} under ${render.illumination_name}`} loading="lazy" /><span>{render.colour_id} · {render.illumination_id} · {render.hex}</span></button>)}</div>
  </>
}
