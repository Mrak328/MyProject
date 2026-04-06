import API from './api';

// Получить все активные объявления
export const getAllListings = async (page = 1, pageSize = 20) => {
    try {
        const response = await API.get(`/listings/search?page=${page}&page_size=${pageSize}`);
        return response.data;
    } catch (error) {
        console.error('Ошибка загрузки:', error);
        return { items: [], total: 0, page: 1, pages: 0 };
    }
};

// Расширенный поиск с фильтрами
export const searchListings = async (filters, page = 1, pageSize = 20) => {
    try {
        const params = new URLSearchParams();

        // Базовая пагинация
        params.append('page', page);
        params.append('page_size', pageSize);

        // Поиск по тексту
        if (filters.query) params.append('query', filters.query);

        // Локация
        if (filters.city) params.append('city', filters.city);
        if (filters.district) params.append('district', filters.district);
        if (filters.metro) params.append('metro', filters.metro);

        // Цена
        if (filters.minPrice) params.append('min_price', filters.minPrice);
        if (filters.maxPrice) params.append('max_price', filters.maxPrice);

        // Площадь
        if (filters.minArea) params.append('min_area', filters.minArea);
        if (filters.maxArea) params.append('max_area', filters.maxArea);

        // Характеристики
        if (filters.rooms) params.append('rooms', filters.rooms);
        if (filters.floor !== undefined && filters.floor !== '') params.append('floor', filters.floor);
        if (filters.maxFloor) params.append('max_floor', filters.maxFloor);

        // Типы
        if (filters.propertyTypeId) params.append('property_type_id', filters.propertyTypeId);
        if (filters.dealTypeId) params.append('deal_type_id', filters.dealTypeId);
        if (filters.renovationId) params.append('renovation_condition_id', filters.renovationId);

        // Дополнительные опции
        if (filters.hasFurniture !== undefined && filters.hasFurniture !== '')
            params.append('has_furniture', filters.hasFurniture);
        if (filters.hasParking !== undefined && filters.hasParking !== '')
            params.append('has_parking', filters.hasParking);
        if (filters.hasBalcony !== undefined && filters.hasBalcony !== '')
            params.append('has_balcony', filters.hasBalcony);
        if (filters.petsAllowed !== undefined && filters.petsAllowed !== '')
            params.append('pets_allowed', filters.petsAllowed);

        // Сортировка
        if (filters.sortBy) params.append('sort_by', filters.sortBy);

        const response = await API.get(`/listings/search?${params}`);
        return response.data;
    } catch (error) {
        console.error('Ошибка поиска:', error);
        return { items: [], total: 0, page: 1, pages: 0 };
    }
};

// Получить одно объявление
export const getListingDetail = async (id) => {
    try {
        const response = await API.get(`/listings/${id}`);
        return response.data;
    } catch (error) {
        console.error('Ошибка загрузки объявления:', error);
        return null;
    }
};

// Получить контакты продавца
export const getListingContacts = async (id) => {
    try {
        const response = await API.get(`/listings/${id}/contacts`);
        return response.data;
    } catch (error) {
        console.error('Ошибка загрузки контактов:', error);
        return null;
    }
};

// Зарегистрировать просмотр
export const registerView = async (listingId, userId = null) => {
    try {
        const response = await API.post(`/listings/${listingId}/view`);
        return response.data;
    } catch (error) {
        console.error('Ошибка регистрации просмотра:', error);
    }
};