import { request } from "./client";

export function login(username, password) {
  return request("/auth/login", {
    method: "POST",
    auth: false,
    body: { username, password }
  });
}
