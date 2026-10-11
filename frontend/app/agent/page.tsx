"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  metadata?: ChatMetadata | null;
};

type ChatMetadata = {
  appointment_request_id?: number;
  doctor_id?: number;
  hospital_id?: number;
  requested_start_at?: string;
  duration_minutes?: number;
  visit_reason?: string | null;
  status?: string;
};

type ChatResponse = {
  success?: boolean;
  message: string;
  intent?: string;

  workflow?: {
    step?: string;
    action?: string;
    appointment_request_id?: number;
  } | null;

  metadata?: ChatMetadata | null;
  booking_state?: unknown | null;
};

type Conversation = {
  id: number;
  user_id: number;
  message: string;
  ai_response: string;
  intent?: string | null;

  extra_data?: {
    metadata?: Record<string, unknown> | null;
    booking_state?: unknown | null;
  } | null;

  created_at: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://127.0.0.1:8000";

export default function AgentPage() {
  const router = useRouter();

  // --------------------------------------------------
  // STATE
  // --------------------------------------------------

  const [messages, setMessages] =
    useState<Message[]>([]);

  const [input, setInput] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [accountMenuOpen, setAccountMenuOpen] =
    useState(false);

  // Important:
  // Do not read localStorage inside useState().
  // This prevents Next.js hydration mismatch.
  const [userName, setUserName] =
    useState("My account");

  const textareaRef =
    useRef<HTMLTextAreaElement>(null);

  // --------------------------------------------------
  // LOAD USER NAME
  // --------------------------------------------------

  useEffect(() => {
    const storedName =
      localStorage.getItem(
        "lightningq_user_name"
      );

    if (storedName) {
      setUserName(storedName);
    }
  }, []);

  // --------------------------------------------------
  // LOAD AUTH + CONVERSATIONS
  // --------------------------------------------------

  useEffect(() => {
    const loadConversations = async () => {
      const token =
        localStorage.getItem(
          "lightningq_access_token"
        );

      // ----------------------------------------------
      // User is not logged in
      // ----------------------------------------------

      if (!token) {
        router.replace("/");
        return;
      }

      try {
        const response = await fetch(
          `${API_BASE_URL}/ai/conversations?limit=100&offset=0`,
          {
            method: "GET",
            headers: {
              Authorization:
                `Bearer ${token}`,
              "Content-Type":
                "application/json",
            },
          }
        );

        // --------------------------------------------
        // Authentication expired
        // --------------------------------------------

        if (response.status === 401) {
          localStorage.removeItem(
            "lightningq_access_token"
          );

          localStorage.removeItem(
            "lightningq_refresh_token"
          );

          localStorage.removeItem(
            "lightningq_session_id"
          );

          localStorage.removeItem(
            "lightningq_user_id"
          );

          localStorage.removeItem(
            "lightningq_user_name"
          );

          router.replace("/");
          return;
        }

        // --------------------------------------------
        // Other HTTP errors
        // --------------------------------------------

        if (!response.ok) {
          const errorData =
            await response
              .json()
              .catch(() => null);

          throw new Error(
            errorData?.detail ||
              errorData?.message ||
              "Unable to load conversations."
          );
        }

        // --------------------------------------------
        // Parse conversations
        // --------------------------------------------

        const conversations =
          (await response.json()) as Conversation[];

        console.log(
          "Loaded conversations:",
          conversations
        );

        // --------------------------------------------
        // Oldest → newest
        // --------------------------------------------

        conversations.sort(
          (a, b) =>
            new Date(
              a.created_at
            ).getTime() -
            new Date(
              b.created_at
            ).getTime()
        );

        // --------------------------------------------
        // Convert DB conversations into UI messages
        // --------------------------------------------

        const history: Message[] = [];

        for (const conversation of conversations) {
          // User message
          history.push({
            id: `${conversation.id}-user`,
            role: "user",
            content:
              conversation.message,
          });

          // Assistant response
          if (conversation.ai_response) {
            history.push({
              id: `${conversation.id}-assistant`,
              role: "assistant",
              content:
                conversation.ai_response,

              metadata:
                conversation.extra_data
                  ?.metadata as
                  | ChatMetadata
                  | null
                  | undefined,
            });
          }
        }

        // --------------------------------------------
        // Restore chat
        // --------------------------------------------

        setMessages(history);
      } catch (error) {
        console.error(
          "Failed to load conversations:",
          error
        );
      }
    };

    loadConversations();
  }, [router]);

  // --------------------------------------------------
  // AUTO SCROLL
  // --------------------------------------------------

  useEffect(() => {
    const container =
      document.getElementById(
        "chat-messages"
      );

    if (container) {
      container.scrollTop =
        container.scrollHeight;
    }
  }, [messages, loading]);

  // --------------------------------------------------
  // SEND MESSAGE
  // --------------------------------------------------

  const sendMessage = async () => {
    const message = input.trim();

    if (!message || loading) {
      return;
    }

    const userId =
      localStorage.getItem(
        "lightningq_user_id"
      );

    const token =
      localStorage.getItem(
        "lightningq_access_token"
      );

    // ----------------------------------------------
    // Authentication check
    // ----------------------------------------------

    if (!userId || !token) {
      router.replace("/");
      return;
    }

    // ----------------------------------------------
    // Add user message immediately
    // ----------------------------------------------

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: message,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setInput("");
    setLoading(true);

    try {
      // --------------------------------------------
      // Call LightningQ backend
      // --------------------------------------------

      const response = await fetch(
        `${API_BASE_URL}/ai/chat`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",

            Authorization:
              `Bearer ${token}`,
          },

          body: JSON.stringify({
            message,
            user_id: Number(userId),
          }),
        }
      );

      // --------------------------------------------
      // Handle HTTP error
      // --------------------------------------------

      if (!response.ok) {
        let errorMessage =
          "Unable to get a response from LightningQ.";

        try {
          const errorData =
            await response.json();

          errorMessage =
            errorData.detail ||
            errorData.message ||
            errorMessage;
        } catch {
          // Ignore invalid response
        }

        throw new Error(errorMessage);
      }

      // --------------------------------------------
      // Parse ChatResponse
      // --------------------------------------------

      const data =
        (await response.json()) as ChatResponse;

      console.log(
        "LightningQ chat response:",
        data
      );

      // --------------------------------------------
      // Add assistant response
      // --------------------------------------------

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          data.message ||
          "I received your request.",
        metadata: data.metadata,
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);
    } catch (error) {
      console.error(
        "LightningQ chat error:",
        error
      );

      // --------------------------------------------
      // Show error in chat
      // --------------------------------------------

      setMessages((previous) => [
        ...previous,

        {
          id: crypto.randomUUID(),
          role: "assistant",
          content:
            error instanceof Error
              ? error.message
              : "I’m having trouble connecting right now. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);

      setTimeout(() => {
        textareaRef.current?.focus();
      }, 50);
    }
  };

  // --------------------------------------------------
  // ENTER KEY
  // --------------------------------------------------

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      sendMessage();
    }
  };

  // --------------------------------------------------
  // NEW CHAT
  // --------------------------------------------------

  const startNewChat = () => {
    setMessages([]);
    setInput("");

    textareaRef.current?.focus();
  };

  // --------------------------------------------------
  // LOGOUT
  // --------------------------------------------------

  const logout = () => {
    localStorage.removeItem(
      "lightningq_access_token"
    );

    localStorage.removeItem(
      "lightningq_refresh_token"
    );

    localStorage.removeItem(
      "lightningq_session_id"
    );

    localStorage.removeItem(
      "lightningq_user_id"
    );

    localStorage.removeItem(
      "lightningq_user_name"
    );

    router.replace("/");
  };

  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (
    <main className="flex h-screen overflow-hidden bg-[#070b12] text-white">

      {/* ==========================================
          SIDEBAR
          ========================================== */}

      <aside className="hidden w-[270px] flex-col border-r border-white/[0.07] bg-[#090e17] md:flex">

        {/* Logo */}

        <div className="flex h-[72px] items-center px-6">
          <div className="text-xl font-bold tracking-[0.22em]">
            <span className="text-cyan-400">
              LIGHTNING
            </span>

            <span className="text-white">
              Q
            </span>
          </div>
        </div>

        {/* New Chat */}

        <div className="px-4">
          <button
            onClick={startNewChat}
            className="group flex w-full items-center gap-3 rounded-xl border border-white/[0.08] bg-white/[0.04] px-4 py-3 text-sm transition hover:bg-white/[0.08]"
          >
            <span className="text-xl text-cyan-400">
              +
            </span>

            <span>
              New chat
            </span>
          </button>
        </div>

        {/* History */}

        <div className="mt-8 flex-1 overflow-y-auto px-4">
          <div className="mb-3 px-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-white/30">
            Today
          </div>

          {messages.length > 0 && (
            <button
              className="w-full truncate rounded-lg px-3 py-2 text-left text-sm text-white/60 hover:bg-white/[0.05]"
            >
              Current conversation
            </button>
          )}
        </div>

        {/* ======================================
            ACCOUNT
            ====================================== */}

        <div className="relative">

          {/* Account trigger */}

          <button
            onClick={() =>
              setAccountMenuOpen(
                (current) => !current
              )
            }
            className="flex w-full items-center gap-3 rounded-lg px-2 py-2 text-white/40 transition hover:bg-white/[0.06] hover:text-white"
          >
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 to-violet-500 text-xs font-bold">
              LQ
            </div>

            <div className="flex-1 text-left">
              <div className="text-white/80">
                {userName}
              </div>

              <div className="text-xs text-white/30">
                LightningQ user
              </div>
            </div>

            <span>
              ⋯
            </span>
          </button>

          {/* Account menu */}

          {accountMenuOpen && (
            <div className="absolute bottom-16 left-0 right-0 z-50 overflow-hidden rounded-2xl border border-white/10 bg-[#101824] shadow-2xl shadow-black/40 backdrop-blur-xl">

              <div className="border-b border-white/[0.07] p-4">
                <p className="text-sm font-medium text-white">
                  {userName}
                </p>

                <p className="mt-1 text-xs text-white/35">
                  LightningQ account
                </p>
              </div>

              <div className="p-2">

                <button
                  onClick={() => {
                    setAccountMenuOpen(false);
                    router.push("/account");
                  }}
                  className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm text-white/65 transition hover:bg-white/[0.06] hover:text-white"
                >
                  <span>
                    ⚙
                  </span>

                  <span>
                    Account settings
                  </span>
                </button>

                <button
                  onClick={() => {
                    setAccountMenuOpen(false);
                    router.push("/account");
                  }}
                  className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm text-white/65 transition hover:bg-white/[0.06] hover:text-white"
                >
                  <span>
                    👤
                  </span>

                  <span>
                    Profile
                  </span>
                </button>

                <div className="my-2 border-t border-white/[0.06]" />

                <button
                  onClick={() => {
                    setAccountMenuOpen(false);
                    logout();
                  }}
                  className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm text-red-400/80 transition hover:bg-red-400/[0.06] hover:text-red-300"
                >
                  <span>
                    ↪
                  </span>

                  <span>
                    Log out
                  </span>
                </button>

              </div>
            </div>
          )}
        </div>
      </aside>

      {/* ==========================================
          MAIN
          ========================================== */}

      <section className="relative flex min-w-0 flex-1 flex-col">

        {/* Background */}

        <div className="pointer-events-none absolute inset-0 overflow-hidden">

          <div className="absolute left-1/2 top-[-250px] h-[500px] w-[700px] -translate-x-1/2 rounded-full bg-cyan-500/[0.06] blur-[120px]" />

          <div className="absolute bottom-[-250px] right-[-100px] h-[500px] w-[500px] rounded-full bg-violet-600/[0.06] blur-[120px]" />

        </div>

        {/* ======================================
            HEADER
            ====================================== */}

        <header className="relative flex h-[72px] items-center justify-between border-b border-white/[0.06] px-5 md:px-8">

          {/* Mobile logo */}

          <div className="text-lg font-bold tracking-[0.18em] md:hidden">
            <span className="text-cyan-400">
              LIGHTNING
            </span>

            <span>
              Q
            </span>
          </div>

          <div className="hidden md:block" />

          <div className="flex items-center gap-3">

            <div className="hidden text-right sm:block">

              <div className="text-xs text-white/70">
                AI Agent
              </div>

              <div className="text-[10px] text-emerald-400">
                ● Online
              </div>

            </div>

            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 to-violet-500 text-xs font-bold">
              LQ
            </div>

          </div>
        </header>

        {/* ======================================
            CHAT AREA
            ====================================== */}

        <div
          id="chat-messages"
          className="relative flex-1 overflow-y-auto"
        >

          {messages.length === 0 ? (

            /* EMPTY STATE */

            <div className="flex h-full flex-col items-center justify-center px-6 pb-32">

              <div className="mb-8 flex h-20 w-20 items-center justify-center rounded-full border border-cyan-400/20 bg-cyan-400/[0.05] shadow-[0_0_80px_rgba(34,211,238,0.12)]">

                <div className="h-12 w-12 rounded-full bg-gradient-to-br from-cyan-400 to-violet-500" />

              </div>

              <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
                How can I help you?
              </h1>

              <p className="mt-4 max-w-xl text-center text-sm leading-6 text-white/40 md:text-base">
                Tell LightningQ what you need.
                I can help you find, book,
                order, automate, and get things done.
              </p>

              <div className="mt-8 grid w-full max-w-2xl grid-cols-1 gap-3 md:grid-cols-2">

                <button
                  onClick={() =>
                    setInput(
                      "Find a pharmacy near me"
                    )
                  }
                  className="rounded-2xl border border-white/[0.08] bg-white/[0.03] px-5 py-4 text-left text-sm text-white/60 transition hover:border-cyan-400/20 hover:bg-white/[0.06] hover:text-white"
                >
                  Find a pharmacy near me
                </button>

                <button
                  onClick={() =>
                    setInput(
                      "Book a doctor appointment"
                    )
                  }
                  className="rounded-2xl border border-white/[0.08] bg-white/[0.03] px-5 py-4 text-left text-sm text-white/60 transition hover:border-cyan-400/20 hover:bg-white/[0.06] hover:text-white"
                >
                  Book a doctor appointment
                </button>

                <button
                  onClick={() =>
                    setInput("Order Dolo 650")
                  }
                  className="rounded-2xl border border-white/[0.08] bg-white/[0.03] px-5 py-4 text-left text-sm text-white/60 transition hover:border-cyan-400/20 hover:bg-white/[0.06] hover:text-white"
                >
                  Order Dolo 650
                </button>

                <button
                  onClick={() =>
                    setInput(
                      "Find a diagnostic center"
                    )
                  }
                  className="rounded-2xl border border-white/[0.08] bg-white/[0.03] px-5 py-4 text-left text-sm text-white/60 transition hover:border-cyan-400/20 hover:bg-white/[0.06] hover:text-white"
                >
                  Find a diagnostic center
                </button>

              </div>
            </div>

          ) : (

            /* MESSAGES */

            <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-8 md:px-6 md:py-10">

              {messages.map((message) => (

                <div
                  key={message.id}
                  className={
                    message.role === "user"
                      ? "flex justify-end"
                      : "flex justify-start"
                  }
                >

                  {message.role === "user" ? (

                    <div className="max-w-[80%] rounded-2xl rounded-br-md bg-gradient-to-r from-cyan-400 to-blue-500 px-4 py-3 text-sm text-black shadow-lg">
                      {message.content}
                    </div>

                  ) : (

                    <div className="flex max-w-[85%] gap-3">

                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 to-violet-500 text-xs font-bold text-black">
                        LQ
                      </div>

                      <div className="rounded-2xl rounded-bl-md border border-white/[0.08] bg-white/[0.04] px-4 py-3 text-sm leading-6 text-white/80">
                        {message.content}
                      </div>

                    </div>

                  )}

                </div>

              ))}

              {/* Loading */}

              {loading && (

                <div className="flex justify-start">

                  <div className="flex gap-3">

                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 to-violet-500 text-xs font-bold text-black">
                      LQ
                    </div>

                    <div className="rounded-2xl rounded-bl-md border border-white/[0.08] bg-white/[0.04] px-4 py-3">

                      <div className="flex items-center gap-1">

                        <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />

                        <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300 [animation-delay:150ms]" />

                        <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300 [animation-delay:300ms]" />

                      </div>

                    </div>

                  </div>

                </div>

              )}

            </div>
          )}

        </div>

        {/* ======================================
            INPUT
            ====================================== */}

        <div className="relative px-4 pb-5 pt-3 md:px-6 md:pb-7">

          <div className="mx-auto max-w-3xl">

            <div className="relative rounded-2xl border border-white/[0.1] bg-[#0d141f]/95 shadow-2xl shadow-black/30 backdrop-blur-xl transition focus-within:border-cyan-400/30">

              <textarea
                ref={textareaRef}
                value={input}
                onChange={(event) =>
                  setInput(event.target.value)
                }
                onKeyDown={handleKeyDown}
                placeholder="Message LightningQ..."
                rows={1}
                className="max-h-40 min-h-[58px] w-full resize-none bg-transparent px-5 py-4 pr-16 text-sm text-white outline-none placeholder:text-white/25"
              />

              <button
                onClick={sendMessage}
                disabled={
                  !input.trim() ||
                  loading
                }
                aria-label="Send message"
                className="absolute bottom-3 right-3 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-r from-cyan-400 to-violet-500 text-black transition hover:scale-105 disabled:cursor-not-allowed disabled:opacity-30"
              >
                {loading ? "..." : "↑"}
              </button>

            </div>

            <p className="mt-3 text-center text-[10px] text-white/20">
              LightningQ can make mistakes.
              Verify important information.
            </p>

          </div>

        </div>

      </section>

    </main>
  );
}