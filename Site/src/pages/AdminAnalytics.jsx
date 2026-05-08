import React, { useState, useEffect, useCallback } from 'react';
import API from '../services/api';
import './AdminAnalytics.css';

const PERIOD_OPTIONS = [
    { value: 'day', label: 'День' },
    { value: 'week', label: 'Неделя' },
    { value: 'month', label: 'Месяц' }
];

const INITIAL_DASHBOARD = { total_listings: 0, active_today: 0, views_today: 0, new_listings_today: 0 };
const INITIAL_PRICE_STATS = { total_active: 0, avg_price: 0, avg_price_per_m2: 0, min_price: 0, max_price: 0, price_ranges: {}, by_type: [] };
const INITIAL_VIEWS_STATS = { total_views: 0, unique_listings: 0, unique_visitors: 0, views_by_day: [] };
const INITIAL_SEARCH = { popular_queries: [] };
const INITIAL_CLOSED_DEALS = { total_closed: 0, total_revenue: 0, avg_days_to_sell: 0, by_type: [] };

function AdminAnalytics() {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [period, setPeriod] = useState('week');

    const [dashboard, setDashboard] = useState(INITIAL_DASHBOARD);
    const [popularListings, setPopularListings] = useState([]);
    const [searchQueries, setSearchQueries] = useState(INITIAL_SEARCH);
    const [priceStats, setPriceStats] = useState(INITIAL_PRICE_STATS);
    const [viewsStats, setViewsStats] = useState(INITIAL_VIEWS_STATS);
    const [closedDeals, setClosedDeals] = useState(INITIAL_CLOSED_DEALS);

    const loadAllAnalytics = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const [dashRes, popularRes, searchRes, viewsRes, priceRes, closedRes] = await Promise.all([
                API.get('/analytics/dashboard'),
                API.get(`/analytics/listings/popular?period=${period}&limit=10`),
                API.get('/analytics/search/queries?days=30'),
                API.get(`/analytics/views?period=${period}`),
                API.get('/analytics/prices'),
                API.get(`/analytics/deals/closed?period=${period === 'day' ? 'week' : period}`)
            ]);

            setDashboard(dashRes.data || INITIAL_DASHBOARD);
            setPopularListings(popularRes.data || []);
            setSearchQueries(searchRes.data || INITIAL_SEARCH);
            setViewsStats(viewsRes.data || INITIAL_VIEWS_STATS);
            setPriceStats(priceRes.data || INITIAL_PRICE_STATS);
            setClosedDeals(closedRes.data || INITIAL_CLOSED_DEALS);
        } catch (err) {
            setError('Не удалось загрузить аналитику');
        } finally {
            setLoading(false);
        }
    }, [period]);

    useEffect(() => {
        loadAllAnalytics();
    }, [loadAllAnalytics]);

    const formatNumber = (num) => (num ?? 0).toLocaleString('ru-RU');

    if (loading) return <div className="loader">Загрузка аналитики...</div>;
    if (error) return <div className="error">{error}</div>;

    return (
        <div className="analytics-page">
            <h1>Аналитика</h1>

            <div className="period-selector">
                {PERIOD_OPTIONS.map((opt) => (
                    <button
                        key={opt.value}
                        className={period === opt.value ? 'active' : ''}
                        onClick={() => setPeriod(opt.value)}
                    >
                        {opt.label}
                    </button>
                ))}
            </div>

            {/* Метрики */}
            <div className="metrics-grid">
                <div className="metric-card">
                    <h3>Всего объявлений</h3>
                    <p className="metric-value">{dashboard.total_listings}</p>
                </div>
                <div className="metric-card">
                    <h3>Активных сегодня</h3>
                    <p className="metric-value">{dashboard.active_today}</p>
                </div>
                <div className="metric-card">
                    <h3>Просмотров сегодня</h3>
                    <p className="metric-value">{dashboard.views_today}</p>
                </div>
                <div className="metric-card">
                    <h3>Новых сегодня</h3>
                    <p className="metric-value">{dashboard.new_listings_today}</p>
                </div>
            </div>

            {/* Просмотры */}
            <div className="analytics-card">
                <h2>Статистика просмотров</h2>
                <div className="stats-grid">
                    <div className="stat-item highlight">
                        <span className="stat-label">Всего просмотров:</span>
                        <span className="stat-value large">{formatNumber(viewsStats.total_views)}</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Уникальных объявлений:</span>
                        <span className="stat-value">{viewsStats.unique_listings}</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Уникальных посетителей:</span>
                        <span className="stat-value">{viewsStats.unique_visitors}</span>
                    </div>
                </div>
                {viewsStats.views_by_day?.length > 0 && (
                    <div className="mini-stats">
                        {viewsStats.views_by_day.map((day, idx) => (
                            <div key={idx} className="mini-stat-item">
                                <span className="mini-stat-date">{day.date}</span>
                                <span className="mini-stat-count">{day.views}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Цены */}
            <div className="analytics-card">
                <h2>Статистика цен</h2>
                <div className="stats-grid">
                    <div className="stat-item highlight">
                        <span className="stat-label">Всего активных:</span>
                        <span className="stat-value large">{priceStats.total_active}</span>
                    </div>
                    <div className="stat-item highlight">
                        <span className="stat-label">Средняя цена:</span>
                        <span className="stat-value large">{formatNumber(priceStats.avg_price)} ₽</span>
                    </div>
                    <div className="stat-item highlight">
                        <span className="stat-label">Цена за м²:</span>
                        <span className="stat-value large">{formatNumber(priceStats.avg_price_per_m2)} ₽</span>
                    </div>
                </div>
                <div className="stats-mini-grid">
                    <div className="stat-mini-item">
                        <span className="stat-mini-label">Мин:</span>
                        <span className="stat-mini-value">{formatNumber(priceStats.min_price)} ₽</span>
                    </div>
                    <div className="stat-mini-item">
                        <span className="stat-mini-label">Макс:</span>
                        <span className="stat-mini-value">{formatNumber(priceStats.max_price)} ₽</span>
                    </div>
                </div>
                {priceStats.price_ranges && Object.keys(priceStats.price_ranges).length > 0 && (
                    <div className="price-ranges">
                        {Object.entries(priceStats.price_ranges).map(([range, count]) => (
                            <div key={range} className="price-range-item">
                                <span className="range-label">{range}:</span>
                                <span className="range-count">{count}</span>
                                <span className="range-percent">
                                    ({priceStats.total_active ? ((count / priceStats.total_active) * 100).toFixed(1) : 0}%)
                                </span>
                            </div>
                        ))}
                    </div>
                )}
                {priceStats.by_type?.length > 0 && (
                    <table className="stats-table">
                        <thead>
                            <tr>
                                <th>Тип</th>
                                <th>Кол-во</th>
                                <th>Средняя цена</th>
                            </tr>
                        </thead>
                        <tbody>
                            {priceStats.by_type.map((item, idx) => (
                                <tr key={idx}>
                                    <td><strong>{item.property_type}</strong></td>
                                    <td>{item.count}</td>
                                    <td>{formatNumber(item.avg_price)} ₽</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Закрытые сделки */}
            {closedDeals.total_closed > 0 && (
                <div className="analytics-card">
                    <h2>Закрытые сделки</h2>
                    <div className="stats-grid">
                        <div className="stat-item highlight">
                            <span className="stat-label">Продано:</span>
                            <span className="stat-value large">{closedDeals.total_closed}</span>
                        </div>
                        <div className="stat-item highlight">
                            <span className="stat-label">Выручка:</span>
                            <span className="stat-value large">{formatNumber(closedDeals.total_revenue)} ₽</span>
                        </div>
                        <div className="stat-item highlight">
                            <span className="stat-label">Среднее время:</span>
                            <span className="stat-value large">{closedDeals.avg_days_to_sell} дн</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Популярные + Поиск */}
            <div className="analytics-columns">
                <div className="analytics-card">
                    <h2>Популярные объявления</h2>
                    <div className="listings-list">
                        {popularListings?.length > 0 ? popularListings.map((item, i) => (
                            <div key={item.listing_id || i} className="listing-item">
                                <span className="rank">{i + 1}</span>
                                {item.photo && <img src={item.photo} alt="" className="listing-thumb" />}
                                <div className="listing-info">
                                    <h4>{item.title || 'Без названия'}</h4>
                                    <p>{item.address || 'Адрес не указан'}</p>
                                </div>
                                <div className="listing-stats">
                                    <span className="views">👁 {item.views}</span>
                                    <span className="price">{formatNumber(item.price)} ₽</span>
                                </div>
                            </div>
                        )) : <p className="no-data">Нет данных</p>}
                    </div>
                </div>

                <div className="analytics-card">
                    <h2>Поисковые запросы</h2>
                    <div className="queries-list">
                        {searchQueries.popular_queries?.length > 0 ? searchQueries.popular_queries.map((item, i) => (
                            <div key={i} className="query-item">
                                <span className="rank">{i + 1}</span>
                                <span className="query">"{item.query || 'пустой запрос'}"</span>
                                <span className="count">{item.count} раз</span>
                            </div>
                        )) : <p className="no-data">Нет данных</p>}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default AdminAnalytics;