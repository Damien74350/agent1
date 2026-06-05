import React, { useState } from 'react';
import {
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { api, ApiError } from '@/api/client';
import { useAuth } from '@/store/auth';
import { Aurora } from '@/components/Aurora';
import { Button, Eyebrow, Hero, Muted } from '@/components/ui';
import { colors, radius, spacing } from '@/theme';

export default function Login() {
  const { signIn } = useAuth();
  const [step, setStep] = useState<'phone' | 'code'>('phone');
  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hint, setHint] = useState<string | null>(null);

  async function sendCode() {
    setError(null);
    setLoading(true);
    try {
      const res = await api.authStart(phone);
      setHint(res.sent ? null : 'Code généré côté serveur (logs Railway).');
      setStep('code');
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Erreur réseau');
    } finally {
      setLoading(false);
    }
  }

  async function verify() {
    setError(null);
    setLoading(true);
    try {
      const { token, user } = await api.authVerify(phone, code);
      await signIn(token, user);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Erreur réseau');
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={styles.root}>
      <Aurora />
      <SafeAreaView style={styles.safe}>
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
          style={styles.container}
        >
          <View style={styles.brandBlock}>
            <Eyebrow>Coach IA · 24/7</Eyebrow>
            <Hero style={styles.logo}>Calo</Hero>
            <Muted style={{ textAlign: 'center', marginTop: spacing.sm, maxWidth: 320 }}>
              Nutrition · Sport · Mental, tout en un. Le compagnon que tu mérites.
            </Muted>
          </View>

          {step === 'phone' ? (
            <View style={styles.form}>
              <Eyebrow style={{ marginBottom: spacing.sm }}>Ton numéro</Eyebrow>
              <TextInput
                style={styles.input}
                placeholder="+41 79 123 45 67"
                placeholderTextColor={colors.textDim}
                keyboardType="phone-pad"
                autoFocus
                value={phone}
                onChangeText={setPhone}
              />
              <Button
                title="Recevoir mon code"
                onPress={sendCode}
                loading={loading}
                variant="accent"
                size="lg"
                style={{ marginTop: spacing.md }}
              />
              <Muted style={{ textAlign: 'center', marginTop: spacing.md }}>
                Tes données restent privées, et tu peux supprimer ton compte à tout moment.
              </Muted>
            </View>
          ) : (
            <View style={styles.form}>
              <Eyebrow style={{ marginBottom: spacing.sm }}>Code reçu</Eyebrow>
              <TextInput
                style={[styles.input, styles.codeInput]}
                placeholder="••••••"
                placeholderTextColor={colors.textDim}
                keyboardType="number-pad"
                maxLength={6}
                autoFocus
                value={code}
                onChangeText={setCode}
              />
              <Button title="Se connecter" onPress={verify} loading={loading} variant="accent" size="lg" style={{ marginTop: spacing.md }} />
              <Button title="Changer de numéro" onPress={() => setStep('phone')} variant="ghost" style={{ marginTop: spacing.sm }} />
              <Muted style={{ textAlign: 'center', marginTop: spacing.md }}>
                Envoyé au {phone}
              </Muted>
            </View>
          )}

          {hint && <Muted style={{ marginTop: spacing.md, textAlign: 'center' }}>{hint}</Muted>}
          {error && <Text style={styles.error}>{error}</Text>}
        </KeyboardAvoidingView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.bg },
  safe: { flex: 1 },
  container: { flex: 1, padding: spacing.lg, justifyContent: 'center' },
  brandBlock: { alignItems: 'center', marginBottom: spacing.xxl, gap: spacing.xs },
  logo: { fontSize: 76, letterSpacing: -3 },
  form: { gap: spacing.xs },
  input: {
    backgroundColor: colors.glassOverlay,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.borderStrong,
    color: colors.text,
    fontSize: 18,
    paddingHorizontal: spacing.md,
    height: 58,
  },
  codeInput: { textAlign: 'center', letterSpacing: 12, fontSize: 28, fontWeight: '900' },
  error: { color: colors.danger, marginTop: spacing.md, textAlign: 'center', fontWeight: '600' },
});
