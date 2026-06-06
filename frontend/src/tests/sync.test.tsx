import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useDashboardData } from "../hooks/useDashboardData";
import { useApi } from "../hooks/useApi";
import { useWebSocket } from "../hooks/useWebSocket";
import * as clientApi from "../api/client";
import type { IntradayTick, TradingSignal } from "../types";

// Mock the API client functions
vi.spyOn(clientApi.marketApi, "getIntradayTicks").mockResolvedValue([]);
vi.spyOn(clientApi.predictionApi, "getLatestModels").mockResolvedValue({ last_reload_time: null, last_reload_status: null, last_reload_duration_ms: null, models: [] });
vi.spyOn(clientApi.signalApi, "getSignals").mockResolvedValue([]);
vi.spyOn(clientApi.portfolioApi, "getHoldings").mockResolvedValue([]);

// We need to mock useWebSocket to simulate messages and connection state
vi.mock("../hooks/useWebSocket", () => ({
  useWebSocket: vi.fn(),
}));

const mockUseWebSocket = vi.mocked(useWebSocket);

describe("useDashboardData - Synchronization", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseWebSocket.mockReturnValue({ isConnected: false, lastMessage: null });
  });

  it("initializes with loading state for all data", async () => {
    const { result } = renderHook(() => useDashboardData("NIFTY 50"));
    
    expect(result.current.ticks.status).toBe("loading");
    expect(result.current.models.status).toBe("loading");
    expect(result.current.signals.status).toBe("loading");
    expect(result.current.portfolio.status).toBe("loading");
  });

  it("updates tick data when market_tick event is received", async () => {
    // 1. Initial render
    const { result, rerender } = renderHook(() => useDashboardData("NIFTY 50"));
    
    // Wait for the mock fetches to resolve
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.ticks.status).toBe("success");

    // 2. Simulate WebSocket message
    const newTick: IntradayTick = {
      id: "t1",
      symbol: "NIFTY 50",
      ltp: 20000,
      timestamp: "2024-01-01T10:00:00Z",
      bid_price: null,
      ask_price: null,
      bid_qty: null,
      ask_qty: null,
      volume: 100,
      cold_storage_uploaded: false,
    };

    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      lastMessage: { event: "market_tick", data: newTick as unknown as Record<string, unknown> }
    });

    rerender();

    // The tick should be prepended
    if (result.current.ticks.status === "success") {
      expect(result.current.ticks.data).toHaveLength(1);
      expect(result.current.ticks.data[0].id).toBe("t1");
      expect(result.current.ticks.data[0].ltp).toBe(20000);
    } else {
      expect.fail("Expected ticks to be in success state");
    }
  });

  it("deduplicates signals by id and prepends them", async () => {
    const { result, rerender } = renderHook(() => useDashboardData("NIFTY 50"));
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    const newSignal: TradingSignal = {
      id: "sig1",
      symbol: "NIFTY 50",
      signal: "Bullish",
      confidence: 0.8,
      target_price: 20500,
      prediction_source: "xgboost",
      outcome: null,
      created_at: "2024-01-01T10:00:00Z",
      updated_at: "2024-01-01T10:00:00Z",
    };

    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      lastMessage: { event: "signal_alert", data: newSignal as unknown as Record<string, unknown> }
    });

    rerender();

    if (result.current.signals.status === "success") {
      expect(result.current.signals.data).toHaveLength(1);
      expect(result.current.signals.data[0].id).toBe("sig1");
    } else {
      expect.fail("Expected signals to be in success state");
    }

    // Send the exact same signal ID again to test deduplication
    const updatedSignal = { ...newSignal, confidence: 0.9 };
    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      lastMessage: { event: "signal_alert", data: updatedSignal as unknown as Record<string, unknown> }
    });

    rerender();

    if (result.current.signals.status === "success") {
      expect(result.current.signals.data).toHaveLength(1); // Still 1
      expect(result.current.signals.data[0].confidence).toBe(0.9); // Replaced with updated one
    }
  });

  it("merges prediction_update directly instead of orchestrating a refetch", async () => {
    const { result, rerender } = renderHook(() => useDashboardData("NIFTY 50"));
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    // Clear counts after initial mount
    vi.clearAllMocks();

    const newModel = {
      model_name: "rf_intraday",
      version: "v1.1.0",
      metrics_json: { accuracy: 0.85 },
      schema_version: "1.0",
      trained_at: "2024-01-01T10:00:00Z"
    };

    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      lastMessage: { event: "prediction_update", data: newModel as unknown as Record<string, unknown> }
    });

    rerender();

    // Verify it merged cleanly
    if (result.current.models.status === "success") {
      expect(result.current.models.data.models).toHaveLength(1);
      expect(result.current.models.data.models[0].version).toBe("v1.1.0");
    } else {
      expect.fail("Expected models to be in success state");
    }

    // Verify we didn't trigger an orchestration refetch
    expect(clientApi.predictionApi.getLatestModels).not.toHaveBeenCalled();
  });

  it("triggers REST refetch when connection is restored", async () => {
    const { rerender } = renderHook(() => useDashboardData("NIFTY 50"));
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    // Clear initial fetch counts
    vi.clearAllMocks();

    // Transition to connected
    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      lastMessage: null
    });

    rerender();

    // Verify all APIs were refetched
    expect(clientApi.marketApi.getIntradayTicks).toHaveBeenCalledWith("NIFTY 50");
    expect(clientApi.predictionApi.getLatestModels).toHaveBeenCalled();
    expect(clientApi.signalApi.getSignals).toHaveBeenCalled();
    expect(clientApi.portfolioApi.getHoldings).toHaveBeenCalled();
  });
});

describe("useApi - Local Updates", () => {
  it("allows optimistic local updates via updateData", async () => {
    const fetcher = vi.fn().mockResolvedValue([{ id: 1 }]);
    const { result } = renderHook(() => useApi<{ id: number }[]>(fetcher));

    // Wait for success
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.status).toBe("success");
    if (result.current.status === "success") {
      expect(result.current.data).toEqual([{ id: 1 }]);
    }

    // Apply local update
    act(() => {
      result.current.updateData((prev) => [...prev, { id: 2 }]);
    });

    if (result.current.status === "success") {
      expect(result.current.data).toEqual([{ id: 1 }, { id: 2 }]);
    }
  });
});
