import React, { createContext, useState, useContext, useEffect } from 'react';
import { getFavorites, addToFavorites, removeFromFavorites } from '../services/favorites';
import { useAuth } from './AuthContext';

const FavoritesContext = createContext();

export const useFavorites = () => useContext(FavoritesContext);

export const FavoritesProvider = ({ children }) => {
  const { user } = useAuth();
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      loadFavorites();
    } else {
      setFavorites([]);
    }
  }, [user]);

  const loadFavorites = async () => {
    setLoading(true);
    try {
      const data = await getFavorites(user.user_id);
      setFavorites(data);
    } catch (error) {
      console.error('Ошибка загрузки избранного:', error);
    }
    setLoading(false);
  };

  const addFavorite = async (userId, listingId) => {
    try {
      await addToFavorites(userId, listingId);
      await loadFavorites();
    } catch (error) {
      console.error('Ошибка добавления в избранное:', error);
    }
  };

  const removeFavorite = async (userId, listingId) => {
    try {
      await removeFromFavorites(userId, listingId);
      await loadFavorites();
    } catch (error) {
      console.error('Ошибка удаления из избранного:', error);
    }
  };

  const isFavorite = (listingId) => {
    return favorites.some(fav => fav.listing_id === listingId);
  };

  return (
    <FavoritesContext.Provider value={{
      favorites,
      loading,
      addFavorite,
      removeFavorite,
      isFavorite,
      refreshFavorites: loadFavorites
    }}>
      {children}
    </FavoritesContext.Provider>
  );
};