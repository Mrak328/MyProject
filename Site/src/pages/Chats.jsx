import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import API from '../services/api';
import { useAuth } from '../context/AuthContext';
import './Chats.css';

function Chats() {
    const { user } = useAuth();
    const [searchParams] = useSearchParams();
    const [chats, setChats] = useState([]);
    const [activeChat, setActiveChat] = useState(null);
    const [messages, setMessages] = useState([]);
    const [text, setText] = useState('');
    const [loading, setLoading] = useState(true);
    const bottomRef = useRef(null);

    useEffect(() => { loadChats(); }, []);
    useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

    const loadChats = async () => {
        try {
            const res = await API.get('/chats/');
            const chatList = res.data || [];
            setChats(chatList);

            // Открыть чат из URL
            const openId = searchParams.get('open');
            if (openId) {
                const chat = chatList.find(c => c.chat_id === Number(openId));
                if (chat) openChat(chat);
            }
        } catch {} finally { setLoading(false); }
    };

    const openChat = async (chat) => {
        setActiveChat(chat);
        try {
            const res = await API.get(`/chats/${chat.chat_id}/messages`);
            setMessages(res.data || []);
        } catch {}
    };

    const sendMessage = async () => {
        if (!text.trim() || !activeChat) return;
        try {
            const res = await API.post(`/chats/${activeChat.chat_id}/messages`, { content: text });
            setMessages(prev => [...prev, res.data]);
            setText('');
        } catch {}
    };

    const startChat = async (agentId) => {
        try {
            const res = await API.post('/chats/', { agent_id: agentId, title: 'Новый чат' });
            setChats(prev => [res.data, ...prev]);
            openChat(res.data);
        } catch {}
    };

    if (loading) return <div className="loader">Загрузка...</div>;

    return (
        <div className="chats-page">
            <div className="chats-sidebar">
                <h3>Чаты</h3>
                {chats.map(c => (
                    <div key={c.chat_id} className={`chat-item ${activeChat?.chat_id === c.chat_id ? 'active' : ''}`} onClick={() => openChat(c)}>
                        <span>{c.title || 'Чат'}</span>
                        {c.is_active ? <span className="badge-active">активен</span> : <span className="badge-closed">закрыт</span>}
                    </div>
                ))}
                {chats.length === 0 && <p className="no-data">Нет чатов</p>}
            </div>

            <div className="chats-main">
                {activeChat ? (
                    <>
                        <div className="chat-header">
                            <h3>{activeChat.title || 'Чат'}</h3>
                            <button onClick={() => setActiveChat(null)}>✖</button>
                        </div>
                        <div className="messages-list">
                            {messages.map(m => (
                                <div key={m.message_id} className={`message ${m.sender_id === user?.user_id ? 'mine' : 'theirs'}`}>
                                    <div className="message-content">{m.content}</div>
                                    <div className="message-time">{new Date(m.sent_at).toLocaleString('ru-RU')}</div>
                                </div>
                            ))}
                            <div ref={bottomRef} />
                        </div>
                        <div className="chat-input">
                            <input value={text} onChange={e => setText(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendMessage()} placeholder="Сообщение..." />
                            <button onClick={sendMessage}>Отправить</button>
                        </div>
                    </>
                ) : (
                    <div className="no-chat">Выберите чат или начните новый</div>
                )}
            </div>
        </div>
    );
}

export default Chats;