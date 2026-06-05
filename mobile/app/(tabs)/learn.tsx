/** Apprendre — micro-courses, sujets, et recherche live dans 200+ fiches Calo. */
import React, { useEffect, useState, useCallback } from 'react';
import {
  ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, TextInput, View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { api, ApiError, KnowledgeHit } from '@/api/client';
import { Card, Muted, Pill, Title } from '@/components/ui';
import { showToast } from '@/components/Toast';
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
  'Mobilité et dos', 'Immunité', 'Cognition',
];

export default function Learn() {
  const router = useRouter();
  const [q, setQ] = useState('');
  const [hits, setHits] = useState<KnowledgeHit[]>([]);
  const [searching, setSearching] = useState(false);

  // Debounced search — 300ms after the last keystroke.
  useEffect(() => {
    const query = q.trim();
    if (query.length < 2) { setHits([]); return; }
    setSearching(true);
    const t = setTimeout(async () => {
      try {
        const res = await api.searchKnowledge(query);
        setHits(res.hits);
      } catch (e) {
        if (e instanceof ApiError && e.status !== 401) showToast(e.message);
      } finally {
        setSearching(false);
      }
    }, 300);
    return () => clearTimeout(t);
  }, [q]);

  const askCalo = useCallback((text: string) => {
    setPendingPrompt(text);
    router.push('/(tabs)/coach');
  }, [router]);

  const showResults = q.trim().length >= 2;

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <ScrollView contentContainerStyle={{ padding: spacing.lg }} keyboardShouldPersistTaps="handled">
        <Title style={{ marginBottom: spacing.xs }}>Apprendre</Title>
        <Muted style={{ marginBottom: spacing.md }}>
          Micro-cours, fiches & 200+ articles validés scientifiquement.
        </Muted>

        <View style={styles.searchBar}>
          <Ionicons name="search" size={18} color={colors.textMuted} />
          <TextInput
            value={q}
            onChangeText={setQ}
            placeholder="Cherche un sujet : sommeil, plateau, SOPK…"
            placeholderTextColor={colors.textMuted}
            style={styles.searchInput}
            returnKeyType="search"
            autoCorrect={false}
          />
          {searching ? <ActivityIndicator color={colors.accent} size="small" /> : null}
          {q.length > 0 && !searching && (
            <Pressable onPress={() => setQ('')} hitSlop={8}>
              <Ionicons name="close-circle" size={20} color={colors.textMuted} />
            </Pressable>
          )}
        </View>

        {showResults ? (
          <View style={{ marginTop: spacing.md }}>
            {hits.length === 0 && !searching ? (
              <Muted style={{ textAlign: 'center', paddingVertical: spacing.lg }}>
                Aucun résultat — demande directement à Calo, il connaît la réponse.
              </Muted>
            ) : (
              hits.map((h, i) => (
                <Pressable key={i} onPress={() => askCalo(`Explique-moi en détail : ${h.title}`)}>
                  <Card style={styles.resultCard}>
                    <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 4, gap: spacing.sm }}>
                      <Text style={styles.resultTitle}>{h.title}</Text>
                    </View>
                    {!!h.topic && <Pill label={h.topic} />}
                    <Text style={styles.resultSnippet} numberOfLines={3}>{h.snippet}</Text>
                  </Card>
                </Pressable>
              ))
            )}
          </View>
        ) : (
          <>
            <Text style={[styles.section, { marginTop: spacing.md }]}>Micro-cours</Text>
            {COURSES.map((c) => (
              <Pressable key={c.title} onPress={() => askCalo(`Démarre le micro-cours ${c.slug} : ${c.title}`)}>
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
                <Pressable key={t} onPress={() => askCalo(`Parle-moi de : ${t}`)} style={styles.topic}>
                  <Text style={styles.topicText}>{t}</Text>
                </Pressable>
              ))}
            </View>
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  section: { color: colors.text, fontSize: 17, fontWeight: '700', marginBottom: spacing.sm },

  searchBar: {
    flexDirection: 'row', alignItems: 'center', gap: spacing.sm,
    backgroundColor: colors.card, borderRadius: radius.md,
    borderWidth: 1, borderColor: colors.border,
    paddingHorizontal: spacing.md, height: 50,
  },
  searchInput: { flex: 1, color: colors.text, fontSize: 16 },

  resultCard: { marginBottom: spacing.sm, gap: 4 },
  resultTitle: { color: colors.text, fontSize: 15, fontWeight: '700', flex: 1 },
  resultSnippet: { color: colors.textMuted, fontSize: 13, lineHeight: 18, marginTop: 4 },

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
