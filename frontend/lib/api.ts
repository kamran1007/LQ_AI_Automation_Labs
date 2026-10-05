const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://127.0.0.1:8000";

export type UserAuthResponse = {
  success: boolean;
  message?: string;

  access_token: string;
  refresh_token: string;

  token_type: string;

  user_id: number;
  session_id: string;

  expires_at?: string;
};

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,

      headers: {
        "Content-Type": "application/json",

        ...(options.headers || {}),
      },
    }
  );

  let data: unknown;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      "Invalid response from server."
    );
  }

  if (!response.ok) {
    const errorData =
      data as {
        detail?: string;
        message?: string;
      };

    throw new Error(
      errorData?.detail ||
        errorData?.message ||
        "Request failed."
    );
  }

  return data as T;
}


/**
 * Send MSG91 access token to LightningQ backend.
 */
export async function verifyMsg91Token(
  accessToken: string
): Promise<UserAuthResponse> {
  return request<UserAuthResponse>(
    "/ai/authuser/verify",
    {
      method: "POST",

      body: JSON.stringify({
        access_token: accessToken,
      }),
    }
  );
}


/**
 * Refresh LightningQ access token.
 */
export async function refreshUserToken(
  refreshToken: string
): Promise<UserAuthResponse> {
  return request<UserAuthResponse>(
    "/ai/authuser/refresh",
    {
      method: "POST",

      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    }
  );
}


/**
 * Logout LightningQ user.
 */
export async function logoutUser(
  accessToken: string
) {
  return request<{
    success: boolean;
    message: string;
  }>(
    "/ai/authuser/logout",
    {
      method: "POST",

      headers: {
        Authorization:
          `Bearer ${accessToken}`,
      },
    }
  );
}