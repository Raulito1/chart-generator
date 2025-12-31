/**
 * ChartDisplay: Renders a chart from ChartSpec using Highcharts.
 * Includes fallback tabular view for accessibility.
 */
import { useMemo } from "react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import type { ChartSpec } from "../types/chartSpec";
import { chartSpecToHighcharts } from "../utils/chartConverter";

interface ChartDisplayProps {
  spec: ChartSpec;
  className?: string;
}

export function ChartDisplay({ spec, className }: ChartDisplayProps) {
  const options = useMemo(() => chartSpecToHighcharts(spec), [spec]);

  // Generate tabular fallback data
  const tableData = useMemo(() => {
    if (spec.chart_type === "pie") {
      // For pie charts, show name and value
      return spec.series[0]?.data.map((item: unknown) => {
        if (typeof item === "object" && item !== null && "name" in item && "y" in item) {
          return {
            name: String(item.name),
            value: Number(item.y),
          };
        }
        return null;
      }).filter(Boolean) || [];
    } else {
      // For other charts, show series data
      const rows: Array<Record<string, unknown>> = [];
      const maxLength = Math.max(...spec.series.map((s) => s.data.length));
      
      for (let i = 0; i < maxLength; i++) {
        const row: Record<string, unknown> = {};
        spec.series.forEach((series) => {
          const point = series.data[i];
          if (Array.isArray(point) && point.length >= 2) {
            row[spec.x_axis.title] = point[0];
            row[series.name] = point[1];
          } else if (typeof point === "number") {
            row[series.name] = point;
          }
        });
        rows.push(row);
      }
      return rows;
    }
  }, [spec]);

  return (
    <div className={className}>
      <div className="chart-container">
        <HighchartsReact highcharts={Highcharts} options={options} />
      </div>
      
      {/* Rationale */}
      <div className="mt-4 p-4 bg-gray-100 rounded">
        <strong>Why this chart type?</strong>
        <p className="mt-2 mb-0">{spec.rationale}</p>
        {spec.alternative_types.length > 0 && (
          <p className="mt-2 mb-0 text-sm text-gray-600">
            Alternative chart types: {spec.alternative_types.join(", ")}
          </p>
        )}
      </div>

      {/* Tabular fallback for accessibility */}
      <details className="mt-4">
        <summary className="cursor-pointer font-semibold">
          View data as table (accessibility)
        </summary>
        <div className="mt-2 overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr>
                {spec.chart_type === "pie" ? (
                  <>
                    <th className="p-2 border border-gray-300 text-left">Name</th>
                    <th className="p-2 border border-gray-300 text-left">Value</th>
                  </>
                ) : (
                  <>
                    <th className="p-2 border border-gray-300 text-left">{spec.x_axis.title}</th>
                    {spec.series.map((s) => (
                      <th key={s.name} className="p-2 border border-gray-300 text-left">
                        {s.name}
                      </th>
                    ))}
                  </>
                )}
              </tr>
            </thead>
            <tbody>
              {tableData.map((row, idx) => (
                <tr key={idx}>
                  {spec.chart_type === "pie" ? (
                    <>
                      <td className="p-2 border border-gray-300">{String(row.name)}</td>
                      <td className="p-2 border border-gray-300">{Number(row.value)}</td>
                    </>
                  ) : (
                    <>
                      <td className="p-2 border border-gray-300">
                        {String(Object.values(row)[0] || "")}
                      </td>
                      {spec.series.map((s) => (
                        <td key={s.name} className="p-2 border border-gray-300">
                          {String(row[s.name] || "")}
                        </td>
                      ))}
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
}
