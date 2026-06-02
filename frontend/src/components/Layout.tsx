import type { ReactNode } from "react";
import "./Layout.css";

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="layout">
      <header className="layout__header" role="banner">
        <div className="layout__header-inner">
          <span className="layout__logo">NSE Intelligence</span>
          <nav className="layout__nav" aria-label="Main navigation">
            <a href="/dashboard" className="layout__nav-link">
              Dashboard
            </a>
          </nav>
        </div>
      </header>

      <main className="layout__main" role="main" id="main-content">
        {children}
      </main>

      <footer className="layout__footer" role="contentinfo">
        <span className="layout__footer-text">
          NSE Intelligence Platform — V1
        </span>
      </footer>
    </div>
  );
}
