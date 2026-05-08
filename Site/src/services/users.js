import API from './api';

export const getUser = (id) =>
    API.get(`/users/${id}`).then(r => r.data);

export const getUserListings = (userId) =>
    API.get('/listings/search', { params: { user_id: userId, page_size: 100 } })
        .then(r => r.data?.items || [])
        .catch(() => []);

export const getUserReviews = (userId) =>
    API.get(`/reviews/user/${userId}`).then(r => r.data).catch(() => []);

export const createReview = (data) =>
    API.post('/reviews/', data).then(r => r.data);

export const updateUser = (userId, data) =>
    API.put(`/users/${userId}`, data).then(r => r.data);