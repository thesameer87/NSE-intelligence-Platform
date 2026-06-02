import { useState, useEffect, useCallback } from "react";
import type { ApiState } from "../types";

export function useApi<T>(
  fetcher: () => Promise<T>,
): ApiState<T> & { 
  refetch: () => void;
  updateData: (updater: (prev: T) => T) => void;
} {
  const [state, setState] = useState<ApiState<T>>({ status: "idle" });

  const execute = useCallback(() => {
    setState({ status: "loading" });
    fetcher()
      .then((data) => setState({ status: "success", data }))
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "Unknown error";
        setState({ status: "error", error: message });
      });
  }, [fetcher]);

  const updateData = useCallback((updater: (prev: T) => T) => {
    setState((prev) => {
      if (prev.status === "success") {
        return { ...prev, data: updater(prev.data) };
      }
      return prev;
    });
  }, []);

  useEffect(() => {
    execute();
  }, [execute]);

  return { ...state, refetch: execute, updateData };
}
