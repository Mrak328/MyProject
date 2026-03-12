import React from 'react';
import './SearchForm.css';

function SearchForm({ filters, onFilterChange }) {

  const handleChange = (e) => {
    const { name, value } = e.target;
    // Сразу вызываем onFilterChange с обновленными фильтрами
    onFilterChange({
      ...filters,
      [name]: value
    });
  };

  return (
    <form className="search-form" onSubmit={(e) => e.preventDefault()}>
      <div className="search-row">
        <input
          type="text"
          name="city"
          placeholder="Город или район"
          value={filters.city || ''}
          onChange={handleChange}
          className="search-input city-input"
        />
      </div>

      <div className="search-row">
        <select
          name="dealType"
          value={filters.dealType || 'sale'}
          onChange={handleChange}
          className="search-select"
        >
          <option value="sale">Купить</option>
          <option value="rent">Снять</option>
        </select>

        <select
          name="rooms"
          value={filters.rooms || ''}
          onChange={handleChange}
          className="search-select"
        >
          <option value="">Все комнаты</option>
          <option value="1">1 комната</option>
          <option value="2">2 комнаты</option>
          <option value="3">3 комнаты</option>
          <option value="4">4+ комнат</option>
        </select>

        <input
          type="number"
          name="minPrice"
          placeholder="Цена от"
          value={filters.minPrice || ''}
          onChange={handleChange}
          className="search-input price-input"
        />

        <input
          type="number"
          name="maxPrice"
          placeholder="Цена до"
          value={filters.maxPrice || ''}
          onChange={handleChange}
          className="search-input price-input"
        />
      </div>
    </form>
  );
}

export default SearchForm;