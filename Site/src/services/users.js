import API from './api';

// Получить профиль пользователя
export const getUser = async (id) => {
  const response = await API.get(`/users/${id}`);
  return response.data;
};

// Получить объявления пользователя
export const getUserListings = async (userId) => {
  const response = await API.get(`/users/${userId}/listings`);
  return response.data;
};

// Получить отзывы о пользователе
export const getUserReviews = async (userId) => {
  const response = await API.get(`/users/${userId}/reviews`);
  return response.data;
};

// Регистрация
export const registerUser = async (userData) => {
  const response = await API.post('/users/', userData);
  return response.data;
};

// Оставить отзыв
export const createReview = async (userId, reviewData) => {
  const response = await API.post(`/users/${userId}/reviews`, reviewData);
  return response.data;
};