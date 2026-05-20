import React, { useState, useEffect, useCallback } from 'react';
import API from '../services/api';
import './AdminUsers.css';

function AdminUsers() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedUser, setSelectedUser] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [blockReason, setBlockReason] = useState('');

    const loadUsers = useCallback(async () => {
        setLoading(true);
        try {
            const res = await API.get('/admin/users');
            setUsers(res.data || []);
        } catch {
            setError('Ошибка загрузки пользователей');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { loadUsers(); }, [loadUsers]);

    const handleBlock = async () => {
        if (!blockReason) return;
        try {
            await API.post(`/admin/users/${selectedUser.user_id}/block`, {
                violation_type_id: 1,
                description: blockReason
            });
            setShowModal(false);
            setBlockReason('');
            loadUsers();
        } catch {
            alert('Ошибка блокировки');
        }
    };

    const handleUnblock = async (userId) => {
        try {
            await API.put(`/admin/users/${userId}/unblock`);
            loadUsers();
        } catch {
            alert('Ошибка разблокировки');
        }
    };

    const openBlockModal = (user) => {
        setSelectedUser(user);
        setShowModal(true);
    };

    const roleLabels = { 1: 'Админ', 2: 'Модератор', 3: 'Пользователь', 4: 'Риэлтор', 5: 'Застройщик' };

    if (loading) return <div className="loader">Загрузка...</div>;
    if (error) return <div className="error">{error}</div>;

    return (
        <div className="admin-users-page">
            <h1>Пользователи</h1>

            <table className="users-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Имя</th>
                        <th>Телефон</th>
                        <th>Email</th>
                        <th>Роль</th>
                        <th>Дата регистрации</th>
                    </tr>
                </thead>
                <tbody>
                    {users.map(u => (
                        <tr key={u.user_id}>
                            <td>{u.user_id}</td>
                            <td>{u.first_name}</td>
                            <td>{u.phone_number}</td>
                            <td>{u.email || '-'}</td>
                            <td>{roleLabels[u.role_id] || u.role_id}</td>
                            <td>{new Date(u.registration_date).toLocaleDateString('ru-RU')}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default AdminUsers;