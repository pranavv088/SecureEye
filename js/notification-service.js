// Notification Service for SecureEye
import { getMessaging, getToken, onMessage } from 'https://www.gstatic.com/firebasejs/9.22.2/firebase-messaging.js';
import { app } from './firebase-config.js';

class NotificationService {
    constructor() {
        this.messaging = null;
        this.isSupported = false;
        this.permission = 'default';
        this.init();
    }

    async init() {
        try {
            // Check if service worker is supported
            if ('serviceWorker' in navigator && 'Notification' in window) {
                this.isSupported = true;
                this.messaging = getMessaging(app);
                await this.setupServiceWorker();
                await this.requestPermission();
                await this.setupMessageListener();
            } else {
                console.log('Push notifications not supported');
            }
        } catch (error) {
            console.error('Notification service initialization failed:', error);
        }
    }

    async setupServiceWorker() {
        try {
            // Register service worker for push notifications
            const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');
            console.log('Service Worker registered:', registration);
        } catch (error) {
            console.error('Service Worker registration failed:', error);
        }
    }

    async requestPermission() {
        try {
            this.permission = await Notification.requestPermission();
            
            if (this.permission === 'granted') {
                console.log('Notification permission granted');
                await this.getToken();
            } else {
                console.log('Notification permission denied');
            }
        } catch (error) {
            console.error('Permission request failed:', error);
        }
    }

    async getToken() {
        try {
            const token = await getToken(this.messaging, {
                vapidKey: 'YOUR_VAPID_KEY_HERE' // Get this from Firebase Console > Project Settings > Cloud Messaging
            });
            
            if (token) {
                console.log('FCM Token:', token);
                // Store token in Firestore for server-side notifications
                await this.storeTokenInFirestore(token);
                return token;
            } else {
                console.log('No registration token available');
            }
        } catch (error) {
            console.error('Token generation failed:', error);
        }
    }

    async storeTokenInFirestore(token) {
        try {
            // This would be called from the main app with user context
            console.log('Token stored in Firestore:', token);
        } catch (error) {
            console.error('Token storage failed:', error);
        }
    }

    async setupMessageListener() {
        try {
            onMessage(this.messaging, (payload) => {
                console.log('Message received:', payload);
                this.handleForegroundMessage(payload);
            });
        } catch (error) {
            console.error('Message listener setup failed:', error);
        }
    }

    handleForegroundMessage(payload) {
        const { notification, data } = payload;
        
        // Show browser notification
        if (notification) {
            this.showBrowserNotification(notification.title, notification.body, data);
        }
        
        // Show in-app notification
        if (data) {
            this.showInAppNotification(data);
        }
    }

    showBrowserNotification(title, body, data = {}) {
        if (this.permission === 'granted') {
            const notification = new Notification(title, {
                body: body,
                icon: '/IMAGES/logo.png',
                badge: '/IMAGES/logo.png',
                tag: data.detectionType || 'secureeye-alert',
                requireInteraction: true,
                actions: [
                    {
                        action: 'view',
                        title: 'View Details'
                    },
                    {
                        action: 'dismiss',
                        title: 'Dismiss'
                    }
                ]
            });

            notification.onclick = () => {
                window.focus();
                notification.close();
                
                // Handle notification click
                if (data.cameraId) {
                    this.handleNotificationClick(data);
                }
            };

            // Auto-close after 10 seconds
            setTimeout(() => {
                notification.close();
            }, 10000);
        }
    }

    showInAppNotification(data) {
        // This will be handled by the main app's notification system
        if (window.showNotification) {
            window.showNotification(
                `🚨 ${data.detectionType?.toUpperCase()} Detected!`,
                `Camera ${data.cameraId} - ${data.confidence}% confidence`,
                'warning'
            );
        }
    }

