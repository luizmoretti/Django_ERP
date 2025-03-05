import type { Metadata } from "next";
import "@/app/globals.css";

export const metadata: Metadata = {
    title: "Sign In",
    description: "Sign in to your account",
    };

export default function PublicLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html>
        <body>
        <div>
        {children}
        </div>
        </body>
    </html>
    
  );
}
