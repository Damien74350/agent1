/** Settings modal — language, voice, notifications, privacy, danger zone. */
import React, { useState } from 'react';
import { Alert, Linking, Pressable, ScrollView, StyleSheet, Switch, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '@/store/auth';
import { Button, Muted } from '@/components/ui';
import { colors, radius, spacing } from '@/theme';

export default function Settings() {
  const router = useRouter();
  const { signOut, user } = useAuth();
  const [voiceOut, setVoiceOut] = useState(true);
  const [notif, setNotif] = useState(true);
  const [photoConsent, setPhotoConsent] = useState(true);

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={{ padding: spacing.lg }}>
        <View style={styles.header}>
          <Text style={styles.title}>Réglages</Text>
          <Pressable onPress={() => router.back()} hitSlop={10}>
            <Ionicons name="close" size={28} color={colors.textMuted} />
          </Pressable>
        </View>

        <Section title="Coach">
          <Toggle icon="mic" label="Réponses vocales de Calo" value={voiceOut} onChange={setVoiceOut} hint="Active la voix clonée en sortie" />
          <Toggle icon="notifications" label="Rappels & check-ins" value={notif} onChange={setNotif} hint="Tu reçois 1-2 messages utiles / jour" />
          <Toggle icon="camera" label="Suivi photo morpho" value={photoConsent} onChange={setPhotoConsent} hint="Consentement obligatoire pour les analyses morpho" />
        </Section>

        <Section title="Compte">
          <Row icon="person" label={user?.name || 'Mon profil'} sublabel="Édite via Calo en chat" />
          <Row icon="logo-whatsapp" label="Numéro lié" sublabel="WhatsApp + app synchronisés" />
          <Row icon="diamond" label="Mon abonnement" onPress={() => { router.back(); setTimeout(() => router.push('/paywall'), 200); }} sublabel="Voir / changer de plan" />
        </Section>

        <Section title="Confidentialité">
          <Row icon="shield-checkmark" label="Politique de confidentialité" onPress={() => Linking.openURL('https://coachwarrior-production.up.railway.app/').catch(() => {})} />
          <Row icon="document-text" label="Conditions d'utilisation" onPress={() => Linking.openURL('https://coachwarrior-production.up.railway.app/').catch(() => {})} />
          <Row icon="download" label="Exporter mes données" onPress={() => Alert.alert('Export', 'Demande envoyée : tu reçois un PDF complet sous 48h via Calo.')} />
        </Section>

        <Section title="Zone sensible">
          <Row icon="log-out" label="Se déconnecter" onPress={() => signOut()} danger />
          <Row icon="trash" label="Supprimer mon compte" onPress={() =>
            Alert.alert('Supprimer ?', 'Tes données seront effacées sous 30 jours. Tu peux annuler avant la fin.', [
              { text: 'Annuler', style: 'cancel' },
              { text: 'Confirmer', style: 'destructive', onPress: () => Alert.alert('OK', 'Suppression planifiée. Calo te confirme par WhatsApp.') },
            ])} danger />
        </Section>

        <Muted style={{ textAlign: 'center', marginTop: spacing.lg }}>Calo v1.0.0 · Made with ❤️ in Switzerland</Muted>
      </ScrollView>
    </SafeAreaView>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={{ marginBottom: spacing.lg }}>
      <Text style={styles.sectionTitle}>{title}</Text>
      <View style={styles.sectionBox}>{children}</View>
    </View>
  );
}

function Toggle({ icon, label, value, onChange, hint }: { icon: any; label: string; value: boolean; onChange: (v: boolean) => void; hint?: string }) {
  return (
    <View style={styles.row}>
      <Ionicons name={icon} size={20} color={colors.textMuted} />
      <View style={{ flex: 1 }}>
        <Text style={styles.label}>{label}</Text>
        {hint && <Muted style={{ fontSize: 12, marginTop: 2 }}>{hint}</Muted>}
      </View>
      <Switch
        value={value}
        onValueChange={onChange}
        trackColor={{ false: colors.bgElevated, true: colors.accent }}
        thumbColor={colors.white}
      />
    </View>
  );
}

function Row({ icon, label, sublabel, onPress, danger }: { icon: any; label: string; sublabel?: string; onPress?: () => void; danger?: boolean }) {
  return (
    <Pressable onPress={onPress} disabled={!onPress} style={({ pressed }) => [styles.row, pressed && { opacity: 0.6 }]}>
      <Ionicons name={icon} size={20} color={danger ? colors.danger : colors.textMuted} />
      <View style={{ flex: 1 }}>
        <Text style={[styles.label, danger && { color: colors.danger }]}>{label}</Text>
        {sublabel && <Muted style={{ fontSize: 12, marginTop: 2 }}>{sublabel}</Muted>}
      </View>
      {onPress && <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.lg },
  title: { color: colors.text, fontSize: 28, fontWeight: '900' },
  sectionTitle: { color: colors.textMuted, fontSize: 12, fontWeight: '700', letterSpacing: 1, textTransform: 'uppercase', marginBottom: spacing.sm, marginLeft: spacing.xs },
  sectionBox: { backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, overflow: 'hidden' },
  row: { flexDirection: 'row', alignItems: 'center', gap: spacing.md, paddingHorizontal: spacing.md, paddingVertical: spacing.md, borderBottomWidth: 0.5, borderBottomColor: colors.border },
  label: { color: colors.text, fontSize: 15, fontWeight: '600' },
});
