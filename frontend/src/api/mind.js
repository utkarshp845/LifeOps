import { request } from "./client";

export const mindApi = {
  getBooks: () => request("/books"),
  createBook: (payload) => request("/books", { method: "POST", body: payload }),
  getBook: (id) => request(`/books/${id}`),
  patchBook: (id, payload) => request(`/books/${id}`, { method: "PATCH", body: payload }),
  getPhilosophy: () => request("/philosophy"),
  createPhilosophy: (payload) => request("/philosophy", { method: "POST", body: payload }),
  getDecisions: () => request("/decisions"),
  createDecision: (payload) => request("/decisions", { method: "POST", body: payload }),
  getDecision: (id) => request(`/decisions/${id}`),
  patchDecision: (id, payload) => request(`/decisions/${id}`, { method: "PATCH", body: payload })
};
