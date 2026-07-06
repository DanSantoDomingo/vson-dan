// Small placeholder brand mark — swap the SVG path for your own glyph.
export function Logo({ className = "h-7 w-7" }: { className?: string }) {
  return (
    <span
      className={`inline-flex items-center justify-center rounded-lg bg-black ring-1 ring-white/15 ${className}`}
    >
      <svg className="h-[55%] w-[55%]" viewBox="0 0 32 32" fill="none">
        <path
          d="M8.6 9.4 16 23.2 23.4 9.4"
          stroke="#ffffff"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </span>
  );
}
