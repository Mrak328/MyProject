import axios from 'axios';

const API = axios.create({
    baseURL: 'http://localhost:8000/api',
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' }
});

// Токен в каждый запрос
API.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Обработка ошибок
API.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.code === 'ERR_NETWORK') {
            console.error('Бэкенд не запущен!');
        }
        // 401 — сброс токена и редирект на логин
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default API;