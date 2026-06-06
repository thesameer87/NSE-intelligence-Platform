import { useDashboardData } from "../hooks/useDashboardData";
import { StatusBadge } from "../components/StatusBadge";
import { Card } from "../components/cards/Card";
import { Grid } from "../components/layout/Grid";
import { LoadingState, ErrorState, EmptyState } from "../components/states/States";
import { MarketTickTable } from "../components/market/MarketTickTable";
import { SignalTable } from "../components/market/SignalTable";
import { PortfolioTable } from "../components/market/PortfolioTable";
import { Table } from "../components/tables/Table";
import { ErrorBoundary } from "../components/error/ErrorBoundary";
import type { ModelRegistry } from "../types";
import "../components/StatusBadge.css";
import "./Dashboard.css";

const MODEL_COLUMNS = [
  { key: "model_name", header: "Model" },
  { key: "version", header: "Version" },
  { key: "schema_version", header: "Schema" },
  { key: "trained_at", header: "Trained At" },
];

export function DashboardPage() {
  const { ticks, models, signals, portfolio, isConnected } = useDashboardData("NIFTY 50");

  return (
    <div className="dashboard">
      <div className="dashboard__header">
        <div>
          <h1 className="dashboard__title">Dashboard</h1>
          <p className="dashboard__subtitle">
            NSE Intelligence Platform — V1 Overview
          </p>
        </div>
        <StatusBadge connected={isConnected} />
      </div>

      <Grid columns={2}>
        {/* Market Data Card */}
        <ErrorBoundary fallbackTitle="Market Data Error">
          <Card title="Market Data" subtitle="Latest Intraday Ticks">
            {ticks.status === "loading" && <LoadingState title="Loading market data" />}
            {ticks.status === "error" && <ErrorState title="Failed to load market data" description={ticks.error} />}
            {ticks.status === "success" && ticks.data.length === 0 && (
              <EmptyState title="No market data" description="Market might be closed or data is unavailable." />
            )}
            {ticks.status === "success" && ticks.data.length > 0 && (
              <MarketTickTable ticks={ticks.data} />
            )}
          </Card>
        </ErrorBoundary>

        {/* Signals Card */}
        <ErrorBoundary fallbackTitle="Signals Error">
          <Card title="Trading Signals" subtitle="Active Generated Signals">
            {signals.status === "loading" && <LoadingState title="Loading signals" />}
            {signals.status === "error" && <ErrorState title="Failed to load signals" description={signals.error} />}
            {signals.status === "success" && signals.data.length === 0 && (
              <EmptyState title="No active signals" description="No trading signals have been generated yet." />
            )}
            {signals.status === "success" && signals.data.length > 0 && (
              <SignalTable signals={signals.data} />
            )}
          </Card>
        </ErrorBoundary>

        {/* Portfolio Card */}
        <ErrorBoundary fallbackTitle="Portfolio Error">
          <Card title="Portfolio" subtitle="Current Holdings">
            {portfolio.status === "loading" && <LoadingState title="Loading portfolio" />}
            {portfolio.status === "error" && <ErrorState title="Failed to load portfolio" description={portfolio.error} />}
            {portfolio.status === "success" && portfolio.data.length === 0 && (
              <EmptyState title="Empty Portfolio" description="No active holdings found." />
            )}
            {portfolio.status === "success" && portfolio.data.length > 0 && (
              <PortfolioTable holdings={portfolio.data} />
            )}
          </Card>
        </ErrorBoundary>

        {/* Models Card */}
        <ErrorBoundary fallbackTitle="Models Error">
          <Card title="Active Models" subtitle="Registered ML Models">
            {models.status === "loading" && <LoadingState title="Loading models" />}
            {models.status === "error" && <ErrorState title="Failed to load models" description={models.error} />}
            {models.status === "success" && (!models.data?.models || models.data.models.length === 0) && (
              <EmptyState title="No active models" description="No ML models have been registered." />
            )}
            {models.status === "success" && Array.isArray(models.data?.models) && models.data.models.length > 0 && (
              <div className="overflow-x-auto">
                <Table<ModelRegistry>
                  columns={MODEL_COLUMNS}
                  data={models.data.models}
                  keyExtractor={(item) => `${item.model_name}-${item.version}`}
                />
              </div>
            )}
          </Card>
        </ErrorBoundary>
      </Grid>
    </div>
  );
}
