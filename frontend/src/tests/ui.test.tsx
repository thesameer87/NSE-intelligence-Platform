import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Card } from "../components/cards/Card";
import { Table } from "../components/tables/Table";
import { Grid } from "../components/layout/Grid";
import { LoadingState, ErrorState, EmptyState } from "../components/states/States";

describe("Card Component", () => {
  it("renders title, subtitle, and children", () => {
    render(
      <Card title="Test Card" subtitle="Test Subtitle">
        <p>Card Content</p>
      </Card>
    );
    expect(screen.getByRole("heading", { name: "Test Card" })).toBeInTheDocument();
    expect(screen.getByText("Test Subtitle")).toBeInTheDocument();
    expect(screen.getByText("Card Content")).toBeInTheDocument();
  });
});

describe("Table Component", () => {
  const columns = [
    { key: "id", header: "ID" },
    { key: "name", header: "Name" }
  ];
  const data = [{ id: "1", name: "Alice" }, { id: "2", name: "Bob" }];

  it("renders headers and data correctly", () => {
    render(
      <Table 
        columns={columns} 
        data={data} 
        keyExtractor={(item) => item.id} 
      />
    );
    
    // Check headers
    expect(screen.getByRole("columnheader", { name: "ID" })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Name" })).toBeInTheDocument();
    
    // Check data cells
    expect(screen.getByRole("cell", { name: "1" })).toBeInTheDocument();
    expect(screen.getByRole("cell", { name: "Alice" })).toBeInTheDocument();
    expect(screen.getByRole("cell", { name: "2" })).toBeInTheDocument();
    expect(screen.getByRole("cell", { name: "Bob" })).toBeInTheDocument();
  });
});

describe("Grid Component", () => {
  it("renders children with correct default classes", () => {
    const { container } = render(<Grid>Item 1</Grid>);
    const gridEl = container.firstChild as HTMLElement;
    expect(gridEl).toHaveClass("grid", "grid--cols-1", "grid--gap-medium");
    expect(screen.getByText("Item 1")).toBeInTheDocument();
  });

  it("renders with custom columns and gap", () => {
    const { container } = render(<Grid columns={3} gap="large">Item 1</Grid>);
    const gridEl = container.firstChild as HTMLElement;
    expect(gridEl).toHaveClass("grid--cols-3", "grid--gap-large");
  });
});

describe("State Components", () => {
  it("LoadingState renders correctly", () => {
    render(<LoadingState title="Loading..." description="Please wait" />);
    expect(screen.getByRole("status")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Loading..." })).toBeInTheDocument();
    expect(screen.getByText("Please wait")).toBeInTheDocument();
  });

  it("ErrorState renders correctly", () => {
    render(<ErrorState title="Error" description="Something went wrong" />);
    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Error" })).toBeInTheDocument();
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });

  it("EmptyState renders correctly", () => {
    render(<EmptyState title="No Data" description="No items found" />);
    expect(screen.getByRole("heading", { name: "No Data" })).toBeInTheDocument();
    expect(screen.getByText("No items found")).toBeInTheDocument();
  });
});
