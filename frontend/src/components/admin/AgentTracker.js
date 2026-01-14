import React, { useState, useEffect, useRef, useCallback } from "react";
import { agentLocationAPI, clientAPI } from "../../api";
import "./AgentTracker.css";

const AgentTracker = () => {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState("");
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [viewMode, setViewMode] = useState("day"); // day, month, year
  const [startTime, setStartTime] = useState("00:00");
  const [endTime, setEndTime] = useState("23:59");
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ points: 0, distance: 0, stops: 0 });
  const [regionalActivity, setRegionalActivity] = useState([]);
  const [error, setError] = useState(null);

  const mapRef = useRef(null);
  const ymapsRef = useRef(null);
  const mapInstanceRef = useRef(null);

  // Load Yandex Maps Script
  useEffect(() => {
    const script = document.createElement("script");
    const apiKey = process.env.REACT_APP_YANDEX_MAPS_KEY || "";
    script.src = `https://api-maps.yandex.ru/2.1/?lang=ru_RU${apiKey ? `&apikey=${apiKey}` : ""}`;
    script.async = true;
    script.onload = () => {
      window.ymaps.ready(() => {
        ymapsRef.current = window.ymaps;
        initMap();
      });
    };
    document.body.appendChild(script);

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.destroy();
      }
    };
  }, []);

  const initMap = () => {
    if (!ymapsRef.current || mapInstanceRef.current) return;

    mapInstanceRef.current = new ymapsRef.current.Map("yandex-map", {
      center: [41.311081, 69.240562], // Tashkent
      zoom: 12,
      controls: ["zoomControl", "typeSelector", "fullscreenControl"],
    });
  };

  // Fetch unique agents
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const res = await agentLocationAPI.getUniqueAgents();
        setAgents(res.data || []);
      } catch (err) {
        console.error("Failed to fetch agents", err);
      }
    };
    fetchAgents();
  }, []);

  const drawTrajectory = useCallback(async () => {
    if (!selectedAgent || !selectedDate || !ymapsRef.current || !mapInstanceRef.current) return;

    setLoading(true);
    setError(null);
    mapInstanceRef.current.geoObjects.removeAll();

    try {
      const res = await agentLocationAPI.getTrajectory(selectedAgent, selectedDate);
      let allPoints = res.data.points || [];
      let allVisits = res.data.visits || [];

      // Filter by time
      const points = allPoints.filter(p => {
        const timeStr = new Date(p.time).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
        return timeStr >= startTime && timeStr <= endTime;
      });

      const visits = allVisits.filter(v => {
        const timeStr = new Date(v.time).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
        return timeStr >= startTime && timeStr <= endTime;
      });

      if (points.length === 0) {
        setError("Ushbu kunda ma'lumot topilmadi");
        setStats({ points: 0, distance: 0, stops: 0 });
        setLoading(false);
        return;
      }

      const coordinates = points.map((p) => [p.lat, p.lng]);
      
      // Calculate Stats & segments
      let totalDistance = 0;
      let stopsCount = 0;
      const segments = [];

      for (let i = 0; i < points.length - 1; i++) {
        const p1 = points[i];
        const p2 = points[i + 1];
        
        // Duration in minutes
        const duration = (new Date(p2.time) - new Date(p1.time)) / 1000 / 60;
        
        let color = "#10b981"; // moving
        if (duration > 15) {
          color = "#ef4444"; // long stop
          stopsCount++;
        } else if (duration > 5) {
          color = "#f59e0b"; // short stop
          stopsCount++;
        }

        // Add stop markers with coordinates
        if (duration > 5) {
          const stopMarker = new ymapsRef.current.Placemark(
            [p1.lat, p1.lng],
            { 
              balloonContent: `
                <strong>To'xtash</strong><br/>
                Vaqt: ${new Date(p1.time).toLocaleTimeString()}<br/>
                Davomiyligi: ${Math.round(duration)} min<br/>
                Kordinata: ${p1.lat}, ${p1.lng}
              `
            },
            { preset: color === "#ef4444" ? "islands#redCircleDotIcon" : "islands#orangeCircleDotIcon" }
          );
          mapInstanceRef.current.geoObjects.add(stopMarker);
        }

        segments.push({
          coords: [[p1.lat, p1.lng], [p2.lat, p2.lng]],
          color: color
        });

        // Simple distance calculation (rough approximation)
        const d = Math.sqrt(Math.pow(p2.lat - p1.lat, 2) + Math.pow(p2.lng - p1.lng, 2)) * 111.32;
        totalDistance += d;
      }

      setStats({
        points: points.length,
        distance: totalDistance.toFixed(2),
        stops: stopsCount,
        visits: visits.length
      });

      // Fetch regional stats for the month if in month/year mode
      if (viewMode !== 'day') {
        const dateObj = new Date(selectedDate);
        let date_from, date_to;
        if (viewMode === 'month') {
          date_from = new Date(dateObj.getFullYear(), dateObj.getMonth(), 1).toISOString().split('T')[0];
          date_to = new Date(dateObj.getFullYear(), dateObj.getMonth() + 1, 0).toISOString().split('T')[0];
        } else {
          date_from = new Date(dateObj.getFullYear(), 0, 1).toISOString().split('T')[0];
          date_to = new Date(dateObj.getFullYear(), 11, 31).toISOString().split('T')[0];
        }
        
        const regRes = await agentLocationAPI.getRegionalActivity({
          agent_code: selectedAgent,
          date_from,
          date_to
        });
        setRegionalActivity(regRes.data.regions || []);
      }

      // Draw segments
      segments.forEach(seg => {
        const polyline = new ymapsRef.current.Polyline(
          seg.coords,
          { hintContent: "Agent harakati" },
          {
            strokeColor: seg.color,
            strokeWidth: 5,
            strokeOpacity: 0.8
          }
        );
        mapInstanceRef.current.geoObjects.add(polyline);
      });

      // Add Start (Green) and End (Red) markers
      const startPoint = new ymapsRef.current.Placemark(
        coordinates[0],
        { 
          balloonContent: `
            <strong>Boshlanish:</strong> ${new Date(points[0].time).toLocaleTimeString()}<br/>
            <strong>Kordinata:</strong> ${points[0].lat}, ${points[0].lng}
          ` 
        },
        { preset: "islands#greenDotIconWithCaption" }
      );
      
      const endPoint = new ymapsRef.current.Placemark(
        coordinates[coordinates.length - 1],
        { 
          balloonContent: `
            <strong>Oxirgi nuqta:</strong> ${new Date(points[points.length - 1].time).toLocaleTimeString()}<br/>
            <strong>Kordinata:</strong> ${points[points.length - 1].lat}, ${points[points.length - 1].lng}
          ` 
        },
        { preset: "islands#redDotIconWithCaption" }
      );

      mapInstanceRef.current.geoObjects.add(startPoint);
      mapInstanceRef.current.geoObjects.add(endPoint);

      // Draw Visits
      visits.forEach(v => {
        const visitMarker = new ymapsRef.current.Placemark(
          [v.lat, v.lng],
          { 
            balloonContent: `
              <strong>Visit: ${v.client_name}</strong><br/>
              Vaqt: ${new Date(v.time).toLocaleTimeString()}<br/>
              Kategoriya: ${v.category || 'Nomalum'}<br/>
              Status: ${v.status || 'Nomalum'}
            `,
            hintContent: `Visit: ${v.client_name}`
          },
          { preset: "islands#blueShoppingIcon" }
        );
        mapInstanceRef.current.geoObjects.add(visitMarker);
      });

      // Fit map to bounds
      mapInstanceRef.current.setBounds(mapInstanceRef.current.geoObjects.getBounds(), {
        checkZoomRange: true,
        zoomMargin: 50
      });

    } catch (err) {
      console.error("Trajectory fetch failed", err);
      setError("Ma'lumotlarni yuklashda xatolik yuz berdi");
    } finally {
      setLoading(false);
    }
  }, [selectedAgent, selectedDate, startTime, endTime, viewMode]);

  const drawRegionalHeatmap = useCallback(async () => {
    if (!ymapsRef.current || !mapInstanceRef.current || regionalActivity.length === 0) return;

    try {
      // Load GeoJSON for Uzbekistan Regions
      // simplified ADM1
      const geojsonUrl = "https://raw.githubusercontent.com/akbartus/GeoJSON-Uzbekistan/master/uzbekistan_regional.geojson";
      const response = await fetch(geojsonUrl);
      const data = await response.json();

      const objectManager = new ymapsRef.current.ObjectManager();
      
      // Map regionalActivity to a lookup
      const activityMap = {};
      regionalActivity.forEach(ra => {
        if (ra.region) activityMap[ra.region.toLowerCase()] = ra.points_count;
      });

      const maxCount = Math.max(...regionalActivity.map(ra => ra.points_count), 1);

      data.features.forEach((feature, idx) => {
        const regionName = feature.properties.name || feature.properties.name_uz || "";
        const activity = activityMap[regionName.toLowerCase()] || 0;
        
        // Calculate color (from light blue to deep red)
        let color = "#e2e8f0"; // default greyish for "not at all"
        if (activity > 0) {
          const ratio = activity / maxCount;
          // Interpolate between #bfdbfe (light blue) and #dc2626 (red)
          if (ratio < 0.3) color = "#93c5fd";
          else if (ratio < 0.7) color = "#fb923c";
          else color = "#dc2626";
        }

        feature.id = idx;
        feature.options = {
          fillColor: color,
          fillOpacity: 0.5,
          strokeColor: "#ffffff",
          strokeWidth: 1,
          labelLayout: '<div>{{properties.name}}</div>'
        };
        
        feature.properties.balloonContent = `
          <strong>${regionName}</strong><br/>
          Aktivlik: ${activity} ta nuqta
        `;
      });

      objectManager.add(data);
      mapInstanceRef.current.geoObjects.add(objectManager);

      // Fit map to Uzbekistan
      mapInstanceRef.current.setCenter([41.3, 64.5], 6);

    } catch (err) {
      console.error("Heatmap failed", err);
    }
  }, [regionalActivity]);

  useEffect(() => {
    if (selectedAgent && selectedDate) {
      drawTrajectory().then(() => {
        if (viewMode !== 'day') {
          drawRegionalHeatmap();
        }
      });
    }
  }, [selectedAgent, selectedDate, startTime, endTime, viewMode, drawTrajectory, drawRegionalHeatmap]);

  return (
    <div className="agent-tracker-container">
      <aside className="tracker-sidebar">
        <div className="sidebar-header">
          <h2>
            <i className="fas fa-map-marker-alt"></i> Tracker
          </h2>
        </div>

        <div className="sidebar-content">
          <div className="view-mode-tabs">
            <button 
              className={viewMode === 'day' ? 'active' : ''} 
              onClick={() => setViewMode('day')}
            >Kunlik</button>
            <button 
              className={viewMode === 'month' ? 'active' : ''} 
              onClick={() => setViewMode('month')}
            >Oylik</button>
            <button 
              className={viewMode === 'year' ? 'active' : ''} 
              onClick={() => setViewMode('year')}
            >Yillik</button>
          </div>

          <div className="filter-group">
            <label>Agent tanlang</label>
            <select
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value)}
            >
              <option value="">Agentni tanlang...</option>
              {agents.map((a) => (
                <option key={a.agent_code} value={a.agent_code}>
                  {a.agent_name || a.agent_code}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>{viewMode === 'day' ? 'Sana' : (viewMode === 'month' ? 'Oy' : 'Yil')}</label>
            <input
              type={viewMode === 'day' ? "date" : (viewMode === 'month' ? "month" : "number")}
              value={viewMode === 'year' ? selectedDate.split('-')[0] : (viewMode === 'month' ? selectedDate.substring(0, 7) : selectedDate)}
              onChange={(e) => {
                let val = e.target.value;
                if (viewMode === 'year') val = `${val}-01-01`;
                if (viewMode === 'month') val = `${val}-01`;
                setSelectedDate(val);
              }}
              min={viewMode === 'year' ? "2020" : ""}
              max={viewMode === 'year' ? "2100" : ""}
            />
          </div>

          {viewMode === 'day' && (
            <div className="filter-group">
              <label>Vaqt oralig'i</label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  type="time"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  style={{ flex: 1 }}
                />
                <input
                  type="time"
                  value={endTime}
                  onChange={(e) => setEndTime(e.target.value)}
                  style={{ flex: 1 }}
                />
              </div>
            </div>
          )}

          <div className="tracker-stats">
            <div className="stat-card">
              <span className="stat-label">Nuqtalar</span>
              <span className="stat-value">{stats.points}</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Masofa (km)</span>
              <span className="stat-value">{stats.distance}</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">To'xtashlar</span>
              <span className="stat-value">{stats.stops}</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Visitlar</span>
              <span className="stat-value">{stats.visits || 0}</span>
            </div>
          </div>

          {viewMode !== 'day' && regionalActivity.length > 0 && (
            <div className="regional-stats">
              <h3>Regionlar bo'yicha aktivlik</h3>
              <div className="regional-list">
                {regionalActivity.map((ra, idx) => (
                  <div key={idx} className="regional-item">
                    <span className="region-name">{ra.region || 'Nomalum'}</span>
                    <span className="region-count">{ra.points_count} ta</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {error && <div className="tracker-error">{error}</div>}
        </div>
      </aside>

      <main className="map-wrapper">
        <div id="yandex-map"></div>

        {loading && (
          <div className="tracker-loading">
            <div className="loader-inner">
              <div className="spinner"></div>
              <span>Xaritaga yuklanmoqda...</span>
            </div>
          </div>
        )}

        <div className="map-overlay">
          {viewMode === 'day' ? (
            <>
              <div className="legend-item">
                <div className="color-dot moving"></div>
                <span className="legend-text">Harakatlanmoqda</span>
              </div>
              <div className="legend-item">
                <div className="color-dot short-stop"></div>
                <span className="legend-text">Qisqa to'xtash (&gt;5 min)</span>
              </div>
              <div className="legend-item">
                <div className="color-dot long-stop"></div>
                <span className="legend-text">Uzoq to'xtash (&gt;15 min)</span>
              </div>
            </>
          ) : (
            <>
              <div className="legend-title">Aktivlik darajasi</div>
              <div className="legend-item">
                <div className="color-dot" style={{ background: '#dc2626' }}></div>
                <span className="legend-text">Yuqori</span>
              </div>
              <div className="legend-item">
                <div className="color-dot" style={{ background: '#fb923c' }}></div>
                <span className="legend-text">O'rtacha</span>
              </div>
              <div className="legend-item">
                <div className="color-dot" style={{ background: '#93c5fd' }}></div>
                <span className="legend-text">Past</span>
              </div>
              <div className="legend-item">
                <div className="color-dot" style={{ background: '#e2e8f0' }}></div>
                <span className="legend-text">Mavjud emas</span>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
};

export default AgentTracker;
