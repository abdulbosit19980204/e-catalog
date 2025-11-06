import React, { useEffect, useState } from "react";
import { nomenklaturaAPI } from "../api";
import "./NomenklaturaList.css";

const NomenklaturaList = () => {
  const [nomenklatura, setNomenklatura] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadNomenklatura();
  }, [page, search]);

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

  return (
    <div className="nomenklatura-list-container">
      <div className="nomenklatura-list-header">
        <h1>Nomenklatura</h1>
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Qidirish..."
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
              nomenklatura.map((item) => (
                <div key={item.id} className="nomenklatura-card">
                  <div className="nomenklatura-image">
                    {item.images && item.images.length > 0 ? (
                      <img
                        src={item.images[0].image_url || item.images[0].image}
                        alt={item.name}
                      />
                    ) : (
                      <div className="no-image">Rasm yo'q</div>
                    )}
                  </div>
                  <div className="nomenklatura-info">
                    <h3>{item.name}</h3>
                    <p className="nomenklatura-code">Code: {item.code_1c}</p>
                    {item.title && <p className="nomenklatura-title">{item.title}</p>}
                    {item.description && (
                      <div
                        className="nomenklatura-description"
                        dangerouslySetInnerHTML={{ __html: item.description }}
                      />
                    )}
                    <div className="nomenklatura-meta">
                      <span className={`status ${item.is_active ? "active" : "inactive"}`}>
                        {item.is_active ? "Active" : "Inactive"}
                      </span>
                      <span className="images-count">
                        {item.images?.length || 0} ta rasm
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

export default NomenklaturaList;

