function SourceCitation({ source }) {
    const getDomainIcon = (domain) => {
        const icons = {
            'konsultasisyariah.com': '📖',
            'rumaysho.com': '📚',
            'almanhaj.or.id': '🕌',
            'salafycirebon.com': '📜',
            'islamqa.info': '🔍',
            'muslim.or.id': '📿',
            'yufid.com': '🎓',
            'muslimah.or.id': '👩',
        }
        return icons[domain] || '📄'
    }

    const getConfidenceColor = (confidence) => {
        if (confidence >= 0.8) return '#22c55e' // green
        if (confidence >= 0.6) return '#eab308' // yellow
        return '#f97316' // orange
    }

    const getConfidenceLabel = (confidence) => {
        if (confidence >= 0.8) return 'Sangat Relevan'
        if (confidence >= 0.6) return 'Relevan'
        return 'Referensi Umum'
    }

    const confidence = source.confidence || 0.5
    const isSpecific = source.source_type === 'specific_article'

    return (
        <div className="source-item">
            <div className="source-icon">
                {getDomainIcon(source.domain)}
            </div>
            <div className="source-content">
                <div className="source-title">{source.title || 'Artikel'}</div>
                <div className="source-domain">
                    {source.domain}
                    <span
                        style={{
                            marginLeft: '8px',
                            padding: '2px 8px',
                            borderRadius: '12px',
                            fontSize: '11px',
                            fontWeight: '600',
                            backgroundColor: getConfidenceColor(confidence) + '20',
                            color: getConfidenceColor(confidence),
                        }}
                    >
                        {isSpecific ? '✓ ' : ''}{getConfidenceLabel(confidence)}
                    </span>
                </div>
            </div>
            <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="source-link"
            >
                Baca →
            </a>
        </div>
    )
}

export default SourceCitation
