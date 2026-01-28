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
  
  // Excel Import state
  const [showImportModal, setShowImportModal] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [importLoading, setImportLoading] = useState(false);
  const [importResult, setImportResult] = useState(null);

  // Filters
  const [filterProject, setFilterProject] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [filterCategory, setFilterCategory] = useState("");
  const [createdFrom, setCreatedFrom] = useState("");
  const [createdTo, setCreatedTo] = useState("");
  const [imageStatusFilter, setImageStatusFilter] = useState("");
  const [descriptionStatusFilter, setDescriptionStatusFilter] = useState("");

  const [projectsList, setProjectsList] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [bulkLoading, setBulkLoading] = useState(null);

  const initialFormData = {
    code_1c: "",
    article_code: "",
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
      const resp = await projectAPI.getProjects({ limit: 1000 });
      setProjectsList(resp.data.results || resp.data);
    } catch (err) {
      console.error("Error loading projects:", err);
    }
  }, []);

  const loadNomenklatura = useCallback(async () => {
    try {
      setLoading(true);
      const params = {
        limit: pageSize,
        offset: (page - 1) * pageSize,
        search: search || undefined,
        project_id: filterProject || undefined,
        is_active: statusFilter || undefined,
        category: filterCategory || undefined,
        created_from: createdFrom || undefined,
        created_to: createdTo || undefined,
        image_status: imageStatusFilter || undefined,
        description_status: descriptionStatusFilter || undefined,
      };
      const response = await nomenklaturaAPI.getNomenklatura(params);
      
      const items = response.data.results || response.data;
      setNomenklatura(items);
      
      if (response.data.count !== undefined) {
        setTotalCount(response.data.count);
        setTotalPages(Math.ceil(response.data.count / pageSize));
      } else {
        setTotalCount(items.length);
        setTotalPages(1);
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Xatolik yuz berdi";
      showError(errorMsg);
      console.error("Error loading nomenklatura:", err);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, search, filterProject, statusFilter, filterCategory, createdFrom, createdTo, imageStatusFilter, descriptionStatusFilter, showError]);

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
    const sanitizedData = { ...initialFormData };
    
    Object.keys(initialFormData).forEach(key => {
      if (key === 'project_ids') return;
      if (item[key] !== null && item[key] !== undefined) {
        sanitizedData[key] = item[key];
      }
    });
    
    // FIXED: Backend now uses `project` (FK) instead of `projects` (M2M)
    sanitizedData.project_ids = item.project ? [item.project.id] : [];

    setFormData(sanitizedData);
    setActiveTab("asosiy");
    setShowModal(true);
  };

  const handleDelete = async (item) => {
    if (!window.confirm("Bu nomenklatura'ni o'chirishni xohlaysizmi?")) return;
    try {
      await nomenklaturaAPI.deleteNomenklatura(item.code_1c, item.project?.id);
      loadNomenklatura();
      success("Nomenklatura o'chirildi");
    } catch (err) {
      showError("O'chirishda xatolik");
    }
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

  const handleToggleActive = async (item) => {
    try {
      await nomenklaturaAPI.updateNomenklatura(item.code_1c, { is_active: !item.is_active }, item.project?.id);
      loadNomenklatura();
      success(`Status o'zgartirildi`);
    } catch (err) {
      showError("Statusni o'zgartirib bo'lmadi");
    }
  };


  const prepareDataForSubmit = (data) => {
    const cleaned = { ...data };
    const numericFields = [
      'base_price', 'sale_price', 'cost_price', 'discount_percent', 'tax_rate',
      'stock_quantity', 'min_stock', 'max_stock', 'weight', 'volume',
      'warranty_period', 'rating', 'popularity_score'
    ];
    numericFields.forEach(field => {
        if (cleaned[field] === "") cleaned[field] = null;
    });
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
        await nomenklaturaAPI.updateNomenklatura(editingNomenklatura.code_1c, dataToSend, editingNomenklatura.project?.id);
        success("Muvaffaqiyatli yangilandi");
      } else {
        await nomenklaturaAPI.createNomenklatura(dataToSend);
        success("Muvaffaqiyatli yaratildi");
      }
      setShowModal(false);
      loadNomenklatura();
    } catch (err) {

      let errorMsg = "Saqlashda xatolik";
      const data = err.response?.data;
      if (data) {
        if (data.detail) errorMsg = data.detail;
        else if (typeof data === 'object') {
          errorMsg = Object.entries(data)
            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(", ") : value}`)
            .join("\n");
        }
      }
      showError(errorMsg);
    }
  };

  const handleImageSelect = (e) => setSelectedImages(Array.from(e.target.files));

  const handleBulkUpload = async () => {
    if (!editingNomenklatura || selectedImages.length === 0) return;
    try {
      setUploading(true);
      const options = {
        ...imageMeta,
        project_id: editingNomenklatura.project?.id
      };
      await nomenklaturaAPI.bulkUploadImages(editingNomenklatura.code_1c, selectedImages, options);

      const updated = await nomenklaturaAPI.getNomenklaturaItem(editingNomenklatura.code_1c, editingNomenklatura.project?.id);
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

  const handleExport = async () => {
    try {
      const params = {
        search: search || undefined,
        project_id: filterProject || undefined,
        is_active: statusFilter || undefined,
        category: filterCategory || undefined,
        image_status: imageStatusFilter || undefined,
        description_status: descriptionStatusFilter || undefined,
      };
      const response = await nomenklaturaAPI.exportNomenklatura(params);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'nomenklatura_export.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      showError("Eksport qilishda xatolik yuz berdi");
    }
  };

  const handleTemplateDownload = async () => {
    try {
      const response = await nomenklaturaAPI.downloadTemplate();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'nomenklatura_template.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      showError("Shablonni yuklab olishda xatolik yuz berdi");
    }
  };

  const handleImport = async (e) => {
    e.preventDefault();
    if (!importFile) return;

    try {
      setImportLoading(true);
      setImportResult(null);
      const response = await nomenklaturaAPI.importNomenklatura(importFile, filterProject);
      setImportResult(response.data);
      success("Import muvaffaqiyatli yakunlandi");
      loadNomenklatura();
    } catch (err) {
      const msg = err.response?.data?.error || "Import qilishda xatolik yuz berdi";
      showError(msg);
    } finally {
      setImportLoading(false);
    }
  };

  // AI Bulk Actions
  const handleBulkEnrich = async (allInProject = false) => {
    if (!allInProject && selectedIds.length === 0) {
      showError("Mahsulotlarni tanlang");
      return;
    }
    if (allInProject && !filterProject) {
      showError("Loyiha tanlanmagan");
      return;
    }

    const confirmMsg = allInProject 
      ? "Loyiha bo'yicha barcha mahsulotlarni boyitish? (Katta hajm vaqt olishi mumkin)"
      : `${selectedIds.length} ta mahsulotni boyitishni tasdiqlaysizmi?`;

    if (!window.confirm(confirmMsg)) return;

    try {
      setBulkLoading('enrich');
      const data = allInProject ? { project_id: filterProject } : { code_1cs: selectedIds };
      const res = await nomenklaturaAPI.bulkEnrich(data);
      success(res.data.message);
      setSelectedIds([]);
      loadNomenklatura();
    } catch (err) {
      showError("Boyitishda xatolik: " + (err.response?.data?.message || err.message));
    } finally {
      setBulkLoading(null);
    }
  };

  const handleBulkClear = async () => {
    if (selectedIds.length === 0) {
      showError("Mahsulotlarni tanlang");
      return;
    }
    if (!window.confirm(`${selectedIds.length} ta mahsulot AI ma'lumotlarini tozalashni tasdiqlaysizmi?`)) return;

    try {
      setBulkLoading('clear');
      const res = await nomenklaturaAPI.bulkClear({ code_1cs: selectedIds });
      success(res.data.message);
      setSelectedIds([]);
      loadNomenklatura();
    } catch (err) {
      showError("Tozalashda xatolik: " + (err.response?.data?.message || err.message));
    } finally {
      setBulkLoading(null);
    }
  };

  const toggleSelectAll = () => {
    if (selectedIds.length === nomenklatura.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(nomenklatura.map(i => i.code_1c));
    }
  };

  const toggleSelectOne = (code) => {
    setSelectedIds(prev => 
      prev.includes(code) ? prev.filter(id => id !== code) : [...prev, code]
    );
  };


  const handleDeleteImage = async (imageId) => {
    if (!window.confirm("Rasmni o'chirish?")) return;
    try {
      await nomenklaturaAPI.deleteImage(imageId);
      const updated = await nomenklaturaAPI.getNomenklaturaItem(editingNomenklatura.code_1c, editingNomenklatura.project?.id);
      setEditingNomenklatura(updated.data);

      success("Rasm o'chirildi");
    } catch (err) {
      showError("Rasmni o'chirib bo'lmadi");
    }
  };

  const handleSetMainImage = async (imageId) => {
    try {
      await nomenklaturaAPI.setMainImage(imageId);
      const updated = await nomenklaturaAPI.getNomenklaturaItem(editingNomenklatura.code_1c, editingNomenklatura.project?.id);
      setEditingNomenklatura(updated.data);

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
              <label>Code 1C *</label>
              <input type="text" value={formData.code_1c} onChange={(e) => setFormData({ ...formData, code_1c: e.target.value })} required className="form-input" disabled={!!editingNomenklatura} />
            </div>
            <div className="form-group">
              <label>Artikul</label>
              <input type="text" value={formData.article_code} onChange={(e) => setFormData({ ...formData, article_code: e.target.value })} className="form-input" />
            </div>
            <div className="form-group">
              <label>Name *</label>
              <input type="text" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} required className="form-input" />
            </div>
            <div className="form-group">
              <label>Title</label>
              <input type="text" value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} className="form-input" />
            </div>
            <div className="form-group full-width">
              <label>Description</label>
              <QuillEditor value={formData.description} onChange={(val) => setFormData({ ...formData, description: val })} className="quill-editor" />
            </div>
            <div className="form-group">
              <label className="checkbox-label">
                <input type="checkbox" checked={formData.is_active} onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })} />
                Faol
              </label>
            </div>
          </div>
        );
      case "specs":
        return (
          <div className="form-grid">
            <div className="form-group"><label>SKU</label><input type="text" value={formData.sku} onChange={(e) => setFormData({ ...formData, sku: e.target.value })} className="form-input" /></div>
            <div className="form-group"><label>Barcode</label><input type="text" value={formData.barcode} onChange={(e) => setFormData({ ...formData, barcode: e.target.value })} className="form-input" /></div>
            <div className="form-group"><label>Brand</label><input type="text" value={formData.brand} onChange={(e) => setFormData({ ...formData, brand: e.target.value })} className="form-input" /></div>
            <div className="form-group"><label>Ishlab chiqaruvchi</label><input type="text" value={formData.manufacturer} onChange={(e) => setFormData({ ...formData, manufacturer: e.target.value })} className="form-input" /></div>
          </div>
        );
      case "pricing":
        return (
          <div className="form-grid">
            <div className="form-group"><label>Base Price</label><input type="number" value={formData.base_price} onChange={(e) => setFormData({ ...formData, base_price: e.target.value })} className="form-input" /></div>
            <div className="form-group"><label>Sale Price</label><input type="number" value={formData.sale_price} onChange={(e) => setFormData({ ...formData, sale_price: e.target.value })} className="form-input" /></div>
            <div className="form-group"><label>Stock Qty</label><input type="number" value={formData.stock_quantity} onChange={(e) => setFormData({ ...formData, stock_quantity: e.target.value })} className="form-input" /></div>
            <div className="form-group"><label>Currency</label><input type="text" value={formData.currency} onChange={(e) => setFormData({ ...formData, currency: e.target.value })} className="form-input" /></div>
          </div>
        );
      case "cat":
        return (
          <div className="form-grid">
            <div className="form-group"><label>Category</label><input type="text" value={formData.category} onChange={(e) => setFormData({ ...formData, category: e.target.value })} className="form-input" /></div>
            <div className="form-group"><label>Subcategory</label><input type="text" value={formData.subcategory} onChange={(e) => setFormData({ ...formData, subcategory: e.target.value })} className="form-input" /></div>
          </div>
        );
      case "loyihalar":
        return (
          <div className="projects-selection-tab">
            <h4>Bog'langan loyihalar</h4>
            <div className="projects-list-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '10px', marginTop: '15px' }}>
              {projectsList.map(project => (
                <div key={project.id} className={`project-selection-item ${formData.project_ids.includes(project.id) ? 'selected' : ''}`} onClick={() => handleProjectToggle(project.id)} style={{ padding: '10px', border: '1px solid #ddd', borderRadius: '8px', cursor: 'pointer', backgroundColor: formData.project_ids.includes(project.id) ? '#e3f2fd' : 'white', borderColor: formData.project_ids.includes(project.id) ? '#2196f3' : '#ddd', display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <input type="checkbox" checked={formData.project_ids.includes(project.id)} readOnly />
                  <span>{project.name}</span>
                </div>
              ))}
              {projectsList.length === 0 && <p>Loyihalar mavjud emas</p>}
            </div>
          </div>
        );
      case "rasmlar":
        return (
          <div className="image-management-tab">
            {!editingNomenklatura ? <p>Rasmlar uchun avval saqlang.</p> : (
              <>
                <div className="image-upload-section">
                  <div className="form-grid">
                    <div className="form-group"><input type="file" multiple onChange={handleImageSelect} className="form-input" /></div>
                    <div className="form-group"><input type="text" placeholder="Category" value={imageMeta.category} onChange={(e) => setImageMeta({...imageMeta, category: e.target.value})} className="form-input" /></div>
                  </div>
                  <button type="button" onClick={handleBulkUpload} className="btn-primary" disabled={uploading || selectedImages.length === 0}>{uploading ? "Yuklanmoqda..." : `Yuklash (${selectedImages.length})`}</button>
                </div>
                <div className="image-management-grid" style={{ marginTop: '20px' }}>
                  {editingNomenklatura.images && editingNomenklatura.images.map(img => (
                    <div key={img.id} className="image-item">
                      <img src={img.image_thumbnail_url} alt="" />
                      <div className="image-item-actions">
                        {!img.is_main && <button type="button" onClick={() => handleSetMainImage(img.id)} className="btn-mini-delete" style={{ background: '#fff', color: '#f59e0b', borderColor: '#f59e0b', marginRight: '5px' }}>⭐</button>}
                        <button type="button" onClick={() => handleDeleteImage(img.id)} className="btn-mini-delete">×</button>
                      </div>
                      {img.is_main && <span className="main-badge">Asosiy</span>}
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

    const renderPageButtons = () => {
      const buttons = [];
      const showEllipsis = totalPages > 7;
      
      if (!showEllipsis) {
        for (let i = 1; i <= totalPages; i++) {
          buttons.push(
            <button key={i} onClick={() => setPage(i)} className={`page-number ${page === i ? 'active' : ''}`}>{i}</button>
          );
        }
      } else {
        // Always show first page
        buttons.push(<button key={1} onClick={() => setPage(1)} className={`page-number ${page === 1 ? 'active' : ''}`}>1</button>);
        
        if (page > 4) buttons.push(<span key="dots-1">...</span>);
        
        const start = Math.max(2, page - 2);
        const end = Math.min(totalPages - 1, page + 2);
        
        for (let i = start; i <= end; i++) {
          buttons.push(
            <button key={i} onClick={() => setPage(i)} className={`page-number ${page === i ? 'active' : ''}`}>{i}</button>
          );
        }
        
        if (page < totalPages - 3) buttons.push(<span key="dots-2">...</span>);
        
        // Always show last page
        buttons.push(<button key={totalPages} onClick={() => setPage(totalPages)} className={`page-number ${page === totalPages ? 'active' : ''}`}>{totalPages}</button>);
      }
      return buttons;
    };

    return (
      <div className="pagination" style={{ marginTop: 0, marginBottom: 20 }}>
        <div className="pagination-controls">
          <button onClick={() => setPage(page-1)} disabled={page===1} className="page-button">Oldingi</button>
          <div className="page-numbers">
            {renderPageButtons()}
          </div>
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
        <div className="header-actions">
          {selectedIds.length > 0 && (
            <div className="bulk-actions-group">
              <button 
                onClick={() => handleBulkEnrich(false)} 
                className="btn-ai enrich" 
                disabled={bulkLoading}
              >
                {bulkLoading === 'enrich' ? '...' : `🤖 Selected (${selectedIds.length})`}
              </button>
              <button 
                onClick={handleBulkClear} 
                className="btn-ai clear" 
                disabled={bulkLoading}
              >
                {bulkLoading === 'clear' ? '...' : '↺ Clear'}
              </button>
            </div>
          )}
          {filterProject && (
            <button 
              onClick={() => handleBulkEnrich(true)} 
              className="btn-ai project-enrich" 
              disabled={bulkLoading}
              title="Loyiha bo'yicha hammasini boyitish"
            >
              🚀 Project AI
            </button>
          )}
          <button onClick={handleExport} className="btn-tertiary">
            <i className="fas fa-file-export"></i> Eksport
          </button>
          <button onClick={() => setShowImportModal(true)} className="btn-tertiary">
            <i className="fas fa-file-import"></i> Import
          </button>
          <button onClick={handleTemplateDownload} className="btn-tertiary" title="Shablon">
             <i className="fas fa-download"></i>
          </button>
          <button onClick={handleCreate} className="btn-primary">+ Yangi</button>
        </div>
      </div>

      <form onSubmit={(e) => {e.preventDefault(); setPage(1);}} className="search-form">
        <div className="search-row">
          <input type="text" placeholder="Qidirish..." value={search} onChange={(e) => setSearch(e.target.value)} className="search-input" />
          <button type="submit" className="btn-primary">Qidirish</button>
          <button type="button" className="btn-tertiary" onClick={() => { 
            setSearch(""); setFilterProject(""); setStatusFilter(""); 
            setFilterCategory(""); setCreatedFrom(""); setCreatedTo(""); 
            setImageStatusFilter(""); setDescriptionStatusFilter("");
            setPage(1);
          }}>Tozalash</button>
        </div>
        <div className="filter-row">
          <div className="filter-field">
            <label>Loyiha</label>
            <select value={filterProject} onChange={(e) => { setFilterProject(e.target.value); setPage(1); }}>
              <option value="">Hammasi</option>
              {projectsList.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>
          <div className="filter-field">
            <label>Status</label>
            <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}>
              <option value="">Hammasi</option>
              <option value="true">Faol</option>
              <option value="false">Faol emas</option>
            </select>
          </div>
          <div className="filter-field"><label>Yaratilgan (dan)</label><input type="date" value={createdFrom} onChange={(e) => { setCreatedFrom(e.target.value); setPage(1); }} /></div>
          <div className="filter-field"><label>Yaratilgan (gacha)</label><input type="date" value={createdTo} onChange={(e) => { setCreatedTo(e.target.value); setPage(1); }} /></div>
          <div className="filter-field">
            <label>Rasm</label>
            <select value={imageStatusFilter} onChange={(e) => { setImageStatusFilter(e.target.value); setPage(1); }}>
              <option value="">Hammasi</option>
              <option value="with">Rasm bor</option>
              <option value="without">Rasm yo'q</option>
            </select>
          </div>
          <div className="filter-field">
            <label>Tavsif</label>
            <select value={descriptionStatusFilter} onChange={(e) => { setDescriptionStatusFilter(e.target.value); setPage(1); }}>
              <option value="">Hammasi</option>
              <option value="with">Tavsif bor</option>
              <option value="without">Tavsif yo'q</option>
            </select>
          </div>
        </div>
      </form>

      {loading ? <div className="loading"><div className="spinner"></div></div> : (
        <>
          {renderPagination()}
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: '40px' }}>
                    <input 
                      type="checkbox" 
                      onChange={toggleSelectAll} 
                      checked={nomenklatura.length > 0 && selectedIds.length === nomenklatura.length}
                    />
                  </th>
                  <th>Code / Artikul</th>
                  <th>Nomi</th>
                  <th>Loyihalar</th>
                  <th>Status</th>
                  <th>Amallar</th>
                </tr>
              </thead>
              <tbody>
                {nomenklatura.map((item) => (
                  <tr key={item.id} className={selectedIds.includes(item.code_1c) ? 'row-selected' : ''}>
                    <td>
                      <input 
                        type="checkbox" 
                        checked={selectedIds.includes(item.code_1c)}
                        onChange={() => toggleSelectOne(item.code_1c)}
                      />
                    </td>
                    <td>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        <span className="code-tag">{item.code_1c}</span>
                        {item.article_code && <span className="code-tag" style={{ backgroundColor: '#fff8e1', color: '#f57f17' }}>{item.article_code}</span>}
                        {item.enrichment_status === 'COMPLETED' && (
                          <span className="status-chip enriched mini">🤖 AI</span>
                        )}
                      </div>
                    </td>
                    <td>{item.name}</td>
                    <td>
                      <div className="project-tags">
                        {item.project ? (
                          <span className="project-tag" style={{ fontSize: '0.8rem', padding: '3px 8px', backgroundColor: item.project.is_integration ? '#e3f2fd' : '#f1f1f1', borderRadius: '4px', border: '1px solid #ddd' }}>
                            {item.project.name}
                          </span>
                        ) : (
                          <span style={{fontSize: '0.75rem', color: '#999'}}>Bog'lanmagan</span>
                        )}
                      </div>
                    </td>
                    <td><span className={`status-badge ${item.is_active ? 'active' : 'inactive'}`} onClick={() => handleToggleActive(item)} style={{cursor:'pointer'}}>{item.is_active ? "● Faol" : "○ Faol emas"}</span></td>
                    <td><div className="action-buttons"><button onClick={() => handleEdit(item)} className="btn-edit">✏️</button><button onClick={() => handleDelete(item)} className="btn-delete">🗑️</button></div></td>
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
            <div className="modal-header"><h3>{editingNomenklatura ? `Tahrirlash: ${editingNomenklatura.name}` : "Yangi"}</h3><button className="modal-close" onClick={() => setShowModal(false)}>×</button></div>
            <div className="tabs-navigation">
              <button onClick={() => setActiveTab("asosiy")} className={`tab-btn ${activeTab === "asosiy" ? "active" : ""}`}>Asosiy</button>
              <button onClick={() => setActiveTab("specs")} className={`tab-btn ${activeTab === "specs" ? "active" : ""}`}>Xususiyatlar</button>
              <button onClick={() => setActiveTab("pricing")} className={`tab-btn ${activeTab === "pricing" ? "active" : ""}`}>Narx/Ombor</button>
              <button onClick={() => setActiveTab("cat")} className={`tab-btn ${activeTab === "cat" ? "active" : ""}`}>Kategoriya</button>
              <button onClick={() => setActiveTab("loyihalar")} className={`tab-btn ${activeTab === "loyihalar" ? "active" : ""}`}>Loyihalar</button>
              <button onClick={() => setActiveTab("rasmlar")} className={`tab-btn ${activeTab === "rasmlar" ? "active" : ""}`}>Rasmlar</button>
            </div>
            <form onSubmit={handleSubmit} className="modal-form">{renderTabContent()}<div className="modal-actions"><button type="button" onClick={() => setShowModal(false)} className="btn-secondary">Bekor</button><button type="submit" className="btn-primary">Saqlash</button></div></form>
          </div>
        </div>
      )}

      {/* Import Excel Modal */}
      {showImportModal && (
        <div className="modal-overlay">
          <div className="modal-content import-modal">
            <div className="modal-header">
              <h2>Excel orqali import qilish</h2>
              <button className="close-btn" onClick={() => {
                setShowImportModal(false);
                setImportResult(null);
                setImportFile(null);
              }}>&times;</button>
            </div>
            <div className="modal-body">
              {!importResult ? (
                <form onSubmit={handleImport}>
                  <div className="form-group">
                    <label>XLSX faylni tanlang:</label>
                    <input 
                      type="file" 
                      accept=".xlsx" 
                      onChange={(e) => setImportFile(e.target.files[0])} 
                      required
                    />
                  </div>
                  {filterProject && (
                    <div className="info-box">
                      <i className="fas fa-info-circle"></i> Tanlangan loyiha ({projectsList.find(p => p.id === parseInt(filterProject))?.name}) uchun import qilinadi.
                    </div>
                  )}
                  <div className="modal-actions">
                    <button type="submit" className="save-btn" disabled={importLoading || !importFile}>
                      {importLoading ? "Yuklanmoqda..." : "Yuklashni boshlash"}
                    </button>
                    <button type="button" className="cancel-btn" onClick={() => setShowImportModal(false)}>
                      Bekor qilish
                    </button>
                  </div>
                </form>
              ) : (
                <div className="import-results">
                  <div className="stats-grid">
                    <div className="stat-card created">
                      <span className="count">{importResult.created}</span>
                      <span className="label">Yaratildi</span>
                    </div>
                    <div className="stat-card updated">
                      <span className="count">{importResult.updated}</span>
                      <span className="label">Yangilandi</span>
                    </div>
                    <div className="stat-card errors">
                      <span className="count">{importResult.errors?.length || 0}</span>
                      <span className="label">Xatoliklar</span>
                    </div>
                  </div>

                  {importResult.errors?.length > 0 && (
                    <div className="error-list">
                      <h3>Xatoliklar tafsiloti:</h3>
                      <ul>
                        {importResult.errors.slice(0, 10).map((err, i) => (
                          <li key={i}>{err}</li>
                        ))}
                        {importResult.errors.length > 10 && (
                          <li className="more-errors">...va yana {importResult.errors.length - 10} ta xatolik</li>
                        )}
                      </ul>
                    </div>
                  )}

                  <div className="modal-actions">
                    <button className="save-btn" onClick={() => {
                        setShowImportModal(false);
                        setImportResult(null);
                        setImportFile(null);
                    }}>Yopish</button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NomenklaturaAdmin;
