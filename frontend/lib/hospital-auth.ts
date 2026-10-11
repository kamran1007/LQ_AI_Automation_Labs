export type HospitalAuth = {
  accessToken: string;
  refreshToken: string;

  userId: number;
  userName: string;

  roleId: number;
  roleName: string;

  hospitalId: number;
  hospitalName: string;

  sessionId: string;

  expiresAt?: string;
};

const STORAGE_KEY =
  "lightningq_hospital_auth";

export function saveHospitalAuth(
  auth: HospitalAuth
) {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify(auth)
  );
}

export function getHospitalAuth():
  | HospitalAuth
  | null {
  if (
    typeof window ===
    "undefined"
  ) {
    return null;
  }

  const value =
    localStorage.getItem(
      STORAGE_KEY
    );

  if (!value) {
    return null;
  }

  try {
    return JSON.parse(
      value
    ) as HospitalAuth;
  } catch {
    return null;
  }
}

export function getHospitalAccessToken():
  | string
  | null {
  const auth = getHospitalAuth();

  return auth?.accessToken ?? null;
}

export function getHospitalRefreshToken():
  | string
  | null {
  const auth = getHospitalAuth();

  return auth?.refreshToken ?? null;
}

export function clearHospitalAuth() {
  localStorage.removeItem(
    STORAGE_KEY
  );
}