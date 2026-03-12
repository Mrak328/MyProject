import React from 'react';
import { useParams } from 'react-router-dom';

function UserProfile() {
  const { id } = useParams();

  return (
    <div className="user-profile">
      <h1>Профиль пользователя #{id}</h1>
    </div>
  );
}

export default UserProfile;