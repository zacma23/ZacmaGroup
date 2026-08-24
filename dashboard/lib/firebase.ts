/**
 * Firebase Client SDK Helper & Authentication Utilities.
 * 
 * Safely initializes Firebase client when NEXT_PUBLIC_FIREBASE_* environment variables are set.
 * In development or when unconfigured, gracefully falls back without breaking existing native login.
 */

export interface FirebaseClientConfig {
  apiKey?: string;
  authDomain?: string;
  projectId?: string;
  storageBucket?: string;
  messagingSenderId?: string;
  appId?: string;
}

export const firebaseConfig: FirebaseClientConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "zacma-platform",
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "",
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "",
};

export const isFirebaseConfigured = (): boolean => {
  return Boolean(firebaseConfig.apiKey && firebaseConfig.projectId);
};

/**
 * Exchange a Firebase ID token with the ZACMA backend for a synchronized session.
 */
export async function authenticateWithFirebaseIdToken(idToken: string, apiBaseUrl: string = "http://127.0.0.1:8000"): Promise<any> {
  const response = await fetch(`${apiBaseUrl}/api/v1/auth/session`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${idToken}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Firebase token exchange failed: ${response.statusText}`);
  }

  return response.json();
}
