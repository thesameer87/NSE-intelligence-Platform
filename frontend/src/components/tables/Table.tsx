import type { ReactNode } from "react";
import "./Table.css";

interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => ReactNode;
  align?: "left" | "center" | "right";
}

interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (item: T) => string;
  "aria-label"?: string;
}

export function Table<T>({ columns, data, keyExtractor, "aria-label": ariaLabel }: TableProps<T>) {
  return (
    <div className="table-container" role="region" aria-label={ariaLabel ?? "Data table"} tabIndex={0}>
      <table className="table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key} className={`table__th table__th--${col.align ?? "left"}`} scope="col">
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr key={keyExtractor(item)} className="table__row">
              {columns.map((col) => (
                <td key={col.key} className={`table__td table__td--${col.align ?? "left"}`}>
                  {col.render ? col.render(item) : (item as Record<string, ReactNode>)[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
