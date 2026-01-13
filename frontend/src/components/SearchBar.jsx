import { useState } from 'react'

function SearchBar({ onSearch, loading }) {
    const [query, setQuery] = useState('')

    const handleSubmit = (e) => {
        e.preventDefault()
        if (query.trim() && !loading) {
            onSearch(query)
        }
    }

    return (
        <form className="search-form" onSubmit={handleSubmit}>
            <div className="search-container">
                <input
                    type="text"
                    className="search-input"
                    placeholder="Tanyakan tentang Islam... contoh: Bagaimana hukum sholat jumat?"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    disabled={loading}
                />
                <button
                    type="submit"
                    className={`search-button ${loading ? 'loading' : ''}`}
                    disabled={loading || !query.trim()}
                >
                    {loading ? (
                        <>
                            <span className="loading-spinner"></span>
                            Mencari...
                        </>
                    ) : (
                        <>
                            🔍 Cari
                        </>
                    )}
                </button>
            </div>
        </form>
    )
}

export default SearchBar
