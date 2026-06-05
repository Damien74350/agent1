import React from 'react';
import { Alert, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '@/store/auth';
import { Button, Card, Muted, Title } from '@/components/ui';
import { colors, radius, spacing } from '@/theme';

export default function Profile() {
  const { user, signOut } = useAuth();
  const router = useRouter();

  const stats = [
    { label: 'Poids', value: user?.weight_kg ? `${user.weight_kg} kg` : '—' },
    { label: 'Objectif', value: user?.target_weight_kg ? `${user.target_weight_kg} kg` : '—' },
    { label: 'Calories/j', value: user?.daily_calories ? `${user.daily_calories}` : '—' },
  ];

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <ScrollView contentContainerStyle={{ padding: spacing.lg }}>
        <View style={styles.avatarBlock}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              {(user?.name?.[0] ?? 'C').toUpperCase()}
            </Text>
          </View>
          <Title style={{ marginTop: spacing.md }}>{user?.name || 'Mon profil'}</Title>
          <Muted>{user?.goal || 'Objectif à définir avec Calo'}</Muted>
        </View>

        <View style={styles.statsRow}>
          {stats.map((s) => (
            <Card key={s.label} style={styles.statCard}>
              <Text style={styles.statValue}>{s.value}</Text>
              <Muted>{s.label}</Muted>
            </Card>
          ))}
        </View>

        <Card style={styles.premiumCard}>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.sm }}>
            <Ionicons name="diamond" size={20} color={colors.accentSoft} />
            <Text style={styles.premiumTitle}>Passe à Calo Plus</Text>
          </View>
          <Muted style={{ marginVertical: spacing.sm }}>
            Coaching illimité, analyses, programmes, vocal et plus.
          </Muted>
          <Button title="Voir les abonnements" variant="accent" onPress={() => router.push('/paywall')} />
        </Card>

        <Row icon="settings" label="Réglages" onPress={() => router.push('/settings')} />
        <Row icon="person-circle" label="Mes informations" onPress={() => Alert.alert('Mes informations', 'Édite ton profil directement via le chat avec Calo : il garde tout à jour pour toi.')} />
        <Row icon="logo-whatsapp" label="WhatsApp lié" onPress={() => Alert.alert('Lier WhatsApp', `Ton numéro est déjà lié à WhatsApp Calo. App et WhatsApp = même compte, synchronisés.`)} />

        <Button title="Se déconnecter" variant="ghost" onPress={signOut} style={{ marginTop: spacing.lg }} />
        <Muted style={{ textAlign: 'center', marginTop: spacing.md }}>Calo v1.0.0</Muted>
      </ScrollView>
    </SafeAreaView>
  );
}

function Row({ icon, label, onPress }: { icon: any; label: string; onPress: () => void }) {
  return (
    <Card style={styles.row}>
      <Ionicons name={icon} size={20} color={colors.textMuted} />
      <Text style={styles.rowLabel} onPress={onPress}>{label}</Text>
      <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
    </Card>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  avatarBlock: { alignItems: 'center', marginBottom: spacing.lg },
  avatar: {
    width: 96, height: 96, borderRadius: 48,
    backgroundColor: 'rgba(255,107,53,0.15)',
    borderWidth: 2, borderColor: colors.accent,
    alignItems: 'center', justifyContent: 'center',
  },
  avatarText: { color: colors.accent, fontSize: 38, fontWeight: '900', letterSpacing: -1 },
  statsRow: { flexDirection: 'row', gap: spacing.sm, marginBottom: spacing.md },
  statCard: { flex: 1, alignItems: 'center' },
  statValue: { color: colors.text, fontSize: 20, fontWeight: '800', marginBottom: 2 },
  premiumCard: { marginBottom: spacing.lg, borderColor: colors.accent },
  premiumTitle: { color: colors.text, fontSize: 17, fontWeight: '700' },
  row: { flexDirection: 'row', alignItems: 'center', gap: spacing.md, marginBottom: spacing.sm, paddingVertical: spacing.md },
  rowLabel: { flex: 1, color: colors.text, fontSize: 16 },
});
