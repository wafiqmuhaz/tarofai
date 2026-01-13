function SourceCitation({ source }) {
    const getDomainIcon = (domain) => {
        const icons = {
            'konsultasisyariah.com': '📖',
            'rumaysho.com': '📚',
            'almanhaj.or.id': '🕌',
            'salafycirebon.com': '📜'
        }
        return icons[domain] || '📄'
    }

    return (
        <div className="source-item">
            <div className="source-icon">
                {getDomainIcon(source.domain)}
            </div>
            <div className="source-content">
                <div className="source-title">{source.title || 'Artikel'}</div>
                <div className="source-domain">{source.domain}</div>
            </div>
            <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="source-link"
            >
                Kunjungi →
            </a>
        </div>
    )
}

export default SourceCitation
