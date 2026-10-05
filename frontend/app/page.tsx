// "use client";

// import { useEffect, useRef, useState } from "react";

// declare global {
//   interface Window {
//     initSendOTP?: (configuration: {
//       widgetId: string;
//       tokenAuth: string;
//       identifier?: string;
//       exposeMethods?: boolean;
//       captchaRenderId?: string;
//       success?: (data: unknown) => void;
//       failure?: (error: unknown) => void;
//     }) => void;

//     sendOtp?: (
//       identifier: string,
//       success?: (data: unknown) => void,
//       failure?: (error: unknown) => void
//     ) => void;

//     verifyOtp?: (
//       otp: string | number,
//       success?: (data: unknown) => void,
//       failure?: (error: unknown) => void,
//       reqId?: string
//     ) => void;

//     retryOtp?: (
//       channel: string | null,
//       success?: (data: unknown) => void,
//       failure?: (error: unknown) => void,
//       reqId?: string
//     ) => void;

//     isCaptchaVerified?: () => boolean;

//     getWidgetData?: () => unknown;
//   }
// }

// type Msg91SendResponse = {
//   reqId?: string;
//   reqid?: string;
//   requestId?: string;
// };

// type Msg91VerifyResponse = {
//   access_token?: string;
//   accessToken?: string;
//   token?: string;
//   [key: string]: unknown;
// };

// export default function Home() {
//   const [mobile, setMobile] = useState("");
//   const [otp, setOtp] = useState("");

//   const [otpSent, setOtpSent] = useState(false);
//   const [loading, setLoading] = useState(false);

//   const [message, setMessage] = useState("");
//   const [reqId, setReqId] = useState("");

//   const initialized = useRef(false);

//  useEffect(() => {
//   if (initialized.current) {
//     return;
//   }

//   initialized.current = true;

//   const widgetId =
//     process.env.NEXT_PUBLIC_MSG91_WIDGET_ID;

//   const tokenAuth =
//     process.env.NEXT_PUBLIC_MSG91_AUTH_TOKEN;

//   if (!widgetId || !tokenAuth) {
//     console.error(
//       "MSG91 configuration is missing.",
//       {
//         widgetIdPresent: Boolean(widgetId),
//         tokenAuthPresent: Boolean(tokenAuth),
//       }
//     );

//     return;
//   }

//   const configuration = {
//     widgetId,
//     tokenAuth,
//     exposeMethods: true,
//     captchaRenderId: "msg91-captcha",

//     success: (data: unknown) => {
//       console.log(
//         "MSG91 global success:",
//         data
//       );
//     },

//     failure: (error: unknown) => {
//       console.error(
//         "MSG91 global failure:",
//         error
//       );
//     },
//   };

//   // If MSG91 has already been loaded,
//   // initialize it directly.
//   if (
//     typeof window.initSendOTP ===
//     "function"
//   ) {
//     console.log(
//       "MSG91 already loaded. Initializing..."
//     );

//     window.initSendOTP(configuration);

//     return;
//   }

//   // Prevent duplicate script injection.
//   const existingScript =
//     document.querySelector(
//       'script[src="https://verify.msg91.com/otp-provider.js"]'
//     );

//   if (existingScript) {
//     console.log(
//       "MSG91 script already exists."
//     );

//     return;
//   }

//   const script =
//     document.createElement("script");

//   script.type = "text/javascript";

//   script.src =
//     "https://verify.msg91.com/otp-provider.js";

//   script.async = true;

//   script.onload = () => {
//     console.log(
//       "MSG91 provider loaded."
//     );

//     if (
//       typeof window.initSendOTP !==
//       "function"
//     ) {
//       console.error(
//         "MSG91 loaded but initSendOTP is unavailable."
//       );

//       return;
//     }

//     console.log(
//       "Initializing MSG91..."
//     );

//     window.initSendOTP(
//       configuration
//     );

//     console.log(
//       "MSG91 initialized."
//     );
//   };

//   script.onerror = () => {
//     console.error(
//       "Could not load MSG91 provider."
//     );
//   };

//   document.head.appendChild(script);
// }, []);

//   const handleSendOtp = () => {
//     const cleanedMobile =
//       mobile.replace(/\D/g, "");

//     if (!cleanedMobile) {
//       setMessage(
//         "Please enter your mobile number."
//       );

//       return;
//     }

//     /*
//      * MSG91 requires country code without +.
//      *
//      * Example:
//      * +91 9999999999
//      *
//      * becomes:
//      * 919999999999
//      */
//     let identifier = cleanedMobile;

//     if (
//       identifier.startsWith("0") &&
//       identifier.length === 10
//     ) {
//       identifier =
//         "91" + identifier.substring(1);
//     }

//     if (
//       identifier.length === 10
//     ) {
//       identifier =
//         "91" + identifier;
//     }

//     console.log(
//       "Sending OTP to:",
//       identifier
//     );

//     if (
//       typeof window.sendOtp !==
//       "function"
//     ) {
//       console.error(
//         "window.sendOtp is unavailable."
//       );

