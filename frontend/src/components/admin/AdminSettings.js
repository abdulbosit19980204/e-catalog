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
  const [aiStats, setAiStats] = useState(null);
  const [activeTab, setActiveTab] = useState("settings");

  useEffect(() => {
    fetchSettings();
    fetchStats();
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

  const fetchStats = async () => {
    try {
      const res = await coreAPI.getAIUsageStats();
      setAiStats(res.data);
    } catch (err) {
      console.error("AI statistikasini yuklab bo'lmadi", err);
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
        <h1>Tizim Boshqaruvi</h1>
        <div className="admin-tabs">
          <button 
            className={`tab-btn ${activeTab === "settings" ? "active" : ""}`}
            onClick={() => setActiveTab("settings")}
          >
            Sozlamalar
          </button>
          <button 
            className={`tab-btn ${activeTab === "ai-stats" ? "active" : ""}`}
            onClick={() => setActiveTab("ai-stats")}
          >
            AI Statistika
          </button>
        </div>
      </div>

      {error && <div className="admin-error-banner">{error}</div>}
      {success && <div className="admin-success-banner">{success}</div>}

      {activeTab === "settings" ? (
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
                    {s.field_type === 'multiselect' ? (
                      <div className="multiselect-group">
                        {s.options?.map(opt => (
                          <label key={opt} className="checkbox-label">
                            <input 
                              type="checkbox"
                              checked={editValue.split(',').map(v => v.trim()).includes(opt)}
                              onChange={(e) => {
                                const currentVals = editValue.split(',').map(v => v.trim()).filter(v => v);
                                if (e.target.checked) {
                                  setEditValue([...currentVals, opt].join(', '));
                                } else {
                                  setEditValue(currentVals.filter(v => v !== opt).join(', '));
                                }
                              }}
                            />
                            {opt}
                          </label>
                        ))}
                      </div>
                    ) : s.field_type === 'select' ? (
                      <select 
                        className="admin-input"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                      >
                        {s.options?.map(opt => (
                          <option key={opt} value={opt}>{opt}</option>
                        ))}
                      </select>
                    ) : (
                      <input
                        type={s.field_type === 'secret' ? "password" : "text"}
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        placeholder="Yangi qiymat"
                        className="admin-input"
                      />
                    )}
                    <div className="edit-actions">
                      <button onClick={() => handleUpdate(s.key)} className="admin-btn primary">
                        Saqlash
                      </button>
                      <button onClick={() => setEditingKey(null)} className="admin-btn">
                        Bekor qilish
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="setting-value">
                      {s.field_type === 'secret' ? "********" : s.value}
                    </div>
                    <button
                      onClick={() => {
                        setEditingKey(s.key);
                        setEditValue(s.value);
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
        </div>
      ) : (
        <div className="ai-stats-container">
          {aiStats ? (
            <>
              <div className="stats-summary grid-3">
                <div className="stat-card card">
                  <h3>Jami So'rovlar</h3>
                  <div className="stat-value">{aiStats.totals.total_requests || 0}</div>
                </div>
                <div className="stat-card card">
                  <h3>Jami Tokenlar</h3>
                  <div className="stat-value">{(aiStats.totals.total_all || 0).toLocaleString()}</div>
                </div>
                <div className="stat-card card">
                  <h3>Input / Output</h3>
                  <div className="stat-value">
                    {(aiStats.totals.total_input || 0).toLocaleString()} / {(aiStats.totals.total_output || 0).toLocaleString()}
                  </div>
                </div>
              </div>

              <div className="stats-details grid-2">
                <div className="models-usage card">
                  <h3>Modellar bo'yicha</h3>
                  <table className="stats-table">
                    <thead>
                      <tr>
                        <th>Model</th>
                        <th>So'rovlar</th>
                        <th>Tokenlar</th>
                      </tr>
                    </thead>
                    <tbody>
                      {aiStats.models.map(m => (
                        <tr key={m.model_name}>
                          <td>{m.model_name}</td>
                          <td>{m.requests}</td>
                          <td>{m.tokens.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="daily-usage card">
                  <h3>Oxirgi 30 kunlik (Tokenlar)</h3>
                  <div className="mini-chart">
                    {aiStats.daily.map(d => (
                      <div 
                        key={d.day} 
                        className="chart-bar" 
                        style={{ height: `${(d.tokens / (aiStats.totals.total_all || 1)) * 100}%` }}
                        title={`${d.day}: ${d.tokens} tokens`}
                      ></div>
                    ))}
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="no-stats">Statistika ma'lumotlari yuklanmadi.</div>
          )}
        </div>
      )}
    </div>
  );
};

export default AdminSettings;
