/**
 * Notification Service - Sistema de notificações toast
 */

type NotificationType = 'success' | 'error' | 'warning' | 'info';

interface Notification {
  id: string;
  message: string;
  type: NotificationType;
  duration: number;
}

let notifications: Notification[] = [];
let listeners: Array<(notifications: Notification[]) => void> = [];

const notify = (message: string, type: NotificationType = 'info', duration: number = 3000) => {
  const id = `notif-${Date.now()}-${Math.random()}`;
  const notification: Notification = { id, message, type, duration };

  notifications = [...notifications, notification];
  emitChange();

  // Auto-remove após duration
  setTimeout(() => {
    removeNotification(id);
  }, duration);
};

const removeNotification = (id: string) => {
  notifications = notifications.filter(n => n.id !== id);
  emitChange();
};

const emitChange = () => {
  listeners.forEach(listener => listener(notifications));
};

export const showNotification = (message: string, type: NotificationType = 'info') => {
  notify(message, type);
};

export const subscribeToNotifications = (listener: (notifications: Notification[]) => void) => {
  listeners.push(listener);
  return () => {
    listeners = listeners.filter(l => l !== listener);
  };
};

export const getNotifications = () => notifications;

// Helpers específicos
export const showSuccess = (message: string) => showNotification(message, 'success');
export const showError = (message: string) => showNotification(message, 'error');
export const showWarning = (message: string) => showNotification(message, 'warning');
export const showInfo = (message: string) => showNotification(message, 'info');

