import { request } from "./client";

export const bodyApi = {
  getWorkouts: () => request("/workouts"),
  createWorkout: (payload) => request("/workouts", { method: "POST", body: payload }),
  getWorkout: (id) => request(`/workouts/${id}`),
  addExercise: (id, payload) => request(`/workouts/${id}/exercises`, { method: "POST", body: payload }),
  getWorkoutHistory: () => request("/workouts/history"),
  getGolf: () => request("/golf"),
  createGolf: (payload) => request("/golf", { method: "POST", body: payload }),
  getMetrics: (limit = 30) => request(`/metrics?limit=${limit}`),
  createMetric: (payload) => request("/metrics", { method: "POST", body: payload })
};
