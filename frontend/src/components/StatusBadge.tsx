interface StatusBadgeProps {
  connected: boolean;
}

export function StatusBadge({ connected }: StatusBadgeProps) {
  return (
    <span
      className={`status-badge status-badge--${connected ? "connected" : "disconnected"}`}
      aria-label={connected ? "WebSocket connected" : "WebSocket disconnected"}
      role="status"
    >
      <span className="status-badge__dot" aria-hidden="true" />
      {connected ? "Live" : "Offline"}
    </span>
  );
}
