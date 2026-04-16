import React, { useState, useEffect } from 'react';
import { addFavorite, removeFavorite, checkFavorite } from '../services/favorites';
import { useAuth } from '../context/AuthContext';

function FavoriteButton({ listingId, onToggle }) {
    const { isAuthenticated } = useAuth();
    const [isFavorite, setIsFavorite] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (isAuthenticated) {
            checkFavorite(listingId).then(setIsFavorite);
        }
    }, [listingId, isAuthenticated]);

    const handleClick = async () => {
        if (!isAuthenticated) {
            alert('Войдите чтобы добавить в избранное');
            return;
        }
        setLoading(true);
        try {
            if (isFavorite) {
                await removeFavorite(listingId);
                setIsFavorite(false);
            } else {
                await addFavorite(listingId);
                setIsFavorite(true);
            }
            if (onToggle) onToggle(!isFavorite);
        } catch (error) {
            console.error('Ошибка:', error);
        }
        setLoading(false);
    };

    return (
        <button
            onClick={handleClick}
            disabled={loading}
            className={`favorite-btn ${isFavorite ? 'active' : ''}`}
        >
            {isFavorite ? '★ В избранном' : '☆ В избранное'}
        </button>
    );
}

export default FavoriteButton;