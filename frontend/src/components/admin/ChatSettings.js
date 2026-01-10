import React, { useState, useEffect } from "react";
import { chatAPI } from "../../api";
import { useNotification } from "../../contexts/NotificationContext";
import "./ChatSettings.css";

const ChatSettings = () => {
  const { error: showError, success: showSuccess } = useNotification();
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState({
    id: null,
    welcome_message: "",
    is_chat_enabled: true,
    auto_reply_enabled: false,
    auto_reply_text: ""
  });

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);
        const response = await chatAPI.getSettings();
        setSettings(response.data);
      } catch (err) {
        showError("Sozlamalarni yuklab bo'lmadi");
      } finally {
        setLoading(false);
      }
    };
    fetchSettings();
  }, [showError]);

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      await chatAPI.updateSettings(settings.id, settings);
      showSuccess("Sozlamalar saqlandi");
    } catch (err) {
      showError("Saqlashda xatolik yuz berdi");
    }
  };

  if (loading) return <div className="loading">Yuklanmoqda...</div>;

  return (
    <div className="chat-settings">
      <h2>Chat Sozlamalari</h2>
      <div className="settings-card">
        <form onSubmit={handleSave}>
          <div className="setting-item">
            <div className="setting-info">
              <label>Chatni faollashtirish</label>
              <p className="setting-desc">Mijozlar chatdan foydalana olishi uchun buni yoqing</p>
            </div>
            <div className="setting-control">
              <input 
                type="checkbox" 
                checked={settings.is_chat_enabled}
                onChange={e => setSettings({...settings, is_chat_enabled: e.target.checked})}
              />
            </div>
          </div>

          <div className="setting-item vertical">
            <label>Xush kelibsiz xabari</label>
            <textarea 
              value={settings.welcome_message}
              onChange={e => setSettings({...settings, welcome_message: e.target.value})}
              placeholder="Yangi suhbat boshlanganda ko'rinadigan xabar..."
            />
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <label>Avtomatik javob (Auto-reply)</label>
              <p className="setting-desc">Ish vaqtidan tashqari vaqtda avtomatik xabar yuborish</p>
            </div>
            <div className="setting-control">
              <input 
                type="checkbox" 
                checked={settings.auto_reply_enabled}
                onChange={e => setSettings({...settings, auto_reply_enabled: e.target.checked})}
              />
            </div>
          </div>

          {settings.auto_reply_enabled && (
            <div className="setting-item vertical">
              <label>Auto-reply xabari</label>
              <textarea 
                value={settings.auto_reply_text}
                onChange={e => setSettings({...settings, auto_reply_text: e.target.value})}
                placeholder="Avtomatik yuboriladigan xabar..."
              />
            </div>
          )}

          <div className="form-actions">
            <button type="submit" className="btn-save">Saqlash</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatSettings;
