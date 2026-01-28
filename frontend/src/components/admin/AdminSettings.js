import React, { useState, useEffect } from "react";
import { coreAPI } from "../../api";
import "./AdminSettings.css";

const AdminSettings = () => {
  const [settings, setSettings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [editingKey, setEditingKey] = useState(null);
  const [editValue, setEditValue] = useState("");

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const res = await coreAPI.getSettings();
      setSettings(res.data.results || res.data);
    } catch (err) {
      setError("Sozlamalarni yuklab bo'lmadi");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (key) => {
    try {
      setSuccess(null);
      setError(null);
      await coreAPI.updateSetting(key, { value: editValue });
      setSuccess(`${key} muvaffaqiyatli yangilandi`);
      setEditingKey(null);
      fetchSettings();
    } catch (err) {
      setError(`${key} ni yangilashda xatolik yuz berdi`);
    }
  };

  if (loading) return <div className="admin-loading">Yuklanmoqda...</div>;

  return (
    <div className="admin-settings-container">
      <div className="admin-settings-header">
        <h1>Tizim Sozlamalari</h1>
        <p>API kalitlari va boshqa dinamik konfiguratsiyalarni boshqarish</p>
      </div>

      {error && <div className="admin-error-banner">{error}</div>}
      {success && <div className="admin-success-banner">{success}</div>}

      <div className="settings-list">
        {settings.map((s) => (
          <div key={s.id} className="setting-item card">
            <div className="setting-info">
              <div className="setting-key">{s.key}</div>
              <div className="setting-desc">{s.description || "Izoh yo'q"}</div>
              <div className="setting-meta">
                Oxirgi yangilanish: {new Date(s.updated_at).toLocaleString()}
              </div>
            </div>

            <div className="setting-actions">
              {editingKey === s.key ? (
                <div className="edit-group">
                  <input
                    type="text"
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    placeholder="Yangi qiymat"
                    className="admin-input"
                  />
                  <button onClick={() => handleUpdate(s.key)} className="admin-btn primary">
                    Saqlash
                  </button>
                  <button onClick={() => setEditingKey(null)} className="admin-btn">
                    Bekor qilish
                  </button>
                </div>
              ) : (
                <>
                  <div className="setting-value">
                    {s.is_secret ? "********" : s.value}
                  </div>
                  <button
                    onClick={() => {
                      setEditingKey(s.key);
                      setEditValue(s.is_secret ? "" : s.value);
                    }}
                    className="admin-btn"
                  >
                    O'zgartirish
                  </button>
                </>
              )}
            </div>
          </div>
        ))}

        {settings.length === 0 && (
          <div className="no-settings">
            Hozircha hech qanday sozlama topilmadi.
            <br />
            Django Admin orqali yangi sozlamalar qo'shishingiz mumkin.
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminSettings;
