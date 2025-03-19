"use client";
import { Button } from "@/components/ui/button";
import {useState, useContext, useRef} from "react";
import { useRouter } from "next/navigation";
import { AuthContext } from "@/context/authcontext";
import { useUser } from "@/context/userContext";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useForm } from "react-hook-form";
import axios from "axios";
import Cookies from "js-cookie";

type TFormLogin= {
    username : string;
    password : string;
}

export default function SignIn() {
const authContext = useContext(AuthContext);
if(!authContext){
    throw new Error("AuthContext não foi encontrado. verifique se o AuthProvider está corretamente definido");
}
const { login } = useUser();


const router = useRouter();
const [error, setError]= useState<string | null>(null);
const [loading, setLoading]= useState(false);
const usernameRef = useRef<HTMLInputElement>(null); // Correctly implemented useRef

const form = useForm<TFormLogin>({
    defaultValues: {
        username: "",
        password: ""
    },
})

  async function handleSubmitLogin(data: TFormLogin) {
        setError(null);
        setLoading(true);

        try{
            const response = await axios.post('http://localhost:8000/api/token',{
                username:data.username,
                password:data.password,
            });
            const {acess,refresh} = response.data;
            
            Cookies.set('acess_token', acess,{secure:true,sameSite:'strict'});
            Cookies.set('refresh_token', refresh, {secure:true,sameSite:'strict'});
            
            const userResponse = await axios.get('http://localhost:8000/api/user',{
                headers:{
                    Authorization:`Bearer ${acess}`,
                }
            })

            login(userResponse.data);


            router.push("/dashboard");        
        } catch(err){
            setError("Usuário ou senha inválidos.");
            console.error("Erro no login",err);
            usernameRef.current?.focus();
        }finally{
            setLoading(false);
        }
    }

    return (
        <div className="w-full h-screen flex items-center justify-center">
            <Card className="w-full max-w-sm">
            <div className="flex justify-center items-center">
                    <img
                        src="/logo.png" alt="Logo" className="h-20 w-20"/>
                    <span className="sr-only" />
                </div>
                <CardHeader>
                    <CardTitle>Sign-In</CardTitle> 
                <CardDescription>
                    Please login to your Account
                </CardDescription>
                </CardHeader>
                <CardContent>
                    {error && (
                        <p className="text-red-500 text-sm mb-2" aria-live="assertive">
                            {error}
                        </p>
                    )}
                    <Form {...form}>
                        <form className="space-y-4" onSubmit={form.handleSubmit(handleSubmitLogin)}>
                            <FormField
                                control={form.control}
                                name="username"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Username</FormLabel>
                                        <FormControl>
                                            <Input placeholder="Enter your username"{...field}disabled={loading}/>
                                        </FormControl>
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="password"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Password</FormLabel>
                                        <FormControl>
                                            <Input type="password" placeholder="Enter your password"{...field}disabled={loading}/>
                                        </FormControl>
                                    </FormItem>
                                )}
                            />
                            <Button className="w-full" type="submit" disabled={loading}>
                              {loading ? "LogOn...": "SigIn"}</Button>   
                        </form>
                    </Form>
                </CardContent>
            </Card>
        </div>
    )
}

// Removed incorrect custom useRef implementation
