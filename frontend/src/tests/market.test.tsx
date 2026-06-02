import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { PriceChange } from "../components/indicators/PriceChange";
import { ConfidenceBadge } from "../components/indicators/ConfidenceBadge";
import { SignalBadge } from "../components/indicators/SignalBadge";
import { MarketTickTable } from "../components/market/MarketTickTable";
import { SignalTable } from "../components/market/SignalTable";
import { PortfolioTable } from "../components/market/PortfolioTable";
import { formatPrice, formatVolume, formatConfidence, formatTime, formatDate } from "../utils/format";
import type { IntradayTick, TradingSignal, PortfolioHolding } from "../types";

// ─── Format Utilities ──────────────────────────────────────────────────────

describe("formatPrice", () => {
  it("formats a valid price in INR", () => {
    const result = formatPrice(20000);
    expect(result).toContain("20,000");
  });

  it("returns '—' for null", () => {
    expect(formatPrice(null)).toBe("—");
  });

  it("returns '—' for undefined", () => {
    expect(formatPrice(undefined)).toBe("—");
  });
});

describe("formatVolume", () => {
  it("formats large volume in compact notation", () => {
    const result = formatVolume(1200000);
    expect(result).toMatch(/1\.2M|12L/); // compact format
  });

  it("returns '—' for null", () => {
    expect(formatVolume(null)).toBe("—");
  });
});

describe("formatConfidence", () => {
  it("formats 0.85 as a percentage", () => {
    expect(formatConfidence(0.85)).toContain("85");
  });

  it("formats 0.0 correctly", () => {
    expect(formatConfidence(0)).toContain("0");
  });
});

describe("formatTime", () => {
  it("returns a non-empty string for a valid ISO timestamp", () => {
    const result = formatTime("2024-01-01T10:30:00Z");
    expect(typeof result).toBe("string");
    expect(result.length).toBeGreaterThan(0);
  });

  it("returns the original string for an invalid timestamp", () => {
    expect(formatTime("not-a-date")).toBe("not-a-date");
  });
});

describe("formatDate", () => {
  it("returns a non-empty string for a valid ISO date", () => {
    const result = formatDate("2024-01-15T00:00:00Z");
    expect(typeof result).toBe("string");
    expect(result.length).toBeGreaterThan(0);
  });
});

// ─── Indicators ────────────────────────────────────────────────────────────

describe("PriceChange", () => {
  it("renders positive value with 'positive' class", () => {
    const { container } = render(<PriceChange value={100} formatted="₹100.00" />);
    expect(container.querySelector(".price-change--positive")).toBeInTheDocument();
  });

  it("renders negative value with 'negative' class", () => {
    const { container } = render(<PriceChange value={-50} formatted="-₹50.00" />);
    expect(container.querySelector(".price-change--negative")).toBeInTheDocument();
  });

  it("renders null value with 'neutral' class", () => {
    const { container } = render(<PriceChange value={null} formatted="—" />);
    expect(container.querySelector(".price-change--neutral")).toBeInTheDocument();
  });

  it("has accessible aria-label", () => {
    render(<PriceChange value={100} formatted="₹100.00" />);
    expect(screen.getByLabelText(/₹100.00/)).toBeInTheDocument();
  });
});

describe("ConfidenceBadge", () => {
  it("renders confidence as a percentage", () => {
    const { container } = render(<ConfidenceBadge value={0.85} />);
    expect(container.querySelector(".confidence-badge")).toHaveTextContent("85.0%");
  });

  it("handles null/undefined by rendering fallback", () => {
    const { container } = render(<ConfidenceBadge value={null} />);
    expect(container.querySelector(".confidence-badge")).toHaveTextContent("—");
  });

  it("has accessible aria-label", () => {
    render(<ConfidenceBadge value={0.85} />);
    expect(screen.getByLabelText(/Confidence/)).toBeInTheDocument();
  });
});

describe("SignalBadge", () => {
  it("renders bullish for 'Bullish'", () => {
    const { container } = render(<SignalBadge signal="Bullish" />);
    expect(container.querySelector(".signal-badge--bullish")).toBeInTheDocument();
  });

  it("renders bearish for 'Bearish'", () => {
    const { container } = render(<SignalBadge signal="Bearish" />);
    expect(container.querySelector(".signal-badge--bearish")).toBeInTheDocument();
  });

  it("renders neutral for unknown signal", () => {
    const { container } = render(<SignalBadge signal="Hold" />);
    expect(container.querySelector(".signal-badge--neutral")).toBeInTheDocument();
  });

  it("renders 'buy' as bullish", () => {
    const { container } = render(<SignalBadge signal="buy" />);
    expect(container.querySelector(".signal-badge--bullish")).toBeInTheDocument();
  });

  it("has accessible aria-label", () => {
    render(<SignalBadge signal="Bullish" />);
    expect(screen.getByLabelText("Signal: Bullish")).toBeInTheDocument();
  });
});

