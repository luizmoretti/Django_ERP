"use client";
import React, {createContext, useContext, useState} from "react";

interface User {
    id: number;
    name: string;
    email: string;
    avatar?:string;
}

interface UserContextType {
    user: User | null;
    login: (userData: User) => void;
    logout: () => void;
}

const UserContext = createContext<UserContextType>({
    user: null,
    login: () => {},
    logout: () => {}
});

export const useUser =()=>{
    return useContext(UserContext);
}

export const UserProvider: React.FC<{children: React.ReactNode}> = ({children})=>{
    const [user, setUser] = useState<User | null>(null);

    interface User {
        id: number;
        name: string;
        email: string;
    }

    const login = (userData: User) => {
        setUser(userData);
    };

    const logout = ()=>{
        setUser(null);
    };

    return (
        <UserContext.Provider value={{user, login, logout}}>
            {children}
        </UserContext.Provider>
    )
}