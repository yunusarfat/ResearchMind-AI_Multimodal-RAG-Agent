"use client";

import { initializeApp, getApps, FirebaseApp } from "firebase/app";

import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signOut as firebaseSignOut,
} from "firebase/auth";
import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useState,
  useCallback,
} from "react";
import { authApi } from "@/lib/api";
import { LoginPayload, SignupPayload, User } from "@/types/auth";
import { useRouter } from "next/navigation";




const STORAGE_KEY = "researchmind_auth";

// ---------------------------------------------------------------------------
// Firebase (Google Sign-In only — manual auth never touches Firebase)
// ---------------------------------------------------------------------------

let firebaseApp: FirebaseApp | null = null;

function getFirebaseApp(): FirebaseApp {
  if (firebaseApp) return firebaseApp;

  const config = {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  };

  if (!config.apiKey) {
    throw new Error(
      "Firebase isn't configured yet. Add NEXT_PUBLIC_FIREBASE_* values to .env.local " +
        "(see .env.local.example) to enable Google Sign-In."
    );
  }

  firebaseApp = getApps().length ? getApps()[0] : initializeApp(config);
  return firebaseApp;
}

async function signInWithGooglePopup(): Promise<string> {
  const app = getFirebaseApp();
  const auth = getAuth(app);
  
  const provider = new GoogleAuthProvider();
  const result = await signInWithPopup(auth, provider);
  return result.user.getIdToken();
}

// ---------------------------------------------------------------------------
// Auth context
// ---------------------------------------------------------------------------

interface StoredAuth {
  token: string;
  user: User;
}

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  signup: (payload: SignupPayload) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function loadStoredAuth(): StoredAuth | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as StoredAuth) : null;
  } catch {
    return null;
  }
}

function saveStoredAuth(auth: StoredAuth | null) {
  if (typeof window === "undefined") return;
  if (auth) {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(auth));
  } else {
    window.localStorage.removeItem(STORAGE_KEY);
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Rehydrate from localStorage on mount, and verify the token still
  // works (catches expired tokens instead of trusting stale storage).
  useEffect(() => {
    const stored = loadStoredAuth();
    if (!stored) {
      setIsLoading(false);
      return;
    }

    authApi
      .me(stored.token)
      .then((freshUser) => {
        setUser(freshUser);
        setToken(stored.token);
      })
      .catch(() => {
        saveStoredAuth(null);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const applyAuth = useCallback((newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
    saveStoredAuth({ token: newToken, user: newUser });
  }, []);

  const login = useCallback(
    async (payload: LoginPayload) => {
      const res = await authApi.login(payload);
      applyAuth(res.access_token, res.user);
    },
    [applyAuth]
  );

  const signup = useCallback(
    async (payload: SignupPayload) => {
      const res = await authApi.signup(payload);
      applyAuth(res.access_token, res.user);
    },
    [applyAuth]
  );

  const loginWithGoogle = useCallback(async () => {
    const idToken = await signInWithGooglePopup();
    const res = await authApi.loginWithGoogle({ id_token: idToken });
    applyAuth(res.access_token, res.user);
  }, [applyAuth]);
  const router = useRouter();
  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    saveStoredAuth(null);
    // Best-effort Firebase sign-out; irrelevant for manual accounts and
    // safe to ignore if Firebase was never initialized.
    if (firebaseApp) {
      firebaseSignOut(getAuth(firebaseApp)).catch(() => {});
    }
    router.replace("/")
  }, [router]);

  return (
    <AuthContext.Provider
      value={{ user, token, isLoading, login, signup, loginWithGoogle, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
