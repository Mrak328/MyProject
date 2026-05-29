import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';
import AddressSelect from '../components/AddressSelect';
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

function CreateListing() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [photosCount, setPhotosCount] = useState(0);
    const fileInputRef = useRef(null);
    const [addressData, setAddressData] = useState({});

    const [form, setForm] = useState({
        title: '', description: '', price: '', total_area: '', rooms: '',
        floor: '', max_floor: '', property_type_id: '1', deal_type_id: '1',
        renovation_condition_id: '', market_type_id: '', contact_person: '',
        contact_phone: '', developer_name: ''
    });

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handlePhotoUpload = (e) => {
        setPhotosCount(e.target.files.length);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const payload = {
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
                developer_name: form.developer_name || undefined,
                ...addressData
            };

            const res = await API.post('/listings/', payload);
            const listingId = res.data.listing_id;

            const files = fileInputRef.current?.files;
            if (files) {
                for (const file of files) {
                    const fd = new FormData();
                    fd.append('file', file);
                    await API.post(`/photos/upload/${listingId}`, fd);
                }
            }

            navigate(`/listing/${listingId}`);
        } catch (err) {
            const msg = err.response?.data?.detail;
            setError(typeof msg === 'string' ? msg : 'Ошибка создания объявления');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="create-listing-page">
            <h1>Создать объявление</h1>
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
                    <label>Адрес</label>
                    <AddressSelect onChange={setAddressData} />
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

                <div className="form-group">
                    <label>Фото</label>
                    <input type="file" multiple accept="image/*" ref={fileInputRef} onChange={handlePhotoUpload} />
                    {photosCount > 0 && <p>Выбрано фото: {photosCount}</p>}
                </div>

                {error && <div className="error-message">{typeof error === 'string' ? error : JSON.stringify(error)}</div>}

                <button type="submit" disabled={loading} className="submit-btn">
                    {loading ? 'Создание...' : 'Опубликовать объявление'}
                </button>
            </form>
        </div>
    );
}

export default CreateListing;