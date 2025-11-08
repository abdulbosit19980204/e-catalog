import React, { useEffect, useState } from "react";
import { clientAPI } from "../api";
import { useNotification } from "../contexts/NotificationContext";
import "./ClientList.css";

const ClientList = () => {
  const { error: showError } = useNotification();
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedClient, setSelectedClient] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [createdFrom, setCreatedFrom] = useState("");
  const [createdTo, setCreatedTo] = useState("");

  useEffect(() => {
    loadClients();
  }, [page, search, createdFrom, createdTo]);

  const loadClients = async () => {
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
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    loadClients();
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
                  onClick={() => {
                    setSelectedClient(client);
                    setCurrentImageIndex(0);
                    setShowDetailModal(true);
                  }}
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

      {showDetailModal && selectedClient && (
        <div className="modal-overlay" onClick={() => setShowDetailModal(false)}>
          <div className="client-detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedClient.name}</h2>
              <button 
                className="modal-close"
                onClick={() => setShowDetailModal(false)}
              >
                ×
              </button>
            </div>
            
            <div className="client-detail-content">
              <div className="client-detail-info">
                <div className="info-row">
                  <strong>Code 1C:</strong>
                  <span>{selectedClient.client_code_1c}</span>
                </div>
                {selectedClient.email && (
                  <div className="info-row">
                    <strong>Email:</strong>
                    <span>{selectedClient.email}</span>
                  </div>
                )}
                {selectedClient.phone && (
                  <div className="info-row">
                    <strong>Phone:</strong>
                    <span>{selectedClient.phone}</span>
                  </div>
                )}
                <div className="info-row">
                  <strong>Status:</strong>
                  <span className={`status ${selectedClient.is_active ? "active" : "inactive"}`}>
                    {selectedClient.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
              </div>

              {selectedClient.description && (
                <div className="client-description-full">
                  <h3>Description</h3>
                  <div
                    className="description-content"
                    dangerouslySetInnerHTML={{ __html: selectedClient.description }}
                  />
                </div>
              )}

              {selectedClient.images && selectedClient.images.length > 0 && (
                <div className="client-images-gallery">
                  <h3>Rasmlar ({selectedClient.images.length})</h3>
                  <div className="gallery-main">
                    <div className="main-image-container">
                      <img
                        src={
                          selectedClient.images[currentImageIndex]?.image_lg_url ||
                          selectedClient.images[currentImageIndex]?.image_md_url ||
                          selectedClient.images[currentImageIndex]?.image_url ||
                          selectedClient.images[currentImageIndex]?.image
                        }
                        alt={`${selectedClient.name} - Image ${currentImageIndex + 1}`}
                        className="main-image"
                      />
                      {selectedClient.images.length > 1 && (
                        <>
                          <button
                            className="gallery-nav gallery-prev"
                            onClick={(e) => {
                              e.stopPropagation();
                              setCurrentImageIndex((prev) => 
                                prev === 0 ? selectedClient.images.length - 1 : prev - 1
                              );
                            }}
                          >
                            ‹
                          </button>
                          <button
                            className="gallery-nav gallery-next"
                            onClick={(e) => {
                              e.stopPropagation();
                              setCurrentImageIndex((prev) => 
                                prev === selectedClient.images.length - 1 ? 0 : prev + 1
                              );
                            }}
                          >
                            ›
                          </button>
                        </>
                      )}
                    </div>
                    {selectedClient.images.length > 1 && (
                      <div className="gallery-thumbnails">
                        {selectedClient.images.map((image, index) => (
                          <div
                            key={image.id}
                            className={`thumbnail ${index === currentImageIndex ? 'active' : ''}`}
                            onClick={(e) => {
                              e.stopPropagation();
                              setCurrentImageIndex(index);
                            }}
                          >
                            <img
                              src={image.image_thumbnail_url || image.image_sm_url || image.image_url || image.image}
                              alt={`Thumbnail ${index + 1}`}
                            />
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClientList;

