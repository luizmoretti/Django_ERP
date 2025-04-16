"use client";

import { useEffect,useState } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog,DialogTrigger,DialogContent,DialogHeader,DialogTitle } from "@/components/ui/dialog";
import { Table,TableHeader,TableRow,TableHead,TableBody,TableCell } from "@/components/ui/table";
import BarcodeScannerComponent from "react-barcode-reader";
import { Plus } from "lucide-react";

const apiURL = process.env.NEXT_PUBLIC_API_URL + "/movements";

interface Movement{
    id:number;
    date:string;
    product:string;
    quantity:number;
    type:"Entry"|"Exiy";
    origin:string;
    destination:string;
}

export default function MovementsPage(){
    const [movements, setMovements]= useState<Movement[]>([]);
    const [search, setSearch]= useState("");
    const [modalOpen, setModalOpen]= useState(false);
    const [scannerResult, setScannerResult]= useState("");
    const [origin, setOrigin]= useState("Fetching location...");
    const [destination, setDestination]= useState("");
    const [rowsPerPage, setRowsPerPage]= useState(10);

    useEffect(()=>{
        loadMovements();
        getLocation();
    },[]);

    const loadMovements = async ()=>{
        try{
            const response = await axios.get(apiURL);
            setMovements(response.data);
        }catch(error){
        console.error("Erro ao buscar movements", error);
        }
    };
    
    const getLocation = ()=>{
        if("geolocation" in navigator){
            navigator.geolocation.getCurrentPosition(
                (position)=>{
                    setOrigin(`Lat: ${position.coords.latitude},Lng: ${position.coords.longitude}`);
                },
                ()=>{
                    setOrigin("Não foi possivel obter a localização");
                }
            );
        }
    };

    return(
        <div className="flex flex-col p-6 ml-64 w-[calc(100%-16rem)]">
            <div className="flex border items-center justify-between bg-white shadow p-4 mb-4 rounded-md">
                <h1 className="text-2xl font-bold">Movements</h1>
                <div className="flex items-center gap-4">
                    <Input
                    type="text"
                    placeholder="Search..."
                    value={search}
                    onChange={(e)=> setSearch(e.target.value)}
                    className="w-64"
                    />
                    <Dialog open={modalOpen}onOpenChange={setModalOpen}>
                        <DialogTrigger asChild>
                            <Button className="bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-2">
                                <Plus size={16}/>
                                Add
                            </Button> 
                        </DialogTrigger>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>New Movement</DialogTitle>
                            </DialogHeader>
                            <div className="space-y-4">
                                <label className="block text-sm font-medium">Scanner</label>
                                <div className="border p-4 text-center bg-gray-100">
                                    {scannerResult ? (
                                        <p className="text-green-600 font-bold">{scannerResult}</p>
                                    ) : (
                                        <p>Scanner</p>
                                    )}
                                    <BarcodeScannerComponent
                                    onScan={(data)=> setScannerResult(data)}
                                    onError={(err)=> console.error(err)}
                                    />
                                </div>

                                <label className="block text-sm font-medium">Product</label>
                                <Input placeholder="Product"/>

                                <label className="block text-sm font-medium">Description</label>
                                <Input placeholder="Description"/> 

                                <label className="block text-sm font-medium">Type</label>
                                <Input value="Entry"disabled/>

                                <label className="block text-sm font-medium">Origin</label>
                                <Input value={origin}disabled/>

                                <label className="block text-sm font-medium">Destination</label>
                                <Input
                                placeholder="Destination"
                                value={destination}
                                onChange={(e)=> setDestination(e.target.value)}
                                />

                                <div className="flex justify-between">
                                    <Button className="bg-blue-600 hover:bg-blue-700 text-white">Save</Button>
                                    <Button className="bg-gray-400 hover:bg-gray-500"onClick={()=> 
                                    setModalOpen(false)}>
                                        Cancel
                                    </Button>
                                </div>
                            </div>
                        </DialogContent>
                    </Dialog>
                </div>
            </div>

            <div className="p-6 bg-white shadow-md rounded-md overflow-x-auto dark:bg-gray-800">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>
                                <input type="checkbox"/>
                            </TableHead>
                            <TableHead>Date</TableHead>
                            <TableHead>Product</TableHead>
                            <TableHead>Quantity</TableHead>
                            <TableHead>Type</TableHead>
                            <TableHead>Origin</TableHead>
                            <TableHead>Destination</TableHead>
                            <TableHead>Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {movements.length > 0 ? (
                            movements.filter((m)=> m.product.toLowerCase().includes(search.toLowerCase()))
                            .slice(0, rowsPerPage)
                            .map((movement)=>(
                                <TableRow key={movement.id}>
                                    <TableCell>
                                        <input type="checkbox"/>
                                    </TableCell>
                                    <TableCell>{movement.date}</TableCell>
                                    <TableCell>{movement.product}</TableCell>
                                    <TableCell>{movement.quantity}</TableCell>
                                <TableCell>
                                    <span className={`px-2 py-1 rounded ${movement.type === "Entry" ? "bg-green-500 text-white" : "bg-red-500 text-white"}`}>
                                        {movement.type}
                                    </span>
                                </TableCell>
                                <TableCell>{movement.origin}</TableCell>
                                <TableCell>{movement.destination}</TableCell>
                                <TableCell>
                                    <Button variant="destructive">Delete</Button>
                                </TableCell>
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell colSpan={8}className="text-center p-4">Not Moviment</TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </div>

            <div className="flex justify-end items-center mt-4">
                <span className="mr-2 text-sm">Rows per page:</span>
                <select
                className="border rounded-md p-1 text-sm"
                value={rowsPerPage}
                onChange={(e)=> setRowsPerPage(Number(e.target.value))}
            >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={15}>15</option>
                <option value={25}>25</option>
            </select>
            </div>
        </div>
    )
}