import React, { useEffect, useState, useMemo } from "react";
import { nomenklaturaAPI } from "../api";
import "./NomenklaturaList.css";

const NomenklaturaList = () => {
  const [nomenklatura, setNomenklatura] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedItem, setSelectedItem] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    loadNomenklatura();
  }, [page, search]);

  useEffect(() => {
    if (showDetailModal) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }

    return () => {
      document.body.style.overflow = "";
    };
  }, [showDetailModal]);

  const loadNomenklatura = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {
        page,
        search: search || undefined,
      };
      const response = await nomenklaturaAPI.getNomenklatura(params);
      setNomenklatura(response.data.results || response.data);
      if (response.data.count) {
        setTotalPages(Math.ceil(response.data.count / 20));
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Xatolik yuz berdi");
      console.error("Error loading nomenklatura:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    loadNomenklatura();
  };

  const openDetailModal = (item) => {
    setSelectedItem(item);
    setCurrentImageIndex(0);
    setShowDetailModal(true);
  };

  const closeDetailModal = () => {
    setShowDetailModal(false);
    setSelectedItem(null);
    setCurrentImageIndex(0);
  };

  const handlePrevImage = () => {
    if (!selectedItem?.images?.length) return;
    setCurrentImageIndex((prev) =>
      prev === 0 ? selectedItem.images.length - 1 : prev - 1
    );
  };

  const handleNextImage = () => {
    if (!selectedItem?.images?.length) return;
    setCurrentImageIndex((prev) =>
      prev === selectedItem.images.length - 1 ? 0 : prev + 1
    );
  };

  const detailImages = useMemo(() => {
    if (!selectedItem?.images?.length) return [];

    return selectedItem.images.map((image) =>
      image.image_lg_url || image.image_md_url || image.image_url || image.image
    );
  }, [selectedItem]);

  const toPlainText = (value) => {
    if (!value) return "";
    if (typeof value !== "string") return String(value);
    const withoutTags = value.replace(/<[^>]+>/g, " ");
    return withoutTags.replace(/\s+/g, " ").trim();
  };

  const getPreviewImage = (item) => {
    if (!item?.images?.length) return null;

    const primary = item.images[0];
    return (
      primary.image_sm_url ||
      primary.image_md_url ||
      primary.image_url ||
      primary.image
    );
  };

  return (
    <div className="nomenklatura-list-container">
      <div className="nomenklatura-list-header">
        <div className="page-heading">
          <h1>Nomenklatura</h1>
          <p>Mahsulot katalogi, suratlar va batafsil tavsiflar bilan</p>
        </div>
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Mahsulot nomi, kodi yoki tavsifi"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
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
          <div className="nomenklatura-grid">
            {nomenklatura.length === 0 ? (
              <div className="no-nomenklatura">
                <p>Nomenklatura topilmadi</p>
              </div>
            ) : (
              nomenklatura.map((item) => {
                const previewImage = getPreviewImage(item);
                const descriptionText = toPlainText(item.description);
                const truncatedText =
                  descriptionText.length > 100
                    ? `${descriptionText.slice(0, 100).trim()}...`
                    : descriptionText;

                return (
                  <article
                    key={item.id}
                    className="nomenklatura-card"
                    onClick={() => openDetailModal(item)}
                  >
                    <div className="nomenklatura-media">
                      {previewImage ? (
                        <img src={previewImage} alt={item.name} />
                      ) : (
                        <div className="no-image">Rasm yo'q</div>
                      )}
                      <div className="card-favorite">♡</div>
                      <div className="card-badges">
                        <span className="badge original">ORIGINAL</span>
                        <span className="badge stock">{item.images?.length || 0} ta rasm</span>
                      </div>
                    </div>
                    <div className="nomenklatura-body">
                      <h3>{item.name}</h3>
                      <p className="nomenklatura-code">Code: {item.code_1c}</p>
                      {item.title && <p className="nomenklatura-title">{item.title}</p>}
                      {truncatedText && (
                        <p className="nomenklatura-description">{truncatedText}</p>
                      )}
                      <div className="nomenklatura-meta">
                        <span
                          className={`status-chip ${item.is_active ? "active" : "inactive"}`}
                        >
                          {item.is_active ? "Sotuvda" : "Arxiv"}
                        </span>
                        <span className="price-placeholder">Narx: —</span>
                      </div>
                      <div className="nomenklatura-actions">
                        <span className="view-detail">Batafsil ko'rish</span>
                      </div>
                    </div>
                  </article>
                );
              })
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

      {showDetailModal && selectedItem && (
        <div className="modal-overlay" onClick={closeDetailModal}>
          <div
            className="nomenklatura-detail-modal"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <div className="modal-title">
                <h2>{selectedItem.name}</h2>
                <p>Code: {selectedItem.code_1c}</p>
              </div>
              <button className="modal-close" onClick={closeDetailModal}>
                ×
              </button>
            </div>

            <div className="detail-content">
              <div className="detail-gallery">
                <div className="gallery-main">
                  {detailImages.length ? (
                    <img
                      src={detailImages[currentImageIndex]}
                      alt={`${selectedItem.name} ${currentImageIndex + 1}`}
                      className="main-image"
                    />
                  ) : (
                    <div className="no-detail-image">Rasm mavjud emas</div>
                  )}
                  {detailImages.length > 1 && (
                    <>
                      <button
                        className="gallery-nav prev"
                        onClick={handlePrevImage}
                        aria-label="Oldingi rasm"
                      >
                        ‹
                      </button>
                      <button
                        className="gallery-nav next"
                        onClick={handleNextImage}
                        aria-label="Keyingi rasm"
                      >
                        ›
                      </button>
                    </>
                  )}
                </div>
                {detailImages.length > 1 && (
                  <div className="gallery-thumbnails">
                    {detailImages.map((image, index) => (
                      <button
                        key={`${image}-${index}`}
                        className={`thumbnail-button ${
                          currentImageIndex === index ? "active" : ""
                        }`}
                        onClick={() => setCurrentImageIndex(index)}
                      >
                        <img src={image} alt={`${selectedItem.name} thumbnail`} />
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <div className="detail-info">
                {selectedItem.title && (
                  <div className="info-block">
                    <h3>Qisqa nomi</h3>
                    <p>{selectedItem.title}</p>
                  </div>
                )}

                <div className="info-block">
                  <h3>Holati</h3>
                  <span
                    className={`status-chip ${
                      selectedItem.is_active ? "active" : "inactive"
                    }`}
                  >
                    {selectedItem.is_active ? "Active" : "Inactive"}
                  </span>
                </div>

                {selectedItem.description && (
                  <div className="info-block">
                    <h3>Tavsif</h3>
                    <div
                      className="description-content"
                      dangerouslySetInnerHTML={{
                        __html: selectedItem.description,
                      }}
                    />
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NomenklaturaList;

