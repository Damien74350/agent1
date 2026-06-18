/** Subtle animated background blobs — visual hook for the landing. */
export function Aurora() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="absolute -left-1/3 -top-1/4 h-[60vw] w-[60vw] rounded-full bg-accent/30 blur-[120px] animate-aurora-1" />
      <div className="absolute -right-1/3 -bottom-1/4 h-[60vw] w-[60vw] rounded-full bg-violet/30 blur-[120px] animate-aurora-2" />
      <div className="absolute inset-0 bg-bg/60" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_50%,rgba(0,0,0,0.6)_100%)]" />
    </div>
  );
}
