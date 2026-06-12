export function Logo({ size = 28 }: { size?: number }) {
  return (
    <div className="flex items-center gap-2">
      <div
        className="grid place-items-center rounded-lg rose-gradient font-black text-black"
        style={{ width: size, height: size, fontSize: size * 0.55 }}
      >
        u
      </div>
      <span className="font-black tracking-tight text-lg lowercase">
        un<span className="rose-text">blur</span>
      </span>
    </div>
  );
}
