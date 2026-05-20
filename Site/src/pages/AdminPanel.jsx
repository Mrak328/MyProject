import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import API from '../services/api';
import './AdminPanel.css';

function AdminPanel() {
    const { user } = useAuth();
    const [stats, setStats] = useState(null);

    useEffect(() => {
        API.get('/admin/stats').then(res => setStats(res.data)).catch(() => {});
    }, []);

    return (
        <div className="admin-panel">
            <h1>Панель администратора</h1>
            <p>Добро пожаловать, {user?.first_name || 'Админ'}!</p>

            {stats && (
                <div className="admin-stats">
                    <div className="admin-stat">
                        <span className="admin-stat-value">{stats.total_users}</span>
                        <span className="admin-stat-label">Пользователей</span>
                    </div>
                    <div className="admin-stat">
                        <span className="admin-stat-value">{stats.total_listings}</span>
                        <span className="admin-stat-label">Объявлений</span>
                    </div>
                    <div className="admin-stat">
                        <span className="admin-stat-value">{stats.active_blocks || 0}</span>
                        <span className="admin-stat-label">Блокировок</span>
                    </div>
                </div>
            )}

            <div className="admin-menu">
                <Link to="/admin/analytics" className="admin-card">
                    <h3>📊 Аналитика</h3>
                    <p>Статистика, просмотры, цены, сделки</p>
                </Link>

                <Link to="/admin/users" className="admin-card">
                    <h3>👥 Пользователи</h3>
                    <p>Список, роли, блокировки</p>
                </Link>

                <Link to="/admin/activity" className="admin-card">
                    <h3>📋 История действий</h3>
                    <p>Логи действий пользователей</p>
                </Link>

                <Link to="/admin/search" className="admin-card">
                    <h3>🔍 Поисковые запросы</h3>
                    <p>Что ищут пользователи</p>
                 </Link>
            </div>
        </div>
    );
}

export default AdminPanel;