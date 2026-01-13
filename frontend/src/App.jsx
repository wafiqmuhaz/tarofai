import { useState } from 'react'
import SearchBar from './components/SearchBar'
import ResultCard from './components/ResultCard'

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
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [lastQuery, setLastQuery] = useState('')

    const handleSearch = async (query) => {
        if (!query.trim()) return

        setLoading(true)
        setError(null)
        setLastQuery(query)

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query }),
            })

            if (!response.ok) {
                throw new Error('Pencarian gagal. Silakan coba lagi.')
            }

            const data = await response.json()
            setResult(data)
        } catch (err) {
            setError(err.message || 'Terjadi kesalahan. Silakan coba lagi.')
        } finally {
            setLoading(false)
        }
    }

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
                <SearchBar onSearch={handleSearch} loading={loading} />
            </section>

            <section className="results-section">
                {error && <div className="error-message">⚠️ {error}</div>}

                {result && !loading && (
                    <ResultCard
                        query={lastQuery}
                        answer={result.answer}
                        sources={result.sources}
                        cached={result.cached}
                    />
                )}

                {!result && !loading && !error && (
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
