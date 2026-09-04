import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricProgress } from "./metric-progress";

describe("MetricProgress", () => {
  it("renders metric label and values", () => {
    const view = render(<MetricProgress label="Proteines" value={120} goal={180} unit=" g" />);
    expect(view.getByText("Proteines")).toBeInTheDocument();
    expect(view.getByText("120 / 180 g")).toBeInTheDocument();
  });
});
