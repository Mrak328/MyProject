import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children, requireAdmin = false, requireModerator = false }) => {
    const { isAuthenticated, isAdmin, isModerator, loading } = useAuth();

    if (loading) {
        return <div className="loader">Загрузка...</div>;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (requireAdmin && !isAdmin) {
        return <Navigate to="/" replace />;
    }

    if (requireModerator && !isAdmin && !isModerator) {
        return <Navigate to="/" replace />;
    }

    return children;
};

export default ProtectedRoute;