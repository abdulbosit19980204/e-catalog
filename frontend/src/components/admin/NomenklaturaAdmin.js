import React, { useEffect, useState, useCallback } from "react";
import QuillEditor from "./QuillEditor";
import { nomenklaturaAPI } from "../../api";
import { useNotification } from "../../contexts/NotificationContext";
import "./AdminCRUD.css";

const NomenklaturaAdmin = () => {
  const { success, error: showError } = useNotification();
  const [nomenklatura, setNomenklatura] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [showModal, setShowModal] = useState(false);
  const [showImageModal, setShowImageModal] = useState(false);
  const [selectedNomenklatura, setSelectedNomenklatura] = useState(null);
  const [selectedImages, setSelectedImages] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [editingNomenklatura, setEditingNomenklatura] = useState(null);
  const [formData, setFormData] = useState({
    code_1c: "",
    name: "",
    title: "",
    description: "",
    is_active: true,
  });

  const loadNomenklatura = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {
        page,
        page_size: pageSize,
        search: search || undefined,
      };
      const response = await nomenklaturaAPI.getNomenklatura(params);
      setNomenklatura(response.data.results || response.data);
      if (response.data.count !== undefined) {
        setTotalCount(response.data.count);
        setTotalPages(Math.ceil(response.data.count / pageSize));
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      setError(errorMsg);
      showError(errorMsg);
      console.error("Error loading nomenklatura:", err);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, search]);

  useEffect(() => {
    loadNomenklatura();
  }, [loadNomenklatura]);

  const handleCreate = () => {
    setEditingNomenklatura(null);
    setFormData({
      code_1c: "",
      name: "",
      title: "",
      description: "",
      is_active: true,
    });
    setShowModal(true);
  };

  const handleEdit = (item) => {
    setEditingNomenklatura(item);
    setFormData({
      code_1c: item.code_1c,
      name: item.name,
      title: item.title || "",
      description: item.description || "",
      is_active: item.is_active !== undefined ? item.is_active : true,
    });
    setShowModal(true);
  };

  const handleDelete = async (code1c) => {
    if (!window.confirm("Bu nomenklatura'ni o'chirishni xohlaysizmi?")) {
      return;
    }

    try {
      await nomenklaturaAPI.deleteNomenklatura(code1c);
      loadNomenklatura();
      success("Nomenklatura muvaffaqiyatli o'chirildi");
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      setError(errorMsg);
      showError(errorMsg);
      console.error("Error deleting nomenklatura:", err);
    }
  };

  const handleToggleActive = async (item) => {
    try {
      await nomenklaturaAPI.updateNomenklatura(item.code_1c, {
        is_active: !item.is_active,
      });
      loadNomenklatura();
      success(`Nomenklatura ${!item.is_active ? 'faollashtirildi' : 'deaktivlashtirildi'}`);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      setError(errorMsg);
      showError(errorMsg);
      console.error("Error toggling active status:", err);
    }
  };

  const handleToggleDeleted = async (item) => {
    try {
      await nomenklaturaAPI.updateNomenklatura(item.code_1c, {
        is_deleted: !item.is_deleted,
      });
      loadNomenklatura();
      success(`Nomenklatura ${!item.is_deleted ? 'o\'chirildi' : 'qayta tiklandi'}`);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      setError(errorMsg);
      showError(errorMsg);
      console.error("Error toggling deleted status:", err);
    }
  };

  const handleUploadImages = (item) => {
    setSelectedNomenklatura(item);
    setSelectedImages([]);
    setShowImageModal(true);
  };

  const handleImageSelect = (e) => {
    const files = Array.from(e.target.files);
    setSelectedImages(files);
  };

  const handleBulkUpload = async () => {
    if (!selectedNomenklatura || selectedImages.length === 0) {
      setError("Iltimos, kamida bitta rasm tanlang");
      return;
    }

    try {
      setUploading(true);
      setError(null);
      await nomenklaturaAPI.bulkUploadImages(selectedNomenklatura.code_1c, selectedImages);
      setShowImageModal(false);
      setSelectedImages([]);
      setSelectedNomenklatura(null);
      loadNomenklatura();
      success(`${selectedImages.length} ta rasm muvaffaqiyatli yuklandi!`);
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.response?.data?.detail || "Rasmlar yuklashda xatolik";
      setError(errorMsg);
      showError(errorMsg);
      console.error("Error uploading images:", err);
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingNomenklatura) {
        await nomenklaturaAPI.updateNomenklatura(editingNomenklatura.code_1c, formData);
        success("Nomenklatura muvaffaqiyatli yangilandi");
      } else {
        await nomenklaturaAPI.createNomenklatura(formData);
        success("Nomenklatura muvaffaqiyatli yaratildi");
      }
      setShowModal(false);
      loadNomenklatura();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      setError(errorMsg);
      showError(errorMsg);
      console.error("Error saving nomenklatura:", err);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    loadNomenklatura();
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage);
    }
  };

  const handlePageSizeChange = (e) => {
    const newSize = parseInt(e.target.value);
    setPageSize(newSize);
    setPage(1);
  };

  const quillModules = {
    toolbar: [
      [{ header: [1, 2, 3, false] }],
      ["bold", "italic", "underline", "strike"],
      [{ list: "ordered" }, { list: "bullet" }],
      [{ align: [] }],
      ["link", "image"],
      ["clean"],
    ],
  };

  return (
    <div className="admin-crud">
      <div className="crud-header">
        <h2>Nomenklatura Boshqaruvi</h2>
        <button onClick={handleCreate} className="btn-primary">
          + Yangi Nomenklatura
        </button>
      </div>

      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          placeholder="Qidirish..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="search-input"
        />
        <button type="submit" className="btn-secondary">
          Qidirish
        </button>
      </form>

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>Yuklanmoqda...</p>
        </div>
      ) : (
        <>
          {totalPages > 1 && (
            <div className="pagination">
              <button
                onClick={() => handlePageChange(page - 1)}
                disabled={page === 1}
                className="page-button"
              >
                Oldingi
              </button>
              <div className="page-numbers">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (page <= 3) {
                    pageNum = i + 1;
                  } else if (page >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = page - 2 + i;
                  }
                  return (
                    <button
                      key={pageNum}
                      onClick={() => handlePageChange(pageNum)}
                      className={`page-number ${page === pageNum ? "active" : ""}`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>
              <button
                onClick={() => handlePageChange(page + 1)}
                disabled={page === totalPages}
                className="page-button"
              >
                Keyingi
              </button>
              <span className="page-info">
                Sahifa {page} / {totalPages} (Jami: {totalCount})
              </span>
              <select
                value={pageSize}
                onChange={handlePageSizeChange}
                className="page-size-select"
              >
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>
          )}

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Code 1C</th>
                  <th>Name</th>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {nomenklatura.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="no-data">
                      Ma'lumot topilmadi
                    </td>
                  </tr>
                ) : (
                  nomenklatura.map((item) => (
                    <tr key={item.id}>
                      <td>{item.code_1c}</td>
                      <td>{item.name}</td>
                      <td>{item.title || "-"}</td>
                      <td>
                        <div className="status-controls">
                          <label className="toggle-switch">
                            <input
                              type="checkbox"
                              checked={item.is_active}
                              onChange={() => handleToggleActive(item)}
                            />
                            <span className="toggle-slider"></span>
                            <span className="toggle-label">
                              {item.is_active ? "Active" : "Inactive"}
                            </span>
                          </label>
                          <label className="toggle-switch">
                            <input
                              type="checkbox"
                              checked={item.is_deleted}
                              onChange={() => handleToggleDeleted(item)}
                            />
                            <span className="toggle-slider"></span>
                            <span className="toggle-label">
                              {item.is_deleted ? "Deleted" : "Not Deleted"}
                            </span>
                          </label>
                        </div>
                      </td>
                      <td>
                        <div className="action-buttons">
                          <button
                            onClick={() => handleEdit(item)}
                            className="btn-edit"
                            title="Tahrirlash"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => handleUploadImages(item)}
                            className="btn-upload"
                            title="Rasmlar yuklash"
                          >
                            📷
                          </button>
                          <button
                            onClick={() => handleDelete(item.code_1c)}
                            className="btn-delete"
                            title="O'chirish"
                          >
                            🗑️
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingNomenklatura ? "Nomenklatura Tahrirlash" : "Yangi Nomenklatura"}</h3>
              <button
                className="modal-close"
                onClick={() => setShowModal(false)}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleSubmit} className="modal-form">
              <div className="form-group">
                <label>Code 1C *</label>
                <input
                  type="text"
                  value={formData.code_1c}
                  onChange={(e) =>
                    setFormData({ ...formData, code_1c: e.target.value })
                  }
                  required
                  className="form-input"
                  disabled={!!editingNomenklatura}
                />
              </div>
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  required
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label>Title</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) =>
                    setFormData({ ...formData, title: e.target.value })
                  }
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <QuillEditor
                  value={formData.description}
                  onChange={(value) =>
                    setFormData({ ...formData, description: value })
                  }
                  modules={quillModules}
                  className="quill-editor"
                  style={{ height: '200px' }}
                />
              </div>
              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) =>
                      setFormData({ ...formData, is_active: e.target.checked })
                    }
                  />
                  Active
                </label>
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="btn-secondary"
                >
                  Bekor qilish
                </button>
                <button type="submit" className="btn-primary">
                  Saqlash
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showImageModal && (
        <div className="modal-overlay" onClick={() => setShowImageModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Rasmlar Yuklash - {selectedNomenklatura?.name}</h3>
              <button
                className="modal-close"
                onClick={() => setShowImageModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-form">
              <div className="form-group">
                <label>Rasmlarni tanlang (bir nechta tanlash mumkin)</label>
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleImageSelect}
                  className="form-input"
                  disabled={uploading}
                />
                {selectedImages.length > 0 && (
                  <p className="image-count">
                    {selectedImages.length} ta rasm tanlandi
                  </p>
                )}
              </div>
              {error && (
                <div className="error-message">
                  <p>{error}</p>
                </div>
              )}
              <div className="modal-actions">
                <button
                  type="button"
                  onClick={() => setShowImageModal(false)}
                  className="btn-secondary"
                  disabled={uploading}
                >
                  Bekor qilish
                </button>
                <button
                  type="button"
                  onClick={handleBulkUpload}
                  className="btn-primary"
                  disabled={uploading || selectedImages.length === 0}
                >
                  {uploading ? "Yuklanmoqda..." : `Yuklash (${selectedImages.length})`}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NomenklaturaAdmin;
