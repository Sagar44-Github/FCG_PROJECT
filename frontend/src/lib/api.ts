const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')
const PREFIX = '/api/v1'

export class ApiError extends Error {
  status?: number
  constructor(message: string, status?: number) { super(message); this.name = 'ApiError'; this.status = status }
}

function endpoint(path: string) {
  return `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(endpoint(`${PREFIX}${path.startsWith('/') ? path : `/${path}`}`), {
      ...init,
      headers: { ...(init?.body ? { 'Content-Type': 'application/json' } : {}), ...init?.headers },
    })
  } catch (error) {
    throw new ApiError(error instanceof Error ? error.message : 'The research API could not be reached.')
  }
  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try { detail = (await response.json()).detail ?? detail } catch { /* response may not be JSON */ }
    throw new ApiError(typeof detail === 'string' ? detail : JSON.stringify(detail), response.status)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const api = {
  get: <T,>(path: string, signal?: AbortSignal) => request<T>(path, { signal }),
  post: <T,>(path: string, body: unknown) => request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
  fileUrl: (path: string) => endpoint(path),
  artifactUrl: (name: string) => endpoint(`${PREFIX}/artifacts/${name.split('/').map(encodeURIComponent).join('/')}`),
  artifact: async (name: string) => {
    const response = await fetch(endpoint(`${PREFIX}/artifacts/${name.split('/').map(encodeURIComponent).join('/')}`))
    if (!response.ok) throw new ApiError(`Artifact ${name} is unavailable.`, response.status)
    return response.text()
  },
}
