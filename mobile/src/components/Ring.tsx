/** Apple Health-style progress ring (SVG, no extra deps). */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Svg, { Circle, Defs, LinearGradient, Stop } from 'react-native-svg';
import { colors } from '@/theme';

export function Ring({
  size = 110,
  stroke = 12,
  progress, // 0..1
  color = colors.accent,
  trackColor = colors.bgElevated,
  label,
  valueText,
  unit,
}: {
  size?: number;
  stroke?: number;
  progress: number;
  color?: string;
  trackColor?: string;
  label?: string;
  valueText?: string;
  unit?: string;
}) {
  const safe = Math.max(0, Math.min(progress, 1.2));
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const dash = c * Math.min(safe, 1);
  return (
    <View style={{ alignItems: 'center' }}>
      <Svg width={size} height={size}>
        <Defs>
          <LinearGradient id={`g-${color}`} x1="0" y1="0" x2="1" y2="1">
            <Stop offset="0" stopColor={color} stopOpacity="1" />
            <Stop offset="1" stopColor={colors.accentSoft} stopOpacity="0.9" />
          </LinearGradient>
        </Defs>
        <Circle cx={size / 2} cy={size / 2} r={r} stroke={trackColor} strokeWidth={stroke} fill="none" />
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          stroke={`url(#g-${color})`}
          strokeWidth={stroke}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={`${dash} ${c}`}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </Svg>
      <View style={[styles.center, { width: size, height: size }]} pointerEvents="none">
        {valueText ? <Text style={styles.value}>{valueText}</Text> : null}
        {unit ? <Text style={styles.unit}>{unit}</Text> : null}
      </View>
      {label ? <Text style={styles.label}>{label}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  center: { position: 'absolute', alignItems: 'center', justifyContent: 'center' },
  value: { color: colors.text, fontSize: 22, fontWeight: '800' },
  unit: { color: colors.textMuted, fontSize: 11, marginTop: 2 },
  label: { color: colors.textMuted, fontSize: 12, marginTop: 6, fontWeight: '600' },
});
