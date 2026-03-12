import React, { useState, useEffect } from 'react';
import API from '../services/api';
import './AdminAnalytics.css';

function AdminAnalytics() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [period, setPeriod] = useState('week');

  // Данные с бэкенда
  const [dashboard, setDashboard] = useState(null);
  const [popularListings, setPopularListings] = useState([]);
  const [searchQueries, setSearchQueries] = useState([]);
  const [priceStats, setPriceStats] = useState(null);
  const [viewsStats, setViewsStats] = useState(null);
  const [closedDeals, setClosedDeals] = useState(null);

  useEffect(() => {
    loadAllAnalytics();
  }, [period]);

  const loadAllAnalytics = async () => {
    setLoading(true);
    setError(null);

    try {
      // Загружаем все эндпоинты
      const requests = [
        API.get('/analytics/analytics/dashboard?days=30'),
        API.get(`/analytics/analytics/listings/popular?period=${period}&limit=10`),
        API.get('/analytics/analytics/search/queries?days=7'),
        API.get('/analytics/analytics/prices'),
        API.get(`/analytics/analytics/views?period=${period}`),
      ];

      // Добавляем closed_deals только для недели и месяца (не для дня)
      if (period !== 'day') {
        requests.push(API.get(`/analytics/analytics/closed_deals?period=${period}`));
      } else {
        // Если день - добавляем заглушку
        requests.push(Promise.resolve({ data: {
          total_closed: 0,
          total_revenue: 0,
          avg_days_to_sell: 0,
          by_type: []
        }}));
      }

      const [dashboardData, popularData, searchData, priceData, viewsData, closedData] = await Promise.all(requests);

      setDashboard(dashboardData.data);
      setPopularListings(popularData.data || []);
      setSearchQueries(searchData.data?.popular_queries || []);
      setPriceStats(priceData.data);
      setViewsStats(viewsData.data);
      setClosedDeals(closedData.data);

    } catch (err) {
      console.error('Ошибка загрузки аналитики:', err);
      if (err.response) {
        console.error('Статус:', err.response.status);
        console.error('Данные:', err.response.data);
      }
      setError(`Не удалось загрузить данные аналитики: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Функция для безопасного форматирования чисел
  const formatNumber = (num) => {
    if (num === undefined || num === null) return '0';
    return num.toLocaleString('ru-RU');
  };

  // Функция для перевода периода на русский
  const getPeriodText = (period) => {
    switch(period) {
      case 'day': return 'день';
      case 'week': return 'неделю';
      case 'month': return 'месяц';
      default: return period;
    }
  };

  if (loading) return <div className="loader">📊 Загрузка аналитики...</div>;
  if (error) return <div className="error">❌ {error}</div>;

  return (
    <div className="analytics-page">
      <h1>📊 Аналитика</h1>

      {/* Кнопки периода */}
      <div className="period-selector">
        <button
          className={period === 'day' ? 'active' : ''}
          onClick={() => setPeriod('day')}
        >
          День
        </button>
        <button
          className={period === 'week' ? 'active' : ''}
          onClick={() => setPeriod('week')}
        >
          Неделя
        </button>
        <button
          className={period === 'month' ? 'active' : ''}
          onClick={() => setPeriod('month')}
        >
          Месяц
        </button>
      </div>

      {/* Dashboard метрики */}
      {dashboard && (
        <div className="metrics-grid">
          <div className="metric-card">
            <h3>Всего объявлений</h3>
            <p className="metric-value">{dashboard.total_listings || 0}</p>
          </div>
          <div className="metric-card">
            <h3>Активных сегодня</h3>
            <p className="metric-value">{dashboard.active_today || 0}</p>
          </div>
          <div className="metric-card">
            <h3>Просмотров сегодня</h3>
            <p className="metric-value">{dashboard.views_today || 0}</p>
          </div>
          <div className="metric-card">
            <h3>Новых сегодня</h3>
            <p className="metric-value">{dashboard.new_listings_today || 0}</p>
          </div>
        </div>
      )}

      {/* Статистика просмотров */}
      {viewsStats && (
        <div className="analytics-card">
          <h2>👁 Статистика просмотров за {getPeriodText(period)}</h2>
          <div className="stats-grid">
            <div className="stat-item highlight">
              <span className="stat-label">Всего просмотров:</span>
              <span className="stat-value large">{formatNumber(viewsStats.total_views)}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Уникальных объявлений:</span>
              <span className="stat-value">{viewsStats.unique_listings || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Уникальных посетителей:</span>
              <span className="stat-value">{viewsStats.unique_visitors || 0}</span>
            </div>
          </div>

          {/* Просмотры по дням */}
          {viewsStats.views_by_day && viewsStats.views_by_day.length > 0 && (
            <>
              <h3>Просмотры по дням</h3>
              <div className="mini-stats">
                {viewsStats.views_by_day.map((day, idx) => (
                  <div key={idx} className="mini-stat-item">
                    <span className="mini-stat-date">{day.date}</span>
                    <span className="mini-stat-count">{day.count}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* Детальная статистика цен */}
      {priceStats && (
        <div className="analytics-card">
          <h2>💰 Детальная статистика цен</h2>

          {/* Основные метрики */}
          <div className="stats-grid">
            <div className="stat-item highlight">
              <span className="stat-label">Всего активных:</span>
              <span className="stat-value large">{priceStats.total_active || 0}</span>
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

          {/* Минимальная и максимальная цена */}
          <div className="stats-mini-grid">
            <div className="stat-mini-item">
              <span className="stat-mini-label">Минимальная цена:</span>
              <span className="stat-mini-value">{formatNumber(priceStats.min_price)} ₽</span>
            </div>
            <div className="stat-mini-item">
              <span className="stat-mini-label">Максимальная цена:</span>
              <span className="stat-mini-value">{formatNumber(priceStats.max_price)} ₽</span>
            </div>
          </div>

          {/* Распределение по ценовым диапазонам */}
          {priceStats.price_ranges && (
            <>
              <h3>📊 Распределение по ценам</h3>
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
            </>
          )}

          {/* Статистика по типам */}
          {priceStats.by_type && priceStats.by_type.length > 0 && (
            <>
              <h3>🏠 По типам недвижимости</h3>
              <table className="stats-table">
                <thead>
                  <tr>
                    <th>Тип</th>
                    <th>Кол-во</th>
                    <th>Средняя цена</th>
                    <th>Мин</th>
                    <th>Макс</th>
                    <th>₽/м²</th>
                    <th>Общая стоимость</th>
                  </tr>
                </thead>
                <tbody>
                  {priceStats.by_type.map((item, idx) => (
                    <tr key={idx}>
                      <td><strong>{item.type}</strong></td>
                      <td>{item.count}</td>
                      <td>{formatNumber(item.avg_price)} ₽</td>
                      <td>{formatNumber(item.min_price)} ₽</td>
                      <td>{formatNumber(item.max_price)} ₽</td>
                      <td>{formatNumber(item.avg_price_per_m2)} ₽</td>
                      <td>{formatNumber(item.total_value)} ₽</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </div>
      )}

      {/* Закрытые сделки */}
      {closedDeals && closedDeals.total_closed > 0 && (
        <div className="analytics-card">
          <h2>✅ Закрытые сделки за {getPeriodText(period)}</h2>
          <div className="stats-grid">
            <div className="stat-item highlight">
              <span className="stat-label">Продано объектов:</span>
              <span className="stat-value large">{closedDeals.total_closed || 0}</span>
            </div>
            <div className="stat-item highlight">
              <span className="stat-label">Общая выручка:</span>
              <span className="stat-value large">{formatNumber(closedDeals.total_revenue)} ₽</span>
            </div>
            <div className="stat-item highlight">
              <span className="stat-label">Среднее время продажи:</span>
              <span className="stat-value large">{closedDeals.avg_days_to_sell || 0} дней</span>
            </div>
          </div>

          {closedDeals.by_type && closedDeals.by_type.length > 0 && (
            <>
              <h3>По типам недвижимости</h3>
              <table className="stats-table">
                <thead>
                  <tr>
                    <th>Тип</th>
                    <th>Продано</th>
                    <th>Средняя цена</th>
                    <th>Выручка</th>
                  </tr>
                </thead>
                <tbody>
                  {closedDeals.by_type.map((item, idx) => (
                    <tr key={idx}>
                      <td><strong>{item.type}</strong></td>
                      <td>{item.count}</td>
                      <td>{formatNumber(item.avg_price)} ₽</td>
                      <td>{formatNumber(item.total_revenue)} ₽</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </div>
      )}

      {/* Две колонки: популярные объявления и поисковые запросы */}
      <div className="analytics-columns">
        {/* Популярные объявления */}
        <div className="analytics-card">
          <h2>🔥 Популярные за {getPeriodText(period)}</h2>
          <div className="listings-list">
            {popularListings.length > 0 ? (
              popularListings.map((item, index) => (
                <div key={item.listing_id || index} className="listing-item">
                  <span className="rank">{index + 1}</span>
                  {item.photo && (
                    <img src={item.photo} alt="" className="listing-thumb" />
                  )}
                  <div className="listing-info">
                    <h4>{item.title || 'Без названия'}</h4>
                    <p>{item.address || 'Адрес не указан'}</p>
                  </div>
                  <div className="listing-stats">
                    <span className="views">👁 {item.views || 0}</span>
                    <span className="price">
                      {formatNumber(item.price)} ₽
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="no-data">Нет данных за {getPeriodText(period)}</p>
            )}
          </div>
        </div>

        {/* Популярные поисковые запросы */}
        <div className="analytics-card">
          <h2>🔍 Популярные запросы</h2>
          <div className="queries-list">
            {searchQueries.length > 0 ? (
              searchQueries.map((item, index) => (
                <div key={index} className="query-item">
                  <span className="rank">{index + 1}</span>
                  <span className="query">"{item.query || 'пустой запрос'}"</span>
                  <span className="count">{item.count || 0} раз</span>
                </div>
              ))
            ) : (
              <p className="no-data">Нет данных о поиске</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminAnalytics;