import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Header.css';

function Header() {
    const { user, isAuthenticated, logout } = useAuth();
    const navigate = useNavigate();
    const isAdmin = user?.role_id === 1;
    const isModerator = user?.role_id === 2;

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <header className="header">
            <div className="header-container">
                <Link to="/" className="logo">Aviko</Link>

                <nav className="nav-menu">
                    <Link to="/">Главная</Link>
                    {isAuthenticated && <Link to="/favorites">Избранное</Link>}
                    {isAuthenticated && <Link to="/create-listing">+ Разместить</Link>}
                    {isAuthenticated && <Link to="/chats">Чат</Link>}
                    {(isAdmin || isModerator) && <Link to="/moderation">Модерация</Link>}
                    {isAdmin && <Link to="/admin">Админ</Link>}
                </nav>

                <div className="auth-buttons">
                    {isAuthenticated ? (
                        <>
                            <Link to={`/user/${user.user_id}`} className="user-name">{user.first_name}</Link>
                            <button onClick={handleLogout} className="logout-btn">Выйти</button>
                        </>
                    ) : (
                        <button onClick={() => navigate('/login')} className="login-btn">Войти</button>
                    )}
                </div>
            </div>
        </header>
    );
}

export default Header;