import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import API from '../services/api';
import { useAuth } from '../context/AuthContext';
import './CreateListing.css';

const PROPERTY_TYPES = [
    { id: 1, label: 'Квартира' }, { id: 2, label: 'Дом' }, { id: 3, label: 'Комната' },
    { id: 4, label: 'Офис' }, { id: 5, label: 'Участок' }
];

const RENOVATION_CONDITIONS = [
    { id: 1, label: 'Без ремонта' }, { id: 2, label: 'Косметический' },
    { id: 3, label: 'Евроремонт' }, { id: 4, label: 'Дизайнерский' },
    { id: 5, label: 'Черновая отделка' }, { id: 6, label: 'Предчистовая' },
    { id: 7, label: 'Чистовая' }
];

function EditListing() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [existingPhotos, setExistingPhotos] = useState([]);
    const [newPhotos, setNewPhotos] = useState([]);

    const [form, setForm] = useState({
        title: '', description: '', price: '', total_area: '', rooms: '',
        floor: '', max_floor: '', property_type_id: '1', deal_type_id: '1',
        renovation_condition_id: '', market_type_id: '', contact_person: '',
        contact_phone: '', developer_name: ''
    });

    useEffect(() => { loadListing(); }, [id]);

    const loadListing = async () => {
        try {
            const res = await API.get(`/listings/${id}`);
            const l = res.data;
            if (l.user_id !== user?.user_id) {
                setError('Нет доступа к этому объявлению');
                setLoading(false);
                return;
            }
            setForm({
                title: l.title || '',
                description: l.description || '',
                price: l.price || '',
                total_area: l.total_area || '',
                rooms: l.rooms || '',
                floor: l.floor || '',
                max_floor: l.max_floor || '',
                property_type_id: String(l.property_type_id || '1'),
                deal_type_id: String(l.deal_type_id || '1'),
                renovation_condition_id: l.renovation_condition_id ? String(l.renovation_condition_id) : '',
                market_type_id: l.market_type_id ? String(l.market_type_id) : '',
                contact_person: l.contact_person || '',
                contact_phone: l.contact_phone || '',
                developer_name: l.developer_name || ''
            });
            setExistingPhotos(l.photos || []);
        } catch {
            setError('Ошибка загрузки объявления');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handlePhotoUpload = (e) => {
        setNewPhotos(Array.from(e.target.files));
    };

    const deletePhoto = async (photoUrl) => {
        try {
            const photosRes = await API.get(`/listings/${id}/photos`);
            const photo = photosRes.data.find(p => p.file_url === photoUrl);
            if (photo) {
                await API.delete(`/photos/${photo.photo_id}`);
                setExistingPhotos(prev => prev.filter(p => p !== photoUrl));
            }
        } catch {
            alert('Ошибка удаления фото');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setError('');

        try {
            await API.put(`/listings/${id}`, {
                title: form.title,
                description: form.description,
                price: Number(form.price),
                total_area: form.total_area ? Number(form.total_area) : undefined,
                rooms: form.rooms ? Number(form.rooms) : undefined,
                floor: form.floor ? Number(form.floor) : undefined,
                max_floor: form.max_floor ? Number(form.max_floor) : undefined,
                property_type_id: Number(form.property_type_id),
                deal_type_id: Number(form.deal_type_id),
                renovation_condition_id: form.renovation_condition_id ? Number(form.renovation_condition_id) : undefined,
                market_type_id: form.market_type_id ? Number(form.market_type_id) : undefined,
                contact_person: form.contact_person || user?.first_name,
                contact_phone: form.contact_phone || user?.phone_number,
                developer_name: form.developer_name || undefined
            });

            for (const file of newPhotos) {
                const fd = new FormData();
                fd.append('file', file);
                await API.post(`/photos/upload/${id}`, fd);
            }

            navigate(`/listing/${id}`);
        } catch (err) {
            const msg = err.response?.data?.detail;
            setError(typeof msg === 'string' ? msg : 'Ошибка сохранения');
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="loader">Загрузка...</div>;

    return (
        <div className="create-listing-page">
            <h1>Редактирование объявления</h1>

            <form onSubmit={handleSubmit} className="create-listing-form">
                <div className="form-group">
                    <label>Название</label>
                    <input type="text" name="title" value={form.title} onChange={handleChange} required />
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label>Тип недвижимости</label>
                        <select name="property_type_id" value={form.property_type_id} onChange={handleChange}>
                            {PROPERTY_TYPES.map(t => <option key={t.id} value={t.id}>{t.label}</option>)}
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Тип сделки</label>
                        <select name="deal_type_id" value={form.deal_type_id} onChange={handleChange}>
                            <option value="1">Продажа</option>
                            <option value="2">Аренда</option>
                        </select>
                    </div>
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label>Цена, ₽</label>
                        <input type="number" name="price" value={form.price} onChange={handleChange} required />
                    </div>
                    <div className="form-group">
                        <label>Площадь, м²</label>
                        <input type="number" name="total_area" value={form.total_area} onChange={handleChange} />
                    </div>
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label>Комнат</label>
                        <input type="number" name="rooms" value={form.rooms} onChange={handleChange} min="1" max="10" />
                    </div>
                    <div className="form-group">
                        <label>Этаж</label>
                        <input type="number" name="floor" value={form.floor} onChange={handleChange} />
                    </div>
                    <div className="form-group">
                        <label>Этажность</label>
                        <input type="number" name="max_floor" value={form.max_floor} onChange={handleChange} />
                    </div>
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label>Ремонт</label>
                        <select name="renovation_condition_id" value={form.renovation_condition_id} onChange={handleChange}>
                            <option value="">Не выбрано</option>
                            {RENOVATION_CONDITIONS.map(r => <option key={r.id} value={r.id}>{r.label}</option>)}
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Рынок</label>
                        <select name="market_type_id" value={form.market_type_id} onChange={handleChange}>
                            <option value="">Не выбрано</option>
                            <option value="1">Новостройка</option>
                            <option value="2">Вторичка</option>
                        </select>
                    </div>
                </div>

                <div className="form-group">
                    <label>Описание</label>
                    <textarea name="description" value={form.description} onChange={handleChange} rows="4" />
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label>Контактное лицо</label>
                        <input type="text" name="contact_person" value={form.contact_person} onChange={handleChange} />
                    </div>
                    <div className="form-group">
                        <label>Телефон</label>
                        <input type="text" name="contact_phone" value={form.contact_phone} onChange={handleChange} />
                    </div>
                </div>

                <div className="form-group">
                    <label>Застройщик</label>
                    <input type="text" name="developer_name" value={form.developer_name} onChange={handleChange} />
                </div>

                {existingPhotos.length > 0 && (
                    <div className="form-group">
                        <label>Текущие фото</label>
                        <div className="existing-photos">
                            {existingPhotos.map((url, i) => (
                                <div key={i} className="photo-thumb">
                                    <img src={url} alt={`Фото ${i + 1}`} />
                                    <button type="button" className="btn-delete-photo" onClick={() => deletePhoto(url)}>✖</button>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                <div className="form-group">
                    <label>Добавить фото</label>
                    <input type="file" multiple accept="image/*" onChange={handlePhotoUpload} />
                    {newPhotos.length > 0 && <p>Новых фото: {newPhotos.length}</p>}
                </div>

                {error && <div className="error-message">{typeof error === 'string' ? error : JSON.stringify(error)}</div>}

                <div className="form-actions">
                    <button type="button" className="btn-cancel" onClick={() => navigate(`/listing/${id}`)}>Отмена</button>
                    <button type="submit" className="btn-submit" disabled={saving}>
                        {saving ? 'Сохранение...' : 'Сохранить'}
                    </button>
                </div>
            </form>
        </div>
    );
}

export default EditListing;