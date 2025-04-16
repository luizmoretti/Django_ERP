import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "@/app/globals.css";
import { cn } from "@/lib/utils";
import { Sidebar } from "@/components/sidebar";
import { SidebarProvider } from "@/components/sidebar/sidebarcontext";
import { AuthProvider } from "@/context/authcontext";
import { UserProvider } from "@/context/userContext";
import { ThemeProvider } from "next-themes";

const inter = Inter({subsets: ["latin"]});

export const metadata: Metadata = {
  title: "Public Pages ERP",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={cn("min-h-screen bg-background font-sans antialiased",
        inter.className 
      )}>
        <AuthProvider>
        <UserProvider>
          <ThemeProvider attribute="class"defaultTheme="system">
        <SidebarProvider>
          <div className="flex w-full flex-col bg-muted/40">
        <Sidebar />
        {children}
        </div>
        </SidebarProvider>
        </ThemeProvider>
      </UserProvider>
      </AuthProvider>
      </body>
    </html>
  );
}
