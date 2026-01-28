import React from 'react';
import { useNotification } from '../contexts/NotificationContext';
import './ErrorDetailModal.css';

const ErrorDetailModal = () => {
    const { errorDetail, setErrorDetail } = useNotification();

    if (!errorDetail) return null;

    const handleCopy = () => {
        navigator.clipboard.writeText(errorDetail);
        alert("Xatolik xabari nusxalandi!");
    };

    return (
        <div className="error-modal-overlay" onClick={() => setErrorDetail(null)}>
            <div className="error-modal card" onClick={e => e.stopPropagation()}>
                <div className="error-modal-header">
                    <div className="error-title-wrapper">
                        <span className="error-icon">⚠️</span>
                        <h3>Xatolik Tafsilotlari</h3>
                    </div>
                    <button className="close-btn" onClick={() => setErrorDetail(null)}>&times;</button>
                </div>
                
                <div className="error-modal-body">
                    <div className="error-content-box">
                        <pre>{errorDetail}</pre>
                    </div>
                </div>

                <div className="error-modal-footer">
                    <button className="btn-secondary" onClick={handleCopy}>
                        📋 Nusxa olish
                    </button>
                    <button className="btn-primary" onClick={() => setErrorDetail(null)}>
                        Yopish
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ErrorDetailModal;