//       setMessage(
//         "MSG91 is not ready. Please refresh the page."
//       );

//       return;
//     }

//     setLoading(true);
//     setMessage("");

//     window.sendOtp(
//       identifier,

//       (data) => {
//         console.log(
//           "MSG91 OTP SEND SUCCESS:",
//           data
//         );

//         const response =
//           data as Msg91SendResponse;

//         const receivedReqId =
//           response.reqId ||
//           response.reqid ||
//           response.requestId ||
//           "";

//         if (receivedReqId) {
//           setReqId(
//             receivedReqId
//           );
//         }

//         setOtpSent(true);
//         setLoading(false);

//         setMessage(
//           "OTP sent. Check your WhatsApp."
//         );
//       },

//       (error) => {
//         console.error(
//           "MSG91 OTP SEND ERROR:",
//           error
//         );

//         setLoading(false);

//         setMessage(
//           "OTP could not be sent. Check the browser console for the MSG91 error."
//         );
//       }
//     );
//   };

//   const handleVerifyOtp = () => {
//     if (!otp.trim()) {
//       setMessage(
//         "Please enter the OTP."
//       );

//       return;
//     }

//     if (
//       typeof window.verifyOtp !==
//       "function"
//     ) {
//       console.error(
//         "window.verifyOtp is unavailable."
//       );

//       setMessage(
//         "MSG91 verification is not ready."
//       );

//       return;
//     }

//     setLoading(true);
//     setMessage("");

//     console.log(
//       "Verifying OTP..."
//     );

//     window.verifyOtp(
//       otp.trim(),

//       (data) => {
//         console.log(
//           "MSG91 OTP VERIFIED:",
//           data
//         );

//         const response =
//           data as Msg91VerifyResponse;

//         /*
//          * MSG91 returns an access token after
//          * successful OTP verification.
//          *
//          * DO NOT send this token directly to
//          * the browser UI or store it in localStorage.
//          *
//          * Later we will send it securely to
//          * our FastAPI backend.
//          */
//         const accessToken =
//           response.access_token ||
//           response.accessToken ||
//           response.token;

//         if (accessToken) {
//           console.log(
//             "MSG91 access token received."
//           );

//           /*
//            * Temporary frontend test only.
//            *
//            * We will replace this with:
//            *
//            * frontend
//            *    ↓
//            * FastAPI
//            *    ↓
//            * MSG91 verifyAccessToken
//            *    ↓
//            * LightningQ JWT
//            */
//         }

//         setLoading(false);

//         setMessage(
//           "WhatsApp OTP verified successfully!"
//         );
//       },

//       (error) => {
//         console.error(
//           "MSG91 OTP VERIFY ERROR:",
//           error
//         );

//         setLoading(false);

//         setMessage(
//           "Invalid or expired OTP."
//         );
//       },

//       reqId || undefined
//     );
//   };

//   const handleRetryOtp = () => {
//     if (
//       typeof window.retryOtp !==
//       "function"
//     ) {
//       console.error(
//         "window.retryOtp is unavailable."
//       );

//       setMessage(
//         "MSG91 resend is not ready."
//       );

//       return;
//     }

//     setLoading(true);
//     setMessage("");

//     /*
//      * For a default widget configuration,
//      * MSG91 documentation allows null.
//      *
//      * If we configure WhatsApp specifically
//      * later, WhatsApp channel is "12".
//      */
//     window.retryOtp(
//       null,

//       (data) => {
//         console.log(
//           "MSG91 OTP RESENT:",
//           data
//         );

//         setLoading(false);

//         setMessage(
//           "OTP resent. Check your WhatsApp."
//         );
//       },

//       (error) => {
//         console.error(
//           "MSG91 OTP RESEND ERROR:",
//           error
//         );

//         setLoading(false);

//         setMessage(
//           "Could not resend OTP."
//         );
//       },

//       reqId || undefined
//     );
//   };

//   return (
//     <main
//       style={{
//         minHeight: "100vh",
//         display: "flex",
//         alignItems: "center",
//         justifyContent: "center",
//         padding: "24px",
//         background: "#f5f5f5",
//       }}
//     >
//       <div
//         style={{
//           width: "100%",
//           maxWidth: "420px",
//           background: "white",
//           padding: "32px",
//           borderRadius: "16px",
//           boxShadow:
//             "0 10px 40px rgba(0,0,0,0.08)",
//         }}
//       >
//         <h1
//           style={{
//             fontSize: "28px",
//             fontWeight: 700,
//             marginBottom: "8px",
//           }}
//         >
//           LightningQ
//         </h1>

//         <p
//           style={{
//             marginBottom: "24px",
//             color: "#666",
//           }}
//         >
//           Login with WhatsApp OTP
//         </p>

//         {/* MSG91 CAPTCHA container */}
//         <div
//           id="msg91-captcha"
//           style={{
//             marginBottom: "16px",
//           }}
//         />

