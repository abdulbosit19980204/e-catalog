import { useState, useCallback } from 'react';

export const useConfirm = () => {
  const [confirmState, setConfirmState] = useState({
    isOpen: false,
    title: '',
    message: '',
    onConfirm: () => {},
    type: 'danger',
  });

  const confirm = useCallback(({ title, message, onConfirm, type = 'danger' }) => {
    return new Promise((resolve) => {
      setConfirmState({
        isOpen: true,
        title,
        message,
        onConfirm: () => {
          onConfirm?.();
          resolve(true);
          setConfirmState(prev => ({ ...prev, isOpen: false }));
        },
        onCancel: () => {
          resolve(false);
          setConfirmState(prev => ({ ...prev, isOpen: false }));
        },
        type,
      });
    });
  }, []);

  const closeConfirm = useCallback(() => {
    setConfirmState(prev => ({ ...prev, isOpen: false }));
  }, []);

  return {
    confirmState,
    confirm,
    closeConfirm,
  };
};
