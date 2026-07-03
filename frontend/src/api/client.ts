import type { LearningItem, ReviewSubmission, User } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`API error ${response.status}: ${body}`);
  }

  return response.json() as Promise<T>;
}

export function getDueItems(userId: number): Promise<LearningItem[]> {
  return request(`/users/${userId}/due`);
}

export function submitReview(payload: ReviewSubmission): Promise<LearningItem> {
  return request("/reviews", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getUser(userId: number): Promise<User> {
  return request(`/users/${userId}`);
}
