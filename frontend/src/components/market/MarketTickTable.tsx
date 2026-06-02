import { formatPrice, formatVolume, formatTime } from "../../utils/format";
import type { IntradayTick } from "../../types";
import "./MarketTickTable.css";

interface MarketTickTableProps {
  ticks: IntradayTick[];
}

/**
 * Presentation component for displaying intraday tick data.
 * Uses deterministic formatting (formatPrice, formatVolume, formatTime).
 * No market logic — renders exactly the data it receives.
 */
export function MarketTickTable({ ticks }: MarketTickTableProps) {
  return (
    <div className="market-tick-table-container" role="region" aria-label="Market tick data" tabIndex={0}>
      <table className="market-tick-table">
        <thead>
          <tr>
            <th scope="col" className="market-tick-table__th">Symbol</th>
            <th scope="col" className="market-tick-table__th market-tick-table__th--right">LTP</th>
            <th scope="col" className="market-tick-table__th market-tick-table__th--right">Bid</th>
            <th scope="col" className="market-tick-table__th market-tick-table__th--right">Ask</th>
            <th scope="col" className="market-tick-table__th market-tick-table__th--right">Volume</th>
            <th scope="col" className="market-tick-table__th">Time</th>
          </tr>
        </thead>
        <tbody>
          {ticks.map((tick) => (
            <tr key={tick.id} className="market-tick-table__row">
              <td className="market-tick-table__td market-tick-table__td--symbol">{tick.symbol}</td>
              <td className="market-tick-table__td market-tick-table__td--right market-tick-table__td--mono">
                {formatPrice(tick.ltp)}
              </td>
              <td className="market-tick-table__td market-tick-table__td--right market-tick-table__td--mono">
                {formatPrice(tick.bid_price)}
              </td>
              <td className="market-tick-table__td market-tick-table__td--right market-tick-table__td--mono">
                {formatPrice(tick.ask_price)}
              </td>
              <td className="market-tick-table__td market-tick-table__td--right market-tick-table__td--mono">
                {formatVolume(tick.volume)}
              </td>
              <td className="market-tick-table__td market-tick-table__td--time">
                {formatTime(tick.timestamp)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
