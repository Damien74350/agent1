/** Tiny in-memory channel so other tabs (Learn) can ask the Chat tab to
 * auto-send a message when it next focuses. No external store needed. */

let _pending: string | null = null;
const listeners = new Set<() => void>();

export function setPendingPrompt(text: string) {
  _pending = text;
  listeners.forEach((l) => l());
}

export function takePendingPrompt(): string | null {
  const v = _pending;
  _pending = null;
  return v;
}

export function subscribePending(cb: () => void) {
  listeners.add(cb);
  return () => listeners.delete(cb);
}
