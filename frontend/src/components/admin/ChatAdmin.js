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
  const [isSocketReady, setIsSocketReady] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
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
      const token = localStorage.getItem("access");
      const wsUrl = `${protocol}//${host}/ws/chat/${activeConversation.id}/${token ? `?token=${token}` : ""}`;
      
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        setIsSocketReady(true);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setMessages(prev => [...prev, data]);
      };
      
      ws.onerror = (err) => {
        console.error("WebSocket Error:", err);
        setIsSocketReady(false);
      };

      ws.onclose = () => {
        setIsSocketReady(false);
      };
      
      setSocket(ws);
      return () => {
        ws.close();
        setIsSocketReady(false);
      };
    }
  }, [activeConversation, loadMessages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if ((!newMessage.trim() && !selectedFile) || !socket) return;
    
    if (selectedFile) {
      // Send via HTTP for file support
      const formData = new FormData();
      formData.append('conversation', activeConversation.id);
      formData.append('body', newMessage || "Fayl biriktirildi");
      formData.append('file', selectedFile);
      
      try {
        await chatAPI.sendMessage(formData);
        setNewMessage("");
        setSelectedFile(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
      } catch (err) {
        showError("Fayl yuborishda xatolik");
      }
    } else {
      // Send via WebSocket for text-only messages
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
          type: 'message',
          body: newMessage
        }));
        setNewMessage("");
      } else {
        showError("Ulanish mavjud emas. Sahifani yangilang.");
      }
    }
  };

  const renderMessageContent = (msg) => {
    return (
      <div className="admin-message-content">
        {msg.body && <div className="admin-message-text">{msg.body}</div>}
        {msg.file && (
          <div className="admin-message-attachment">
            {msg.file.match(/\.(jpg|jpeg|png|gif)$/i) ? (
              <a href={msg.file} target="_blank" rel="noopener noreferrer">
                <img src={msg.file} alt="Attachment" className="admin-message-image-preview" />
              </a>
            ) : (
              <a href={msg.file} target="_blank" rel="noopener noreferrer" className="admin-file-link">
                📎 Faylni ko'rish
              </a>
            )}
          </div>
        )}
        {msg.image && !msg.file && (
          <div className="admin-message-attachment">
            <a href={msg.image} target="_blank" rel="noopener noreferrer">
              <img src={msg.image} alt="Attachment" className="admin-message-image-preview" />
            </a>
          </div>
        )}
      </div>
    );
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

  if (loading) {
    return (
      <div className="chat-admin-loading">
        <div className="spinner"></div>
        <p>Suhbatlar yuklanmoqda...</p>
      </div>
    );
  }

  return (
    <div className="chat-admin-container">
      <div className="chat-admin-sidebar">
        <div className="chat-admin-sidebar-header">
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
                    {renderMessageContent(msg)}
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
                <div className="admin-input-with-actions">
                  <input 
                    type="file"
                    id="admin-chat-file-input"
                    ref={fileInputRef}
                    onChange={(e) => setSelectedFile(e.target.files[0])}
                    style={{ display: 'none' }}
                  />
                  <button 
                    type="button" 
                    className="admin-btn-attach"
                    onClick={() => fileInputRef.current?.click()}
                    title="Fayl yoki skrinshot biriktirish"
                  >
                    <span className="icon">📎</span>
                  </button>
                  <input 
                    type="text" 
                    placeholder="Javob yozing..." 
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    className="admin-message-input"
                  />
                  <button type="submit" className="admin-btn-send" disabled={(!newMessage.trim() && !selectedFile) || (!isSocketReady && !selectedFile)}>
                    {isSocketReady || selectedFile ? 'Yuborish' : 'Bog\'lanmoqda...'}
                  </button>
                </div>
                {selectedFile && (
                  <div className="admin-selected-file-preview">
                    <span>📎 {selectedFile.name}</span>
                    <button type="button" onClick={() => {
                      setSelectedFile(null);
                      if (fileInputRef.current) fileInputRef.current.value = "";
                    }} className="btn-remove-file">×</button>
                  </div>
                )}
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
