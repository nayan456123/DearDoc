export async function apiRequest(path, options = {}) {
  const { method = 'GET', body, token } = options

  const response = await fetch(`${import.meta.env.VITE_API_BASE || ''}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Token ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  })

  if (response.status === 204) {
    return null
  }

  const payload = await response.json()

  if (!response.ok) {
    throw new Error(payload.detail || 'Request failed.')
  }

  return payload
}
