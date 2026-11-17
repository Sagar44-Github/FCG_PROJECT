import Papa from 'papaparse'
import { api } from './api'

export async function loadCsv<T extends Record<string, unknown>>(name: string): Promise<T[]> {
  const csv = await api.artifact(name)
  const parsed = Papa.parse<T>(csv, { header: true, dynamicTyping: true, skipEmptyLines: true })
  if (parsed.errors.length) throw new Error(parsed.errors[0].message)
  return parsed.data
}

export function numeric(value: unknown): number {
  const result = typeof value === 'number' ? value : Number(value)
  return Number.isFinite(result) ? result : 0
}
