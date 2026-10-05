import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";

export const metadata: Metadata = {
  title: "LightningQ",
  description:
    "Your AI agent for the real world.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}

        <Script
          src="https://verify.msg91.com/otp-provider.js"
          strategy="afterInteractive"
        />
      </body>
    </html>
  );
}