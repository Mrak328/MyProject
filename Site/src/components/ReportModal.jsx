import React, { useState } from 'react';
import { createComplaint } from '../services/complaints';

function ReportModal({ listingId, onClose, onSuccess }) {
    const [complaintType, setComplaintType] = useState('');
    const [description, setDescription] = useState('');
    const [loading, setLoading] = useState(false);

    const complaintTypes = [
        { value: 'spam', label: 'Спам' },
        { value: 'fraud', label: 'Мошенничество' },
        { value: 'incorrect_info', label: 'Недостоверная информация' },
        { value: 'duplicate', label: 'Дубликат' },
        { value: 'other', label: 'Другое' }
    ];

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!complaintType) {
            alert('Выберите причину жалобы');
            return;
        }
        setLoading(true);
        try {
            await createComplaint(listingId, complaintType, description);
            alert('Жалоба отправлена');
            if (onSuccess) onSuccess();
            onClose();
        } catch (error) {
            alert('Ошибка при отправке жалобы');
        }
        setLoading(false);
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <h3>Пожаловаться на объявление</h3>
                <form onSubmit={handleSubmit}>
                    <select
                        value={complaintType}
                        onChange={(e) => setComplaintType(e.target.value)}
                        required
                    >
                        <option value="">Выберите причину</option>
                        {complaintTypes.map(t => (
                            <option key={t.value} value={t.value}>{t.label}</option>
                        ))}
                    </select>
                    <textarea
                        placeholder="Дополнительная информация (необязательно)"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        rows="4"
                    />
                    <div className="modal-buttons">
                        <button type="button" onClick={onClose}>Отмена</button>
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