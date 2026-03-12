import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './ListingCard.css';

function ListingCard({ listing }) {
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);

  // Получаем массив фото (если есть)
  const photos = listing.photos || [];
  const hasMultiplePhotos = photos.length > 1;

  const formatPrice = (price) => {
    if (!price) return 'Цена не указана';
    return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
  };

  const nextPhoto = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (photos.length > 0) {
      setCurrentPhotoIndex((prev) => (prev + 1) % photos.length);
    }
  };

  const prevPhoto = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (photos.length > 0) {
      setCurrentPhotoIndex((prev) => (prev - 1 + photos.length) % photos.length);
    }
  };

  // Текущее фото
  const currentPhoto = photos.length > 0
    ? photos[currentPhotoIndex]?.file_url || photos[currentPhotoIndex]
    : 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=300';

  return (
    <div className="listing-card">
      <Link to={`/listing/${listing.listing_id}`}>
        <div className="card-image-container">
          <img
            src={currentPhoto}
            alt={listing.title}
            className="card-image"
            onError={(e) => {
              e.target.src = 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=300';
            }}
          />

          {/* Стрелки навигации (только если есть несколько фото) */}
          {hasMultiplePhotos && (
            <>
              <button
                className="photo-nav prev"
                onClick={prevPhoto}
                aria-label="Предыдущее фото"
              >
                ‹
              </button>
              <button
                className="photo-nav next"
                onClick={nextPhoto}
                aria-label="Следующее фото"
              >
                ›
              </button>
            </>
          )}

          {/* Счетчик фото */}
          {hasMultiplePhotos && (
            <div className="photo-counter">
              {currentPhotoIndex + 1} / {photos.length}
            </div>
          )}

          {/* Бейдж с типом сделки */}
          {listing.deal_type && (
            <span className="deal-badge">
              {listing.deal_type === 'rent' ? 'Аренда' : 'Продажа'}
            </span>
          )}
        </div>

        <div className="card-content">
          <h3 className="card-title">{listing.title || 'Без названия'}</h3>
          <p className="card-price">{formatPrice(listing.price)}</p>
          <p className="card-address">
            📍 {listing.address || 'Адрес не указан'}
          </p>
          <div className="card-details">
            {listing.total_area && (
              <span>📐 {listing.total_area} м²</span>
            )}
            {listing.rooms && (
              <span>🛏 {listing.rooms} комн</span>
            )}
          </div>
          <div className="card-footer">
            <span className="card-views">👁 {listing.views || 0}</span>
            <span className="card-date">
              {listing.publication_date ?
                new Date(listing.publication_date).toLocaleDateString() :
                ''}
            </span>
          </div>
        </div>
      </Link>
    </div>
  );
}

export default ListingCard;