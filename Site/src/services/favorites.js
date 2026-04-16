import API from './api';

export const addFavorite = async (listingId) => {
    const response = await API.post(`/favorites/${listingId}`);
    return response.data;
};

export const removeFavorite = async (listingId) => {
    const response = await API.delete(`/favorites/${listingId}`);
    return response.data;
};

export const getFavorites = async () => {
    const response = await API.get('/favorites/');
    return response.data;
};

export const checkFavorite = async (listingId) => {
    const response = await API.get(`/favorites/check/${listingId}`);
    return response.data.is_favorite;
};