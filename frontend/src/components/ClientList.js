import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { clientAPI } from "../api";
import { useNotification } from "../contexts/NotificationContext";
import "./ClientList.css";

const ClientList = () => {
  const navigate = useNavigate();
  /* eslint-disable no-unused-vars */
  const { error: showError } = useNotification();
  /* eslint-enable no-unused-vars */
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [createdFrom, setCreatedFrom] = useState("");
  const [createdTo, setCreatedTo] = useState("");

  const loadClients = React.useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {
        page,
        search: search || undefined,
        created_from: createdFrom || undefined,
        created_to: createdTo || undefined,
      };
      const response = await clientAPI.getClients(params);
      setClients(response.data.results || response.data);
      if (response.data.count) {
        setTotalPages(Math.ceil(response.data.count / 20));
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Xatolik yuz berdi");
      console.error("Error loading clients:", err);
    } finally {
      setLoading(false);
    }
  }, [page, search, createdFrom, createdTo]);

  useEffect(() => {
    loadClients();
  }, [loadClients]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    loadClients();
  };

  const handleCardClick = (clientCode1c) => {
    navigate(`/clients/${clientCode1c}`);
  };

  return (
    <div className="client-list-container">
      <div className="client-list-header">
        <h1>Clients</h1>
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Qidirish..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
          <div className="date-filters">
            <label>
              Yaratilgan (dan)
              <input
                type="date"
                value={createdFrom}
                onChange={(e) => {
                  setCreatedFrom(e.target.value);
                  setPage(1);
                }}
              />
            </label>
            <label>
              Yaratilgan (gacha)
              <input
                type="date"
                value={createdTo}
                onChange={(e) => {
                  setCreatedTo(e.target.value);
                  setPage(1);
                }}
              />
            </label>
          </div>
          <button type="submit" className="search-button">
            Qidirish
          </button>
        </form>
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Yuklanmoqda...</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && (
        <>
          <div className="clients-grid">
            {clients.length === 0 ? (
              <div className="no-clients">
                <p>Clients topilmadi</p>
              </div>
            ) : (
              clients.map((client) => (
                <div 
                  key={client.id} 
                  className="client-card"
                  onClick={() => handleCardClick(client.client_code_1c)}
                >
                  <div className="client-image">
                    {client.images && client.images.length > 0 ? (
                      <img
                        src={client.images[0].image_sm_url || client.images[0].image_url || client.images[0].image}
                        alt={client.name}
                      />
                    ) : (
                      <div className="no-image">Rasm yo'q</div>
                    )}
                  </div>
                  <div className="client-info">
                    <h3>{client.name}</h3>
                    <p className="client-code">Code: {client.client_code_1c}</p>
                    {client.email && (
                      <p className="client-email">
                        <span className="icon">📧</span> {client.email}
                      </p>
                    )}
                    {client.phone && (
                      <p className="client-phone">
                        <span className="icon">📞</span> {client.phone}
                      </p>
                    )}
                    {client.description && (
                      <div
                        className="client-description-preview"
                        dangerouslySetInnerHTML={{ 
                          __html: client.description.length > 100 
                            ? client.description.substring(0, 100) + '...' 
                            : client.description 
                        }}
                      />
                    )}
                    <div className="client-meta">
                      <span className={`status ${client.is_active ? "active" : "inactive"}`}>
                        {client.is_active ? "Active" : "Inactive"}
                      </span>
                      <span className="images-count">
                        {client.images?.length || 0} ta rasm
                      </span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="page-button"
              >
                Oldingi
              </button>
              <span className="page-info">
                Sahifa {page} / {totalPages}
              </span>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page === totalPages}
                className="page-button"
              >
                Keyingi
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ClientList;

