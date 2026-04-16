import React, { useState, useEffect } from 'react';
import { getFavorites } from '../services/favorites';
import ListingCard from '../components/ListingCard';

function Favorites() {
    const [listings, setListings] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadFavorites();
    }, []);

    const loadFavorites = async () => {
        const data = await getFavorites();
        setListings(data);
        setLoading(false);
    };

    if (loading) return <div className="loader">Загрузка...</div>;

    return (
        <div className="favorites-page">
            <h1>Избранное</h1>
            {listings.length === 0 ? (
                <p>У вас пока нет избранных объявлений</p>
            ) : (
                <div className="listings-grid">
                    {listings.map(listing => (
                        <ListingCard key={listing.listing_id} listing={listing} />
                    ))}
                </div>
            )}
        </div>
    );
}

export default Favorites;