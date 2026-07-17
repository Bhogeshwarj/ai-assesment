import type {
  DashboardSummary,
  SimulationInput,
  SimulationListItem,
  SimulationResponse,
} from "@/types/simulation";

// Server Components/Actions run inside the frontend container, where
// "localhost" refers to that container, not the backend one - so they need
// the Docker-network hostname (API_INTERNAL_URL, e.g. http://backend:8000).
// The browser runs on the host and needs the publicly published port
// (NEXT_PUBLIC_API_BASE_URL, baked in at build time). Fall back to the
// public URL when no internal one is set (e.g. running both locally without
// Docker, where "localhost" is correct in both places).
const API_BASE_URL =
  typeof window === "undefined"
    ? process.env.API_INTERNAL_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1"
    : process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options?.headers ?? {}) },
    cache: "no-store",
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      // no JSON body
    }
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  createSimulation: (payload: SimulationInput) =>
    request<SimulationResponse>("/simulation", { method: "POST", body: JSON.stringify(payload) }),

  listSimulations: () => request<SimulationListItem[]>("/simulation"),

  getSimulation: (id: string) => request<SimulationResponse>(`/simulation/${id}`),

  dashboardSummary: () => request<DashboardSummary>("/dashboard/summary"),
};
