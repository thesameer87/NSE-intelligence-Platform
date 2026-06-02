import { formatPrice, formatDate } from "../../utils/format";
import type { PortfolioHolding } from "../../types";
import "./PortfolioTable.css";

interface PortfolioTableProps {
  holdings: PortfolioHolding[];
}

/**
 * Presentation component for portfolio holdings.
 * Displays quantity, average buy price, and buy date.
 * No P&L calculation — rendering only what the REST contract delivers.
 */
export function PortfolioTable({ holdings }: PortfolioTableProps) {
  return (
    <div className="portfolio-table-container" role="region" aria-label="Portfolio holdings" tabIndex={0}>
      <table className="portfolio-table">
        <thead>
          <tr>
            <th scope="col" className="portfolio-table__th">Symbol</th>
            <th scope="col" className="portfolio-table__th portfolio-table__th--right">Qty</th>
            <th scope="col" className="portfolio-table__th portfolio-table__th--right">Avg Price</th>
            <th scope="col" className="portfolio-table__th">Buy Date</th>
            <th scope="col" className="portfolio-table__th">Notes</th>
          </tr>
        </thead>
        <tbody>
          {holdings.map((holding) => (
            <tr key={holding.symbol} className="portfolio-table__row">
              <td className="portfolio-table__td portfolio-table__td--symbol">{holding.symbol}</td>
              <td className="portfolio-table__td portfolio-table__td--right portfolio-table__td--mono">
                {holding.quantity.toLocaleString("en-IN")}
              </td>
              <td className="portfolio-table__td portfolio-table__td--right portfolio-table__td--mono">
                {formatPrice(holding.avg_buy_price)}
              </td>
              <td className="portfolio-table__td portfolio-table__td--date">
                {formatDate(holding.buy_date)}
              </td>
              <td className="portfolio-table__td portfolio-table__td--notes">
                {holding.notes ?? <span className="portfolio-table__empty-note" aria-label="No notes">—</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
