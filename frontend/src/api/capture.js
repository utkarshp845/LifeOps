import { request } from "./client";

export const captureApi = {
  getCaptures: (status = "open") => request(status ? `/captures?status=${status}` : "/captures"),
  createCapture: (payload) => request("/captures", { method: "POST", body: payload }),
  updateCapture: (id, payload) => request(`/captures/${id}`, { method: "PATCH", body: payload }),
  convertCapture: (id, payload) => request(`/captures/${id}/convert`, { method: "POST", body: payload })
};
