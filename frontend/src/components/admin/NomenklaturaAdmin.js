import React, { useEffect, useState, useCallback } from "react";
import QuillEditor from "./QuillEditor";
import { nomenklaturaAPI, projectAPI } from "../../api";
import { useNotification } from "../../contexts/NotificationContext";
import "./AdminCRUD.css";

const NomenklaturaAdmin = () => {
  const { success, error: showError } = useNotification();
  const [nomenklatura, setNomenklatura] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [showModal, setShowModal] = useState(false);
  const [activeTab, setActiveTab] = useState("asosiy");
  const [uploading, setUploading] = useState(false);
  const [editingNomenklatura, setEditingNomenklatura] = useState(null);

  // Filters
  const [filterProject, setFilterProject] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [filterCategory, setFilterCategory] = useState("");
  const [createdFrom, setCreatedFrom] = useState("");
  const [createdTo, setCreatedTo] = useState("");

  const [projectsList, setProjectsList] = useState([]);

  const initialFormData = {
    code_1c: "",
    name: "",
    title: "",
    description: "",
    is_active: true,
    project_ids: [],
    sku: "",
    barcode: "",
    brand: "",
    manufacturer: "",
    model: "",
    series: "",
    vendor_code: "",
    base_price: "",
    sale_price: "",
    cost_price: "",
    currency: "UZS",
    discount_percent: "",
    tax_rate: "",
    stock_quantity: "",
    min_stock: "",
    max_stock: "",
    unit_of_measure: "",
    weight: "",
    dimensions: "",
    volume: "",
    category: "",
    subcategory: "",
    tags: [],
    color: "",
    size: "",
    material: "",
    warranty_period: "",
    expiry_date: "",
    production_date: "",
    notes: "",
    rating: "",
    popularity_score: 0,
    seo_keywords: "",
    source: "",
  };

  const [formData, setFormData] = useState(initialFormData);
  const [selectedImages, setSelectedImages] = useState([]);
  const [imageMeta, setImageMeta] = useState({ category: "", note: "" });

  const loadProjects = useCallback(async () => {
    try {
      const resp = await projectAPI.getProjects({ page_size: 1000 });
      setProjectsList(resp.data.results || resp.data);
    } catch (err) {
      console.error("Error loading projects:", err);
    }
  }, []);

  const loadNomenklatura = useCallback(async () => {
    try {
      setLoading(true);
      const params = {
        page,
        page_size: pageSize,
        search: search || undefined,
        project_id: filterProject || undefined,
        is_active: statusFilter || undefined,
        category: filterCategory || undefined,
        created_from: createdFrom || undefined,
        created_to: createdTo || undefined,
      };
      const response = await nomenklaturaAPI.getNomenklatura(params);
      setNomenklatura(response.data.results || response.data);
      if (response.data.count !== undefined) {
        setTotalCount(response.data.count);
        setTotalPages(Math.ceil(response.data.count / pageSize));
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      showError(errorMsg);
      console.error("Error loading nomenklatura:", err);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, search, filterProject, statusFilter, filterCategory, createdFrom, createdTo, showError]);

  useEffect(() => {
    loadProjects();
    loadNomenklatura();
  }, [loadProjects, loadNomenklatura]);

  const handleCreate = () => {
    setEditingNomenklatura(null);
    setFormData(initialFormData);
    setActiveTab("asosiy");
    setShowModal(true);
  };

  const handleEdit = (item) => {
    setEditingNomenklatura(item);
    
    // Sanitize data to ensure no null values which cause React controlled input warnings
    const sanitizedData = { ...initialFormData };
    
    Object.keys(initialFormData).forEach(key => {
      if (key === 'project_ids') return; // Handle separately
      if (item[key] !== null && item[key] !== undefined) {
        sanitizedData[key] = item[key];
      }
    });
    
    // Handle special fields
    sanitizedData.project_ids = item.projects ? item.projects.map(p => p.id) : [];
    
    setFormData(sanitizedData);
    setActiveTab("asosiy");
    setShowModal(true);
  };

  const handleDelete = async (code1c) => {
    if (!window.confirm("Bu nomenklatura'ni o'chirishni xohlaysizmi?")) return;
    try {
      await nomenklaturaAPI.deleteNomenklatura(code1c);
      loadNomenklatura();
      success("Nomenklatura o'chirildi");
    } catch (err) {
      showError("O'chirishda xatolik");
    }
  };

  const handleToggleActive = async (item) => {
    try {
      await nomenklaturaAPI.updateNomenklatura(item.code_1c, { is_active: !item.is_active });
      loadNomenklatura();
      success(`Status o'zgartirildi`);
    } catch (err) {
      showError("Statusni o'zgartirib bo'lmadi");
    }
  };

  // Helper to clean data before sending to API
  const prepareDataForSubmit = (data) => {
    const cleaned = { ...data };
    
    // Numeric fields
    const numericFields = [
      'base_price', 'sale_price', 'cost_price', 'discount_percent', 'tax_rate',
      'stock_quantity', 'min_stock', 'max_stock', 'weight', 'volume'
    ];
    
    numericFields.forEach(field => {
        if (cleaned[field] === "") cleaned[field] = null;
    });

    // Date fields
    ['expiry_date', 'production_date'].forEach(field => {
        if (cleaned[field] === "") cleaned[field] = null;
    });
    
    return cleaned;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const dataToSend = prepareDataForSubmit(formData);
      if (editingNomenklatura) {
        await nomenklaturaAPI.updateNomenklatura(editingNomenklatura.code_1c, dataToSend);
        success("Muvaffaqiyatli yangilandi");
      } else {
        await nomenklaturaAPI.createNomenklatura(dataToSend);
        success("Muvaffaqiyatli yaratildi");
      }
      setShowModal(false);
      loadNomenklatura();
    } catch (err) {
      showError(err.response?.data?.detail || "Saqlashda xatolik");
    }
  };

  const handleImageSelect = (e) => {
    setSelectedImages(Array.from(e.target.files));
  };

  const handleBulkUpload = async () => {
    if (!editingNomenklatura || selectedImages.length === 0) return;
    try {
      setUploading(true);
      await nomenklaturaAPI.bulkUploadImages(editingNomenklatura.code_1c, selectedImages, imageMeta);
      const updated = await nomenklaturaAPI.getNomenklaturaItem(editingNomenklatura.code_1c);
      setEditingNomenklatura(updated.data);
      setSelectedImages([]);
      setImageMeta({ category: "", note: "" });
      success("Rasmlar yuklandi!");
    } catch (err) {
      showError("Rasmlar yuklashda xatolik");
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteImage = async (imageId) => {
    if (!window.confirm("Rasmni o'chirish?")) return;
    try {
      await nomenklaturaAPI.deleteImage(imageId);
      const updated = await nomenklaturaAPI.getNomenklaturaItem(editingNomenklatura.code_1c);
      setEditingNomenklatura(updated.data);
      success("Rasm o'chirildi");
    } catch (err) {
      showError("Rasmni o'chirib bo'lmadi");
    }
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
                onChange={(e) => setFormData({ ...formData, code_1c: e.target.value })}
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
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Title</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Loyihalar</label>
              <select
                multiple
                value={formData.project_ids}
                onChange={(e) => {
                  const values = Array.from(e.target.selectedOptions, option => parseInt(option.value));
                  setFormData({ ...formData, project_ids: values });
                }}
                className="form-input multi-select"
                style={{ height: '80px' }}
              >
                {projectsList.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
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
      case "specs":
        return (
          <div className="form-grid">
            <div className="form-group">
              <label>SKU</label>
              <input type="text" value={formData.sku} onChange={(e) => setFormData({ ...formData, sku: e.target.value })} className="form-input" />
            </div>
            <div className="form-group">
              <label>Barcode</label>
              <input type="text" value={formData.barcode} onChange={(e) => setFormData({ ...formData, barcode: e.target.value })} className="form-input" />
            </div>
            <div className="form-group">
              <label>Brand</label>
              <input type="text" value={formData.brand} onChange={(e) => setFormData({ ...formData, brand: e.target.value })} className="form-input" />
            </div>
            <div className="form-group">
              <label>Ishlab chiqaruvchi</label>
              <input type="text" value={formData.manufacturer} onChange={(e) => setFormData({ ...formData, manufacturer: e.target.value })} className="form-input" />
            </div>
            <div className="form-group">
              <label>Model</label>
              <input type="text" value={formData.model} onChange={(e) => setFormData({ ...formData, model: e.target.value })} className="form-input" />
            </div>
            <div className="form-group">
              <label>Vendor Code</label>
              <input type="text" value={formData.vendor_code} onChange={(e) => setFormData({ ...formData, vendor_code: e.target.value })} className="form-input" />
            </div>
            <div className="form-group">
              <label>Color</label>
              <input type="text" value={formData.color} onChange={(e) => setFormData({ ...formData, color: e.target.value })} className="form-input" />
            </div>
            <div className="form-group">
              <label>Size</label>
              <input type="text" value={formData.size} onChange={(e) => setFormData({ ...formData, size: e.target.value })} className="form-input" />
            </div>
          </div>
        );
      case "pricing":
        return (
          <div className="form-grid">
            <div className="form-group">
              <label>Base Price</label>
              <input type="number" value={formData.base_price} onChange={(e) => setFormData({ ...formData, base_price: e.target.value })} className="form-input" />
            </div>
            <div className="form-group">
              <label>Sale Price</label>
              <input type="number" value={formData.sale_price} onChange={(e) => setFormData({ ...formData, sale_price: e.target.value })} className="form-input" />
            </div>
            <div className="form-group">
              <label>Stock Qty</label>
              <input type="number" value={formData.stock_quantity} onChange={(e) => setFormData({ ...formData, stock_quantity: e.target.value })} className="form-input" />
            </div>
            <div className="form-group">
              <label>Unit</label>
              <input type="text" value={formData.unit_of_measure} onChange={(e) => setFormData({ ...formData, unit_of_measure: e.target.value })} className="form-input" />
            </div>
            <div className="form-group">
              <label>Currency</label>
              <input type="text" value={formData.currency} onChange={(e) => setFormData({ ...formData, currency: e.target.value })} className="form-input" />
            </div>
            <div className="form-group">
              <label>Tax Rate (%)</label>
              <input type="number" value={formData.tax_rate} onChange={(e) => setFormData({ ...formData, tax_rate: e.target.value })} className="form-input" />
            </div>
          </div>
        );
      case "cat":
        return (
          <div className="form-grid">
            <div className="form-group">
              <label>Category</label>
              <input type="text" value={formData.category} onChange={(e) => setFormData({ ...formData, category: e.target.value })} className="form-input" />
            </div>
            <div className="form-group">
              <label>Subcategory</label>
              <input type="text" value={formData.subcategory} onChange={(e) => setFormData({ ...formData, subcategory: e.target.value })} className="form-input" />
            </div>
            <div className="form-group full-width">
              <label>SEO Keywords</label>
              <textarea value={formData.seo_keywords} onChange={(e) => setFormData({ ...formData, seo_keywords: e.target.value })} className="form-textarea" rows={2} />
            </div>
          </div>
        );
      case "rasmlar":
        return (
          <div className="image-management-tab">
            {!editingNomenklatura ? (
              <p>Rasmlar uchun avval saqlang.</p>
            ) : (
              <>
                <div className="image-upload-section">
                  <div className="form-grid">
                    <div className="form-group"><input type="file" multiple onChange={handleImageSelect} className="form-input" /></div>
                    <div className="form-group"><input type="text" placeholder="Category" value={imageMeta.category} onChange={(e) => setImageMeta({...imageMeta, category: e.target.value})} className="form-input" /></div>
                  </div>
                  <button type="button" onClick={handleBulkUpload} className="btn-primary" disabled={uploading || selectedImages.length === 0}>
                    {uploading ? "Yuklanmoqda..." : `Yuklash (${selectedImages.length})`}
                  </button>
                </div>
                <div className="image-management-grid" style={{ marginTop: '20px' }}>
                  {editingNomenklatura.images && editingNomenklatura.images.map(img => (
                    <div key={img.id} className="image-item">
                      <img src={img.image_thumbnail_url} alt="" />
                      <div className="image-item-actions">
                        <button type="button" onClick={() => handleDeleteImage(img.id)} className="btn-mini-delete">×</button>
                      </div>
                      {img.is_main && <span className="main-badge">Main</span>}
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        );
      default: return null;
    }
  };

  const renderPagination = () => {
    if (totalPages <= 1) return null;
    return (
      <div className="pagination" style={{ marginTop: 0, marginBottom: 20 }}>
        <div className="pagination-controls">
          <button onClick={() => setPage(page-1)} disabled={page===1} className="page-button">Oldingi</button>
          <span style={{margin: '0 10px', fontWeight: 600}}>Sahifa {page} / {totalPages}</span>
          <button onClick={() => setPage(page+1)} disabled={page===totalPages} className="page-button">Keyingi</button>
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
        <h2>📦 Nomenklatura</h2>
        <button onClick={handleCreate} className="btn-primary">+ Yangi</button>
      </div>

      <form onSubmit={(e) => {e.preventDefault(); setPage(1); loadNomenklatura();}} className="search-form">
        <div className="search-row">
          <input type="text" placeholder="Qidirish (nomi, code, sku)..." value={search} onChange={(e) => setSearch(e.target.value)} className="search-input" />
          <button type="submit" className="btn-primary">Qidirish</button>
          <button type="button" className="btn-tertiary" onClick={() => {
            setSearch(""); 
            setFilterProject("");
            setStatusFilter("");
            setFilterCategory("");
            setCreatedFrom("");
            setCreatedTo("");
            setPage(1); 
            loadNomenklatura();
          }}>Tozalash</button>
        </div>
        <div className="filter-row">
          <div className="filter-field">
            <label>Loyiha</label>
            <select value={filterProject} onChange={(e) => setFilterProject(e.target.value)}>
              <option value="">Hammasi</option>
              {projectsList.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          <div className="filter-field">
            <label>Status</label>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">Hammasi</option>
              <option value="true">Faol</option>
              <option value="false">Faol emas</option>
            </select>
          </div>
          <div className="filter-field">
            <label>Kategoriya</label>
            <input type="text" placeholder="Category..." value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)} />
          </div>
          <div className="filter-field">
            <label>Yaratilgan (dan)</label>
            <input type="date" value={createdFrom} onChange={(e) => setCreatedFrom(e.target.value)} />
          </div>
          <div className="filter-field">
            <label>Yaratilgan (gacha)</label>
            <input type="date" value={createdTo} onChange={(e) => setCreatedTo(e.target.value)} />
          </div>
        </div>
      </form>

      {loading ? (
        <div className="loading"><div className="spinner"></div></div>
      ) : (
        <>
          {renderPagination()}
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Nomi</th>
                  <th>Status</th>
                  <th>Amallar</th>
                </tr>
              </thead>
              <tbody>
                {nomenklatura.map((item) => (
                  <tr key={item.id}>
                    <td><span className="code-tag">{item.code_1c}</span></td>
                    <td>{item.name}</td>
                    <td>
                      <span className={`status-badge ${item.is_active ? 'active' : 'inactive'}`} onClick={() => handleToggleActive(item)} style={{cursor:'pointer'}}>
                        {item.is_active ? "● Faol" : "○ Faol emas"}
                      </span>
                    </td>
                    <td>
                      <div className="action-buttons">
                        <button onClick={() => handleEdit(item)} className="btn-edit">✏️</button>
                        <button onClick={() => handleDelete(item.code_1c)} className="btn-delete">🗑️</button>
                      </div>
                    </td>
                  </tr>
                ))}
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
              <h3>{editingNomenklatura ? `Tahrirlash: ${editingNomenklatura.name}` : "Yangi"}</h3>
              <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <div className="tabs-navigation">
              <button onClick={() => setActiveTab("asosiy")} className={`tab-btn ${activeTab === "asosiy" ? "active" : ""}`}>Asosiy</button>
              <button onClick={() => setActiveTab("specs")} className={`tab-btn ${activeTab === "specs" ? "active" : ""}`}>Xususiyatlar</button>
              <button onClick={() => setActiveTab("pricing")} className={`tab-btn ${activeTab === "pricing" ? "active" : ""}`}>Narx/Ombor</button>
              <button onClick={() => setActiveTab("cat")} className={`tab-btn ${activeTab === "cat" ? "active" : ""}`}>Kategoriya</button>
              <button onClick={() => setActiveTab("rasmlar")} className={`tab-btn ${activeTab === "rasmlar" ? "active" : ""}`}>Rasmlar</button>
            </div>
            <form onSubmit={handleSubmit} className="modal-form">
              {renderTabContent()}
              <div className="modal-actions">
                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary">Bekor</button>
                <button type="submit" className="btn-primary">Saqlash</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default NomenklaturaAdmin;
