import React, { useEffect, useState, useCallback } from "react";
import QuillEditor from "./QuillEditor";
import { projectAPI } from "../../api";
import { useNotification } from "../../contexts/NotificationContext";
import "./AdminCRUD.css";

const ProjectAdmin = () => {
  const { success, error: showError } = useNotification();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [showModal, setShowModal] = useState(false);

  const [selectedImages, setSelectedImages] = useState([]);
  const [currentImages, setCurrentImages] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [descriptionStatus, setDescriptionStatus] = useState("");
  const [imageStatus, setImageStatus] = useState("");
  const [createdFrom, setCreatedFrom] = useState("");
  const [createdTo, setCreatedTo] = useState("");
  const [updatedFrom, setUpdatedFrom] = useState("");
  const [updatedTo, setUpdatedTo] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [formData, setFormData] = useState({
    code_1c: "",
    name: "",
    title: "",
    description: "",
    is_active: true,
  });
  const [activeTab, setActiveTab] = useState("asosiy");
  const [imageMeta, setImageMeta] = useState({
    category: "",
    note: "",
  });

  const loadProjects = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {
        page,
        page_size: pageSize,
        search: search || undefined,
        description_status: descriptionStatus || undefined,
        image_status: imageStatus || undefined,
        is_active: statusFilter || undefined,
        created_from: createdFrom || undefined,
        created_to: createdTo || undefined,
        updated_from: updatedFrom || undefined,
        updated_to: updatedTo || undefined,
      };
      const response = await projectAPI.getProjects(params);
      setProjects(response.data.results || response.data);
      if (response.data.count !== undefined) {
        setTotalCount(response.data.count);
        setTotalPages(Math.ceil(response.data.count / pageSize));
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      setError(errorMsg);
      showError(errorMsg);
      console.error("Error loading projects:", err);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, search, descriptionStatus, imageStatus, statusFilter, createdFrom, createdTo, updatedFrom, updatedTo, showError]);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  const handleCreate = () => {
    setEditingProject(null);
    setFormData({
      code_1c: "",
      name: "",
      title: "",
      description: "",
      is_active: true,
    });
    setActiveTab("asosiy");
    setShowModal(true);
  };

  const handleEdit = (project) => {
    setEditingProject(project);
    setFormData({
      code_1c: project.code_1c || "",
      name: project.name || "",
      title: project.title || "",
      description: project.description || "",
      is_active: project.is_active !== undefined ? project.is_active : true,
    });
    setActiveTab("asosiy");
    setShowModal(true);
  };

  const handleDelete = async (code1c) => {
    if (!window.confirm("Bu project'ni o'chirishni xohlaysizmi?")) {
      return;
    }

    try {
      await projectAPI.deleteProject(code1c);
      loadProjects();
      success("Project muvaffaqiyatli o'chirildi");
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      setError(errorMsg);
      showError(errorMsg);
      console.error("Error deleting project:", err);
    }
  };

  const handleToggleActive = async (project) => {
    try {
      await projectAPI.updateProject(project.code_1c, {
        is_active: !project.is_active,
      });
      loadProjects();
      success(`Project ${!project.is_active ? 'faollashtirildi' : 'deaktivlashtirildi'}`);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      setError(errorMsg);
      showError(errorMsg);
      console.error("Error toggling active status:", err);
    }
  };


  const loadProjectImages = async (code1c) => {
    try {
      const response = await projectAPI.getProjectImages(code1c);
      const data = response.data;
      if (Array.isArray(data)) {
        setCurrentImages(data);
      } else if (data && Array.isArray(data.results)) {
        setCurrentImages(data.results);
      } else {
        setCurrentImages([]);
      }
    } catch (err) {
      console.error("Error loading images:", err);
      setCurrentImages([]);
    }
  };

  const handleDeleteImage = async (imageId) => {
    if (!window.confirm("Bu rasmni o'chirishni xohlaysizmi?")) return;
    try {
      await projectAPI.deleteImage(imageId);
      if (editingProject) loadProjectImages(editingProject.code_1c);
      success("Rasm o'chirildi");
    } catch (err) {
      showError("Rasmni o'chirib bo'lmadi");
    }
  };

  const handleSetMainImage = async (imageId) => {
    try {
      await projectAPI.setMainImage(imageId);
      if (editingProject) loadProjectImages(editingProject.code_1c);
      success("Rasm asosiy qilib belgilandi");
    } catch (err) {
      showError("Rasmni asosiy qilib bo'lmadi");
    }
  };

  const handleUploadImages = (project) => {
    setEditingProject(project);
    setFormData({
      code_1c: project.code_1c || "",
      name: project.name || "",
      title: project.title || "",
      description: project.description || "",
      is_active: project.is_active !== undefined ? project.is_active : true,
    });
    setActiveTab("rasmlar");
    setSelectedImages([]);
    setImageMeta({ category: "", note: "" });
    setError(null);
    setCurrentImages([]);
    loadProjectImages(project.code_1c);
    setShowModal(true);
  };

  const handleImageSelect = (e) => {
    const files = Array.from(e.target.files);
    setSelectedImages(files);
  };

  const handleBulkUpload = async () => {
    if (!editingProject || selectedImages.length === 0) {
      setError("Iltimos, kamida bitta rasm tanlang");
      return;
    }

    try {
      setUploading(true);
      setError(null);
      await projectAPI.bulkUploadImages(editingProject.code_1c, selectedImages, imageMeta);
      setSelectedImages([]);
      setImageMeta({ category: "", note: "" });
      loadProjects();
      loadProjectImages(editingProject.code_1c);
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

  // Helper to clean data before sending to API
  const prepareDataForSubmit = (data) => {
    const cleaned = { ...data };
    
    // Convert empty strings to null if needed (for Projects mostly text, but good practice)
    // If title or description are optional and can be null? 
    // Usually DRF handles blank string for text fields fine.
    
    return cleaned;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const dataToSend = prepareDataForSubmit(formData);
      if (editingProject) {
        await projectAPI.updateProject(editingProject.code_1c, dataToSend);
        success("Project muvaffaqiyatli yangilandi");
      } else {
        await projectAPI.createProject(dataToSend);
        success("Project muvaffaqiyatli yaratildi");
      }
      setShowModal(false);
      loadProjects();
    } catch (err) {
      let errorMsg = "Xatolik yuz berdi";
      const data = err.response?.data;
      if (data) {
        if (data.detail) {
          errorMsg = data.detail;
        } else if (typeof data === 'object') {
          errorMsg = Object.entries(data)
            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(", ") : value}`)
            .join("\n");
        }
      }
      showError(errorMsg);
      console.error("Error saving project:", err);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    loadProjects();
  };

  const handleResetFilters = () => {
    setSearch("");
    setDescriptionStatus("");
    setImageStatus("");
    setStatusFilter("");
    setCreatedFrom("");
    setCreatedTo("");
    setUpdatedFrom("");
    setUpdatedTo("");
    setPage(1);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case "asosiy":
        return (
          <div className="form-grid">
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
                  disabled={!!editingProject}
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
            <div className="form-group full-width">
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
            <div className="form-group full-width">
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
                  Faol
                </label>
            </div>
          </div>
        );
      case "rasmlar":
        return (
            <div className="image-management-tab">
                {!editingProject ? (
                    <p>Rasmlar uchun avval saqlang.</p>
                ) : (
                    <>
                        <div className="image-upload-section">
                            <div className="form-group">
                                <label>Rasmlarni tanlang</label>
                                <input
                                    type="file"
                                    multiple
                                    accept="image/*"
                                    onChange={handleImageSelect}
                                    className="form-input"
                                    disabled={uploading}
                                />
                                {selectedImages.length > 0 && <p className="image-count">{selectedImages.length} ta rasm tanlandi</p>}
                            </div>
                            <div className="form-group">
                                <label>Toifa (ixtiyoriy)</label>
                                <input
                                    type="text"
                                    value={imageMeta.category}
                                    onChange={(e) => setImageMeta({ ...imageMeta, category: e.target.value })}
                                    className="form-input"
                                    placeholder="Masalan: banner"
                                />
                            </div>
                             <button
                                type="button"
                                onClick={handleBulkUpload}
                                className="btn-primary"
                                disabled={uploading || selectedImages.length === 0}
                                style={{ marginTop: '10px' }}
                            >
                                {uploading ? "Yuklanmoqda..." : `Yuklash (${selectedImages.length})`}
                            </button>
                        </div>

                        <div className="current-images-section" style={{ marginTop: '30px' }}>
                            <h4>Hozirgi rasmlar</h4>
                            {currentImages.length === 0 ? <p className="no-data">Rasmlar yo'q</p> : (
                                <div className="image-management-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: '10px' }}>
                                    {currentImages.map(img => (
                                        <div key={img.id} className="image-item" style={{ position: 'relative', border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden', background: '#fff' }}>
                                            <div style={{ height: '120px', overflow: 'hidden' }}>
                                                <img src={img.image_thumbnail_url || img.image} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                            </div>
                                            {img.is_main && <span className="main-badge" style={{ position: 'absolute', top: 5, right: 5, background: '#10b981', color: 'white', padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: 'bold' }}>ASOSIY</span>}
                                            <div className="image-item-actions" style={{ padding: '8px', display: 'flex', gap: '8px', justifyContent: 'center', background: '#f8fafc', borderTop: '1px solid #e2e8f0' }}>
                                                {!img.is_main && (
                                                    <button 
                                                        type="button" 
                                                        onClick={() => handleSetMainImage(img.id)} 
                                                        style={{ border: '1px solid #fbbf24', background: '#fff', color: '#fbbf24', borderRadius: '6px', width: '30px', height: '30px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }} 
                                                        title="Asosiy qilish"
                                                    >
                                                        ⭐
                                                    </button>
                                                )}
                                                <button 
                                                    type="button" 
                                                    onClick={() => handleDeleteImage(img.id)} 
                                                    style={{ border: '1px solid #ef4444', background: '#fff', color: '#ef4444', borderRadius: '6px', width: '30px', height: '30px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }} 
                                                    title="O'chirish"
                                                >
                                                    ×
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </>
                )}
            </div>
        );
      default:
        return null;
    }
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage);
    }
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

  const renderPagination = () => {
    if (totalPages <= 1) return null;
    return (
      <div className="pagination" style={{ marginTop: 0, marginBottom: 20 }}>
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
          <span className="page-info">Jami: {totalCount}</span>
          <select
            value={pageSize}
            onChange={(e) => {
              setPageSize(parseInt(e.target.value));
              setPage(1);
            }}
            className="page-size-select"
          >
            {[10, 20, 50, 100].map((sz) => (
              <option key={sz} value={sz}>
                {sz}
              </option>
            ))}
          </select>
        </div>
      </div>
    );
  };

  return (
    <div className="admin-crud">
      <div className="crud-header">
        <h2>📁 Projects</h2>
        <button onClick={handleCreate} className="btn-primary">
          <span>+</span> Yangi Project
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
            <label>Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">Hammasi</option>
              <option value="true">Faol</option>
              <option value="false">Faol emas</option>
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
          {renderPagination()}
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
                {projects.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="no-data">
                      Ma'lumot topilmadi
                    </td>
                  </tr>
                ) : (
                  projects.map((project) => (
                    <tr key={project.id}>
                      <td>{project.code_1c}</td>
                      <td>{project.name}</td>
                      <td>{project.title || "-"}</td>
                      <td>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                          <span 
                            className={`status-badge ${project.is_active ? 'active' : 'inactive'}`}
                            onClick={() => handleToggleActive(project)}
                            style={{ cursor: 'pointer' }}
                          >
                            {project.is_active ? "● Faol" : "○ Faol emas"}
                          </span>
                          {project.is_deleted && (
                            <span className="status-badge" style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444' }}>
                              🗑️ O'chirilgan
                            </span>
                          )}
                        </div>
                      </td>
                      <td>
                        <div className="action-buttons">
                          <button
                            onClick={() => handleEdit(project)}
                            className="btn-edit"
                            title="Tahrirlash"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => handleUploadImages(project)}
                            className="btn-upload"
                            title="Rasmlar yuklash"
                          >
                            📸
                          </button>
                          <button
                            onClick={() => handleDelete(project.code_1c)}
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

          {renderPagination()}
        </>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingProject ? "Project Tahrirlash" : "Yangi Project"}</h3>
               <div className="admin-tabs" style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                <button
                    type="button"
                    className={`tab-btn ${activeTab === "asosiy" ? "active" : ""}`}
                    onClick={() => setActiveTab("asosiy")}
                    style={{ 
                        padding: '8px 16px', 
                        border: 'none', 
                        background: activeTab === "asosiy" ? '#3b82f6' : '#e2e8f0', 
                        color: activeTab === "asosiy" ? 'white' : '#64748b',
                        borderRadius: '6px',
                        cursor: 'pointer'
                    }}
                >
                    Asosiy
                </button>
                <button
                    type="button"
                    className={`tab-btn ${activeTab === "rasmlar" ? "active" : ""}`}
                    onClick={() => setActiveTab("rasmlar")}
                    style={{ 
                        padding: '8px 16px', 
                        border: 'none', 
                        background: activeTab === "rasmlar" ? '#3b82f6' : '#e2e8f0', 
                        color: activeTab === "rasmlar" ? 'white' : '#64748b',
                        borderRadius: '6px',
                        cursor: 'pointer'
                    }}
                >
                    Rasmlar
                </button>
              </div>
              <button
                className="modal-close"
                onClick={() => setShowModal(false)}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleSubmit} className="modal-form">
               {renderTabContent()}

               {activeTab === "asosiy" && (
                <>
                 {error && <div className="error-message"><p>{error}</p></div>}
                 <div className="modal-actions">
                    <button type="button" onClick={() => setShowModal(false)} className="btn-secondary">
                        Bekor qilish
                    </button>
                    <button type="submit" className="btn-primary">
                        Saqlash
                    </button>
                 </div>
                </>
               )}
                {activeTab === "rasmlar" && (
                    <div className="modal-actions">
                         <button type="button" onClick={() => setShowModal(false)} className="btn-secondary">
                            Yopish
                         </button>
                    </div>
                )}
            </form>
          </div>
        </div>
      )}


    </div>
  );
};

export default ProjectAdmin;
