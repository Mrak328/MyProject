import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './AdminPanel.css';

function AdminPanel() {
    const { user } = useAuth();

    return (
        <div className="admin-panel">
            <h1>Панель администратора</h1>
            <p>Добро пожаловать, {user?.first_name}!</p>

            <div className="admin-menu">
                <Link to="/analytics" className="admin-card">
                    <h3>📊 Аналитика</h3>
                    <p>Просмотр статистики продаж и объявлений</p>
                </Link>

                <Link to="/users" className="admin-card">
                    <h3>👥 Пользователи</h3>
                    <p>Управление пользователями</p>
                </Link>

                <Link to="/listings/moderate" className="admin-card">
                    <h3>📋 Модерация</h3>
                    <p>Проверка объявлений</p>
                </Link>

                <Link to="/settings" className="admin-card">
                    <h3>⚙️ Настройки</h3>
                    <p>Настройки сайта</p>
                </Link>
            </div>
        </div>
    );
}

export default AdminPanel;