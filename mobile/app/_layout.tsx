import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator } from 'react-native';
import { Stack, useRouter, useSegments } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { AuthProvider, useAuth } from '@/store/auth';
import { ToastHost } from '@/components/Toast';
import { shouldShowOnboarding } from './onboarding';
import { colors } from '@/theme';

function RootNavigator() {
  const { ready, token } = useAuth();
  const segments = useSegments();
  const router = useRouter();
  const [onbReady, setOnbReady] = useState(false);
  const [needsOnb, setNeedsOnb] = useState(false);

  useEffect(() => {
    (async () => {
      setNeedsOnb(await shouldShowOnboarding());
      setOnbReady(true);
    })();
  }, []);

  useEffect(() => {
    if (!ready || !onbReady) return;
    const first = segments[0];
    const inAuthArea = first === 'login' || first === 'onboarding' || first === undefined;

    if (!token) {
      if (needsOnb && first !== 'onboarding') router.replace('/onboarding');
      else if (!needsOnb && !inAuthArea) router.replace('/login');
    } else if (token && (first === 'login' || first === 'onboarding')) {
      router.replace('/(tabs)');
    }
  }, [ready, onbReady, token, needsOnb, segments]);

  if (!ready || !onbReady) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: 'center' }}>
        <ActivityIndicator color={colors.accent} size="large" />
      </View>
    );
  }

  return (
    <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.bg } }}>
      <Stack.Screen name="index" />
      <Stack.Screen name="onboarding" />
      <Stack.Screen name="login" />
      <Stack.Screen name="(tabs)" />
      <Stack.Screen name="paywall" options={{ presentation: 'modal' }} />
      <Stack.Screen name="settings" options={{ presentation: 'modal' }} />
    </Stack>
  );
}

export default function RootLayout() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <AuthProvider>
          <StatusBar style="light" />
          <RootNavigator />
          <ToastHost />
        </AuthProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}
