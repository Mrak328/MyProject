import React, { useState, useEffect } from 'react';
import { getCountries, getRegions, getCities, getDistricts, getStreets, getHouses } from '../services/geo';

function AddressSelect({ onChange }) {
    const [countries, setCountries] = useState([]);
    const [regions, setRegions] = useState([]);
    const [cities, setCities] = useState([]);
    const [districts, setDistricts] = useState([]);
    const [streets, setStreets] = useState([]);
    const [houses, setHouses] = useState([]);

    const [countryId, setCountryId] = useState('1');
    const [regionId, setRegionId] = useState('');
    const [cityId, setCityId] = useState('');
    const [districtId, setDistrictId] = useState('');
    const [streetId, setStreetId] = useState('');
    const [houseId, setHouseId] = useState('');

    useEffect(() => {
        getCountries().then(setCountries);
        getRegions(1).then(data => {
            setRegions(data);
            const kirovRegion = data.find(r => r.name === 'Кировская область');
            if (kirovRegion) setRegionId(String(kirovRegion.id));
        });
    }, []);

    useEffect(() => {
        if (regionId) {
            getCities(regionId).then(data => {
                setCities(data);
                const kirovCity = data.find(c => c.name === 'Киров');
                if (kirovCity) setCityId(String(kirovCity.id));
            });
            setDistricts([]);
            setStreets([]);
            setHouses([]);
            setDistrictId('');
            setStreetId('');
            setHouseId('');
        }
    }, [regionId]);

    useEffect(() => {
        if (cityId) {
            getDistricts(cityId).then(setDistricts);
            getStreets(cityId).then(setStreets);
            setHouses([]);
            setStreetId('');
            setHouseId('');
        }
    }, [cityId]);

    useEffect(() => {
        if (streetId) {
            getHouses(streetId).then(setHouses);
            setHouseId('');
        }
    }, [streetId]);

    useEffect(() => {
        onChange?.({
            country_id: countryId || null,
            region_id: regionId || null,
            city_id: cityId || null,
            district_id: districtId || null,
            street_id: streetId || null,
            house_id: houseId || null
        });
    }, [countryId, regionId, cityId, districtId, streetId, houseId]);

    const handleCountryChange = (e) => {
        setCountryId(e.target.value);
        setRegionId('');
        setCityId('');
    };

    const handleRegionChange = (e) => {
        setRegionId(e.target.value);
        setCityId('');
    };

    const handleCityChange = (e) => {
        setCityId(e.target.value);
        setDistrictId('');
    };

    const handleStreetChange = (e) => {
        setStreetId(e.target.value);
    };

    return (
        <div className="address-select">
            <select value={countryId} onChange={handleCountryChange}>
                <option value="">Страна</option>
                {countries.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>

            <select value={regionId} onChange={handleRegionChange} disabled={!countryId}>
                <option value="">Регион</option>
                {regions.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
            </select>

            <select value={cityId} onChange={handleCityChange} disabled={!regionId}>
                <option value="">Город</option>
                {cities.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>

            <select value={districtId} onChange={(e) => setDistrictId(e.target.value)} disabled={!cityId}>
                <option value="">Район</option>
                {districts.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>

            <select value={streetId} onChange={handleStreetChange} disabled={!cityId}>
                <option value="">Улица</option>
                {streets.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>

            <select value={houseId} onChange={(e) => setHouseId(e.target.value)} disabled={!streetId}>
                <option value="">Дом</option>
                {houses.map(h => <option key={h.id} value={h.id}>{h.number}</option>)}
            </select>
        </div>
    );
}

export default AddressSelect;