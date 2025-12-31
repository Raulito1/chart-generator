/**
 * Utility to convert ChartSpec to Highcharts configuration.
 * This keeps the rendering logic separate from the data contract.
 */
import type { Options } from "highcharts";
import type { ChartSpec } from "../types/chartSpec";
import { ChartType } from "../types/chartSpec";

export function chartSpecToHighcharts(spec: ChartSpec): Options {
  const baseConfig: Options = {
    title: {
      text: spec.title,
    },
    subtitle: spec.subtitle
      ? {
          text: spec.subtitle,
        }
      : undefined,
    credits: {
      enabled: false,
    },
    accessibility: {
      description: spec.description || spec.title,
    },
  };

  // Map chart type
  const chartType = spec.chart_type;

  // Build series
  const series = spec.series.map((s) => {
    const seriesConfig: Highcharts.SeriesOptionsType = {
      name: s.name,
      data: s.data as unknown[],
      type: chartType as Highcharts.SeriesOptionsType["type"],
      color: s.color || undefined,
      yAxis: s.y_axis,
    };

    // Special handling for pie charts
    if (chartType === ChartType.PIE) {
      return {
        ...seriesConfig,
        type: "pie",
        data: s.data as Array<{ name: string; y: number }>,
      };
    }

    return seriesConfig;
  });

  // Build axes
  let xAxis: Highcharts.XAxisOptions | undefined;
  let yAxis: Highcharts.YAxisOptions | undefined;

  if (spec.x_axis && chartType !== ChartType.PIE) {
    xAxis = {
      title: {
        text: spec.x_axis.title,
      },
      type:
        spec.x_axis.type === "datetime"
          ? "datetime"
          : spec.x_axis.type === "log"
          ? "logarithmic"
          : spec.x_axis.type === "category"
          ? "category"
          : "linear",
      min: spec.x_axis.min ?? undefined,
      max: spec.x_axis.max ?? undefined,
    };
  }

  if (spec.y_axis && chartType !== ChartType.PIE) {
    yAxis = {
      title: {
        text: spec.y_axis.title + (spec.y_axis.unit ? ` (${spec.y_axis.unit})` : ""),
      },
      type:
        spec.y_axis.type === "log"
          ? "logarithmic"
          : spec.y_axis.type === "category"
          ? "category"
          : "linear",
      min: spec.y_axis.min ?? undefined,
      max: spec.y_axis.max ?? undefined,
    };
  }

  // Combine into Highcharts options
  const options: Options = {
    ...baseConfig,
    chart: {
      type: chartType === ChartType.PIE ? "pie" : chartType,
    },
    series,
    xAxis: xAxis ? [xAxis] : undefined,
    yAxis: yAxis ? [yAxis] : undefined,
    ...spec.config,
  };

  return options;
}

