import React, { useState, useEffect, useRef, useCallback } from "react";
import { chatAPI } from "../api";
import { useNotification } from "../contexts/NotificationContext";
import "./ChatPage.css";

const ChatPage = () => {
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
      
      if (docs.length > 0 && !activeConversation) {
        setActiveConversation(docs[0]);
      } else if (docs.length === 0) {
        // Option to start a new conversation
      }
    } catch (err) {
      console.error("Error loading conversations:", err);
    } finally {
      setLoading(false);
    }
  }, [activeConversation]);

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
      
      // Setup WebSocket
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
      <div className="message-content">
        {msg.body && <div className="message-text">{msg.body}</div>}
        {msg.file && (
          <div className="message-attachment">
            {msg.file.match(/\.(jpg|jpeg|png|gif)$/i) ? (
              <a href={msg.file} target="_blank" rel="noopener noreferrer">
                <img src={msg.file} alt="Attachment" className="message-image-preview" />
              </a>
            ) : (
              <a href={msg.file} target="_blank" rel="noopener noreferrer" className="file-link">
                📎 Faylni ko'rish
              </a>
            )}
          </div>
        )}
        {msg.image && !msg.file && (
          <div className="message-attachment">
            <a href={msg.image} target="_blank" rel="noopener noreferrer">
              <img src={msg.image} alt="Attachment" className="message-image-preview" />
            </a>
          </div>
        )}
      </div>
    );
  };

  const startNewConversation = async () => {
    try {
      const resp = await chatAPI.createConversation({});
      const newConv = resp.data;
      setConversations(prev => [newConv, ...prev]);
      setActiveConversation(newConv);
    } catch (err) {
      showError("Suhbat boshlashda xatolik");
    }
  };

  if (loading) {
    return <div className="chat-loading">Yuklanmoqda...</div>;
  }

  return (
    <div className="chat-container">
      <div className="chat-sidebar">
        <div className="chat-sidebar-header">
          <h3>Suhbatlar</h3>
          <button onClick={startNewConversation} className="btn-new-chat">+</button>
        </div>
        <div className="conversation-list">
          {conversations.map(conv => (
            <div 
              key={conv.id} 
              className={`conversation-item ${activeConversation?.id === conv.id ? 'active' : ''}`}
              onClick={() => setActiveConversation(conv)}
            >
              <div className="conv-info">
                <span className="conv-name">Suhbat #{conv.id}</span>
                <span className="conv-status">{conv.status}</span>
              </div>
              <div className="conv-time">
                {new Date(conv.last_message_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
              </div>
            </div>
          ))}
          {conversations.length === 0 && <p className="empty-msg">Suhbatlar yo'q</p>}
        </div>
      </div>
      
      <div className="chat-main">
        {activeConversation ? (
          <>
            <div className="chat-header">
              <h4>Suhbat #{activeConversation.id}</h4>
              <span className={`status-dot ${activeConversation.status}`}></span>
            </div>
            
            <div className="messages-display">
              {messages.map((msg, idx) => (
                <div key={idx} className={`message-wrapper ${msg.sender.id === currentUser.id ? 'sent' : 'received'}`}>
                  <div className="message-bubble">
                    <div className="message-sender">{msg.sender.username}</div>
                    {renderMessageContent(msg)}
                    <div className="message-meta">
                      {new Date(msg.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            
            <form className="message-input-area" onSubmit={handleSendMessage}>
              <div className="input-with-actions">
                <input 
                  type="file"
                  id="chat-file-input"
                  ref={fileInputRef}
                  onChange={(e) => setSelectedFile(e.target.files[0])}
                  style={{ display: 'none' }}
                />
                <button 
                  type="button" 
                  className="btn-attach"
                  onClick={() => fileInputRef.current?.click()}
                  title="Fayl yoki skrinshot biriktirish"
                >
                  <span className="icon">📎</span>
                </button>
                <input 
                  type="text" 
                  placeholder="Xabar yozing..." 
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  className="message-input"
                />
                <button type="submit" className="btn-send" disabled={(!newMessage.trim() && !selectedFile) || (!isSocketReady && !selectedFile)}>
                  {isSocketReady || selectedFile ? 'Yuborish' : 'Bog\'lanmoqda...'}
                </button>
              </div>
              {selectedFile && (
                <div className="selected-file-preview">
                  <span>📎 {selectedFile.name}</span>
                  <button type="button" onClick={() => {
                    setSelectedFile(null);
                    if (fileInputRef.current) fileInputRef.current.value = "";
                  }} className="btn-remove-file">×</button>
                </div>
              )}
            </form>
          </>
        ) : (
          <div className="no-chat-selected">
            <div className="chat-placeholder-icon">💬</div>
            <p>Suhbatni tanlang yoki yangisini boshlang</p>
            <button onClick={startNewConversation} className="btn-primary">Yangi suhbat</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatPage;
