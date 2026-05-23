import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import API from '../services/api';
import ListingCard from '../components/ListingCard';
import { useAuth } from '../context/AuthContext';
import './UserProfile.css';

function UserProfile() {
    const { id } = useParams();
    const { user: currentUser } = useAuth();
    const navigate = useNavigate();

    const [profile, setProfile] = useState(null);
    const [listings, setListings] = useState([]);
    const [comments, setComments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [newComment, setNewComment] = useState('');

    const isOwnProfile = currentUser?.user_id === Number(id);

    const loadData = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const [userRes, listingsRes, commentsRes] = await Promise.all([
                API.get(`/users/${id}`),
                API.get('/listings/search', { params: { user_id: id } }),
                API.get(`/comments/profile/${id}`)
            ]);
            setProfile(userRes.data);
            setListings(listingsRes.data?.items || listingsRes.data || []);
            setComments(commentsRes.data || []);
        } catch {
            setError('Не удалось загрузить данные');
        } finally {
            setLoading(false);
        }
    }, [id]);

    useEffect(() => { loadData(); }, [loadData]);

    const handleWrite = async () => {
        if (!currentUser) return navigate('/login');
        try {
            const res = await API.post('/chats/', { user_id: Number(id) });
            navigate(`/chats?open=${res.data.chat_id}`);
        } catch {
            alert('Ошибка при создании чата');
        }
    };

    const submitComment = async () => {
        if (!newComment.trim()) return;
        try {
            await API.post('/comments/', { profile_user_id: Number(id), content: newComment });
            setNewComment('');
            loadData();
        } catch (err) {
            alert(err.response?.data?.detail || 'Ошибка');
        }
    };

    const deleteComment = async (commentId) => {
        if (!window.confirm('Удалить комментарий?')) return;
        try {
            await API.delete(`/comments/${commentId}`);
            loadData();
        } catch {}
    };

    if (loading) return <div className="loader">Загрузка...</div>;
    if (error) return <div className="error">{error}</div>;
    if (!profile) return <div className="error">Пользователь не найден</div>;

    return (
        <div className="user-profile-page">
            <div className="profile-header">
                <div className="profile-avatar">
                    {profile.avatar_url ? (
                        <img src={profile.avatar_url} alt={profile.first_name} />
                    ) : (
                        <div className="avatar-placeholder">{profile.first_name?.charAt(0) || '?'}</div>
                    )}
                </div>
                <div className="profile-info">
                    <h1>{profile.first_name}</h1>
                    <p className="profile-registered">
                        На сайте с {new Date(profile.registration_date).toLocaleDateString('ru-RU')}
                    </p>
                    <div className="profile-stats">
                        <span>🏠 {listings.length} объявлений</span>
                        <span>💬 {comments.length} комментариев</span>
                    </div>
                    {!isOwnProfile && currentUser && (
                        <button className="btn-write" onClick={handleWrite}>💬 Написать</button>
                    )}
                </div>
            </div>

            {/* Объявления */}
            <div className="profile-section">
                <h2>Объявления ({listings.length})</h2>
                {listings.length === 0 ? (
                    <p className="no-data">Нет объявлений</p>
                ) : (
                    <div className="listings-grid">
                        {listings.map(l => <ListingCard key={l.listing_id} listing={l} />)}
                    </div>
                )}
            </div>

            {/* Комментарии */}
            <div className="profile-section">
                <h2>Комментарии ({comments.length})</h2>

                {currentUser && !isOwnProfile && (
                    <div className="comment-form">
                        <input
                            placeholder="Напишите комментарий..."
                            value={newComment}
                            onChange={(e) => setNewComment(e.target.value)}
                            onKeyDown={(e) => { if (e.key === 'Enter') submitComment(); }}
                        />
                        <button onClick={submitComment}>Отправить</button>
                    </div>
                )}

                {comments.length === 0 && !currentUser && (
                    <p className="no-data">Войдите, чтобы оставить комментарий</p>
                )}

                {comments.map(c => (
                    <div key={c.comment_id} className="comment-card">
                        <div className="comment-header">
                            <strong>{c.author_name || 'Пользователь'}</strong>
                            <span className="comment-date">
                                {new Date(c.created_date).toLocaleDateString('ru-RU')}
                            </span>
                        </div>
                        <p>{c.content}</p>
                        {currentUser?.user_id === c.author_id && (
                            <button className="btn-delete-comment" onClick={() => deleteComment(c.comment_id)}>
                                🗑
                            </button>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default UserProfile;