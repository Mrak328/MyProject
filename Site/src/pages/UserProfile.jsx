import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import API from '../services/api';
import ListingCard from '../components/ListingCard';
import { useAuth } from '../context/AuthContext';
import './UserProfile.css';

function UserProfile() {
    const { id } = useParams();
    const { user: currentUser } = useAuth();
    const navigate = useNavigate();
    const [profile, setProfile] = useState(null);
    const [listings, setListings] = useState([]);
    const [reviews, setReviews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('listings');

    const isOwnProfile = currentUser?.user_id === Number(id);

    const loadData = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const [userRes, listingsRes, reviewsRes] = await Promise.all([
                API.get(`/users/${id}`),
                API.get('/listings/search', { params: { user_id: id } }),
                API.get(`/reviews/user/${id}`)
            ]);
            setProfile(userRes.data);
            setListings(listingsRes.data?.items || listingsRes.data || []);
            setReviews(reviewsRes.data || []);
        } catch {
            setError('Не удалось загрузить данные');
        } finally {
            setLoading(false);
        }
    }, [id]);

    useEffect(() => { loadData(); }, [loadData]);

    const handleWrite = async () => {
        if (!currentUser) return navigate('/login');
        try {
            // Найти или создать чат с пользователем
            const agentRes = await API.get(`/agents/by-user/${id}`);
            const agentId = agentRes.data?.agent_id;
            if (agentId) {
                const chatRes = await API.post('/chats/', { agent_id: agentId, title: `Чат с ${profile?.first_name}` });
                navigate(`/chats?open=${chatRes.data.chat_id}`);
            }
        } catch {
            // Если не агент — нельзя написать
            alert('Пользователь не является риэлтором');
        }
    };

    if (loading) return <div className="loader">Загрузка...</div>;
    if (error) return <div className="error">{error}</div>;
    if (!profile) return <div className="error">Пользователь не найден</div>;

    return (
        <div className="user-profile-page">
            <div className="profile-header">
                <div className="profile-avatar">
                    {profile.avatar_url ? (
                        <img src={profile.avatar_url} alt={profile.first_name} />
                    ) : (
                        <div className="avatar-placeholder">{profile.first_name?.charAt(0) || '?'}</div>
                    )}
                </div>
                <div className="profile-info">
                    <h1>{profile.first_name}</h1>
                    <p className="profile-registered">
                        На сайте с {new Date(profile.registration_date).toLocaleDateString('ru-RU')}
                    </p>
                    <div className="profile-stats">
                        <span>🏠 {listings.length} объявлений</span>
                        <span>📝 {reviews.length} отзывов</span>
                    </div>
                    {!isOwnProfile && currentUser && (
                        <button className="btn-write" onClick={handleWrite}>💬 Написать</button>
                    )}
                </div>
            </div>

            <div className="profile-tabs">
                <button className={activeTab === 'listings' ? 'active' : ''} onClick={() => setActiveTab('listings')}>
                    Объявления ({listings.length})
                </button>
                <button className={activeTab === 'reviews' ? 'active' : ''} onClick={() => setActiveTab('reviews')}>
                    Отзывы ({reviews.length})
                </button>
            </div>

            {activeTab === 'listings' && (
                <div className="profile-listings">
                    {listings.length === 0 ? (
                        <p className="no-data">Нет объявлений</p>
                    ) : (
                        <div className="listings-grid">
                            {listings.map(l => <ListingCard key={l.listing_id} listing={l} />)}
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'reviews' && (
                <div className="profile-reviews">
                    {reviews.length === 0 ? (
                        <p className="no-data">Нет отзывов</p>
                    ) : (
                        reviews.map(r => (
                            <div key={r.review_id} className="review-card">
                                <div className="review-header">
                                    <strong>{r.author_name || 'Пользователь'}</strong>
                                    <span>{new Date(r.created_date).toLocaleDateString('ru-RU')}</span>
                                </div>
                                <p>{r.content}</p>
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
}

export default UserProfile;