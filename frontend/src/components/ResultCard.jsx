import SourceCitation from './SourceCitation'

function ResultCard({ query, answer, sources, cached, intent, processingTime }) {
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

    return (
        <div className={`result-card ${cached ? 'cached' : ''}`}>
            <div className="result-header">
                <span className="result-query">Pertanyaan: {query}</span>
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
                    {processingTime > 0 && (
                        <span style={{
                            fontSize: '11px',
                            color: '#6b7280',
                            fontFamily: 'monospace'
                        }}>
                            {processingTime.toFixed(2)}s
                        </span>
                    )}
                </div>
            </div>

            <div className="result-answer" dangerouslySetInnerHTML={{
                __html: answer
                    .replace(/^## (.+)$/gm, '<h3 style="color:#38bdf8;margin:1rem 0 0.5rem;font-size:1.1rem;">$1</h3>')
                    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\n/g, '<br/>')
            }} />

            {sources && sources.length > 0 && (
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
