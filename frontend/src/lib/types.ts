export type ColourId = 'G' | 'Y' | 'O' | 'R'
export type IlluminationId = 'L1' | 'L2' | 'L3'
export type ActionId = 'fresh' | 'watch' | 'discount' | 'donate'

export interface ColourDefinition { name: string; action: ActionId; hex: string }
export interface IlluminationDefinition { name: string; kind: string; cct_kelvin: number; is_standard: boolean }
export interface ProjectConfiguration {
  project: { title: string; version: string; random_seed: number; wavelength_nm: { start: number; end: number; step: number }; observer: string }
  colours: Record<ColourId, ColourDefinition>
  illuminations: Record<IlluminationId, IlluminationDefinition>
  observer: { base_error_probability: number; maximum_additional_error_probability: number; delta_e_midpoint: number; delta_e_scale: number; confusion_weights: { adjacent: number; nonadjacent: number } }
  donation: { mean_near_expiry_arrivals_per_day: number; simulation_days: number; replicates: number; donation_capacities_per_day: number[]; average_product_kg: number; avoided_emissions_kgco2e_per_kg: number }
  sustainability: { emissions_factor_scenarios_kgco2e_per_kg: Record<string, number>; factor_source_note: string }
}

export interface ConfigurationResponse { configuration: ProjectConfiguration; sha256: string; mutable_via_api: boolean; note: string }
export interface JobRecord { id: string; type?: string; status: string; created_at: string; updated_at?: string | null; error?: string | null; request?: Record<string, unknown>; result?: Record<string, any> | null }
export interface Page<T> { total: number; limit: number; offset: number; items: T[] }

export interface DashboardSummary {
  project_title: string; configuration_sha256: string; render_status: string; render_count: number; baseline_render_count: number
  render_job_count: number; latest_render_job_status: string | null; render_catalog: RenderItem[]
  colour_analysis_status: string; colour_measurement_count: number; delta_e_summary: Record<string, any>[]
  red_trigger_summary: Record<string, any>[]; donation_summary: Record<string, any>[]; sustainability_summary: Record<string, any>[]
  generated_at: string | null; software: Record<string, any>; recent_jobs: JobRecord[]; artifact_count: number
}
export interface RenderItem { render_id: string; filename: string; colour_id?: ColourId; colour_name?: string; hex?: string; illumination_id?: IlluminationId; illumination_name?: string; kind?: string; url: string }
export interface Measurement extends Record<string, string> { colour_id: string; illumination_id: string; delta_e00: string; hex: string }
export interface ChromaRow extends Record<string, string> { colour_id: string; illumination_id: string; digital_x: string; digital_y: string }
export interface Comparison { id: string; colour_id: ColourId; illumination_id: IlluminationId; result: Record<string, any>; created_at?: string | null }
export interface DonationSimulation { id: string; illumination_id: IlluminationId; recognition?: string | null; capacity_per_day?: number | null; result: Record<string, any>; created_at?: string | null }
export interface Artifact { name: string; available: boolean; bytes?: number | null }
