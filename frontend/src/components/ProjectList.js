import React, { useEffect, useState } from "react";
import { projectAPI } from "../api";
import "./ProjectList.css";

const ProjectList = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [createdFrom, setCreatedFrom] = useState("");
  const [createdTo, setCreatedTo] = useState("");

  useEffect(() => {
    loadProjects();
  }, [page, search, createdFrom, createdTo]);

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {
        page,
        search: search || undefined,
        created_from: createdFrom || undefined,
        created_to: createdTo || undefined,
      };
      const response = await projectAPI.getProjects(params);
      setProjects(response.data.results || response.data);
      if (response.data.count) {
        setTotalPages(Math.ceil(response.data.count / 20));
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Xatolik yuz berdi");
      console.error("Error loading projects:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    loadProjects();
  };

  return (
    <div className="project-list-container">
      <div className="project-list-header">
        <h1>Projects</h1>
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
          <div className="projects-grid">
            {projects.length === 0 ? (
              <div className="no-projects">
                <p>Projects topilmadi</p>
              </div>
            ) : (
              projects.map((project) => (
                <div key={project.id} className="project-card">
                  <div className="project-image">
                    {project.images && project.images.length > 0 ? (
                      <img
                        src={project.images[0].image_url || project.images[0].image}
                        alt={project.name}
                      />
                    ) : (
                      <div className="no-image">Rasm yo'q</div>
                    )}
                  </div>
                  <div className="project-info">
                    <h3>{project.name}</h3>
                    <p className="project-code">Code: {project.code_1c}</p>
                    {project.title && <p className="project-title">{project.title}</p>}
                    {project.description && (
                      <div
                        className="project-description"
                        dangerouslySetInnerHTML={{ __html: project.description }}
                      />
                    )}
                    <div className="project-meta">
                      <span className={`status ${project.is_active ? "active" : "inactive"}`}>
                        {project.is_active ? "Active" : "Inactive"}
                      </span>
                      <span className="images-count">
                        {project.images?.length || 0} ta rasm
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

export default ProjectList;
