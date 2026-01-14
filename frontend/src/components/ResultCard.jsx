import SourceCitation from './SourceCitation'

function ResultCard({ query, answer, sources, cached, intent, processingTime, isStreaming }) {
    const getIntentLabel = (intent) => {
        const labels = {
            'definisi': 'Definisi',
            'hukum': 'Hukum Syar\'i',
            'konsekuensi': 'Konsekuensi',
            'dalil': 'Dalil',
            'cara': 'Tata Cara',
            'syarat': 'Syarat & Rukun',
            'general': 'Umum'
        }
        return labels[intent] || 'Umum'
    }

    const getIntentColor = (intent) => {
        const colors = {
            'definisi': '#3b82f6',
            'hukum': '#22c55e',
            'konsekuensi': '#f97316',
            'dalil': '#a855f7',
            'cara': '#06b6d4',
            'syarat': '#eab308',
            'general': '#6b7280'
        }
        return colors[intent] || '#6b7280'
    }

    // Format answer with markdown-like styling
    const formatAnswer = (text) => {
        return text
            .replace(/^## (.+)$/gm, '<h3 style="color:#38bdf8;margin:1rem 0 0.5rem;font-size:1.1rem;">$1</h3>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br/>')
    }

    return (
        <div className={`result-card ${cached ? 'cached' : ''}`}>
            {/* Inline styles for streaming cursor */}
            <style>{`
                @keyframes blink {
                    0%, 50% { opacity: 1; }
                    51%, 100% { opacity: 0; }
                }
                .streaming-cursor {
                    display: inline-block;
                    width: 2px;
                    height: 1.2em;
                    background: #38bdf8;
                    margin-left: 2px;
                    vertical-align: text-bottom;
                    animation: blink 1s infinite;
                }
            `}</style>

            <div className="result-header">
                {query && <span className="result-query">Pertanyaan: {query}</span>}
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    {intent && (
                        <span
                            style={{
                                padding: '4px 10px',
                                borderRadius: '12px',
                                fontSize: '11px',
                                fontWeight: '600',
                                backgroundColor: getIntentColor(intent) + '20',
                                color: getIntentColor(intent),
                            }}
                        >
                            {getIntentLabel(intent)}
                        </span>
                    )}
                    {cached && <span className="cached-badge">Cached</span>}
                    {processingTime > 0 && !isStreaming && (
                        <span style={{
                            fontSize: '11px',
                            color: '#6b7280',
                            fontFamily: 'monospace'
                        }}>
                            {processingTime.toFixed(2)}s
                        </span>
                    )}
                    {isStreaming && (
                        <span style={{
                            fontSize: '11px',
                            color: '#38bdf8',
                            fontFamily: 'monospace'
                        }}>
                            streaming...
                        </span>
                    )}
                </div>
            </div>

            <div className="result-answer">
                <span dangerouslySetInnerHTML={{ __html: formatAnswer(answer) }} />
                {isStreaming && <span className="streaming-cursor"></span>}
            </div>

            {sources && sources.length > 0 && !isStreaming && (
                <div className="sources-section">
                    <h3 className="sources-title">Referensi Sumber ({sources.length})</h3>
                    <div className="sources-list">
                        {sources.map((source, index) => (
                            <SourceCitation key={index} source={source} />
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}

export default ResultCard