//         {!otpSent ? (
//           <>
//             <input
//               type="tel"
//               inputMode="tel"
//               autoComplete="tel"
//               placeholder="919999999999"
//               value={mobile}
//               onChange={(event) =>
//                 setMobile(
//                   event.target.value
//                 )
//               }
//               disabled={loading}
//               style={{
//                 width: "100%",
//                 padding: "14px",
//                 fontSize: "16px",
//                 border:
//                   "1px solid #ddd",
//                 borderRadius: "10px",
//                 marginBottom: "12px",
//               }}
//             />

//             <button
//               type="button"
//               onClick={
//                 handleSendOtp
//               }
//               disabled={loading}
//               style={{
//                 width: "100%",
//                 padding: "14px",
//                 fontSize: "16px",
//                 border: "none",
//                 borderRadius: "10px",
//                 cursor: loading
//                   ? "not-allowed"
//                   : "pointer",
//                 background:
//                   "#111",
//                 color: "white",
//               }}
//             >
//               {loading
//                 ? "Sending..."
//                 : "Send WhatsApp OTP"}
//             </button>
//           </>
//         ) : (
//           <>
//             <p
//               style={{
//                 marginBottom: "8px",
//               }}
//             >
//               OTP sent to:
//             </p>

//             <strong
//               style={{
//                 display: "block",
//                 marginBottom: "16px",
//               }}
//             >
//               {mobile}
//             </strong>

//             <input
//               type="text"
//               inputMode="numeric"
//               autoComplete="one-time-code"
//               placeholder="Enter OTP"
//               value={otp}
//               onChange={(event) =>
//                 setOtp(
//                   event.target.value
//                 )
//               }
//               disabled={loading}
//               style={{
//                 width: "100%",
//                 padding: "14px",
//                 fontSize: "18px",
//                 border:
//                   "1px solid #ddd",
//                 borderRadius: "10px",
//                 marginBottom: "12px",
//               }}
//             />

//             <button
//               type="button"
//               onClick={
//                 handleVerifyOtp
//               }
//               disabled={loading}
//               style={{
//                 width: "100%",
//                 padding: "14px",
//                 fontSize: "16px",
//                 border: "none",
//                 borderRadius: "10px",
//                 cursor: loading
//                   ? "not-allowed"
//                   : "pointer",
//                 background:
//                   "#111",
//                 color: "white",
//                 marginBottom: "10px",
//               }}
//             >
//               {loading
//                 ? "Verifying..."
//                 : "Verify OTP"}
//             </button>

//             <button
//               type="button"
//               onClick={
//                 handleRetryOtp
//               }
//               disabled={loading}
//               style={{
//                 width: "100%",
//                 padding: "12px",
//                 fontSize: "14px",
//                 border:
//                   "1px solid #ddd",
//                 borderRadius: "10px",
//                 background: "white",
//                 cursor: loading
//                   ? "not-allowed"
//                   : "pointer",
//               }}
//             >
//               Resend OTP
//             </button>
//           </>
//         )}

//         {message && (
//           <p
//             style={{
//               marginTop: "20px",
//               fontSize: "14px",
//             }}
//           >
//             {message}
//           </p>
//         )}

//         {reqId && (
//           <p
//             style={{
//               marginTop: "12px",
//               fontSize: "12px",
//               color: "#888",
//             }}
//           >
//             OTP request created successfully.
//           </p>
//         )}
//       </div>
//     </main>
//   );
// }

"use client";

import { useState, useEffect } from "react";

import { initializeMsg91, getMsg91ErrorMessage } from "@/lib/msg91";

import { verifyMsg91Token } from "@/lib/api";

import { saveAuth } from "@/lib/auth";
import router from "next/dist/client/router";

const suggestions = [
  "Find Dolo 650 near me",
  "Book a doctor appointment",
  "Find a diagnostic center",
  "Find a plumber nearby",
];

