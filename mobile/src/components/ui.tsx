/** Branded UI primitives — glass cards, big buttons, hero typography. */
import React from 'react';
import {
  ActivityIndicator,
  Pressable,
  StyleProp,
  StyleSheet,
  Text,
  TextStyle,
  View,
  ViewStyle,
} from 'react-native';
import { colors, font, radius, shadow, spacing } from '@/theme';

export function Button({
  title,
  onPress,
  loading,
  disabled,
  variant = 'primary',
  size = 'md',
  style,
  icon,
}: {
  title: string;
  onPress: () => void;
  loading?: boolean;
  disabled?: boolean;
  variant?: 'primary' | 'accent' | 'ghost' | 'glass';
  size?: 'md' | 'lg';
  style?: StyleProp<ViewStyle>;
  icon?: React.ReactNode;
}) {
  const bg =
    variant === 'accent' ? colors.accent :
    variant === 'ghost' ? 'transparent' :
    variant === 'glass' ? colors.glassOverlay :
    colors.primary;
  const isDisabled = disabled || loading;
  const height = size === 'lg' ? 58 : 52;
  return (
    <Pressable
      onPress={onPress}
      disabled={isDisabled}
      style={({ pressed }) => [
        styles.btn,
        { backgroundColor: bg, height, opacity: isDisabled ? 0.5 : pressed ? 0.85 : 1 },
        variant === 'ghost' && { borderWidth: 1, borderColor: colors.border },
        variant === 'glass' && { borderWidth: 1, borderColor: colors.borderStrong },
        variant === 'accent' && shadow.glow,
        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={colors.white} />
      ) : (
        <View style={styles.btnRow}>
          {icon}
          <Text style={[styles.btnText, variant === 'ghost' && { color: colors.text }]}>{title}</Text>
        </View>
      )}
    </Pressable>
  );
}

export function Card({
  children,
  style,
  variant = 'solid',
}: {
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
  variant?: 'solid' | 'glass' | 'elevated';
}) {
  const v =
    variant === 'glass' ? styles.cardGlass :
    variant === 'elevated' ? styles.cardElevated :
    styles.card;
  return <View style={[v, style]}>{children}</View>;
}

export function Pill({ label, tone = 'default' }: { label: string; tone?: 'default' | 'accent' | 'mint' }) {
  const color =
    tone === 'accent' ? colors.accentSoft :
    tone === 'mint' ? colors.mint :
    colors.textMuted;
  return (
    <View style={styles.pill}>
      <Text style={[styles.pillText, { color }]}>{label}</Text>
    </View>
  );
}

export function Title({ children, style }: { children: React.ReactNode; style?: StyleProp<TextStyle> }) {
  return <Text style={[font.display, style]}>{children}</Text>;
}

export function Hero({ children, style }: { children: React.ReactNode; style?: StyleProp<TextStyle> }) {
  return <Text style={[font.hero, style]}>{children}</Text>;
}

export function Muted({ children, style }: { children: React.ReactNode; style?: StyleProp<TextStyle> }) {
  return <Text style={[font.small, style]}>{children}</Text>;
}

export function Eyebrow({ children, style }: { children: React.ReactNode; style?: StyleProp<TextStyle> }) {
  return <Text style={[font.micro, style]}>{children}</Text>;
}

const styles = StyleSheet.create({
  btn: {
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.lg,
  },
  btnRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  btnText: { color: colors.white, fontSize: 16, fontWeight: '800', letterSpacing: 0.2 },

  card: {
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cardGlass: {
    backgroundColor: colors.glassOverlay,
    borderRadius: radius.lg,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.borderStrong,
    backdropFilter: 'blur(18px)' as any, // web only — ignored on native
  },
  cardElevated: {
    backgroundColor: colors.cardHi,
    borderRadius: radius.lg,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
    ...shadow.soft,
  },

  pill: {
    alignSelf: 'flex-start',
    backgroundColor: colors.bgElevated,
    borderRadius: radius.pill,
    paddingHorizontal: spacing.md,
    paddingVertical: 6,
    borderWidth: 1,
    borderColor: colors.border,
  },
  pillText: { fontSize: 11, fontWeight: '800', letterSpacing: 0.5 },
});
