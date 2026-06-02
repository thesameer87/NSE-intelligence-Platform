import "./PriceChange.css";

interface PriceChangeProps {
  value: number | null;
  formatted: string;
}

/**
 * Renders a price/numeric value with directional colour semantics.
 * Positive → success green. Negative → error red. Zero/null → neutral.
 * Presentation-only — no business logic.
 */
export function PriceChange({ value, formatted }: PriceChangeProps) {
  const direction: "positive" | "negative" | "neutral" =
    value == null ? "neutral" : value > 0 ? "positive" : value < 0 ? "negative" : "neutral";

  const arrow = direction === "positive" ? "▲" : direction === "negative" ? "▼" : "";

  return (
    <span
      className={`price-change price-change--${direction}`}
      aria-label={`${direction === "neutral" ? "" : direction + " "} ${formatted}`}
    >
      {arrow && <span className="price-change__arrow" aria-hidden="true">{arrow}</span>}
      {formatted}
    </span>
  );
}
