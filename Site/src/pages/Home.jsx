import React, { useState, useEffect } from 'react';
import ListingCard from '../components/ListingCard';
import SearchForm from '../components/SearchForm';
import { searchListings } from '../services/listings';
import './Home.css';

function Home() {
    const [listings, setListings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [filters, setFilters] = useState({
        query: '', city: '', minPrice: '', maxPrice: '', minArea: '', maxArea: '',
        rooms: null, floor: '', maxFloor: '', renovationId: '', propertyTypeId: '', dealTypeId: '', sortBy: 'date_desc'
    });

    useEffect(() => {
        loadListings();
    }, [filters, page]);

    const loadListings = async () => {
        setLoading(true);
        setError(null);

        try {
            const data = await searchListings(filters, page, 20);
            setListings(data.items || []);
            setTotal(data.total || 0);
        } catch (err) {
            setError('Не удалось загрузить объявления');
            setListings([]);
        } finally {
            setLoading(false);
        }
    };

    const handleFilterChange = (newFilters) => {
        setFilters(newFilters);
        setPage(1);
    };

    const totalPages = Math.ceil(total / 20);

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
                        {listings.map(listing => (
                            <ListingCard key={listing.listing_id} listing={listing} />
                        ))}
                    </div>

                    {listings.length === 0 && !loading && (
                        <div className="no-results">
                            <p>😕 Объявлений не найдено</p>
                            <p>Попробуйте изменить параметры поиска</p>
                        </div>
                    )}

                    {page < totalPages && (
                        <div className="load-more">
                            <button onClick={() => setPage(p => p + 1)} disabled={loading}>
                                {loading ? 'Загрузка...' : 'Показать еще'}
                            </button>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}

export default Home;