import React, { useState, useEffect, useCallback } from 'react';
import { getFavorites } from '../services/favorites';
import ListingCard from '../components/ListingCard';
import { useAuth } from '../context/AuthContext';

function Favorites() {
    const { isAuthenticated } = useAuth();
    const [listings, setListings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const loadFavorites = useCallback(async () => {
        if (!isAuthenticated) {
            setListings([]);
            setLoading(false);
            return;
        }
        setLoading(true);
        setError(null);
        try {
            const data = await getFavorites();
            setListings(data || []);
        } catch (err) {
            setError('Ошибка загрузки избранного');
        } finally {
            setLoading(false);
        }
    }, [isAuthenticated]);

    useEffect(() => {
        loadFavorites();
    }, [loadFavorites]);

    if (!isAuthenticated) {
        return (
            <div className="favorites-page">
                <h1>Избранное</h1>
                <p>Войдите, чтобы увидеть избранное</p>
            </div>
        );
    }

    if (loading) return <div className="loader">Загрузка...</div>;

    if (error) return <div className="error">{error}</div>;

    return (
        <div className="favorites-page">
            <h1>Избранное</h1>
            {listings.length === 0 ? (
                <p>У вас пока нет избранных объявлений</p>
            ) : (
                <div className="listings-grid">
                    {listings.map((listing) => (
                        <ListingCard key={listing.listing_id} listing={listing} />
                    ))}
                </div>
            )}
        </div>
    );
}

export default Favorites;