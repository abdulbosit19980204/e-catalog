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
import ClientDetail from "./components/ClientDetail";
import NomenklaturaDetail from "./components/NomenklaturaDetail";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminLayout from "./components/AdminLayout";
import AdminDashboard from "./components/AdminDashboard";
import ProjectAdmin from "./components/admin/ProjectAdmin";
import ClientAdmin from "./components/admin/ClientAdmin";
import NomenklaturaAdmin from "./components/admin/NomenklaturaAdmin";
import IntegrationAdmin from "./components/admin/IntegrationAdmin";
import ChatPage from "./components/ChatPage";
import ChatAdmin from "./components/admin/ChatAdmin";
import ChatSettings from "./components/admin/ChatSettings";
import UserAdmin from "./components/admin/UserAdmin";
import ClearDbPage from "./components/admin/ClearDbPage";
import DuplicatesPage from "./components/admin/DuplicatesPage";
import AgentTracker from "./components/admin/AgentTracker";
import AgentTrackerPage from "./components/AgentTrackerPage";

function App() {
  return (
    <NotificationProvider>
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
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
          <Route path="/chat" element={
            <>
              <Navigation />
              <main className="App-main">
                <ChatPage />
              </main>
            </>
          } />
          <Route path="/tracker" element={
            <ProtectedRoute>
              <AgentTrackerPage />
            </ProtectedRoute>
          } />
          
          {/* Detail Pages */}
          <Route path="/clients/:id" element={<ClientDetail />} />
          <Route path="/nomenklatura/:id" element={<NomenklaturaDetail />} />
          
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
          <Route
            path="/admin/chat"
            element={
              <ProtectedRoute>
                <AdminLayout>
                  <ChatAdmin />
                </AdminLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/chat-settings"
            element={
              <ProtectedRoute>
                <AdminLayout>
                  <ChatSettings />
                </AdminLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/users"
            element={
              <ProtectedRoute>
                <AdminLayout>
                  <UserAdmin />
                </AdminLayout>
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/admin/clear-db"
            element={
              <ProtectedRoute>
                <AdminLayout>
                  <ClearDbPage />
                </AdminLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/duplicates"
            element={
              <ProtectedRoute>
                <AdminLayout>
                  <DuplicatesPage />
                </AdminLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/agent-tracker"
            element={
              <ProtectedRoute>
                <AdminLayout>
                  <AgentTracker />
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
