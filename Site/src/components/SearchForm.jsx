import React, { useState } from 'react';
import './SearchForm.css';

function SearchForm({ filters, onFilterChange }) {
    const [localFilters, setLocalFilters] = useState(filters);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setLocalFilters(prev => ({ ...prev, [name]: value }));
        onFilterChange({ ...filters, [name]: value });
    };

    const handleRoomsChange = (rooms) => {
        const newValue = localFilters.rooms === rooms ? null : rooms;
        setLocalFilters(prev => ({ ...prev, rooms: newValue }));
        onFilterChange({ ...filters, rooms: newValue });
    };

    const handleSortChange = (sortBy) => {
        setLocalFilters(prev => ({ ...prev, sortBy }));
        onFilterChange({ ...filters, sortBy });
    };

    const handleReset = () => {
        const emptyFilters = {
            query: '', city: '', minPrice: '', maxPrice: '', minArea: '', maxArea: '',
            rooms: null, floor: '', maxFloor: '', renovationId: '', propertyTypeId: '', dealTypeId: '', sortBy: 'date_desc'
        };
        setLocalFilters(emptyFilters);
        onFilterChange(emptyFilters);
    };

    return (
        <div className="search-container">
            {/* ПОИСКОВАЯ СТРОКА */}
            <div className="search-bar">
                <input
                    type="text"
                    name="query"
                    placeholder="Поиск по заголовку или описанию"
                    value={localFilters.query || ''}
                    onChange={handleChange}
                    className="search-input"
                />
                <input
                    type="text"
                    name="city"
                    placeholder="Город или район"
                    value={localFilters.city || ''}
                    onChange={handleChange}
                    className="search-input"
                />
            </div>

            {/* ВСЕ ФИЛЬТРЫ В ОДНУ СТРОКУ */}
            <div className="filters-row">
                {/* Сортировка */}
                <div className="filter-group">
                    <select
                        value={localFilters.sortBy || 'date_desc'}
                        onChange={(e) => handleSortChange(e.target.value)}
                        className="filter-select"
                    >
                        <option value="date_desc">📅 Сначала новые</option>
                        <option value="price_asc">💰 Сначала дешевле</option>
                        <option value="price_desc">💰 Сначала дороже</option>
                        <option value="views_desc">👁 Популярные</option>
                    </select>
                </div>

                {/* Комнаты */}
                <div className="filter-group">
                    <select
                        value={localFilters.rooms || ''}
                        onChange={(e) => handleRoomsChange(e.target.value ? parseInt(e.target.value) : null)}
                        className="filter-select"
                    >
                        <option value="">Все комнаты</option>
                        <option value="1">1 комната</option>
                        <option value="2">2 комнаты</option>
                        <option value="3">3 комнаты</option>
                        <option value="4">4+ комнат</option>
                    </select>
                </div>

                {/* Цена от */}
                <div className="filter-group">
                    <input
                        type="number"
                        name="minPrice"
                        placeholder="Цена от"
                        value={localFilters.minPrice || ''}
                        onChange={handleChange}
                        className="filter-input"
                    />
                </div>

                {/* Цена до */}
                <div className="filter-group">
                    <input
                        type="number"
                        name="maxPrice"
                        placeholder="Цена до"
                        value={localFilters.maxPrice || ''}
                        onChange={handleChange}
                        className="filter-input"
                    />
                </div>

                {/* Площадь от */}
                <div className="filter-group">
                    <input
                        type="number"
                        name="minArea"
                        placeholder="Площадь от"
                        value={localFilters.minArea || ''}
                        onChange={handleChange}
                        className="filter-input"
                    />
                </div>

                {/* Площадь до */}
                <div className="filter-group">
                    <input
                        type="number"
                        name="maxArea"
                        placeholder="Площадь до"
                        value={localFilters.maxArea || ''}
                        onChange={handleChange}
                        className="filter-input"
                    />
                </div>

                {/* Этаж */}
                <div className="filter-group">
                    <input
                        type="number"
                        name="floor"
                        placeholder="Этаж"
                        value={localFilters.floor || ''}
                        onChange={handleChange}
                        className="filter-input"
                    />
                </div>

                {/* Этажность */}
                <div className="filter-group">
                    <input
                        type="number"
                        name="maxFloor"
                        placeholder="Этажность"
                        value={localFilters.maxFloor || ''}
                        onChange={handleChange}
                        className="filter-input"
                    />
                </div>

                {/* Состояние ремонта */}
                <div className="filter-group">
                    <select
                        name="renovationId"
                        value={localFilters.renovationId || ''}
                        onChange={handleChange}
                        className="filter-select"
                    >
                        <option value="">Ремонт</option>
                        <option value="1">Нет ремонта</option>
                        <option value="2">Косметический</option>
                        <option value="3">Евроремонт</option>
                        <option value="4">Дизайнерский</option>
                    </select>
                </div>

                {/* Тип недвижимости */}
                <div className="filter-group">
                    <select
                        name="propertyTypeId"
                        value={localFilters.propertyTypeId || ''}
                        onChange={handleChange}
                        className="filter-select"
                    >
                        <option value="">Тип</option>
                        <option value="1">Квартира</option>
                        <option value="2">Дом</option>
                        <option value="3">Комната</option>
                        <option value="4">Участок</option>
                    </select>
                </div>

                {/* Тип сделки */}
                <div className="filter-group">
                    <select
                        name="dealTypeId"
                        value={localFilters.dealTypeId || ''}
                        onChange={handleChange}
                        className="filter-select"
                    >
                        <option value="">Сделка</option>
                        <option value="1">Продажа</option>
                        <option value="2">Аренда</option>
                    </select>
                </div>

                {/* Кнопка сброса */}
                <button className="reset-btn" onClick={handleReset}>
                    ✖
                </button>
            </div>
        </div>
    );
}

export default SearchForm;