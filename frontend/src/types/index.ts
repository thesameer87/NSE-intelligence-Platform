// Types aligned with backend Pydantic schemas (Tasks 11 & 13)

// ─── Market ────────────────────────────────────────────────
export interface IntradayTick {
  id: string;
  symbol: string;
  timestamp: string;
  ltp: number;
  bid_price: number | null;
  ask_price: number | null;
  bid_qty: number | null;
  ask_qty: number | null;
  volume: number | null;
  cold_storage_uploaded: boolean;
}

export interface DailyOHLCV {
  id: string;
  symbol: string;
  trade_date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// ─── Predictions ───────────────────────────────────────────
export interface ModelRegistry {
  model_name: string;
  version: string;
  metrics_json: Record<string, unknown>;
  schema_version: string;
  trained_at: string;
}

// ─── Signals ───────────────────────────────────────────────
export interface TradingSignal {
  id: string;
  symbol: string;
  signal: string;
  confidence: number;
  target_price: number;
  prediction_source: string;
  outcome: string | null;
  created_at: string;
  updated_at: string;
}

// ─── Portfolio ─────────────────────────────────────────────
export interface PortfolioHolding {
  symbol: string;
  quantity: number;
  avg_buy_price: number;
  buy_date: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

// ─── WebSocket ─────────────────────────────────────────────
export interface WebSocketMessage {
  event: string;
  data: Record<string, unknown>;
}

// ─── API Utilities ─────────────────────────────────────────
export type ApiState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: string };
