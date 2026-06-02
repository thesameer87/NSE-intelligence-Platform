import type { ReactNode } from "react";
import "./Card.css";

interface CardProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  headerRight?: ReactNode;
  "aria-label"?: string;
}

export function Card({ title, subtitle, children, headerRight, "aria-label": ariaLabel }: CardProps) {
  return (
    <section className="card" aria-label={ariaLabel ?? title}>
      <header className="card__header">
        <div className="card__header-content">
          <h2 className="card__title">{title}</h2>
          {subtitle && <p className="card__subtitle">{subtitle}</p>}
        </div>
        {headerRight && <div className="card__header-right">{headerRight}</div>}
      </header>
      <div className="card__body">{children}</div>
    </section>
  );
}
