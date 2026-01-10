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
      const wsUrl = `${protocol}//${host}/ws/chat/${activeConversation.id}/`;
      
      const ws = new WebSocket(wsUrl);
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setMessages(prev => [...prev, data]);
      };
      
      ws.onerror = (err) => {
        console.error("WebSocket Error:", err);
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

  return (
    <div className="chat-container">
      <div className="chat-sidebar">
        <div className="sidebar-header">
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
                    <div className="message-text">{msg.body}</div>
                    <div className="message-meta">
                      {new Date(msg.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            
            <form className="message-input-area" onSubmit={handleSendMessage}>
              <input 
                type="text" 
                placeholder="Xabar yozing..." 
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                className="message-input"
              />
              <button type="submit" className="btn-send" disabled={!newMessage.trim()}>Yuborish</button>
            </form>
          </>
        ) : (
          <div className="no-chat-selected">
            <div className="placeholder-icon">💬</div>
            <p>Suhbatni tanlang yoki yangisini boshlang</p>
            <button onClick={startNewConversation} className="btn-primary">Yangi suhbat</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatPage;
