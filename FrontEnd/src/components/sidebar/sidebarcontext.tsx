"use client"
import React, { createContext, useState, useContext } from "react"

type SidebarContextType = {
    isSidebarVisible: boolean;
    setisSidebarVisible:(visible:boolean) => void;
};

const SidebarContext = createContext<SidebarContextType | undefined>(undefined);

export const SidebarProvider = ({children} : {children: React.ReactNode}) => {
    const [isSidebarVisible, setisSidebarVisible] = useState(true);

    return(
        <SidebarContext.Provider value= {{isSidebarVisible, setisSidebarVisible}}>
            {children}
        </SidebarContext.Provider>
    );
};

export const useSidebar = () =>{
    const context = useContext(SidebarContext);
    if(!context){
        throw new Error("useSidebar must be used within a SidebarProvider");
    }
    return context;
}

