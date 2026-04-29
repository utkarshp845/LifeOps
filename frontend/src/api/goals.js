import { request } from "./client";

export const goalsApi = {
  getAreas: () => request("/goals/areas"),
  createArea: (payload) => request("/goals/areas", { method: "POST", body: payload }),
  patchArea: (id, payload) => request(`/goals/areas/${id}`, { method: "PATCH", body: payload }),
  getGoals: (status = "") => request(status ? `/goals?status=${status}` : "/goals"),
  createGoal: (payload) => request("/goals", { method: "POST", body: payload }),
  getGoal: (id) => request(`/goals/${id}`),
  patchGoal: (id, payload) => request(`/goals/${id}`, { method: "PATCH", body: payload }),
  getSummary: () => request("/goals/summary"),
  getReviews: (kind = "") => request(kind ? `/reviews?kind=${kind}` : "/reviews"),
  createReview: (payload) => request("/reviews", { method: "POST", body: payload }),
  getReview: (id) => request(`/reviews/${id}`),
  patchReview: (id, payload) => request(`/reviews/${id}`, { method: "PATCH", body: payload }),
  getReviewDue: () => request("/reviews/due")
};
