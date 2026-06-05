/** Cross-platform secure-ish storage.
 *
 * - iOS/Android → expo-secure-store (Keychain / Keystore).
 * - Web        → localStorage fallback (not 'secure', but acceptable for the
 *                dev/preview flow ; production web tokens should move to
 *                httpOnly cookies anyway).
 */
import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

const memoryStore = new Map<string, string>();

function webGet(key: string): string | null {
  try {
    return globalThis.localStorage?.getItem(key) ?? memoryStore.get(key) ?? null;
  } catch {
    return memoryStore.get(key) ?? null;
  }
}

function webSet(key: string, value: string) {
  try {
    globalThis.localStorage?.setItem(key, value);
  } catch {
    memoryStore.set(key, value);
  }
}

function webDel(key: string) {
  try {
    globalThis.localStorage?.removeItem(key);
  } catch {
    memoryStore.delete(key);
  }
}

export const storage = {
  async getItemAsync(key: string): Promise<string | null> {
    if (Platform.OS === 'web') return webGet(key);
    return SecureStore.getItemAsync(key);
  },
  async setItemAsync(key: string, value: string): Promise<void> {
    if (Platform.OS === 'web') return webSet(key, value);
    return SecureStore.setItemAsync(key, value);
  },
  async deleteItemAsync(key: string): Promise<void> {
    if (Platform.OS === 'web') return webDel(key);
    return SecureStore.deleteItemAsync(key);
  },
};
