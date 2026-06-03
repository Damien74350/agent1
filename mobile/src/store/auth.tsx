/** Auth context: persists the bearer token in SecureStore and exposes
 * login/logout + the current user across the app. */
import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import * as SecureStore from 'expo-secure-store';
import { api, setToken, PublicUser } from '@/api/client';

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
        const saved = await SecureStore.getItemAsync(TOKEN_KEY);
        if (saved) {
          setToken(saved);
          setTok(saved);
          try {
            const { user } = await api.me();
            setUser(user);
          } catch {
            // token invalid/expired — clear it
            await SecureStore.deleteItemAsync(TOKEN_KEY);
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
    await SecureStore.setItemAsync(TOKEN_KEY, newToken);
    setToken(newToken);
    setTok(newToken);
    setUser(newUser);
  }, []);

  const signOut = useCallback(async () => {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    setToken(null);
    setTok(null);
    setUser(null);
  }, []);

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
