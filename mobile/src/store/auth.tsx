/** Auth context: persists the bearer token across native (SecureStore) and
 * web (localStorage), exposes login/logout + the current user app-wide. */
import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { api, setToken, setUnauthorizedHandler, PublicUser } from '@/api/client';
import { showToast } from '@/components/Toast';
import { storage } from '@/store/storage';

const TOKEN_KEY = 'calo.token';

type AuthState = {
  ready: boolean;
  token: string | null;
  user: PublicUser | null;
  signIn: (token: string, user: PublicUser) => Promise<void>;
  signOut: () => Promise<void>;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [ready, setReady] = useState(false);
  const [token, setTok] = useState<string | null>(null);
  const [user, setUser] = useState<PublicUser | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const saved = await storage.getItemAsync(TOKEN_KEY);
        if (saved) {
          setToken(saved);
          setTok(saved);
          try {
            const { user } = await api.me();
            setUser(user);
          } catch {
            // token invalid/expired — clear it
            await storage.deleteItemAsync(TOKEN_KEY);
            setToken(null);
            setTok(null);
          }
        }
      } finally {
        setReady(true);
      }
    })();
  }, []);

  const signIn = useCallback(async (newToken: string, newUser: PublicUser) => {
    await storage.setItemAsync(TOKEN_KEY, newToken);
    setToken(newToken);
    setTok(newToken);
    setUser(newUser);
  }, []);

  const signOut = useCallback(async () => {
    await storage.deleteItemAsync(TOKEN_KEY);
    setToken(null);
    setTok(null);
    setUser(null);
  }, []);

  // Auto-sign-out if the backend ever returns 401 (token expired/revoked).
  useEffect(() => {
    setUnauthorizedHandler(() => {
      showToast('Session expirée, reconnecte-toi 🙂');
      void signOut();
    });
    return () => setUnauthorizedHandler(null);
  }, [signOut]);

  const refreshUser = useCallback(async () => {
    try {
      const { user } = await api.me();
      setUser(user);
    } catch {}
  }, []);

  return (
    <AuthContext.Provider value={{ ready, token, user, signIn, signOut, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
