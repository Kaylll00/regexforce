export class ApiError extends Error {
  readonly code: string;
  readonly position: number | null;

  constructor(message: string, code = "api_error", position: number | null = null) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.position = position;
  }
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  let response: Response;
  try {
    response = await fetch(`${baseUrl}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new ApiError("The API could not be reached.", "network_error");
  }
  const payload: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    if (
      typeof payload === "object" &&
      payload !== null &&
      "error" in payload &&
      typeof payload.error === "object" &&
      payload.error !== null
    ) {
      const error = payload.error as { code?: unknown; message?: unknown; position?: unknown };
      throw new ApiError(
        typeof error.message === "string" ? error.message : "The API request failed.",
        typeof error.code === "string" ? error.code : "api_error",
        typeof error.position === "number" ? error.position : null,
      );
    }
    throw new ApiError("The API request failed.", "api_error");
  }
  return payload as T;
}

export async function downloadPost(path: string, body: unknown, filename: string): Promise<void> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const response = await fetch(`${baseUrl}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new ApiError("The export request failed.", "export_error");
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
