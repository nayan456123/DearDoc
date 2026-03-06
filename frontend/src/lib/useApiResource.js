import { useEffect, useState } from 'react'
import { apiRequest } from './api'

export function useApiResource(path, token, initialValue) {
  const [data, setData] = useState(initialValue)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    if (!token) {
      setLoading(false)
      return
    }

    let ignore = false

    async function load() {
      setLoading(true)
      setError('')
      try {
        const next = await apiRequest(path, { token })
        if (!ignore) {
          setData(next)
        }
      } catch (requestError) {
        if (!ignore) {
          setError(requestError.message)
        }
      } finally {
        if (!ignore) {
          setLoading(false)
        }
      }
    }

    load()

    return () => {
      ignore = true
    }
  }, [path, reloadKey, token])

  return {
    data,
    loading,
    error,
    refetch: () => setReloadKey((current) => current + 1),
  }
}
