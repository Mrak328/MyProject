import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import API from '../services/api';
import { useAuth } from '../context/AuthContext';
import FavoriteButton from '../components/FavoriteButton';
import ReportModal from '../components/ReportModal';
import './ListingDetail.css';

const PLACEHOLDER = 'https://via.placeholder.com/800x600?text=Нет+фото';

function ListingDetail() {
    const { id } = useParams();
    const { user, isAuthenticated } = useAuth();

    const [listing, setListing] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedPhoto, setSelectedPhoto] = useState(0);
    const [showReportModal, setShowReportModal] = useState(false);
    const [reviews, setReviews] = useState([]);
    const [comments, setComments] = useState({});
    const [newReview, setNewReview] = useState('');
    const [commentInputs, setCommentInputs] = useState({});

    useEffect(() => {
        loadListing();
        loadReviews();
    }, [id]);

    const loadListing = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await API.get(`/listings/${id}`);
            setListing(res.data);
        } catch {
            setError('Ошибка загрузки объявления');
        } finally {
            setLoading(false);
        }
    }, [id]);

    const loadReviews = async () => {
        try {
            const res = await API.get(`/reviews/listing/${id}`);
            setReviews(res.data || []);
            res.data?.forEach(r => loadComments(r.review_id));
        } catch {}
    };

    const loadComments = async (reviewId) => {
        try {
            const res = await API.get(`/comments/review/${reviewId}`);
            setComments(prev => ({ ...prev, [reviewId]: res.data || [] }));
        } catch {}
    };

    const submitReview = async () => {
        if (!newReview.trim()) return;
        try {
            await API.post('/reviews/', {
                user_id: listing.user_id,
                listing_id: listing.listing_id,
                content: newReview
            });
            setNewReview('');
            loadReviews();
        } catch (err) {
            alert(err.response?.data?.detail || 'Ошибка');
        }
    };

    const submitComment = async (reviewId, content) => {
        if (!content.trim()) return;
        try {
            await API.post('/comments/', { review_id: reviewId, content });
            setCommentInputs(prev => ({ ...prev, [reviewId]: '' }));
            loadComments(reviewId);
        } catch {}
    };

    const changePhoto = useCallback((delta) => {
        setSelectedPhoto((prev) => {
            if (!listing?.photos?.length) return 0;
            return (prev + delta + listing.photos.length) % listing.photos.length;
        });
    }, [listing]);

    const formatPrice = (price) => {
        if (!price) return 'Цена не указана';
        return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
    };

    const formatDate = (date) => {
        if (!date) return '';
        return new Date(date).toLocaleDateString('ru-RU', {
            day: 'numeric', month: 'long', year: 'numeric'
        });
    };

    if (loading) return <div className="loader">Загрузка...</div>;
    if (error) return <div className="error">{error}</div>;
    if (!listing) return <div className="error">Объявление не найдено</div>;

    const photos = listing.photos || [];
    const currentPhoto = photos.length > 0
        ? (photos[selectedPhoto]?.file_url || photos[selectedPhoto])
        : PLACEHOLDER;
    const dealTypeLabel = listing.deal_type_id === 1 ? 'Продажа' : listing.deal_type_id === 2 ? 'Аренда' : '';

    return (
        <div className="listing-detail">
            <div className="breadcrumbs">
                <Link to="/">Главная</Link> / <Link to="/listings">Объявления</Link> / <span>{listing.title}</span>
            </div>

            <h1 className="detail-title">{listing.title}</h1>

            <div className="detail-content">
                <div className="detail-left">
                    <div className="main-photo-container">
                        <img src={currentPhoto} alt={listing.title} className="main-photo" onError={(e) => { e.target.src = PLACEHOLDER; }} />
                        {photos.length > 1 && (
                            <>
                                <button className="main-photo-nav prev" onClick={() => changePhoto(-1)}>‹</button>
                                <button className="main-photo-nav next" onClick={() => changePhoto(1)}>›</button>
                                <div className="main-photo-counter">{selectedPhoto + 1} / {photos.length}</div>
                            </>
                        )}
                    </div>

                    {photos.length > 1 && (
                        <div className="photo-thumbnails">
                            {photos.map((photo, index) => (
                                <div key={index} className={`thumbnail ${selectedPhoto === index ? 'active' : ''}`} onClick={() => setSelectedPhoto(index)}>
                                    <img src={photo.file_url || photo} alt={`Фото ${index + 1}`} onError={(e) => { e.target.src = PLACEHOLDER; }} />
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
                        {listing.deal_type_id === 2 && <div className="price-period">в месяц</div>}
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
                            {listing.rooms && (
                                <div className="feature-item">
                                    <span className="feature-label">Комнат</span>
                                    <span className="feature-value">{listing.rooms}</span>
                                </div>
                            )}
                            {listing.floor && (
                                <div className="feature-item">
                                    <span className="feature-label">Этаж</span>
                                    <span className="feature-value">{listing.floor}{listing.max_floor ? ` / ${listing.max_floor}` : ''}</span>
                                </div>
                            )}
                            {listing.address && (
                                <div className="feature-item">
                                    <span className="feature-label">Адрес</span>
                                    <span className="feature-value">{listing.address}</span>
                                </div>
                            )}
                            {dealTypeLabel && (
                                <div className="feature-item">
                                    <span className="feature-label">Тип сделки</span>
                                    <span className="feature-value">{dealTypeLabel}</span>
                                </div>
                            )}
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

                    <div className="action-buttons">
                        <FavoriteButton listingId={Number(id)} />
                        <button onClick={() => setShowReportModal(true)} className="report-btn">🚨 Пожаловаться</button>
                    </div>

                    {/* Контакты */}
                    <div className="contacts-section">
                        <h3>Контакты</h3>
                        {listing.contact_phone ? (
                            <div className="contacts-info">
                                <div className="contact-item">
                                    <span className="contact-icon">📞</span>
                                    <a href={`tel:${listing.contact_phone}`}>{listing.contact_phone}</a>
                                </div>
                                {listing.contact_person && (
                                    <div className="contact-item">
                                        <span className="contact-icon">👤</span>
                                        <span>{listing.contact_person}</span>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <p className="no-contacts">Контакты не указаны</p>
                        )}

                        {listing.user_id && (
                            <div className="contact-item profile-link-row">
                                <span className="contact-icon">👤</span>
                                <Link to={`/user/${listing.user_id}`} className="profile-link">
                                    Профиль продавца
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Отзывы */}
            <div className="reviews-section">
                <h2>Отзывы ({reviews.length})</h2>

                {isAuthenticated && (
                    <div className="review-form">
                        <textarea placeholder="Напишите отзыв..." value={newReview} onChange={(e) => setNewReview(e.target.value)} rows="3" maxLength={1000} />
                        <button onClick={submitReview} disabled={!newReview.trim()}>Оставить отзыв</button>
                    </div>
                )}

                {reviews.length === 0 && !isAuthenticated && (
                    <p className="no-data">Войдите, чтобы оставить отзыв</p>
                )}

                {reviews.map((review) => (
                    <div key={review.review_id} className="review-card">
                        <div className="review-header">
                            <strong>{review.author_name || 'Пользователь'}</strong>
                            <span className="review-date">{formatDate(review.created_date)}</span>
                        </div>
                        <p className="review-content">{review.content}</p>

                        {comments[review.review_id]?.length > 0 && (
                            <div className="comments-list">
                                {comments[review.review_id].map((c) => (
                                    <div key={c.comment_id} className="comment-item">
                                        <strong>{c.user_name || 'Пользователь'}</strong>: {c.content}
                                        <span className="comment-date">{formatDate(c.created_date)}</span>
                                    </div>
                                ))}
                            </div>
                        )}

                        {isAuthenticated && (
                            <div className="comment-form">
                                <input
                                    placeholder="Добавить комментарий..."
                                    value={commentInputs[review.review_id] || ''}
                                    onChange={(e) => setCommentInputs(prev => ({ ...prev, [review.review_id]: e.target.value }))}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter') submitComment(review.review_id, e.target.value);
                                    }}
                                />
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {showReportModal && (
                <ReportModal listingId={Number(id)} onClose={() => setShowReportModal(false)} />
            )}
        </div>
    );
}

export default ListingDetail;