// Firestore Database Service for SecureEye
import { 
    getFirestore, 
    collection, 
    addDoc, 
    getDocs, 
    query, 
    orderBy, 
    limit, 
    where,
    onSnapshot,
    serverTimestamp,
    doc,
    setDoc,
    getDoc,
    updateDoc,
    deleteDoc
} from 'https://www.gstatic.com/firebasejs/9.22.2/firebase-firestore.js';
import { app } from './firebase-config.js';

const db = getFirestore(app);

class FirestoreService {
    constructor() {
        this.db = db;
    }

    // Detection Events Management
    async addDetectionEvent(cameraId, detectionType, confidence, userId, metadata = {}) {
        try {
            const docRef = await addDoc(collection(this.db, 'detections'), {
                cameraId: cameraId,
                detectionType: detectionType,
                confidence: confidence,
                userId: userId,
                timestamp: serverTimestamp(),
                processed: true,
                acknowledged: false,
                metadata: metadata
            });
            return docRef.id;
        } catch (error) {
            console.error('Error adding detection event:', error);
            throw error;
        }
    }

    async getDetectionEvents(userId, limitCount = 50) {
        try {
            const q = query(
                collection(this.db, 'detections'),
                where('userId', '==', userId),
                orderBy('timestamp', 'desc'),
                limit(limitCount)
            );
            const querySnapshot = await getDocs(q);
            return querySnapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data()
            }));
        } catch (error) {
            console.error('Error getting detection events:', error);
            throw error;
        }
    }

    async subscribeToDetectionEvents(userId, callback) {
        try {
            const q = query(
                collection(this.db, 'detections'),
                where('userId', '==', userId),
                orderBy('timestamp', 'desc'),
                limit(20)
            );
            
            return onSnapshot(q, (querySnapshot) => {
                const events = querySnapshot.docs.map(doc => ({
                    id: doc.id,
                    ...doc.data()
                }));
                callback(events);
            });
        } catch (error) {
            console.error('Error subscribing to detection events:', error);
            throw error;
        }
    }

    // Camera Configuration Management
    async saveCameraConfig(cameraId, config, userId) {
        try {
            const docRef = doc(this.db, 'cameras', cameraId);
            await setDoc(docRef, {
                ...config,
                userId: userId,
                createdAt: serverTimestamp(),
                updatedAt: serverTimestamp(),
                active: true
            });
            return docRef.id;
        } catch (error) {
            console.error('Error saving camera config:', error);
            throw error;
        }
    }

    async getCameraConfig(cameraId) {
        try {
            const docRef = doc(this.db, 'cameras', cameraId);
            const docSnap = await getDoc(docRef);
            
            if (docSnap.exists()) {
                return { id: docSnap.id, ...docSnap.data() };
            } else {
                return null;
            }
        } catch (error) {
            console.error('Error getting camera config:', error);
            throw error;
        }
    }

    async getUserCameras(userId) {
        try {
            const q = query(
                collection(this.db, 'cameras'),
                where('userId', '==', userId),
                where('active', '==', true)
            );
            const querySnapshot = await getDocs(q);
            return querySnapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data()
            }));
        } catch (error) {
            console.error('Error getting user cameras:', error);
            throw error;
        }
    }

    async updateCameraConfig(cameraId, updates) {
        try {
            const docRef = doc(this.db, 'cameras', cameraId);
            await updateDoc(docRef, {
                ...updates,
                updatedAt: serverTimestamp()
            });
        } catch (error) {
            console.error('Error updating camera config:', error);
            throw error;
        }
    }

    async deleteCamera(cameraId) {
        try {
            const docRef = doc(this.db, 'cameras', cameraId);
            await updateDoc(docRef, {
                active: false,
                deletedAt: serverTimestamp()
            });
        } catch (error) {
            console.error('Error deleting camera:', error);
            throw error;
        }
    }

    // User Preferences Management
    async saveUserPreferences(userId, preferences) {
        try {
            const docRef = doc(this.db, 'userPreferences', userId);
            await setDoc(docRef, {
                ...preferences,
                updatedAt: serverTimestamp()
            }, { merge: true });
        } catch (error) {
            console.error('Error saving user preferences:', error);
            throw error;
        }
    }

    async getUserPreferences(userId) {
        try {
            const docRef = doc(this.db, 'userPreferences', userId);
            const docSnap = await getDoc(docRef);
            
            if (docSnap.exists()) {
                return docSnap.data();
            } else {
                // Return default preferences
                return {
                    notifications: {
                        email: true,
                        push: true,
                        sound: true
                    },
                    detectionSettings: {
                        fireThreshold: 0.7,
                        motionThreshold: 500,
                        violenceThreshold: 0.1,
                        crowdThreshold: 0.15
                    },
                    uiSettings: {
                        theme: 'light',
                        autoRefresh: true,
                        showLogs: true
                    }
                };
            }
        } catch (error) {
            console.error('Error getting user preferences:', error);
            throw error;
        }
    }

    // Alert Management
    async acknowledgeAlert(detectionId) {
        try {
            const docRef = doc(this.db, 'detections', detectionId);
            await updateDoc(docRef, {
                acknowledged: true,
                acknowledgedAt: serverTimestamp()
            });
        } catch (error) {
            console.error('Error acknowledging alert:', error);
            throw error;
        }
    }

    async getUnacknowledgedAlerts(userId) {
        try {
            const q = query(
                collection(this.db, 'detections'),
                where('userId', '==', userId),
                where('acknowledged', '==', false),
                orderBy('timestamp', 'desc')
            );
            const querySnapshot = await getDocs(q);
            return querySnapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data()
            }));
        } catch (error) {
            console.error('Error getting unacknowledged alerts:', error);
            throw error;
        }
    }

    // Analytics and Reporting
    async getDetectionStats(userId, startDate, endDate) {
        try {
            const q = query(
                collection(this.db, 'detections'),
                where('userId', '==', userId),
                where('timestamp', '>=', startDate),
                where('timestamp', '<=', endDate)
            );
            const querySnapshot = await getDocs(q);
            
            const stats = {
                total: querySnapshot.docs.length,
                byType: {},
                byCamera: {},
                byDate: {}
            };
            
            querySnapshot.docs.forEach(doc => {
                const data = doc.data();
                const type = data.detectionType;
                const cameraId = data.cameraId;
                const date = data.timestamp.toDate().toDateString();
                
                // Count by type
                stats.byType[type] = (stats.byType[type] || 0) + 1;
                
                // Count by camera
                stats.byCamera[cameraId] = (stats.byCamera[cameraId] || 0) + 1;
                
                // Count by date
                stats.byDate[date] = (stats.byDate[date] || 0) + 1;
            });
            
            return stats;
        } catch (error) {
            console.error('Error getting detection stats:', error);
            throw error;
        }
    }

    // System Logs
    async addSystemLog(level, message, userId, metadata = {}) {
        try {
            await addDoc(collection(this.db, 'systemLogs'), {
                level: level, // 'info', 'warning', 'error', 'success'
                message: message,
                userId: userId,
                timestamp: serverTimestamp(),
                metadata: metadata
            });
        } catch (error) {
            console.error('Error adding system log:', error);
            throw error;
        }
    }

    async getSystemLogs(userId, limitCount = 100) {
        try {
            const q = query(
                collection(this.db, 'systemLogs'),
                where('userId', '==', userId),
                orderBy('timestamp', 'desc'),
                limit(limitCount)
            );
            const querySnapshot = await getDocs(q);
            return querySnapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data()
            }));
        } catch (error) {
            console.error('Error getting system logs:', error);
            throw error;
        }
    }
}

// Export singleton instance
export const firestoreService = new FirestoreService();

