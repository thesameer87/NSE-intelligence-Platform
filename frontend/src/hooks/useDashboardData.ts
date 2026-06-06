import { useEffect, useCallback, useState } from "react";
import { useApi } from "./useApi";
import { useWebSocket } from "./useWebSocket";
import { marketApi, predictionApi, signalApi, portfolioApi } from "../api/client";
import type { IntradayTick, ModelLatestResponse, PredictionRuntimeStatus, TradingSignal, PortfolioHolding, ApiState } from "../types";

export interface DashboardData {
  ticks: ApiState<IntradayTick[]>;
  models: ApiState<ModelLatestResponse>;
  signals: ApiState<TradingSignal[]>;
  portfolio: ApiState<PortfolioHolding[]>;
  runtimeStatus: PredictionRuntimeStatus | null;
  isConnected: boolean;
  refreshAll: () => void;
}

export function useDashboardData(symbol = "NIFTY 50"): DashboardData {
  // 1. Initial REST fetch - memoized to prevent infinite re-renders in useApi
  const fetchTicks = useCallback(() => marketApi.getIntradayTicks(symbol), [symbol]);
  const fetchModels = useCallback(() => predictionApi.getLatestModels(), []);
  const fetchSignals = useCallback(() => signalApi.getSignals(), []);
  const fetchPortfolio = useCallback(() => portfolioApi.getHoldings(), []);

  const ticksApi = useApi(fetchTicks);
  const modelsApi = useApi(fetchModels);
  const signalsApi = useApi(fetchSignals);
  const portfolioApiData = useApi(fetchPortfolio);

  // 2. Real-time WebSocket connection
  const { isConnected, lastMessage } = useWebSocket();
  const [runtimeStatus, setRuntimeStatus] = useState<PredictionRuntimeStatus | null>(null);

  // 3. Reconcile WebSocket updates deterministically
  useEffect(() => {
    if (!lastMessage) return;

    switch (lastMessage.event) {
      case "market_tick": {
        const newTick = lastMessage.data as unknown as IntradayTick;
        // Only update if it matches our symbol
        if (newTick.symbol === symbol) {
          ticksApi.updateData((prevTicks) => {
            if (!Array.isArray(prevTicks)) return prevTicks;
            // Prepend new tick (backend/REST controls retention policy, frontend just merges)
            return [newTick, ...prevTicks.filter((t) => t.id !== newTick.id)];
          });
        }
        break;
      }
      
      case "signal_alert": {
        const newSignal = lastMessage.data as unknown as TradingSignal;
        signalsApi.updateData((prevSignals) => {
          if (!Array.isArray(prevSignals)) return prevSignals;
          // Prepend new signal, filter out exact duplicates by id
          return [newSignal, ...prevSignals.filter((s) => s.id !== newSignal.id)];
        });
        break;
      }

      case "prediction_update": {
        const newStatus = lastMessage.data as unknown as PredictionRuntimeStatus;
        if (newStatus.symbol === symbol) {
          setRuntimeStatus(newStatus);
        }
        break;
      }

      case "portfolio_update": {
        const updatedHolding = lastMessage.data as unknown as PortfolioHolding;
        portfolioApiData.updateData((prevHoldings) => {
          if (!Array.isArray(prevHoldings)) return prevHoldings;
          // Update or append
          const exists = prevHoldings.find((h) => h.symbol === updatedHolding.symbol);
          if (exists) {
            return prevHoldings.map((h) => h.symbol === updatedHolding.symbol ? updatedHolding : h);
          }
          return [...prevHoldings, updatedHolding];
        });
        break;
      }

      default:
        // Ignore unknown events
        break;
    }
  }, [lastMessage, symbol, ticksApi, modelsApi, signalsApi, portfolioApiData]);

  // 4. Fallback/Reconnect handling: refetch REST on reconnect
  useEffect(() => {
    if (isConnected) {
      // When connection is restored, state might be stale. We do a silent refetch.
      ticksApi.refetch();
      signalsApi.refetch();
      portfolioApiData.refetch();
      modelsApi.refetch();
    }
    // We explicitly omit APIs from deps because we only want to trigger on `isConnected` transitioning to true
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isConnected]);

  return {
    ticks: ticksApi,
    models: modelsApi,
    signals: signalsApi,
    portfolio: portfolioApiData,
    runtimeStatus,
    isConnected,
    refreshAll: () => {
      ticksApi.refetch();
      modelsApi.refetch();
      signalsApi.refetch();
      portfolioApiData.refetch();
    },
  };
}
