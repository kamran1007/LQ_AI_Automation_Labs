"use client";

import { useEffect, useRef, useState } from "react";

declare global {
  interface Window {
    initSendOTP?: (configuration: {
      widgetId: string;
      tokenAuth: string;
      identifier?: string;
      exposeMethods?: boolean;
      captchaRenderId?: string;
      success?: (data: unknown) => void;
      failure?: (error: unknown) => void;
    }) => void;

    sendOtp?: (
      identifier: string,
      success?: (data: unknown) => void,
      failure?: (error: unknown) => void
    ) => void;

    verifyOtp?: (
      otp: string | number,
      success?: (data: unknown) => void,
      failure?: (error: unknown) => void,
      reqId?: string
    ) => void;

    retryOtp?: (
      channel: string | null,
      success?: (data: unknown) => void,
      failure?: (error: unknown) => void,
      reqId?: string
    ) => void;

    isCaptchaVerified?: () => boolean;

    getWidgetData?: () => unknown;
  }
}

type Msg91SendResponse = {
  reqId?: string;
  reqid?: string;
  requestId?: string;
};

type Msg91VerifyResponse = {
  access_token?: string;
  accessToken?: string;
  token?: string;
  [key: string]: unknown;
};

export default function Home() {
  const [mobile, setMobile] = useState("");
  const [otp, setOtp] = useState("");

  const [otpSent, setOtpSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const [message, setMessage] = useState("");
  const [reqId, setReqId] = useState("");

  const initialized = useRef(false);

 useEffect(() => {
  if (initialized.current) {
    return;
  }

  initialized.current = true;

  const widgetId =
    process.env.NEXT_PUBLIC_MSG91_WIDGET_ID;

  const tokenAuth =
    process.env.NEXT_PUBLIC_MSG91_AUTH_TOKEN;

  if (!widgetId || !tokenAuth) {
    console.error(
      "MSG91 configuration is missing.",
      {
        widgetIdPresent: Boolean(widgetId),
        tokenAuthPresent: Boolean(tokenAuth),
      }
    );

    return;
  }

  const configuration = {
    widgetId,
    tokenAuth,
    exposeMethods: true,
    captchaRenderId: "msg91-captcha",

    success: (data: unknown) => {
      console.log(
        "MSG91 global success:",
        data
      );
    },

    failure: (error: unknown) => {
      console.error(
        "MSG91 global failure:",
        error
      );
    },
  };

  // If MSG91 has already been loaded,
  // initialize it directly.
  if (
    typeof window.initSendOTP ===
    "function"
  ) {
    console.log(
      "MSG91 already loaded. Initializing..."
    );

    window.initSendOTP(configuration);

    return;
  }

  // Prevent duplicate script injection.
  const existingScript =
    document.querySelector(
      'script[src="https://verify.msg91.com/otp-provider.js"]'
    );

  if (existingScript) {
    console.log(
      "MSG91 script already exists."
    );

    return;
  }

  const script =
    document.createElement("script");

  script.type = "text/javascript";

  script.src =
    "https://verify.msg91.com/otp-provider.js";

  script.async = true;

  script.onload = () => {
    console.log(
      "MSG91 provider loaded."
    );

    if (
      typeof window.initSendOTP !==
      "function"
    ) {
      console.error(
        "MSG91 loaded but initSendOTP is unavailable."
      );

      return;
    }

    console.log(
      "Initializing MSG91..."
    );

    window.initSendOTP(
      configuration
    );

    console.log(
      "MSG91 initialized."
    );
  };

  script.onerror = () => {
    console.error(
      "Could not load MSG91 provider."
    );
  };

  document.head.appendChild(script);
}, []);

  const handleSendOtp = () => {
    const cleanedMobile =
      mobile.replace(/\D/g, "");

    if (!cleanedMobile) {
      setMessage(
        "Please enter your mobile number."
      );

      return;
    }

    /*
     * MSG91 requires country code without +.
     *
     * Example:
     * +91 9999999999
     *
     * becomes:
     * 919999999999
     */
    let identifier = cleanedMobile;

    if (
      identifier.startsWith("0") &&
      identifier.length === 10
    ) {
      identifier =
        "91" + identifier.substring(1);
    }

    if (
      identifier.length === 10
    ) {
      identifier =
        "91" + identifier;
    }

    console.log(
      "Sending OTP to:",
      identifier
    );

    if (
      typeof window.sendOtp !==
      "function"
    ) {
      console.error(
        "window.sendOtp is unavailable."
      );

      setMessage(
        "MSG91 is not ready. Please refresh the page."
      );

      return;
    }

    setLoading(true);
    setMessage("");

    window.sendOtp(
      identifier,

      (data) => {
        console.log(
          "MSG91 OTP SEND SUCCESS:",
          data
        );

        const response =
          data as Msg91SendResponse;

        const receivedReqId =
          response.reqId ||
          response.reqid ||
          response.requestId ||
          "";

        if (receivedReqId) {
          setReqId(
            receivedReqId
          );
        }

        setOtpSent(true);
        setLoading(false);

        setMessage(
          "OTP sent. Check your WhatsApp."
        );
      },

      (error) => {
        console.error(
          "MSG91 OTP SEND ERROR:",
          error
        );

        setLoading(false);

        setMessage(
          "OTP could not be sent. Check the browser console for the MSG91 error."
        );
      }
    );
  };

  const handleVerifyOtp = () => {
    if (!otp.trim()) {
      setMessage(
        "Please enter the OTP."
      );

      return;
    }

    if (
      typeof window.verifyOtp !==
      "function"
    ) {
      console.error(
        "window.verifyOtp is unavailable."
      );

      setMessage(
        "MSG91 verification is not ready."
      );

      return;
    }

    setLoading(true);
    setMessage("");

    console.log(
      "Verifying OTP..."
    );

    window.verifyOtp(
      otp.trim(),

      (data) => {
        console.log(
          "MSG91 OTP VERIFIED:",
          data
        );

        const response =
          data as Msg91VerifyResponse;

        /*
         * MSG91 returns an access token after
         * successful OTP verification.
         *
         * DO NOT send this token directly to
         * the browser UI or store it in localStorage.
         *
         * Later we will send it securely to
         * our FastAPI backend.
         */
        const accessToken =
          response.access_token ||
          response.accessToken ||
          response.token;

        if (accessToken) {
          console.log(
            "MSG91 access token received."
          );

          /*
           * Temporary frontend test only.
           *
           * We will replace this with:
           *
           * frontend
           *    ↓
           * FastAPI
           *    ↓
           * MSG91 verifyAccessToken
           *    ↓
           * LightningQ JWT
           */
        }

        setLoading(false);

        setMessage(
          "WhatsApp OTP verified successfully!"
        );
      },

      (error) => {
        console.error(
          "MSG91 OTP VERIFY ERROR:",
          error
        );

        setLoading(false);

        setMessage(
          "Invalid or expired OTP."
        );
      },

      reqId || undefined
    );
  };

  const handleRetryOtp = () => {
    if (
      typeof window.retryOtp !==
      "function"
    ) {
      console.error(
        "window.retryOtp is unavailable."
      );

      setMessage(
        "MSG91 resend is not ready."
      );

      return;
    }

    setLoading(true);
    setMessage("");

    /*
     * For a default widget configuration,
     * MSG91 documentation allows null.
     *
     * If we configure WhatsApp specifically
     * later, WhatsApp channel is "12".
     */
    window.retryOtp(
      null,

      (data) => {
        console.log(
          "MSG91 OTP RESENT:",
          data
        );

        setLoading(false);

        setMessage(
          "OTP resent. Check your WhatsApp."
        );
      },

      (error) => {
        console.error(
          "MSG91 OTP RESEND ERROR:",
          error
        );

        setLoading(false);

        setMessage(
          "Could not resend OTP."
        );
      },

      reqId || undefined
    );
  };

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "24px",
        background: "#f5f5f5",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "420px",
          background: "white",
          padding: "32px",
          borderRadius: "16px",
          boxShadow:
            "0 10px 40px rgba(0,0,0,0.08)",
        }}
      >
        <h1
          style={{
            fontSize: "28px",
            fontWeight: 700,
            marginBottom: "8px",
          }}
        >
          LightningQ
        </h1>

        <p
          style={{
            marginBottom: "24px",
            color: "#666",
          }}
        >
          Login with WhatsApp OTP
        </p>

        {/* MSG91 CAPTCHA container */}
        <div
          id="msg91-captcha"
          style={{
            marginBottom: "16px",
          }}
        />

        {!otpSent ? (
          <>
            <input
              type="tel"
              inputMode="tel"
              autoComplete="tel"
              placeholder="919999999999"
              value={mobile}
              onChange={(event) =>
                setMobile(
                  event.target.value
                )
              }
              disabled={loading}
              style={{
                width: "100%",
                padding: "14px",
                fontSize: "16px",
                border:
                  "1px solid #ddd",
                borderRadius: "10px",
                marginBottom: "12px",
              }}
            />

            <button
              type="button"
              onClick={
                handleSendOtp
              }
              disabled={loading}
              style={{
                width: "100%",
                padding: "14px",
                fontSize: "16px",
                border: "none",
                borderRadius: "10px",
                cursor: loading
                  ? "not-allowed"
                  : "pointer",
                background:
                  "#111",
                color: "white",
              }}
            >
              {loading
                ? "Sending..."
                : "Send WhatsApp OTP"}
            </button>
          </>
        ) : (
          <>
            <p
              style={{
                marginBottom: "8px",
              }}
            >
              OTP sent to:
            </p>

            <strong
              style={{
                display: "block",
                marginBottom: "16px",
              }}
            >
              {mobile}
            </strong>

            <input
              type="text"
              inputMode="numeric"
              autoComplete="one-time-code"
              placeholder="Enter OTP"
              value={otp}
              onChange={(event) =>
                setOtp(
                  event.target.value
                )
              }
              disabled={loading}
              style={{
                width: "100%",
                padding: "14px",
                fontSize: "18px",
                border:
                  "1px solid #ddd",
                borderRadius: "10px",
                marginBottom: "12px",
              }}
            />

            <button
              type="button"
              onClick={
                handleVerifyOtp
              }
              disabled={loading}
              style={{
                width: "100%",
                padding: "14px",
                fontSize: "16px",
                border: "none",
                borderRadius: "10px",
                cursor: loading
                  ? "not-allowed"
                  : "pointer",
                background:
                  "#111",
                color: "white",
                marginBottom: "10px",
              }}
            >
              {loading
                ? "Verifying..."
                : "Verify OTP"}
            </button>

            <button
              type="button"
              onClick={
                handleRetryOtp
              }
              disabled={loading}
              style={{
                width: "100%",
                padding: "12px",
                fontSize: "14px",
                border:
                  "1px solid #ddd",
                borderRadius: "10px",
                background: "white",
                cursor: loading
                  ? "not-allowed"
                  : "pointer",
              }}
            >
              Resend OTP
            </button>
          </>
        )}

        {message && (
          <p
            style={{
              marginTop: "20px",
              fontSize: "14px",
            }}
          >
            {message}
          </p>
        )}

        {reqId && (
          <p
            style={{
              marginTop: "12px",
              fontSize: "12px",
              color: "#888",
            }}
          >
            OTP request created successfully.
          </p>
        )}
      </div>
    </main>
  );
}