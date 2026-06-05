/** "Aujourd'hui" — the premium home dashboard. Pull-to-refresh, lots of
 * animated motion, sourced from /app/home. */
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
import { Card, Muted, Pill } from '@/components/ui';
import { Ring } from '@/components/Ring';
import { showToast } from '@/components/Toast';
import { setPendingPrompt } from '@/store/pendingPrompt';
import { colors, radius, spacing } from '@/theme';

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
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    await load();
    setRefreshing(false);
  };

  const goCoach = (prompt?: string) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    if (prompt) setPendingPrompt(prompt);
    router.push('/(tabs)/coach');
  };

  const t = data?.today;
  const kcalProgress = t?.targets.kcal ? (t.consumed.kcal / t.targets.kcal) : 0;
  const proteinProgress = t?.targets.protein ? (t.consumed.protein / t.targets.protein) : 0;
  const carbsProgress = t?.targets.carbs ? (t.consumed.carbs / t.targets.carbs) : 0;
  const fatProgress = t?.targets.fat ? (t.consumed.fat / t.targets.fat) : 0;

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <ScrollView
        contentContainerStyle={{ padding: spacing.lg, paddingBottom: spacing.xxl }}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />
        }
      >
        <Text style={styles.greeting}>{data?.greeting ?? 'Bienvenue ✨'}</Text>
        {!!data?.goal && <Muted style={{ marginBottom: spacing.lg }}>Objectif : {data.goal}</Muted>}

        {data?.insight ? <InsightCard insight={data.insight} onPress={() => goCoach(`Développe : ${data.insight.title}`)} /> : null}

        {/* Big calorie ring + 3 small macro rings */}
        <Card style={{ marginTop: spacing.md }}>
          <View style={{ flexDirection: 'row', alignItems: 'center' }}>
            <Ring
              size={140}
              stroke={14}
              progress={kcalProgress}
              valueText={`${t?.consumed.kcal ?? 0}`}
              unit={`/ ${t?.targets.kcal || '—'} kcal`}
              label="Aujourd'hui"
            />
            <View style={{ flex: 1, marginLeft: spacing.lg, gap: spacing.sm }}>
              <MacroLine label="Protéines" consumed={t?.consumed.protein ?? 0} target={t?.targets.protein ?? 0} unit="g" progress={proteinProgress} color="#4FC3A1" />
              <MacroLine label="Glucides" consumed={t?.consumed.carbs ?? 0} target={t?.targets.carbs ?? 0} unit="g" progress={carbsProgress} color="#F4A24C" />
              <MacroLine label="Lipides" consumed={t?.consumed.fat ?? 0} target={t?.targets.fat ?? 0} unit="g" progress={fatProgress} color="#E07B00" />
            </View>
          </View>
        </Card>

        {/* Streak + weight side by side */}
        <View style={styles.row2}>
          <Card style={[styles.statCard, { borderColor: (data?.streak ?? 0) >= 3 ? colors.accent : colors.border }]}>
            <Text style={styles.statEmoji}>🔥</Text>
            <Text style={styles.statValue}>{data?.streak ?? 0}</Text>
            <Muted>{(data?.streak ?? 0) <= 1 ? 'jour de streak' : 'jours d\'affilée'}</Muted>
          </Card>
          <Card style={styles.statCard}>
            <Text style={styles.statEmoji}>⚖️</Text>
            <Text style={styles.statValue}>
              {data?.weight.latest_kg != null ? `${data.weight.latest_kg.toFixed(1)}` : '—'}
            </Text>
            <Muted>
              {data?.weight.delta_30d_kg != null
                ? `${data.weight.delta_30d_kg > 0 ? '+' : ''}${data.weight.delta_30d_kg} kg / 30j`
                : 'kg actuels'}
            </Muted>
          </Card>
        </View>

        {/* 30-day heatmap */}
        <Card style={{ marginTop: spacing.md }}>
          <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: spacing.sm }}>
            <Text style={styles.sectionLabel}>30 derniers jours</Text>
            <Muted>{data?.heatmap_30d.filter(c => c.active).length ?? 0} jours actifs</Muted>
          </View>
          <Heatmap cells={data?.heatmap_30d ?? []} />
        </Card>

        {/* Quick actions */}
        <Text style={[styles.sectionLabel, { marginTop: spacing.lg, marginBottom: spacing.sm }]}>
          Action rapide
        </Text>
        <View style={styles.quickGrid}>
          <QuickAction icon="camera" label="Photo repas" onPress={() => goCoach('Analyse ce repas (j\'envoie une photo)')} />
          <QuickAction icon="scale" label="Log poids" onPress={() => goCoach('Je pèse :')} />
          <QuickAction icon="barbell" label="Programme" onPress={() => goCoach('Donne-moi mon programme du jour')} />
          <QuickAction icon="moon" label="J\'ai mal dormi" onPress={() => goCoach('J\'ai mal dormi cette nuit, comment rattraper la journée ?')} />
        </View>

        <Pressable onPress={() => goCoach()} style={styles.askBtn}>
          <Ionicons name="sparkles" size={20} color={colors.white} />
          <Text style={styles.askText}>Demande à Calo</Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}

