import React, { useState, useEffect, useCallback } from 'react';
import API from '../services/api';
import './AdminActivity.css';

const ACTION_LABELS = {
    1: 'Просмотр', 2: 'Создание', 3: 'Редактирование', 4: 'Удаление',
    5: 'Избранное/Отзыв', 6: 'Комментарий', 7: 'Звонок', 8: 'Жалоба',
    9: 'Регистрация', 10: 'Вход'
};

function AdminActivity() {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchId, setSearchId] = useState('');

    const loadAllLogs = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await API.get('/activity/all');
            setLogs(res.data || []);
        } catch {
            setError('Ошибка загрузки логов');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadAllLogs();
    }, [loadAllLogs]);

    const searchByUser = async () => {
        if (!searchId) return;
        setLoading(true);
        setError(null);
        try {
            const res = await API.get(`/activity/user/${searchId}`);
            setLogs(res.data || []);
        } catch {
            setError('Пользователь не найден или ошибка');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="admin-activity-page">
            <h1>История действий</h1>

            <div className="activity-toolbar">
                <button onClick={loadAllLogs} className="btn-refresh">🔄 Все логи</button>

                <div className="activity-search">
                    <input
                        type="number"
                        placeholder="ID пользователя"
                        value={searchId}
                        onChange={e => setSearchId(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && searchByUser()}
                    />
                    <button onClick={searchByUser}>Найти</button>
                </div>
            </div>

            {loading && <div className="loader">Загрузка...</div>}
            {error && <div className="error">{error}</div>}

            {logs.length > 0 && (
                <table className="logs-table">
                    <thead>
                        <tr>
                            <th>Дата</th>
                            <th>Пользователь</th>
                            <th>Действие</th>
                            <th>ID объявления</th>
                            <th>IP</th>
                        </tr>
                    </thead>
                    <tbody>
                        {logs.map(log => (
                            <tr key={log.log_id}>
                                <td>{new Date(log.action_datetime).toLocaleString('ru-RU')}</td>
                                <td>{log.user_id || '-'}</td>
                                <td>{ACTION_LABELS[log.action_type_id] || log.action_type_id}</td>
                                <td>{log.listing_id || '-'}</td>
                                <td>{log.ip_address || '-'}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}

            {logs.length === 0 && !loading && (
                <p className="no-data">Нет записей</p>
            )}
        </div>
    );
}

export default AdminActivity;