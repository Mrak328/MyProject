import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getListingDetail, getListingContacts, registerView } from '../services/listings';
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
        // Регистрируем просмотр при открытии страницы
        registerView(id, user?.user_id);
    }, [id, user]);

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
            <div className="breadcrumbs">
                <Link to="/">Главная</Link> / <span>Объявление {id}</span>
            </div>

            <h1 className="detail-title">{listing.title}</h1>

            <div className="detail-content">
                <div className="detail-left">
                    <div className="main-photo-container">
                        {photos.length > 0 ? (
                            <img
                                //src={photos[selectedPhoto]?.file_url || photos[selectedPhoto]}
                                alt={listing.title}
                                className="main-photo"
                                onError={(e) => {
                                    e.target.src = 'https://via.placeholder.com/800x600?text=Нет+фото';
                                }}
                            />
                        ) : (
                            <img
                                src="https://via.placeholder.com/800x600?text=Нет+фото"
                                alt="Нет фото"
                                className="main-photo"
                            />
                        )}

                        {hasMultiplePhotos && (
                            <>
                                <button className="main-photo-nav prev" onClick={prevPhoto}>‹</button>
                                <button className="main-photo-nav next" onClick={nextPhoto}>›</button>
                            </>
                        )}

                        {hasMultiplePhotos && (
                            <div className="main-photo-counter">
                                {selectedPhoto + 1} / {photos.length}
                            </div>
                        )}
                    </div>

                    {photos.length > 1 && (
                        <div className="photo-thumbnails">
                            {photos.map((photo, index) => (
                                <div
                                    key={index}
                                    className={`thumbnail ${selectedPhoto === index ? 'active' : ''}`}
                                    onClick={() => setSelectedPhoto(index)}
                                >
                                    <img
                                        //src={photo.file_url || photo}
                                        alt={`Фото ${index + 1}`}
                                        onError={(e) => {
                                            e.target.src = 'https://via.placeholder.com/100x100?text=Фото';
                                        }}
                                    />
                                </div>
                            ))}
                        </div>
                    )}

                    {listing.description && (
                        <div className="description-section">
                            <h3>Описание</h3>
                            <p className="description-text">{listing.description}</p>
                        </div>
                    )}
                </div>

                <div className="detail-right">
                    <div className="price-section">
                        <div className="price">{formatPrice(listing.price)}</div>
                        {listing.deal_type === 'rent' && (
                            <div className="price-period">в месяц</div>
                        )}
                    </div>

                    <div className="features-section">
                        <h3>Характеристики</h3>
                        <div className="features-grid">
                            {listing.total_area && (
                                <div className="feature-item">
                                    <span className="feature-label">Площадь</span>
                                    <span className="feature-value">{listing.total_area} м²</span>
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