import type {Metadata} from "next";
import { Inter } from "next/font/google";
import { cn } from "@/lib/utils";
import "@/app/globals.css";
import { SidebarProvider } from "@/components/sidebar/sidebarcontext";
import { Sidebar } from "@/components/sidebar";

const inter = Inter({subsets: ["latin"]});

export const metadata: Metadata = {title:"Suppliers Page"};

export default function RootLayout({children,}: Readonly<{children: React.ReactNode}>)
{
    return(
        <html lang="en">
        <body className={cn("min-h-screen bg-background font-sans antialiased", inter.className)}>
            <SidebarProvider>
            <div className="flex w-full flex-col bg-muted/40">
            <Sidebar/>
            {children}
            </div>
            </SidebarProvider>
        </body>
        </html>
    )
}