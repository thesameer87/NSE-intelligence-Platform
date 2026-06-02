import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ErrorBoundary } from "../components/error/ErrorBoundary";
import { logger } from "../components/observability/logger";

// Mock the logger to prevent console noise during tests
vi.mock("../components/observability/logger", () => ({
  logger: {
    error: vi.fn(),
  },
}));

const Bomb = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error("Kaboom!");
  }
  return <div>Safe content</div>;
};

describe("ErrorBoundary", () => {
  it("renders children when there is no error", () => {
    render(
      <ErrorBoundary>
        <Bomb shouldThrow={false} />
      </ErrorBoundary>
    );
    expect(screen.getByText("Safe content")).toBeInTheDocument();
  });

  it("renders fallback UI when a child throws", () => {
    // Suppress React's intentional console.error for the thrown error in testing
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    render(
      <ErrorBoundary fallbackTitle="Custom Error Title">
        <Bomb shouldThrow={true} />
      </ErrorBoundary>
    );

    // Should render the custom title and the error message
    expect(screen.getByText("Custom Error Title")).toBeInTheDocument();
    expect(screen.getByText("Kaboom!")).toBeInTheDocument();
    
    // Should log deterministically
    expect(logger.error).toHaveBeenCalledWith(
      "React ErrorBoundary caught an exception",
      expect.any(Error),
      expect.objectContaining({ componentStack: expect.any(String) })
    );

    spy.mockRestore();
  });

  it("resets the error state when Try Again is clicked", () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    const TestComponent = () => {
      const [isBroken, setIsBroken] = React.useState(true);
      return (
        <ErrorBoundary onReset={() => setIsBroken(false)}>
          <Bomb shouldThrow={isBroken} />
        </ErrorBoundary>
      );
    };

    render(<TestComponent />);

    const button = screen.getByRole("button", { name: "Try Again" });
    fireEvent.click(button);



    expect(screen.getByText("Safe content")).toBeInTheDocument();

    spy.mockRestore();
  });
});
