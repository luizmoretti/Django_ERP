"use client"
import { useContext, useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import {Button} from "@/components/ui/button";
import {Table, TableHeader, TableHead, TableBody, TableRow, TableCell, TableFooter} from "@/components/ui/table";
import { Checkbox } from "@/components/ui/checkbox";
import { Plus } from "lucide-react";
import { useSidebar } from "@/components/sidebar/sidebarcontext";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogFooter} from "@/components/ui/dialog";
import { useRouter } from "next/navigation";
import { AuthContext } from "@/context/authcontext";

export default function Stores(){
    const auth = useContext(AuthContext);
    const router = useRouter();
    const {isSidebarVisible} = useSidebar();
    const [search, setSearch] = useState("");
    const [selectedRows, setSelectedRows] = useState<{[key: number]: boolean}>({});
    const [allSelected, setAllSelected] = useState(false);
    const [itemsPerPage, setItemsPerPage] = useState(5);
    const [currentPage, setCurrentPage] = useState(1);
    const [open, setOpen] = useState(false);
    const [newStore, setNewStore] = useState<{name: string;}>({name: ""});
    const [sortConfig, setSortConfig] = useState<{key: keyof typeof stores[0]; direction: "asc"| "desc"| null}>({key: "name", direction: null});

    const stores: {name: string;}[]=[
        {name: "HomeDepot- WTH"},
        {name: "Pátio"},
        {name: "Loja 1"},
        {name: "Loja 2"},
        {name: "Loja 3"},
        {name: "Loja 4"},
        {name: "Loja 5"},
    ];
    const filteredStores = stores.filter((stores)=>
        stores.name.toLowerCase().includes(search.toLowerCase())
    );

    const sortedStores = [...filteredStores].sort((a,b)=>{
        if(!sortConfig.key) return 0;
        const order = sortConfig.direction === "asc" ? 1 : -1;
        return a[sortConfig.key].localeCompare(b[sortConfig.key]) * order;
    });

    const totalPages = Math.ceil(filteredStores.length / itemsPerPage);
    const paginatedStores = filteredStores.slice(
        (currentPage - 1) * itemsPerPage,
        currentPage * itemsPerPage
    );

    const toggleAllCheckboxes = ()=>{
        const newSelectedRows = allSelected ? {} : Object.fromEntries(paginatedStores.map((_, index)=>[index, true]));
        setSelectedRows(newSelectedRows);
        setAllSelected(!allSelected);
    };

    useEffect(()=>{
        if (!auth?.user){
            router.push("/signin");
          }
      
    },[auth,router]);



    return(
        <main className={`p-6 transition-margin duration-300 ease-in-out ${isSidebarVisible ? "ml-64" : "ml-0"}`} style={{marginTop: "3.5rem"}}>
            <div className="border rounded-lg p-4 space-y-4">
                <div className="flex justify-between items-center">
                    <h2 className="font-semibold text-lg">Stores</h2>
                    <div className="flex items-center gap-3">
                        <Input
                            placeholder="Search..."
                            className="w-64 border rounded-md"
                            value={search}
                            onChange={(e)=> setSearch(e.target.value)}
                        />
                        <Dialog open={open} onOpenChange={setOpen}>
                            <DialogTrigger asChild>
                                <Button className="bg-blue-600 flex items-center gap-2">
                                    <Plus className="w-4 h-4"/>
                                    Add
                                </Button>
                            </DialogTrigger>
                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>New Store</DialogTitle>
                                </DialogHeader>
                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Name</label>
                                        <Input
                                            placeholder="Name"
                                            value={newStore.name}
                                            onChange={(e)=> setNewStore((prev)=>({...prev,name:e.target.value}))}
                                        />    
                                    </div>
                                </div>
                                <DialogFooter className="flex justify-end gap-2">
                                    <Button variant="outline" onClick={()=> setOpen(false)}>Cancel</Button>
                                    <Button className="bg-blue-600" onClick={()=>{
                                        console.log("Saving:", newStore);
                                        setOpen(false);
                                    }}>
                                        Save
                                    </Button>
                                </DialogFooter>
                            </DialogContent>
                        </Dialog>   
                    </div>
                </div>

                <div className="border rounded-lg overflow-hidden bg-white">
                    <Table className="w-full">
                        <TableHeader className="bg-gray-100 border-b">
                            <TableRow>
                                <TableHead className="w-12 px-4">
                                    <Checkbox checked={allSelected} onCheckedChange={toggleAllCheckboxes}
                                        className="data-[state=checked]:bg-blue-600
                                        data-[state=checked]:border-blue-600"
                                    />
                                </TableHead>
                                <TableHead className="cursor-pointer flex items-center gap-1">
                                    Name
                                </TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {paginatedStores.map((stores, index)=>(
                                <TableRow key={index} className="border-b hover:bg-gray-50">
                                    <TableCell>
                                        <Checkbox
                                        checked={!!selectedRows[index]}
                                        onCheckedChange={()=>
                                            setSelectedRows((prev)=>({
                                                ...prev,
                                                [index]: !prev[index]
                                            }))
                                        }
                                        className="data-[state=checked]:bg-blue-600
                                        data-[state=checked]:border-blue-600"
                                        />
                                    </TableCell>
                                    <TableCell className="text-gray-600">{stores.name}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </div>
                <div className="flex justify-end items-center p-4 bg-white">
                    <span className="text-sm text-gray-600">Rows per page:</span>
                    <select
                        className="border rounded-md px-2 py-1 ml-2"
                        value={itemsPerPage}
                        onChange={(e)=> setItemsPerPage(Number(e.target.value))}
                    >
                        <option value={5}>5</option>
                        <option value={10}>10</option>
                        <option value={15}>15</option>
                    </select>
                    <span className="ml-4 text-sm text-gray-600">
                        {currentPage}-{Math.min(currentPage * itemsPerPage, filteredStores.length)} of {filteredStores.length}
                    </span>
                </div>
            </div>
        </main>
    )
}