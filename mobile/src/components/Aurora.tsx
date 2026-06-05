/** Aurora — subtle animated mesh-gradient background for hero screens
 * (login, onboarding, splash). Pure RN — no extra dep, uses two soft blobs
 * that drift slowly under the content. */
import React, { useEffect, useRef } from 'react';
import { Animated, Easing, StyleSheet, View, Dimensions } from 'react-native';
import { colors } from '@/theme';

const { width, height } = Dimensions.get('window');

export function Aurora() {
  const a = useRef(new Animated.Value(0)).current;
  const b = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const loopA = Animated.loop(
      Animated.sequence([
        Animated.timing(a, { toValue: 1, duration: 9000, easing: Easing.inOut(Easing.sin), useNativeDriver: true }),
        Animated.timing(a, { toValue: 0, duration: 9000, easing: Easing.inOut(Easing.sin), useNativeDriver: true }),
      ]),
    );
    const loopB = Animated.loop(
      Animated.sequence([
        Animated.timing(b, { toValue: 1, duration: 12000, easing: Easing.inOut(Easing.sin), useNativeDriver: true }),
        Animated.timing(b, { toValue: 0, duration: 12000, easing: Easing.inOut(Easing.sin), useNativeDriver: true }),
      ]),
    );
    loopA.start();
    loopB.start();
    return () => { loopA.stop(); loopB.stop(); };
  }, []);

  return (
    <View pointerEvents="none" style={[StyleSheet.absoluteFill, { zIndex: 0 }]}>
      <Animated.View
        pointerEvents="none"
        style={[
          styles.blob,
          {
            backgroundColor: colors.accent,
            transform: [
              { translateX: a.interpolate({ inputRange: [0, 1], outputRange: [-60, 60] }) },
              { translateY: a.interpolate({ inputRange: [0, 1], outputRange: [-30, 30] }) },
            ],
            top: -height * 0.15,
            left: -width * 0.3,
          },
        ]}
      />
      <Animated.View
        pointerEvents="none"
        style={[
          styles.blob,
          {
            backgroundColor: colors.violet,
            transform: [
              { translateX: b.interpolate({ inputRange: [0, 1], outputRange: [40, -40] }) },
              { translateY: b.interpolate({ inputRange: [0, 1], outputRange: [40, -40] }) },
            ],
            bottom: -height * 0.2,
            right: -width * 0.4,
            opacity: 0.55,
          },
        ]}
      />
      <View pointerEvents="none" style={styles.veil} />
    </View>
  );
}

const styles = StyleSheet.create({
  blob: {
    position: 'absolute',
    width: width * 1.1,
    height: width * 1.1,
    borderRadius: width,
    opacity: 0.32,
    // 'filter' is web-only and silently ignored on native
    filter: 'blur(80px)' as any,
  },
  veil: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(7,11,20,0.4)' },
});
