/**
 * Main App component.
 */
import { useState } from "react";
import { JsonInput } from "./components/JsonInput";
import { ChartDisplay } from "./components/ChartDisplay";
import { useGenerateChartMutation } from "./api/chartApi";
import type { ChartRequest, ChartSpec } from "./types/chartSpec";

function App() {
  const [chartSpec, setChartSpec] = useState<ChartSpec | null>(null);
  const [generateChart, { isLoading, error }] = useGenerateChartMutation();

  const handleSubmit = async (request: ChartRequest) => {
    try {
      const result = await generateChart(request).unwrap();
      setChartSpec(result);
    } catch (err) {
      console.error("Failed to generate chart:", err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-8">
      <header className="mb-8 text-center">
        <h1 className="m-0 text-4xl font-bold">Chart Generator</h1>
        <p className="text-gray-600 mt-2">
          Paste or upload JSON data to automatically generate charts
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <JsonInput onSubmit={handleSubmit} isLoading={isLoading} />
          
          {error && (
            <div className="mt-4 p-4 bg-red-100 text-red-800 rounded border border-red-300">
              <strong>Error:</strong>{" "}
              {"data" in error && typeof error.data === "object" && error.data !== null && "detail" in error.data
                ? String(error.data.detail)
                : "Failed to generate chart. Please check your JSON data."}
            </div>
          )}
        </div>

        <div>
          {chartSpec ? (
            <ChartDisplay spec={chartSpec} />
          ) : (
            <div className="p-8 text-center text-gray-500 border-2 border-dashed border-gray-300 rounded">
              <p>Enter JSON data and click "Generate Chart" to see the result.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
