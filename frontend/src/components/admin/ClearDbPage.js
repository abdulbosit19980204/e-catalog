import React, { useState } from 'react';
import api from '../../api';

const ClearDbPage = () => {
  const [selectedModels, setSelectedModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [confirming, setConfirming] = useState(false);

  const AVAILABLE_MODELS = [
    { key: 'client', label: 'Clients' },
    { key: 'client_image', label: 'Client Images' },
    { key: 'nomenklatura', label: 'Nomenklatura' },
    { key: 'nomenklatura_image', label: 'Nomenklatura Images' },
    { key: 'project', label: 'Projects' },
    { key: 'project_image', label: 'Project Images' },
    { key: 'agent_location', label: 'Agent Locations' },
    { key: 'visit', label: 'Visits (Tashriflar)' },
    { key: 'visit_plan', label: 'Visit Plans (Tashrif Rejalari)' },
    { key: 'visit_image', label: 'Visit Images (Tashrif Rasmlari)' },
    { key: 'image_source', label: 'Image Sources' },
    { key: 'image_status', label: 'Image Statuses' },
  ];

  const handleCheckboxChange = (key) => {
    if (selectedModels.includes(key)) {
      setSelectedModels(selectedModels.filter(m => m !== key));
    } else {
      setSelectedModels([...selectedModels, key]);
    }
  };

  const handleSelectAll = () => {
    if (selectedModels.length === AVAILABLE_MODELS.length) {
      setSelectedModels([]);
    } else {
      setSelectedModels(AVAILABLE_MODELS.map(m => m.key));
    }
  };

  const handleClear = async () => {
    if (!selectedModels.length) return;
    
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await api.post('/admin/clear-db/', { models: selectedModels });
      setResult(response.data);
      setSelectedModels([]);
      setConfirming(false);
    } catch (err) {
      console.error("Clear DB error:", err);
      setError(err.response?.data?.error || "Xatolik yuz berdi");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-page">
      <div className="admin-header-actions">
        <h2>Ma'lumotlar bazasini tozalash</h2>
        <p className="warning-text">
          ⚠️ DIQQAT: Bu amal qaytarib bo'lmaydi! Tanlangan jadvallardagi barcha ma'lumotlar o'chiriladi.
        </p>
      </div>

      <div className="clear-db-container">
        <div className="selection-controls">
          <button 
            type="button" 
            className="btn btn-secondary"
            onClick={handleSelectAll}
          >
            {selectedModels.length === AVAILABLE_MODELS.length ? "Barchasini bekor qilish" : "Barchasini tanlash"}
          </button>
        </div>

        <div className="models-grid">
          {AVAILABLE_MODELS.map(model => (
            <div key={model.key} className="model-checkbox-item">
              <label>
                <input
                  type="checkbox"
                  checked={selectedModels.includes(model.key)}
                  onChange={() => handleCheckboxChange(model.key)}
                />
                <span className="model-label">{model.label}</span>
              </label>
            </div>
          ))}
        </div>

        <div className="action-area">
          {!confirming ? (
            <button
              className="btn btn-danger btn-lg"
              disabled={!selectedModels.length || loading}
              onClick={() => setConfirming(true)}
            >
              Tozalashni boshlash
            </button>
          ) : (
            <div className="confirmation-box">
              <p>Haqiqatan ham {selectedModels.length} ta jadvalni tozalamoqchimisiz?</p>
              <div className="confirm-actions">
                <button 
                  className="btn btn-secondary"
                  onClick={() => setConfirming(false)}
                  disabled={loading}
                >
                  Bekor qilish
                </button>
                <button 
                  className="btn btn-danger"
                  onClick={handleClear}
                  disabled={loading}
                >
                  {loading ? "O'chirilmoqda..." : "HA, O'CHIRILSIN"}
                </button>
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        {result && (
          <div className="results-box">
            <h3>Natijalar:</h3>
            <div className="stats-grid">
              {Object.entries(result.stats).map(([key, count]) => (
                <div key={key} className="stat-item">
                  <span className="stat-key">{key}:</span>
                  <span className="stat-value">{count} ta o'chirildi</span>
                </div>
              ))}
            </div>
            {result.errors && result.errors.length > 0 && (
              <div className="errors-list">
                <h4>Xatoliklar:</h4>
                <ul>
                  {result.errors.map((err, i) => <li key={i}>{err}</li>)}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      <style jsx>{`
        .warning-text {
          color: #dc3545;
          font-weight: bold;
          background: #ffe6e6;
          padding: 1rem;
          border-radius: 4px;
          margin-bottom: 2rem;
        }
        .models-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 1rem;
          margin: 2rem 0;
          padding: 1rem;
          background: #f8f9fa;
          border-radius: 8px;
        }
        .model-checkbox-item label {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          cursor: pointer;
          font-size: 1.1rem;
        }
        .action-area {
          margin-top: 2rem;
          display: flex;
          justify-content: center;
        }
        .confirmation-box {
          background: #fff3cd;
          border: 1px solid #ffeeba;
          padding: 2rem;
          border-radius: 8px;
          text-align: center;
        }
        .confirm-actions {
          display: flex;
          gap: 1rem;
          justify-content: center;
          margin-top: 1rem;
        }
        .results-box {
          margin-top: 2rem;
          padding: 1rem;
          border: 1px solid #dee2e6;
          border-radius: 8px;
        }
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1rem;
          margin-top: 1rem;
        }
        .stat-item {
          display: flex;
          justify-content: space-between;
          padding: 0.5rem;
          background: #e9ecef;
          border-radius: 4px;
        }
        .alert-error {
          color: #721c24;
          background-color: #f8d7da;
          border-color: #f5c6cb;
          padding: 1rem;
          margin-top: 1rem;
          border-radius: 4px;
        }
      `}</style>
    </div>
  );
};

export default ClearDbPage;
