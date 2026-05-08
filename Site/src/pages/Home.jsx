import React, { useState, useEffect, useCallback } from 'react';
import ListingCard from '../components/ListingCard';
import SearchForm from '../components/SearchForm';
import { searchListings } from '../services/listings';
import './Home.css';

const PAGE_SIZE = 20;

const INITIAL_FILTERS = {
    query: '', city: '', minPrice: '', maxPrice: '', minArea: '', maxArea: '',
    rooms: null, floor: '', dealTypeId: '', propertyTypeId: '', renovationId: '',
    sortBy: 'date_desc'
};

function Home() {
    const [listings, setListings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [filters, setFilters] = useState(INITIAL_FILTERS);

    const loadListings = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await searchListings(filters, page, PAGE_SIZE);
            setListings((prev) => page === 1 ? data.items || [] : [...prev, ...(data.items || [])]);
            setTotal(data.total || 0);
        } catch {
            setError('Не удалось загрузить объявления');
            if (page === 1) setListings([]);
        } finally {
            setLoading(false);
        }
    }, [filters, page]);

    useEffect(() => {
        loadListings();
    }, [loadListings]);

    const handleFilterChange = useCallback((newFilters) => {
        setFilters(newFilters);
        setPage(1);
        setListings([]);
    }, []);

    const handleLoadMore = useCallback(() => {
        setPage((p) => p + 1);
    }, []);

    const totalPages = Math.ceil(total / PAGE_SIZE);
    const hasMore = page < totalPages;

    return (
        <div>
            <SearchForm filters={filters} onFilterChange={handleFilterChange} />

            <div className="results-info">
                <p>Найдено {total} объявлений</p>
            </div>

            {error && <div className="error">{error}</div>}

            {loading && page === 1 ? (
                <div className="loader">Загрузка объявлений...</div>
            ) : (
                <>
                    <div className="listings-grid">
                        {listings.map((listing) => (
                            <ListingCard key={listing.listing_id} listing={listing} />
                        ))}
                    </div>

                    {listings.length === 0 && !loading && (
                        <div className="no-results">
                            <p>😕 Объявлений не найдено</p>
                            <p>Попробуйте изменить параметры поиска</p>
                        </div>
                    )}

                    {hasMore && (
                        <div className="load-more">
                            <button onClick={handleLoadMore} disabled={loading}>
                                {loading ? 'Загрузка...' : 'Показать ещё'}
                            </button>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}

export default Home;