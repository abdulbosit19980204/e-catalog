import React, { useState, useEffect, useCallback } from 'react';
import { coreAPI } from '../../api';
import './SystemHealth.css';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
  Legend
);

const MAX_HISTORY = 20;

const SystemHealth = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshInterval, setRefreshInterval] = useState(5000); // 5 seconds
  const [cpuHistory, setCpuHistory] = useState(new Array(MAX_HISTORY).fill(0));
  const [memHistory, setMemHistory] = useState(new Array(MAX_HISTORY).fill(0));

  const fetchStatus = useCallback(async () => {
    try {
      const res = await coreAPI.getStatus();
      const newData = res.data;
      setData(newData);
      
      if (newData?.system) {
        setCpuHistory(prev => [...prev.slice(1), newData.system.cpu_percent]);
        setMemHistory(prev => [...prev.slice(1), newData.system.memory.percent]);
      }
      
      setError(null);
    } catch (err) {
      console.error("Health check failed", err);
      setError("Server bilan aloqa uzildi");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const timer = setInterval(fetchStatus, refreshInterval);
    return () => clearInterval(timer);
  }, [fetchStatus, refreshInterval]);

  const getStatusClass = (status) => {
    switch (status) {
      case 'healthy': return 'status-up';
      case 'unhealthy': return 'status-down';
      default: return 'status-unknown';
    }
  };

  const formatLatency = (ms) => {
    if (ms === undefined) return 'N/A';
    return `${ms.toFixed(0)} ms`;
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false }
    },
    scales: {
      y: { min: 0, max: 100, display: false },
      x: { display: false }
    },
    elements: {
      point: { radius: 0 },
      line: { tension: 0.4 }
    }
  };

  const getChartData = (history, color) => ({
    labels: new Array(MAX_HISTORY).fill(''),
    datasets: [{
      fill: true,
      data: history,
      borderColor: color,
      backgroundColor: `${color}22`,
      borderWidth: 2,
    }]
  });

  if (!data && loading) return <div className="health-loading">Monitoring yuklanmoqda...</div>;

  return (
    <div className="system-health">
      <header className="health-header">
        <h1>Server Xolati Monitorni</h1>
        <div className="refresh-controls">
          <span>Yangilanish: </span>
          <select value={refreshInterval} onChange={(e) => setRefreshInterval(Number(e.target.value))}>
            <option value={5000}>5 soniya</option>
            <option value={30000}>30 soniya</option>
            <option value={60000}>1 daqiqa</option>
          </select>
          <button onClick={fetchStatus} disabled={loading} className="btn-refresh">
            {loading ? '...' : '🔄'}
          </button>
        </div>
      </header>

      {error && <div className="health-error-alert">{error}</div>}

      <div className="health-grid">
        {/* Connection Status Cards */}
        <section className="health-card services">
          <h2>Ulanishlar</h2>
          <div className="service-list">
            <div className={`service-item ${getStatusClass(data?.services?.database?.status)}`}>
              <div className="service-info">
                <h3>Ma'lumotlar Bazasi (DB)</h3>
                <span className="sub">{data?.services?.database?.engine} | {data?.services?.database?.host}</span>
              </div>
              <div className="service-metrics">
                <span className="latency">{formatLatency(data?.services?.database?.latency_ms)}</span>
                <span className="badge">{data?.services?.database?.status?.toUpperCase()}</span>
              </div>
            </div>

            <div className={`service-item ${getStatusClass(data?.services?.redis?.status)}`}>
              <div className="service-info">
                <h3>Redis (Caching)</h3>
                <span className="sub">{data?.services?.redis?.url}</span>
              </div>
              <div className="service-metrics">
                <span className="latency">{formatLatency(data?.services?.redis?.latency_ms)}</span>
                <span className="badge">{data?.services?.redis?.status?.toUpperCase()}</span>
              </div>
            </div>

            {/* Dynamic External Services */}
            {data?.services?.external && Object.entries(data.services.external).map(([key, service]) => (
                service.status !== 'not_configured' && (
                    <div key={key} className={`service-item ${getStatusClass(service.status)}`}>
                        <div className="service-info">
                            <h3>{service.name || key.replace(/_/g, ' ').toUpperCase()}</h3>
                            <span className="sub">{service.url || 'URL mavjud emas'}</span>
                        </div>
                        <div className="service-metrics">
                            {service.latency_ms !== undefined && (
                                <span className="latency">{formatLatency(service.latency_ms)}</span>
                            )}
                            <span className="badge">{service.status?.toUpperCase()}</span>
                        </div>
                        {service.error && (
                            <div className="service-error-detail">{service.error}</div>
                        )}
                    </div>
                )
            ))}
          </div>
        </section>

        {/* System Resource Cards */}
        <section className="health-card system">
          <h2>Server Resurslari</h2>
          <div className="metrics-grid">
            <div className="metric-box">
              <div className="metric-header">
                <label>CPU Yuklanishi</label>
                <span className="value">{data?.system?.cpu_percent}%</span>
              </div>
              <div className="mini-chart">
                <Line data={getChartData(cpuHistory, '#10b981')} options={chartOptions} />
              </div>
              <div className="progress-bar">
                <div className="fill" style={{width: `${data?.system?.cpu_percent}%`, background: data?.system?.cpu_percent > 80 ? '#ef4444' : '#10b981'}}></div>
              </div>
            </div>

            <div className="metric-box">
              <div className="metric-header">
                <label>Xotira (RAM) - {data?.system?.memory?.used_gb} / {data?.system?.memory?.total_gb} GB</label>
                <span className="value">{data?.system?.memory?.percent}%</span>
              </div>
              <div className="mini-chart">
                <Line data={getChartData(memHistory, '#3b82f6')} options={chartOptions} />
              </div>
              <div className="progress-bar">
                <div className="fill" style={{width: `${data?.system?.memory?.percent}%`, background: data?.system?.memory?.percent > 90 ? '#ef4444' : '#3b82f6'}}></div>
              </div>
            </div>

            <div className="metric-box">
              <div className="metric-header">
                <label>Disk - {data?.system?.disk?.used_gb} / {data?.system?.disk?.total_gb} GB</label>
                <span className="value">{data?.system?.disk?.percent}%</span>
              </div>
              <div className="progress-bar">
                <div className="fill" style={{width: `${data?.system?.disk?.percent}%`, background: data?.system?.disk?.percent > 85 ? '#ef4444' : '#8b5cf6'}}></div>
              </div>
            </div>
          </div>
          
          <div className="system-footer">
            <span>Uptime: {Math.floor((data?.system?.uptime_seconds || 0) / 3600)} soat</span>
            <span>Debug Mode: {data?.environment?.debug ? 'YOQILGAN' : 'OCHIRILGAN'}</span>
          </div>
        </section>

        {/* Top Processes Section */}
        <section className="health-card processes">
          <h2>Eng ko'p resurs yeyotgan servislar</h2>
          <div className="process-tables-grid">
            <div className="process-group">
              <h3>CPU bo'yicha TOP</h3>
              <div className="table-responsive">
                <table>
                  <thead>
                    <tr>
                      <th>Servis</th>
                      <th>CPU %</th>
                      <th>RAM</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data?.system?.top_processes_cpu?.map(p => (
                      <tr key={`cpu-${p.pid}`}>
                        <td className="proc-name" title={p.name}>{p.name}</td>
                        <td className="proc-val highlight">{p.cpu}%</td>
                        <td className="proc-val">{p.memory_mb} MB</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="process-group">
              <h3>Xotira (RAM) bo'yicha TOP</h3>
              <div className="table-responsive">
                <table>
                  <thead>
                    <tr>
                      <th>Servis</th>
                      <th>RAM</th>
                      <th>CPU %</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data?.system?.top_processes_mem?.map(p => (
                      <tr key={`mem-${p.pid}`}>
                        <td className="proc-name" title={p.name}>{p.name}</td>
                        <td className="proc-val highlight">{p.memory_mb} MB</td>
                        <td className="proc-val">{p.cpu}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default SystemHealth;
