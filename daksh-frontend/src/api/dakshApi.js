// Shared API primitives. All raw fetch() calls live behind this file and its
// siblings (moduleApi.js, multiDocumentApi.js) — components never call
// fetch() directly. Toggle real vs. mock via VITE_API_MODE.

export const API_MODE = import.meta.env.VITE_API_MODE === 'real' ? 'real' : 'mock'

export class DakshApiError extends Error {
  constructor(message, { stage, retryable = true, cause } = {}) {
    super(message)
    this.name = 'DakshApiError'
    this.stage = stage // where it failed: 'upload' | 'ocr' | 'validation' | 'network' | ...
    this.retryable = retryable
    this.cause = cause
  }
}

export async function request(url, options = {}) {
  if (!url) {
    throw new DakshApiError('This module has no backend configured for this environment.', {
      stage: 'network',
      retryable: false
    })
  }
  try {
    const res = await fetch(url, options)
    let payload = null
    try {
      payload = await res.json()
    } catch (e) {
      payload = null
    }

    if (!res.ok) {
      const detailMsg = (payload && (payload.error || (payload.adapter_errors && payload.adapter_errors.join('; '))))
        || `Backend responded with ${res.status}`
      throw new DakshApiError(detailMsg, {
        stage: 'server',
        retryable: res.status >= 500,
        cause: payload
      })
    }
    return payload
  } catch (err) {
    if (err instanceof DakshApiError) throw err
    throw new DakshApiError('Could not reach the backend service.', {
      stage: 'network',
      retryable: true,
      cause: err
    })
  }
}

// Small helper so mock flows still feel like network round-trips.
export function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}
