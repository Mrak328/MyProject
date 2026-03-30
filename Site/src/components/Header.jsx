import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Header.css';

function Header() {
    const { user, isAdmin, isModerator, isAuthenticated, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <header className="header">
            <div className="header-container">
                <Link to="/" className="logo">🏠 Недвижимость</Link>

                <nav className="nav-menu">
                    <Link to="/">Главная</Link>

                    {isAuthenticated && (
                        <Link to="/favorites">Избранное</Link>
                    )}

                    {(isAdmin || isModerator) && (
                        <Link to="/moderation">Модерация</Link>
                    )}

                    {isAdmin && (
                        <Link to="/analytics">Аналитика</Link>
                    )}
                </nav>

                <div className="auth-buttons">
                    {isAuthenticated ? (
                        <>
                            <span className="user-name">
                                👤 {user?.first_name}
                                {isAdmin && <span className="role-badge admin">Admin</span>}
                                {isModerator && !isAdmin && <span className="role-badge moderator">Moderator</span>}
                                {!isAdmin && !isModerator && <span className="role-badge user">User</span>}
                            </span>
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