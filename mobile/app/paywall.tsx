import React, { useState } from 'react';
import { ScrollView, StyleSheet, Text, View, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Button, Muted } from '@/components/ui';
import { colors, radius, spacing } from '@/theme';

const PLANS = [
  {
    id: 'plus',
    name: 'Calo Plus',
    price: '99€',
    period: '/mois',
    highlight: true,
    perks: [
      'Coaching IA 24/7 illimité (texte + vocal)',
      'Analyses repas, morpho, étiquettes, bilans',
      '8 programmes sport + 16 challenges',
      'Recettes IA + plans repas',
      'Graphes & rapports mensuels PDF',
    ],
  },
  {
    id: 'elite',
    name: 'Calo Elite',
    price: '299€',
    period: '/mois',
    highlight: false,
    perks: [
      'Tout Plus +',
      '1 call 30 min/mois avec Damien',
      'Bilan sanguin annuel + interprétation',
      'Ta voix clonée dans Calo',
      'Priorité WhatsApp < 30 sec',
    ],
  },
  {
    id: 'pro',
    name: 'Calo Pro',
    price: '999€',
    period: '/mois',
    highlight: false,
    perks: [
      'Tout Elite +',
      'Calls illimités avec Damien',
      'Bilans trimestriels deep',
      'Conciergerie complète (voyage, pros)',
      'Réseau de pros partenaires',
    ],
  },
];

export default function Paywall() {
  const router = useRouter();
  const [selected, setSelected] = useState('plus');

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={{ padding: spacing.lg }}>
        <Pressable onPress={() => router.back()} style={styles.close} hitSlop={10}>
          <Ionicons name="close" size={28} color={colors.textMuted} />
        </Pressable>

        <Text style={styles.title}>Débloque tout Calo</Text>
        <Muted style={{ marginBottom: spacing.lg }}>
          Ton coach complet nutrition · sport · mental. Annulable à tout moment.
        </Muted>

        {PLANS.map((p) => {
          const isSel = selected === p.id;
          return (
            <Pressable key={p.id} onPress={() => setSelected(p.id)}>
              <View
                style={[
                  styles.plan,
                  isSel && styles.planSelected,
                  p.highlight && styles.planHighlight,
                ]}
              >
                {p.highlight && (
                  <View style={styles.badge}>
                    <Text style={styles.badgeText}>POPULAIRE</Text>
                  </View>
                )}
                <View style={styles.planHeader}>
                  <Text style={styles.planName}>{p.name}</Text>
                  <View style={{ flexDirection: 'row', alignItems: 'flex-end' }}>
                    <Text style={styles.planPrice}>{p.price}</Text>
                    <Text style={styles.planPeriod}>{p.period}</Text>
                  </View>
                </View>
                {p.perks.map((perk) => (
                  <View key={perk} style={styles.perkRow}>
                    <Ionicons name="checkmark-circle" size={18} color={colors.success} />
                    <Text style={styles.perkText}>{perk}</Text>
                  </View>
                ))}
              </View>
            </Pressable>
          );
        })}

        <Button
          title="S'abonner"
          variant="accent"
          onPress={() => router.back()}
          style={{ marginTop: spacing.md }}
        />
        <Muted style={{ textAlign: 'center', marginTop: spacing.md, fontSize: 12 }}>
          Paiement via l'App Store. L'abonnement se renouvelle automatiquement
          sauf annulation 24h avant la fin de la période.
        </Muted>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  close: { alignSelf: 'flex-end', marginBottom: spacing.sm },
  title: { color: colors.white, fontSize: 28, fontWeight: '900', marginBottom: spacing.xs },
  plan: {
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    padding: spacing.lg,
    borderWidth: 2,
    borderColor: colors.border,
    marginBottom: spacing.md,
  },
  planSelected: { borderColor: colors.accent },
  planHighlight: { borderColor: colors.accent },
  badge: {
    position: 'absolute',
    top: -10,
    right: spacing.lg,
    backgroundColor: colors.accent,
    borderRadius: radius.pill,
    paddingHorizontal: spacing.md,
    paddingVertical: 4,
  },
  badgeText: { color: colors.white, fontSize: 11, fontWeight: '800' },
  planHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    marginBottom: spacing.md,
  },
  planName: { color: colors.text, fontSize: 20, fontWeight: '800' },
  planPrice: { color: colors.accentSoft, fontSize: 28, fontWeight: '900' },
  planPeriod: { color: colors.textMuted, fontSize: 14, marginBottom: 5, marginLeft: 2 },
  perkRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.sm },
  perkText: { color: colors.text, fontSize: 14, flex: 1 },
});
