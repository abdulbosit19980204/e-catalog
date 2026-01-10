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
  const [activeTab, setActiveTab] = useState("asosiy");
  const [uploading, setUploading] = useState(false);
  const [editingClient, setEditingClient] = useState(null);
  
  // Filters
  const [descriptionStatus, setDescriptionStatus] = useState("");
  const [imageStatus, setImageStatus] = useState("");
  const [createdFrom, setCreatedFrom] = useState("");
  const [createdTo, setCreatedTo] = useState("");
  const [updatedFrom, setUpdatedFrom] = useState("");
  const [updatedTo, setUpdatedTo] = useState("");

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
  };

  const [formData, setFormData] = useState(initialFormData);
  const [selectedImages, setSelectedImages] = useState([]);
  const [imageMeta, setImageMeta] = useState({ category: "", note: "" });

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
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, search, descriptionStatus, imageStatus, createdFrom, createdTo, updatedFrom, updatedTo, showError]);

  useEffect(() => {
    loadClients();
  }, [loadClients]);

  const handleCreate = () => {
    setEditingClient(null);
    setFormData(initialFormData);
    setActiveTab("asosiy");
    setShowModal(true);
  };

  const handleEdit = (client) => {
    setEditingClient(client);
    setFormData({
      ...initialFormData,
      ...client,
      established_date: client.established_date || "",
    });
    setActiveTab("asosiy");
    setShowModal(true);
  };

  const handleDelete = async (clientCode1c) => {
    if (!window.confirm("Bu client'ni o'chirishni xohlaysizmi?")) return;
    try {
      await clientAPI.deleteClient(clientCode1c);
      loadClients();
      success("Client muvaffaqiyatli o'chirildi");
    } catch (err) {
      showError(err.response?.data?.detail || "O'chirishda xatolik");
    }
  };

  const handleToggleActive = async (client) => {
    try {
      await clientAPI.updateClient(client.client_code_1c, { is_active: !client.is_active });
      loadClients();
      success(`Client statusi o'zgartirildi`);
    } catch (err) {
      showError("Statusni o'zgartirib bo'lmadi");
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
      showError(err.response?.data?.detail || "Saqlashda xatolik yuz berdi");
    }
  };

  const handleImageSelect = (e) => {
    setSelectedImages(Array.from(e.target.files));
  };

  const handleBulkUpload = async () => {
    if (!editingClient || selectedImages.length === 0) return;
    try {
      setUploading(true);
      await clientAPI.bulkUploadImages(editingClient.client_code_1c, selectedImages, imageMeta);
      // Reload the client data to refresh images tab
      const updated = await clientAPI.getClient(editingClient.client_code_1c);
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

  const handleDeleteImage = async (imageId) => {
    if (!window.confirm("Bu rasmni o'chirishni xohlaysizmi?")) return;
    try {
      await clientAPI.deleteClientImage(imageId);
      const updated = await clientAPI.getClient(editingClient.client_code_1c);
      setEditingClient(updated.data);
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
              <input
                type="text"
                value={formData.currency}
                onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                className="form-input"
              />
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

  return (
    <div className="admin-crud">
      <div className="crud-header">
        <h2>👥 Clients</h2>
        <button onClick={handleCreate} className="btn-primary">
          <span>+</span> Yangi Client
        </button>
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
          <button type="button" className="btn-tertiary" onClick={() => {setSearch(""); setPage(1); loadClients();}}>🔄 Tozalash</button>
        </div>
      </form>

      {error && <div className="error-message"><p>{error}</p></div>}

      {loading ? (
        <div className="loading"><div className="spinner"></div><p>Yuklanmoqda...</p></div>
      ) : (
        <>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Code 1C</th>
                  <th>Name</th>
                  <th>Email / Phone</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {clients.length === 0 ? (
                  <tr><td colSpan="5" className="no-data">Ma'lumot topilmadi</td></tr>
                ) : (
                  clients.map((client) => (
                    <tr key={client.id}>
                      <td><span className="code-tag">{client.client_code_1c}</span></td>
                      <td><strong>{client.name}</strong></td>
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
                          <button onClick={() => handleDelete(client.client_code_1c)} className="btn-delete" title="O'chirish">🗑️</button>
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
          )}
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
