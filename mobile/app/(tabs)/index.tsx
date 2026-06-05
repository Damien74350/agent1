/** Aujourd'hui — premium dashboard. Hero greeting, bento grid, insight card,
 * heatmap, quick actions, floating Ask Calo CTA. Refonte premium 2026. */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Animated,
  Easing,
  Pressable,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFocusEffect, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { api, ApiError, Home as HomeData } from '@/api/client';
import { Aurora } from '@/components/Aurora';
import { Card, Eyebrow, Hero, Muted } from '@/components/ui';
import { Ring } from '@/components/Ring';
import { showToast } from '@/components/Toast';
import { setPendingPrompt } from '@/store/pendingPrompt';
import { colors, radius, shadow, spacing } from '@/theme';

export default function Home() {
  const router = useRouter();
  const [data, setData] = useState<HomeData | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      setData(await api.home());
    } catch (e) {
      if (e instanceof ApiError && e.status !== 401) {
        showToast(`Chargement impossible : ${e.message}`);
      }
    }
  }, []);

  useFocusEffect(useCallback(() => { void load(); }, [load]));

  const onRefresh = async () => {
    setRefreshing(true);
    try { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); } catch {}
    await load();
    setRefreshing(false);
  };

  const goCoach = (prompt?: string) => {
    try { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); } catch {}
    if (prompt) setPendingPrompt(prompt);
    router.push('/(tabs)/coach');
  };

  const t = data?.today;
  const kcalProgress = t?.targets.kcal ? (t.consumed.kcal / t.targets.kcal) : 0;
  const proteinProgress = t?.targets.protein ? (t.consumed.protein / t.targets.protein) : 0;
  const carbsProgress = t?.targets.carbs ? (t.consumed.carbs / t.targets.carbs) : 0;
  const fatProgress = t?.targets.fat ? (t.consumed.fat / t.targets.fat) : 0;

  return (
    <View style={styles.root}>
      <Aurora />
      <SafeAreaView style={styles.safe} edges={['top']}>
        <ScrollView
          contentContainerStyle={{ padding: spacing.lg, paddingBottom: 140 }}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />
          }
        >
          {/* HERO */}
          <Eyebrow>Aujourd'hui</Eyebrow>
          <Hero style={{ marginTop: 4 }}>{data?.greeting ?? 'Bienvenue ✨'}</Hero>
          {!!data?.goal && (
            <Muted style={{ marginTop: spacing.sm, marginBottom: spacing.lg }}>
              Objectif · <Text style={{ color: colors.accentSoft, fontWeight: '700' }}>{data.goal}</Text>
            </Muted>
          )}

          {/* INSIGHT CARD */}
          {data?.insight && (
            <InsightCard insight={data.insight} onPress={() => goCoach(`Développe : ${data.insight.title}`)} />
          )}

          {/* MAIN BENTO : big ring + macros */}
          <Card variant="elevated" style={{ marginTop: spacing.md }}>
            <Eyebrow>Nutrition</Eyebrow>
            <View style={{ flexDirection: 'row', alignItems: 'center', marginTop: spacing.sm }}>
              <Ring
                size={140}
                stroke={14}
                progress={kcalProgress}
                valueText={`${t?.consumed.kcal ?? 0}`}
                unit={`/ ${t?.targets.kcal || '—'} kcal`}
                label="Calories"
              />
              <View style={{ flex: 1, marginLeft: spacing.lg, gap: spacing.md }}>
                <MacroLine label="Protéines" consumed={t?.consumed.protein ?? 0} target={t?.targets.protein ?? 0} unit="g" progress={proteinProgress} color={colors.mint} />
                <MacroLine label="Glucides" consumed={t?.consumed.carbs ?? 0} target={t?.targets.carbs ?? 0} unit="g" progress={carbsProgress} color={colors.violet} />
                <MacroLine label="Lipides" consumed={t?.consumed.fat ?? 0} target={t?.targets.fat ?? 0} unit="g" progress={fatProgress} color={colors.accent} />
              </View>
            </View>
          </Card>

          {/* BENTO STATS : 2x */}
          <View style={styles.row2}>
            <StatCard
              emoji="🔥"
              value={`${data?.streak ?? 0}`}
              label={(data?.streak ?? 0) <= 1 ? 'jour de streak' : 'jours d\'affilée'}
              highlight={(data?.streak ?? 0) >= 3}
            />
            <StatCard
              emoji="⚖️"
              value={data?.weight.latest_kg != null ? data.weight.latest_kg.toFixed(1) : '—'}
              label={data?.weight.delta_30d_kg != null
                ? `${data.weight.delta_30d_kg > 0 ? '+' : ''}${data.weight.delta_30d_kg} kg / 30j`
                : 'kg actuels'}
            />
          </View>

          {/* 30-DAY HEATMAP */}
          <Card variant="elevated" style={{ marginTop: spacing.md }}>
            <View style={styles.cardHeader}>
              <Eyebrow>30 derniers jours</Eyebrow>
              <Muted style={{ color: colors.accentSoft, fontWeight: '700' }}>
                {data?.heatmap_30d.filter(c => c.active).length ?? 0} actifs
              </Muted>
            </View>
            <Heatmap cells={data?.heatmap_30d ?? []} />
          </Card>

          {/* QUICK ACTIONS */}
          <Eyebrow style={{ marginTop: spacing.xl, marginBottom: spacing.sm }}>Action rapide</Eyebrow>
          <View style={styles.quickGrid}>
            <QuickAction icon="camera" label="Photo repas" onPress={() => goCoach('Analyse ce repas (j\'envoie une photo)')} />
            <QuickAction icon="scale" label="Log poids" onPress={() => goCoach('Je pèse :')} />
            <QuickAction icon="barbell" label="Programme" onPress={() => goCoach('Donne-moi mon programme du jour')} />
            <QuickAction icon="moon" label="J\'ai mal dormi" onPress={() => goCoach('J\'ai mal dormi cette nuit, comment rattraper la journée ?')} />
          </View>
        </ScrollView>

        {/* FLOATING ASK CALO BUTTON */}
        <View style={styles.fabWrap} pointerEvents="box-none">
          <Pressable onPress={() => goCoach()} style={({ pressed }) => [styles.fab, pressed && { opacity: 0.9 }]}>
            <Ionicons name="sparkles" size={20} color={colors.white} />
            <Text style={styles.fabText}>Demande à Calo</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    </View>
  );
}

