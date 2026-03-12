import React, { useState, useEffect } from 'react';
import ListingCard from '../components/ListingCard';
import SearchForm from '../components/SearchForm';
import { getAllListings, searchListings } from '../services/listings';
import './Home.css';

function Home() {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    city: '',
    dealType: 'sale',
    minPrice: '',
    maxPrice: '',
    rooms: ''
  });

  // Загрузка при первом открытии
  useEffect(() => {
    loadAllListings();
  }, []);

  // Загрузка при изменении фильтров
  useEffect(() => {
    // Не загружаем при первом рендере (уже загрузили)
    if (loading) return;

    // Добавляем небольшую задержку чтобы не спамить запросами
    const timer = setTimeout(() => {
      loadFilteredListings();
    }, 500);

    return () => clearTimeout(timer);
  }, [filters]);

  const loadAllListings = async () => {
    setLoading(true);
    try {
      const data = await getAllListings();
      setListings(data);
      setError(null);
    } catch (err) {
      setError('Не удалось загрузить объявления');
    } finally {
      setLoading(false);
    }
  };

  const loadFilteredListings = async () => {
    // Проверяем, есть ли активные фильтры
    const hasFilters = filters.city || filters.minPrice || filters.maxPrice || filters.rooms;

    if (!hasFilters) {
      loadAllListings();
      return;
    }

    setLoading(true);
    try {
      const data = await searchListings(filters);
      setListings(data);
      setError(null);
    } catch (err) {
      setError('Ошибка при поиске');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  // Проверка подключения к бэкенду
  if (error?.includes('Network Error')) {
    return (
      <div className="error-container">
        <h2>❌ Бэкенд не запущен!</h2>
        <p>Запустите сервер командой:</p>
        <code>cd backend && python run.py</code>
      </div>
    );
  }

  return (
    <div className="home-page">
      <h1>Поиск недвижимости</h1>

      <SearchForm
        filters={filters}
        onFilterChange={handleFilterChange}
      />

      {error && <div className="error">{error}</div>}

      {loading ? (
        <div className="loader">Загрузка объявлений...</div>
      ) : (
        <>
          <div className="results-info">
            <p>Найдено {listings.length} объявлений</p>
          </div>

          {listings.length === 0 ? (
            <div className="no-results">
              <p>😕 Объявлений не найдено</p>
              <p>Попробуйте изменить параметры поиска</p>
            </div>
          ) : (
            <div className="listings-grid">
              {listings.map(listing => (
                <ListingCard key={listing.listing_id} listing={listing} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Home;