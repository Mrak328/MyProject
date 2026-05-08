import API from './api';

export const getCountries = () => API.get('/geo/countries').then(r => r.data);
export const getRegions = (countryId) => API.get('/geo/regions', { params: { country_id: countryId } }).then(r => r.data);
export const getCities = (regionId) => API.get('/geo/cities', { params: { region_id: regionId } }).then(r => r.data);
export const getDistricts = (cityId) => API.get('/geo/districts', { params: { city_id: cityId } }).then(r => r.data);
export const getStreets = (cityId) => API.get('/geo/streets', { params: { city_id: cityId } }).then(r => r.data);
export const getHouses = (streetId) => API.get('/geo/houses', { params: { street_id: streetId } }).then(r => r.data);