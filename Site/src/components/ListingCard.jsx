import React, { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { registerView } from '../services/listings';
import { useAuth } from '../context/AuthContext';
import './ListingCard.css';

const PLACEHOLDER = 'https://via.placeholder.com/300x200?text=Нет+фото';

function ListingCard({ listing }) {
    const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);
    const [imgError, setImgError] = useState(false);
    const { user } = useAuth();

    const photos = listing.photos || [];
    const hasMultiplePhotos = photos.length > 1;

    const formatPrice = (price) => {
        if (!price) return 'Цена не указана';
        return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
    };

    const changePhoto = useCallback((delta, e) => {
        e.preventDefault();
        e.stopPropagation();
        setCurrentPhotoIndex((prev) => (prev + delta + photos.length) % photos.length);
        setImgError(false);
    }, [photos.length]);

    const nextPhoto = (e) => changePhoto(1, e);
    const prevPhoto = (e) => changePhoto(-1, e);

    const handleCardClick = () => {
        registerView(listing.listing_id, user?.user_id);
    };

    const currentPhoto = photos.length > 0
        ? (photos[currentPhotoIndex]?.file_url || photos[currentPhotoIndex])
        : PLACEHOLDER;

    // Маппинг deal_type_id → текст
    const dealTypeLabel = listing.deal_type_id === 1 ? 'Продажа' : listing.deal_type_id === 2 ? 'Аренда' : '';

    return (
        <div className="listing-card" onClick={handleCardClick}>
            <Link to={`/listing/${listing.listing_id}`}>
                <div className="card-image-container">
                    <img
                        src={imgError ? PLACEHOLDER : currentPhoto}
                        alt={listing.title}
                        className="card-image"
                        loading="lazy"
                        onError={() => setImgError(true)}
                    />

                    {hasMultiplePhotos && (
                        <>
                            <button className="photo-nav prev" onClick={prevPhoto} type="button">‹</button>
                            <button className="photo-nav next" onClick={nextPhoto} type="button">›</button>
                            <div className="photo-counter">
                                {currentPhotoIndex + 1} / {photos.length}
                            </div>
                        </>
                    )}

                    {dealTypeLabel && (
                        <span className={`deal-badge ${listing.deal_type_id === 1 ? 'sale' : 'rent'}`}>
                            {dealTypeLabel}
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
                        {listing.total_area && <span>📐 {listing.total_area} м²</span>}
                        {listing.rooms && <span>🛏 {listing.rooms} комн</span>}
                        {listing.floor && listing.max_floor && (
                            <span>🏢 {listing.floor}/{listing.max_floor} эт</span>
                        )}
                    </div>
                    <div className="card-footer">
                        <span className="card-views">👁 {listing.views || 0}</span>
                        <span className="card-date">
                            {listing.publication_date
                                ? new Date(listing.publication_date).toLocaleDateString('ru-RU')
                                : ''}
                        </span>
                    </div>
                </div>
            </Link>
        </div>
    );
}

export default ListingCard;