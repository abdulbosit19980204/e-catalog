import React, { useState, useEffect, useCallback } from "react";
import { userAPI } from "../../api";
import { useNotification } from "../../contexts/NotificationContext";
import "./UserAdmin.css";

const UserAdmin = () => {
  const { error: showError, success: showSuccess } = useNotification();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    username: "",
    first_name: "",
    last_name: "",
    email: "",
    is_staff: false,
    is_active: true
  });

  const loadUsers = useCallback(async () => {
    try {
      setLoading(true);
      const response = await userAPI.getUsers();
      setUsers(response.data.results || response.data);
    } catch (err) {
      showError("Foydalanuvchilarni yuklab bo'lmadi");
    } finally {
      setLoading(false);
    }
  }, [showError]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const handleEdit = (user) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      first_name: user.first_name || "",
      last_name: user.last_name || "",
      email: user.email || "",
      is_staff: user.is_staff,
      is_active: user.is_active
    });
    setShowModal(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      if (editingUser) {
        await userAPI.updateUser(editingUser.id, formData);
        showSuccess("Foydalanuvchi yangilandi");
      } else {
        await userAPI.createUser(formData);
        showSuccess("Foydalanuvchi yaratildi");
      }
      setShowModal(false);
      loadUsers();
    } catch (err) {
      showError("Saqlashda xatolik yuz berdi");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("O'chirmoqchimisiz?")) return;
    try {
      await userAPI.deleteUser(id);
      showSuccess("O'chirildi");
      loadUsers();
    } catch (err) {
      showError("O'chirishda xatolik");
    }
  };

  if (loading && users.length === 0) {
    return (
      <div className="admin-loading">
        <div className="spinner"></div>
        <p>Foydalanuvchilar yuklanmoqda...</p>
      </div>
    );
  }

  return (
    <div className="user-admin">
      <div className="admin-header">
        <h2>Foydalanuvchilar Boshqaruvi</h2>
        <button onClick={() => { setEditingUser(null); setFormData({ username: "", first_name: "", last_name: "", email: "", is_staff: false, is_active: true }); setShowModal(true); }} className="btn-add">
          Yangi Foydalanuvchi
        </button>
      </div>

      <div className="user-table-container">
        <table className="user-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Username</th>
              <th>F.I.SH</th>
              <th>Role</th>
              <th>Status</th>
              <th>Amallar</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.username}</td>
                <td>{user.first_name} {user.last_name}</td>
                <td>{user.is_staff ? "Admin" : "User"}</td>
                <td>
                  <span className={`status-pill ${user.is_active ? 'active' : 'inactive'}`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td>
                  <button onClick={() => handleEdit(user)} className="btn-edit">Tahrirlash</button>
                  <button onClick={() => handleDelete(user.id)} className="btn-delete">O'chirish</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="user-modal-overlay">
          <div className="user-modal-content">
            <h3>{editingUser ? "Tahrirlash" : "Yangi Foydalanuvchi"}</h3>
            <form onSubmit={handleSave}>
              <div className="form-group">
                <label>Username</label>
                <input 
                  type="text" 
                  value={formData.username} 
                  onChange={e => setFormData({...formData, username: e.target.value})}
                  disabled={editingUser}
                  required
                />
              </div>
              <div className="form-group">
                <label>Ism</label>
                <input 
                  type="text" 
                  value={formData.first_name} 
                  onChange={e => setFormData({...formData, first_name: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Staff Role</label>
                <input 
                  type="checkbox" 
                  checked={formData.is_staff} 
                  onChange={e => setFormData({...formData, is_staff: e.target.checked})}
                /> Admin huquqi
              </div>
              <div className="user-modal-actions">
                <button type="button" onClick={() => setShowModal(false)}>Bekor qilish</button>
                <button type="submit" className="btn-primary">Saqlash</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserAdmin;
