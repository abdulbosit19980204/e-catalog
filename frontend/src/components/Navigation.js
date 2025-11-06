import React from "react";
import { Link, useLocation } from "react-router-dom";
import "./Navigation.css";

const Navigation = () => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path ? "active" : "";
  };

  return (
    <nav className="navigation">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          E-Catalog
        </Link>
        <ul className="nav-menu">
          <li>
            <Link to="/" className={`nav-link ${isActive("/")}`}>
              Projects
            </Link>
          </li>
          <li>
            <Link to="/clients" className={`nav-link ${isActive("/clients")}`}>
              Clients
            </Link>
          </li>
          <li>
            <Link to="/nomenklatura" className={`nav-link ${isActive("/nomenklatura")}`}>
              Nomenklatura
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navigation;

