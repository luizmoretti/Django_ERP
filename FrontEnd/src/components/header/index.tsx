"use client";
import { useState } from "react";
import { LogOut, UserCircle, Menu, ArrowLeft } from "lucide-react";
import { useSidebar } from "../sidebar/sidebarcontext";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../ui/tooltip";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import { useUser } from "@/context/userContext";

export function Header(){
    const {isSidebarVisible, setisSidebarVisible}= useSidebar();
    const[MenuOpen, setMenuOpen]= useState(false);
    const router = useRouter()
    const {user, logout} = useUser();



    const handleLogout =()=>{
        logout();
        Cookies.remove("acess_token");
        Cookies.remove("refresh_token");
        router.push("/signin");

        setMenuOpen(false);
    }

    return(
        <header className="fixed top-0 left-0 z-30 w-full h-14 bg-transparent border-b
        flex items-center justify-between px-4 shadow-sm">
            <TooltipProvider>
                <Tooltip>
                    <TooltipTrigger asChild>
                        <button
                        onClick={()=> setisSidebarVisible(!isSidebarVisible)}
                        className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground
                        transition-colors hover:text-foreground"
                        >
                            {isSidebarVisible ? <ArrowLeft className="h-5 w-5"/> : <Menu className="h-5 w-5"/>}
                        </button>
                    </TooltipTrigger>
                    <TooltipContent side="bottom">
                        {isSidebarVisible ? "Esconder" : "Mostrar"}
                    </TooltipContent>
                </Tooltip>
            </TooltipProvider>
            <div className="relative">
            <button onClick={()=> setMenuOpen(!MenuOpen)}className="focus:outline-none">
                <Avatar className="w-10 h-10 border border-gray-300">
                    <AvatarImage src={user?.avatar} alt="user"/>
                    <AvatarFallback>{user?.name[0]}</AvatarFallback>
                </Avatar>
            </button>
            
            {MenuOpen && (
                <div className="absolute right-0 top-12 w-56 bg-white rounded-lg shadow-lg p-4">
                    <div className="flex items-center gap-3">
                        <UserCircle className="w-12 h-12 text-gray-500"/>
                        <div>
                            <p className="font-bold">{user?.name}</p>
                            <p className="text-sm text-gray-500">{user?.email}</p>
                        </div>
                    </div>
                    <hr className="my-3"/>
                    <button
                    className="flex w-full items-center gap-2 text-red-600 hover:bg-red-50 p-2 rounded-md"
                    onClick={(handleLogout)=> console.log("Logout")}
                    >
                        <LogOut className="w-5 h-5"/>
                        Sign Out
                    </button>
                </div>
            )}
            </div>
        </header>
    )
}