/**
 * Redux store configuration with RTK Query.
 */
import { configureStore } from "@reduxjs/toolkit";
import { chartApi } from "../api/chartApi";

export const store = configureStore({
  reducer: {
    [chartApi.reducerPath]: chartApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(chartApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

