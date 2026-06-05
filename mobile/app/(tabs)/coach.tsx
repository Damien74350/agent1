import React, { useCallback, useRef, useState } from 'react';
import {
  FlatList,
  Image,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import * as Haptics from 'expo-haptics';
import { useFocusEffect } from 'expo-router';
import { api, ApiError, ChatMedia } from '@/api/client';
import { TypingDots } from '@/components/TypingDots';
import { takePendingPrompt, subscribePending } from '@/store/pendingPrompt';
import { colors, radius, spacing } from '@/theme';

type Msg = {
  id: string;
  role: 'user' | 'calo';
  text: string;
  media?: ChatMedia[];
  imageUri?: string;
  pending?: boolean;
};

const WELCOME: Msg = {
  id: 'welcome',
  role: 'calo',
  text:
    "Salut ! 👋 Je suis Calo, ton coach nutrition · sport · mental. " +
    "Envoie-moi une photo de ton repas, parle-moi de ta journée, ou pose-moi " +
    'une question. On avance ensemble 💪',
};

const QUICK_PROMPTS = [
  '📸 Analyse mon repas',
  '🏋️ Programme de la semaine',
  '😴 J\'ai mal dormi',
  '📊 Mon bilan du jour',
];

export default function Chat() {
  const [messages, setMessages] = useState<Msg[]>([WELCOME]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const listRef = useRef<FlatList<Msg>>(null);

  const scrollToEnd = useCallback(() => {
    setTimeout(() => listRef.current?.scrollToEnd({ animated: true }), 80);
  }, []);

  // Other tabs (Learn) can hand us a prompt to send when we focus.
  useFocusEffect(
    useCallback(() => {
      const drain = () => {
        const pending = takePendingPrompt();
        if (pending) send(pending);
      };
      drain();
      return subscribePending(drain);
    }, []),
  );

  async function send(text: string, imageBase64?: string, imageUri?: string) {
    if (!text.trim() && !imageBase64) return;
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    const userMsg: Msg = { id: `u-${Date.now()}`, role: 'user', text, imageUri };
    const typing: Msg = { id: `t-${Date.now()}`, role: 'calo', text: '', pending: true };
    setMessages((m) => [...m, userMsg, typing]);
    setInput('');
    setSending(true);
    scrollToEnd();
    try {
      const res = await api.chat(text, imageBase64);
      // DEBUG: log the full response so we can diagnose any rendering issue.
      console.log('[CALO chat response]', res);
      const rawReply: any = res?.reply;
      const reply: string =
        typeof rawReply === 'string'
          ? rawReply
          : rawReply == null
            ? '(réponse vide du serveur)'
            : `(format inattendu: ${JSON.stringify(rawReply).slice(0, 200)})`;
      setMessages((m) =>
        m.map((msg) =>
          msg.id === typing.id
            ? { ...msg, text: reply, media: res.media ?? [], pending: false }
            : msg,
        ),
      );
      try { Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success); } catch {}
    } catch (e) {
      console.log('[CALO chat error]', e);
      const detail =
        e instanceof ApiError ? e.message :
        e instanceof Error ? e.message :
        'Connexion impossible';
      const safeDetail = typeof detail === 'string' ? detail : JSON.stringify(detail);
      setMessages((m) =>
        m.map((msg) =>
          msg.id === typing.id ? { ...msg, text: `⚠️ ${safeDetail}`, pending: false } : msg,
        ),
      );
    } finally {
      setSending(false);
      scrollToEnd();
    }
  }

  async function pickPhoto() {
    const res = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.7,
      base64: true,
    });
    if (!res.canceled && res.assets[0]?.base64) {
      const asset = res.assets[0];
      send(input || 'Voici une photo 📸', asset.base64!, asset.uri);
    }
  }

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.header}>
        <View>
          <Text style={styles.headerEyebrow}>EN LIGNE</Text>
          <Text style={styles.headerTitle}>Calo</Text>
        </View>
        <View style={styles.statusDot} />
      </View>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 8 : 0}
      >
        <FlatList
          ref={listRef}
          data={messages}
          keyExtractor={(m) => m.id}
          contentContainerStyle={{ padding: spacing.md, paddingBottom: spacing.lg }}
          renderItem={({ item }) => <Bubble msg={item} />}
          onContentSizeChange={scrollToEnd}
          ListFooterComponent={
            messages.length === 1 ? (
              <View style={styles.quickWrap}>
                {QUICK_PROMPTS.map((q) => (
                  <Pressable key={q} style={styles.quick} onPress={() => send(q.replace(/^\S+\s/, ''))}>
                    <Text style={styles.quickText}>{q}</Text>
                  </Pressable>
                ))}
              </View>
            ) : null
          }
        />
        <View style={styles.inputBar}>
          <Pressable onPress={pickPhoto} style={styles.iconBtn} hitSlop={8}>
            <Ionicons name="camera" size={24} color={colors.accentSoft} />
          </Pressable>
          <TextInput
            style={styles.input}
            placeholder="Écris à Calo…"
            placeholderTextColor={colors.textMuted}
            value={input}
            onChangeText={setInput}
            multiline
          />
          <Pressable
            onPress={() => send(input)}
            disabled={sending || !input.trim()}
            style={[styles.sendBtn, { opacity: sending || !input.trim() ? 0.4 : 1 }]}
          >
            <Ionicons name="send" size={20} color={colors.white} />
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

