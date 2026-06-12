import { ReactNode } from "react";

export function Card({ children, className = "", title, subtitle, right }: { children: ReactNode; className?: string; title?: ReactNode; subtitle?: ReactNode; right?: ReactNode }) {
  return (
    <section className={`glass rounded-2xl p-5 ${className}`}>
      {(title || right) && (
        <header className="flex items-start justify-between gap-3 mb-4">
          <div>
            {title && <h3 className="text-base font-bold">{title}</h3>}
            {subtitle && <p className="text-xs text-muted mt-0.5">{subtitle}</p>}
          </div>
          {right}
        </header>
      )}
      {children}
    </section>
  );
}

export function Stat({ label, value, hint, trend, icon }: { label: string; value: ReactNode; hint?: ReactNode; trend?: number; icon?: ReactNode }) {
  return (
    <div className="glass rounded-2xl p-4">
      <div className="flex items-center justify-between">
        <p className="text-xs uppercase tracking-wider text-muted">{label}</p>
        {icon && <div className="text-muted">{icon}</div>}
      </div>
      <p className="mt-2 text-2xl sm:text-3xl font-black tracking-tight">{value}</p>
      <div className="mt-1 flex items-center gap-2 text-xs">
        {typeof trend === "number" && (
          <span className={trend >= 0 ? "text-success" : "text-danger"}>
            {trend >= 0 ? "▲" : "▼"} {Math.abs(trend).toFixed(1)}%
          </span>
        )}
        {hint && <span className="text-muted">{hint}</span>}
      </div>
    </div>
  );
}

export function Pill({ children, color = "muted" }: { children: ReactNode; color?: "rose" | "sun" | "sky" | "violet" | "success" | "muted" }) {
  const map: Record<string, string> = {
    rose: "bg-rose/15 text-rose ring-rose/30",
    sun: "bg-sun/15 text-sun ring-sun/30",
    sky: "bg-sky/15 text-sky ring-sky/30",
    violet: "bg-violet/15 text-violet ring-violet/30",
    success: "bg-success/15 text-success ring-success/30",
    muted: "bg-white/5 text-muted ring-white/10",
  };
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ring-1 ${map[color]}`}>
      {children}
    </span>
  );
}
