import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { setAuthToken } from "../api";
import "./AdminLayout.css";

const AdminLayout = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = () => {
    setAuthToken(null);
    localStorage.removeItem("refreshToken");
    navigate("/login");
  };

  const isActive = (path) => {
    return location.pathname === path ? "active" : "";
  };

  return (
    <div className="admin-layout">
      <aside className={`admin-sidebar ${sidebarOpen ? "open" : "closed"}`}>
        <div className="sidebar-header">
          <h2>E-Catalog Admin</h2>
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? "←" : "→"}
          </button>
        </div>
        
        <nav className="sidebar-nav">
          <Link
            to="/admin"
            className={`nav-item ${isActive("/admin")}`}
          >
            <span className="nav-icon">📊</span>
            {sidebarOpen && <span>Dashboard</span>}
          </Link>
          
          <Link
            to="/admin/projects"
            className={`nav-item ${isActive("/admin/projects")}`}
          >
            <span className="nav-icon">📁</span>
            {sidebarOpen && <span>Projects</span>}
          </Link>
          
          <Link
            to="/admin/clients"
            className={`nav-item ${isActive("/admin/clients")}`}
          >
            <span className="nav-icon">👥</span>
            {sidebarOpen && <span>Clients</span>}
          </Link>
          
          <Link
            to="/admin/nomenklatura"
            className={`nav-item ${isActive("/admin/nomenklatura")}`}
          >
            <span className="nav-icon">📦</span>
            {sidebarOpen && <span>Nomenklatura</span>}
          </Link>
          
          <Link
            to="/admin/integration"
            className={`nav-item ${isActive("/admin/integration")}`}
          >
            <span className="nav-icon">🔗</span>
            {sidebarOpen && <span>Integration</span>}
          </Link>

          <Link
            to="/admin/chat"
            className={`nav-item ${isActive("/admin/chat")}`}
          >
            <span className="nav-icon">💬</span>
            {sidebarOpen && <span>Chat</span>}
          </Link>

          <Link
            to="/admin/chat-settings"
            className={`nav-item ${isActive("/admin/chat-settings")}`}
          >
            <span className="nav-icon">⚙️</span>
            {sidebarOpen && <span>Chat Settings</span>}
          </Link>

          <Link
            to="/admin/users"
            className={`nav-item ${isActive("/admin/users")}`}
          >
            <span className="nav-icon">👤</span>
            {sidebarOpen && <span>Users</span>}
          </Link>

          <Link
            to="/admin/clear-db"
            className={`nav-item ${isActive("/admin/clear-db")}`}
          >
            <span className="nav-icon">🗑️</span>
            {sidebarOpen && <span>Clear DB</span>}
          </Link>
        </nav>
        
        <div className="sidebar-footer">
          <button onClick={handleLogout} className="logout-button">
            {sidebarOpen && <span>Chiqish</span>}
          </button>
        </div>
      </aside>
      
      <main className="admin-main">
        <header className="admin-header">
          <h1>Admin Panel</h1>
        </header>
        <div className="admin-content">
          {children}
        </div>
      </main>
    </div>
  );
};

export default AdminLayout;

