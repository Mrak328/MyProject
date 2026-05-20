import React, { useState, useEffect } from 'react';
import API from '../services/api';
import './AdminSearch.css';

function AdminSearch() {
    const [queries, setQueries] = useState([]);
    const [details, setDetails] = useState(null);
    const [loading, setLoading] = useState(true);

    // Состояния для раскрытия блоков
    const [openQueries, setOpenQueries] = useState(true);
    const [openCities, setOpenCities] = useState(false);
    const [openPropertyTypes, setOpenPropertyTypes] = useState(false);
    const [openDealTypes, setOpenDealTypes] = useState(false);
    const [openPrices, setOpenPrices] = useState(false);
    const [openRooms, setOpenRooms] = useState(false);
    const [openAreas, setOpenAreas] = useState(false);
    const [openFloors, setOpenFloors] = useState(false);
    const [openRenovation, setOpenRenovation] = useState(false);

    useEffect(() => {
        loadAll();
    }, []);

    const loadAll = async () => {
        try {
            const [queriesRes, detailsRes] = await Promise.all([
                API.get('/analytics/search/queries?days=30'),
                API.get('/analytics/search/details?days=30')
            ]);
            setQueries(queriesRes.data?.popular_queries || []);
            setDetails(detailsRes.data);
        } catch {} finally {
            setLoading(false);
        }
    };

    const ToggleBlock = ({ title, open, setOpen, children }) => (
        <div className="analytics-card">
            <button className="toggle-block-btn" onClick={() => setOpen(!open)}>
                {title} <span className={`arrow ${open ? 'open' : ''}`}>▼</span>
            </button>
            <div className={`block-wrapper ${open ? 'open' : ''}`}>
                {children}
            </div>
        </div>
    );

    if (loading) return <div className="loader">Загрузка...</div>;

    return (
        <div className="admin-search-page">
            <h1>Поисковые запросы</h1>

            {/* Популярные запросы */}
            <ToggleBlock title="Популярные запросы" open={openQueries} setOpen={setOpenQueries}>
                <div className="queries-list">
                    {queries.length > 0 ? queries.map((item, i) => (
                        <div key={i} className="query-item">
                            <span className="rank">{i + 1}</span>
                            <span className="query">"{item.query}"</span>
                            <span className="count">{item.count} раз</span>
                        </div>
                    )) : <p className="no-data">Нет данных</p>}
                </div>
            </ToggleBlock>

            {details && (
                <>
                    {/* По городам */}
                    {Object.keys(details.cities || {}).length > 0 && (
                        <ToggleBlock title="По городам" open={openCities} setOpen={setOpenCities}>
                            <div className="queries-list">
                                {Object.entries(details.cities).map(([name, count], i) => (
                                    <div key={i} className="query-item">
                                        <span className="rank">{i + 1}</span>
                                        <span className="query">{name}</span>
                                        <span className="count">{count} запросов</span>
                                    </div>
                                ))}
                            </div>
                        </ToggleBlock>
                    )}

                    {/* По типу недвижимости */}
                    {Object.keys(details.property_types || {}).length > 0 && (
                        <ToggleBlock title="По типу недвижимости" open={openPropertyTypes} setOpen={setOpenPropertyTypes}>
                            <div className="queries-list">
                                {Object.entries(details.property_types).map(([name, count], i) => (
                                    <div key={i} className="query-item">
                                        <span className="rank">{i + 1}</span>
                                        <span className="query">{name}</span>
                                        <span className="count">{count} запросов</span>
                                    </div>
                                ))}
                            </div>
                        </ToggleBlock>
                    )}

                    {/* По типу сделки */}
                    {Object.keys(details.deal_types || {}).length > 0 && (
                        <ToggleBlock title="По типу сделки" open={openDealTypes} setOpen={setOpenDealTypes}>
                            <div className="queries-list">
                                {Object.entries(details.deal_types).map(([name, count], i) => (
                                    <div key={i} className="query-item">
                                        <span className="rank">{i + 1}</span>
                                        <span className="query">{name}</span>
                                        <span className="count">{count} запросов</span>
                                    </div>
                                ))}
                            </div>
                        </ToggleBlock>
                    )}

                    {/* По комнатам */}
                    {Object.keys(details.rooms || {}).length > 0 && (
                        <ToggleBlock title="По комнатам" open={openRooms} setOpen={setOpenRooms}>
                            <div className="queries-list">
                                {Object.entries(details.rooms).map(([rooms, count], i) => (
                                    <div key={i} className="query-item">
                                        <span className="rank">{i + 1}</span>
                                        <span className="query">{rooms} комн.</span>
                                        <span className="count">{count} запросов</span>
                                    </div>
                                ))}
                            </div>
                        </ToggleBlock>
                    )}

                    {/* По ценам */}
                    {Object.values(details.price_ranges || {}).some(v => v > 0) && (
                        <ToggleBlock title="По ценам" open={openPrices} setOpen={setOpenPrices}>
                            <div className="queries-list">
                                {Object.entries(details.price_ranges).filter(([, v]) => v > 0).map(([range, count], i) => (
                                    <div key={i} className="query-item">
                                        <span className="rank">{i + 1}</span>
                                        <span className="query">{range}</span>
                                        <span className="count">{count} запросов</span>
                                    </div>
                                ))}
                            </div>
                        </ToggleBlock>
                    )}

                    {/* По площади */}
                    {Object.keys(details.areas || {}).length > 0 && (
                        <ToggleBlock title="По площади" open={openAreas} setOpen={setOpenAreas}>
                            <div className="queries-list">
                                {Object.entries(details.areas).map(([range, count], i) => (
                                    <div key={i} className="query-item">
                                        <span className="rank">{i + 1}</span>
                                        <span className="query">{range}</span>
                                        <span className="count">{count} запросов</span>
                                    </div>
                                ))}
                            </div>
                        </ToggleBlock>
                    )}

                    {/* По этажам */}
                    {Object.keys(details.floors || {}).length > 0 && (
                        <ToggleBlock title="По этажам" open={openFloors} setOpen={setOpenFloors}>
                            <div className="queries-list">
                                {Object.entries(details.floors).map(([floor, count], i) => (
                                    <div key={i} className="query-item">
                                        <span className="rank">{i + 1}</span>
                                        <span className="query">{floor} эт.</span>
                                        <span className="count">{count} запросов</span>
                                    </div>
                                ))}
                            </div>
                        </ToggleBlock>
                    )}

                    {/* По ремонту */}
                    {Object.keys(details.renovation || {}).length > 0 && (
                        <ToggleBlock title="По ремонту" open={openRenovation} setOpen={setOpenRenovation}>
                            <div className="queries-list">
                                {Object.entries(details.renovation).map(([name, count], i) => (
                                    <div key={i} className="query-item">
                                        <span className="rank">{i + 1}</span>
                                        <span className="query">{name}</span>
                                        <span className="count">{count} запросов</span>
                                    </div>
                                ))}
                            </div>
                        </ToggleBlock>
                    )}
                </>
            )}
        </div>
    );
}

export default AdminSearch;