export function compact(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(n >= 10_000_000 ? 0 : 1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(n >= 10_000 ? 0 : 1) + "k";
  return n.toString();
}

export function fmtEUR(n: number, decimals = 2): string {
  return n.toLocaleString("fr-FR", { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) + " €";
}

export function relativeDate(iso: string): string {
  const d = new Date(iso);
  const diff = Date.now() - d.getTime();
  if (diff < 60_000) return "à l'instant";
  if (diff < 3_600_000) return Math.floor(diff / 60_000) + "min";
  if (diff < 86_400_000) return Math.floor(diff / 3_600_000) + "h";
  if (diff < 7 * 86_400_000) return Math.floor(diff / 86_400_000) + "j";
  return d.toLocaleDateString("fr-FR", { day: "2-digit", month: "short" });
}
