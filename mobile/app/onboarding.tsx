/** First-launch onboarding — 3 swipeable hero slides à la Apple. */
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
import { Aurora } from '@/components/Aurora';
import { Button, Eyebrow, Hero, Muted } from '@/components/ui';
import { storage } from '@/store/storage';
import { colors, radius, shadow, spacing } from '@/theme';

const SEEN_KEY = 'calo.onboarding.seen';
const { width } = Dimensions.get('window');

const SLIDES = [
  {
    icon: 'sparkles',
    eyebrow: 'Bienvenue',
    title: 'Ton coach\nde poche.',
    body: 'Calo coach nutrition, sport et mental en un seul agent. Disponible 24/7 par texte, photo, voix.',
  },
  {
    icon: 'camera',
    eyebrow: 'Multimodal',
    title: 'Une photo.\nUne analyse.',
    body: 'Repas, morpho, étiquettes, bilans sanguins — Calo lit tes photos et adapte ton plan instantanément.',
  },
  {
    icon: 'pulse',
    eyebrow: 'Sur-mesure',
    title: 'Évolue\navec toi.',
    body: 'Ton profil se calibre chaque semaine sur tes vrais résultats. WhatsApp et app, tout synchronisé.',
  },
] as const;

export default function Onboarding() {
  const router = useRouter();
  const [index, setIndex] = useState(0);
  const scrollRef = useRef<ScrollView>(null);

  const onScroll = (e: NativeSyntheticEvent<NativeScrollEvent>) => {
    const i = Math.round(e.nativeEvent.contentOffset.x / width);
    if (i !== index) setIndex(i);
  };

  const finish = async () => {
    try { await storage.setItemAsync(SEEN_KEY, '1'); } catch {}
    router.replace('/login');
  };

  const next = () => {
    if (index === SLIDES.length - 1) finish();
    else scrollRef.current?.scrollTo({ x: (index + 1) * width, animated: true });
  };

  return (
    <View style={styles.root}>
      <Aurora />
      <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
        <ScrollView
          ref={scrollRef}
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
            title={index === SLIDES.length - 1 ? 'Commencer' : 'Continuer'}
            variant="accent"
            size="lg"
            onPress={next}
          />
          <Pressable onPress={finish} hitSlop={10}>
            <Muted style={styles.skip}>Passer</Muted>
          </Pressable>
        </View>
      </SafeAreaView>
    </View>
  );
}

function Slide({ icon, eyebrow, title, body, active }: { icon: any; eyebrow: string; title: string; body: string; active: boolean }) {
  const anim = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.timing(anim, {
      toValue: active ? 1 : 0,
      duration: 600,
      useNativeDriver: true,
      easing: Easing.out(Easing.cubic),
    }).start();
  }, [active]);

  return (
    <View style={[styles.slide, { width }]}>
      <Animated.View
        style={{
          opacity: anim,
          transform: [{ translateY: anim.interpolate({ inputRange: [0, 1], outputRange: [28, 0] }) }],
        }}
      >
        <View style={styles.iconBubble}>
          <Ionicons name={icon} size={72} color={colors.accent} />
        </View>
        <Eyebrow style={{ textAlign: 'center', color: colors.accentSoft, marginBottom: spacing.sm }}>{eyebrow}</Eyebrow>
        <Hero style={styles.title}>{title}</Hero>
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
  root: { flex: 1, backgroundColor: colors.bg },
  safe: { flex: 1 },
  slide: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: spacing.xl },
  iconBubble: {
    width: 160, height: 160, borderRadius: 80,
    backgroundColor: 'rgba(255,107,53,0.15)',
    borderWidth: 1, borderColor: 'rgba(255,107,53,0.4)',
    alignItems: 'center', justifyContent: 'center', alignSelf: 'center',
    marginBottom: spacing.xl,
    ...shadow.glow,
  },
  title: { textAlign: 'center', marginBottom: spacing.md, fontSize: 48, letterSpacing: -2 },
  body: { color: colors.textMuted, fontSize: 17, lineHeight: 26, textAlign: 'center', paddingHorizontal: spacing.lg },

  footer: { padding: spacing.lg, gap: spacing.md },
  dots: { flexDirection: 'row', justifyContent: 'center', gap: 6 },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: colors.border },
  dotActive: { backgroundColor: colors.accent, width: 28 },
  skip: { textAlign: 'center', paddingVertical: spacing.sm },
});
