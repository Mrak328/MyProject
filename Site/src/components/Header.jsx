import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Header.css';

function Header() {
    const { user, isAdmin, logout, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <header className="header">
            <div className="header-container">
                <Link to="/" className="logo">
                    🏠 Недвижимость
                </Link>

                <nav className="nav-menu">
                    <Link to="/">Главная</Link>

                    {isAdmin && (
                        <>
                            <Link to="/admin">Админ панель</Link>
                            <Link to="/analytics">Аналитика</Link>
                        </>
                    )}
                </nav>

                <div className="auth-buttons">
                    {isAuthenticated ? (
                        <>
                            <span className="user-name">{user?.first_name}</span>
                            <button onClick={handleLogout}>Выйти</button>
                        </>
                    ) : (
                        <button onClick={() => navigate('/login')}>Войти</button>
                    )}
                </div>
            </div>
        </header>
    );
}

export default Header;