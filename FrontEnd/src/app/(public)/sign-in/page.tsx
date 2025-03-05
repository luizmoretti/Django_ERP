"use client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useForm } from "react-hook-form";

type TFormLogin= {
    username : string;
    password : string;
}

export default function SignIn() {
const form = useForm<TFormLogin>({
    defaultValues: {
        username: "",
        password: ""
    },
})

    function handleSubmitLogin(data: TFormLogin) {
        console.log(data);
    }

    return (
        <div className="w-full h-screen flex items-center justify-center">
            <Card className="w-full max-w-sm">
            <div className="flex justify-center items-center">
                    <img
                        src="/logo.png" alt="Logo" className="h-20 w-20" />
                    <span className="sr-only" />
                </div>
                <CardHeader>
                    <CardTitle>Sign-In</CardTitle> 
                <CardDescription>
                    Please login to your Account
                </CardDescription>

                </CardHeader>
                <CardContent>
                    <Form {...form}>
                        <form className="space-y-4" onSubmit={form.handleSubmit(handleSubmitLogin)}>
                            <FormField
                                control={form.control}
                                name="username"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Username</FormLabel>
                                        <FormControl>
                                            <Input placeholder="Enter your username"{...field}/>
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
                                            <Input type="password" placeholder="Enter your password"{...field}/>
                                        </FormControl>
                                    </FormItem>
                                )}
                            />
                            <Button className="w-full" type="submit">Sign In</Button>   
                        </form>
                    </Form>
                </CardContent>
            </Card>
        </div>
    )
}