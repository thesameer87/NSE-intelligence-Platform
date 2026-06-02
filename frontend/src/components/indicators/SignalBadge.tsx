import "./SignalBadge.css";

interface SignalBadgeProps {
  signal: string;
}

type SignalVariant = "bullish" | "bearish" | "neutral";

function resolveVariant(signal: string): SignalVariant {
  const lower = signal.toLowerCase();
  if (lower.includes("bull") || lower === "buy" || lower === "long") return "bullish";
  if (lower.includes("bear") || lower === "sell" || lower === "short") return "bearish";
  return "neutral";
}

/**
 * Renders a signal direction label as a styled pill.
 * Variant is derived from the signal string — presentation-only.
 * No signal generation logic; purely maps received text to visual tier.
 */
export function SignalBadge({ signal }: SignalBadgeProps) {
  const variant = resolveVariant(signal);
  return (
    <span
      className={`signal-badge signal-badge--${variant}`}
      aria-label={`Signal: ${signal}`}
    >
      {signal}
    </span>
  );
}
