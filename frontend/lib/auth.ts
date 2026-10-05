const ACCESS_TOKEN_KEY =
  "lightningq_access_token";

const REFRESH_TOKEN_KEY =
  "lightningq_refresh_token";

const USER_ID_KEY =
  "lightningq_user_id";

const SESSION_ID_KEY =
  "lightningq_session_id";

export type StoredAuth = {
  accessToken: string;
  refreshToken: string;
  userId: number;
  sessionId: string;
};

export function saveAuth(
  auth: StoredAuth
) {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.setItem(
    ACCESS_TOKEN_KEY,
    auth.accessToken
  );

  localStorage.setItem(
    REFRESH_TOKEN_KEY,
    auth.refreshToken
  );

  localStorage.setItem(
    USER_ID_KEY,
    String(auth.userId)
  );

  localStorage.setItem(
    SESSION_ID_KEY,
    auth.sessionId
  );
}

export function getAccessToken() {
  if (typeof window === "undefined") {
    return null;
  }

  return localStorage.getItem(
    ACCESS_TOKEN_KEY
  );
}

export function getRefreshToken() {
  if (typeof window === "undefined") {
    return null;
  }

  return localStorage.getItem(
    REFRESH_TOKEN_KEY
  );
}

export function getAuth(): StoredAuth | null {
  if (typeof window === "undefined") {
    return null;
  }

  const accessToken =
    getAccessToken();

  const refreshToken =
    getRefreshToken();

  const userId =
    localStorage.getItem(USER_ID_KEY);

  const sessionId =
    localStorage.getItem(SESSION_ID_KEY);

  if (
    !accessToken ||
    !refreshToken ||
    !userId ||
    !sessionId
  ) {
    return null;
  }

  return {
    accessToken,
    refreshToken,
    userId: Number(userId),
    sessionId,
  };
}

export function clearAuth() {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.removeItem(
    ACCESS_TOKEN_KEY
  );

  localStorage.removeItem(
    REFRESH_TOKEN_KEY
  );

  localStorage.removeItem(
    USER_ID_KEY
  );

  localStorage.removeItem(
    SESSION_ID_KEY
  );
}

export function isAuthenticated() {
  return !!getAccessToken();
}