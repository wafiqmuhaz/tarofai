import SourceCitation from './SourceCitation'

function ResultCard({ query, answer, sources, cached }) {
    return (
        <div className={`result-card ${cached ? 'cached' : ''}`}>
            <div className="result-header">
                <span className="result-query">Pertanyaan: {query}</span>
                {cached && <span className="cached-badge">Cached</span>}
            </div>

            <div className="result-answer">
                {answer}
            </div>

            {sources && sources.length > 0 && (
                <div className="sources-section">
                    <h3 className="sources-title">Referensi Sumber</h3>
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
