/**
 * Deterministic number formatting utilities.
 * All formatters are pure functions with no side-effects.
 * Uses Intl.NumberFormat for locale-aware, deterministic output.
 */

const INR_FORMATTER = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const VOLUME_FORMATTER = new Intl.NumberFormat("en-IN", {
  notation: "compact",
  compactDisplay: "short",
  maximumFractionDigits: 1,
});

const PERCENT_FORMATTER = new Intl.NumberFormat("en-IN", {
  style: "percent",
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

/** Format a price value as Indian Rupees. Returns "—" for null/undefined/NaN. */
export function formatPrice(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) return "—";
  return INR_FORMATTER.format(value);
}

/** Format a volume count in compact notation (e.g. 1.2M). Returns "—" for null/NaN. */
export function formatVolume(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) return "—";
  return VOLUME_FORMATTER.format(value);
}

/** Format a decimal confidence ratio as a percentage string (e.g. 0.85 → 85.0%). */
export function formatConfidence(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) return "—";
  return PERCENT_FORMATTER.format(value);
}

/** Format an ISO timestamp string to a short local time string. */
export function formatTime(isoString: string): string {
  const d = new Date(isoString);
  if (isNaN(d.getTime())) return isoString;
  return d.toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

/** Format an ISO timestamp string to a short local date string. */
export function formatDate(isoString: string): string {
  const d = new Date(isoString);
  if (isNaN(d.getTime())) return isoString;
  return d.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}
