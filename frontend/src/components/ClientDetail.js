import React, { useEffect, useState, useMemo } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { clientAPI } from "../api";
import "./NomenklaturaDetail.css"; // Reuse styling logic

const ClientDetail = () => {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const projectId = searchParams.get('project_id');
  const navigate = useNavigate();
  const [client, setClient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    const loadClient = async () => {
      try {
        setLoading(true);
        const response = await clientAPI.getClient(id, projectId);
        setClient(response.data);
      } catch (err) {
        setError("Mijoz topilmadi");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadClient();
  }, [id, projectId]);

  const detailImages = useMemo(() => {
    if (!client?.images?.length) return [];
    return client.images.map((image) =>
      image.image_lg_url || image.image_md_url || image.image_url || image.image
    );
  }, [client]);

  if (loading) return (
    <div className="detail-page-loading">
      <div className="spinner"></div>
      <p>Yuklanmoqda...</p>
    </div>
  );

  if (error || !client) return (
    <div className="detail-page-error">
      <h2>{error || "Mijoz topilmadi"}</h2>
      <button onClick={() => navigate("/clients")} className="btn-secondary">
        Ortga qaytish
      </button>
    </div>
  );

  return (
    <div className="detail-page-container">
        <button className="back-button" onClick={() => navigate("/clients")}>
          ← Barcha mijozlar
        </button>
        
        <div className="detail-main-card">
          <div className="detail-header-mobile">
            <h1>{client.name}</h1>
          </div>

          {detailImages.length > 0 ? (
            <div className="detail-gallery-section">
              <div className="gallery-main-view">
                <img
                  src={detailImages[currentImageIndex]}
                  alt={`${client.name} ${currentImageIndex + 1}`}
                  className="main-image"
                />
                {detailImages.length > 1 && (
                  <>
                    <button 
                      className="nav-btn prev" 
                      onClick={() => setCurrentImageIndex(i => i === 0 ? detailImages.length - 1 : i - 1)}
                    >‹</button>
                    <button 
                      className="nav-btn next" 
                      onClick={() => setCurrentImageIndex(i => i === detailImages.length - 1 ? 0 : i + 1)}
                    >›</button>
                  </>
                )}
              </div>
              {detailImages.length > 1 && (
                <div className="gallery-thumbnails-row">
                  {detailImages.map((image, index) => (
                    <button
                      key={index}
                      className={`thumb-btn ${currentImageIndex === index ? "active" : ""}`}
                      onClick={() => setCurrentImageIndex(index)}
                    >
                      <img src={image} alt={`Thumbnail ${index}`} />
                    </button>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="detail-gallery-section placeholder">
              <div className="no-image-placeholder">Rasm mavjud emas</div>
            </div>
          )}

          <div className="detail-info-section">
            <div className="detail-header-desktop">
              <h1>{client.name}</h1>
              <div className="badges-row">
                <span className="badge-code">Code: {client.client_code_1c}</span>
                <span className={`badge-status ${client.is_active ? "active" : "inactive"}`}>
                  {client.is_active ? "Active" : "Inactive"}
                </span>
                {client.business_region_name && (
                  <span className="badge-region">📍 {client.business_region_name}</span>
                )}
              </div>
            </div>

            <div className="info-group contact-info">
              {client.email && (
                <div className="contact-item">
                  <strong>Email:</strong> {client.email}
                </div>
              )}
              {client.phone && (
                <div className="contact-item">
                  <strong>Telefon:</strong> {client.phone}
                </div>
              )}
            </div>

            {client.description && (
              <div className="info-group">
                <h3>Tavsif</h3>
                <div
                  className="description-text"
                  dangerouslySetInnerHTML={{ __html: client.description }}
                />
              </div>
            )}
          </div>
      </div>
    </div>
  );
};

export default ClientDetail;
