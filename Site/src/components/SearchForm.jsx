import React, { useState, useEffect } from 'react';
import AddressSelect from './AddressSelect';
import './SearchForm.css';

const PROPERTY_TYPES = [
    { id: 1, label: 'Квартира' }, { id: 2, label: 'Дом' }, { id: 3, label: 'Комната' },
    { id: 4, label: 'Офис' }, { id: 5, label: 'Участок' }
];

const RENOVATION_CONDITIONS = [
    { id: 1, label: 'Без ремонта' }, { id: 2, label: 'Косметический' },
    { id: 3, label: 'Евроремонт' }, { id: 4, label: 'Дизайнерский' }
];

const INITIAL_FILTERS = {
    query: '', city: 'Киров', minPrice: '', maxPrice: '', minArea: '', maxArea: '',
    rooms: null, floor: '', dealTypeId: '', propertyTypeId: '', renovationId: '',
    sortBy: 'date_desc', city_id: '', region_id: '', country_id: ''
};

function SearchForm({ filters, onFilterChange }) {
    const [localFilters, setLocalFilters] = useState({ ...INITIAL_FILTERS, ...filters });
    const [filtersOpen, setFiltersOpen] = useState(false);

    useEffect(() => {
        setLocalFilters((prev) => ({ ...prev, ...filters }));
    }, [filters]);

    const updateFilter = (name, value) => {
        const updated = { ...localFilters, [name]: value };
        setLocalFilters(updated);
        onFilterChange(updated);
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        updateFilter(name, value);
    };

    const handleNumberChange = (e) => {
        const { name, value } = e.target;
        updateFilter(name, value === '' ? '' : Number(value));
    };

    const handleRoomsChange = (rooms) => {
        updateFilter('rooms', localFilters.rooms === rooms ? null : rooms);
    };

    const handleAddressChange = (address) => {
        const updated = { ...localFilters, ...address };
        setLocalFilters(updated);
        onFilterChange(updated);
    };

    const handleReset = () => {
        setLocalFilters({ ...INITIAL_FILTERS });
        onFilterChange({ ...INITIAL_FILTERS });
    };

    return (
        <div className="search-container">
            <div className="search-bar">
                <input type="text" name="query" placeholder="Поиск по заголовку или описанию" value={localFilters.query} onChange={handleChange} className="search-input" />
                <button type="button" className={`toggle-filters-btn ${filtersOpen ? 'open' : ''}`} onClick={() => setFiltersOpen(!filtersOpen)}>
                    Фильтры <span className="arrow">▼</span>
                </button>
            </div>

            <div className={`filters-wrapper ${filtersOpen ? 'open' : ''}`}>
                <div className="filters-row">
                    <AddressSelect onChange={handleAddressChange} />

                    <select value={localFilters.sortBy} onChange={handleChange} name="sortBy" className="filter-select">
                        <option value="date_desc">📅 Сначала новые</option>
                        <option value="price_asc">💰 Сначала дешевле</option>
                        <option value="price_desc">💰 Сначала дороже</option>
                        <option value="views_desc">👁 Популярные</option>
                    </select>

                    <select value={localFilters.rooms || ''} onChange={(e) => handleRoomsChange(e.target.value ? Number(e.target.value) : null)} className="filter-select">
                        <option value="">Все комнаты</option>
                        <option value="1">1 комната</option>
                        <option value="2">2 комнаты</option>
                        <option value="3">3 комнаты</option>
                        <option value="4">4+ комнат</option>
                    </select>

                    <input type="number" name="minPrice" placeholder="Цена от" value={localFilters.minPrice} onChange={handleNumberChange} className="filter-input" />
                    <input type="number" name="maxPrice" placeholder="Цена до" value={localFilters.maxPrice} onChange={handleNumberChange} className="filter-input" />
                    <input type="number" name="minArea" placeholder="Площадь от" value={localFilters.minArea} onChange={handleNumberChange} className="filter-input" />
                    <input type="number" name="maxArea" placeholder="Площадь до" value={localFilters.maxArea} onChange={handleNumberChange} className="filter-input" />
                    <input type="number" name="floor" placeholder="Этаж" value={localFilters.floor} onChange={handleNumberChange} className="filter-input" />

                    <select name="dealTypeId" value={localFilters.dealTypeId} onChange={handleChange} className="filter-select">
                        <option value="">Сделка</option>
                        <option value="1">Продажа</option>
                        <option value="2">Аренда</option>
                    </select>

                    <select name="propertyTypeId" value={localFilters.propertyTypeId} onChange={handleChange} className="filter-select">
                        <option value="">Тип недвижимости</option>
                        {PROPERTY_TYPES.map((t) => (<option key={t.id} value={t.id}>{t.label}</option>))}
                    </select>

                    <select name="renovationId" value={localFilters.renovationId} onChange={handleChange} className="filter-select">
                        <option value="">Ремонт</option>
                        {RENOVATION_CONDITIONS.map((r) => (<option key={r.id} value={r.id}>{r.label}</option>))}
                    </select>

                    <button className="reset-btn" onClick={handleReset} type="button" title="Сбросить фильтры">✖</button>
                </div>
            </div>
        </div>
    );
}

export default SearchForm;