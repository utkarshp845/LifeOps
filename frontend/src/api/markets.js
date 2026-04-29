import { request } from "./client";

export const marketsApi = {
  getStocks: () => request("/markets/stocks"),
  createStock: (payload) => request("/markets/stocks", { method: "POST", body: payload }),
  getStock: (id) => request(`/markets/stocks/${id}`),
  patchStock: (id, payload) => request(`/markets/stocks/${id}`, { method: "PATCH", body: payload }),
  refreshQuote: (id) => request(`/markets/stocks/${id}/quote`)
};
