import React from 'react';
import { Redirect } from 'expo-router';
import { useAuth } from '@/store/auth';

/** Entry gate: bounce to the app or to login depending on auth. */
export default function Index() {
  const { token } = useAuth();
  return <Redirect href={token ? '/(tabs)' : '/login'} />;
}
