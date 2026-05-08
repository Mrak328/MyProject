import React, { useState, useEffect, useCallback } from 'react';
import API from '../services/api';
import { useAuth } from '../context/AuthContext';
import './Moderation.css';

const COMPLAINT_TYPES = {
    1: 'Спам', 2: 'Мошенничество', 3: 'Неактуальное', 4: 'Оскорбление',
    5: 'Запрещённый контент', 6: 'Дубликат', 7: 'Неверная цена',
    8: 'Чужие фото', 9: 'Фишинг', 10: 'Другое'
};

function Moderation() {
    const { isModerator, isAdmin } = useAuth();
    const [activeTab, setActiveTab] = useState('complaints');
    const [listings, setListings] = useState([]);
    const [complaints, setComplaints] = useState([]);
    const [loading, setLoading] = useState(true);

    const loadPendingListings = useCallback(async () => {
        setLoading(true);
        try {
            const res = await API.get('/moderation/pending-listings');
            setListings(res.data || []);
        } catch {
            setListings([]);
        } finally {
            setLoading(false);
        }
    }, []);

    const loadComplaints = useCallback(async () => {
        setLoading(true);
        try {
            const res = await API.get('/moderation/complaints?status_filter=pending');
            setComplaints(res.data || []);
        } catch {
            setComplaints([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        activeTab === 'listings' ? loadPendingListings() : loadComplaints();
    }, [activeTab, loadPendingListings, loadComplaints]);

    const approveListing = async (listingId) => {
        try {
            await API.put(`/moderation/listings/${listingId}/approve`);
            loadPendingListings();
        } catch {
            alert('Ошибка при одобрении');
        }
    };

    const rejectListing = async (listingId) => {
        if (!window.confirm('Отклонить объявление?')) return;
        try {
            await API.put(`/moderation/listings/${listingId}/reject`);
            loadPendingListings();
        } catch {
            alert('Ошибка при отклонении');
        }
    };

    const resolveComplaint = async (complaintId, action) => {
        try {
            await API.put(`/moderation/complaints/${complaintId}/resolve?action=${action}`);
            loadComplaints();
        } catch {
            alert('Ошибка при обработке жалобы');
        }
    };

    if (!isModerator && !isAdmin) {
        return <div className="access-denied">Доступ запрещён</div>;
    }

    const pendingCount = complaints.length;

    return (
        <div className="moderation-page">
            <h1>Модерация</h1>

            <div className="moderation-tabs">
                <button
                    className={`tab-btn ${activeTab === 'listings' ? 'active' : ''}`}
                    onClick={() => setActiveTab('listings')}
                >
                    Объявления ({listings.length})
                </button>
                <button
                    className={`tab-btn ${activeTab === 'complaints' ? 'active' : ''}`}
                    onClick={() => setActiveTab('complaints')}
                >
                    Жалобы ({pendingCount})
                </button>
            </div>

            {loading && <div className="loader">Загрузка...</div>}

            {/* Объявления на модерацию */}
            {!loading && activeTab === 'listings' && (
                <div className="listings-section">
                    {listings.length === 0 ? (
                        <p className="empty-state">Нет объявлений на модерацию</p>
                    ) : (
                        <div className="moderation-list">
                            {listings.map((listing) => (
                                <div key={listing.listing_id} className="moderation-card">
                                    <div className="moderation-card-body">
                                        <h3>{listing.title}</h3>
                                        <p>📍 {listing.address || 'Адрес не указан'}</p>
                                        <p>
                                            {listing.total_area && <span>📐 {listing.total_area} м² </span>}
                                            {listing.rooms && <span>🛏 {listing.rooms} комн </span>}
                                            <span>💰 {listing.price?.toLocaleString()} ₽</span>
                                        </p>
                                        <p className="moderation-description">
                                            {listing.description?.substring(0, 150)}
                                            {listing.description?.length > 150 && '...'}
                                        </p>
                                    </div>
                                    <div className="moderation-card-actions">
                                        <a
                                            href={`http://localhost:3000/listing/${listing.listing_id}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="btn-link"
                                        >
                                            🔗 К объявлению
                                        </a>
                                        <button className="btn-approve" onClick={() => approveListing(listing.listing_id)}>
                                            ✅ Одобрить
                                        </button>
                                        <button className="btn-reject" onClick={() => rejectListing(listing.listing_id)}>
                                            ❌ Отклонить
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Жалобы */}
            {!loading && activeTab === 'complaints' && (
                <div className="complaints-section">
                    {complaints.length === 0 ? (
                        <p className="empty-state">Нет новых жалоб</p>
                    ) : (
                        <div className="moderation-list">
                            {complaints.map((c) => (
                                <div key={c.complaint_id} className="moderation-card">
                                    <div className="moderation-card-body">
                                        <div className="complaint-header">
                                            <span className="complaint-type-badge">
                                                {COMPLAINT_TYPES[c.complaint_type_id] || 'Другое'}
                                            </span>
                                            <span className="complaint-date">
                                                {new Date(c.created_date).toLocaleDateString('ru-RU')}
                                            </span>
                                        </div>
                                        <p>
                                            <strong>Объявление:</strong>{' '}
                                            {c.listing?.title || 'Удалено'}
                                        </p>
                                        <p>
                                            <strong>Адрес:</strong>{' '}
                                            {c.listing?.address || 'Не указан'}
                                        </p>
                                        {c.description && (
                                            <p className="moderation-description">
                                                <strong>Причина жалобы:</strong> {c.description}
                                            </p>
                                        )}
                                    </div>
                                    <div className="moderation-card-actions">
                                        {c.listing?.listing_id && (
                                            <a
                                                href={`http://localhost:3000/listing/${c.listing.listing_id}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="btn-link"
                                            >
                                                🔗 К объявлению
                                            </a>
                                        )}
                                        <button
                                            className="btn-dismiss"
                                            onClick={() => resolveComplaint(c.complaint_id, 'dismiss')}
                                        >
                                            ✅ Всё в порядке
                                        </button>
                                        <button
                                            className="btn-approve btn-sm"
                                            onClick={() => resolveComplaint(c.complaint_id, 'hide_listing')}
                                        >
                                            🙈 Скрыть
                                        </button>
                                        <button
                                            className="btn-reject btn-sm"
                                            onClick={() => resolveComplaint(c.complaint_id, 'delete_listing')}
                                        >
                                            🗑 Удалить
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default Moderation;