function StatCard({ emoji, value, label, highlight }: { emoji: string; value: string; label: string; highlight?: boolean }) {
  return (
    <View style={[styles.statCard, highlight && styles.statCardHi]}>
      <Text style={styles.statEmoji}>{emoji}</Text>
      <Text style={styles.statValue}>{value}</Text>
      <Muted style={{ marginTop: 2 }}>{label}</Muted>
    </View>
  );
}

function MacroLine({ label, consumed, target, unit, progress, color }: {
  label: string; consumed: number; target: number; unit: string; progress: number; color: string;
}) {
  const animatedW = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.timing(animatedW, {
      toValue: Math.max(0, Math.min(progress, 1)) * 100,
      duration: 700,
      easing: Easing.out(Easing.cubic),
      useNativeDriver: false,
    }).start();
  }, [progress]);
  return (
    <View>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 }}>
        <Text style={styles.macroLabel}>{label}</Text>
        <Text style={styles.macroValue}>{consumed} / {target || '—'} {unit}</Text>
      </View>
      <View style={styles.macroTrack}>
        <Animated.View
          style={[
            styles.macroFill,
            { backgroundColor: color, width: animatedW.interpolate({ inputRange: [0, 100], outputRange: ['0%', '100%'] }) },
          ]}
        />
      </View>
    </View>
  );
}

function InsightCard({ insight, onPress }: { insight: { icon: string; title: string; body: string }; onPress: () => void }) {
  const anim = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.timing(anim, { toValue: 1, duration: 560, useNativeDriver: true, easing: Easing.out(Easing.cubic) }).start();
  }, [insight.title]);
  return (
    <Animated.View
      style={{
        opacity: anim,
        transform: [{ translateY: anim.interpolate({ inputRange: [0, 1], outputRange: [16, 0] }) }],
      }}
    >
      <Pressable onPress={onPress} style={({ pressed }) => pressed && { opacity: 0.85 }}>
        <Card variant="elevated" style={styles.insightCard}>
          <View style={styles.insightIconWrap}>
            <Text style={styles.insightIcon}>{insight.icon}</Text>
          </View>
          <View style={{ flex: 1 }}>
            <Eyebrow style={{ color: colors.accentSoft }}>Insight du moment</Eyebrow>
            <Text style={styles.insightTitle}>{insight.title}</Text>
            <Text style={styles.insightBody}>{insight.body}</Text>
          </View>
          <Ionicons name="chevron-forward" size={22} color={colors.textMuted} />
        </Card>
      </Pressable>
    </Animated.View>
  );
}

