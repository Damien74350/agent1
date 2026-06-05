/** First-launch onboarding — 3 swipeable slides à la Apple. Shown before login,
 * once. We persist a "seen" flag in storage so it never appears again. */
import React, { useEffect, useRef, useState } from 'react';
import {
  Animated,
  Dimensions,
  Easing,
  NativeScrollEvent,
  NativeSyntheticEvent,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Button, Muted } from '@/components/ui';
import { storage } from '@/store/storage';
import { colors, radius, spacing } from '@/theme';

const SEEN_KEY = 'calo.onboarding.seen';
const { width } = Dimensions.get('window');

const SLIDES = [
  {
    icon: 'sparkles',
    title: 'Coach IA · 24/7',
    body: 'Calo est ton coach nutrition, sport et mental — disponible nuit et jour, à un message près.',
  },
  {
    icon: 'camera',
    title: 'Photo, vocal, texte',
    body: 'Photo de repas, message vocal, ou écrit : Calo lit, analyse, et adapte ton plan à toi.',
  },
  {
    icon: 'heart',
    title: 'Tes données te suivent',
    body: 'WhatsApp ou app, tout est synchronisé. Ton profil évolue chaque semaine, calibré par tes vrais résultats.',
  },
] as const;

export default function Onboarding() {
  const router = useRouter();
  const [index, setIndex] = useState(0);

  const onScroll = (e: NativeSyntheticEvent<NativeScrollEvent>) => {
    const i = Math.round(e.nativeEvent.contentOffset.x / width);
    if (i !== index) setIndex(i);
  };

  const finish = async () => {
    try { await storage.setItemAsync(SEEN_KEY, '1'); } catch {}
    router.replace('/login');
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      <ScrollView
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onScroll={onScroll}
        scrollEventThrottle={16}
        style={{ flex: 1 }}
      >
        {SLIDES.map((s, i) => (
          <Slide key={i} {...s} active={i === index} />
        ))}
      </ScrollView>

      <View style={styles.footer}>
        <View style={styles.dots}>
          {SLIDES.map((_, i) => (
            <View key={i} style={[styles.dot, index === i && styles.dotActive]} />
          ))}
        </View>
        <Button
          title={index === SLIDES.length - 1 ? 'Démarrer' : 'Suivant'}
          variant="accent"
          onPress={() => {
            if (index === SLIDES.length - 1) finish();
            else setIndex(index + 1);
          }}
        />
        <Pressable onPress={finish} hitSlop={8}>
          <Muted style={styles.skip}>Passer</Muted>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

function Slide({ icon, title, body, active }: { icon: any; title: string; body: string; active: boolean }) {
  const anim = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.timing(anim, {
      toValue: active ? 1 : 0,
      duration: 480,
      useNativeDriver: true,
      easing: Easing.out(Easing.cubic),
    }).start();
  }, [active]);

  return (
    <View style={[styles.slide, { width }]}>
      <Animated.View
        style={{
          opacity: anim,
          transform: [{ translateY: anim.interpolate({ inputRange: [0, 1], outputRange: [20, 0] }) }],
        }}
      >
        <View style={styles.iconBubble}>
          <Ionicons name={icon} size={64} color={colors.white} />
        </View>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.body}>{body}</Text>
      </Animated.View>
    </View>
  );
}

export async function shouldShowOnboarding(): Promise<boolean> {
  try {
    const v = await storage.getItemAsync(SEEN_KEY);
    return !v;
  } catch {
    return true;
  }
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  slide: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: spacing.xl },
  iconBubble: {
    width: 140, height: 140, borderRadius: 70, backgroundColor: colors.primary,
    alignItems: 'center', justifyContent: 'center', alignSelf: 'center', marginBottom: spacing.xl,
    shadowColor: colors.accent, shadowOpacity: 0.4, shadowRadius: 24, shadowOffset: { width: 0, height: 8 },
  },
  title: { color: colors.text, fontSize: 30, fontWeight: '900', textAlign: 'center', marginBottom: spacing.md },
  body: { color: colors.textMuted, fontSize: 17, lineHeight: 24, textAlign: 'center', paddingHorizontal: spacing.lg },

  footer: { padding: spacing.lg, gap: spacing.md },
  dots: { flexDirection: 'row', justifyContent: 'center', gap: 6 },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: colors.border },
  dotActive: { backgroundColor: colors.accent, width: 24 },
  skip: { textAlign: 'center', paddingVertical: spacing.sm },
});
