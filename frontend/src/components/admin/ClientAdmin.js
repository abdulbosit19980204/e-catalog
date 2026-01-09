import React, { useEffect, useState, useCallback } from "react";
import QuillEditor from "./QuillEditor";
import { clientAPI } from "../../api";
import { useNotification } from "../../contexts/NotificationContext";
import "./AdminCRUD.css";

const ClientAdmin = () => {
  const { success, error: showError } = useNotification();
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [showModal, setShowModal] = useState(false);
  const [showImageModal, setShowImageModal] = useState(false);
  const [selectedClient, setSelectedClient] = useState(null);
  const [selectedImages, setSelectedImages] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [editingClient, setEditingClient] = useState(null);
  const [descriptionStatus, setDescriptionStatus] = useState("");
  const [imageStatus, setImageStatus] = useState("");
  const [createdFrom, setCreatedFrom] = useState("");
  const [createdTo, setCreatedTo] = useState("");
  const [updatedFrom, setUpdatedFrom] = useState("");
  const [updatedTo, setUpdatedTo] = useState("");
  const [formData, setFormData] = useState({
    client_code_1c: "",
    name: "",
    email: "",
    phone: "",
    description: "",
    is_active: true,
  });
  const [imageMeta, setImageMeta] = useState({
    category: "",
    note: "",
  });

  const loadClients = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {
        page,
        page_size: pageSize,
        search: search || undefined,
        description_status: descriptionStatus || undefined,
        image_status: imageStatus || undefined,
        created_from: createdFrom || undefined,
        created_to: createdTo || undefined,
        updated_from: updatedFrom || undefined,
        updated_to: updatedTo || undefined,
      };
      const response = await clientAPI.getClients(params);
      setClients(response.data.results || response.data);
      if (response.data.count !== undefined) {
        setTotalCount(response.data.count);
        setTotalPages(Math.ceil(response.data.count / pageSize));
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      setError(errorMsg);
      showError(errorMsg);
      console.error("Error loading clients:", err);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, search, descriptionStatus, imageStatus, createdFrom, createdTo, updatedFrom, updatedTo, showError]);

  useEffect(() => {
    loadClients();
  }, [loadClients]);

  const handleCreate = () => {
    setEditingClient(null);
    setFormData({
      client_code_1c: "",
      name: "",
      email: "",
      phone: "",
      description: "",
      is_active: true,
    });
    setShowModal(true);
  };

  const handleEdit = (client) => {
    setEditingClient(client);
    setFormData({
      client_code_1c: client.client_code_1c,
      name: client.name,
      email: client.email || "",
      phone: client.phone || "",
      description: client.description || "",
      is_active: client.is_active !== undefined ? client.is_active : true,
    });
    setShowModal(true);
  };

  const handleDelete = async (clientCode1c) => {
    if (!window.confirm("Bu client'ni o'chirishni xohlaysizmi?")) {
      return;
    }

    try {
      await clientAPI.deleteClient(clientCode1c);
      loadClients();
      success("Client muvaffaqiyatli o'chirildi");
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      setError(errorMsg);
      showError(errorMsg);
      console.error("Error deleting client:", err);
    }
  };

  const handleToggleActive = async (client) => {
    try {
      await clientAPI.updateClient(client.client_code_1c, {
        is_active: !client.is_active,
      });
      loadClients();
      success(`Client ${!client.is_active ? 'faollashtirildi' : 'deaktivlashtirildi'}`);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      setError(errorMsg);
      showError(errorMsg);
      console.error("Error toggling active status:", err);
    }
  };

  const handleToggleDeleted = async (client) => {
    try {
      await clientAPI.updateClient(client.client_code_1c, {
        is_deleted: !client.is_deleted,
      });
      loadClients();
      success(`Client ${!client.is_deleted ? 'o\'chirildi' : 'qayta tiklandi'}`);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      setError(errorMsg);
      showError(errorMsg);
      console.error("Error toggling deleted status:", err);
    }
  };

  const handleUploadImages = (client) => {
    setSelectedClient(client);
    setSelectedImages([]);
    setImageMeta({ category: "", note: "" });
    setError(null);
    setShowImageModal(true);
  };

  const handleImageSelect = (e) => {
    const files = Array.from(e.target.files);
    setSelectedImages(files);
  };

  const handleBulkUpload = async () => {
    if (!selectedClient || selectedImages.length === 0) {
      setError("Iltimos, kamida bitta rasm tanlang");
      return;
    }

    try {
      setUploading(true);
      setError(null);
      await clientAPI.bulkUploadImages(selectedClient.client_code_1c, selectedImages, imageMeta);
      setShowImageModal(false);
      setSelectedImages([]);
      setSelectedClient(null);
      setImageMeta({ category: "", note: "" });
      loadClients();
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
      if (editingClient) {
        await clientAPI.updateClient(editingClient.client_code_1c, formData);
        success("Client muvaffaqiyatli yangilandi");
      } else {
        await clientAPI.createClient(formData);
        success("Client muvaffaqiyatli yaratildi");
      }
      setShowModal(false);
      loadClients();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      setError(errorMsg);
      showError(errorMsg);
      console.error("Error saving client:", err);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    loadClients();
  };

  const handleResetFilters = () => {
    setSearch("");
    setDescriptionStatus("");
    setImageStatus("");
    setCreatedFrom("");
    setCreatedTo("");
    setUpdatedFrom("");
    setUpdatedTo("");
    setPage(1);
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
        <h2>👥 Clients</h2>
        <button onClick={handleCreate} className="btn-primary">
          <span>+</span> Yangi Client
        </button>
      </div>

      <form onSubmit={handleSearch} className="search-form">
        <div className="search-row">
          <input
            type="text"
            placeholder="Qidirish..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="btn-primary">
            🔍 Qidirish
          </button>
          <button type="button" className="btn-tertiary" onClick={handleResetFilters}>
            🔄 Tozalash
          </button>
        </div>
        <div className="filter-row">
          <div className="filter-field">
            <label>Description holati</label>
            <select
              value={descriptionStatus}
              onChange={(e) => setDescriptionStatus(e.target.value)}
            >
              <option value="">Hammasi</option>
              <option value="with">Description bor</option>
              <option value="without">Description yo'q</option>
            </select>
          </div>
          <div className="filter-field">
            <label>Rasm holati</label>
            <select
              value={imageStatus}
              onChange={(e) => setImageStatus(e.target.value)}
            >
              <option value="">Hammasi</option>
              <option value="with">Rasm bor</option>
              <option value="without">Rasm yo'q</option>
            </select>
          </div>
          <div className="filter-field">
            <label>Yaratilgan (dan)</label>
            <input
              type="date"
              value={createdFrom}
              onChange={(e) => setCreatedFrom(e.target.value)}
            />
          </div>
          <div className="filter-field">
            <label>Yaratilgan (gacha)</label>
            <input
              type="date"
              value={createdTo}
              onChange={(e) => setCreatedTo(e.target.value)}
            />
          </div>
          <div className="filter-field">
            <label>Yangilangan (dan)</label>
            <input
              type="date"
              value={updatedFrom}
              onChange={(e) => setUpdatedFrom(e.target.value)}
            />
          </div>
          <div className="filter-field">
            <label>Yangilangan (gacha)</label>
            <input
              type="date"
              value={updatedTo}
              onChange={(e) => setUpdatedTo(e.target.value)}
            />
          </div>
        </div>
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
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Code 1C</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {clients.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="no-data">
                      Ma'lumot topilmadi
                    </td>
                  </tr>
                ) : (
                  clients.map((client) => (
                    <tr key={client.id}>
                      <td>{client.client_code_1c}</td>
                      <td>{client.name}</td>
                      <td>{client.email || "-"}</td>
                      <td>{client.phone || "-"}</td>
                      <td>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                          <span 
                            className={`status-badge ${client.is_active ? 'active' : 'inactive'}`}
                            onClick={() => handleToggleActive(client)}
                            style={{ cursor: 'pointer' }}
                          >
                            {client.is_active ? "● Faol" : "○ Faol emas"}
                          </span>
                          {client.is_deleted && (
                            <span className="status-badge" style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444' }}>
                              🗑️ O'chirilgan
                            </span>
                          )}
                        </div>
                      </td>
                      <td>
                        <div className="action-buttons">
                          <button
                            onClick={() => handleEdit(client)}
                            className="btn-edit"
                            title="Tahrirlash"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => handleUploadImages(client)}
                            className="btn-upload"
                            title="Rasmlar yuklash"
                          >
                            📸
                          </button>
                          <button
                            onClick={() => handleDelete(client.client_code_1c)}
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

          {totalPages > 1 && (
            <div className="pagination">
              <div className="pagination-controls">
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
              </div>
              <div className="pagination-controls">
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
            </div>
          )}
        </>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingClient ? "Client Tahrirlash" : "Yangi Client"}</h3>
              <button
                className="modal-close"
                onClick={() => setShowModal(false)}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleSubmit} className="modal-form">
              <div className="form-group">
                <label>Client Code 1C *</label>
                <input
                  type="text"
                  value={formData.client_code_1c}
                  onChange={(e) =>
                    setFormData({ ...formData, client_code_1c: e.target.value })
                  }
                  required
                  className="form-input"
                  disabled={!!editingClient}
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
                <label>Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input
                  type="text"
                  value={formData.phone}
                  onChange={(e) =>
                    setFormData({ ...formData, phone: e.target.value })
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
              <h3>Rasmlar Yuklash - {selectedClient?.name}</h3>
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
              <div className="meta-grid">
                <div className="form-group">
                  <label>Toifa (ixtiyoriy)</label>
                  <input
                    type="text"
                    value={imageMeta.category}
                    onChange={(e) =>
                      setImageMeta((prev) => ({ ...prev, category: e.target.value }))
                    }
                    className="form-input"
                    placeholder="Masalan: vitrina, hisobot"
                    disabled={uploading}
                  />
                </div>
                <div className="form-group">
                  <label>Izoh (ixtiyoriy)</label>
                  <textarea
                    value={imageMeta.note}
                    onChange={(e) =>
                      setImageMeta((prev) => ({ ...prev, note: e.target.value }))
                    }
                    className="form-textarea"
                    rows={3}
                    placeholder="Qo'shimcha ma'lumot..."
                    disabled={uploading}
                  />
                </div>
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

export default ClientAdmin;
