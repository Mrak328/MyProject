import API from './api';

export const login = (emailOrPhone, password) =>
    API.post('/auth/login', { email_or_phone: emailOrPhone, password }).then(r => r.data);

export const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (!token) return null;
    try {
        const r = await API.get('/users/me');
        return r.data;
    } catch {
        localStorage.removeItem('token');
        return null;
    }
};

export const setAuthToken = (token) => {
    if (token) {
        API.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
        delete API.defaults.headers.common['Authorization'];
    }
};

export const logout = () => {
    localStorage.removeItem('token');
    delete API.defaults.headers.common['Authorization'];
};