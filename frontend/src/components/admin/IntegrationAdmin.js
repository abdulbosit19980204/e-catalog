import React, { useEffect, useState } from "react";
import { integrationAPI } from "../../api";
import { useNotification } from "../../contexts/NotificationContext";
import "./AdminCRUD.css";

const IntegrationAdmin = () => {
  const { success, error: showError } = useNotification();
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [syncStatus, setSyncStatus] = useState({});
  const [syncing, setSyncing] = useState({});

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await integrationAPI.getIntegrations();
      setIntegrations(response.data);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Integration'lar yuklashda xatolik";
      setError(errorMsg);
      showError(errorMsg);
      console.error("Error loading integrations:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSyncNomenklatura = async (integrationId) => {
    try {
      setError(null);
      setSyncing({ ...syncing, [`nomenklatura_${integrationId}`]: true });
      
      const response = await integrationAPI.syncNomenklatura(integrationId);
      const { task_id } = response.data;
      
      success(`Nomenklatura sync boshlandi: ${response.data.integration?.name || 'Integration'}`);
      
      // Progress'ni kuzatish
      const checkProgress = async () => {
        try {
          const statusResponse = await integrationAPI.getSyncStatus(task_id);
          const status = statusResponse.data;
          setSyncStatus((prev) => ({ ...prev, [task_id]: status }));
          
          if (status.status === 'processing' || status.status === 'fetching') {
            setTimeout(checkProgress, 2000);
          } else {
            setSyncing((prev) => {
              const newState = { ...prev };
              delete newState[`nomenklatura_${integrationId}`];
              return newState;
            });
            
            if (status.status === 'completed') {
              success(`Nomenklatura sync yakunlandi: ${status.created || 0} yaratildi, ${status.updated || 0} yangilandi`);
            } else if (status.status === 'error') {
              showError(`Nomenklatura sync xatosi: ${status.error_message || "Noma'lum xatolik"}`);
            }
          }
        } catch (err) {
          console.error("Error checking status:", err);
          setSyncing((prev) => {
            const newState = { ...prev };
            delete newState[`nomenklatura_${integrationId}`];
            return newState;
          });
        }
      };
      
      checkProgress();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Nomenklatura sync xatolik";
      setError(errorMsg);
      showError(errorMsg);
      setSyncing((prev) => {
        const newState = { ...prev };
        delete newState[`nomenklatura_${integrationId}`];
        return newState;
      });
      console.error("Error syncing nomenklatura:", err);
    }
  };

  const handleSyncClients = async (integrationId) => {
    try {
      setError(null);
      setSyncing({ ...syncing, [`clients_${integrationId}`]: true });
      
      const response = await integrationAPI.syncClients(integrationId);
      const { task_id } = response.data;
      
      success(`Clients sync boshlandi: ${response.data.integration?.name || 'Integration'}`);
      
      // Progress'ni kuzatish
      const checkProgress = async () => {
        try {
          const statusResponse = await integrationAPI.getSyncStatus(task_id);
          const status = statusResponse.data;
          setSyncStatus((prev) => ({ ...prev, [task_id]: status }));
          
          if (status.status === 'processing' || status.status === 'fetching') {
            setTimeout(checkProgress, 2000);
          } else {
            setSyncing((prev) => {
              const newState = { ...prev };
              delete newState[`clients_${integrationId}`];
              return newState;
            });
            
            if (status.status === 'completed') {
              success(`Clients sync yakunlandi: ${status.created || 0} yaratildi, ${status.updated || 0} yangilandi`);
            } else if (status.status === 'error') {
              showError(`Clients sync xatosi: ${status.error_message || "Noma'lum xatolik"}`);
            }
          }
        } catch (err) {
          console.error("Error checking status:", err);
          setSyncing((prev) => {
            const newState = { ...prev };
            delete newState[`clients_${integrationId}`];
            return newState;
          });
        }
      };
      
      checkProgress();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Clients sync xatolik";
      setError(errorMsg);
      showError(errorMsg);
      setSyncing((prev) => {
        const newState = { ...prev };
        delete newState[`clients_${integrationId}`];
        return newState;
      });
      console.error("Error syncing clients:", err);
    }
  };

  return (
    <div className="admin-crud">
      <div className="crud-header">
        <h2>Integration Boshqaruvi</h2>
        <button onClick={loadIntegrations} className="btn-secondary">
          🔄 Yangilash
        </button>
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      {loading ? (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Yuklanmoqda...</p>
        </div>
      ) : integrations.length === 0 ? (
        <div className="integration-info">
          <p>
            Integration'lar topilmadi. Iltimos, Django Admin orqali Integration yarating.
          </p>
        </div>
      ) : (
        <>
          <div className="integration-info">
            <p>
              Integration'lar Django Admin orqali sozlanadi. 
              Bu yerda sync operatsiyalarini boshqarish mumkin.
            </p>
          </div>

          <div className="integrations-list">
            {integrations.map((integration) => (
              <div key={integration.id} className="integration-card">
                <div className="integration-card-header">
                  <div>
                    <h3>{integration.name}</h3>
                    <p className="integration-project">
                      <strong>Project:</strong> {integration.project_name} ({integration.project_code_1c})
                    </p>
                  </div>
                  <div className="integration-status">
                    {integration.is_active ? (
                      <span className="status-badge status-active">Active</span>
                    ) : (
                      <span className="status-badge status-inactive">Inactive</span>
                    )}
                  </div>
                </div>
                
                <div className="integration-details">
                  <p><strong>WSDL URL:</strong> {integration.wsdl_url}</p>
                  <p><strong>Chunk Size:</strong> {integration.chunk_size}</p>
                  <p><strong>Method Nomenklatura:</strong> {integration.method_nomenklatura}</p>
                  <p><strong>Method Clients:</strong> {integration.method_clients}</p>
                </div>
                
                <div className="sync-buttons">
                  <button
                    onClick={() => handleSyncNomenklatura(integration.id)}
                    className="btn-primary"
                    disabled={syncing[`nomenklatura_${integration.id}`]}
                  >
                    {syncing[`nomenklatura_${integration.id}`] ? (
                      <>
                        <span className="spinner-small"></span>
                        <span>Sync...</span>
                      </>
                    ) : (
                      "🔄 Nomenklatura Sync"
                    )}
                  </button>
                  <button
                    onClick={() => handleSyncClients(integration.id)}
                    className="btn-primary"
                    disabled={syncing[`clients_${integration.id}`]}
                  >
                    {syncing[`clients_${integration.id}`] ? (
                      <>
                        <span className="spinner-small"></span>
                        <span>Sync...</span>
                      </>
                    ) : (
                      "🔄 Clients Sync"
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {Object.keys(syncStatus).length > 0 && (
        <div className="sync-status-list">
          <h3>Sync Status</h3>
          {Object.entries(syncStatus).map(([taskId, status]) => (
            <div key={taskId} className="status-card">
              <div className="status-header">
                <span className="status-badge">{status.status}</span>
                <span>Task ID: {taskId}</span>
              </div>
              {status.total > 0 && (
                <div className="progress-container">
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${status.progress_percent}%`,
                        backgroundColor: status.status === 'completed' ? '#28a745' : '#007bff'
                      }}
                    >
                      {status.progress_percent}%
                    </div>
                  </div>
                  <div className="progress-info">
                    <span>Processed: {status.processed} / {status.total}</span>
                    <span>Created: {status.created}</span>
                    <span>Updated: {status.updated}</span>
                    <span>Errors: {status.errors}</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default IntegrationAdmin;

