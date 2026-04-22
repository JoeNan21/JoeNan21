const PREFIX = 'caos_'

export const KEYS = {
  leads: `${PREFIX}leads`,
  settings: `${PREFIX}settings`,
  apiKey: `${PREFIX}api_key`,
  bootstrapped: `${PREFIX}bootstrapped`,
} as const

export function readJSON<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    if (!raw) return fallback
    return JSON.parse(raw) as T
  } catch {
    return fallback
  }
}

export function writeJSON<T>(key: string, value: T): void {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {
    // quota or availability — swallow, caller shouldn't crash UI
  }
}

export function readString(key: string, fallback = ''): string {
  try {
    return localStorage.getItem(key) ?? fallback
  } catch {
    return fallback
  }
}

export function writeString(key: string, value: string): void {
  try {
    localStorage.setItem(key, value)
  } catch {
    // swallow
  }
}

export function removeKey(key: string): void {
  try {
    localStorage.removeItem(key)
  } catch {
    // swallow
  }
}
