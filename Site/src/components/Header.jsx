import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Header.css';

function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // Проверка на админа (role_id = 1)
  const isAdmin = user?.role_id === 1;

  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="logo">
          🏠 Недвижимость
        </Link>

        <nav className="nav-menu">
          <Link to="/">Главная</Link>
          {isAdmin && (  // Ссылка на аналитику только для админа
            <Link to="/analytics">Аналитика</Link>
          )}
          {user && (
            <>
              <Link to="/favorites">Избранное</Link>
              <Link to={`/user/${user.user_id}`}>Профиль</Link>
            </>
          )}
        </nav>

        <div className="auth-buttons">
          {user ? (
            <button onClick={logout}>Выйти</button>
          ) : (
            <button onClick={() => navigate('/login')}>Войти</button>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;