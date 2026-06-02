import "./NotFound.css";

export function NotFoundPage() {
  return (
    <div className="not-found">
      <h1 className="not-found__code">404</h1>
      <p className="not-found__message">Page not found.</p>
      <a href="/dashboard" className="not-found__link">
        Return to Dashboard
      </a>
    </div>
  );
}
