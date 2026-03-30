import API from './api';

// Получить все активные объявления
export const getAllListings = async () => {
  try {
    const response = await API.get('/listings/?limit=50');
    return response.data;
  } catch (error) {
    console.error('Ошибка загрузки:', error);
    return [];
  }
};

// Поиск с фильтрами
export const searchListings = async (filters) => {
  try {
    const params = new URLSearchParams();
    if (filters.city) params.append('city', filters.city);
    if (filters.dealType) params.append('deal_type', filters.dealType);
    if (filters.rooms) params.append('rooms', filters.rooms);
    if (filters.minPrice) params.append('min_price', filters.minPrice);
    if (filters.maxPrice) params.append('max_price', filters.maxPrice);

    const response = await API.get(`/listings/search?${params}`);
    return response.data;
  } catch (error) {
    console.error('Ошибка поиска:', error);
    return [];
  }
};

// Получить детальную информацию об объявлении с фото
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

// Получить все фото объявления
export const getListingPhotos = async (id) => {
  try {
    const response = await API.get(`/listings/${id}/photos`);
    return response.data;
  } catch (error) {
    console.error('Ошибка загрузки фото:', error);
    return [];
  }
};

export const registerView = async (listingId, userId = null) => {
    try {
        const response = await API.post(`/listings/${listingId}/view`, { user_id: userId });
        return response.data;
    } catch (error) {
        console.error('Ошибка регистрации просмотра:', error);
    }
};