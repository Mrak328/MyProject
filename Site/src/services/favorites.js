import API from './api';

export const addFavorite = (listingId) =>
    API.post(`/favorites/${listingId}`).then(r => r.data);

export const removeFavorite = (listingId) =>
    API.delete(`/favorites/${listingId}`).then(r => r.data);

export const getFavorites = () =>
    API.get('/favorites/').then(r => r.data);

export const checkFavorite = (listingId) =>
    API.get(`/favorites/check/${listingId}`).then(r => r.data.is_favorite);