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
import { Button, Muted, Title } from '@/components/ui';
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
      setHint(res.sent ? null : 'Code envoyé (voir logs serveur en dev).');
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
    <SafeAreaView style={styles.safe}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.container}
      >
        <View style={styles.brandBlock}>
          <Text style={styles.logo}>Calo</Text>
          <Muted style={{ textAlign: 'center', marginTop: spacing.sm }}>
            Ton coach nutrition · sport · mental, disponible 24/7
          </Muted>
        </View>

        {step === 'phone' ? (
          <View>
            <Title style={{ fontSize: 22, marginBottom: spacing.md }}>Bienvenue 👋</Title>
            <Muted style={{ marginBottom: spacing.sm }}>Entre ton numéro de téléphone</Muted>
            <TextInput
              style={styles.input}
              placeholder="+41 79 123 45 67"
              placeholderTextColor={colors.textMuted}
              keyboardType="phone-pad"
              autoFocus
              value={phone}
              onChangeText={setPhone}
            />
            <Button title="Recevoir mon code" onPress={sendCode} loading={loading} style={{ marginTop: spacing.md }} />
          </View>
        ) : (
          <View>
            <Title style={{ fontSize: 22, marginBottom: spacing.md }}>Code de vérification</Title>
            <Muted style={{ marginBottom: spacing.sm }}>
              Envoyé au {phone}
            </Muted>
            <TextInput
              style={[styles.input, styles.codeInput]}
              placeholder="000000"
              placeholderTextColor={colors.textMuted}
              keyboardType="number-pad"
              maxLength={6}
              autoFocus
              value={code}
              onChangeText={setCode}
            />
            <Button title="Se connecter" onPress={verify} loading={loading} variant="accent" style={{ marginTop: spacing.md }} />
            <Button title="Changer de numéro" onPress={() => setStep('phone')} variant="ghost" style={{ marginTop: spacing.sm }} />
          </View>
        )}

        {hint && <Muted style={{ marginTop: spacing.md, textAlign: 'center' }}>{hint}</Muted>}
        {error && <Text style={styles.error}>{error}</Text>}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  container: { flex: 1, padding: spacing.lg, justifyContent: 'center' },
  brandBlock: { alignItems: 'center', marginBottom: spacing.xxl },
  logo: { color: colors.white, fontSize: 52, fontWeight: '900', letterSpacing: 1 },
  input: {
    backgroundColor: colors.card,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    color: colors.text,
    fontSize: 18,
    paddingHorizontal: spacing.md,
    height: 56,
  },
  codeInput: { textAlign: 'center', letterSpacing: 8, fontSize: 28 },
  error: { color: colors.danger, marginTop: spacing.md, textAlign: 'center' },
});
