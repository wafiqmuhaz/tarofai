import SearchBar from './components/SearchBar'
import ResultCard from './components/ResultCard'
import useStreamingSearch from './hooks/useStreamingSearch'

const APPROVED_SOURCES = [
    "salafipublications.com",
    "salaf.com",
    "sunnisalafi.com",
    "madeenah.org",
    "aqidah.com",
    "tawhidfirst.com",
    "abovethethrone.com",
    "fiqhonline.com",
    "manhaj.com",
    "piousmuslim.com",
    "albani.co.uk",
    "binbaz.co.uk",
    "fawzan.co.uk",
    "rabee.co.uk",
    "muqbil.co.uk",
    "ubayd.co.uk",
    "ibntaymiyyah.com",
    "islamqa.info",
    "rodja.tv",
    "radiorodja.com",
    "yufid.com",
    "yufid.tv",
    "muslim.or.id",
    "kajian.net",
    "ngaji.org",
    "islamdownload.net",
    "almanhaj.or.id",
    "rumaysho.com",
    "muslimah.or.id",
    "konsultasisyariah.com",
    "salafycirebon.com",
]

function App() {
    const {
        answer,
        sources,
        status,
        isStreaming,
        error,
        metadata,
        search
    } = useStreamingSearch()

    const handleSearch = (query) => {
        if (!query.trim()) return
        search(query)
    }

    // Determine if we should show content
    const hasContent = answer || sources.length > 0
    const isLoading = isStreaming && !answer

    return (
        <div className="app">
            {/* ===== INLINE CSS ===== */}
            <style>{`
                .footer {
                    padding: 16px;
                    background: #0f172a;
                    color: #e5e7eb;
                    overflow: hidden;
                }

                .scroll-wrapper {
                    overflow: hidden;
                    white-space: nowrap;
                    width: 100%;
                }

                .scroll-track {
                    display: inline-flex;
                    gap: 12px;
                    animation: scroll-left 40s linear infinite;
                }

                .approved-source-badge {
                    padding: 6px 14px;
                    background: #1e293b;
                    border-radius: 999px;
                    font-size: 13px;
                    color: #38bdf8;
                    white-space: nowrap;
                }

                @keyframes scroll-left {
                    0% {
                        transform: translateX(0);
                    }
                    100% {
                        transform: translateX(-50%);
                    }
                }

                .status-indicator {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    padding: 16px 24px;
                    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                    border-radius: 12px;
                    color: #e5e7eb;
                    margin-bottom: 16px;
                    border: 1px solid #334155;
                }

                .status-spinner {
                    width: 20px;
                    height: 20px;
                    border: 2px solid #334155;
                    border-top-color: #38bdf8;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                }

                @keyframes spin {
                    to { transform: rotate(360deg); }
                }

                .status-text {
                    font-size: 14px;
                    opacity: 0.9;
                }
            `}</style>

            <header className="header">
                <div className="logo">
                    <div className="logo-icon">🕌</div>
                    <h1 className="logo-text">Tarofa</h1>
                </div>
                <p className="tagline">Mesin Pencari Islam dengan AI</p>
                <p className="tagline-arabic">
                    بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
                </p>
            </header>

            <section className="search-section">
                <SearchBar onSearch={handleSearch} loading={isLoading} />
            </section>

            <section className="results-section">
                {error && <div className="error-message">⚠️ {error}</div>}

                {/* Status indicator during processing */}
                {status && (
                    <div className="status-indicator">
                        <div className="status-spinner"></div>
                        <span className="status-text">{status.message}</span>
                    </div>
                )}

                {hasContent && (
                    <ResultCard
                        query=""
                        answer={answer}
                        sources={sources}
                        cached={metadata?.cached || false}
                        intent={metadata?.intent}
                        processingTime={metadata?.processing_time}
                        isStreaming={isStreaming}
                    />
                )}

                {!hasContent && !isStreaming && !error && (
                    <div className="empty-state">
                        <div className="empty-icon">📚</div>
                        <p>Ajukan pertanyaan seputar Islam</p>
                        <p style={{ fontSize: '0.9rem', marginTop: '0.5rem', opacity: 0.7 }}>
                            Jawaban diambil dari sumber-sumber Salafi terpercaya
                        </p>
                    </div>
                )}
            </section>

            {/* ===== AUTO SCROLL FOOTER ===== */}
            <footer className="footer">
                <p>Sumber data terpercaya:</p>
                <div className="scroll-wrapper">
                    <div className="scroll-track">
                        {[...APPROVED_SOURCES, ...APPROVED_SOURCES].map((site, i) => (
                            <span key={i} className="approved-source-badge">
                                {site}
                            </span>
                        ))}
                    </div>
                </div>
            </footer>
        </div>
    )
}

export default App

