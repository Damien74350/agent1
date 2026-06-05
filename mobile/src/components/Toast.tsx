/** Minimal global toast — push from anywhere via showToast(message). */
import React, { useEffect, useRef, useState } from 'react';
import { Animated, StyleSheet, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, radius, spacing } from '@/theme';

type ToastItem = { id: number; message: string };
let push: ((m: string) => void) | null = null;

export function showToast(message: string) {
  push?.(message);
}

export function ToastHost() {
  const [items, setItems] = useState<ToastItem[]>([]);
  const idRef = useRef(0);

  useEffect(() => {
    push = (message: string) => {
      const id = ++idRef.current;
      setItems((it) => [...it, { id, message }]);
      setTimeout(() => setItems((it) => it.filter((t) => t.id !== id)), 3200);
    };
    return () => {
      push = null;
    };
  }, []);

  if (items.length === 0) return null;
  return (
    <SafeAreaView pointerEvents="none" style={styles.host} edges={['top']}>
      {items.map((t) => (
        <ToastBubble key={t.id} message={t.message} />
      ))}
    </SafeAreaView>
  );
}

function ToastBubble({ message }: { message: string }) {
  const anim = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.spring(anim, { toValue: 1, useNativeDriver: true, tension: 80, friction: 9 }).start();
  }, []);
  return (
    <Animated.View
      style={[
        styles.bubble,
        {
          opacity: anim,
          transform: [{ translateY: anim.interpolate({ inputRange: [0, 1], outputRange: [-40, 0] }) }],
        },
      ]}
    >
      <Text style={styles.text}>{message}</Text>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  host: { position: 'absolute', top: 0, left: 0, right: 0, alignItems: 'center', zIndex: 1000 },
  bubble: {
    marginTop: spacing.sm,
    backgroundColor: colors.bgElevated,
    borderRadius: radius.pill,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
    maxWidth: '90%',
  },
  text: { color: colors.text, fontSize: 14, fontWeight: '600', textAlign: 'center' },
});
