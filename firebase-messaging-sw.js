// Firebase Cloud Messaging Service Worker
importScripts('https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.22.2/firebase-messaging-compat.js');

// Initialize Firebase in service worker
const firebaseConfig = {
  apiKey: "AIzaSyC_ggfoy4_1FoF1mlgxw2Y6NGZVdvKyHEA",
  authDomain: "eye-61167.firebaseapp.com",
  projectId: "eye-61167",
  storageBucket: "eye-61167.appspot.com",
  messagingSenderId: "1087072838592",
  appId: "1:1087072838592:web:76ae2a4d93695277665e25",
  measurementId: "G-QY2DS5YY23"
};

firebase.initializeApp(firebaseConfig);

// Initialize Firebase Messaging
const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  console.log('Background message received:', payload);
  
  const notificationTitle = payload.notification?.title || 'SecureEye Alert';
  const notificationOptions = {
    body: payload.notification?.body || 'Security alert detected',
    icon: '/IMAGES/logo.png',
    badge: '/IMAGES/logo.png',
    tag: payload.data?.detectionType || 'secureeye-alert',
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
    ],
    data: payload.data
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification click
self.addEventListener('notificationclick', (event) => {
  console.log('Notification clicked:', event);
  
  event.notification.close();
  
  if (event.action === 'view') {
    // Open the app and focus on the specific camera
    event.waitUntil(
      clients.openWindow('/home.html')
    );
  } else if (event.action === 'dismiss') {
    // Just close the notification
    event.notification.close();
  } else {
    // Default action - open the app
    event.waitUntil(
      clients.openWindow('/home.html')
    );
  }
});

// Handle notification close
self.addEventListener('notificationclose', (event) => {
  console.log('Notification closed:', event);
});