// ─── Market Components ─────────────────────────────────────────────────────

const mockTick: IntradayTick = {
  id: "t1",
  symbol: "NIFTY 50",
  ltp: 20000,
  timestamp: "2024-01-01T10:00:00Z",
  bid_price: 19999,
  ask_price: 20001,
  bid_qty: 10,
  ask_qty: 5,
  volume: 1200000,
  cold_storage_uploaded: false,
};

describe("MarketTickTable", () => {
  it("renders tick symbol", () => {
    render(<MarketTickTable ticks={[mockTick]} />);
    expect(screen.getByText("NIFTY 50")).toBeInTheDocument();
  });

  it("renders formatted LTP price", () => {
    render(<MarketTickTable ticks={[mockTick]} />);
    // Should find a formatted INR price
    expect(screen.getAllByText(/20,000|20000/).length).toBeGreaterThan(0);
  });

  it("renders '—' for null bid price", () => {
    const tickWithNullBid = { ...mockTick, bid_price: null };
    render(<MarketTickTable ticks={[tickWithNullBid]} />);
    expect(screen.getAllByText("—").length).toBeGreaterThan(0);
  });

  it("has accessible region role", () => {
    render(<MarketTickTable ticks={[mockTick]} />);
    expect(screen.getByRole("region", { name: /market tick data/i })).toBeInTheDocument();
  });

  it("uses tick id as row key (no duplicate key warnings) for multiple ticks", () => {
    const ticks = [mockTick, { ...mockTick, id: "t2", ltp: 20100 }];
    render(<MarketTickTable ticks={ticks} />);
    expect(screen.getAllByText("NIFTY 50")).toHaveLength(2);
  });
});

const mockSignal: TradingSignal = {
  id: "sig1",
  symbol: "NIFTY 50",
  signal: "Bullish",
  confidence: 0.85,
  target_price: 20500,
  prediction_source: "xgboost",
  outcome: null,
  created_at: "2024-01-01T10:00:00Z",
  updated_at: "2024-01-01T10:00:00Z",
};

describe("SignalTable", () => {
  it("renders signal symbol", () => {
    render(<SignalTable signals={[mockSignal]} />);
    expect(screen.getByText("NIFTY 50")).toBeInTheDocument();
  });

  it("renders SignalBadge for signal direction", () => {
    const { container } = render(<SignalTable signals={[mockSignal]} />);
    expect(container.querySelector(".signal-badge--bullish")).toBeInTheDocument();
  });

  it("renders ConfidenceBadge for confidence", () => {
    const { container } = render(<SignalTable signals={[mockSignal]} />);
    expect(container.querySelector(".confidence-badge")).toBeInTheDocument();
  });

  it("has accessible region role", () => {
    render(<SignalTable signals={[mockSignal]} />);
    expect(screen.getByRole("region", { name: /trading signals/i })).toBeInTheDocument();
  });
});

const mockHolding: PortfolioHolding = {
  symbol: "RELIANCE",
  quantity: 10,
  avg_buy_price: 2500,
  buy_date: "2024-01-01T00:00:00Z",
  notes: null,
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

describe("PortfolioTable", () => {
  it("renders holding symbol", () => {
    render(<PortfolioTable holdings={[mockHolding]} />);
    expect(screen.getByText("RELIANCE")).toBeInTheDocument();
  });

  it("renders formatted avg price", () => {
    render(<PortfolioTable holdings={[mockHolding]} />);
    expect(screen.getAllByText(/2,500|2500/).length).toBeGreaterThan(0);
  });

  it("renders '—' for null notes", () => {
    render(<PortfolioTable holdings={[mockHolding]} />);
    expect(screen.getByLabelText("No notes")).toBeInTheDocument();
  });

  it("has accessible region role", () => {
    render(<PortfolioTable holdings={[mockHolding]} />);
    expect(screen.getByRole("region", { name: /portfolio holdings/i })).toBeInTheDocument();
  });
});
