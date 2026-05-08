import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import { login as apiLogin, checkAuth, logout as apiLogout, setAuthToken } from '../services/auth';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Проверка токена при загрузке
    useEffect(() => {
        const initAuth = async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                setLoading(false);
                return;
            }
            setAuthToken(token);
            try {
                const userData = await checkAuth();
                setUser(userData);
            } catch {
                localStorage.removeItem('token');
                setAuthToken(null);
            }
            setLoading(false);
        };
        initAuth();
    }, []);

    const login = useCallback(async (emailOrPhone, password) => {
        setError(null);
        try {
            const data = await apiLogin(emailOrPhone, password);
            localStorage.setItem('token', data.access_token);
            setAuthToken(data.access_token);
            const userData = await checkAuth();
            setUser(userData);
            return true;
        } catch (err) {
            setError(err.response?.data?.detail || 'Ошибка входа');
            return false;
        }
    }, []);

    const logout = useCallback(() => {
        apiLogout();
        localStorage.removeItem('token');
        setAuthToken(null);
        setUser(null);
    }, []);

    const isAuthenticated = !!user;
    const isAdmin = user?.role_id === 1;
    const isModerator = user?.role_id === 2;
    const isUser = user?.role_id === 3;

    return (
        <AuthContext.Provider value={{
            user,
            loading,
            error,
            login,
            logout,
            isAuthenticated,
            isAdmin,
            isModerator,
            isUser
        }}>
            {children}
        </AuthContext.Provider>
    );
};