import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authAPI, setAuthToken } from "../api";
import { useNotification } from "../contexts/NotificationContext";
import "./Login.css";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { success, error: showError } = useNotification();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!username.trim() || !password.trim()) {
      showError("Iltimos, barcha maydonlarni to'ldiring");
      return;
    }

    setLoading(true);

    try {
      const response = await authAPI.login(username.trim(), password);
      const { access, refresh } = response.data;
      
      // Token saqlash
      setAuthToken(access);
      localStorage.setItem("refreshToken", refresh);
      
      success("Muvaffaqiyatli kirildi!");
      
      // Admin panel'ga o'tish
      setTimeout(() => {
        navigate("/admin");
      }, 500);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.response?.data?.message || "Login yoki parol noto'g'ri";
      showError(errorMsg);
      console.error("Login error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSubmit(e);
    }
  };

  return (
    <div className="login-page">
      <div className="login-background">
        <div className="bg-circle circle-1"></div>
        <div className="bg-circle circle-2"></div>
      </div>
      
      <div className="login-card">
        <div className="login-card-inner">
          <div className="login-brand">
            <div className="brand-logo">E</div>
            <h2>E-Catalog Admin</h2>
            <p>Xush kelibsiz! Panelga kirish uchun ma'lumotlarni kiriting.</p>
          </div>
          
          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label>Foydalanuvchi nomi</label>
              <div className="input-group">
                <span className="input-icon">👤</span>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Username"
                  required
                  disabled={loading}
                />
              </div>
            </div>
            
            <div className="form-group">
              <label>Parol</label>
              <div className="input-group">
                <span className="input-icon">🔒</span>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Password"
                  required
                  disabled={loading}
                />
                <button
                  type="button"
                  className="show-password"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? "👁️" : "👁️‍🗨️"}
                </button>
              </div>
            </div>
            
            <button
              type="submit"
              className="login-submit-btn"
              disabled={loading || !username.trim() || !password.trim()}
            >
              {loading ? (
                <div className="loading-spinner"></div>
              ) : (
                <>Tizimga kirish <span className="arrow">→</span></>
              )}
            </button>
          </form>
          
          <div className="login-footer">
            <p>© {new Date().getFullYear()} e-catalog.uz</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;

