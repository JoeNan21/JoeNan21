import { useCallback, useEffect, useState } from 'react'
import type { RoomBlock, Settings } from '@/types'
import { KEYS, readJSON, readString, writeJSON, writeString } from '@/lib/storage'

const DEFAULT_SETTINGS: Settings = {
  operatorName: 'Joey',
  venueName: 'Sorrento in the Park',
  apiKey: '',
  monthlyTargets: {},
  roomBlocks: [],
}

function loadInitial(): Settings {
  const base = readJSON<Omit<Settings, 'apiKey'>>(KEYS.settings, {
    operatorName: DEFAULT_SETTINGS.operatorName,
    venueName: DEFAULT_SETTINGS.venueName,
    monthlyTargets: DEFAULT_SETTINGS.monthlyTargets,
    roomBlocks: DEFAULT_SETTINGS.roomBlocks,
  })
  const apiKey = readString(KEYS.apiKey, '')
  return { ...DEFAULT_SETTINGS, ...base, apiKey }
}

export function useSettings() {
  const [settings, setSettings] = useState<Settings>(() => loadInitial())

  useEffect(() => {
    const { apiKey, ...rest } = settings
    writeJSON(KEYS.settings, rest)
    writeString(KEYS.apiKey, apiKey)
  }, [settings])

  const update = useCallback((patch: Partial<Settings>) => {
    setSettings((prev) => ({ ...prev, ...patch }))
  }, [])

  const setTarget = useCallback((monthKey: string, value: number) => {
    setSettings((prev) => ({
      ...prev,
      monthlyTargets: { ...prev.monthlyTargets, [monthKey]: value },
    }))
  }, [])

  const addRoomBlock = useCallback((block: RoomBlock) => {
    setSettings((prev) => ({ ...prev, roomBlocks: [...prev.roomBlocks, block] }))
  }, [])

  const removeRoomBlock = useCallback((id: string) => {
    setSettings((prev) => ({
      ...prev,
      roomBlocks: prev.roomBlocks.filter((b) => b.id !== id),
    }))
  }, [])

  return { settings, update, setTarget, addRoomBlock, removeRoomBlock }
}

export function maskKey(key: string): string {
  if (!key) return ''
  if (key.length <= 4) return '••••'
  return `••••••••${key.slice(-4)}`
}
