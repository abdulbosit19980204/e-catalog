import React, { useState, useEffect, useCallback } from 'react';
import { visitAPI } from '../../api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import './VisitManagement.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
);

const VisitManagement = () => {
  const [visits, setVisits] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [filters, setFilters] = useState({
    agent_code: '',
    client_code: '',
    visit_status: '',
    date_from: '',
    date_to: ''
  });
  const [loading, setLoading] = useState(false);
  const [selectedVisit, setSelectedVisit] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const loadVisits = useCallback(async () => {
    setLoading(true);
    try {
      const response = await visitAPI.getVisits(filters);
      setVisits(response.data.results || response.data);
    } catch (error) {
      console.error('Error loading visits:', error);
    }
    setLoading(false);
  }, [filters]);

  const loadStatistics = useCallback(async () => {
    try {
      const response = await visitAPI.getStatistics(filters);
      setStatistics(response.data);
    } catch (error) {
      console.error('Error loading statistics:', error);
    }
  }, [filters]);

  useEffect(() => {
    loadVisits();
    loadStatistics();
  }, [loadVisits, loadStatistics]);

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    });
  };

  const handleViewDetails = async (visitId) => {
    try {
      const response = await visitAPI.getVisit(visitId);
      setSelectedVisit(response.data);
      setShowModal(true);
    } catch (error) {
      console.error('Error loading visit details:', error);
    }
  };

  const handleCheckIn = async (visitId) => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(async (position) => {
        try {
          await visitAPI.checkIn(visitId, {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          });
          loadVisits();
          alert('Check-in muvaffaqiyatli!');
        } catch (error) {
          console.error('Check-in error:', error);
          alert('Check-in xato: ' + error.message);
        }
      });
    } else {
      alert('GPS mavjud emas');
    }
  };

  const handleCheckOut = async (visitId) => {
    const outcome = prompt('Tashrif natijasi:');
    const notes = prompt('Izohlar:');
    
    if (outcome) {
      try {
        await visitAPI.checkOut(visitId, { outcome, notes });
        loadVisits();
        alert('Check-out muvaffaqiyatli!');
      } catch (error) {
        console.error('Check-out error:', error);
        alert('Check-out xato: ' + error.message);
      }
    }
  };

  const handleCancelVisit = async (visitId) => {
    const reason = prompt('Bekor qilish sababi:');
    if (reason) {
      try {
        await visitAPI.cancelVisit(visitId, {
          reason,
          cancelled_by: 'Admin'
        });
        loadVisits();
        alert('Tashrif bekor qilindi');
      } catch (error) {
        console.error('Cancel error:', error);
        alert('Xato: ' + error.message);
      }
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'SCHEDULED': '#3b82f6',
      'CONFIRMED': '#10b981',
      'IN_PROGRESS': '#f59e0b',
      'COMPLETED': '#22c55e',
      'CANCELLED': '#ef4444',
      'POSTPONED': '#6b7280',
      'NO_SHOW': '#991b1b'
    };
    return colors[status] || '#6b7280';
  };

  const getStatusText = (status) => {
    const texts = {
      'SCHEDULED': 'Rejalashtirilgan',
      'CONFIRMED': 'Tasdiqlangan',
      'IN_PROGRESS': 'Jarayonda',
      'COMPLETED': 'Yakunlangan',
      'CANCELLED': 'Bekor qilingan',
      'POSTPONED': 'Kechiktirilgan',
      'NO_SHOW': 'Kelmaganlar'
    };
    return texts[status] || status;
  };

  // Chart data
  const statusChartData = statistics ? {
    labels: ['Rejalashtirilgan', 'Jarayonda', 'Yakunlangan', 'Bekor qilingan'],
    datasets: [{
      data: [
        statistics.total_visits - statistics.completed_visits - statistics.in_progress_visits - statistics.cancelled_visits,
        statistics.in_progress_visits,
        statistics.completed_visits,
        statistics.cancelled_visits
      ],
      backgroundColor: ['#3b82f6', '#f59e0b', '#22c55e', '#ef4444'],
      borderWidth: 2,
      borderColor: '#fff'
    }]
  } : null;

  const completionRateData = statistics ? {
    labels: ['Bajarilgan', 'Bajarilmagan'],
    datasets: [{
      data: [statistics.completion_rate, 100 - statistics.completion_rate],
      backgroundColor: ['#10b981', '#e5e7eb'],
      borderWidth: 0
    }]
  } : null;

  return (
    <div className="visit-management">
      <div className="vm-header">
        <h1>Tashrif Boshqaruvi</h1>
        <p className="vm-subtitle">Agent tashriflarini kuzatish va tahlil qilish</p>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="stats-grid">
          <div className="stat-card gradient-blue">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <div className="stat-label">Jami Tashriflar</div>
              <div className="stat-value">{statistics.total_visits}</div>
            </div>
          </div>
          
          <div className="stat-card gradient-green">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <div className="stat-label">Yakunlangan</div>
              <div className="stat-value">{statistics.completed_visits}</div>
            </div>
          </div>
          
          <div className="stat-card gradient-orange">
            <div className="stat-icon">⏳</div>
            <div className="stat-content">
              <div className="stat-label">Jarayonda</div>
              <div className="stat-value">{statistics.in_progress_visits}</div>
            </div>
          </div>
          
          <div className="stat-card gradient-purple">
            <div className="stat-icon">📸</div>
            <div className="stat-content">
              <div className="stat-label">Jami Rasmlar</div>
              <div className="stat-value">{statistics.total_images}</div>
            </div>
          </div>

          <div className="stat-card gradient-teal">
            <div className="stat-icon">⚡</div>
            <div className="stat-content">
              <div className="stat-label">Bajarilish Foizi</div>
              <div className="stat-value">{statistics.completion_rate}%</div>
            </div>
          </div>

          <div className="stat-card gradient-pink">
            <div className="stat-icon">⏱️</div>
            <div className="stat-content">
              <div className="stat-label">O'rtacha Vaqt</div>
              <div className="stat-value">{Math.round(statistics.average_duration)} daqiqa</div>
            </div>
          </div>
        </div>
      )}

      {/* Charts Section */}
      {statistics && (
        <div className="charts-section">
          <div className="chart-card">
            <h3>Status bo'yicha Taqsimot</h3>
            <div className="chart-container">
              <Doughnut 
                data={statusChartData} 
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'bottom'
                    }
                  }
                }}
              />
            </div>
          </div>

          <div className="chart-card">
            <h3>Bajarilish Darajasi</h3>
            <div className="chart-container">
              <Doughnut 
                data={completionRateData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'bottom'
                    }
                  }
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="filters-section">
        <h3>Filtrlash</h3>
        <div className="filters-grid">
          <input
            type="text"
            name="agent_code"
            placeholder="Agent kodi"
            value={filters.agent_code}
            onChange={handleFilterChange}
          />
          <input
            type="text"
            name="client_code"
            placeholder="Klient kodi"
            value={filters.client_code}
            onChange={handleFilterChange}
          />
          <select
            name="visit_status"
            value={filters.visit_status}
            onChange={handleFilterChange}
          >
            <option value="">Barcha statuslar</option>
            <option value="SCHEDULED">Rejalashtirilgan</option>
            <option value="IN_PROGRESS">Jarayonda</option>
            <option value="COMPLETED">Yakunlangan</option>
            <option value="CANCELLED">Bekor qilingan</option>
          </select>
          <input
            type="date"
            name="date_from"
            value={filters.date_from}
            onChange={handleFilterChange}
          />
          <input
            type="date"
            name="date_to"
            value={filters.date_to}
            onChange={handleFilterChange}
          />
          <button className="btn-reset" onClick={() => setFilters({
            agent_code: '',
            client_code: '',
            visit_status: '',
            date_from: '',
            date_to: ''
          })}>
            Tozalash
          </button>
        </div>
      </div>

      {/* Visits Table */}
      <div className="visits-section">
        <h3>Tashriflar Ro'yxati ({visits.length})</h3>
        {loading ? (
          <div className="loading">Yuklanmoqda...</div>
        ) : (
          <div className="table-container">
            <table className="visits-table">
              <thead>
                <tr>
                  <th>Sana</th>
                  <th>Agent</th>
                  <th>Klient</th>
                  <th>Turi</th>
                  <th>Status</th>
                  <th>Davomiyligi</th>
                  <th>Amallar</th>
                </tr>
              </thead>
              <tbody>
                {visits.map(visit => (
                  <tr key={visit.visit_id}>
                    <td>{visit.planned_date}</td>
                    <td>
                      <div className="agent-cell">
                        <div className="agent-name">{visit.agent_name}</div>
                        <div className="agent-code">{visit.agent_code}</div>
                      </div>
                    </td>
                    <td>
                      <div className="client-cell">
                        <div className="client-name">{visit.client_name}</div>
                        <div className="client-code">{visit.client_code}</div>
                      </div>
                    </td>
                    <td>{visit.visit_type}</td>
                    <td>
                      <span 
                        className="status-badge"
                        style={{ backgroundColor: getStatusColor(visit.visit_status) }}
                      >
                        {getStatusText(visit.visit_status)}
                      </span>
                    </td>
                    <td>
                      {visit.duration_minutes ? 
                        `${visit.duration_minutes} daqiqa` : 
                        '-'
                      }
                    </td>
                    <td>
                      <div className="action-buttons">
                        <button 
                          className="btn-action btn-view"
                          onClick={() => handleViewDetails(visit.visit_id)}
                          title="Ko'rish"
                        >
                          👁️
                        </button>
                        {visit.visit_status === 'SCHEDULED' && (
                          <button 
                            className="btn-action btn-checkin"
                            onClick={() => handleCheckIn(visit.visit_id)}
                            title="Check-in"
                          >
                            📍
                          </button>
                        )}
                        {visit.visit_status === 'IN_PROGRESS' && (
                          <button 
                            className="btn-action btn-checkout"
                            onClick={() => handleCheckOut(visit.visit_id)}
                            title="Check-out"
                          >
                            ✅
                          </button>
                        )}
                        {visit.visit_status !== 'COMPLETED' && (
                          <button 
                            className="btn-action btn-cancel"
                            onClick={() => handleCancelVisit(visit.visit_id)}
                            title="Bekor qilish"
                          >
                            ❌
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Visit Details Modal */}
      {showModal && selectedVisit && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Tashrif Tafsilotlari</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="detail-grid">
                <div className="detail-item">
                  <label>Agent:</label>
                  <div>{selectedVisit.agent_name} ({selectedVisit.agent_code})</div>
                </div>
                <div className="detail-item">
                  <label>Klient:</label>
                  <div>{selectedVisit.client_name}</div>
                </div>
                <div className="detail-item">
                  <label>Rejalashtirilgan sana:</label>
                  <div>{selectedVisit.planned_date} {selectedVisit.planned_time}</div>
                </div>
                <div className="detail-item">
                  <label>Status:</label>
                  <div>
                    <span 
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(selectedVisit.visit_status) }}
                    >
                      {getStatusText(selectedVisit.visit_status)}
                    </span>
                  </div>
                </div>
                {selectedVisit.actual_start_time && (
                  <div className="detail-item">
                    <label>Boshlandi:</label>
                    <div>{new Date(selectedVisit.actual_start_time).toLocaleString('uz')}</div>
                  </div>
                )}
                {selectedVisit.actual_end_time && (
                  <div className="detail-item">
                    <label>Tugadi:</label>
                    <div>{new Date(selectedVisit.actual_end_time).toLocaleString('uz')}</div>
                  </div>
                )}
                {selectedVisit.duration_minutes && (
                  <div className="detail-item">
                    <label>Davomiyligi:</label>
                    <div>{selectedVisit.duration_minutes} daqiqa</div>
                  </div>
                )}
                {selectedVisit.purpose && (
                  <div className="detail-item full-width">
                    <label>Maqsad:</label>
                    <div>{selectedVisit.purpose}</div>
                  </div>
                )}
                {selectedVisit.outcome && (
                  <div className="detail-item full-width">
                    <label>Natija:</label>
                    <div>{selectedVisit.outcome}</div>
                  </div>
                )}
                {selectedVisit.notes && (
                  <div className="detail-item full-width">
                    <label>Izohlar:</label>
                    <div>{selectedVisit.notes}</div>
                  </div>
                )}
                {selectedVisit.images && selectedVisit.images.length > 0 && (
                  <div className="detail-item full-width">
                    <label>Rasmlar ({selectedVisit.images.length}):</label>
                    <div className="images-grid">
                      {selectedVisit.images.map(img => (
                        <div key={img.image_id} className="image-card">
                          <img src={img.thumbnail_url || img.image_url} alt={img.image_type} />
                          <p>{img.image_type}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VisitManagement;
