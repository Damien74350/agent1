import React from 'react';
import { Alert, ScrollView, StyleSheet, Text, View, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Card, Muted, Pill, Title } from '@/components/ui';
import { setPendingPrompt } from '@/store/pendingPrompt';
import { colors, radius, spacing } from '@/theme';

type Course = { icon: string; title: string; days: string; tag: string; slug: string };
const COURSES: Course[] = [
  { icon: 'nutrition', title: 'Maîtrise tes macros', days: '5 jours', tag: 'Nutrition', slug: 'macros-5j' },
  { icon: 'barbell', title: 'Premiers pas en boxing', days: '14 jours', tag: 'Sport', slug: 'boxing-init-14j' },
  { icon: 'leaf', title: 'Gestion du stress', days: '5 jours', tag: 'Mental', slug: 'stress-5j' },
  { icon: 'moon', title: 'Sommeil optimal', days: '7 jours', tag: 'Mental', slug: 'sommeil-7j' },
  { icon: 'repeat', title: 'Habitudes durables', days: '7 jours', tag: 'Mental', slug: 'habitudes-7j' },
  { icon: 'female', title: 'Comprends ton cycle', days: '7 jours', tag: 'Femme', slug: 'cycle-7j' },
];

const TOPICS = [
  'Plateau de poids', 'Manger au restaurant', 'Sommeil & perte de poids',
  'Cycle hormonal', 'Microbiote', 'Longévité', 'Testostérone naturelle',
];

export default function Learn() {
  const router = useRouter();
  const startCourse = (c: Course) => {
    setPendingPrompt(`Démarre le micro-cours ${c.slug} : ${c.title}`);
    router.push('/(tabs)');
  };
  const askTopic = (t: string) => {
    setPendingPrompt(`Parle-moi de : ${t}`);
    router.push('/(tabs)');
  };
  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <ScrollView contentContainerStyle={{ padding: spacing.lg }}>
        <Title style={{ marginBottom: spacing.xs }}>Apprendre</Title>
        <Muted style={{ marginBottom: spacing.lg }}>
          Micro-cours et fiches, format 5 min par jour.
        </Muted>

        <Text style={styles.section}>Micro-cours</Text>
        {COURSES.map((c) => (
          <Pressable key={c.title} onPress={() => startCourse(c)}>
            <Card style={styles.courseCard}>
              <View style={styles.iconWrap}>
                <Ionicons name={c.icon as any} size={22} color={colors.accentSoft} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.courseTitle}>{c.title}</Text>
                <Muted>{c.days}</Muted>
              </View>
              <Pill label={c.tag} />
            </Card>
          </Pressable>
        ))}

        <Text style={[styles.section, { marginTop: spacing.lg }]}>Sujets populaires</Text>
        <View style={styles.topicsWrap}>
          {TOPICS.map((t) => (
            <Pressable key={t} onPress={() => askTopic(t)} style={styles.topic}>
              <Text style={styles.topicText}>{t}</Text>
            </Pressable>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  section: { color: colors.text, fontSize: 17, fontWeight: '700', marginBottom: spacing.sm },
  courseCard: { flexDirection: 'row', alignItems: 'center', marginBottom: spacing.sm, gap: spacing.md },
  iconWrap: {
    width: 44, height: 44, borderRadius: radius.md, backgroundColor: colors.bgElevated,
    alignItems: 'center', justifyContent: 'center',
  },
  courseTitle: { color: colors.text, fontSize: 16, fontWeight: '700' },
  topicsWrap: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  topic: {
    backgroundColor: colors.card, borderRadius: radius.pill, paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm, borderWidth: 1, borderColor: colors.border,
  },
  topicText: { color: colors.text, fontSize: 14 },
});
