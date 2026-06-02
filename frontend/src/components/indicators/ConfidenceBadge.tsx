import { formatConfidence } from "../../utils/format";
import "./ConfidenceBadge.css";

interface ConfidenceBadgeProps {
  value: number | null | undefined; // 0.0 – 1.0
}

/**
 * Renders a confidence ratio as a styled percentage pill.
 * Presentation-only — no business classification.
 */
export function ConfidenceBadge({ value }: ConfidenceBadgeProps) {
  return (
    <span
      className="confidence-badge"
      aria-label={`Confidence: ${formatConfidence(value)}`}
    >
      {formatConfidence(value)}
    </span>
  );
}
