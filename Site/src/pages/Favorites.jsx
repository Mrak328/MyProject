import React from 'react';
import { useAuth } from '../context/AuthContext';

function Favorites() {
  const { user } = useAuth();

  return (
    <div className="favorites-page">
      <h1>Избранное</h1>
      {!user && <p>Войдите чтобы увидеть избранное</p>}
    </div>
  );
}

export default Favorites;