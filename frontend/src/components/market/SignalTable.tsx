import { SignalBadge } from "../indicators/SignalBadge";
import { ConfidenceBadge } from "../indicators/ConfidenceBadge";
import { formatPrice, formatDate } from "../../utils/format";
import type { TradingSignal } from "../../types";
import "./SignalTable.css";

interface SignalTableProps {
  signals: TradingSignal[];
}

/**
 * Presentation component for displaying trading signals.
 * Uses SignalBadge and ConfidenceBadge for visual indicators.
 * No signal generation — renders exactly what the backend delivers.
 */
export function SignalTable({ signals }: SignalTableProps) {
  return (
    <div className="signal-table-container" role="region" aria-label="Trading signals" tabIndex={0}>
      <table className="signal-table">
        <thead>
          <tr>
            <th scope="col" className="signal-table__th">Symbol</th>
            <th scope="col" className="signal-table__th">Signal</th>
            <th scope="col" className="signal-table__th signal-table__th--right">Confidence</th>
            <th scope="col" className="signal-table__th signal-table__th--right">Target</th>
            <th scope="col" className="signal-table__th">Source</th>
            <th scope="col" className="signal-table__th">Date</th>
          </tr>
        </thead>
        <tbody>
          {signals.map((sig) => (
            <tr key={sig.id} className="signal-table__row">
              <td className="signal-table__td signal-table__td--symbol">{sig.symbol}</td>
              <td className="signal-table__td">
                <SignalBadge signal={sig.signal} />
              </td>
              <td className="signal-table__td signal-table__td--right">
                <ConfidenceBadge value={sig.confidence} />
              </td>
              <td className="signal-table__td signal-table__td--right signal-table__td--mono">
                {formatPrice(sig.target_price)}
              </td>
              <td className="signal-table__td signal-table__td--source">{sig.prediction_source}</td>
              <td className="signal-table__td signal-table__td--date">{formatDate(sig.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
