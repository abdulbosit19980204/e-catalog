import React, { useEffect, useState,  useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { nomenklaturaAPI, projectAPI } from "../api";
import "./NomenklaturaList.css";

const NomenklaturaList = () => {
  const navigate = useNavigate();
  const [nomenklatura, setNomenklatura] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [createdFrom, setCreatedFrom] = useState("");
  const [createdTo, setCreatedTo] = useState("");
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState("");
  const [imageStatus, setImageStatus] = useState("");

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await projectAPI.getProjects();
        setProjects(response.data.results || response.data);
      } catch (err) {
        console.error("Failed to load projects", err);
      }
    };
    fetchProjects();
  }, []);

  const loadNomenklatura = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {
        page,
        search: search || undefined,
        created_from: createdFrom || undefined,
        created_to: createdTo || undefined,
        project_id: selectedProject || undefined,
        image_status: imageStatus || undefined,
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
  }, [page, search, createdFrom, createdTo, selectedProject, imageStatus]);

  useEffect(() => {
    loadNomenklatura();
  }, [loadNomenklatura]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    loadNomenklatura();
  };

  const handleCardClick = (item) => {
    // Navigating with project_id to avoid ambiguity
    // item.project can be an object (nested serializer) or an ID
    const projectId = item.project?.id || item.project;
    navigate(`/nomenklatura/${item.code_1c}?project_id=${projectId}`);
  };

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
          <div className="filters-row">
            <select
              value={selectedProject}
              onChange={(e) => {
                setSelectedProject(e.target.value);
                setPage(1);
              }}
              className="filter-select"
            >
              <option value="">Barcha loyihalar</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
            <select
              value={imageStatus}
              onChange={(e) => {
                setImageStatus(e.target.value);
                setPage(1);
              }}
              className="filter-select"
            >
              <option value="">Rasm holati (Barchasi)</option>
              <option value="with">Rasmli</option>
              <option value="without">Rasmsiz</option>
            </select>
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
                    onClick={() => handleCardClick(item)}
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
    </div>
  );
};

export default NomenklaturaList;

