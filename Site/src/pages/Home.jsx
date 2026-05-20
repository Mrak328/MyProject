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
    const [sortOpen, setSortOpen] = useState(false);

    const loadListings = useCallback(async (currentFilters, currentPage) => {
        setLoading(true);
        setError(null);
        try {
            const data = await searchListings(currentFilters || filters, currentPage || page, PAGE_SIZE);
            if (currentPage === 1 || !currentPage) {
                setListings(data.items || []);
            } else {
                setListings(prev => [...prev, ...(data.items || [])]);
            }
            setTotal(data.total || 0);
        } catch {
            setError('Не удалось загрузить объявления');
        } finally {
            setLoading(false);
        }
    }, [filters, page]);

    useEffect(() => {
        loadListings(filters, 1);
    }, []);

    const handleFilterChange = useCallback((newFilters) => {
        setFilters(newFilters);
    }, []);

    const handleSearch = useCallback((searchFilters) => {
        setFilters(searchFilters);
        setPage(1);
        setListings([]);
        loadListings(searchFilters, 1);
    }, [loadListings]);

    const handleSort = useCallback((sortBy) => {
        const updated = { ...filters, sortBy };
        setFilters(updated);
        setPage(1);
        setListings([]);
        loadListings(updated, 1);
    }, [filters, loadListings]);

    const handleLoadMore = useCallback(() => {
        const nextPage = page + 1;
        setPage(nextPage);
        loadListings(filters, nextPage);
    }, [page, filters, loadListings]);

    const totalPages = Math.ceil(total / PAGE_SIZE);
    const hasMore = page < totalPages;

    return (
        <div className="home-page">
            <SearchForm
                filters={filters}
                onFilterChange={handleFilterChange}
                onSearch={handleSearch}
            />

            {/* Выдвижной блок сортировки — такой же стиль как SearchForm */}
            <div className="sort-container">
                <div className="sort-bar-header">
                    <button type="button" className={`toggle-sort-btn ${sortOpen ? 'open' : ''}`} onClick={() => setSortOpen(!sortOpen)}>
                        Сортировка: {filters.sortBy === 'date_desc' ? 'Новые' : filters.sortBy === 'price_asc' ? 'Дешевле' : filters.sortBy === 'price_desc' ? 'Дороже' : 'Популярные'} <span className="arrow">▼</span>
                    </button>
                    <span className="sort-count">Найдено {total} объявлений</span>
                </div>

                <div className={`sort-wrapper ${sortOpen ? 'open' : ''}`}>
                    <div className="sort-row">
                        <button className={filters.sortBy === 'date_desc' ? 'active' : ''} onClick={() => handleSort('date_desc')}>🆕 Новые</button>
                        <button className={filters.sortBy === 'price_asc' ? 'active' : ''} onClick={() => handleSort('price_asc')}>💰 Дешевле</button>
                        <button className={filters.sortBy === 'price_desc' ? 'active' : ''} onClick={() => handleSort('price_desc')}>💎 Дороже</button>
                        <button className={filters.sortBy === 'views_desc' ? 'active' : ''} onClick={() => handleSort('views_desc')}>🔥 Популярные</button>
                    </div>
                </div>
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