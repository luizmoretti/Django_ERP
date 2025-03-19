"use client";

import {createContext, useState, useEffect} from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";

export interface AuthContextType{
    user:any,
    login:(email:string,password:string)=>Promise<void>;
    logout:()=>void;
}

export const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({children}: {children: React.ReactNode})=> {
    const [user, setUser] = useState<any>(null);
    const router = useRouter();

    useEffect(()=>{
        const storedUser = Cookies.get("user");
        if(storedUser){
            setUser(JSON.parse(storedUser));
        }
    },[])

    const login = async(email:string, password:string)=>{
        try{
            const response = await fetch ("http://127.0.0.1:8000/api/v1/login/",{
                method:"POST",
                credentials:"include",
                headers:{
                    "Context-Type":"application/json",
                },
                body:JSON.stringify({email,password}),
            });

            if(!response.ok){
                throw new Error("Erro ao fazer login");
            }

            const data = await response.json();
            setUser(data);

            Cookies.set("user",JSON.stringify(data), {expires:1,secure:true});

            router.push(data.redirect_url || "/products");
        }   catch(error){
            console.error("Erro ao fazer login:",error);
        }
    };

    const logout =()=>{
        Cookies.remove("user");
        setUser(null);
        router.push("/signin");
    };

    return(
        <AuthContext.Provider value={{user, login, logout}}>
            {children}
        </AuthContext.Provider>
    );

;}