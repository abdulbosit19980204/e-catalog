import React, { useEffect, useState } from "react";
import { projectAPI, clientAPI, nomenklaturaAPI } from "../api";
import "./AdminDashboard.css";

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    projects: 0,
    clients: 0,
    nomenklatura: 0,
    loading: true,
  });

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [projectsRes, clientsRes, nomenklaturaRes] = await Promise.all([
        projectAPI.getProjects({ page_size: 1 }),
        clientAPI.getClients({ page_size: 1 }),
        nomenklaturaAPI.getNomenklatura({ page_size: 1 }),
      ]);

      setStats({
        projects: projectsRes.data.count || projectsRes.data.length || 0,
        clients: clientsRes.data.count || clientsRes.data.length || 0,
        nomenklatura: nomenklaturaRes.data.count || nomenklaturaRes.data.length || 0,
        loading: false,
      });
    } catch (err) {
      console.error("Error loading stats:", err);
      setStats({ ...stats, loading: false });
    }
  };

  if (stats.loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Yuklanmoqda...</p>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📁</div>
          <div className="stat-info">
            <h3>Projects</h3>
            <p className="stat-number">{stats.projects}</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-info">
            <h3>Clients</h3>
            <p className="stat-number">{stats.clients}</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📦</div>
          <div className="stat-info">
            <h3>Nomenklatura</h3>
            <p className="stat-number">{stats.nomenklatura}</p>
          </div>
        </div>
      </div>
      
      <div className="dashboard-actions">
        <h2>Tezkor Amallar</h2>
        <div className="actions-grid">
          <a href="/admin/projects" className="action-card">
            <span className="action-label">📁 Projects</span>
            <span className="action-desc">Loyihalarni boshqarish va tahrirlash</span>
          </a>
          <a href="/admin/clients" className="action-card">
            <span className="action-label">👥 Clients</span>
            <span className="action-desc">Mijozlar bazasini ko'rish va yangilash</span>
          </a>
          <a href="/admin/nomenklatura" className="action-card">
            <span className="action-label">📦 Nomenklatura</span>
            <span className="action-desc">Mahsulotlar katalogini boshqarish</span>
          </a>
          <a href="/admin/integration" className="action-card">
            <span className="action-label">🔗 Integration</span>
            <span className="action-desc">1C bilan ma'lumotlarni sinxronlash</span>
          </a>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;

