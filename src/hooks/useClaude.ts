import { useCallback, useState } from 'react'
import { callClaude } from '@/lib/claude'

interface State {
  isGenerating: boolean
  error: string | null
  output: string
}

export function useClaude(apiKey: string) {
  const [state, setState] = useState<State>({
    isGenerating: false,
    error: null,
    output: '',
  })

  const generate = useCallback(
    async (userPrompt: string, maxTokens?: number): Promise<string | null> => {
      if (!apiKey) {
        setState({
          isGenerating: false,
          error: 'API key missing — add it in Settings.',
          output: '',
        })
        return null
      }
      setState({ isGenerating: true, error: null, output: '' })
      try {
        const output = await callClaude({ apiKey, userPrompt, maxTokens })
        setState({ isGenerating: false, error: null, output })
        return output
      } catch (err) {
        const message =
          err instanceof Error
            ? err.message === 'API_KEY_MISSING'
              ? 'API key missing — add it in Settings.'
              : err.message
            : 'Unknown error'
        setState({ isGenerating: false, error: message, output: '' })
        return null
      }
    },
    [apiKey],
  )

  const reset = useCallback(() => {
    setState({ isGenerating: false, error: null, output: '' })
  }, [])

  return { ...state, generate, reset }
}
