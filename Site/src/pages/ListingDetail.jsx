import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getListingDetail, getListingContacts } from '../services/listings';
import { useAuth } from '../context/AuthContext';
import './ListingDetail.css';

function ListingDetail() {
  const { id } = useParams();
  const { user } = useAuth();

  const [listing, setListing] = useState(null);
  const [contacts, setContacts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showContacts, setShowContacts] = useState(false);
  const [selectedPhoto, setSelectedPhoto] = useState(0);

  useEffect(() => {
    loadListing();
  }, [id]);

  const loadListing = async () => {
    setLoading(true);
    try {
      const data = await getListingDetail(id);
      if (data) {
        setListing(data);
      } else {
        setError('Объявление не найдено');
      }
    } catch (err) {
      setError('Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  };

  const handleShowContacts = async () => {
    if (!user) {
      alert('Войдите чтобы увидеть контакты');
      return;
    }

    const data = await getListingContacts(id);
    if (data) {
      setContacts(data);
      setShowContacts(true);
    }
  };

  const formatPrice = (price) => {
    if (!price) return 'Цена не указана';
    return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
  };

  const formatDate = (date) => {
    if (!date) return '';
    return new Date(date).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  const nextPhoto = () => {
    if (listing?.photos?.length) {
      setSelectedPhoto((prev) => (prev + 1) % listing.photos.length);
    }
  };

  const prevPhoto = () => {
    if (listing?.photos?.length) {
      setSelectedPhoto((prev) => (prev - 1 + listing.photos.length) % listing.photos.length);
    }
  };

  if (loading) return <div className="loader">Загрузка...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!listing) return <div className="error">Объявление не найдено</div>;

  const photos = listing.photos || [];
  const hasMultiplePhotos = photos.length > 1;

  return (
    <div className="listing-detail">
      {/* Хлебные крошки */}
      <div className="breadcrumbs">
        <Link to="/">Главная</Link> / <span>Объявление {id}</span>
      </div>

      <h1 className="detail-title">{listing.title}</h1>

      <div className="detail-content">
        {/* Левая колонка - фото */}
        <div className="detail-left">
          {/* Большое фото с навигацией */}
          <div className="main-photo-container">
            {photos.length > 0 ? (
              <img
                src={photos[selectedPhoto]?.file_url || photos[selectedPhoto]}
                alt={listing.title}
                className="main-photo"
                onError={(e) => {
                  e.target.src = 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800';
                }}
              />
            ) : (
              <img
                src="https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800"
                alt="Нет фото"
                className="main-photo"
              />
            )}

            {/* Стрелки навигации для большого фото */}
            {hasMultiplePhotos && (
              <>
                <button className="main-photo-nav prev" onClick={prevPhoto}>
                  ‹
                </button>
                <button className="main-photo-nav next" onClick={nextPhoto}>
                  ›
                </button>
              </>
            )}

            {/* Счетчик фото */}
            {hasMultiplePhotos && (
              <div className="main-photo-counter">
                {selectedPhoto + 1} / {photos.length}
              </div>
            )}
          </div>

          {/* Миниатюры */}
          {photos.length > 1 && (
            <div className="photo-thumbnails">
              {photos.map((photo, index) => (
                <div
                  key={index}
                  className={`thumbnail ${selectedPhoto === index ? 'active' : ''}`}
                  onClick={() => setSelectedPhoto(index)}
                >
                  <img
                    src={photo.file_url || photo}
                    alt={`Фото ${index + 1}`}
                    onError={(e) => {
                      e.target.src = 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=100';
                    }}
                  />
                </div>
              ))}
            </div>
          )}

          {/* Описание */}
          {listing.description && (
            <div className="description-section">
              <h3>Описание</h3>
              <p className="description-text">{listing.description}</p>
            </div>
          )}
        </div>

        {/* Правая колонка - информация и контакты */}
        <div className="detail-right">
          {/* Цена */}
          <div className="price-section">
            <div className="price">{formatPrice(listing.price)}</div>
            {listing.deal_type === 'rent' && (
              <div className="price-period">в месяц</div>
            )}
          </div>

          {/* Характеристики */}
          <div className="features-section">
            <h3>Характеристики</h3>
            <div className="features-grid">
              {listing.total_area && (
                <div className="feature-item">
                  <span className="feature-label">Площадь</span>
                  <span className="feature-value">{listing.total_area} м²</span>
                </div>
              )}
              {listing.rooms && (
                <div className="feature-item">
                  <span className="feature-label">Комнат</span>
                  <span className="feature-value">{listing.rooms}</span>
                </div>
              )}
              <div className="feature-item">
                <span className="feature-label">Адрес</span>
                <span className="feature-value">{listing.address}</span>
              </div>
              <div className="feature-item">
                <span className="feature-label">Дата публикации</span>
                <span className="feature-value">{formatDate(listing.publication_date)}</span>
              </div>
              <div className="feature-item">
                <span className="feature-label">Просмотров</span>
                <span className="feature-value">{listing.views || 0}</span>
              </div>
            </div>
          </div>

          {/* Контакты продавца */}
          <div className="contacts-section">
            <h3>Контакты</h3>

            {showContacts && contacts ? (
              <div className="contacts-info">
                <div className="contact-item">
                  <span className="contact-icon">📞</span>
                  <a href={`tel:${contacts.phone}`} className="contact-phone">
                    {contacts.phone}
                  </a>
                </div>
                {contacts.person && (
                  <div className="contact-item">
                    <span className="contact-icon">👤</span>
                    <span>{contacts.person}</span>
                  </div>
                )}
                {contacts.email && (
                  <div className="contact-item">
                    <span className="contact-icon">✉️</span>
                    <a href={`mailto:${contacts.email}`}>{contacts.email}</a>
                  </div>
                )}
              </div>
            ) : (
              <button
                className="show-contacts-btn"
                onClick={handleShowContacts}
              >
                {user ? 'Показать телефон' : 'Войдите чтобы увидеть контакты'}
              </button>
            )}
          </div>

          {/* Кнопка в избранное */}
          {user && (
            <button className="favorite-btn">
              ★ В избранное
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default ListingDetail;