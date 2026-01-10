import React, { useEffect, useState, useCallback } from "react";
import { integrationAPI } from "../../api";
import { useNotification } from "../../contexts/NotificationContext";
import "./IntegrationAdmin.css";

const IntegrationAdmin = () => {
  const { success, error: showError } = useNotification();
  const [integrations, setIntegrations] = useState([]);
  const [histories, setHistories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncStatus, setSyncStatus] = useState({});
  const [syncing, setSyncing] = useState({});
  const [showHistory, setShowHistory] = useState(false);
  const [expandedErrors, setExpandedErrors] = useState({});

  
  // Filters for history
  const [statusFilter, setStatusFilter] = useState("");
  const [integrationFilter, setIntegrationFilter] = useState("");

  const loadIntegrations = useCallback(async () => {
    try {
      setLoading(true);
      const response = await integrationAPI.getIntegrations();
      setIntegrations(response.data);
    } catch (err) {
      showError(err.response?.data?.detail || "Integration'lar yuklashda xatolik");
    } finally {
      setLoading(false);
    }
  }, [showError]);

  const loadHistory = useCallback(async () => {
    try {
      const params = {
        status: statusFilter || undefined,
        integration_id: integrationFilter || undefined,
        page_size: 50
      };
      const response = await integrationAPI.getHistory(params);
      setHistories(response.data.results || response.data);
    } catch (err) {
      console.error("Error loading history:", err);
    }
  }, [statusFilter, integrationFilter]);

  useEffect(() => {
    loadIntegrations();
  }, [loadIntegrations]);

  useEffect(() => {
    if (showHistory) {
      loadHistory();
    }
  }, [showHistory, loadHistory, statusFilter, integrationFilter]);

  const handleSyncNomenklatura = async (integrationId, integrationName) => {
    const key = `nomenklatura_${integrationId}`;
    try {
      setSyncing({ ...syncing, [key]: true });
      
      const response = await integrationAPI.syncNomenklatura(integrationId);
      const { task_id } = response.data;
      
      success(`Nomenklatura sync boshlandi: ${integrationName}`);
      
      const checkProgress = async () => {
        try {
          const statusResponse = await integrationAPI.getSyncStatus(task_id);
          const status = statusResponse.data;
          setSyncStatus((prev) => ({ ...prev, [`${integrationId}_nomen`]: status }));
          
          if (status.status === 'processing' || status.status === 'fetching') {
            setTimeout(checkProgress, 1000);
          } else {
            setSyncing((prev) => {
              const newState = { ...prev };
              delete newState[key];
              return newState;
            });
            
            if (status.status === 'completed') {
              success(`✅ Nomenklatura sync yakunlandi: ${status.created_items || 0} yaratildi, ${status.updated_items || 0} yangilandi`);
              loadHistory();
            } else if (status.status === 'error') {
              showError(`❌ Nomenklatura sync xatosi: ${status.error_details || "Noma'lum xatolik"}`);
            }
          }
        } catch (err) {
          console.error("Error checking status:", err);
          setSyncing((prev) => {
            const newState = { ...prev };
            delete newState[key];
            return newState;
          });
        }
      };
      
      checkProgress();
    } catch (err) {
      showError(err.response?.data?.detail || "Nomenklatura sync xatolik");
      setSyncing((prev) => {
        const newState = { ...prev };
        delete newState[key];
        return newState;
      });
    }
  };

  const handleSyncClients = async (integrationId, integrationName) => {
    const key = `clients_${integrationId}`;
    try {
      setSyncing({ ...syncing, [key]: true });
      
      const response = await integrationAPI.syncClients(integrationId);
      const { task_id } = response.data;
      
      success(`Clients sync boshlandi: ${integrationName}`);
      
      const checkProgress = async () => {
        try {
          const statusResponse = await integrationAPI.getSyncStatus(task_id);
          const status = statusResponse.data;
          setSyncStatus((prev) => ({ ...prev, [`${integrationId}_client`]: status }));
          
          if (status.status === 'processing' || status.status === 'fetching') {
            setTimeout(checkProgress, 1000);
          } else {
            setSyncing((prev) => {
              const newState = { ...prev };
              delete newState[key];
              return newState;
            });
            
            if (status.status === 'completed') {
              success(`✅ Clients sync yakunlandi: ${status.created_items || 0} yaratildi, ${status.updated_items || 0} yangilandi`);
              loadHistory();
            } else if (status.status === 'error') {
              showError(`❌ Clients sync xatosi: ${status.error_details || "Noma'lum xatolik"}`);
            }
          }
        } catch (err) {
          console.error("Error checking status:", err);
          setSyncing((prev) => {
            const newState = { ...prev };
            delete newState[key];
            return newState;
          });
        }
      };
      
      checkProgress();
    } catch (err) {
      showError(err.response?.data?.detail || "Clients sync xatolik");
      setSyncing((prev) => {
        const newState = { ...prev };
        delete newState[key];
        return newState;
      });
    }
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'completed': return '✅';
      case 'error': return '❌';
      case 'processing': return '🔄';
      case 'fetching': return '📥';
      default: return '⏳';
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'completed': return '#10b981';
      case 'error': return '#ef4444';
      case 'processing': return '#3b82f6';
      case 'fetching': return '#8b5cf6';
      default: return '#6b7280';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '—';
    const date = new Date(dateString);
    return date.toLocaleString('uz-UZ', { 
      year: 'numeric', 
      month: '2-digit', 
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleTimeString('uz-UZ', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    });
  };


  const renderProgressBar = (integration) => {
    const nomenStatus = syncStatus[`${integration.id}_nomen`];
    const clientStatus = syncStatus[`${integration.id}_client`];
    
    if (!nomenStatus && !clientStatus) return null;

    return (
      <div className="integration-progress">
        {nomenStatus && (
          <div className="progress-section">
            <div className="progress-header">
              <span>📦 Nomenklatura</span>
              <span className="progress-percentage">
                {nomenStatus.status === 'fetching' ? 'Bog\'lanmoqda...' : `${nomenStatus.processed_items || 0} / ${nomenStatus.total_items || 0}`}
              </span>
            </div>
            <div className={`progress-bar-container ${nomenStatus.status === 'fetching' ? 'fetching' : ''}`}>
              <div 
                className={`progress-bar-fill ${nomenStatus.status === 'fetching' ? 'indeterminate' : ''}`}
                style={nomenStatus.status === 'fetching' ? {} : { 
                  width: `${((nomenStatus.processed_items || 0) / (nomenStatus.total_items || 1)) * 100}%`,
                  backgroundColor: getStatusColor(nomenStatus.status)
                }}
              />
            </div>
            <div className="progress-stats">
              {nomenStatus.status === 'fetching' ? (
                <span>1C dan ma'lumotlar olinmoqda...</span>
              ) : (
                <>
                  <div className="stat-main">
                    <span>✅ {nomenStatus.created_items || 0}</span>
                    <span>🔄 {nomenStatus.updated_items || 0}</span>
                    {nomenStatus.error_items > 0 && <span className="error-count">❌ {nomenStatus.error_items}</span>}
                  </div>
                  
                  {nomenStatus.status === 'completed' && (
                    <span className="status-finished">✅ Bajarildi {formatTime(nomenStatus.completed_at)}</span>
                  )}
                  {nomenStatus.status === 'error' && (
                    <span className="status-err-label">❌ To'xtadi {formatTime(nomenStatus.completed_at)}</span>
                  )}
                </>
              )}
            </div>


          </div>
        )}
        
        {clientStatus && (
          <div className="progress-section">
            <div className="progress-header">
              <span>👥 Clients</span>
              <span className="progress-percentage">
                {clientStatus.status === 'fetching' ? 'Bog\'lanmoqda...' : `${clientStatus.processed_items || 0} / ${clientStatus.total_items || 0}`}
              </span>
            </div>
            <div className={`progress-bar-container ${clientStatus.status === 'fetching' ? 'fetching' : ''}`}>
              <div 
                className={`progress-bar-fill ${clientStatus.status === 'fetching' ? 'indeterminate' : ''}`}
                style={clientStatus.status === 'fetching' ? {} : { 
                  width: `${((clientStatus.processed_items || 0) / (clientStatus.total_items || 1)) * 100}%`,
                  backgroundColor: getStatusColor(clientStatus.status)
                }}
              />
            </div>
            <div className="progress-stats">
              {clientStatus.status === 'fetching' ? (
                <span>1C dan ma'lumotlar olinmoqda...</span>
              ) : (
                <>
                  <div className="stat-main">
                    <span>✅ {clientStatus.created_items || 0}</span>
                    <span>🔄 {clientStatus.updated_items || 0}</span>
                    {clientStatus.error_items > 0 && <span className="error-count">❌ {clientStatus.error_items}</span>}
                  </div>
                  
                  {clientStatus.status === 'completed' && (
                    <span className="status-finished">✅ Bajarildi {formatTime(clientStatus.completed_at)}</span>
                  )}
                  {clientStatus.status === 'error' && (
                    <span className="status-err-label">❌ To'xtadi {formatTime(clientStatus.completed_at)}</span>
                  )}
                </>
              )}
            </div>

          </div>
        )}

      </div>
    );
  };


  if (loading) {
    return (
      <div className="integration-admin">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Yuklanmoqda...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="integration-admin">
      <div className="integration-header">
        <h2>🔗 Integration Boshqaruvi</h2>
        <div className="header-actions">
          <button onClick={() => setShowHistory(!showHistory)} className={`btn-toggle ${showHistory ? 'active' : ''}`}>
            {showHistory ? '📋 Integration' : '📜 Tarix'}
          </button>
          <button onClick={loadIntegrations} className="btn-refresh">
            🔄 Yangilash
          </button>
        </div>
      </div>

      {!showHistory ? (
        // INTEGRATION CARDS
        integrations.length === 0 ? (
          <div className="empty-state">
            <p>Integration'lar topilmadi. Django Admin orqali Integration yarating.</p>
          </div>
        ) : (
          <div className="integration-grid">
            {integrations.map((integration) => (
              <div key={integration.id} className="integration-card-new">
                <div className="card-header">
                  <div className="card-title">
                    <h3>{integration.name}</h3>
                    <span className={`status-badge ${integration.is_active ? 'active' : 'inactive'}`}>
                      {integration.is_active ? '● Faol' : '○ Faol emas'}
                    </span>
                  </div>
                  <div className="card-project">
                    <span className="project-badge">{integration.project_name}</span>
                    <span className="project-code">{integration.project_code_1c}</span>
                  </div>
                </div>

                <div className="card-details">
                  <div className="detail-row">
                    <span className="detail-label">🌐 WSDL:</span>
                    <span className="detail-value" title={integration.wsdl_url}>{integration.wsdl_url.slice(0, 40)}...</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">📦 Method:</span>
                    <span className="detail-value">{integration.method_nomenklatura}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">👥 Method:</span>
                    <span className="detail-value">{integration.method_clients}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">⚙️ Chunk:</span>
                    <span className="detail-value">{integration.chunk_size}</span>
                  </div>
                </div>

                {renderProgressBar(integration)}

                <div className="card-actions">
                  <button
                    onClick={() => handleSyncNomenklatura(integration.id, integration.name)}
                    className="btn-sync"
                    disabled={syncing[`nomenklatura_${integration.id}`]}
                  >
                    {syncing[`nomenklatura_${integration.id}`] ? (
                      <>
                        <span className="spinner-mini"></span>
                        <span>Sync...</span>
                      </>
                    ) : (
                      <>📦 Nomenklatura Sync</>
                    )}
                  </button>
                  <button
                    onClick={() => handleSyncClients(integration.id, integration.name)}
                    className="btn-sync"
                    disabled={syncing[`clients_${integration.id}`]}
                  >
                    {syncing[`clients_${integration.id}`] ? (
                      <>
                        <span className="spinner-mini"></span>
                        <span>Sync...</span>
                      </>
                    ) : (
                      <>👥 Clients Sync</>
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )
      ) : (
        // HISTORY VIEW
        <div className="history-view">
          <div className="history-filters">
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="filter-select">
              <option value="">Barcha statuslar</option>
              <option value="completed">✅ Completed</option>
              <option value="error">❌ Error</option>
              <option value="processing">🔄 Processing</option>
            </select>
            <select value={integrationFilter} onChange={(e) => setIntegrationFilter(e.target.value)} className="filter-select">
              <option value="">Barcha integration'lar</option>
              {integrations.map(int => (
                <option key={int.id} value={int.id}>{int.name}</option>
              ))}
            </select>
            <button onClick={loadHistory} className="btn-filter">Qidirish</button>
          </div>

          <div className="history-list">
            {histories.length === 0 ? (
              <p className="empty-message">Tarix topilmadi</p>
            ) : (
              histories.map((log) => (
                <div key={log.id} className="history-card">
                  <div className="history-header">
                    <div className="history-title">
                      <span className="status-icon">{getStatusIcon(log.status)}</span>
                      <span className="history-type">{log.sync_type === 'nomenklatura' ? '📦 Nomenklatura' : '👥 Clients'}</span>
                      <span className="history-integration">{log.integration_name || 'Unknown'}</span>
                    </div>
                    <span className="history-date">{formatDate(log.created_at)}</span>
                  </div>
                  <div className="history-stats">
                    <span className="stat">📊 Jami: {log.total_items || 0}</span>
                    <span className="stat">✅ Yaratildi: {log.created_items || 0}</span>
                    <span className="stat">🔄 Yangilandi: {log.updated_items || 0}</span>
                    {log.error_items > 0 && <span className="stat error">❌ Xatolar: {log.error_items}</span>}
                  </div>
                  {log.error_details && (
                    <div className="history-error">
                      <strong>Umumiy xato:</strong> {log.error_details}
                    </div>
                  )}
                  
                  {log.error_items > 0 && log.item_errors && log.item_errors.length > 0 && (
                    <div className="history-item-errors">
                      <button 
                        className="btn-text" 
                        onClick={() => setExpandedErrors(prev => ({...prev, [log.id]: !prev[log.id]}))}
                      >
                        {expandedErrors[log.id] ? '🔼 Xatolarni yashirish' : `🔽 Barcha xatolarni ko'rish (${log.item_errors.length})`}
                      </button>
                      
                      {expandedErrors[log.id] && (
                        <div className="errors-list">
                          {log.item_errors.map((err, idx) => (
                            <div key={idx} className="error-item">
                              <span className="err-code">{err.code}</span>: <span className="err-msg">{err.error}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default IntegrationAdmin;
