/**
 * ChartSpec: TypeScript interfaces matching the backend Pydantic models.
 * This is the stable contract between frontend and backend.
 */

export enum ChartType {
  LINE = "line",
  BAR = "bar",
  COLUMN = "column",
  PIE = "pie",
  AREA = "area",
  SCATTER = "scatter",
  HEATMAP = "heatmap",
}

export interface AxisSpec {
  title: string;
  field?: string | null;
  type: string;
  unit?: string | null;
  format?: string | null;
  min?: number | null;
  max?: number | null;
}

export interface SeriesSpec {
  name: string;
  data: Array<Record<string, unknown> | Array<number | string> | number>;
  type?: string | null;
  color?: string | null;
  y_axis: number;
}

export interface ChartSpec {
  chart_type: ChartType;
  title: string;
  subtitle?: string | null;
  series: SeriesSpec[];
  x_axis: AxisSpec;
  y_axis?: AxisSpec | null;
  rationale: string;
  alternative_types: ChartType[];
  description?: string | null;
  config: Record<string, unknown>;
}

// Request types
export interface UserHints {
  preferred_chart_type?: ChartType | null;
  x_field?: string | null;
  y_field?: string | null;
  units?: Record<string, string> | null;
  formatting?: Record<string, string> | null;
}

export interface ChartRequest {
  data: Record<string, unknown>;
  hints?: UserHints | null;
}

