import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { registerView } from '../services/listings';
import { useAuth } from '../context/AuthContext';
import './ListingCard.css';

function ListingCard({ listing }) {
    const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);
    const { user } = useAuth();

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

    const handleCardClick = () => {
        // Регистрируем просмотр при клике на карточку
        registerView(listing.listing_id, user?.user_id);
    };

    const currentPhoto = photos.length > 0
        ? (photos[currentPhotoIndex]?.file_url || photos[currentPhotoIndex])
        : 'https://via.placeholder.com/300x200?text=Нет+фото';

    return (
        <div className="listing-card" onClick={handleCardClick}>
            <Link to={`/listing/${listing.listing_id}`}>
                <div className="card-image-container">
                    <img
                        src={currentPhoto}
                        alt={listing.title}
                        className="card-image"
                        onError={(e) => {
                            e.target.src = 'https://via.placeholder.com/300x200?text=Нет+фото';
                        }}
                    />

                    {hasMultiplePhotos && (
                        <>
                            <button className="photo-nav prev" onClick={prevPhoto}>‹</button>
                            <button className="photo-nav next" onClick={nextPhoto}>›</button>
                        </>
                    )}

                    {hasMultiplePhotos && (
                        <div className="photo-counter">
                            {currentPhotoIndex + 1} / {photos.length}
                        </div>
                    )}

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