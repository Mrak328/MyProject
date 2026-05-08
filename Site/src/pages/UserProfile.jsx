import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import API from '../services/api';
import ListingCard from '../components/ListingCard';
import './UserProfile.css';

function UserProfile() {
    const { id } = useParams();
    const [user, setUser] = useState(null);
    const [listings, setListings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const loadUserData = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const [userRes, listingsRes] = await Promise.all([
                API.get(`/users/${id}`),
                API.get('/listings/search', { params: { user_id: id } }) // или свой эндпоинт
            ]);
            setUser(userRes.data);
            setListings(listingsRes.data?.items || listingsRes.data || []);
        } catch (err) {
            setError(err.response?.data?.detail || 'Не удалось загрузить данные');
        } finally {
            setLoading(false);
        }
    }, [id]);

    useEffect(() => {
        loadUserData();
    }, [loadUserData]);

    if (loading) return <div className="loader">Загрузка...</div>;

    if (error) return (
        <div className="error-container">
            <div className="error-message">{error}</div>
            <button onClick={loadUserData} className="retry-btn">Повторить</button>
        </div>
    );

    if (!user) return <div className="error">Пользователь не найден</div>;

    return (
        <div className="user-profile">
            <div className="profile-header">
                <div className="avatar">
                    {user.avatar_url ? (
                        <img src={user.avatar_url} alt={user.first_name} />
                    ) : (
                        <div className="avatar-placeholder">
                            {user.first_name?.charAt(0) || '?'}
                        </div>
                    )}
                </div>
                <div className="profile-info">
                    <h1>{user.first_name}</h1>
                    <p className="registered">
                        На сайте с {new Date(user.registration_date).toLocaleDateString('ru-RU')}
                    </p>
                    <p className="stat">
                        🏠 Объявлений: {listings.length}
                    </p>
                </div>
            </div>

            <div className="user-listings">
                <h2>Объявления пользователя</h2>
                {listings.length === 0 ? (
                    <p className="no-listings">У пользователя пока нет объявлений</p>
                ) : (
                    <div className="listings-grid">
                        {listings.map((listing) => (
                            <ListingCard key={listing.listing_id} listing={listing} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default UserProfile;