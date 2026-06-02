import type { ReactNode } from "react";
import "./Grid.css";

interface GridProps {
  children: ReactNode;
  columns?: 1 | 2 | 3 | 4;
  gap?: "small" | "medium" | "large";
}

export function Grid({ children, columns = 1, gap = "medium" }: GridProps) {
  return (
    <div className={`grid grid--cols-${columns} grid--gap-${gap}`}>
      {children}
    </div>
  );
}
