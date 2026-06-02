import { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";
import { logger } from "../observability/logger";
import { ErrorState } from "../states/States";

interface Props {
  children?: ReactNode;
  fallbackTitle?: string;
  onReset?: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Deterministic React Error Boundary.
 * Prevents the entire React tree from crashing when a child component throws.
 * Provides accessible fallback rendering.
 */
export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Observable UI errors via deterministic logger
    logger.error("React ErrorBoundary caught an exception", error, {
      componentStack: errorInfo.componentStack,
    });
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: "var(--spacing-4)" }}>
          <ErrorState 
            title={this.props.fallbackTitle ?? "Something went wrong"} 
            description={this.state.error?.message ?? "An unexpected error occurred in this component."} 
          />
          <button 
            onClick={this.handleReset}
            style={{
              marginTop: "var(--spacing-4)",
              padding: "var(--spacing-2) var(--spacing-4)",
              backgroundColor: "var(--color-surface)",
              color: "var(--color-text-primary)",
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-sm)",
              cursor: "pointer",
            }}
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
