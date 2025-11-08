import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { NotificationProvider } from "./contexts/NotificationContext";
import Notification from "./components/Notification";
import "./App.css";
import Navigation from "./components/Navigation";
import Home from "./components/Home";
import ClientList from "./components/ClientList";
import NomenklaturaList from "./components/NomenklaturaList";
import Login from "./components/Login";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminLayout from "./components/AdminLayout";
import AdminDashboard from "./components/AdminDashboard";
import ProjectAdmin from "./components/admin/ProjectAdmin";
import ClientAdmin from "./components/admin/ClientAdmin";
import NomenklaturaAdmin from "./components/admin/NomenklaturaAdmin";
import IntegrationAdmin from "./components/admin/IntegrationAdmin";

function App() {
  return (
    <NotificationProvider>
      <Router>
        <div className="App">
          <Notification />
          <Routes>
          {/* Public routes */}
          <Route path="/" element={
            <>
              <Navigation />
              <main className="App-main">
                <Home />
              </main>
            </>
          } />
          <Route path="/clients" element={
            <>
              <Navigation />
              <main className="App-main">
                <ClientList />
              </main>
            </>
          } />
          <Route path="/nomenklatura" element={
            <>
              <Navigation />
              <main className="App-main">
                <NomenklaturaList />
              </main>
            </>
          } />
          
          {/* Login */}
          <Route path="/login" element={<Login />} />
          
          {/* Admin routes */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute>
                <AdminLayout>
                  <AdminDashboard />
                </AdminLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/projects"
            element={
              <ProtectedRoute>
                <AdminLayout>
                  <ProjectAdmin />
                </AdminLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/clients"
            element={
              <ProtectedRoute>
                <AdminLayout>
                  <ClientAdmin />
                </AdminLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/nomenklatura"
            element={
              <ProtectedRoute>
                <AdminLayout>
                  <NomenklaturaAdmin />
                </AdminLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/integration"
            element={
              <ProtectedRoute>
                <AdminLayout>
                  <IntegrationAdmin />
                </AdminLayout>
              </ProtectedRoute>
            }
          />
          
          {/* Redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </NotificationProvider>
  );
}

export default App;
