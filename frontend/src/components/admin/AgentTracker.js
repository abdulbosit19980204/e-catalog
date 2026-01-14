import React, { useState, useEffect, useRef, useCallback } from "react";
import { agentLocationAPI, clientAPI } from "../../api";
import "./AgentTracker.css";

const AgentTracker = () => {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState("");
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [startTime, setStartTime] = useState("00:00");
  const [endTime, setEndTime] = useState("23:59");
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ points: 0, distance: 0, stops: 0 });
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
        { balloonContent: `Boshlanish: ${new Date(points[0].time).toLocaleTimeString()}` },
        { preset: "islands#greenDotIconWithCaption" }
      );
      
      const endPoint = new ymapsRef.current.Placemark(
        coordinates[coordinates.length - 1],
        { balloonContent: `Oxirgi nuqta: ${new Date(points[points.length - 1].time).toLocaleTimeString()}` },
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
  }, [selectedAgent, selectedDate, startTime, endTime]);

  useEffect(() => {
    if (selectedAgent && selectedDate) {
      drawTrajectory();
    }
  }, [selectedAgent, selectedDate, startTime, endTime, drawTrajectory]);

  return (
    <div className="agent-tracker-container">
      <aside className="tracker-sidebar">
        <div className="sidebar-header">
          <h2>
            <i className="fas fa-map-marker-alt"></i> Tracker
          </h2>
        </div>

        <div className="sidebar-content">
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
            <label>Sana</label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
            />
          </div>

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
        </div>
      </main>
    </div>
  );
};

export default AgentTracker;
