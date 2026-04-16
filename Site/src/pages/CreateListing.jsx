import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';
import { useAuth } from '../context/AuthContext';
import './CreateListing.css';

function CreateListing() {
    const { isAuthenticated } = useAuth();
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        title: '',
        description: '',
        price: '',
        address: '',
        total_area: '',
        rooms: '',
        property_type_id: 1,
        deal_type_id: 1,
        contact_phone: '',
        contact_person: ''
    });
    const [photos, setPhotos] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Проверка авторизации
    if (!isAuthenticated) {
        navigate('/login');
        return null;
    }

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handlePhotoUpload = async (e) => {
        const files = Array.from(e.target.files);
        setPhotos([...photos, ...files]);
    };

    const removePhoto = (index) => {
        setPhotos(photos.filter((_, i) => i !== index));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // Сначала создаем объявление
            const listingResponse = await API.post('/listings/', {
                title: formData.title,
                description: formData.description,
                price: parseFloat(formData.price),
                address: formData.address,
                total_area: formData.total_area ? parseFloat(formData.total_area) : null,
                rooms: formData.rooms ? parseInt(formData.rooms) : null,
                property_type_id: parseInt(formData.property_type_id),
                deal_type_id: parseInt(formData.deal_type_id),
                contact_phone: formData.contact_phone,
                contact_person: formData.contact_person
            });

            const listingId = listingResponse.data.listing_id;

            // Загружаем фото
            if (photos.length > 0) {
                for (const photo of photos) {
                    const formDataPhoto = new FormData();
                    formDataPhoto.append('file', photo);
                    await API.post(`/photos/upload/${listingId}`, formDataPhoto, {
                        headers: { 'Content-Type': 'multipart/form-data' }
                    });
                }
            }

            navigate(`/listing/${listingId}`);
        } catch (err) {
            setError(err.response?.data?.detail || 'Ошибка создания объявления');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="create-listing-page">
            <div className="create-listing-container">
                <h1>Создание объявления</h1>

                <form onSubmit={handleSubmit}>
                    <div className="form-section">
                        <h3>Основная информация</h3>

                        <div className="form-group">
                            <label>Название *</label>
                            <input
                                type="text"
                                name="title"
                                value={formData.title}
                                onChange={handleChange}
                                required
                                placeholder="Например: 2-комнатная квартира в центре"
                            />
                        </div>

                        <div className="form-group">
                            <label>Описание</label>
                            <textarea
                                name="description"
                                value={formData.description}
                                onChange={handleChange}
                                rows="5"
                                placeholder="Подробное описание объекта..."
                            />
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Цена *</label>
                                <input
                                    type="number"
                                    name="price"
                                    value={formData.price}
                                    onChange={handleChange}
                                    required
                                    placeholder="Сумма в рублях"
                                />
                            </div>

                            <div className="form-group">
                                <label>Площадь, м²</label>
                                <input
                                    type="number"
                                    name="total_area"
                                    value={formData.total_area}
                                    onChange={handleChange}
                                    placeholder="Общая площадь"
                                />
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Количество комнат</label>
                                <select
                                    name="rooms"
                                    value={formData.rooms}
                                    onChange={handleChange}
                                >
                                    <option value="">Не указано</option>
                                    <option value="1">1 комната</option>
                                    <option value="2">2 комнаты</option>
                                    <option value="3">3 комнаты</option>
                                    <option value="4">4+ комнат</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label>Тип недвижимости *</label>
                                <select
                                    name="property_type_id"
                                    value={formData.property_type_id}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="1">Квартира</option>
                                    <option value="2">Дом</option>
                                    <option value="3">Комната</option>
                                    <option value="4">Участок</option>
                                </select>
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Тип сделки *</label>
                                <select
                                    name="deal_type_id"
                                    value={formData.deal_type_id}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="1">Продажа</option>
                                    <option value="2">Аренда</option>
                                </select>
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Адрес *</label>
                            <input
                                type="text"
                                name="address"
                                value={formData.address}
                                onChange={handleChange}
                                required
                                placeholder="Город, улица, дом"
                            />
                        </div>
                    </div>

                    <div className="form-section">
                        <h3>Контактная информация</h3>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Контактный телефон *</label>
                                <input
                                    type="tel"
                                    name="contact_phone"
                                    value={formData.contact_phone}
                                    onChange={handleChange}
                                    required
                                    placeholder="+7XXXXXXXXXX"
                                />
                            </div>

                            <div className="form-group">
                                <label>Контактное лицо</label>
                                <input
                                    type="text"
                                    name="contact_person"
                                    value={formData.contact_person}
                                    onChange={handleChange}
                                    placeholder="Как к вам обращаться"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="form-section">
                        <h3>Фотографии</h3>

                        <div className="photo-upload">
                            <input
                                type="file"
                                accept="image/*"
                                multiple
                                onChange={handlePhotoUpload}
                                className="file-input"
                            />

                            <div className="photo-preview">
                                {photos.map((photo, index) => (
                                    <div key={index} className="photo-item">
                                        <img src={URL.createObjectURL(photo)} alt="preview" />
                                        <button type="button" onClick={() => removePhoto(index)}>✖</button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {error && <div className="error-message">{error}</div>}

                    <div className="form-buttons">
                        <button type="button" onClick={() => navigate(-1)} className="cancel-btn">
                            Отмена
                        </button>
                        <button type="submit" disabled={loading}>
                            {loading ? 'Публикация...' : 'Опубликовать объявление'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default CreateListing;