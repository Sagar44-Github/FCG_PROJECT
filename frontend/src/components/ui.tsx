import type { CSSProperties, ReactNode } from 'react'
import { ArrowUpRight, LoaderCircle, RefreshCw, Sparkles } from 'lucide-react'

export function Eyebrow({ children }: { children: ReactNode }) { return <span className="eyebrow">{children}</span> }
export function PageHeading({ kicker, title, description, action }: { kicker: string; title: string; description?: string; action?: ReactNode }) {
  return <div className="page-heading"><div><Eyebrow>{kicker}</Eyebrow><h1>{title}</h1>{description && <p>{description}</p>}</div>{action && <div className="page-heading__action">{action}</div>}</div>
}
export function Panel({ children, className = '', style }: { children: ReactNode; className?: string; style?: CSSProperties }) { return <section className={`panel ${className}`} style={style}>{children}</section> }
export function PanelHeading({ title, note, action }: { title: string; note?: string; action?: ReactNode }) {
  return <div className="panel-heading"><div><h2>{title}</h2>{note && <p>{note}</p>}</div>{action}</div>
}
export function MetricCard({ label, value, note, accent = 'cyan', icon }: { label: string; value: ReactNode; note?: string; accent?: string; icon?: ReactNode }) {
  return <div className={`metric-card metric-card--${accent}`}><div className="metric-card__top"><span>{label}</span>{icon && <span className="metric-card__icon">{icon}</span>}</div><strong>{value}</strong>{note && <small>{note}</small>}</div>
}
export function Badge({ children, tone = 'neutral', dot = false }: { children: ReactNode; tone?: string; dot?: boolean }) { return <span className={`badge badge--${tone}`}>{dot && <i />}{children}</span> }
export function Button({ children, variant = 'primary', loading = false, icon, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'quiet' | 'danger'; loading?: boolean; icon?: ReactNode }) {
  return <button className={`button button--${variant}`} {...props} disabled={props.disabled || loading}>{loading ? <LoaderCircle className="spin" size={16} /> : icon}{children}</button>
}
export function SelectField({ label, value, onChange, options, help }: { label: string; value: string; onChange: (value: string) => void; options: { value: string; label: string }[]; help?: string }) {
  return <label className="field"><span>{label}</span><select value={value} onChange={(event) => onChange(event.target.value)}>{options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select>{help && <small>{help}</small>}</label>
}
export function Field({ label, children, help }: { label: string; children: ReactNode; help?: string }) { return <label className="field"><span>{label}</span>{children}{help && <small>{help}</small>}</label> }
export function SectionTitle({ eyebrow, title, trailing }: { eyebrow?: string; title: string; trailing?: ReactNode }) { return <div className="section-title">{eyebrow && <Eyebrow>{eyebrow}</Eyebrow>}<div><h2>{title}</h2>{trailing}</div></div> }
export function ErrorState({ title = 'Could not load this data', message, onRetry }: { title?: string; message: string; onRetry?: () => void }) {
  return <div className="state-box state-box--error"><div><strong>{title}</strong><p>{message}</p>{onRetry && <Button variant="secondary" icon={<RefreshCw size={15} />} onClick={onRetry}>Retry request</Button>}</div></div>
}
export function EmptyState({ title, message }: { title: string; message: string }) { return <div className="empty-state"><Sparkles size={18} /><strong>{title}</strong><p>{message}</p></div> }
export function LoadingState({ label = 'Loading saved research data…' }: { label?: string }) { return <div className="loading-state"><LoaderCircle className="spin" size={18} />{label}</div> }
export function DataTable({ columns, rows, rowKey }: { columns: { key: string; label: string; render?: (row: Record<string, any>) => ReactNode }[]; rows: Record<string, any>[]; rowKey?: string }) {
  if (!rows.length) return <EmptyState title="No saved rows" message="Run the relevant analysis through the API to create this evidence." />
  return <div className="table-scroll"><table><thead><tr>{columns.map((column) => <th key={column.key}>{column.label}</th>)}</tr></thead><tbody>{rows.map((row, index) => <tr key={String(row[rowKey ?? 'id'] ?? `${index}`)}>{columns.map((column) => <td key={column.key}>{column.render ? column.render(row) : (row[column.key] ?? '—')}</td>)}</tr>)}</tbody></table></div>
}
export function ExternalLink({ href, children }: { href: string; children: ReactNode }) { return <a className="inline-link" href={href} target="_blank" rel="noreferrer">{children}<ArrowUpRight size={14} /></a> }
