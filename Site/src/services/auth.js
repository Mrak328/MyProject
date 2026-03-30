import API from './api';

export const login = async (emailOrPhone, password) => {
    try {
        const response = await API.post('/auth/login', {
            email_or_phone: emailOrPhone,
            password
        });
        return response.data;
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
};

// Проверка токена
export const checkAuth = async () => {
    try {
        const token = localStorage.getItem('token');
        if (!token) return null;

        // Получаем данные текущего пользователя
        const response = await API.get('/users/me');
        return response.data;
    } catch (error) {
        localStorage.removeItem('token');
        return null;
    }
};

// Выход
export const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete API.defaults.headers.common['Authorization'];
};

// Установка токена для всех запросов
export const setAuthToken = (token) => {
    if (token) {
        API.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
        delete API.defaults.headers.common['Authorization'];
    }
};