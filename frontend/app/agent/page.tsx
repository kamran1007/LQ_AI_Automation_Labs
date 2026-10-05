"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getAuth } from "@/lib/auth";

export default function AgentPage() {
  const router = useRouter();

  useEffect(() => {
    const auth = getAuth();

    if (!auth) {
      router.replace("/");
    }
  }, [router]);

  return (
    <main className="min-h-screen bg-[#030712] text-white">
      <div className="mx-auto max-w-5xl px-6 py-20">
        <p className="text-sm text-cyan-300">
          LightningQ AI Agent
        </p>

        <h1 className="mt-4 text-5xl font-semibold">
          How can I help?
        </h1>

        <p className="mt-4 text-white/40">
          Your authenticated LightningQ experience starts here.
        </p>
      </div>
    </main>
  );
}