"use client";

import { useEffect, useState } from "react";

import { useRouter } from "next/navigation";

import { saveHospitalAuth } from "@/lib/hospital-auth";

export type HospitalAuthResponse = {
  success: boolean;
  message: string;

  access_token: string;
  refresh_token: string;
  token_type: string;

  user_id: number;
  user_name: string;

  role_id: number;
  role_name: string;

  hospital_id: number;
  hospital_name: string;

  session_id: string;
  expires_at: string;
};

type Msg91CallbackData = {
  reqId?: string;
  request_id?: string;
  requestId?: string;

  access_token?: string;
  accessToken?: string;
  token?: string;

  [key: string]: unknown;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export default function HospitalLoginPage() {
  const router = useRouter();

  const [step, setStep] = useState<"mobile" | "otp">("mobile");

  const [mobile, setMobile] = useState("");

  const [otp, setOtp] = useState("");

  const [reqId, setReqId] = useState<string | null>(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [message, setMessage] = useState("");

  const [sdkReady, setSdkReady] = useState(false);

  // --------------------------------------------------
  // CHECK EXISTING HOSPITAL LOGIN
  // --------------------------------------------------

  useEffect(() => {
    const existingAuth = localStorage.getItem("lightningq_hospital_auth");

    if (existingAuth) {
      router.replace("/hospital/dashboard");
    }
  }, [router]);

  // --------------------------------------------------
  // SEND OTP
  // --------------------------------------------------

  const handleSendOtp = () => {
    setError("");
    setMessage("");

    const cleanedMobile = mobile.replace(/\D/g, "");

    if (cleanedMobile.length !== 10) {
      setError("Please enter a valid 10-digit mobile number.");

      return;
    }

    if (!sdkReady || typeof window.sendOtp !== "function") {
      setError(
        "OTP service is not ready yet. Please wait a moment and try again.",
      );

      return;
    }

    setLoading(true);

    const identifier = `91${cleanedMobile}`;

    window.sendOtp(
      identifier,

      (data) => {
        console.log("Hospital OTP sent:", data);

        const receivedReqId = data.reqId ?? data.request_id ?? data.requestId;

        if (receivedReqId) {
          setReqId(receivedReqId);
        }

        setStep("otp");

        setMessage(`OTP sent to +91 ${cleanedMobile}`);

        setLoading(false);
      },

      (error) => {
        console.error("Hospital OTP send failed:", error);

        setError("Unable to send OTP. Please try again.");

        setLoading(false);
      },
    );
  };

  // --------------------------------------------------
  // VERIFY OTP
  // --------------------------------------------------

  const handleVerifyOtp = () => {
    setError("");
    setMessage("");

    const cleanedMobile = mobile.replace(/\D/g, "");
    const cleanedOtp = otp.replace(/\D/g, "");

    if (cleanedOtp.length !== 6) {
      setError("Please enter the 6-digit OTP.");

      return;
    }

    setLoading(true);

    verifyHospitalLogin(`91${cleanedMobile}`, cleanedOtp);
  };

  // --------------------------------------------------
  // BACKEND HOSPITAL LOGIN
  // --------------------------------------------------

  const verifyHospitalLogin = async (
    cleanedMobile: string,
    cleanedOtp: string,
  ) => {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/hospital/auth/verify`, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          mobile: cleanedMobile,
          otp: cleanedOtp,
        }),
      });

      let data: unknown = null;

      try {
        data = await response.json();
      } catch {
        // Ignore invalid JSON
      }

      if (!response.ok) {
        const errorData = data as {
          detail?: string;
          message?: string;
        } | null;

        throw new Error(
          errorData?.detail || errorData?.message || "Hospital login failed.",
        );
      }

      const authResponse = data as HospitalAuthResponse;

      if (!authResponse.access_token || !authResponse.refresh_token) {
        throw new Error(
          "Hospital authentication succeeded but tokens were not returned.",
        );
      }

      // ------------------------------------------
      // SAVE HOSPITAL SESSION
      // ------------------------------------------

      saveHospitalAuth({
        accessToken: authResponse.access_token,

        refreshToken: authResponse.refresh_token,

        userId: authResponse.user_id,

        userName: authResponse.user_name,

        roleId: authResponse.role_id,

        roleName: authResponse.role_name,

        hospitalId: authResponse.hospital_id,

        hospitalName: authResponse.hospital_name,

        sessionId: authResponse.session_id,

        expiresAt: authResponse.expires_at,
      });

      setMessage("Login successful. Redirecting...");

      // ------------------------------------------
      // GO TO DASHBOARD
      // ------------------------------------------

      router.replace("/hospital/dashboard");
    } catch (error) {
      console.error("Hospital login failed:", error);

      setError(error instanceof Error ? error.message : "Unable to login.");

      setLoading(false);
    }
  };

  // --------------------------------------------------
  // CHANGE MOBILE
  // --------------------------------------------------

  const changeMobile = () => {
    setStep("mobile");
    setOtp("");
    setReqId(null);
    setError("");
    setMessage("");
  };
  useEffect(() => {
    let script: HTMLScriptElement | null = null;

    const loadMsg91 = () => {
      const widgetId = process.env.NEXT_PUBLIC_MSG91_WIDGET_ID;

      const tokenAuth = process.env.NEXT_PUBLIC_MSG91_AUTH_TOKEN;

      if (!widgetId) {
        setError("MSG91 Widget ID is missing.");
        return;
      }

      if (!tokenAuth) {
        setError("MSG91 authentication token is missing.");
        return;
      }

      // Already loaded
      if (typeof window.initSendOTP === "function") {
        window.initSendOTP({
          widgetId,
          tokenAuth,
          exposeMethods: true,

          success: (data) => {
            console.log("MSG91 initialized:", data);
          },

          failure: (error) => {
            console.error("MSG91 initialization failed:", error);
          },
        });

        setSdkReady(true);
        return;
      }

      // Check if script already exists
      const existingScript = document.querySelector(
        'script[src="https://verify.msg91.com/otp-provider.js"]',
      );

      if (existingScript) {
        existingScript.addEventListener("load", () => {
          initializeMsg91();
        });

        return;
      }

      script = document.createElement("script");

      script.type = "text/javascript";

      script.src = "https://verify.msg91.com/otp-provider.js";

      script.async = true;

      script.onload = () => {
        console.log("MSG91 OTP provider loaded.");

        initializeMsg91();
      };

      script.onerror = () => {
        console.error("Failed to load MSG91 OTP provider.");

        setError("Unable to load OTP service. Please refresh the page.");

        setSdkReady(false);
      };

      document.head.appendChild(script);
    };

    const initializeMsg91 = () => {
      const widgetId = process.env.NEXT_PUBLIC_MSG91_WIDGET_ID;

      const tokenAuth = process.env.NEXT_PUBLIC_MSG91_AUTH_TOKEN;

      if (!widgetId || !tokenAuth) {
        return;
      }

      if (typeof window.initSendOTP !== "function") {
        console.error("MSG91 initSendOTP is unavailable.");

        setError("OTP service is not ready. Please refresh the page.");

        return;
      }

      console.log("Initializing MSG91...");

      window.initSendOTP({
        widgetId,
        tokenAuth,
        exposeMethods: true,

        success: (data) => {
          console.log("MSG91 global success:", data);
        },

        failure: (error) => {
          console.error("MSG91 global failure:", error);
        },
      });

      setSdkReady(true);

      console.log("MSG91 OTP service ready.");
    };

    loadMsg91();

    return () => {
      // Don't remove the global MSG91 script here.
      // Other pages may also use it.
    };
  }, []);
  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#050a12] px-4 text-white">
      {/* Background */}

      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/2 top-[-300px] h-[600px] w-[700px] -translate-x-1/2 rounded-full bg-cyan-500/[0.08] blur-[140px]" />

        <div className="absolute bottom-[-250px] right-[-150px] h-[500px] w-[500px] rounded-full bg-violet-600/[0.08] blur-[130px]" />
      </div>

      {/* Login Card */}

      <div className="relative w-full max-w-md">
        <div className="rounded-3xl border border-white/[0.09] bg-[#0b1320]/95 p-8 shadow-2xl shadow-black/40 backdrop-blur-xl md:p-10">
          {/* Logo */}

          <div className="mb-8">
            <div className="text-xl font-bold tracking-[0.2em]">
              <span className="text-cyan-400">LIGHTNING</span>

              <span className="text-white">Q</span>
            </div>

            <div className="mt-2 text-xs uppercase tracking-[0.18em] text-white/30">
              Hospital Portal
            </div>
          </div>

          {/* Heading */}

          {step === "mobile" ? (
            <>
              <h1 className="text-3xl font-semibold tracking-tight">
                Hospital sign in
              </h1>

              <p className="mt-3 text-sm leading-6 text-white/40">
                Sign in securely using your registered hospital mobile number.
              </p>
            </>
          ) : (
            <>
              <h1 className="text-3xl font-semibold tracking-tight">
                Verify your OTP
              </h1>

              <p className="mt-3 text-sm leading-6 text-white/40">
                Enter the 6-digit OTP sent to your registered mobile number.
              </p>
            </>
          )}

          {/* ----------------------------------------
              MOBILE STEP
              ---------------------------------------- */}

          {step === "mobile" && (
            <div className="mt-8">
              <label className="mb-2 block text-sm font-medium text-white/70">
                Mobile number
              </label>

              <div className="flex overflow-hidden rounded-xl border border-white/[0.1] bg-white/[0.03] focus-within:border-cyan-400/40">
                <div className="flex items-center border-r border-white/[0.08] px-4 text-sm text-white/40">
                  +91
                </div>

                <input
                  type="tel"
                  inputMode="numeric"
                  autoComplete="tel"
                  maxLength={10}
                  value={mobile}
                  onChange={(event) => {
                    setMobile(event.target.value.replace(/\D/g, ""));

                    setError("");
                  }}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && mobile.length === 10) {
                      handleSendOtp();
                    }
                  }}
                  disabled={loading}
                  placeholder="Enter mobile number"
                  className="min-w-0 flex-1 bg-transparent px-4 py-4 text-base text-white outline-none placeholder:text-white/25"
                />
              </div>

              <button
                type="button"
                onClick={handleSendOtp}
                disabled={loading || !sdkReady || mobile.length !== 10}
                className="mt-5 w-full rounded-xl bg-gradient-to-r from-cyan-400 to-violet-500 px-5 py-4 font-medium text-black transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-40"
              >
                {loading ? "Sending OTP..." : "Send OTP →"}
              </button>
            </div>
          )}

          {/* ----------------------------------------
              OTP STEP
              ---------------------------------------- */}

          {step === "otp" && (
            <div className="mt-8">
              <div className="mb-5 rounded-xl border border-white/[0.07] bg-white/[0.03] px-4 py-3 text-sm text-white/50">
                OTP sent to <span className="text-white/80">+91 {mobile}</span>
              </div>

              <label className="mb-2 block text-sm font-medium text-white/70">
                One-time password
              </label>

              <input
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                maxLength={6}
                value={otp}
                onChange={(event) => {
                  setOtp(event.target.value.replace(/\D/g, ""));

                  setError("");
                }}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && otp.length === 6) {
                    handleVerifyOtp();
                  }
                }}
                disabled={loading}
                autoFocus
                placeholder="Enter 6-digit OTP"
                className="w-full rounded-xl border border-white/[0.1] bg-white/[0.03] px-4 py-4 text-center text-xl tracking-[0.35em] text-white outline-none placeholder:text-sm placeholder:tracking-normal placeholder:text-white/25 focus:border-cyan-400/40"
              />

              <button
                type="button"
                onClick={handleVerifyOtp}
                disabled={loading || otp.length !== 6}
                className="mt-5 w-full rounded-xl bg-gradient-to-r from-cyan-400 to-violet-500 px-5 py-4 font-medium text-black transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-40"
              >
                {loading ? "Verifying..." : "Verify & Sign in →"}
              </button>

              <div className="mt-5 flex items-center justify-between text-sm">
                <button
                  type="button"
                  onClick={changeMobile}
                  disabled={loading}
                  className="text-white/40 transition hover:text-white"
                >
                  ← Change number
                </button>

                <button
                  type="button"
                  onClick={handleSendOtp}
                  disabled={loading}
                  className="text-cyan-400 transition hover:text-cyan-300 disabled:opacity-40"
                >
                  Resend OTP
                </button>
              </div>
            </div>
          )}

          {/* Error */}

          {error && (
            <div className="mt-5 rounded-xl border border-red-400/20 bg-red-400/[0.06] px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          )}

          {/* Success */}

          {message && !error && (
            <div className="mt-5 rounded-xl border border-emerald-400/20 bg-emerald-400/[0.06] px-4 py-3 text-sm text-emerald-300">
              {message}
            </div>
          )}

          {/* Footer */}

          <div className="mt-8 border-t border-white/[0.06] pt-5 text-center text-xs leading-5 text-white/25">
            Authorized hospital staff only.
          </div>
        </div>
      </div>
    </main>
  );
}
