// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-analytics.js";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyC_ggfoy4_1FoF1mlgxw2Y6NGZVdvKyHEA",
  authDomain: "eye-61167.firebaseapp.com",
  projectId: "eye-61167",
  storageBucket: "eye-61167.appspot.com",
  messagingSenderId: "1087072838592",
  appId: "1:1087072838592:web:76ae2a4d93695277665e25",
  measurementId: "G-QY2DS5YY23"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
// Export app for use in other scripts if needed
export { app }; 