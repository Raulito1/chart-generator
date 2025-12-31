/**
 * RTK Query API slice for chart generation.
 */
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { ChartSpec, ChartRequest } from "../types/chartSpec";

export const chartApi = createApi({
  reducerPath: "chartApi",
  baseQuery: fetchBaseQuery({
    baseUrl: "/api/v1",
  }),
  tagTypes: ["Chart"],
  endpoints: (builder) => ({
    generateChart: builder.mutation<ChartSpec, ChartRequest>({
      query: (body) => ({
        url: "/charts/generate",
        method: "POST",
        body,
      }),
    }),
    validateData: builder.mutation<
      { valid: boolean; patterns?: Record<string, boolean>; error?: string },
      Record<string, unknown>
    >({
      query: (body) => ({
        url: "/charts/validate",
        method: "POST",
        body,
      }),
    }),
    getChartTypes: builder.query<
      { chart_types: Array<{ type: string; description: string; best_for: string[] }> },
      void
    >({
      query: () => "/charts/types",
    }),
  }),
});

export const {
  useGenerateChartMutation,
  useValidateDataMutation,
  useGetChartTypesQuery,
} = chartApi;

