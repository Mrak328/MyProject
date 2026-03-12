import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Login() {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    // Временная заглушка
    login({ user_id: 1, name: 'Тестовый пользователь' }, 'fake-token');
    navigate('/');
  };

  return (
    <div className="login-page">
      <h2>Вход</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <input
            type="tel"
            placeholder="Телефон"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />
        </div>
        <div>
          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button type="submit">Войти</button>
      </form>
    </div>
  );
}

export default Login;