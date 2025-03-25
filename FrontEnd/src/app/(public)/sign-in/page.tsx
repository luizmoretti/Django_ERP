"use client";
import { Button } from "@/components/ui/button";
import {useState, useContext, useRef, useEffect} from "react";
import { useRouter } from "next/navigation";
import { AuthContext } from "@/context/authcontext";
import { useUser } from "@/context/userContext";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useForm } from "react-hook-form";
import axios from "axios";
import Cookies from "js-cookie";
import { Eye, EyeOff, Loader2 } from "lucide-react";

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
const [rememberMe, setRememberMe]= useState(false);
const usernameRef = useRef<HTMLInputElement>(null); // Correctly implemented useRef
const [showPassword, setShowPassword] = useState(false);

const form = useForm<TFormLogin>({
    defaultValues: {
        email: "",
        password: ""
    },
})

    useEffect(()=>{
        const savedEmail = localStorage.getItem("rememberedEmail");
        const savedPassword = localStorage.getItem("rememberedPassword");

        if(savedEmail && savedPassword){
            form.setValue("email", savedEmail);
            form.setValue("password", savedPassword);
            setRememberMe(true);
        }
    },[form]);

  async function handleSubmitLogin(data: TFormLogin) {
        setError(null);
        setLoading(true);

        try{
            const apiURL=process.env.NEXT_PUBLIC_API_URL;

            const response = await axios.post(`${apiURL}/user/login/`,{
                email:data.email,
                password:data.password,
            });


            const {token,acess,refresh} = response.data;
            
            Cookies.set('acess_token', token,{secure:true,sameSite:'strict'});
            Cookies.set('acess_token', acess,{secure:true,sameSite:'strict'});
            Cookies.set('refresh_token', refresh, {secure:true,sameSite:'strict'});
            
            const userResponse = await axios.get(`${apiURL}/user/`,{
                headers:{
                    Authorization:`Bearer ${acess}`,
                }
            })

            login(userResponse.data);

            if(rememberMe){
                localStorage.setItem("rememberedEmail", data.email);
                localStorage.setItem("rememberedPassword", data.password);
            }else{
                localStorage.removeItem("rememberedEmail");
                localStorage.removeItem("rememberedPassword");
            }


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
                                        <div className="relative">
                                            <FormControl>
                                                <Input type={showPassword ? "text": "password"}
                                                placeholder="password"
                                                disabled={loading}
                                                {...field}
                                                className="pr-10"
                                                />
                                            </FormControl>
                                            <button
                                            type="button"
                                            onClick={()=> setShowPassword(!showPassword)}
                                            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400
                                            hover:text-gray-600 focus:outline-none"
                                            disabled={loading}
                                            >
                                                {showPassword ? (
                                                    <EyeOff className="h-4 w-4"/>
                                                ):(
                                                    <Eye className="h-4 w-4"/>
                                                )}
                                            </button>
                                        </div>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <div className="flex items-center space-x-2">
                                <input
                                type="checkbox"
                                id="rememberMe"
                                checked={rememberMe}
                                onChange={()=> setRememberMe(!rememberMe)}
                                className="hidden peer"
                                />
                                <label htmlFor="rememberMe"
                                className="w-5 h-5 flex items-center justify-center border-2 border-gray-300
                                rounded-full cursor-pointer peer-checked:bg-blue-600 transition-all duration-200"
                                >
                                    {rememberMe && (
                                        <svg
                                        className="w-4 h-4 text-white"
                                        fill="none"
                                        stroke="currentColor"
                                        strokeWidth="2"
                                        viewBox="0 0 24 24"
                                        xmlns="http://www.w3.org/2000/svg"
                                    >
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7"></path>
                                        </svg>
                                    )}
                                    </label>
                                    <span className="text-sm text-gray-600 select-none"onClick={()=>
                                        setRememberMe(!rememberMe)}>
                                            Remember-me
                                        </span>                            
                                    </div>
                            <Button className="w-full" type="submit" disabled={loading}>
                              {loading ?(
                                <div className="flex items-center justify-center gap-2">
                                    <Loader2 className="h-4 w-4 animate-spin"/>
                                    <span>Signing in...</span>
                                </div>
                                ):(
                                    "Sign In"
                                )}
                            </Button>   
                        </form>
                    </Form>
                </CardContent>
            </Card>
        </div>
    )
}

