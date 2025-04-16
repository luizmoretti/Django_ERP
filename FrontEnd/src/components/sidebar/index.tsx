"use client"
import Link from "next/link"
import { Button } from "../ui/button"
import { Sheet, SheetContent, SheetTrigger } from "../ui/sheet"
import {ArrowLeft, BriefcaseBusiness, ChartBar, Circle, HandCoins, HousePlus, Menu, Package, Package2, PackagePlus, Store, Users } from "lucide-react"
import { TooltipProvider, Tooltip, TooltipTrigger } from "../ui/tooltip"
import { useSidebar } from "./sidebarcontext";
import { Header } from "../header"


export function Sidebar(){
    const {isSidebarVisible, setisSidebarVisible} = useSidebar()
    return(
        <div className="flex w-full flex-col bg-muted/40">
            <Header />
            <aside className={`fixed inset-y-0 left-0 z-10 w-60 sm:flex flex-col transition-transform duration-300 ease-in-out ${
                isSidebarVisible ? "translate-x-0":"-translate-x-full"
                }`}
                style={{top: "3.5rem"}}
                >
                <nav className="flex flex-col items-center gap-4 px-2 py-5">
                    <TooltipProvider>
                    <div className="flex items-center gap-3 px-2 py-5">
                        <Link href="#" className="flex h-10 w-10 shrink-0 items-center justify-center text-primary-foreground rounded-full">
                            <img
                                src="/logo.png" alt="Logo" className="h-10 w-10 object-contain" />
                        </Link>
                        </div>
                        <div className="w-full">
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <button
                                 className="flex shrink-0 items-center gap-3 px-4 py-2 w-full
                                justify-center text-muted-foreground transition-colors hover:text-foreground whitespace-nowrap">
                                    <HousePlus className="h-5 w-5" />
                                    {isSidebarVisible && "Warehouses"}
                                </button>
                            </TooltipTrigger>
                        </Tooltip>

                        <Tooltip>
                            <TooltipTrigger asChild>
                            <Link href="/dashboard"
                        className="flex gap-3 px-4 py-2 shrink-0 items-center justify-center 
                        text-muted-foreground transition-colors hover:text-foreground whitespace-nowrap"
                        >

                            <ChartBar className="h-5 w-5"/>
                            {isSidebarVisible && "Dashboard"}
                        </Link>
                            </TooltipTrigger>
                        </Tooltip>
                        <Tooltip>
                            <TooltipTrigger asChild>
                            <Link href="/products"
                        className="flex gap-3 px-4 py-2 shrink-0 items-center justify-center 
                        text-muted-foreground transition-colors hover:text-foreground whitespace-nowrap"
                        >

                            <Package2 className="h-5 w-5"/>
                            {isSidebarVisible && "Products"}
                        </Link>
                            </TooltipTrigger>
                        </Tooltip>
                        <Tooltip>
                            <TooltipTrigger asChild>
                            <Link href="/categories"
                        className="flex gap-3 px-4 py-2 shrink-0 items-center justify-center 
                        text-muted-foreground transition-colors hover:text-foreground whitespace-nowrap"
                        >

                            <PackagePlus className="h-5 w-5"/>
                            {isSidebarVisible && "Categories"}
                        </Link>
                            </TooltipTrigger>
                        </Tooltip>
                        <Tooltip>
                            <TooltipTrigger asChild>
                            <Link href="/brands"
                        className="flex gap-3 px-4 py-2 shrink-0 items-center justify-center 
                        text-muted-foreground transition-colors hover:text-foreground whitespace-nowrap"
                        >

                            <BriefcaseBusiness className="h-5 w-5"/>
                            {isSidebarVisible && "Brands"}
                        </Link>
                            </TooltipTrigger>
                        </Tooltip>
                        <Tooltip>
                            <TooltipTrigger asChild>
                            <Link href="/stores"
                        className="flex gap-3 px-4 py-2 shrink-0 items-center justify-center 
                        text-muted-foreground transition-colors hover:text-foreground whitespace-nowrap"
                        >

                            <Store className="h-5 w-5"/>
                            {isSidebarVisible && "Stores"}
                        </Link>
                            </TooltipTrigger>
                        </Tooltip>
                        <Tooltip>
                            <TooltipTrigger asChild>
                            <Link href="/suppliers"
                        className="flex gap-3 px-4 py-2 shrink-0 items-center justify-center 
                        text-muted-foreground transition-colors hover:text-foreground whitespace-nowrap"
                        >

                            <Users className="h-5 w-5"/>
                            {isSidebarVisible && "Suppliers"}
                        </Link>
                            </TooltipTrigger>
                        </Tooltip>
                        <Tooltip>
                            <TooltipTrigger asChild>
                            <Link href="#"
                        className="flex gap-3 px-4 py-2 shrink-0 items-center justify-center 
                        text-muted-foreground transition-colors hover:text-foreground whitespace-nowrap"
                        >

                            <HandCoins className="h-5 w-5"/>
                            {isSidebarVisible && "Movements"}
                        </Link>
                            </TooltipTrigger>
                        </Tooltip>
                        </div>
                    </TooltipProvider>
                </nav>
            </aside>
            
            <div className="sm:hidden flex flex-col sm:gap-4 sm:py-4 sm:pl-14">
                <header className="sticky top-0 z-30 flex h-14 items-center px-4 border-b bg-background 
                gap-4 sm:static sm:h-auto sm:border-0 sm:bg-transparent sm:px-6">
                    <Sheet>
                        <SheetTrigger asChild>
                            <Button size="icon" variant="outline" className="sm:hidden">
                                <Menu className="w-5 h-5" />
                            </Button>
                        </SheetTrigger>

                        <SheetContent side="left" className="sm:max-w-x">
                            <nav className="grid gap-6 text-lg font-medium">
                                <Link href="#"
                                className="flex h-10 w-10 bg-primary rounded-full text-lg
                                items-center justify-center text-primary-foreground md:text-base gap-2"
                                prefetch={false}
                                >
                                    <Package className="h-5 w-5 transition-all"/>
                                </Link>

                                <Link href="#"
                                className="flex items-center gap-4 px-2.5 text-muted-foreground
                                hover:text-foreground"
                                prefetch={false}
                                >
                                    <HousePlus className="h-5 w-5 transition-all"/>
                                     Warehouse
                                </Link>
                                <Link href="/dashboard"
                                className="flex items-center gap-4 px-2.5 text-muted-foreground
                                hover:text-foreground"
                                prefetch={false}
                                >
                                    <ChartBar className="h-5 w-5 transition-all"/>
                                     Dashboard
                                </Link>

                                <Link href="/products"
                                className="flex items-center gap-4 px-2.5 text-muted-foreground
                                hover:text-foreground"
                                prefetch={false}
                                >
                                    <Package2 className="h-5 w-5 transition-all"/>
                                     Products
                                </Link>
                                <Link href="/categories"
                                className="flex items-center gap-4 px-2.5 text-muted-foreground
                                hover:text-foreground"
                                prefetch={false}
                                >
                                    <Circle className="h-5 w-5 transition-all"/>
                                     Categories
                                </Link>
                                <Link href="/brands"
                                className="flex items-center gap-4 px-2.5 text-muted-foreground
                                hover:text-foreground"
                                prefetch={false}
                                >
                                    <BriefcaseBusiness className="h-5 w-5 transition-all"/>
                                     Brands
                                </Link>
                                <Link href="/stores"
                                className="flex items-center gap-4 px-2.5 text-muted-foreground
                                hover:text-foreground"
                                prefetch={false}
                                >
                                    <Store className="h-5 w-5 transition-all"/>
                                     Stores
                                </Link>
                                <Link href="#"
                                className="flex items-center gap-4 px-2.5 text-muted-foreground
                                hover:text-foreground"
                                prefetch={false}
                                >
                                    <Users className="h-5 w-5 transition-all"/>
                                     Suppliers
                                </Link>
                                <Link href="#"
                                className="flex items-center gap-4 px-2.5 text-muted-foreground
                                hover:text-foreground"
                                prefetch={false}
                                >
                                    <HandCoins className="h-5 w-5 transition-all"/>
                                     Movements
                                </Link>
                            </nav>
                        </SheetContent>
                    </Sheet>
                </header>
            </div>
        </div>
    )
}