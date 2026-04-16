import API from './api';

// Получить профиль пользователя
export const getUser = async (id) => {
    try {
        const response = await API.get(`/users/${id}`);
        return response.data;
    } catch (error) {
        console.error('Ошибка получения пользователя:', error);
        throw error;
    }
};

// Получить объявления пользователя
export const getUserListings = async (userId) => {
    try {
        const response = await API.get(`/users/${userId}/listings`);
        return response.data;
    } catch (error) {
        console.error('Ошибка получения объявлений пользователя:', error);
        return [];
    }
};

// Получить отзывы о пользователе
export const getUserReviews = async (userId) => {
    try {
        const response = await API.get(`/users/${userId}/reviews`);
        return response.data;
    } catch (error) {
        console.error('Ошибка получения отзывов:', error);
        return [];
    }
};

// Регистрация
export const registerUser = async (userData) => {
    try {
        const response = await API.post('/auth/register', userData);
        return response.data;
    } catch (error) {
        console.error('Ошибка регистрации:', error);
        throw error;
    }
};

// Оставить отзыв
export const createReview = async (userId, reviewData) => {
    try {
        const response = await API.post(`/users/${userId}/reviews`, reviewData);
        return response.data;
    } catch (error) {
        console.error('Ошибка создания отзыва:', error);
        throw error;
    }
};

// Обновить профиль
export const updateUser = async (userId, userData) => {
    try {
        const response = await API.put(`/users/${userId}`, userData);
        return response.data;
    } catch (error) {
        console.error('Ошибка обновления профиля:', error);
        throw error;
    }
};

// Удалить пользователя (только админ)
export const deleteUser = async (userId) => {
    try {
        const response = await API.delete(`/users/${userId}`);
        return response.data;
    } catch (error) {
        console.error('Ошибка удаления пользователя:', error);
        throw error;
    }
};