/** ScreenContainer — keeps the mobile UI looking right on a desktop browser
 * by capping the width to a phone-friendly 540px and centring horizontally.
 * On native it's a transparent passthrough. */
import React from 'react';
import { Platform, StyleProp, StyleSheet, View, ViewStyle } from 'react-native';
import { colors } from '@/theme';

const MAX_W = 540;

export function ScreenContainer({
  children,
  style,
}: {
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
}) {
  if (Platform.OS !== 'web') {
    return <View style={[styles.full, style]}>{children}</View>;
  }
  return (
    <View style={styles.outer}>
      <View style={[styles.inner, style]}>{children}</View>
    </View>
  );
}

const styles = StyleSheet.create({
  full: { flex: 1, backgroundColor: colors.bg },
  outer: { flex: 1, alignItems: 'center', backgroundColor: colors.bg },
  inner: {
    flex: 1,
    width: '100%',
    maxWidth: MAX_W,
    backgroundColor: colors.bg,
  },
});
