import React from 'react';
import { useNotification } from '../contexts/NotificationContext';
import './Notification.css';

const Notification = () => {
  const { notifications, removeNotification, setErrorDetail } = useNotification();

  const getIcon = (type) => {
    switch (type) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
      default: return 'ℹ️';
    }
  };

  return (
    <div className="notification-container">
      {notifications.map((n) => {
        const isLong = n.message && n.message.length > 120;
        const displayMessage = isLong 
          ? n.message.substring(0, 120) + "..." 
          : n.message;

        return (
          <div
            key={n.id}
            className={`notification notification-${n.type}`}
          >
            <div className="notification-content">
              <span className="notification-icon">{getIcon(n.type)}</span>
              <div className="notification-body">
                <span className="notification-message">{displayMessage}</span>
                {n.type === 'error' && (
                  <div className="notification-actions">
                    <button 
                      className="btn-details" 
                      onClick={() => setErrorDetail(n.message)}
                    >
                      🔍 Batafsil o'qish
                    </button>
                  </div>
                )}
              </div>
              <button
                className="notification-close"
                onClick={() => removeNotification(n.id)}
              >
                ×
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default Notification;

