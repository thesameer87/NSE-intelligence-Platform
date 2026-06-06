import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { App } from "../App";
import { DashboardPage } from "../pages/Dashboard";
import { NotFoundPage } from "../pages/NotFound";
import { Layout } from "../components/Layout";
import { StatusBadge } from "../components/StatusBadge";
import * as clientApi from "../api/client";

// WebSocket must be a class constructor for `new WebSocket(...)` to work
class MockWebSocket {
  readyState = 0;
  onopen: null = null;
  onmessage: null = null;
  onclose: null = null;
  onerror: null = null;
  close = vi.fn();
}
vi.stubGlobal("WebSocket", MockWebSocket);

// Mock the API client functions to resolve immediately for DashboardPage rendering
vi.spyOn(clientApi.marketApi, "getIntradayTicks").mockResolvedValue([]);
vi.spyOn(clientApi.predictionApi, "getLatestModels").mockResolvedValue({ last_reload_time: null, last_reload_status: null, last_reload_duration_ms: null, models: [] });
vi.spyOn(clientApi.signalApi, "getSignals").mockResolvedValue([]);
vi.spyOn(clientApi.portfolioApi, "getHoldings").mockResolvedValue([]);

describe("Layout", () => {
  it("renders header, main, and footer", () => {
    render(<Layout>Content</Layout>);
    expect(screen.getByRole("banner")).toBeInTheDocument();
    expect(screen.getByRole("main")).toBeInTheDocument();
    expect(screen.getByRole("contentinfo")).toBeInTheDocument();
  });

  it("renders children inside main", () => {
    render(<Layout><p>Hello World</p></Layout>);
    expect(screen.getByText("Hello World")).toBeInTheDocument();
  });
});

describe("StatusBadge", () => {
  it("shows Live when connected", () => {
    render(<StatusBadge connected={true} />);
    expect(screen.getByText("Live")).toBeInTheDocument();
  });

  it("shows Offline when disconnected", () => {
    render(<StatusBadge connected={false} />);
    expect(screen.getByText("Offline")).toBeInTheDocument();
  });
});

describe("DashboardPage", () => {
  it("renders the Dashboard heading", async () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>,
    );
    expect(await screen.findByRole("heading", { level: 1, name: /dashboard/i })).toBeInTheDocument();
  });

  it("renders all four section cards", async () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>,
    );
    expect(await screen.findByRole("heading", { name: "Market Data" })).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Trading Signals" })).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Portfolio" })).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Active Models" })).toBeInTheDocument();
  });
});

describe("NotFoundPage", () => {
  it("shows 404 code", () => {
    render(<NotFoundPage />);
    expect(screen.getByText("404")).toBeInTheDocument();
  });

  it("renders a link back to dashboard", () => {
    render(<NotFoundPage />);
    expect(screen.getByRole("link", { name: /dashboard/i })).toBeInTheDocument();
  });
});

describe("App routing", () => {
  it("redirects / to /dashboard", async () => {
    render(<App />);
    expect(await screen.findByRole("heading", { level: 1, name: /dashboard/i })).toBeInTheDocument();
  });

  it("renders 404 for unknown route", async () => {
    render(
      <MemoryRouter initialEntries={["/unknown-route"]}>
        <Routes>
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(await screen.findByText("404")).toBeInTheDocument();
  });
});