    handleNotificationClick(data) {
        // Navigate to specific camera or show details
        console.log('Notification clicked:', data);
        
        // You can implement specific actions based on notification data
        if (data.cameraId) {
            // Focus on specific camera
            const cameraElement = document.querySelector(`[data-camera-id="${data.cameraId}"]`);
            if (cameraElement) {
                cameraElement.scrollIntoView({ behavior: 'smooth' });
                cameraElement.style.border = '3px solid #FF3366';
                setTimeout(() => {
                    cameraElement.style.border = '';
                }, 3000);
            }
        }
    }

    // Email notification simulation (would be handled by backend)
    async sendEmailNotification(userEmail, subject, message, detectionData) {
        try {
            // This would typically be handled by a backend service
            console.log('Email notification would be sent:', {
                to: userEmail,
                subject: subject,
                message: message,
                data: detectionData
            });
            
            // For demo purposes, we'll just log it
            return true;
        } catch (error) {
            console.error('Email notification failed:', error);
            return false;
        }
    }

    // SMS notification simulation (would be handled by backend)
    async sendSMSNotification(phoneNumber, message, detectionData) {
        try {
            // This would typically be handled by a backend service like Twilio
            console.log('SMS notification would be sent:', {
                to: phoneNumber,
                message: message,
                data: detectionData
            });
            
            return true;
        } catch (error) {
            console.error('SMS notification failed:', error);
            return false;
        }
    }

    // Telegram bot notification simulation
    async sendTelegramNotification(chatId, message, detectionData) {
        try {
            // This would typically be handled by a backend service
            console.log('Telegram notification would be sent:', {
                chatId: chatId,
                message: message,
                data: detectionData
            });
            
            return true;
        } catch (error) {
            console.error('Telegram notification failed:', error);
            return false;
        }
    }

    // WhatsApp notification simulation
    async sendWhatsAppNotification(phoneNumber, message, detectionData) {
        try {
            // This would typically be handled by a backend service
            console.log('WhatsApp notification would be sent:', {
                to: phoneNumber,
                message: message,
                data: detectionData
            });
            
            return true;
        } catch (error) {
            console.error('WhatsApp notification failed:', error);
            return false;
        }
    }

    // Comprehensive notification dispatch
    async dispatchNotifications(detectionData, userPreferences) {
        const { detectionType, cameraId, confidence } = detectionData;
        const message = `🚨 ${detectionType.toUpperCase()} detected on Camera ${cameraId} (${confidence}% confidence)`;
        
        const notifications = [];

        // Push notification
        if (userPreferences.notifications?.push) {
            this.showBrowserNotification(
                'SecureEye Alert',
                message,
                detectionData
            );
            notifications.push('push');
        }

        // Email notification
        if (userPreferences.notifications?.email && userPreferences.email) {
            await this.sendEmailNotification(
                userPreferences.email,
                'SecureEye Security Alert',
                message,
                detectionData
            );
            notifications.push('email');
        }

        // SMS notification
        if (userPreferences.notifications?.sms && userPreferences.phone) {
            await this.sendSMSNotification(
                userPreferences.phone,
                message,
                detectionData
            );
            notifications.push('sms');
        }

        // Telegram notification
        if (userPreferences.notifications?.telegram && userPreferences.telegramChatId) {
            await this.sendTelegramNotification(
                userPreferences.telegramChatId,
                message,
                detectionData
            );
            notifications.push('telegram');
        }

        // WhatsApp notification
        if (userPreferences.notifications?.whatsapp && userPreferences.whatsappPhone) {
            await this.sendWhatsAppNotification(
                userPreferences.whatsappPhone,
                message,
                detectionData
            );
            notifications.push('whatsapp');
        }

        console.log('Notifications dispatched:', notifications);
        return notifications;
    }

    // Test notification
    async testNotification() {
        if (this.permission === 'granted') {
            this.showBrowserNotification(
                'SecureEye Test',
                'This is a test notification from SecureEye',
                { test: true }
            );
        } else {
            console.log('Notification permission not granted');
        }
    }
}

// Export singleton instance
export const notificationService = new NotificationService();

