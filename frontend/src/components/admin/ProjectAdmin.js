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
  const [showImageModal, setShowImageModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [selectedImages, setSelectedImages] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [formData, setFormData] = useState({
    code_1c: "",
    name: "",
    title: "",
    description: "",
    is_active: true,
  });

  const loadProjects = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {
        page,
        page_size: pageSize,
        search: search || undefined,
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
  }, [page, pageSize, search]);

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
    setShowModal(true);
  };

  const handleEdit = (project) => {
    setEditingProject(project);
    setFormData({
      code_1c: project.code_1c,
      name: project.name,
      title: project.title || "",
      description: project.description || "",
      is_active: project.is_active !== undefined ? project.is_active : true,
    });
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

  const handleToggleDeleted = async (project) => {
    try {
      await projectAPI.updateProject(project.code_1c, {
        is_deleted: !project.is_deleted,
      });
      loadProjects();
      success(`Project ${!project.is_deleted ? 'o\'chirildi' : 'qayta tiklandi'}`);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      setError(errorMsg);
      showError(errorMsg);
      console.error("Error toggling deleted status:", err);
    }
  };

  const handleUploadImages = (project) => {
    setSelectedProject(project);
    setSelectedImages([]);
    setShowImageModal(true);
  };

  const handleImageSelect = (e) => {
    const files = Array.from(e.target.files);
    setSelectedImages(files);
  };

  const handleBulkUpload = async () => {
    if (!selectedProject || selectedImages.length === 0) {
      setError("Iltimos, kamida bitta rasm tanlang");
      return;
    }

    try {
      setUploading(true);
      setError(null);
      await projectAPI.bulkUploadImages(selectedProject.code_1c, selectedImages);
      setShowImageModal(false);
      setSelectedImages([]);
      setSelectedProject(null);
      loadProjects();
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
      if (editingProject) {
        await projectAPI.updateProject(editingProject.code_1c, formData);
        success("Project muvaffaqiyatli yangilandi");
      } else {
        await projectAPI.createProject(formData);
        success("Project muvaffaqiyatli yaratildi");
      }
      setShowModal(false);
      loadProjects();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      setError(errorMsg);
      showError(errorMsg);
      console.error("Error saving project:", err);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    loadProjects();
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
        <h2>Projects Boshqaruvi</h2>
        <button onClick={handleCreate} className="btn-primary">
          + Yangi Project
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
                        <div className="status-controls">
                          <label className="toggle-switch">
                            <input
                              type="checkbox"
                              checked={project.is_active}
                              onChange={() => handleToggleActive(project)}
                            />
                            <span className="toggle-slider"></span>
                            <span className="toggle-label">
                              {project.is_active ? "Active" : "Inactive"}
                            </span>
                          </label>
                          <label className="toggle-switch">
                            <input
                              type="checkbox"
                              checked={project.is_deleted}
                              onChange={() => handleToggleDeleted(project)}
                            />
                            <span className="toggle-slider"></span>
                            <span className="toggle-label">
                              {project.is_deleted ? "Deleted" : "Not Deleted"}
                            </span>
                          </label>
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
                            📷
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
        </>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingProject ? "Project Tahrirlash" : "Yangi Project"}</h3>
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
              <h3>Rasmlar Yuklash - {selectedProject?.name}</h3>
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

export default ProjectAdmin;
