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
  
  // Model state
  const [models, setModels] = useState([]);
  const [modelsLoading, setModelsLoading] = useState(false);
  const [editingModel, setEditingModel] = useState(null);
  const [showModelForm, setShowModelForm] = useState(false);
  const [modelForm, setModelForm] = useState({ name: "", model_id: "", provider: "google", is_active: true, is_default: false });

  useEffect(() => {
    fetchSettings();
    fetchStats();
    fetchModels();
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

  const fetchModels = async () => {
    try {
      setModelsLoading(true);
      const res = await coreAPI.getAIModels();
      setModels(res.data.results || res.data);
    } catch (err) {
      console.error("Modellarni yuklab bo'lmadi", err);
    } finally {
      setModelsLoading(false);
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

  const handleModelSave = async (e) => {
    e.preventDefault();
    try {
      if (editingModel) {
        await coreAPI.updateAIModel(editingModel.id, modelForm);
        setSuccess("Model muvaffaqiyatli yangilandi");
      } else {
        await coreAPI.createAIModel(modelForm);
        setSuccess("Yangi model qo'shildi");
      }
      setShowModelForm(false);
      setEditingModel(null);
      fetchModels();
    } catch (err) {
      setError("Modelni saqlashda xatolik yuz berdi");
    }
  };

  const handleModelDelete = async (id) => {
    if (!window.confirm("Rostdan ham ushbu modelni o'chirib tashlamoqchimisiz?")) return;
    try {
      await coreAPI.deleteAIModel(id);
      setSuccess("Model o'chirildi");
      fetchModels();
    } catch (err) {
      setError("Modelni o'chirishda xatolik yuz berdi");
    }
  };

  const handleModelToggle = async (model) => {
    try {
      await coreAPI.updateAIModel(model.id, { is_active: !model.is_active });
      fetchModels();
    } catch (err) {
      setError("Model holatini o'zgartirishda xatolik");
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
            className={`tab-btn ${activeTab === "models" ? "active" : ""}`}
            onClick={() => setActiveTab("models")}
          >
            Modellar
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
      ) : activeTab === "models" ? (
        <div className="models-management">
          <div className="section-header">
            <h3>Mavjud AI Modellar</h3>
            <button 
              className="admin-btn primary"
              onClick={() => {
                setEditingModel(null);
                setModelForm({ name: "", model_id: "", provider: "google", is_active: true, is_default: false });
                setShowModelForm(true);
              }}
            >
              Yangi model qo'shish
            </button>
          </div>

          <div className="models-list">
            {models.map(m => (
              <div key={m.id} className="model-item card">
                <div className="model-info">
                  <div className="model-name-wrapper">
                    <span className="model-name">{m.name}</span>
                    {m.is_default && <span className="badge default">Asosiy</span>}
                    {!m.is_active && <span className="badge inactive">O'chirilgan</span>}
                  </div>
                  <div className="model-id">{m.model_id}</div>
                  <div className="model-provider">Provayder: {m.provider}</div>
                </div>
                <div className="model-actions">
                  <button 
                    className={`admin-btn ${m.is_active ? "warning" : "success"}`}
                    onClick={() => handleModelToggle(m)}
                  >
                    {m.is_active ? "O'chirib qo'yish" : "Yoqish"}
                  </button>
                  <button 
                    className="admin-btn"
                    onClick={() => {
                      setEditingModel(m);
                      setModelForm({ ...m });
                      setShowModelForm(true);
                    }}
                  >
                    Tahrirlash
                  </button>
                  <button className="admin-btn danger" onClick={() => handleModelDelete(m.id)}>O'chirish</button>
                </div>
              </div>
            ))}
          </div>

          {showModelForm && (
            <div className="settings-modal-overlay">
              <div className="settings-modal-content card">
                <h3>{editingModel ? "Modelni tahrirlash" : "Yangi model qo'shish"}</h3>
                <form onSubmit={handleModelSave} className="settings-modal-form">
                  <div className="form-group">
                    <label>Nomi</label>
                    <input 
                      className="admin-input" 
                      value={modelForm.name} 
                      onChange={e => setModelForm({...modelForm, name: e.target.value})} 
                      required 
                    />
                  </div>
                  <div className="form-group">
                    <label>Model ID (API uchun)</label>
                    <input 
                      className="admin-input" 
                      value={modelForm.model_id} 
                      onChange={e => setModelForm({...modelForm, model_id: e.target.value})} 
                      required 
                    />
                  </div>
                  <div className="form-group">
                    <label>Provayder</label>
                    <select 
                      className="admin-input" 
                      value={modelForm.provider} 
                      onChange={e => setModelForm({...modelForm, provider: e.target.value})}
                    >
                      <option value="google">Google</option>
                      <option value="openai">OpenAI</option>
                    </select>
                  </div>
                  <div className="form-checkbox">
                    <label>
                      <input 
                        type="checkbox" 
                        checked={modelForm.is_default} 
                        onChange={e => setModelForm({...modelForm, is_default: e.target.checked})} 
                      />
                      Asosiy (Default) qilib belgilash
                    </label>
                  </div>
                  <div className="form-actions">
                    <button type="button" className="admin-btn" onClick={() => setShowModelForm(false)}>Bekor qilish</button>
                    <button type="submit" className="admin-btn primary">Saqlash</button>
                  </div>
                </form>
              </div>
            </div>
          ) }
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
