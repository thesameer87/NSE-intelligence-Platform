import "./States.css";

interface StateProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function LoadingState({ title, description }: StateProps) {
  return (
    <div className="state-container state-container--loading" role="status" aria-busy="true">
      <div className="state__spinner" aria-hidden="true" />
      <h3 className="state__title">{title}</h3>
      {description && <p className="state__description">{description}</p>}
    </div>
  );
}

export function ErrorState({ title, description, action }: StateProps) {
  return (
    <div className="state-container state-container--error" role="alert">
      <div className="state__icon" aria-hidden="true">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      </div>
      <h3 className="state__title">{title}</h3>
      {description && <p className="state__description">{description}</p>}
      {action && <div className="state__action">{action}</div>}
    </div>
  );
}

export function EmptyState({ title, description, action }: StateProps) {
  return (
    <div className="state-container state-container--empty">
      <div className="state__icon" aria-hidden="true">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <line x1="9" y1="9" x2="15" y2="15" />
          <line x1="15" y1="9" x2="9" y2="15" />
        </svg>
      </div>
      <h3 className="state__title">{title}</h3>
      {description && <p className="state__description">{description}</p>}
      {action && <div className="state__action">{action}</div>}
    </div>
  );
}
