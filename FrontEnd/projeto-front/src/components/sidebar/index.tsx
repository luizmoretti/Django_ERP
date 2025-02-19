import { Sheet, SheetTrigger, SheetContent, SheetTitle } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import Link from "next/link";
import { Workflow, ChartNoAxesCombined, GitFork, Home, Package, PanelBottom, Store, Combine, Target, ShoppingBag, Users, Package2, LogOut } from "lucide-react";
import { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent } from "@radix-ui/react-tooltip";
import { VisuallyHidden } from "@radix-ui/react-visually-hidden";


export function Sidebar() {
    return (
        <div className="flex w-full flex-col bg-muted/40">

            <aside className="fixed inset-y-0 left-0 z-10 hidden w-14 border-r bg-background
            sm:flex flex-col">

                <nav className="flex flex-col items-center gap-4 px-2 py-5">
                    <TooltipProvider>
                        <Link
                            href=""
                            className="flex h-9 w-9 shrink-0 items-center justify-center bg-primary
                        text-primary-foreground rounded-full"
                        >
                            <GitFork className="h-4 w-4 " />
                            <span className="sr-only">Stock</span>
                        </Link>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Link
                                    href=""
                                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg
                                text-muted-foreground transition-colors hover:text-foreground"
                                >
                                    <ChartNoAxesCombined className="h-5 w-5" />
                                    <span className="sr-only">Dashboard</span>
                                </Link>
                            </TooltipTrigger>
                            <TooltipContent side="right">Dashboard</TooltipContent>
                        </Tooltip>

                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Link
                                    href=""
                                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg
                                text-muted-foreground transition-colors hover:text-foreground"
                                >
                                    <Package className="h-5 w-5" />
                                    <span className="sr-only">Products</span>
                                </Link>
                            </TooltipTrigger>
                            <TooltipContent side="right">Products</TooltipContent>
                        </Tooltip>

                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Link
                                    href=""
                                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg
                                text-muted-foreground transition-colors hover:text-foreground"
                                >
                                    <Package2 className="h-5 w-5" />
                                    <span className="sr-only">Categories</span>
                                </Link>
                            </TooltipTrigger>
                            <TooltipContent side="right">Categories</TooltipContent>
                        </Tooltip>

                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Link
                                    href=""
                                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg
                                text-muted-foreground transition-colors hover:text-foreground"
                                >
                                    <Workflow className="h-5 w-5" />
                                    <span className="sr-only">Brands</span>
                                </Link>
                            </TooltipTrigger>
                            <TooltipContent side="right">Brands</TooltipContent>
                        </Tooltip>

                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Link
                                    href=""
                                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg
                                text-muted-foreground transition-colors hover:text-foreground"
                                >
                                    <Store className="h-5 w-5" />
                                    <span className="sr-only">Store</span>
                                </Link>
                            </TooltipTrigger>
                            <TooltipContent side="right">Store</TooltipContent>
                        </Tooltip>

                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Link
                                    href=""
                                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg
                                text-muted-foreground transition-colors hover:text-foreground"
                                >
                                    <Users className="h-5 w-5" />
                                    <span className="sr-only">Suppliers</span>
                                </Link>
                            </TooltipTrigger>
                            <TooltipContent side="right">Suppliers</TooltipContent>
                        </Tooltip>

                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Link
                                    href=""
                                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg
                                text-muted-foreground transition-colors hover:text-foreground"
                                >
                                    <Package className="h-5 w-5" />
                                    <span className="sr-only">Products</span>
                                </Link>
                            </TooltipTrigger>
                            <TooltipContent side="right">Producs</TooltipContent>
                        </Tooltip>

                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Link
                                    href=""
                                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg
                                text-muted-foreground transition-colors hover:text-foreground"
                                >
                                    <Target className="h-5 w-5" />
                                    <span className="sr-only">Movements</span>
                                </Link>
                            </TooltipTrigger>
                            <TooltipContent side="right">Movements</TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
                </nav>

                <nav className="mt-auto flex flex-col items-center gap-4 px-4 py-5">
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Link
                                    href=""
                                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg
                                text-muted-foreground transition-colors hover:text-foreground"
                                >
                                    <LogOut className="h-5 w-5" />
                                    <span className="sr-only">Logout</span>
                                </Link>
                            </TooltipTrigger>
                            <TooltipContent side="right">Logout</TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
                </nav>
            </aside>

            <div className="sm:hidden flex flex-col sm:gap-4 sm:py-4 sm:pl-14">
                <header className="sticky top-0 z-30 flex h-14 items-center px-4 border-b 
                bg-background gap-4 sm:static sm:h-auto sm:border-0 sm:bg-transparent sm:px-6">
                    <Sheet>
                        <SheetTrigger asChild>
                            <Button size="icon" variant="outline" className="sm:hidden">
                                <PanelBottom className="w-5 h-5" />
                                <span className="sr-only">Abrir / fechar menu</span>
                            </Button>
                        </SheetTrigger>

                        <SheetContent side="left" className="sm:max-w-x">
                            <SheetTitle>
                                <VisuallyHidden>Menu</VisuallyHidden>
                            </SheetTitle>
                            <nav className="grid gap-6 text-lg font-medium">
                                <Link
                                    href="#"
                                    className="flex h-10 w-10 bg-primary rounded-full text-lg
                                    items-center justify-center text-primary-foreground md:text-base
                                    gap-2"
                                    prefetch={false}
                                >
                                    <Package className="h-5 w-5 transition-all" />
                                    <span className="sr-only">Logo</span>
                                </Link>

                                <Link
                                    href="#"
                                    className="flex items-center gap-4 px-2.5 text-muted-foreground
                                    hover:text-foreground"
                                    prefetch={false}
                                >
                                    <GitFork className="h-5 w-5 transition-all" />
                                    Stock
                                </Link>

                                <Link
                                    href="#"
                                    className="flex items-center gap-4 px-2.5 text-muted-foreground
                                    hover:text-foreground"
                                    prefetch={false}
                                >
                                    <ChartNoAxesCombined className="h-5 w-5 transition-all" />
                                    Dashboard
                                </Link>

                                <Link
                                    href="../pages/categories"
                                    className="flex items-center gap-4 px-2.5 text-muted-foreground
                                    hover:text-foreground"
                                    prefetch={false}
                                >
                                    <Package className="h-5 w-5 transition-all" />
                                    Categories
                                </Link>

                                <Link
                                    href="#"
                                    className="flex items-center gap-4 px-2.5 text-muted-foreground
                                    hover:text-foreground"
                                    prefetch={false}
                                >
                                    <Workflow className="h-5 w-5 transition-all" />
                                    Brands
                                </Link>

                                <Link
                                    href="#"
                                    className="flex items-center gap-4 px-2.5 text-muted-foreground
                                    hover:text-foreground"
                                    prefetch={false}
                                >
                                    <Store className="h-5 w-5 transition-all" />
                                    Stores
                                </Link>

                                <Link
                                    href="#"
                                    className="flex items-center gap-4 px-2.5 text-muted-foreground
                                    hover:text-foreground"
                                    prefetch={false}
                                >
                                    <Combine className="h-5 w-5 transition-all" />
                                    Suppliers
                                </Link>

                                <Link
                                    href="#"
                                    className="flex items-center gap-4 px-2.5 text-muted-foreground
                                    hover:text-foreground"
                                    prefetch={false}
                                >
                                    <Target className="h-5 w-5 transition-all" />
                                    Products
                                </Link>

                                <Link
                                    href="#"
                                    className="flex items-center gap-4 px-2.5 text-muted-foreground
                                    hover:text-foreground"
                                    prefetch={false}
                                >
                                    <Target className="h-5 w-5 transition-all" />
                                    Movements
                                </Link>
                            </nav>
                        </SheetContent>
                    </Sheet>
                    <h2>Menu</h2>
                </header>
            </div>
        </div>
    )
}