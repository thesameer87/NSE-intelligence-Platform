import type {
  DailyOHLCV,
  IntradayTick,
  ModelLatestResponse,
  PortfolioHolding,
  TradingSignal,
} from "../types";

// Base URL driven by Vite env so it can be overridden per environment
const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8000";

class ApiRequestError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
  });

  if (!response.ok) {
    throw new ApiRequestError(response.status, `Request failed: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

// ─── Market ────────────────────────────────────────────────
export const marketApi = {
  getIntradayTicks: (symbol: string): Promise<IntradayTick[]> =>
    get<IntradayTick[]>(`/api/v1/market/ticks/${encodeURIComponent(symbol)}`),

  getDailyOHLCV: (symbol: string): Promise<DailyOHLCV[]> =>
    get<DailyOHLCV[]>(`/api/v1/market/ohlcv/${encodeURIComponent(symbol)}`),
};

// ─── Predictions ───────────────────────────────────────────
export const predictionApi = {
  getLatestModels: (): Promise<ModelLatestResponse> =>
    get<ModelLatestResponse>("/api/v1/prediction/models/latest"),
};

// ─── Signals ───────────────────────────────────────────────
export const signalApi = {
  getSignals: (): Promise<TradingSignal[]> =>
    get<TradingSignal[]>("/api/v1/signal/"),
};

// ─── Portfolio ─────────────────────────────────────────────
export const portfolioApi = {
  getHoldings: (): Promise<PortfolioHolding[]> =>
    get<PortfolioHolding[]>("/api/v1/portfolio/holdings"),
};

// ─── Health ────────────────────────────────────────────────
export const healthApi = {
  check: (): Promise<Record<string, unknown>> =>
    get<Record<string, unknown>>("/health"),
};

export { ApiRequestError as ApiError };
