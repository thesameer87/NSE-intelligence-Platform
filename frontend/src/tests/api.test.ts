import { describe, it, expect, vi, beforeEach } from "vitest";
import { marketApi, signalApi, portfolioApi, predictionApi, ApiError } from "../api/client";

// Mock global fetch
const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

beforeEach(() => {
  mockFetch.mockReset();
});

function jsonResponse(data: unknown, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    statusText: status === 200 ? "OK" : "Error",
    json: () => Promise.resolve(data),
  } as Response);
}

describe("marketApi.getIntradayTicks", () => {
  it("fetches ticks for a symbol", async () => {
    const mockTicks = [{ id: "1", symbol: "RELIANCE", ltp: 2500 }];
    mockFetch.mockReturnValueOnce(jsonResponse(mockTicks));

    const result = await marketApi.getIntradayTicks("RELIANCE");

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/market/ticks/RELIANCE"),
      expect.any(Object),
    );
    expect(result).toEqual(mockTicks);
  });

  it("throws ApiError on non-2xx response", async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({}, 500));

    await expect(marketApi.getIntradayTicks("RELIANCE")).rejects.toBeInstanceOf(ApiError);
  });
});

describe("marketApi.getDailyOHLCV", () => {
  it("fetches OHLCV for a symbol", async () => {
    const mockBars = [{ id: "1", symbol: "INFY", open: 1500, close: 1520 }];
    mockFetch.mockReturnValueOnce(jsonResponse(mockBars));

    const result = await marketApi.getDailyOHLCV("INFY");
    expect(result).toEqual(mockBars);
  });
});

describe("signalApi.getSignals", () => {
  it("fetches all trading signals", async () => {
    const mockSignals = [{ id: "s1", symbol: "TCS", signal: "Bullish" }];
    mockFetch.mockReturnValueOnce(jsonResponse(mockSignals));

    const result = await signalApi.getSignals();
    expect(result).toEqual(mockSignals);
  });
});

describe("portfolioApi.getHoldings", () => {
  it("fetches portfolio holdings", async () => {
    const mockHoldings = [{ symbol: "WIPRO", quantity: 10 }];
    mockFetch.mockReturnValueOnce(jsonResponse(mockHoldings));

    const result = await portfolioApi.getHoldings();
    expect(result).toEqual(mockHoldings);
  });
});

describe("predictionApi.getLatestModels", () => {
  it("fetches latest models", async () => {
    const mockModels = [{ model_name: "xgboost", version: "v1.0.0" }];
    mockFetch.mockReturnValueOnce(jsonResponse(mockModels));

    const result = await predictionApi.getLatestModels();
    expect(result).toEqual(mockModels);
  });
});

describe("ApiError", () => {
  it("carries status and message", () => {
    const err = new ApiError(404, "Not found");
    expect(err.status).toBe(404);
    expect(err.message).toBe("Not found");
    expect(err.name).toBe("ApiError");
  });
});
