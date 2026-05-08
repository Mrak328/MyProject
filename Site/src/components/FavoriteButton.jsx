import React, { useState, useEffect, useCallback } from 'react';
import { addFavorite, removeFavorite, checkFavorite } from '../services/favorites';
import { useAuth } from '../context/AuthContext';

function FavoriteButton({ listingId, onToggle }) {
    const { isAuthenticated } = useAuth();
    const [isFavorite, setIsFavorite] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (isAuthenticated && listingId) {
            checkFavorite(listingId).then(setIsFavorite).catch(() => {});
        } else {
            setIsFavorite(false);
        }
    }, [listingId, isAuthenticated]);

    const handleClick = useCallback(async () => {
        if (!isAuthenticated) {
            alert('Войдите, чтобы добавить в избранное');
            return;
        }
        setLoading(true);
        const newState = !isFavorite;
        setIsFavorite(newState); // оптимистичное обновление
        try {
            if (newState) {
                await addFavorite(listingId);
            } else {
                await removeFavorite(listingId);
            }
            onToggle?.(newState);
        } catch (error) {
            setIsFavorite(!newState); // откат при ошибке
            console.error('Ошибка избранного:', error);
        } finally {
            setLoading(false);
        }
    }, [isAuthenticated, isFavorite, listingId, onToggle]);

    return (
        <button
            onClick={handleClick}
            disabled={loading}
            className={`favorite-btn ${isFavorite ? 'active' : ''}`}
            aria-label={isFavorite ? 'Удалить из избранного' : 'Добавить в избранное'}
        >
            {isFavorite ? '★ В избранном' : '☆ В избранное'}
        </button>
    );
}

export default FavoriteButton;