import { useEffect } from "react";
import axios from 'axios';
import Cookies from 'js-cookie';
import { useUser } from "./userContext";

export const useSyncUser =()=>{
    const {user, login} = useUser();

    useEffect(()=>{
        const acessToken = Cookies.get('acess_token');

        if(acessToken && !user){
            const fetchUserData = async () =>{
                try{
                    const response = await axios.get('http://localhost:8000/api/v1/user/',{
                        headers:{
                            Authorization: `Bearer ${acessToken}`,
                        },
                    });
                    login(response.data);
                }   catch(error){
                    console.error('Erro na busca dos dados:', error);
                    Cookies.remove('acess_token');
                }
            };

            fetchUserData();
        }
    }, [user, login]);
        
}