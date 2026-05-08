import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children, roles = [] }) => {
    const { isAuthenticated, user, loading } = useAuth();

    if (loading) {
        return <div className="loader">Загрузка...</div>;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    // Если роли указаны — проверяем доступ
    if (roles.length > 0 && !roles.includes(user?.role_id)) {
        return <Navigate to="/" replace />;
    }

    return children;
};

export default ProtectedRoute;