function MacroLine({ label, consumed, target, unit, progress, color }: {
  label: string; consumed: number; target: number; unit: string; progress: number; color: string;
}) {
  const pct = Math.max(0, Math.min(progress, 1)) * 100;
  return (
    <View>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 }}>
        <Text style={styles.macroLabel}>{label}</Text>
        <Text style={styles.macroValue}>{consumed} / {target || '—'} {unit}</Text>
      </View>
      <View style={styles.macroTrack}>
        <View style={[styles.macroFill, { width: `${pct}%`, backgroundColor: color }]} />
      </View>
    </View>
  );
}

function InsightCard({ insight, onPress }: { insight: { icon: string; title: string; body: string }; onPress: () => void }) {
  const anim = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.timing(anim, { toValue: 1, duration: 480, useNativeDriver: true, easing: Easing.out(Easing.cubic) }).start();
  }, [insight.title]);
  return (
    <Animated.View
      style={{
        opacity: anim,
        transform: [{ translateY: anim.interpolate({ inputRange: [0, 1], outputRange: [12, 0] }) }],
      }}
    >
      <Pressable onPress={onPress}>
        <Card style={styles.insightCard}>
          <Text style={styles.insightIcon}>{insight.icon}</Text>
          <View style={{ flex: 1 }}>
            <Text style={styles.insightTitle}>{insight.title}</Text>
            <Text style={styles.insightBody}>{insight.body}</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color={colors.textMuted} />
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
  safe: { flex: 1, backgroundColor: colors.bg },
  greeting: { color: colors.text, fontSize: 28, fontWeight: '900', marginBottom: spacing.xs },
  sectionLabel: { color: colors.text, fontSize: 16, fontWeight: '700' },

  row2: { flexDirection: 'row', gap: spacing.sm, marginTop: spacing.md },
  statCard: { flex: 1, alignItems: 'center', paddingVertical: spacing.lg },
  statEmoji: { fontSize: 24, marginBottom: 4 },
  statValue: { color: colors.text, fontSize: 28, fontWeight: '900' },

  insightCard: {
    flexDirection: 'row', alignItems: 'center', gap: spacing.md,
    borderColor: colors.accent, borderWidth: 1,
  },
  insightIcon: { fontSize: 28 },
  insightTitle: { color: colors.text, fontSize: 16, fontWeight: '800', marginBottom: 2 },
  insightBody: { color: colors.textMuted, fontSize: 13, lineHeight: 18 },

  macroLabel: { color: colors.textMuted, fontSize: 12, fontWeight: '600' },
  macroValue: { color: colors.text, fontSize: 12, fontWeight: '700' },
  macroTrack: { height: 6, backgroundColor: colors.bgElevated, borderRadius: 3, overflow: 'hidden' },
  macroFill: { height: 6, borderRadius: 3 },

  heatRow: { flexDirection: 'row', gap: 4, flexWrap: 'wrap' },
  heatCell: { width: 18, height: 18, borderRadius: 4 },

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

  askBtn: {
    marginTop: spacing.lg, flexDirection: 'row', justifyContent: 'center', alignItems: 'center',
    gap: spacing.sm, backgroundColor: colors.primary, height: 56, borderRadius: radius.md,
  },
  askText: { color: colors.white, fontSize: 17, fontWeight: '800' },
});
