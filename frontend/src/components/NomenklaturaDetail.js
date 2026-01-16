import React, { useEffect, useState, useMemo } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { nomenklaturaAPI } from "../api";
import "./NomenklaturaDetail.css";

const NomenklaturaDetail = () => {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const projectId = searchParams.get('project_id');
  const navigate = useNavigate();
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    const loadItem = async () => {
      try {
        setLoading(true);
        const response = await nomenklaturaAPI.getNomenklaturaItem(id, projectId);
        setItem(response.data);
      } catch (err) {
        setError("Ma'lumot topilmadi");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadItem();
  }, [id, projectId]);

  const detailImages = useMemo(() => {
    if (!item?.images?.length) return [];
    return item.images.map((image) =>
      image.image_lg_url || image.image_md_url || image.image_url || image.image
    );
  }, [item]);

  const handlePrevImage = () => {
    setCurrentImageIndex((prev) => (prev === 0 ? detailImages.length - 1 : prev - 1));
  };

  const handleNextImage = () => {
    setCurrentImageIndex((prev) => (prev === detailImages.length - 1 ? 0 : prev + 1));
  };

  if (loading) return (
    <div className="detail-page-loading">
      <div className="spinner"></div>
      <p>Yuklanmoqda...</p>
    </div>
  );

  if (error || !item) return (
    <div className="detail-page-error">
      <h2>{error || "Mahsulot topilmadi"}</h2>
      <button onClick={() => navigate("/nomenklatura")} className="btn-secondary">
        Ortga qaytish
      </button>
    </div>
  );

  return (
    <div className="detail-page-container">
        <button className="back-button" onClick={() => navigate("/nomenklatura")}>
          ← Katalogga qaytish
        </button>
        
        <div className="detail-main-card">
          <div className="detail-header-mobile">
            <h1>{item.name}</h1>
            <div className="mobile-codes">
              <span className="code">Kodi: {item.code_1c}</span>
              {item.article_code && <span className="article">Artikul: {item.article_code}</span>}
            </div>
          </div>

          <div className="detail-gallery-section">
            <div className="gallery-main-view">
              {detailImages.length ? (
                <img
                  src={detailImages[currentImageIndex]}
                  alt={`${item.name} ${currentImageIndex + 1}`}
                  className="main-image"
                />
              ) : (
                <div className="no-image-placeholder">Rasm mavjud emas</div>
              )}
              {detailImages.length > 1 && (
                <>
                  <button className="nav-btn prev" onClick={handlePrevImage}>‹</button>
                  <button className="nav-btn next" onClick={handleNextImage}>›</button>
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

          <div className="detail-info-section">
            <div className="detail-header-desktop">
              <h1>{item.name}</h1>
              <div className="badges-row">
                <span className="badge-code">Kodi: {item.code_1c}</span>
                {item.article_code && <span className="badge-article">Artikul: {item.article_code}</span>}
                <span className={`badge-status ${item.is_active ? "active" : "inactive"}`}>
                  {item.is_active ? "Sotuvda" : "Arxiv"}
                </span>
              </div>
            </div>

            {item.title && (
              <div className="info-group">
                <h3>Qisqa nomi</h3>
                <p className="detail-title-text">{item.title}</p>
              </div>
            )}

            <div className="info-group">
              <h3>Xususiyatlar</h3>
              <div className="specifications-grid">
                {item.article_code && (
                  <div className="spec-item">
                    <span className="spec-label">Artikul:</span>
                    <span className="spec-value highlight">{item.article_code}</span>
                  </div>
                )}
                {item.brand && (
                  <div className="spec-item">
                    <span className="spec-label">Brend:</span>
                    <span className="spec-value">{item.brand}</span>
                  </div>
                )}
                {item.roditel && (
                  <div className="spec-item">
                    <span className="spec-label">Guruh:</span>
                    <span className="spec-value">{item.roditel}</span>
                  </div>
                )}
                {item.category && (
                  <div className="spec-item">
                    <span className="spec-label">Kategoriya:</span>
                    <span className="spec-value">{item.category}</span>
                  </div>
                )}
                {item.unit_of_measure && (
                  <div className="spec-item">
                    <span className="spec-label">O'lchov birligi:</span>
                    <span className="spec-value">{item.unit_of_measure}</span>
                  </div>
                )}
                {item.supplier && (
                  <div className="spec-item">
                    <span className="spec-label">Yetkazib beruvchi:</span>
                    <span className="spec-value">{item.supplier}</span>
                  </div>
                )}
                {item.country && (
                  <div className="spec-item">
                    <span className="spec-label">Ishlab chiqarilgan davlat:</span>
                    <span className="spec-value">{item.country}</span>
                  </div>
                )}
                {item.barcode && (
                  <div className="spec-item">
                    <span className="spec-label">Barkod:</span>
                    <span className="spec-value">{item.barcode}</span>
                  </div>
                )}
                {item.series && (
                  <div className="spec-item">
                    <span className="spec-label">Seriya:</span>
                    <span className="spec-value">{item.series}</span>
                  </div>
                )}
              </div>
            </div>

            {item.projects && item.projects.length > 0 && (
              <div className="info-group">
                <h3>Bog'langan loyihalar</h3>
                <div className="project-tags">
                  {item.projects.map((proj) => (
                    <span key={proj.id} className="project-tag">
                      {proj.name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {item.description && (
              <div className="info-group">
                <h3>Tavsif</h3>
                <div
                  className="description-text"
                  dangerouslySetInnerHTML={{ __html: item.description }}
                />
              </div>
            )}
          </div>
      </div>
    </div>
  );
};

export default NomenklaturaDetail;
