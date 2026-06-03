import React, { useCallback, useState } from 'react';
import { RefreshControl, ScrollView, StyleSheet, Text, View, Dimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFocusEffect } from 'expo-router';
import Svg, { Polyline, Circle, Line } from 'react-native-svg';
import { api, Progress as ProgressData } from '@/api/client';
import { Card, Muted, Title } from '@/components/ui';
import { colors, spacing } from '@/theme';

export default function Progress() {
  const [data, setData] = useState<ProgressData | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      setData(await api.progress());
    } catch {}
  }, []);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  const today = data?.today;
  const pct =
    today && today.target_kcal
      ? Math.min(100, Math.round((today.consumed_kcal / today.target_kcal) * 100))
      : 0;

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <ScrollView
        contentContainerStyle={{ padding: spacing.lg }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />}
      >
        <Title style={{ marginBottom: spacing.lg }}>Tes progrès</Title>

        <Card style={{ marginBottom: spacing.md }}>
          <Muted>Aujourd'hui</Muted>
          <View style={styles.kcalRow}>
            <Text style={styles.kcalBig}>{today?.consumed_kcal ?? 0}</Text>
            <Text style={styles.kcalUnit}>
              / {today?.target_kcal || '—'} kcal
            </Text>
          </View>
          <View style={styles.progressTrack}>
            <View style={[styles.progressFill, { width: `${pct}%` }]} />
          </View>
          <Muted style={{ marginTop: spacing.sm }}>
            {today?.remaining_kcal != null
              ? `${today.remaining_kcal} kcal restantes · ${data?.meals_today ?? 0} repas loggés`
              : 'Complète ton profil pour voir tes objectifs'}
          </Muted>
        </Card>

        <Card>
          <Muted style={{ marginBottom: spacing.md }}>Évolution du poids</Muted>
          {data && data.weights.length >= 2 ? (
            <WeightChart points={data.weights.map((w) => w.kg).reverse()} />
          ) : (
            <Muted>Pas encore assez de pesées. Envoie ton poids à Calo pour démarrer le suivi.</Muted>
          )}
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
}

function WeightChart({ points }: { points: number[] }) {
  const W = Dimensions.get('window').width - spacing.lg * 2 - spacing.lg * 2;
  const H = 160;
  const min = Math.min(...points);
  const max = Math.max(...points);
  const range = max - min || 1;
  const stepX = points.length > 1 ? W / (points.length - 1) : W;
  const coords = points.map((p, i) => {
    const x = i * stepX;
    const y = H - ((p - min) / range) * (H - 20) - 10;
    return { x, y };
  });
  const poly = coords.map((c) => `${c.x},${c.y}`).join(' ');

  return (
    <View>
      <Svg width={W} height={H}>
        <Line x1={0} y1={H - 1} x2={W} y2={H - 1} stroke={colors.border} strokeWidth={1} />
        <Polyline points={poly} fill="none" stroke={colors.accent} strokeWidth={3} />
        {coords.map((c, i) => (
          <Circle key={i} cx={c.x} cy={c.y} r={4} fill={colors.accentSoft} />
        ))}
      </Svg>
      <View style={styles.chartLabels}>
        <Muted>{min.toFixed(1)} kg</Muted>
        <Muted>{max.toFixed(1)} kg</Muted>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  kcalRow: { flexDirection: 'row', alignItems: 'flex-end', marginTop: spacing.xs },
  kcalBig: { color: colors.text, fontSize: 40, fontWeight: '900' },
  kcalUnit: { color: colors.textMuted, fontSize: 16, marginBottom: 8, marginLeft: 6 },
  progressTrack: {
    height: 10,
    backgroundColor: colors.bgElevated,
    borderRadius: 5,
    marginTop: spacing.sm,
    overflow: 'hidden',
  },
  progressFill: { height: 10, backgroundColor: colors.accent, borderRadius: 5 },
  chartLabels: { flexDirection: 'row', justifyContent: 'space-between', marginTop: spacing.sm },
});
