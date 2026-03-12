import API from './api';

export const getFavorites = async (userId) => {
  try {
    const response = await API.get(`/favorites/user/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Ошибка получения избранного:', error);
    return [];
  }
};

export const addToFavorites = async (userId, listingId) => {
  const response = await API.post(`/favorites/user/${userId}/listing/${listingId}`);
  return response.data;
};

export const removeFromFavorites = async (userId, listingId) => {
  const response = await API.delete(`/favorites/user/${userId}/listing/${listingId}`);
  return response.data;
};