function Heatmap({ cells }: { cells: { date: string; active: boolean }[] }) {
  return (
    <View style={styles.heatRow}>
      {cells.map((c) => (
        <View
          key={c.date}
          style={[
            styles.heatCell,
            { backgroundColor: c.active ? colors.accent : colors.bgElevated },
          ]}
        />
      ))}
    </View>
  );
}

function QuickAction({ icon, label, onPress }: { icon: any; label: string; onPress: () => void }) {
  return (
    <Pressable onPress={onPress} style={({ pressed }) => [styles.quickAction, pressed && { opacity: 0.7 }]}>
      <View style={styles.quickIconWrap}>
        <Ionicons name={icon} size={22} color={colors.accentSoft} />
      </View>
      <Text style={styles.quickLabel}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.bg },
  safe: { flex: 1 },

  cardHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: spacing.md },

  row2: { flexDirection: 'row', gap: spacing.sm, marginTop: spacing.md },
  statCard: {
    flex: 1, padding: spacing.lg, borderRadius: radius.lg,
    backgroundColor: colors.cardHi,
    borderWidth: 1, borderColor: colors.border,
    alignItems: 'flex-start',
    ...shadow.soft,
  },
  statCardHi: { borderColor: colors.accent },
  statEmoji: { fontSize: 24, marginBottom: spacing.sm },
  statValue: { color: colors.text, fontSize: 36, fontWeight: '900', letterSpacing: -1 },

  insightCard: {
    flexDirection: 'row', alignItems: 'center', gap: spacing.md,
    borderColor: colors.accent, borderWidth: 1,
  },
  insightIconWrap: {
    width: 52, height: 52, borderRadius: radius.md,
    backgroundColor: 'rgba(255,120,73,0.15)',
    alignItems: 'center', justifyContent: 'center',
  },
  insightIcon: { fontSize: 28 },
  insightTitle: { color: colors.text, fontSize: 18, fontWeight: '900', marginTop: 2, letterSpacing: -0.3 },
  insightBody: { color: colors.textMuted, fontSize: 13, lineHeight: 19, marginTop: 4 },

  macroLabel: { color: colors.textMuted, fontSize: 11, fontWeight: '700', letterSpacing: 0.5, textTransform: 'uppercase' },
  macroValue: { color: colors.text, fontSize: 13, fontWeight: '800' },
  macroTrack: { height: 6, backgroundColor: colors.bgElevated, borderRadius: 3, overflow: 'hidden' },
  macroFill: { height: 6, borderRadius: 3 },

  heatRow: { flexDirection: 'row', gap: 5, flexWrap: 'wrap' },
  heatCell: { width: 18, height: 18, borderRadius: 5 },

  quickGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  quickAction: {
    flexBasis: '47%', flexGrow: 1, flexDirection: 'row', alignItems: 'center', gap: spacing.sm,
    backgroundColor: colors.card, borderRadius: radius.md, padding: spacing.md,
    borderWidth: 1, borderColor: colors.border,
  },
  quickIconWrap: {
    width: 40, height: 40, borderRadius: radius.md, backgroundColor: colors.bgElevated,
    alignItems: 'center', justifyContent: 'center',
  },
  quickLabel: { color: colors.text, fontSize: 14, fontWeight: '700', flexShrink: 1 },

  fabWrap: {
    position: 'absolute', left: 0, right: 0, bottom: spacing.md,
    alignItems: 'center',
  },
  fab: {
    flexDirection: 'row', alignItems: 'center', gap: spacing.sm,
    backgroundColor: colors.accent,
    paddingHorizontal: spacing.xl, paddingVertical: spacing.md,
    borderRadius: radius.pill,
    ...shadow.glow,
  },
  fabText: { color: colors.white, fontSize: 16, fontWeight: '900', letterSpacing: 0.3 },
});
