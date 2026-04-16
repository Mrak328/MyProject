import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getUser, getUserListings } from '../services/users';
import ListingCard from '../components/ListingCard';
import './UserProfile.css';

function UserProfile() {
    const { id } = useParams();
    const [user, setUser] = useState(null);
    const [listings, setListings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadUserData();
    }, [id]);

    const loadUserData = async () => {
        setLoading(true);
        setError(null);
        try {
            const [userData, listingsData] = await Promise.all([
                getUser(id),
                getUserListings(id)
            ]);
            setUser(userData);
            setListings(listingsData);
        } catch (err) {
            console.error('Ошибка загрузки:', err);
            setError(err.response?.data?.detail || 'Не удалось загрузить данные пользователя');
        } finally {
            setLoading(false);
        }
    };

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
                            {user.first_name?.charAt(0) || '👤'}
                        </div>
                    )}
                </div>
                <div className="profile-info">
                    <h1>{user.first_name}</h1>
                    <div className="stats">
                        <div className="stat">
                            <span className="stat-value">{user.rating || 0}</span>
                            <span className="stat-label">⭐ Рейтинг</span>
                        </div>
                        <div className="stat">
                            <span className="stat-value">{user.reviews_count || 0}</span>
                            <span className="stat-label">📝 Отзывов</span>
                        </div>
                        <div className="stat">
                            <span className="stat-value">{listings.length}</span>
                            <span className="stat-label">🏠 Объявлений</span>
                        </div>
                    </div>
                    <p className="registered">
                        На сайте с {new Date(user.registration_date).toLocaleDateString('ru-RU')}
                    </p>
                </div>
            </div>

            <div className="user-listings">
                <h2>Объявления пользователя</h2>
                {listings.length === 0 ? (
                    <p className="no-listings">У пользователя пока нет объявлений</p>
                ) : (
                    <div className="listings-grid">
                        {listings.map(listing => (
                            <ListingCard key={listing.listing_id} listing={listing} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default UserProfile;