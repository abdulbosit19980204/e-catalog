import React, { useEffect, useState, useCallback } from "react";
import QuillEditor from "./QuillEditor";
import { clientAPI, projectAPI } from "../../api";
import { useNotification } from "../../contexts/NotificationContext";
import "./AdminCRUD.css";

const ClientAdmin = () => {
  const { error: showError, success, confirm } = useNotification();
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [showModal, setShowModal] = useState(false);
  const [activeTab, setActiveTab] = useState("asosiy");
  const [uploading, setUploading] = useState(false);
  const [editingClient, setEditingClient] = useState(null);
  
  const [statusFilter, setStatusFilter] = useState("");
  const [descriptionStatus, setDescriptionStatus] = useState("");
  const [imageStatus, setImageStatus] = useState("");
  const [createdFrom, setCreatedFrom] = useState("");
  const [createdTo, setCreatedTo] = useState("");
  const [projectFilter, setProjectFilter] = useState("");
  const [availableProjects, setAvailableProjects] = useState([]);

  const initialFormData = {
    client_code_1c: "",
    name: "",
    email: "",
    phone: "",
    description: "",
    is_active: true,
    company_name: "",
    tax_id: "",
    registration_number: "",
    legal_address: "",
    actual_address: "",
    fax: "",
    website: "",
    industry: "",
    business_type: "",
    employee_count: "",
    annual_revenue: "",
    established_date: "",
    payment_terms: "",
    credit_limit: "",
    currency: "UZS",
    city: "",
    region: "",
    country: "Uzbekistan",
    postal_code: "",
    contact_person: "",
    contact_position: "",
    contact_email: "",
    contact_phone: "",
    notes: "",
    rating: "",
    priority: 0,
    source: "",
    business_region_code: "",
    business_region_name: "",
    project_ids: [],
  };

  const [formData, setFormData] = useState(initialFormData);
  const [selectedImages, setSelectedImages] = useState([]);
  const [imageMeta, setImageMeta] = useState({ category: "", note: "" });

  const loadClients = useCallback(async () => {
    try {
      setLoading(true);
      const params = {
        limit: pageSize,
        offset: (page - 1) * pageSize,
        search: search || undefined,
        is_active: statusFilter || undefined,
        description_status: descriptionStatus || undefined,
        image_status: imageStatus || undefined,
        created_from: createdFrom || undefined,
        created_to: createdTo || undefined,
        project: projectFilter || undefined,
      };
      const response = await clientAPI.getClients(params);
      setClients(response.data.results || response.data);
      if (response.data.count !== undefined) {
        setTotalCount(response.data.count);
        setTotalPages(Math.ceil(response.data.count / pageSize));
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      showError(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, search, statusFilter, descriptionStatus, imageStatus, createdFrom, createdTo, projectFilter, showError]);

  const loadAvailableProjects = useCallback(async () => {
    try {
      const response = await projectAPI.getProjects({ limit: 100 });
      setAvailableProjects(response.data.results || response.data);
    } catch (err) {
      console.error("Error loading projects:", err);
    }
  }, []);

  useEffect(() => {
    loadClients();
    loadAvailableProjects();
  }, [loadClients, loadAvailableProjects]);

  const handleCreate = () => {
    setEditingClient(null);
    setFormData(initialFormData);
    setActiveTab("asosiy");
    setShowModal(true);
  };

  const handleEdit = (client) => {
    setEditingClient(client);
    
    // Sanitize data to ensure no null values which cause React controlled input warnings
    const sanitizedData = { ...initialFormData };
    
    Object.keys(initialFormData).forEach(key => {
      if (client[key] !== null && client[key] !== undefined) {
        sanitizedData[key] = client[key];
      }
    });

    // Populate project_ids from project object
    // FIXED: Backend now uses `project` (FK) instead of `projects` (M2M)
    if (client.project) {
      sanitizedData.project_ids = [client.project.id];
    } else {
      sanitizedData.project_ids = [];
    }

    setFormData(sanitizedData);
    setActiveTab("asosiy");
    setShowModal(true);
  };

  const handleDelete = async (client) => {
    const confirmed = await confirm({
      title: "Mijozni o'chirish?",
      message: `${client.name} mijozini o'chirib yubormoqchimisiz?`,
      type: 'danger'
    });
    if (!confirmed) return;
    try {
      await clientAPI.deleteClient(client.client_code_1c, client.project?.id);
      loadClients();
      success("Client muvaffaqiyatli o'chirildi");
    } catch (err) {
      showError(err.response?.data?.detail || "O'chirishda xatolik");
    }
  };


  // Helper to clean data before sending to API
  const prepareDataForSubmit = (data) => {
    const cleaned = { ...data };
    // Convert empty strings to null for date fields
    if (cleaned.established_date === "") cleaned.established_date = null;
    
    // Numeric fields should be null if empty string
    ['annual_revenue', 'employee_count', 'credit_limit'].forEach(field => {
        if (cleaned[field] === "") cleaned[field] = null;
    });

    // Clean project_ids
    if (cleaned.project_ids) {
        cleaned.project_ids = cleaned.project_ids.map(id => Number(id));
    }

    return cleaned;
  };

  const handleProjectToggle = (projectId) => {
    const currentIds = [...formData.project_ids];
    const index = currentIds.indexOf(projectId);
    if (index === -1) {
      currentIds.push(projectId);
    } else {
      currentIds.splice(index, 1);
    }
    setFormData({ ...formData, project_ids: currentIds });
  };

  const handleToggleActive = async (client) => {
    try {
      await clientAPI.updateClient(client.client_code_1c, { is_active: !client.is_active }, client.project?.id);
      loadClients();
      success(`Client statusi o'zgartirildi`);
    } catch (err) {
      showError("Statusni o'zgartirib bo'lmadi");
    }
  };


  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const dataToSend = prepareDataForSubmit(formData);
      if (editingClient) {
        await clientAPI.updateClient(editingClient.client_code_1c, dataToSend, editingClient.project?.id);
        success("Client muvaffaqiyatli yangilandi");
      } else {
        await clientAPI.createClient(dataToSend);
        success("Client muvaffaqiyatli yaratildi");
      }
      setShowModal(false);
      loadClients();
    } catch (err) {

      let errorMsg = "Saqlashda xatolik yuz berdi";
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
      console.error("Save error:", err);
    }
  };

  const handleImageSelect = (e) => {
    setSelectedImages(Array.from(e.target.files));
  };

  const handleBulkUpload = async () => {
    if (!editingClient || selectedImages.length === 0) return;
    try {
      setUploading(true);
      const options = {
        ...imageMeta,
        project_id: editingClient.project?.id
      };
      await clientAPI.bulkUploadImages(editingClient.client_code_1c, selectedImages, options);

      // Reload the client data to refresh images tab
      const updated = await clientAPI.getClient(editingClient.client_code_1c, editingClient.project?.id);
      setEditingClient(updated.data);

      setSelectedImages([]);
      setImageMeta({ category: "", note: "" });
      success("Rasmlar muvaffaqiyatli yuklandi!");
    } catch (err) {
      showError("Rasmlar yuklashda xatolik");
    } finally {
      setUploading(false);
    }
  };

  const handleImportExcel = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    // Get project ID if filter is project code_1c
    let project_id = null;
    if (projectFilter) {
      const project = availableProjects.find(p => p.code_1c === projectFilter);
      project_id = project?.id;
      if (!window.confirm(`Ma'lumotlar "${project?.name}" loyihasiga import qilinadi. Davom etasizmi?`)) return;
    } else {
      if (!window.confirm("Loyiha tanlanmagan. Ma'lumotlar mavjud client_code_1c bo'yicha yangilanadi yoki yangi yozuvlar loyihasiz yaratiladi. Davom etasizmi?")) return;
    }

    try {
      setLoading(true);
      const response = await clientAPI.importClients(file, project_id);
      success(`Import yakunlandi: ${response.data.created} yaratildi, ${response.data.updated} yangilandi`);
      if (response.data.errors.length > 0) {
        console.warn("Import errors:", response.data.errors);
      }
      loadClients();
    } catch (err) {
      showError("Excel importda xatolik yuz berdi");
    } finally {
      setLoading(false);
      e.target.value = null;
    }
  };


  const handleDeleteImage = async (imageId) => {
    if (!window.confirm("Bu rasmni o'chirishni xohlaysizmi?")) return;
    try {
      await clientAPI.deleteImage(imageId);
      const updated = await clientAPI.getClient(editingClient.client_code_1c, editingClient.project?.id);
      setEditingClient(updated.data);

      success("Rasm o'chirildi");
    } catch (err) {
      showError("Rasmni o'chirib bo'lmadi");
    }
  };

  const handleSetMainImage = async (imageId) => {
    try {
      await clientAPI.setMainImage(imageId);
      const updated = await clientAPI.getClient(editingClient.client_code_1c, editingClient.project?.id);
      setEditingClient(updated.data);

      success("Rasm asosiy qilib belgilandi");
    } catch (err) {
      showError("Rasmni asosiy qilib bo'lmadi");
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case "asosiy":
        return (
          <div className="form-grid">
            <div className="form-group">
              <label>Client Code 1C *</label>
              <input
                type="text"
                value={formData.client_code_1c}
                onChange={(e) => setFormData({ ...formData, client_code_1c: e.target.value })}
                required
                className="form-input"
                disabled={!!editingClient}
              />
            </div>
            <div className="form-group">
              <label>Full Name *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Phone</label>
              <input
                type="text"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group full-width">
              <label>Description</label>
              <QuillEditor
                value={formData.description}
                onChange={(val) => setFormData({ ...formData, description: val })}
                className="quill-editor"
              />
            </div>
            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                />
                Faol
              </label>
            </div>
          </div>
        );
      case "kompaniya":
        return (
          <div className="form-grid">
            <div className="form-group">
              <label>Kompaniya nomi</label>
              <input
                type="text"
                value={formData.company_name}
                onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>INN / STIR</label>
              <input
                type="text"
                value={formData.tax_id}
                onChange={(e) => setFormData({ ...formData, tax_id: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Ro'yxatdan o'tish raqami</label>
              <input
                type="text"
                value={formData.registration_number}
                onChange={(e) => setFormData({ ...formData, registration_number: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Tashkil etilgan sana</label>
              <input
                type="date"
                value={formData.established_date}
                onChange={(e) => setFormData({ ...formData, established_date: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Soha / Industry</label>
              <input
                type="text"
                value={formData.industry}
                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Biznes turi</label>
              <input
                type="text"
                value={formData.business_type}
                onChange={(e) => setFormData({ ...formData, business_type: e.target.value })}
                className="form-input"
              />
            </div>
          </div>
        );
      case "manzillar":
        return (
          <div className="form-grid">
            <div className="form-group full-width">
              <label>Yuridik manzil</label>
              <textarea
                value={formData.legal_address}
                onChange={(e) => setFormData({ ...formData, legal_address: e.target.value })}
                className="form-textarea"
                rows={2}
              />
            </div>
            <div className="form-group full-width">
              <label>Haqiqiy manzil</label>
              <textarea
                value={formData.actual_address}
                onChange={(e) => setFormData({ ...formData, actual_address: e.target.value })}
                className="form-textarea"
                rows={2}
              />
            </div>
            <div className="form-group">
              <label>Viloyat / Hudud</label>
              <input
                type="text"
                value={formData.region}
                onChange={(e) => setFormData({ ...formData, region: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Shahar</label>
              <input
                type="text"
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Davlat</label>
              <input
                type="text"
                value={formData.country}
                onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Pochta indeksi</label>
              <input
                type="text"
                value={formData.postal_code}
                onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Business Region (Code)</label>
              <input
                type="text"
                value={formData.business_region_code}
                onChange={(e) => setFormData({ ...formData, business_region_code: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Business Region (Name)</label>
              <input
                type="text"
                value={formData.business_region_name}
                onChange={(e) => setFormData({ ...formData, business_region_name: e.target.value })}
                className="form-input"
              />
            </div>
          </div>
        );
      case "moliya":
        return (
          <div className="form-grid">
            <div className="form-group">
              <label>To'lov shartlari</label>
              <input
                type="text"
                value={formData.payment_terms}
                onChange={(e) => setFormData({ ...formData, payment_terms: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Kredit limiti</label>
              <input
                type="number"
                value={formData.credit_limit}
                onChange={(e) => setFormData({ ...formData, credit_limit: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Valyuta</label>
              <select
                value={formData.currency}
                onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                className="form-input"
              >
                <option value="UZS">UZS</option>
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
              </select>
            </div>
            <div className="form-group">
              <label>Yillik daromad</label>
              <input
                type="number"
                value={formData.annual_revenue}
                onChange={(e) => setFormData({ ...formData, annual_revenue: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Xodimlar soni</label>
              <input
                type="number"
                value={formData.employee_count}
                onChange={(e) => setFormData({ ...formData, employee_count: e.target.value })}
                className="form-input"
              />
            </div>
          </div>
        );
      case "kontakt":
        return (
          <div className="form-grid">
            <div className="form-group">
              <label>Kontakt shaxs</label>
              <input
                type="text"
                value={formData.contact_person}
                onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Lavozimi</label>
              <input
                type="text"
                value={formData.contact_position}
                onChange={(e) => setFormData({ ...formData, contact_position: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Kontakt Email</label>
              <input
                type="email"
                value={formData.contact_email}
                onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Kontakt Telefon</label>
              <input
                type="text"
                value={formData.contact_phone}
                onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Veb-sayt</label>
              <input
                type="url"
                value={formData.website}
                onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Faks</label>
              <input
                type="text"
                value={formData.fax}
                onChange={(e) => setFormData({ ...formData, fax: e.target.value })}
                className="form-input"
              />
            </div>
          </div>
        );
      case "loyihalar":
        return (
          <div className="projects-selection-tab">
            <h4>Bog'langan loyihalar</h4>
            <div className="projects-list-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '10px', marginTop: '15px' }}>
              {availableProjects.map(project => (
                <div 
                  key={project.id} 
                  className={`project-selection-item ${formData.project_ids.includes(project.id) ? 'selected' : ''}`}
                  onClick={() => handleProjectToggle(project.id)}
                  style={{
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    backgroundColor: formData.project_ids.includes(project.id) ? '#e3f2fd' : 'white',
                    borderColor: formData.project_ids.includes(project.id) ? '#2196f3' : '#ddd',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px'
                  }}
                >
                  <input 
                    type="checkbox" 
                    checked={formData.project_ids.includes(project.id)} 
                    readOnly 
                  />
                  <span>{project.name}</span>
                </div>
              ))}
              {availableProjects.length === 0 && <p>Loyihalar mavjud emas</p>}
            </div>
          </div>
        );
      case "rasmlar":
        return (
          <div className="image-management-tab">
            {!editingClient ? (
              <p className="form-info">Rasm yuklash uchun avval clientni saqlang.</p>
            ) : (
              <>
                <div className="image-upload-section">
                  <h4>Yangi rasm yuklash</h4>
                  <div className="form-grid">
                    <div className="form-group">
                      <input type="file" multiple onChange={handleImageSelect} className="form-input" />
                    </div>
                    <div className="form-group">
                      <input 
                        type="text" 
                        placeholder="Toifa (vitrina, hisobot...)" 
                        value={imageMeta.category}
                        onChange={(e) => setImageMeta({...imageMeta, category: e.target.value})}
                        className="form-input" 
                      />
                    </div>
                    <div className="form-group full-width">
                      <textarea 
                        placeholder="Izoh..." 
                        value={imageMeta.note}
                        onChange={(e) => setImageMeta({...imageMeta, note: e.target.value})}
                        className="form-textarea" 
                        rows={2}
                      />
                    </div>
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
                  {editingClient.images && editingClient.images.length > 0 ? (
                    <div className="image-management-grid">
                      {editingClient.images.map(img => (
                        <div key={img.id} className="image-item">
                          <img src={img.image_thumbnail_url} alt={img.category} />
                          {img.is_main && <span className="main-badge">Asosiy</span>}
                          <div className="image-item-actions">
                            {!img.is_main && (
                              <button
                                type="button"
                                onClick={() => handleSetMainImage(img.id)}
                                className="btn-mini-delete"
                                style={{ background: '#fff', color: '#f59e0b', borderColor: '#f59e0b', marginRight: '5px' }}
                                title="Asosiy qilish"
                              >
                                ⭐
                              </button>
                            )}
                            <button 
                              type="button" 
                              onClick={() => handleDeleteImage(img.id)} 
                              className="btn-mini-delete"
                              title="O'chirish"
                            >
                              ×
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p>Rasmlar mavjud emas.</p>
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

  const renderPagination = () => {
    if (totalPages <= 1) return null;
    return (
      <div className="pagination" style={{ marginTop: 0, marginBottom: 20 }}>
        <div className="pagination-controls">
          <button onClick={() => setPage(page - 1)} disabled={page === 1} className="page-button">Oldingi</button>
          <div className="page-numbers">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum = totalPages <= 5 || page <= 3 ? i + 1 : (page >= totalPages - 2 ? totalPages - 4 + i : page - 2 + i);
              return (
                <button key={pageNum} onClick={() => setPage(pageNum)} className={`page-number ${page === pageNum ? "active" : ""}`}>
                  {pageNum}
                </button>
              );
            })}
          </div>
          <button onClick={() => setPage(page + 1)} disabled={page === totalPages} className="page-button">Keyingi</button>
        </div>
        <div className="pagination-controls">
          <span className="page-info">Jami: {totalCount}</span>
          <select value={pageSize} onChange={(e) => {setPageSize(parseInt(e.target.value)); setPage(1);}} className="page-size-select">
            {[10, 20, 50, 100].map(sz => <option key={sz} value={sz}>{sz}</option>)}
          </select>
        </div>
      </div>
    );
  };

  return (
    <div className="admin-crud">
      <div className="crud-header">
        <h2>👥 Clients</h2>
        <div className="header-actions">
          <label className="btn-tertiary" style={{ cursor: 'pointer', display: 'inline-flex', alignItems: 'center' }}>
            📥 Import Excel
            <input type="file" accept=".xlsx, .xls" onChange={handleImportExcel} style={{ display: 'none' }} />
          </label>
          <button onClick={handleCreate} className="btn-primary">
            <span>+</span> Yangi Client
          </button>
        </div>
      </div>


      <form onSubmit={(e) => {e.preventDefault(); setPage(1); loadClients();}} className="search-form">
        <div className="search-row">
          <input
            type="text"
            placeholder="Qidirish (ism, email, phone, code)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="btn-primary">🔍 Qidirish</button>
          <button type="button" className="btn-tertiary" onClick={() => {
            setSearch(""); 
            setStatusFilter("");
            setDescriptionStatus("");
            setImageStatus("");
            setCreatedFrom("");
            setCreatedTo("");
            setProjectFilter("");
            setPage(1); 
          }}>🔄 Tozalash</button>
        </div>
        <div className="filter-row">
          <div className="filter-field">
            <label>Status</label>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">Hammasi</option>
              <option value="true">Faol</option>
              <option value="false">Faol emas</option>
            </select>
          </div>
          <div className="filter-field">
            <label>Description holati</label>
            <select value={descriptionStatus} onChange={(e) => setDescriptionStatus(e.target.value)}>
              <option value="">Hammasi</option>
              <option value="with">Description bor</option>
              <option value="without">Description yo'q</option>
            </select>
          </div>
          <div className="filter-field">
            <label>Rasm holati</label>
            <select value={imageStatus} onChange={(e) => setImageStatus(e.target.value)}>
              <option value="">Hammasi</option>
              <option value="with">Rasm bor</option>
              <option value="without">Rasm yo'q</option>
            </select>
          </div>
          <div className="filter-field">
            <label>Yaratilgan (dan)</label>
            <input type="date" value={createdFrom} onChange={(e) => setCreatedFrom(e.target.value)} />
          </div>
          <div className="filter-field">
            <label>Yaratilgan (gacha)</label>
            <input type="date" value={createdTo} onChange={(e) => setCreatedTo(e.target.value)} />
          </div>
          <div className="filter-field">
            <label>Loyiha (Project)</label>
            <select value={projectFilter} onChange={(e) => setProjectFilter(e.target.value)}>
              <option value="">Hammasi</option>
              {availableProjects.map(p => (
                <option key={p.id} value={p.code_1c}>{p.name}</option>
              ))}
            </select>
          </div>
        </div>
      </form>

      {loading ? (
        <div className="loading"><div className="spinner"></div><p>Yuklanmoqda...</p></div>
      ) : (
        <>
          {renderPagination()}
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Code 1C</th>
                  <th>Name</th>
                  <th>Loyihalar</th>
                  <th>Email / Phone</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {clients.length === 0 ? (
                  <tr><td colSpan="6" className="no-data">Ma'lumot topilmadi</td></tr>
                ) : (
                  clients.map((client) => (
                    <tr key={client.id}>
                      <td><span className="code-tag">{client.client_code_1c}</span></td>
                      <td><strong>{client.name}</strong></td>
                      <td>
                        <div className="project-tags">
                          {client.project ? (
                            <span 
                              className="project-tag" 
                              style={{
                                fontSize: '0.8rem',
                                padding: '3px 8px',
                                backgroundColor: client.project.is_integration ? '#e3f2fd' : '#f1f1f1',
                                borderRadius: '4px',
                                border: '1px solid #ddd'
                              }}
                            >
                              {client.project.name}
                            </span>
                          ) : (
                            <span style={{fontSize: '0.75rem', color: '#999'}}>Bog'lanmagan</span>
                          )}
                        </div>
                      </td>
                      <td>
                        <div style={{fontSize: '0.8rem'}}>
                          {client.email && <div>✉️ {client.email}</div>}
                          {client.phone && <div>📞 {client.phone}</div>}
                        </div>
                      </td>
                      <td>
                        <span 
                          className={`status-badge ${client.is_active ? 'active' : 'inactive'}`}
                          onClick={() => handleToggleActive(client)}
                          style={{ cursor: 'pointer' }}
                        >
                          {client.is_active ? "● Faol" : "○ Faol emas"}
                        </span>
                      </td>
                      <td>
                        <div className="action-buttons">
                          <button onClick={() => handleEdit(client)} className="btn-edit" title="Tahrirlash">✏️</button>
                          <button onClick={() => handleDelete(client)} className="btn-delete" title="O'chirish">🗑️</button>
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
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingClient ? `Client Tahrirlash: ${editingClient.name}` : "Yangi Client"}</h3>
              <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            
            <div className="tabs-navigation">
              <button onClick={() => setActiveTab("asosiy")} className={`tab-btn ${activeTab === "asosiy" ? "active" : ""}`}>Asosiy</button>
              <button onClick={() => setActiveTab("kompaniya")} className={`tab-btn ${activeTab === "kompaniya" ? "active" : ""}`}>Kompaniya</button>
              <button onClick={() => setActiveTab("manzillar")} className={`tab-btn ${activeTab === "manzillar" ? "active" : ""}`}>Manzillar</button>
              <button onClick={() => setActiveTab("moliya")} className={`tab-btn ${activeTab === "moliya" ? "active" : ""}`}>Moliya</button>
              <button onClick={() => setActiveTab("kontakt")} className={`tab-btn ${activeTab === "kontakt" ? "active" : ""}`}>Kontakt</button>
              <button onClick={() => setActiveTab("loyihalar")} className={`tab-btn ${activeTab === "loyihalar" ? "active" : ""}`}>Loyihalar</button>
              <button onClick={() => setActiveTab("rasmlar")} className={`tab-btn ${activeTab === "rasmlar" ? "active" : ""}`}>Rasmlar</button>
            </div>

            <form onSubmit={handleSubmit} className="modal-form">
              {renderTabContent()}
              
              <div className="modal-actions" style={{position: 'sticky', bottom: 0, background: 'var(--bg-card)', zIndex: 10, paddingBottom: 0}}>
                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary">Bekor qilish</button>
                <button type="submit" className="btn-primary">Saqlash</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClientAdmin;
