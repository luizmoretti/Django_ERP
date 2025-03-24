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
    email : string;
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
        email: "",
        password: ""
    },
})

  async function handleSubmitLogin(data: TFormLogin) {
        setError(null);
        setLoading(true);

        try{
            const apiURL= process.env.NEXT_PUBLIC_API_URL;


            const response = await axios.post(`${apiURL}/user/login/`,{
                email:data.email,
                password:data.password,
            });
            const {token,base,redirect_url} = response.data;


            const {acess,refresh} = response.data;
            
            Cookies.set('acess_token', token,{secure:true,sameSite:'strict'});
            Cookies.set('acess_token', acess,{secure:true,sameSite:'strict'});
            Cookies.set('refresh_token', refresh, {secure:true,sameSite:'strict'});
            
            const userResponse = await axios.get(`${apiURL}/user/`,{
                headers:{
                    Authorization:`Bearer ${acess}`,
                }
            })

            login(userResponse.data);


            router.push("/products");        
        } catch(err){
            setError("Email ou senha inválidos.");
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
                <CardHeader className="justify-center items-center">
                    <CardTitle className="justify-center items-center">Sign-In</CardTitle> 
                <CardDescription className="justify-center items-center">
                    Please login to your Account
                </CardDescription>
                </CardHeader>
                <CardContent>
                    {error && (
                        <p className="text-red-500 text-sm mb-2 text-center" aria-live="assertive">
                            {error}
                        </p>
                    )}
                    <Form {...form}>
                        <form className="space-y-4" onSubmit={form.handleSubmit(handleSubmitLogin)}>
                            <FormField
                                control={form.control}
                                name="email"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormControl>
                                            <Input placeholder="Email"{...field}disabled={loading}/>
                                        </FormControl>
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="password"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormControl>
                                            <Input type="password" placeholder="password"{...field}disabled={loading}/>
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
