import { request } from "./client";

export const wealthApi = {
  getSnapshots: (limit = 30) => request(`/wealth/snapshots?limit=${limit}`),
  createSnapshot: (payload) => request("/wealth/snapshots", { method: "POST", body: payload }),
  getSummary: () => request("/wealth/summary")
};
