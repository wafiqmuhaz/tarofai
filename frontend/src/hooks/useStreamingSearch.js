import { useState, useCallback, useRef } from 'react'

/**
 * Custom React hook for streaming search with SSE.
 * 
 * Handles Server-Sent Events from the backend and provides
 * real-time token streaming for typing effect.
 */
export function useStreamingSearch() {
    const [answer, setAnswer] = useState('')
    const [sources, setSources] = useState([])
    const [status, setStatus] = useState(null)
    const [isStreaming, setIsStreaming] = useState(false)
    const [error, setError] = useState(null)
    const [metadata, setMetadata] = useState(null)
    
    const abortControllerRef = useRef(null)

    const cancelStream = useCallback(() => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort()
            abortControllerRef.current = null
        }
        setIsStreaming(false)
    }, [])

    const search = useCallback(async (query) => {
        // Cancel any existing stream
        cancelStream()
        
        // Reset state
        setAnswer('')
        setSources([])
        setStatus({ stage: 'starting', message: 'Memulai pencarian...' })
        setIsStreaming(true)
        setError(null)
        setMetadata(null)
        
        // Create new AbortController
        abortControllerRef.current = new AbortController()
        
        try {
            const response = await fetch('/api/search-stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query }),
                signal: abortControllerRef.current.signal
            })
            
            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`)
            }
            
            const reader = response.body.getReader()
            const decoder = new TextDecoder()
            let buffer = ''
            
            while (true) {
                const { done, value } = await reader.read()
                
                if (done) break
                
                buffer += decoder.decode(value, { stream: true })
                
                // Parse SSE events from buffer
                const lines = buffer.split('\n')
                buffer = lines.pop() || '' // Keep incomplete line in buffer
                
                let currentEvent = null
                
                for (const line of lines) {
                    if (line.startsWith('event: ')) {
                        currentEvent = line.slice(7)
                    } else if (line.startsWith('data: ') && currentEvent) {
                        try {
                            const data = JSON.parse(line.slice(6))
                            
                            switch (currentEvent) {
                                case 'status':
                                    setStatus(data)
                                    break
                                case 'token':
                                    setAnswer(prev => prev + data.content)
                                    break
                                case 'sources':
                                    setSources(data.sources || [])
                                    break
                                case 'done':
                                    setMetadata(data)
                                    setIsStreaming(false)
                                    setStatus(null)
                                    break
                                case 'error':
                                    setError(data.message)
                                    setIsStreaming(false)
                                    setStatus(null)
                                    break
                            }
                        } catch (e) {
                            console.error('Failed to parse SSE data:', e)
                        }
                        currentEvent = null
                    }
                }
            }
        } catch (err) {
            if (err.name === 'AbortError') {
                // Request was cancelled, don't show error
                return
            }
            console.error('Streaming search error:', err)
            setError(err.message || 'Terjadi kesalahan saat mencari.')
            setIsStreaming(false)
            setStatus(null)
        }
    }, [cancelStream])

    return {
        answer,
        sources,
        status,
        isStreaming,
        error,
        metadata,
        search,
        cancelStream
    }
}

export default useStreamingSearch
