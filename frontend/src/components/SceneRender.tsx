import { Badge } from './ui'

export type SceneRenderId = '01_supermarket_hero' | '02_shelf_detail' | '03_donate_now_macro' | '04_colour_status_system' | '05_illuminant_comparison' | '06_supermarket_isometric'

const captions: Record<SceneRenderId, string> = {
  '01_supermarket_hero': 'VERDANT MARKET · supermarket hero',
  '02_shelf_detail': 'Retail assortment · shelf detail',
  '03_donate_now_macro': 'Near-expiry ticket · DONATE NOW',
  '04_colour_status_system': 'Four-state expiry response · G / Y / O / R',
  '05_illuminant_comparison': 'RGB scene appearance · D65 / 4000 K / 3000 K',
  '06_supermarket_isometric': 'Store plan · open-roof isometric view',
}

export function SceneRender({ id, title, note, className = '' }: { id: SceneRenderId; title?: string; note?: string; className?: string }) {
  return <figure className={`scene-render ${className}`}>
    <a href={`/assets/supermarket/${id}.png`} target="_blank" rel="noreferrer" aria-label={`Open full-size ${captions[id]} Blender render`}>
      <img src={`/assets/supermarket/${id}.png`} alt={captions[id]} loading="lazy" />
    </a>
    <figcaption><span><strong>{title ?? captions[id]}</strong>{note && <small>{note}</small>}</span><Badge tone="neutral">BLENDER · CYCLES</Badge></figcaption>
  </figure>
}
