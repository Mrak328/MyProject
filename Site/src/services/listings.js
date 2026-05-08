import API from './api';

export const searchListings = (filters = {}, page = 1, pageSize = 20) => {
    const params = { page, page_size: pageSize };

    if (filters.query) params.query = filters.query;
    if (filters.city) params.city = filters.city;
    if (filters.minPrice) params.min_price = filters.minPrice;
    if (filters.maxPrice) params.max_price = filters.maxPrice;
    if (filters.minArea) params.min_area = filters.minArea;
    if (filters.maxArea) params.max_area = filters.maxArea;
    if (filters.rooms) params.rooms = filters.rooms;
    if (filters.floor) params.floor = filters.floor;
    if (filters.propertyTypeId) params.property_type_id = filters.propertyTypeId;
    if (filters.dealTypeId) params.deal_type_id = filters.dealTypeId;
    if (filters.renovationId) params.renovation_condition_id = filters.renovationId;
    if (filters.sortBy) params.sort_by = filters.sortBy;

    return API.get('/listings/search', { params })
        .then(r => r.data)
        .catch(() => ({ items: [], total: 0, page: 1, pages: 0 }));
};

export const getListingDetail = (id) =>
    API.get(`/listings/${id}`).then(r => r.data).catch(() => null);

export const registerView = (listingId) =>
    API.post(`/listings/${listingId}/view`).catch(() => {});