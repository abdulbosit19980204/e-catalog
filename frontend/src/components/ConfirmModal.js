import React from 'react';
import { useNotification } from '../contexts/NotificationContext';
import './ConfirmModal.css';

const ConfirmModal = () => {
    const { confirmState } = useNotification();

    if (!confirmState) return null;

    const { title, message, resolve, type = 'danger' } = confirmState;

    return (
        <div className="confirm-overlay" onClick={() => resolve(false)}>
            <div className="confirm-modal card" onClick={e => e.stopPropagation()}>
                <div className={`confirm-icon-wrapper ${type}`}>
                    {type === 'danger' ? '⚠️' : '❓'}
                </div>
                <h3>{title || 'Tasdiqlash'}</h3>
                <p>{message || "Haqiqatan ham ushbu amalni bajarishni xohlaysizmi?"}</p>
                
                <div className="confirm-actions">
                    <button 
                        className="btn-secondary" 
                        onClick={() => resolve(false)}
                    >
                        Bekor qilish
                    </button>
                    <button 
                        className={`btn-primary ${type === 'danger' ? 'btn-danger' : ''}`}
                        onClick={() => resolve(true)}
                    >
                        Tasdiqlash
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ConfirmModal;
