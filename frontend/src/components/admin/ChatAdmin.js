import React, { useState, useEffect, useCallback, useRef } from "react";
import { chatAPI } from "../../api";
import { useNotification } from "../../contexts/NotificationContext";
import "./ChatAdmin.css";

const ChatAdmin = () => {
  const { error: showError } = useNotification();
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [socket, setSocket] = useState(null);
  
  const messagesEndRef = useRef(null);
  const currentUser = JSON.parse(localStorage.getItem("user") || "{}");

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadConversations = useCallback(async () => {
    try {
      setLoading(true);
      const response = await chatAPI.getConversations();
      const docs = response.data.results || response.data;
      setConversations(docs);
    } catch (err) {
      console.error("Error loading conversations:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadMessages = useCallback(async (convId) => {
    try {
      const resp = await chatAPI.getMessages(convId);
      setMessages(resp.data);
    } catch (err) {
      console.error("Error loading messages:", err);
    }
  }, []);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  useEffect(() => {
    if (activeConversation) {
      loadMessages(activeConversation.id);
      
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = window.location.hostname === "localhost" ? "localhost:8000" : window.location.host;
      const wsUrl = `${protocol}//${host}/ws/chat/${activeConversation.id}/`;
      
      const ws = new WebSocket(wsUrl);
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setMessages(prev => [...prev, data]);
      };
      
      setSocket(ws);
      return () => ws.close();
    }
  }, [activeConversation, loadMessages]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !socket) return;
    
    socket.send(json.stringify({
      type: 'message',
      body: newMessage
    }));
    setNewMessage("");
  };

  const handleCloseChat = async (id) => {
    if (!window.confirm("Suhbatni yopmoqchimisiz?")) return;
    try {
      await chatAPI.closeConversation(id);
      loadConversations();
      setActiveConversation(null);
    } catch (err) {
      showError("Suhbatni yopib bo'lmadi");
    }
  };

  return (
    <div className="chat-admin-container">
      <div className="chat-admin-sidebar">
        <div className="sidebar-header">
          <h3>Suhbatlar boshqaruvi</h3>
          <button onClick={loadConversations} className="btn-refresh">🔄</button>
        </div>
        <div className="admin-conversation-list">
          {conversations.map(conv => (
            <div 
              key={conv.id} 
              className={`admin-conversation-item ${activeConversation?.id === conv.id ? 'active' : ''} ${conv.status}`}
              onClick={() => setActiveConversation(conv)}
            >
              <div className="admin-conv-info">
                <span className="admin-conv-user">{conv.user.username}</span>
                <span className="admin-conv-status">{conv.status === 'open' ? '🟢 Ochiq' : '⚪ Yopiq'}</span>
              </div>
              {conv.unread_count > 0 && <span className="unread-badge">{conv.unread_count}</span>}
            </div>
          ))}
          {conversations.length === 0 && <p className="empty-msg">Suhbatlar yo'q</p>}
        </div>
      </div>
      
      <div className="chat-admin-main">
        {activeConversation ? (
          <>
            <div className="chat-admin-header">
              <div className="header-user-info">
                <h4>{activeConversation.user.username} bilan suhbat</h4>
                {activeConversation.status === 'open' && (
                  <button onClick={() => handleCloseChat(activeConversation.id)} className="btn-close-chat">Suhbatni yopish</button>
                )}
              </div>
            </div>
            
            <div className="admin-messages-display">
              {messages.map((msg, idx) => (
                <div key={idx} className={`admin-message-wrapper ${msg.sender.id === currentUser.id ? 'sent' : 'received'}`}>
                  <div className="admin-message-bubble">
                    <div className="admin-message-sender">{msg.sender.username}</div>
                    <div className="admin-message-text">{msg.body}</div>
                    <div className="admin-message-meta">
                      {new Date(msg.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            
            {activeConversation.status === 'open' ? (
              <form className="admin-message-input-area" onSubmit={handleSendMessage}>
                <input 
                  type="text" 
                  placeholder="Javob yozing..." 
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  className="admin-message-input"
                />
                <button type="submit" className="admin-btn-send" disabled={!newMessage.trim()}>Yuborish</button>
              </form>
            ) : (
              <div className="chat-closed-banner">Bu suhbat yopilgan</div>
            )}
          </>
        ) : (
          <div className="admin-no-chat-selected">
            <div className="admin-placeholder-icon">📨</div>
            <p>Javob berish uchun suhbatni tanlang</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatAdmin;
