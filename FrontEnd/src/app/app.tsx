import { UserProvider } from "@/context/userContext";
import { useSyncUser } from "@/context/useSyncUser";

import { AppProps } from "next/app";

export default function App({ Component, pageProps }: AppProps){
    useSyncUser();

    return(
        <UserProvider>
            <Component {...pageProps} />
        </UserProvider>
    )
}