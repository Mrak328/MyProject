import React, { useState } from 'react';
import { useNavigate, Navigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Login.css';

function Login() {
    const [emailOrPhone, setEmailOrPhone] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const { login, error, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    if (isAuthenticated) {
        return <Navigate to="/" replace />;
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        const success = await login(emailOrPhone, password);
        if (success) {
            navigate('/');
        }

        setLoading(false);
    };

    return (
        <div className="login-page">
            <div className="login-container">
                <div className="login-header">
                    <h1>Добро пожаловать</h1>
                    <p>Войдите в свой аккаунт</p>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Email или Телефон</label>
                        <div className="input-icon">
                            <input
                                type="text"
                                value={emailOrPhone}
                                onChange={(e) => setEmailOrPhone(e.target.value)}
                                placeholder="admin@example.com или +79999999999"
                                required
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Пароль</label>
                        <div className="input-icon">
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Введите пароль"
                                required
                            />
                        </div>
                    </div>

                    {error && <div className="error-message">{error}</div>}

                    <button type="submit" disabled={loading} className="login-submit">
                        {loading ? 'Вход...' : 'Войти'}
                    </button>
                </form>

                <div className="login-footer">
                    <p>
                        Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
                    </p>
                    <p className="demo-info">
                        <strong>Тестовые данные:</strong><br />
                        Админ: admin@example.com / admin123<br />
                        Модератор: moderator@example.com / mod123<br />
                        Пользователь: user@example.com / user123
                    </p>
                </div>
            </div>
        </div>
    );
}

export default Login;