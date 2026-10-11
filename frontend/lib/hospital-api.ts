import {
  getHospitalAuth,
  clearHospitalAuth,
} from "./hospital-auth";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://127.0.0.1:8000";

export async function hospitalRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const auth = getHospitalAuth();
  const token = auth?.accessToken;

  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,

      headers: {
        "Content-Type": "application/json",

        ...(token
          ? {
              Authorization: `Bearer ${token}`,
            }
          : {}),

        ...(options.headers || {}),
      },
    }
  );

  if (response.status === 401) {
    clearHospitalAuth();

    window.location.href =
      "/hospital/login";

    throw new Error(
      "Hospital session expired."
    );
  }

  let data: unknown = null;

  try {
    data = await response.json();
  } catch {
    // Ignore empty response
  }

  if (!response.ok) {
    const error = data as {
      detail?: string;
      message?: string;
    } | null;

    throw new Error(
      error?.detail ||
        error?.message ||
        "Hospital request failed."
    );
  }

  return data as T;
}