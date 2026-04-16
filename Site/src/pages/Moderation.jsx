import React, { useState, useEffect } from 'react';
import API from '../services/api';
import { useAuth } from '../context/AuthContext';
import './Moderation.css';

function Moderation() {
    const { isModerator, isAdmin } = useAuth();
    const [activeTab, setActiveTab] = useState('complaints'); // ← по умолчанию жалобы
    const [listings, setListings] = useState([]);
    const [complaints, setComplaints] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (activeTab === 'listings') {
            loadPendingListings();
        } else {
            loadComplaints();
        }
    }, [activeTab]);

    const loadPendingListings = async () => {
        setLoading(true);
        try {
            const response = await API.get('/moderation/pending-listings');
            console.log('📋 Объявления на модерацию:', response.data);
            setListings(response.data);
        } catch (error) {
            console.error('Ошибка загрузки объявлений:', error);
        }
        setLoading(false);
    };

    const loadComplaints = async () => {
        setLoading(true);
        try {
            const response = await API.get('/moderation/complaints');
            console.log('🚨 Получены жалобы:', response.data);
            console.log('📊 Количество жалоб:', response.data?.length || 0);
            setComplaints(response.data || []);
        } catch (error) {
            console.error('❌ Ошибка загрузки жалоб:', error);
            console.error('Статус ошибки:', error.response?.status);
            console.error('Данные ошибки:', error.response?.data);
            setComplaints([]);
        }
        setLoading(false);
    };

    const approveListing = async (listingId) => {
        try {
            await API.put(`/moderation/approve-listing/${listingId}`);
            loadPendingListings();
        } catch (error) {
            alert('Ошибка при одобрении');
        }
    };

    const rejectListing = async (listingId) => {
        if (!window.confirm('Удалить объявление?')) return;
        try {
            await API.delete(`/moderation/reject-listing/${listingId}`);
            loadPendingListings();
        } catch (error) {
            alert('Ошибка при отклонении');
        }
    };

    const approveComplaint = async (complaintId, action) => {
        try {
            await API.put(`/moderation/complaints/${complaintId}/approve?action=${action}`);
            loadComplaints();
        } catch (error) {
            alert('Ошибка при обработке жалобы');
        }
    };

    const rejectComplaint = async (complaintId) => {
        try {
            await API.put(`/moderation/complaints/${complaintId}/reject`);
            loadComplaints();
        } catch (error) {
            alert('Ошибка при отклонении');
        }
    };

    if (!isModerator && !isAdmin) {
        return <div className="access-denied">Доступ запрещён</div>;
    }

    const newComplaintsCount = complaints.filter(c => c.status === 'new').length;

    return (
        <div className="moderation-page">
            <h1>🛡️ Модерация</h1>

            <div className="moderation-tabs">
                <button
                    className={`tab-btn ${activeTab === 'listings' ? 'active' : ''}`}
                    onClick={() => setActiveTab('listings')}
                >
                    📋 На модерацию ({listings.length})
                </button>
                <button
                    className={`tab-btn ${activeTab === 'complaints' ? 'active' : ''}`}
                    onClick={() => setActiveTab('complaints')}
                >
                    🚨 Жалобы ({newComplaintsCount})
                </button>
            </div>

            {loading && <div className="loader">Загрузка...</div>}

            {!loading && activeTab === 'listings' && (
                <div className="listings-section">
                    {listings.length === 0 ? (
                        <div className="empty-state">
                            <p>✨ Нет объявлений на модерацию</p>
                        </div>
                    ) : (
                        <div className="listings-grid">
                            {listings.map(listing => (
                                <div key={listing.listing_id} className="listing-card">
                                    <div className="card-image">
                                        {listing.photos?.[0] ? (
                                            <img src={listing.photos[0]} alt={listing.title} />
                                        ) : (
                                            <div className="no-image">📷</div>
                                        )}
                                    </div>
                                    <div className="card-content">
                                        <h3 className="card-title">{listing.title}</h3>
                                        <p className="card-price">{listing.price?.toLocaleString()} ₽</p>
                                        <p className="card-address">📍 {listing.address}</p>
                                        <div className="card-details">
                                            {listing.total_area && <span>📐 {listing.total_area} м²</span>}
                                            {listing.rooms && <span>🛏 {listing.rooms} комн</span>}
                                        </div>
                                        <p className="card-description">
                                            {listing.description?.substring(0, 100)}...
                                        </p>
                                    </div>
                                    <div className="card-actions">
                                        <button
                                            className="btn-approve"
                                            onClick={() => approveListing(listing.listing_id)}
                                        >
                                            ✅ Одобрить
                                        </button>
                                        <button
                                            className="btn-reject"
                                            onClick={() => rejectListing(listing.listing_id)}
                                        >
                                            ❌ Отклонить
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {!loading && activeTab === 'complaints' && (
                <div className="complaints-section">
                    {complaints.length === 0 ? (
                        <div className="empty-state">
                            <p>✨ Нет жалоб</p>
                            <p style={{ fontSize: '12px', marginTop: '10px', color: '#999' }}>
                                Попробуйте создать тестовую жалобу через POST /api/complaints/1
                            </p>
                        </div>
                    ) : (
                        <div className="complaints-list">
                            {complaints.map(complaint => (
                                <div key={complaint.complaint_id} className="complaint-card">
                                    <div className="complaint-header">
                                        <div className="complaint-info">
                                            <span className={`status-badge ${complaint.status}`}>
                                                {complaint.status === 'new' ? '🟡 Новая' :
                                                 complaint.status === 'approved' ? '✅ Одобрена' : '❌ Отклонена'}
                                            </span>
                                            <span className="complaint-type">
                                                {complaint.complaint_type === 'spam' ? '📧 Спам' :
                                                 complaint.complaint_type === 'fraud' ? '⚠️ Мошенничество' :
                                                 complaint.complaint_type === 'incorrect_info' ? '📝 Недостоверная информация' :
                                                 complaint.complaint_type === 'duplicate' ? '🔄 Дубликат' : '📌 Другое'}
                                            </span>
                                            <span className="complaint-date">
                                                📅 {new Date(complaint.created_date).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="complaint-body">
                                        <div className="complaint-listing">
                                            <strong>📢 Объявление:</strong> {complaint.listing?.title || 'Удалено'}
                                        </div>
                                        {complaint.description && (
                                            <div className="complaint-description">
                                                <strong>💬 Описание:</strong> {complaint.description}
                                            </div>
                                        )}
                                    </div>
                                    {complaint.status === 'new' && (
                                        <div className="complaint-actions">
                                            <select
                                                className="action-select"
                                                id={`action-${complaint.complaint_id}`}
                                            >
                                                <option value="hide_listing">🔒 Скрыть объявление</option>
                                                <option value="delete_listing">🗑️ Удалить объявление</option>
                                                <option value="warn_user">⚠️ Предупредить пользователя</option>
                                                <option value="ban_user">🚫 Заблокировать пользователя</option>
                                            </select>
                                            <button
                                                className="btn-approve"
                                                onClick={() => {
                                                    const select = document.getElementById(`action-${complaint.complaint_id}`);
                                                    approveComplaint(complaint.complaint_id, select.value);
                                                }}
                                            >
                                                ✅ Одобрить жалобу
                                            </button>
                                            <button
                                                className="btn-reject"
                                                onClick={() => rejectComplaint(complaint.complaint_id)}
                                            >
                                                ❌ Отклонить
                                            </button>
                                        </div>
                                    )}
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