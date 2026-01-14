import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import "./Navigation.css";

const Navigation = () => {
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    if (typeof window === "undefined") return false;
    return !!localStorage.getItem("authToken");
  });

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const isActive = (paths) => {
    const pathList = Array.isArray(paths) ? paths : [paths];
    return pathList.some((path) => location.pathname.startsWith(path))
      ? "active"
      : "";
  };

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (menuOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }

    return () => {
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return undefined;
    }
    const handleAuthChange = () => {
      setIsAuthenticated(!!localStorage.getItem("authToken"));
    };

    window.addEventListener("storage", handleAuthChange);
    window.addEventListener("auth-token-changed", handleAuthChange);

    return () => {
      window.removeEventListener("storage", handleAuthChange);
      window.removeEventListener("auth-token-changed", handleAuthChange);
    };
  }, []);

  const toggleMenu = () => setMenuOpen((prev) => !prev);
  const handleLinkClick = () => setMenuOpen(false);

  return (
    <>
      <nav className={`navigation ${scrolled ? "scrolled" : ""}`}>
        <div className="nav-container">
          <Link to="/" className="nav-logo">
            <span className="logo-mark">E</span>
            <span className="logo-text">Catalog</span>
          </Link>

          <button
            className={`menu-toggle ${menuOpen ? "open" : ""}`}
            onClick={toggleMenu}
            aria-expanded={menuOpen}
            aria-label="Toggle navigation"
          >
            <span></span>
            <span></span>
            <span></span>
          </button>

          <ul className={`nav-menu ${menuOpen ? "visible" : ""}`}>
            <li>
              <Link
                to="/"
                className={`nav-link ${isActive("/")}`}
                onClick={handleLinkClick}
              >
                Projects
              </Link>
            </li>
            {isAuthenticated && (
              <li>
                <Link
                  to="/clients"
                  className={`nav-link ${isActive("/clients")}`}
                  onClick={handleLinkClick}
                >
                  Clients
                </Link>
              </li>
            )}
            <li>
              <Link
                to="/nomenklatura"
                className={`nav-link ${isActive("/nomenklatura")}`}
                onClick={handleLinkClick}
              >
                Nomenklatura
              </Link>
            </li>
            <li>
              <Link
                to="/chat"
                className={`nav-link ${isActive("/chat")}`}
                onClick={handleLinkClick}
              >
                Chat
              </Link>
            </li>
            {isAuthenticated && (
              <li>
                <Link
                  to="/tracker"
                  className={`nav-link ${isActive("/tracker")}`}
                  onClick={handleLinkClick}
                >
                  Tracker
                </Link>
              </li>
            )}
            <li>
              <Link
                to={isAuthenticated ? "/admin" : "/login"}
                className={`nav-link ${isActive(["/admin", "/login"])}`}
                onClick={handleLinkClick}
              >
                Admin
              </Link>
            </li>
          </ul>
        </div>
      </nav>

      {menuOpen && <div className="nav-backdrop" onClick={toggleMenu}></div>}
    </>
  );
};

export default Navigation;