function Bubble({ msg }: { msg: Msg }) {
  const isUser = msg.role === 'user';
  return (
    <View style={[styles.row, { justifyContent: isUser ? 'flex-end' : 'flex-start' }]}>
      <View
        style={[
          styles.bubble,
          isUser ? styles.bubbleUser : styles.bubbleCalo,
          { maxWidth: '82%' },
        ]}
      >
        {msg.imageUri && <Image source={{ uri: msg.imageUri }} style={styles.bubbleImage} />}
        {msg.pending ? (
          <TypingDots />
        ) : (
          <Text style={[styles.bubbleText, isUser && { color: colors.white }]}>
            {typeof msg.text === 'string' ? msg.text : JSON.stringify(msg.text)}
          </Text>
        )}
        {msg.media?.map((m, i) => (
          <Image key={i} source={{ uri: m.url }} style={styles.mediaImage} />
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  headerEyebrow: { color: colors.success, fontSize: 10, fontWeight: '800', letterSpacing: 1.5 },
  headerTitle: { color: colors.text, fontSize: 28, fontWeight: '900', letterSpacing: -0.8 },
  statusDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: colors.success,
    shadowColor: colors.success,
    shadowOpacity: 0.8,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 0 },
  },
  row: { flexDirection: 'row', marginVertical: 6 },
  bubble: { borderRadius: 22, padding: spacing.md, paddingHorizontal: spacing.lg },
  bubbleUser: { backgroundColor: colors.bubbleUser, borderBottomRightRadius: 6 },
  bubbleCalo: {
    backgroundColor: colors.bubbleCalo,
    borderBottomLeftRadius: 6,
    borderWidth: 1,
    borderColor: colors.border,
  },
  bubbleText: { color: colors.text, fontSize: 16, lineHeight: 23, fontWeight: '500' },
  bubbleImage: { width: 200, height: 200, borderRadius: radius.md, marginBottom: spacing.sm },
  mediaImage: { width: 220, height: 220, borderRadius: radius.md, marginTop: spacing.sm },
  inputBar: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: spacing.sm,
    gap: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    backgroundColor: colors.bgElevated,
  },
  iconBtn: { padding: spacing.sm },
  input: {
    flex: 1,
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    color: colors.text,
    fontSize: 16,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    maxHeight: 120,
  },
  sendBtn: {
    backgroundColor: colors.accent,
    width: 46,
    height: 46,
    borderRadius: 23,
    alignItems: 'center',
    justifyContent: 'center',
  },
  quickWrap: {
    flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm,
    paddingHorizontal: spacing.sm, paddingTop: spacing.md,
  },
  quick: {
    backgroundColor: colors.card, borderRadius: radius.pill,
    paddingHorizontal: spacing.md, paddingVertical: spacing.sm,
    borderWidth: 1, borderColor: colors.border,
  },
  quickText: { color: colors.text, fontSize: 14, fontWeight: '600' },
});
