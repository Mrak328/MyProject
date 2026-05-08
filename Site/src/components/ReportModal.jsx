import React, { useState } from 'react';
import { createComplaint } from '../services/complaints';

// Маппинг complaint_type_id из БД
const COMPLAINT_TYPES = [
    { id: 1, label: 'Спам' },
    { id: 2, label: 'Мошенничество' },
    { id: 3, label: 'Неактуальное объявление' },
    { id: 4, label: 'Оскорбление' },
    { id: 5, label: 'Запрещённый контент' },
    { id: 6, label: 'Дубликат' },
    { id: 7, label: 'Неверная цена' },
    { id: 8, label: 'Чужие фото' },
    { id: 9, label: 'Фишинг' },
    { id: 10, label: 'Другое' }
];

function ReportModal({ listingId, onClose, onSuccess }) {
    const [complaintTypeId, setComplaintTypeId] = useState('');
    const [description, setDescription] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!complaintTypeId) {
            setError('Выберите причину жалобы');
            return;
        }
        setLoading(true);
        setError('');
        try {
            await createComplaint(listingId, Number(complaintTypeId), description);
            onSuccess?.();
            onClose();
        } catch (err) {
            setError(err.response?.data?.detail || 'Ошибка при отправке жалобы');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <h3>Пожаловаться на объявление</h3>
                <form onSubmit={handleSubmit}>
                    <select
                        value={complaintTypeId}
                        onChange={(e) => setComplaintTypeId(e.target.value)}
                        required
                    >
                        <option value="">Выберите причину</option>
                        {COMPLAINT_TYPES.map((t) => (
                            <option key={t.id} value={t.id}>{t.label}</option>
                        ))}
                    </select>

                    <textarea
                        placeholder="Дополнительная информация (необязательно)"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        rows="4"
                        maxLength={500}
                    />

                    {error && <p className="modal-error">{error}</p>}

                    <div className="modal-buttons">
                        <button type="button" onClick={onClose} disabled={loading}>
                            Отмена
                        </button>
                        <button type="submit" disabled={loading}>
                            {loading ? 'Отправка...' : 'Отправить жалобу'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default ReportModal;