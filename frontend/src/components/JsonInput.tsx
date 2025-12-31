/**
 * JsonInput: Component for pasting or uploading JSON data.
 */
import { useState, useCallback } from "react";
import type { ChartRequest, UserHints, ChartType } from "../types/chartSpec";

interface JsonInputProps {
  onSubmit: (request: ChartRequest) => void;
  isLoading?: boolean;
}

export function JsonInput({ onSubmit, isLoading }: JsonInputProps) {
  const [jsonText, setJsonText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [preferredChartType, setPreferredChartType] = useState<ChartType | "">("");
  const [xField, setXField] = useState("");
  const [yField, setYField] = useState("");

  const handleSubmit = useCallback(() => {
    setError(null);
    
    try {
      const data = JSON.parse(jsonText);
      
      const hints: UserHints = {};
      if (preferredChartType) {
        hints.preferred_chart_type = preferredChartType as ChartType;
      }
      if (xField.trim()) {
        hints.x_field = xField.trim();
      }
      if (yField.trim()) {
        hints.y_field = yField.trim();
      }

      onSubmit({
        data,
        hints: Object.keys(hints).length > 0 ? hints : null,
      });
    } catch (e) {
      setError(`Invalid JSON: ${e instanceof Error ? e.message : String(e)}`);
    }
  }, [jsonText, preferredChartType, xField, yField, onSubmit]);

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      setJsonText(text);
      setError(null);
    };
    reader.onerror = () => {
      setError("Failed to read file");
    };
    reader.readAsText(file);
  }, []);

  const loadExample = useCallback((example: string) => {
    setJsonText(example);
    setError(null);
  }, []);

  const timeSeriesExample = JSON.stringify({
    points: [
      { t: "2025-12-01", value: 10 },
      { t: "2025-12-02", value: 15 },
      { t: "2025-12-03", value: 12 },
      { t: "2025-12-04", value: 18 },
      { t: "2025-12-05", value: 20 },
    ],
  }, null, 2);

  const categoricalExample = JSON.stringify({
    items: [
      { label: "Category A", value: 45 },
      { label: "Category B", value: 30 },
      { label: "Category C", value: 25 },
    ],
  }, null, 2);

  const multiSeriesExample = JSON.stringify({
    series: [
      {
        name: "CPU",
        points: [
          { t: "2025-12-01", value: 50 },
          { t: "2025-12-02", value: 55 },
          { t: "2025-12-03", value: 48 },
        ],
      },
      {
        name: "Memory",
        points: [
          { t: "2025-12-01", value: 60 },
          { t: "2025-12-02", value: 65 },
          { t: "2025-12-03", value: 58 },
        ],
      },
    ],
  }, null, 2);

  return (
    <div className="p-4 border border-gray-300 rounded bg-gray-50">
      <h2 className="mt-0 mb-4 text-xl font-semibold">Input JSON Data</h2>
      
      {/* Example buttons */}
      <div className="mb-4">
        <strong>Load example:</strong>{" "}
        <button
          type="button"
          onClick={() => loadExample(timeSeriesExample)}
          className="mr-2 px-2 py-1 text-sm bg-blue-100 hover:bg-blue-200 text-blue-800 rounded transition-colors"
        >
          Time Series
        </button>
        <button
          type="button"
          onClick={() => loadExample(categoricalExample)}
          className="mr-2 px-2 py-1 text-sm bg-blue-100 hover:bg-blue-200 text-blue-800 rounded transition-colors"
        >
          Categorical
        </button>
        <button
          type="button"
          onClick={() => loadExample(multiSeriesExample)}
          className="mr-2 px-2 py-1 text-sm bg-blue-100 hover:bg-blue-200 text-blue-800 rounded transition-colors"
        >
          Multi-Series
        </button>
      </div>

      {/* File upload */}
      <div className="mb-4">
        <label className="font-semibold">
          Or upload JSON file:
          <input
            type="file"
            accept=".json,application/json"
            onChange={handleFileUpload}
            className="ml-2"
          />
        </label>
      </div>

      {/* JSON textarea */}
      <div className="mb-4">
        <label htmlFor="json-input" className="font-semibold block mb-2">
          JSON Data:
        </label>
        <textarea
          id="json-input"
          value={jsonText}
          onChange={(e) => {
            setJsonText(e.target.value);
            setError(null);
          }}
          placeholder='Paste JSON here, e.g., { "points": [{ "t": "2025-12-01", "value": 10 }] }'
          className="w-full min-h-[200px] font-mono text-sm p-2 border border-gray-300 rounded mt-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Hints */}
      <div className="mb-4 p-4 bg-white rounded border border-gray-300">
        <strong>Optional Hints:</strong>
        <div className="mt-2 grid grid-cols-2 gap-2">
          <div>
            <label className="block">
              Preferred Chart Type:
              <select
                value={preferredChartType}
                onChange={(e) => setPreferredChartType(e.target.value as ChartType | "")}
                className="w-full mt-1 p-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Auto-detect</option>
                <option value="line">Line</option>
                <option value="bar">Bar</option>
                <option value="column">Column</option>
                <option value="pie">Pie</option>
                <option value="area">Area</option>
                <option value="scatter">Scatter</option>
              </select>
            </label>
          </div>
          <div>
            <label className="block">
              X Field Name:
              <input
                type="text"
                value={xField}
                onChange={(e) => setXField(e.target.value)}
                placeholder="e.g., t, date, category"
                className="w-full mt-1 p-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </label>
          </div>
          <div>
            <label className="block">
              Y Field Name:
              <input
                type="text"
                value={yField}
                onChange={(e) => setYField(e.target.value)}
                placeholder="e.g., value, y, count"
                className="w-full mt-1 p-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </label>
          </div>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="mb-4 p-2 bg-red-100 text-red-800 rounded">
          {error}
        </div>
      )}

      {/* Submit button */}
      <button
        type="button"
        onClick={handleSubmit}
        disabled={!jsonText.trim() || isLoading}
        className={`px-6 py-3 text-base font-medium text-white rounded transition-colors ${
          isLoading || !jsonText.trim()
            ? "bg-gray-400 cursor-not-allowed opacity-60"
            : "bg-blue-600 hover:bg-blue-700 cursor-pointer"
        }`}
      >
        {isLoading ? "Generating Chart..." : "Generate Chart"}
      </button>
    </div>
  );
}
