import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import API from '../services/api';
import './Register.css';

function Register() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        first_name: '',
        phone_number: '',
        email: '',
        password: '',
        confirm_password: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.confirm_password) {
            setError('Пароли не совпадают');
            return;
        }

        if (formData.password.length < 6) {
            setError('Пароль должен быть не менее 6 символов');
            return;
        }

        setLoading(true);

        try {
            const response = await API.post('/auth/register', {
                first_name: formData.first_name,
                phone_number: formData.phone_number,
                email: formData.email || null,
                password: formData.password
            });

            localStorage.setItem('token', response.data.access_token);
            navigate('/');
        } catch (err) {
            console.error('Ошибка регистрации:', err);

            // Обрабатываем разные форматы ошибок
            let errorText = 'Ошибка регистрации';

            if (err.response?.data?.detail) {
                // Если detail - объект (валидационная ошибка)
                if (typeof err.response.data.detail === 'object') {
                    errorText = JSON.stringify(err.response.data.detail);
                } else {
                    errorText = err.response.data.detail;
                }
            } else if (err.response?.data?.message) {
                errorText = err.response.data.message;
            } else if (err.message) {
                errorText = err.message;
            }

            setError(errorText);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="register-page">
            <div className="register-container">
                <h1>Регистрация</h1>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Имя *</label>
                        <input
                            type="text"
                            name="first_name"
                            value={formData.first_name}
                            onChange={handleChange}
                            required
                            placeholder="Введите ваше имя"
                        />
                    </div>

                    <div className="form-group">
                        <label>Телефон *</label>
                        <input
                            type="tel"
                            name="phone_number"
                            value={formData.phone_number}
                            onChange={handleChange}
                            required
                            placeholder="+7XXXXXXXXXX"
                        />
                    </div>

                    <div className="form-group">
                        <label>Email (необязательно)</label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="example@mail.com"
                        />
                    </div>

                    <div className="form-group">
                        <label>Пароль *</label>
                        <input
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            placeholder="Не менее 6 символов"
                        />
                    </div>

                    <div className="form-group">
                        <label>Подтверждение пароля *</label>
                        <input
                            type="password"
                            name="confirm_password"
                            value={formData.confirm_password}
                            onChange={handleChange}
                            required
                            placeholder="Повторите пароль"
                        />
                    </div>

                    {error && <div className="error-message">{error}</div>}

                    <button type="submit" disabled={loading}>
                        {loading ? 'Регистрация...' : 'Зарегистрироваться'}
                    </button>
                </form>

                <p className="login-link">
                    Уже есть аккаунт? <Link to="/login">Войти</Link>
                </p>
            </div>
        </div>
    );
}

export default Register;