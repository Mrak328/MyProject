import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import { addFavorite, removeFavorite, checkFavorite } from '../services/favorites';
import { useAuth } from './AuthContext';

const FavoritesContext = createContext();

export const useFavorites = () => useContext(FavoritesContext);

export const FavoritesProvider = ({ children }) => {
    const { user, isAuthenticated } = useAuth();
    const [favoriteIds, setFavoriteIds] = useState(new Set());
    const [loading, setLoading] = useState(false);

    // Сброс при логауте
    useEffect(() => {
        if (!isAuthenticated) {
            setFavoriteIds(new Set());
        }
    }, [isAuthenticated]);

    const isFavorite = useCallback((listingId) => {
        return favoriteIds.has(listingId);
    }, [favoriteIds]);

    const check = useCallback(async (listingId) => {
        if (!isAuthenticated) return false;
        try {
            const result = await checkFavorite(listingId);
            return result?.is_favorite || false;
        } catch {
            return false;
        }
    }, [isAuthenticated]);

    const toggle = useCallback(async (listingId) => {
        if (!isAuthenticated) return;
        setLoading(true);
        const wasFavorite = favoriteIds.has(listingId);

        // Оптимистичное обновление
        setFavoriteIds((prev) => {
            const next = new Set(prev);
            wasFavorite ? next.delete(listingId) : next.add(listingId);
            return next;
        });

        try {
            if (wasFavorite) {
                await removeFavorite(listingId);
            } else {
                await addFavorite(listingId);
            }
        } catch {
            // Откат при ошибке
            setFavoriteIds((prev) => {
                const next = new Set(prev);
                wasFavorite ? next.add(listingId) : next.delete(listingId);
                return next;
            });
        } finally {
            setLoading(false);
        }
    }, [isAuthenticated, favoriteIds]);

    return (
        <FavoritesContext.Provider value={{
            favoriteIds,
            loading,
            isFavorite,
            check,
            toggle,
            count: favoriteIds.size
        }}>
            {children}
        </FavoritesContext.Provider>
    );
};