const capabilities = [
  {
    icon: "✦",
    title: "Medicines",
    description: "Find, compare and order from nearby pharmacies.",
  },
  {
    icon: "⌁",
    title: "Healthcare",
    description: "Discover doctors, clinics and appointments.",
  },
  {
    icon: "◈",
    title: "Diagnostics",
    description: "Find labs and book diagnostic tests.",
  },
  {
    icon: "⌘",
    title: "Local Services",
    description: "Connect with trusted providers around you.",
  },
  {
    icon: "▣",
    title: "Shopping",
    description: "Discover and order from local businesses.",
  },
  {
    icon: "⚡",
    title: "Automation",
    description: "Let AI handle repetitive everyday tasks.",
  },
];

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [activeSuggestion, setActiveSuggestion] = useState(0);
  const [showLogin, setShowLogin] = useState(false);

  const handlePrompt = (value: string) => {
    setPrompt(value);
  };

  const nextSuggestion = () => {
    setActiveSuggestion((current) => {
      const next = (current + 1) % suggestions.length;
      setPrompt(suggestions[next]);
      return next;
    });
  };

  return (
    <main className="min-h-screen overflow-hidden bg-[#030712] text-white">
      {/* Background atmosphere */}
      <div className="pointer-events-none fixed inset-0">
        <div className="absolute left-[15%] top-[-20%] h-[650px] w-[650px] rounded-full bg-cyan-500/10 blur-[150px]" />

        <div className="absolute right-[-10%] top-[15%] h-[600px] w-[600px] rounded-full bg-violet-600/10 blur-[150px]" />

        <div className="absolute bottom-[-20%] left-[25%] h-[500px] w-[700px] rounded-full bg-blue-600/10 blur-[150px]" />

        <div
          className="absolute inset-0 opacity-[0.035]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(255,255,255,.4) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.4) 1px, transparent 1px)",
            backgroundSize: "70px 70px",
          }}
        />
      </div>

      {/* Navigation */}
      <header className="relative z-20 border-b border-white/[0.06]">
        <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6 lg:px-8">
          <Logo />

          <nav className="hidden items-center gap-9 text-sm text-white/55 md:flex">
            <a href="#features" className="transition hover:text-white">
              Features
            </a>

            <a href="#how-it-works" className="transition hover:text-white">
              How it works
            </a>

            <a href="#businesses" className="transition hover:text-white">
              For Businesses
            </a>

            <a href="#about" className="transition hover:text-white">
              About
            </a>
          </nav>

          <button
            onClick={() => setShowLogin(true)}
            className="rounded-full border border-white/15 bg-white/[0.04] px-5 py-2.5 text-sm font-medium transition hover:border-cyan-300/50 hover:bg-white/[0.08]"
          >
            Sign in
          </button>
        </div>
      </header>

      {/* Hero */}
      <section className="relative z-10">
        <div className="mx-auto grid max-w-7xl items-center gap-14 px-6 pb-24 pt-20 lg:grid-cols-[0.95fr_1.05fr] lg:px-8 lg:pb-32 lg:pt-28">
          {/* Hero copy */}
          <div>
            <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/[0.06] px-4 py-2 text-xs font-medium tracking-wide text-cyan-300">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-cyan-400" />
              YOUR AI AGENT FOR THE REAL WORLD
            </div>

            <h1 className="max-w-3xl text-5xl font-semibold leading-[0.98] tracking-[-0.055em] sm:text-6xl lg:text-[76px]">
              Don&apos;t search.
              <br />
              Don&apos;t call.
              <br />
              Just tell{" "}
              <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-violet-400 bg-clip-text text-transparent">
                LightningQ.
              </span>
            </h1>

            <p className="mt-7 max-w-xl text-base leading-7 text-white/50 sm:text-lg">
              One AI agent to find medicines, book appointments, connect with
              businesses, manage orders and automate everyday tasks.
            </p>

            <div className="mt-9 flex flex-wrap gap-3">
              <button
                onClick={() => {
                  document
                    .getElementById("agent")
                    ?.scrollIntoView({ behavior: "smooth" });
                }}
                className="rounded-xl bg-gradient-to-r from-cyan-400 to-violet-500 px-6 py-3.5 text-sm font-semibold text-black shadow-[0_0_35px_rgba(34,211,238,.18)] transition hover:scale-[1.02]"
              >
                Try AI Agent →
              </button>

              <button
                onClick={() => setShowLogin(true)}
                className="rounded-xl border border-white/15 bg-white/[0.035] px-6 py-3.5 text-sm font-semibold text-white transition hover:border-white/30 hover:bg-white/[0.07]"
              >
                Sign in
              </button>
            </div>

            <div className="mt-8 flex flex-wrap gap-5 text-xs text-white/35">
              <span>⚡ Fast</span>
              <span>◈ Secure</span>
              <span>◌ Reliable</span>
              <span>∞ Always available</span>
            </div>
          </div>

          {/* AI Agent */}
          <div id="agent" className="relative">
            <div className="absolute left-1/2 top-1/2 h-[430px] w-[430px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-400/10 blur-[100px]" />

            <div className="relative mx-auto max-w-xl">
              {/* Orb */}
              <div className="relative mx-auto mb-[-35px] flex h-64 w-64 items-center justify-center">
                <div className="absolute inset-0 animate-[spin_18s_linear_infinite] rounded-full border border-cyan-300/20" />

                <div className="absolute inset-5 rounded-full border border-violet-400/20" />

                <div className="absolute inset-10 rounded-full bg-gradient-to-br from-cyan-300/30 via-blue-500/20 to-violet-500/30 blur-xl" />

                <div className="relative flex h-36 w-36 items-center justify-center rounded-[42px] border border-cyan-200/30 bg-gradient-to-br from-[#14243e] to-[#070d19] shadow-[0_0_80px_rgba(34,211,238,.18)]">
                  <div className="flex gap-5">
                    <span className="h-4 w-7 rounded-full bg-cyan-300 shadow-[0_0_18px_rgba(103,232,249,.9)]" />
                    <span className="h-4 w-7 rounded-full bg-cyan-300 shadow-[0_0_18px_rgba(103,232,249,.9)]" />
                  </div>
                </div>

                <div className="absolute right-[-25px] top-10 rounded-2xl border border-white/10 bg-[#0b1425]/90 px-4 py-3 text-xs leading-5 text-white/70 shadow-xl backdrop-blur-xl">
                  Hi 👋
                  <br />
                  I&apos;m LightningQ.
                  <br />
                  Tell me what you need.
                </div>
              </div>

              {/* Prompt */}
              <div className="relative rounded-3xl border border-cyan-300/30 bg-white/[0.055] p-2 shadow-[0_0_60px_rgba(34,211,238,.08)] backdrop-blur-2xl">
                <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-[#07111f]/90 px-4 py-4">
                  <span className="text-lg text-cyan-300">✦</span>

                  <input
                    value={prompt}
                    onChange={(event) => setPrompt(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" && prompt.trim()) {
                        setShowLogin(true);
                      }
                    }}
                    placeholder="What can I help you with today?"
                    className="min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-white/30"
                  />

                  <button
                    onClick={() => {
                      if (!prompt.trim()) {
                        nextSuggestion();
                        return;
                      }

                      setShowLogin(true);
                    }}
                    className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-r from-cyan-400 to-blue-500 text-lg font-bold text-black transition hover:scale-105"
                  >
                    →
                  </button>
                </div>
              </div>

              {/* Prompt suggestions */}
              <div className="mt-4 flex flex-wrap justify-center gap-2">
                {suggestions.map((item) => (
                  <button
                    key={item}
                    onClick={() => handlePrompt(item)}
                    className="rounded-full border border-white/10 bg-white/[0.025] px-3.5 py-2 text-xs text-white/45 transition hover:border-cyan-300/30 hover:text-white"
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Capability cards */}
      <section id="features" className="relative z-10">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-6">
            {capabilities.map((item) => (
              <div
                key={item.title}
                className="group rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5 transition duration-300 hover:-translate-y-1 hover:border-cyan-300/20 hover:bg-white/[0.045]"
              >
                <div className="mb-5 flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/[0.04] text-sm text-cyan-300">
                  {item.icon}
                </div>

                <h3 className="text-sm font-semibold">{item.title}</h3>

                <p className="mt-2 text-xs leading-5 text-white/35">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section
        id="how-it-works"
        className="relative z-10 mx-auto max-w-7xl px-6 py-28 lg:px-8"
      >
        <div className="grid gap-14 lg:grid-cols-2 lg:items-center">
          <div className="rounded-3xl border border-white/10 bg-white/[0.025] p-6 shadow-2xl shadow-black/20">
            <div className="rounded-2xl border border-white/10 bg-[#07111f] p-5">
              <div className="flex gap-3">
                <div className="h-9 w-9 rounded-full bg-gradient-to-br from-cyan-300 to-blue-600" />

                <div>
                  <p className="text-xs font-medium text-white/50">You</p>

                  <div className="mt-1 rounded-2xl rounded-tl-none bg-white/[0.06] px-4 py-3 text-sm text-white/80">
                    I need Dolo 650 near me.
                  </div>
                </div>
              </div>

              <div className="mt-7 flex gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-full border border-cyan-300/30 bg-cyan-300/10 text-xs text-cyan-300">
                  LQ
                </div>

                <div className="flex-1">
                  <p className="text-xs font-medium text-cyan-300">
                    LightningQ
                  </p>

                  <div className="mt-2 rounded-2xl rounded-tl-none border border-white/10 bg-white/[0.035] p-4">
                    <p className="text-sm text-white/65">
                      Searching nearby pharmacies...
                    </p>

                    <div className="mt-4 space-y-2">
                      {[
                        ["MediPlus Pharmacy", "0.8 km", "₹24"],
                        ["HealthCare Medicals", "1.2 km", "₹25"],
                        ["City Pharmacy", "1.5 km", "₹26"],
                      ].map(([name, distance, price]) => (
                        <div
                          key={name}
                          className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.025] px-3 py-3"
                        >
                          <div>
                            <p className="text-xs font-medium">{name}</p>

                            <p className="mt-1 text-[10px] text-white/30">
                              {distance} · In stock · {price}
                            </p>
                          </div>

                          <button
                            onClick={() => setShowLogin(true)}
                            className="rounded-lg bg-white/[0.08] px-3 py-1.5 text-[10px] font-medium"
                          >
                            Order
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <div className="mb-5 inline-flex rounded-full border border-cyan-300/20 bg-cyan-300/[0.05] px-3 py-1.5 text-xs text-cyan-300">
              See LightningQ in action
            </div>

            <h2 className="text-4xl font-semibold tracking-[-0.04em] sm:text-5xl">
              From a simple request
              <span className="block bg-gradient-to-r from-cyan-300 to-violet-400 bg-clip-text text-transparent">
                to real results.
              </span>
            </h2>

            <p className="mt-5 max-w-xl leading-7 text-white/40">
              LightningQ understands what you need, searches across trusted
              providers and helps you get things done without jumping between
              apps.
            </p>

            <div className="mt-9 space-y-6">
              <Step number="01" title="You tell us what you need">
                “I need Dolo 650 near me.”
              </Step>

              <Step number="02" title="AI searches and finds the best options">
                Nearby providers, availability and relevant information.
              </Step>

              <Step number="03" title="You compare and choose">
                See options, distance, price and availability.
              </Step>

              <Step number="04" title="LightningQ gets it done">
                Order, book or connect — all from one place.
              </Step>
            </div>
          </div>
        </div>
      </section>

      {/* Ecosystem */}
      <section
        id="businesses"
        className="relative z-10 border-y border-white/[0.06] bg-white/[0.015]"
      >
        <div className="mx-auto max-w-7xl px-6 py-28 text-center lg:px-8">
          <div className="mx-auto max-w-3xl">
            <div className="mb-5 inline-flex rounded-full border border-violet-300/20 bg-violet-300/[0.05] px-3 py-1.5 text-xs text-violet-300">
              More than a helper
            </div>

            <h2 className="text-4xl font-semibold tracking-[-0.04em] sm:text-6xl">
              An AI Agent for your
              <span className="block bg-gradient-to-r from-cyan-300 via-blue-400 to-violet-400 bg-clip-text text-transparent">
                entire everyday world.
              </span>
            </h2>

            <p className="mx-auto mt-5 max-w-2xl leading-7 text-white/40">
              LightningQ connects people with the real-world businesses and
              services they need.
            </p>
          </div>

          <div className="mx-auto mt-20 grid max-w-5xl grid-cols-2 gap-4 md:grid-cols-4">
            {[
              "Pharmacies",
              "Hospitals & Clinics",
              "Diagnostic Centers",
              "Local Services",
              "Food & Groceries",
              "Retail & Shopping",
              "Salons & Wellness",
              "Travel & Transport",
            ].map((item, index) => (
              <div
                key={item}
                className="rounded-2xl border border-white/10 bg-white/[0.025] p-5 text-left transition hover:border-cyan-300/20 hover:bg-white/[0.05]"
              >
                <div className="mb-4 text-2xl">
                  {["✚", "⌁", "◈", "⌘", "◍", "▣", "✦", "◇"][index]}
                </div>

                <p className="text-sm font-medium">{item}</p>

                <p className="mt-1 text-xs text-white/30">
                  Connected to your AI agent
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section id="about" className="relative z-10 px-6 py-28">
        <div className="mx-auto max-w-5xl overflow-hidden rounded-[32px] border border-cyan-300/15 bg-gradient-to-br from-cyan-400/[0.08] via-blue-500/[0.05] to-violet-500/[0.08] p-10 text-center sm:p-16">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-cyan-300/20 bg-cyan-300/10 text-2xl text-cyan-300">
            ⚡
          </div>

          <h2 className="mt-7 text-4xl font-semibold tracking-[-0.04em] sm:text-6xl">
            Tell LightningQ.
            <br />
            Let AI handle the rest.
          </h2>

          <p className="mx-auto mt-5 max-w-xl leading-7 text-white/40">
            Your next everyday task could be one conversation away.
          </p>

          <button
            onClick={() => setShowLogin(true)}
            className="mt-8 rounded-xl bg-white px-7 py-4 text-sm font-semibold text-black transition hover:bg-cyan-50"
          >
            Get started →
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/[0.06]">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-6 py-8 text-xs text-white/30 sm:flex-row sm:items-center sm:justify-between lg:px-8">
          <div>
            <span className="font-medium text-white/60">LightningQ</span> · AI
            Automation Labs
          </div>

          <div>
            © {new Date().getFullYear()} LightningQ. All rights reserved.
          </div>
        </div>
      </footer>

      {/* Login modal */}
      {showLogin && <LoginModal onClose={() => setShowLogin(false)} />}
    </main>
  );
}

function Logo() {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-300 to-blue-500 text-lg font-black text-black shadow-[0_0_25px_rgba(34,211,238,.2)]">
        ⚡
      </div>

      <div>
        <p className="text-sm font-semibold tracking-wide">LightningQ</p>

        <p className="text-[9px] uppercase tracking-[0.22em] text-white/30">
          AI Automation Labs
        </p>
      </div>
    </div>
  );
}

function Step({
  number,
  title,
  children,
}: {
  number: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex gap-4">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-cyan-300/20 bg-cyan-300/[0.06] text-[10px] font-semibold text-cyan-300">
        {number}
      </div>

      <div>
        <h3 className="text-sm font-semibold">{title}</h3>

        <p className="mt-1 text-xs leading-5 text-white/35">{children}</p>
      </div>
    </div>
  );
}

function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="mt-4 rounded-xl border border-red-400/20 bg-red-400/[0.06] px-4 py-3 text-sm text-red-300">
      {message}
    </div>
  );
}

function LoginModal({ onClose }: { onClose: () => void }) {
  const [step, setStep] = useState<"mobile" | "otp">("mobile");

  const [mobile, setMobile] = useState("");

  const [otp, setOtp] = useState("");

  const [reqId, setReqId] = useState<string | null>(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [message, setMessage] = useState("");

  const [sdkReady, setSdkReady] = useState(false);

  /*
   * Initialize MSG91
   */
  useEffect(() => {
    const initialize = () => {
      try {
        initializeMsg91();

        setSdkReady(true);

        console.log("MSG91 initialized");
      } catch (error) {
        console.error("MSG91 initialization failed:", error);

        setError(
          error instanceof Error
            ? error.message
            : "Unable to initialize OTP service.",
        );
      }
    };

    /*
     * Script may already be loaded
     */
    if (window.initSendOTP) {
      initialize();
      return;
    }

    /*
     * Wait for MSG91 script
     */
    const timer = window.setInterval(() => {
      if (window.initSendOTP) {
        window.clearInterval(timer);

        initialize();
      }
    }, 100);

    return () => {
      window.clearInterval(timer);
    };
  }, []);

  /*
   * SEND OTP
   */
  const sendOtp = () => {
    setError("");
    setMessage("");

    const cleanedMobile = mobile.replace(/\D/g, "");

    if (cleanedMobile.length !== 10) {
      setError("Please enter a valid 10-digit mobile number.");

      return;
    }

    if (!sdkReady || !window.sendOtp) {
      setError("OTP service is not ready. Please try again.");

      return;
    }

    setLoading(true);

    /*
     * MSG91 expects country code
     * without the + sign.
     *
     * Example:
     *
     * 918421205672
     */
    const identifier = `91${cleanedMobile}`;

    window.sendOtp(
      identifier,

      /*
       * SUCCESS
       */
      (data: Msg91CallbackData) => {
        console.log("MSG91 send OTP success:", data);

        const requestId =
          data.reqId ??
          data.request_id ??
          data.requestId ??
          (typeof data.message === "string" ? data.message : undefined);

        console.log("MSG91 request ID:", requestId);

        if (!requestId) {
          setError("OTP request ID was not returned.");
          setLoading(false);
          return;
        }

        setReqId(requestId);
        setStep("otp");
        setMessage("OTP sent successfully.");
        setLoading(false);
      },

      /*
       * FAILURE
       */
      (error: unknown) => {
        console.error("MSG91 send OTP failed:", error);

        setError(
          getMsg91ErrorMessage(error, "Unable to send OTP. Please try again."),
        );

        setLoading(false);
      },
    );
  };

  /*
   * VERIFY OTP
   */
  const verifyOtp = () => {
    setError("");
    setMessage("");

    if (otp.length !== 6) {
      setError("Please enter the 6-digit OTP.");

      return;
    }

    if (!window.verifyOtp) {
      setError("OTP service is not ready.");

      return;
    }

    if (!reqId) {
      setError("OTP session has expired. Please request a new OTP.");

      return;
    }

    setLoading(true);

    window.verifyOtp(
      otp,
      async (data: Msg91CallbackData) => {
        console.log("MSG91 OTP verified:", data);

        const msg91AccessToken =
          data.access_token ?? data.accessToken ?? data.token ?? data.message;

        if (!msg91AccessToken) {
          setError("OTP verified, but no MSG91 access token was returned.");
          setLoading(false);
          return;
        }

        try {
          console.log("Sending MSG91 token to LightningQ backend...");

          const authResponse = await verifyMsg91Token(msg91AccessToken);

          console.log("LightningQ authentication successful.");

          saveAuth({
            accessToken: authResponse.access_token,
            refreshToken: authResponse.refresh_token,
            userId: authResponse.user_id,
            sessionId: authResponse.session_id,
          });

          setMessage("Login successful.");

          router.push("/agent");
        } catch (error: unknown) {
          console.error("LightningQ authentication failed:", error);

          setError(
            error instanceof Error
              ? error.message
              : "Unable to complete login.",
          );

          setLoading(false);
        }
      },
      (error: unknown) => {
        console.error("MSG91 verify OTP failed:", error);

        setError(getMsg91ErrorMessage(error, "Invalid or expired OTP."));

        setLoading(false);
      },
      reqId,
    );
  };

  /*
   * RESEND OTP
   */
  const resendOtp = (channel: "sms" | "voice" = "sms") => {
    setError("");
    setMessage("");

    if (!window.retryOtp) {
      setError("OTP service is not ready.");

      return;
    }

    if (!reqId) {
      setError(
        "OTP session has expired. Please enter your mobile number again.",
      );

      return;
    }

    setLoading(true);

    window.retryOtp(
      channel,

      /*
       * SUCCESS
       */
      (data: Msg91CallbackData) => {
        console.log("MSG91 resend success:", data);

        const requestId = data?.reqId || data?.request_id || data?.requestId;

        if (requestId) {
          setReqId(requestId);
        }

        setMessage("A new OTP has been sent.");

        setLoading(false);
      },

      /*
       * FAILURE
       */
      (error: unknown) => {
        console.error("MSG91 resend failed:", error);

        setError(getMsg91ErrorMessage(error, "Unable to resend OTP."));

        setLoading(false);
      },

      /*
       * Existing request ID
       */
      reqId,
    );
  };

  /*
   * Change number
   */
  const changeMobile = () => {
    setStep("mobile");

    setOtp("");

    setReqId(null);

    setError("");

    setMessage("");
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-5 backdrop-blur-xl"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-3xl border border-white/10 bg-[#091322] p-8 shadow-2xl shadow-cyan-950/30"
        onClick={(event) => event.stopPropagation()}
      >
        {/* HEADER */}

        <div className="mb-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-300">
            LightningQ
          </p>

          {step === "mobile" ? (
            <>
              <h2 className="mt-3 text-3xl font-semibold">Welcome back.</h2>

              <p className="mt-2 text-sm leading-6 text-white/40">
                Sign in to continue with your LightningQ AI agent.
              </p>
            </>
          ) : (
            <>
              <h2 className="mt-3 text-3xl font-semibold">
                Verify your number.
              </h2>

              <p className="mt-2 text-sm leading-6 text-white/40">
                Enter the OTP sent to{" "}
                <span className="text-white/70">+91 {mobile}</span>
              </p>
            </>
          )}
        </div>

        {/* MOBILE */}

        {step === "mobile" && (
          <>
            <label className="mb-2 block text-sm text-white/65">
              Mobile number
            </label>

            <div className="flex overflow-hidden rounded-xl border border-white/10 bg-white/[0.04] focus-within:border-cyan-300/40">
              <span className="border-r border-white/10 px-4 py-4 text-sm text-white/40">
                +91
              </span>

              <input
                type="tel"
                inputMode="numeric"
                autoComplete="tel"
                maxLength={10}
                value={mobile}
                onChange={(event) => {
                  setMobile(event.target.value.replace(/\D/g, "").slice(0, 10));

                  setError("");
                }}
                placeholder="Enter mobile number"
                className="flex-1 bg-transparent px-4 text-sm text-white outline-none placeholder:text-white/25"
              />
            </div>

            {error && <ErrorMessage message={error} />}

            <button
              onClick={sendOtp}
              disabled={loading || mobile.length !== 10 || !sdkReady}
              className="mt-5 w-full rounded-xl bg-gradient-to-r from-cyan-400 to-violet-500 py-4 text-sm font-semibold text-black transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-40"
            >
              {loading ? "Sending OTP..." : "Continue →"}
            </button>

            {!sdkReady && (
              <p className="mt-3 text-center text-xs text-white/25">
                Initializing secure OTP...
              </p>
            )}

            <p className="mt-5 text-center text-xs text-white/25">
              Your number is used to securely authenticate your LightningQ
              account.
            </p>
          </>
        )}

        {/* OTP */}

        {step === "otp" && (
          <>
            <div className="flex gap-2">
              {Array.from({
                length: 6,
              }).map((_, index) => (
                <input
                  key={index}
                  id={`login-otp-${index}`}
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={otp[index] || ""}
                  onChange={(event) => {
                    const value = event.target.value.replace(/\D/g, "");

                    const digits = otp.split("");

                    digits[index] = value.slice(-1);

                    setOtp(digits.join("").slice(0, 6));

                    setError("");

                    if (value && index < 5) {
                      document
                        .getElementById(`login-otp-${index + 1}`)
                        ?.focus();
                    }
                  }}
                  onKeyDown={(event) => {
                    if (event.key === "Backspace" && !otp[index] && index > 0) {
                      document
                        .getElementById(`login-otp-${index - 1}`)
                        ?.focus();
                    }
                  }}
                  className="h-14 w-full rounded-xl border border-white/10 bg-white/[0.04] text-center text-xl font-semibold text-white outline-none transition focus:border-cyan-300/50 focus:ring-2 focus:ring-cyan-300/10"
                />
              ))}
            </div>

            {message && <p className="mt-4 text-sm text-cyan-300">{message}</p>}

            {error && <ErrorMessage message={error} />}

            <button
              onClick={verifyOtp}
              disabled={loading || otp.length !== 6}
              className="mt-6 w-full rounded-xl bg-gradient-to-r from-cyan-400 to-violet-500 py-4 text-sm font-semibold text-black transition disabled:cursor-not-allowed disabled:opacity-40"
            >
              {loading ? "Verifying..." : "Verify & Continue →"}
            </button>

            <div className="mt-5 flex items-center justify-between">
              <button
                onClick={changeMobile}
                disabled={loading}
                className="text-sm text-white/35 transition hover:text-white"
              >
                ← Change number
              </button>

              <button
                onClick={() => resendOtp("sms")}
                disabled={loading}
                className="text-sm text-cyan-300/70 transition hover:text-cyan-300 disabled:opacity-40"
              >
                Resend OTP
              </button>
            </div>
          </>
        )}

        <button
          onClick={onClose}
          disabled={loading}
          className="mt-7 w-full text-sm text-white/30 transition hover:text-white"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
