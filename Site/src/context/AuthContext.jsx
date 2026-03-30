import React, { createContext, useState, useContext, useEffect } from 'react';
import { login as apiLogin, checkAuth, logout as apiLogout, setAuthToken } from '../services/auth';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Проверка авторизации при загрузке
    useEffect(() => {
        const initAuth = async () => {
            const token = localStorage.getItem('token');
            if (token) {
                setAuthToken(token);
                const userData = await checkAuth();
                if (userData) {
                    setUser(userData);
                } else {
                    localStorage.removeItem('token');
                }
            }
            setLoading(false);
        };
        initAuth();
    }, []);

    // Вход
const login = async (emailOrPhone, password) => {
    setError(null);
    try {
        const data = await apiLogin(emailOrPhone, password);
        const { access_token } = data;

        localStorage.setItem('token', access_token);
        setAuthToken(access_token);

        const userData = await checkAuth();
        setUser(userData);
        return true;
    } catch (err) {
        setError(err.response?.data?.detail || 'Ошибка входа');
        return false;
    }
};

    // Выход
    const logout = () => {
        apiLogout();
        setUser(null);
    };

    // Проверка на админа
    const isAdmin = user?.role_id === 1;

    return (
        <AuthContext.Provider value={{
            user,
            loading,
            error,
            login,
            logout,
            isAdmin,
            isAuthenticated: !!user
        }}>
            {children}
        </AuthContext.Provider>
    );
};