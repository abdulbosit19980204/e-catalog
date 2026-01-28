import React, { createContext, useContext, useState, useCallback } from 'react';

const NotificationContext = createContext();

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within NotificationProvider');
  }
  return context;
};

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
  const [history, setHistory] = useState([]);
  const [confirmState, setConfirmState] = useState(null);
  const [errorDetail, setErrorDetail] = useState(null);

  const removeNotification = useCallback((id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const showNotification = useCallback((message, type = 'info', duration = 5000) => {
    const id = Date.now() + Math.random();
    const notification = {
      id,
      message,
      type,
      duration,
      timestamp: new Date(),
    };

    setNotifications((prev) => [...prev, notification]);
    setHistory((prev) => [notification, ...prev].slice(0, 50));

    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, duration);
    }

    return id;
  }, [removeNotification]);

  const confirm = useCallback((config) => {
    return new Promise((resolve) => {
      setConfirmState({
        ...config,
        resolve: (v) => {
          setConfirmState(null);
          resolve(v);
        }
      });
    });
  }, []);

  const success = useCallback((message, duration) => {
    return showNotification(message, 'success', duration);
  }, [showNotification]);

  const error = useCallback((message, duration) => {
    return showNotification(message, 'error', duration);
  }, [showNotification]);

  const warning = useCallback((message, duration) => {
    return showNotification(message, 'warning', duration);
  }, [showNotification]);

  const info = useCallback((message, duration) => {
    return showNotification(message, 'info', duration);
  }, [showNotification]);

  const clearHistory = useCallback(() => setHistory([]), []);

  const value = {
    notifications,
    history,
    confirmState,
    confirm,
    showNotification,
    removeNotification,
    success,
    error,
    warning,
    info,
    clearHistory,
    errorDetail,
    setErrorDetail
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};
