import React, { createContext, useState, useContext, useEffect } from 'react';
import { login as apiLogin, checkAuth, logout as apiLogout, setAuthToken } from '../services/auth';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

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

    const login = async (emailOrPhone, password) => {
        setError(null);
        try {
            const data = await apiLogin(emailOrPhone, password);
            const { access_token } = data;

            localStorage.setItem('token', access_token);
            setAuthToken(access_token);

            const userData = await checkAuth();

            if (userData) {
                setUser(userData);
                return true;
            }
            return false;
        } catch (err) {
            setError(err.response?.data?.detail || 'Ошибка входа');
            return false;
        }
    };

    const logout = () => {
        apiLogout();
        setUser(null);
    };

    // Проверки ролей
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
            isAdmin,
            isModerator,
            isUser,
            isAuthenticated: !!user
        }}>
            {children}
        </AuthContext.Provider>
    );
};