import React from 'react';
import { ScrollView, StyleSheet, Text, View, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Card, Muted, Pill, Title } from '@/components/ui';
import { colors, radius, spacing } from '@/theme';

const COURSES = [
  { icon: 'nutrition', title: 'Maîtrise tes macros', days: '5 jours', tag: 'Nutrition' },
  { icon: 'barbell', title: 'Premiers pas en boxing', days: '14 jours', tag: 'Sport' },
  { icon: 'leaf', title: 'Gestion du stress', days: '5 jours', tag: 'Mental' },
  { icon: 'moon', title: 'Sommeil optimal', days: '7 jours', tag: 'Mental' },
  { icon: 'repeat', title: 'Habitudes durables', days: '7 jours', tag: 'Mental' },
  { icon: 'female', title: 'Comprends ton cycle', days: '7 jours', tag: 'Femme' },
] as const;

const TOPICS = [
  'Plateau de poids', 'Manger au restaurant', 'Sommeil & perte de poids',
  'Cycle hormonal', 'Microbiote', 'Longévité', 'Testostérone naturelle',
];

export default function Learn() {
  const router = useRouter();
  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <ScrollView contentContainerStyle={{ padding: spacing.lg }}>
        <Title style={{ marginBottom: spacing.xs }}>Apprendre</Title>
        <Muted style={{ marginBottom: spacing.lg }}>
          Micro-cours et fiches, format 5 min par jour.
        </Muted>

        <Text style={styles.section}>Micro-cours</Text>
        {COURSES.map((c) => (
          <Pressable key={c.title} onPress={() => router.push('/(tabs)')}>
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
            <Pressable key={t} onPress={() => router.push('/(tabs)')} style={styles.topic}>
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
