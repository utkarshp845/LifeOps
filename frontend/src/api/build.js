import { request } from "./client";

export const buildApi = {
  getProjects: () => request("/build/projects"),
  createProject: (payload) => request("/build/projects", { method: "POST", body: payload }),
  getProject: (id) => request(`/build/projects/${id}`),
  patchProject: (id, payload) => request(`/build/projects/${id}`, { method: "PATCH", body: payload })
};
