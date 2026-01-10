import React from 'react';
import './ConfirmDialog.css';

const ConfirmDialog = ({ isOpen, title, message, onConfirm, onCancel, confirmText = "Tasdiqlash", cancelText = "Bekor qilish", type = "danger" }) => {
  if (!isOpen) return null;

  return (
    <div className="confirm-overlay" onClick={onCancel}>
      <div className="confirm-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="confirm-header">
          <div className={`confirm-icon confirm-icon-${type}`}>
            {type === 'danger' ? '⚠️' : type === 'warning' ? '⚠' : 'ℹ️'}
          </div>
          <h3>{title}</h3>
        </div>
        <div className="confirm-body">
          <p>{message}</p>
        </div>
        <div className="confirm-actions">
          <button className="btn-confirm-cancel" onClick={onCancel}>
            {cancelText}
          </button>
          <button className={`btn-confirm-ok btn-confirm-${type}`} onClick={onConfirm}>
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDialog;
