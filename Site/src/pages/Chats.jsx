import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import API from '../services/api';
import { useAuth } from '../context/AuthContext';
import './Chats.css';

function Chats() {
    const { user } = useAuth();
    const [searchParams] = useSearchParams();
    const [chats, setChats] = useState([]);
    const [agents, setAgents] = useState([]);
    const [activeChat, setActiveChat] = useState(null);
    const [messages, setMessages] = useState([]);
    const [text, setText] = useState('');
    const [loading, setLoading] = useState(true);
    const [showAgents, setShowAgents] = useState(false);
    const bottomRef = useRef(null);

    useEffect(() => {
        loadChats();
        API.get('/agents/').then(res => setAgents(res.data || [])).catch(() => {});
    }, []);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const loadChats = async () => {
        try {
            const res = await API.get('/chats/');
            const chatList = res.data || [];
            setChats(chatList);
            const openId = searchParams.get('open');
            if (openId) {
                const chat = chatList.find(c => c.chat_id === Number(openId));
                if (chat) openChat(chat);
            }
        } catch {} finally {
            setLoading(false);
        }
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
        const messageText = text;
        setText('');
        try {
            const res = await API.post(`/chats/${activeChat.chat_id}/messages`, { content: messageText });
            setMessages(prev => [...prev, res.data]);
        } catch {
            setText(messageText);
            alert('Ошибка отправки');
        }
    };

    const deleteChat = async (chatId, e) => {
        e.stopPropagation();
        if (!window.confirm('Удалить чат?')) return;
        try {
            await API.delete(`/chats/${chatId}`);
            setChats(prev => prev.filter(c => c.chat_id !== chatId));
            if (activeChat?.chat_id === chatId) {
                setActiveChat(null);
                setMessages([]);
            }
        } catch {
            alert('Ошибка удаления');
        }
    };

    const startChat = async (agentId) => {
        const agent = agents.find(a => a.agent_id === agentId);
        const title = agent?.company_name || 'Риэлтор';
        try {
            const res = await API.post('/chats/', {
                agent_id: Number(agentId),
                title: title
            });
            setChats(prev => [res.data, ...prev]);
            openChat(res.data);
            setShowAgents(false);
        } catch {}
    };

    if (loading) return <div className="loader">Загрузка...</div>;

    return (
        <div className="chats-page">
            <div className="chats-sidebar">
                <h3>Чаты</h3>

                <button className="btn-new-chat" onClick={() => setShowAgents(!showAgents)}>
                    {showAgents ? 'Скрыть риэлторов' : '📝 Написать риэлтору'}
                </button>

                {showAgents && (
                    <div className="agents-list">
                        {agents.map(a => (
                            <div key={a.agent_id} className="agent-item">
                                <Link to={`/user/${a.user_id}`} className="agent-info">
                                    <div className="agent-name">{a.user_name || a.company_name || 'Риэлтор'}</div>
                                    <div className="agent-about">{a.about?.substring(0, 60)}</div>
                                </Link>
                                <button className="agent-start-btn" onClick={(e) => { e.preventDefault(); startChat(a.agent_id); }}>
                                    💬 Написать
                                </button>
                            </div>
                        ))}
                        {agents.length === 0 && <p className="no-data">Нет риэлторов</p>}
                    </div>
                )}

                {chats.map(c => (
                    <div
                        key={c.chat_id}
                        className={`chat-item ${activeChat?.chat_id === c.chat_id ? 'active' : ''}`}
                        onClick={() => openChat(c)}
                    >
                        <span className="chat-item-title">{c.title || 'Чат'}</span>
                        <div className="chat-item-actions">
                            {c.is_active ? (
                                <span className="badge-active">●</span>
                            ) : (
                                <span className="badge-closed">○</span>
                            )}
                            <button className="btn-delete-chat" onClick={(e) => deleteChat(c.chat_id, e)} title="Удалить">🗑</button>
                        </div>
                    </div>
                ))}
                {chats.length === 0 && !showAgents && (
                    <p className="no-data">Нет чатов</p>
                )}
            </div>

            <div className="chats-main">
                {activeChat ? (
                    <>
                        <div className="chat-header">
                            <h3>{activeChat.title || 'Чат'}</h3>
                            <div className="chat-header-actions">
                                <button
                                    onClick={() => deleteChat(activeChat.chat_id, { stopPropagation: () => {} })}
                                    className="btn-header-delete"
                                    title="Удалить чат"
                                >
                                    🗑
                                </button>
                                <button onClick={() => setActiveChat(null)}>✖</button>
                            </div>
                        </div>
                        <div className="messages-list">
                            {messages.map(m => (
                                <div
                                    key={m.message_id}
                                    className={`message ${m.sender_id === user?.user_id ? 'mine' : 'theirs'}`}
                                >
                                    <div className="message-content">{m.content}</div>
                                    <div className="message-time">
                                        {new Date(m.sent_at).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
                                    </div>
                                </div>
                            ))}
                            <div ref={bottomRef} />
                        </div>
                        {activeChat.is_active && (
                            <div className="chat-input">
                                <input
                                    value={text}
                                    onChange={e => setText(e.target.value)}
                                    onKeyDown={e => e.key === 'Enter' && sendMessage()}
                                    placeholder="Сообщение..."
                                />
                                <button onClick={sendMessage}>Отправить</button>
                            </div>
                        )}
                        {!activeChat.is_active && (
                            <div className="chat-closed-notice">Чат закрыт</div>
                        )}
                    </>
                ) : (
                    <div className="no-chat">
                        <div>
                            <p>Выберите чат слева</p>
                            <p>или начните новый с риэлтором</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Chats;