"use client"
import { useContext, useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import {Button} from "@/components/ui/button";
import {Table, TableHeader, TableHead, TableBody, TableRow, TableCell, TableFooter} from "@/components/ui/table";
import { Checkbox } from "@/components/ui/checkbox";
import { Plus, MoreVertical, Edit, Trash } from "lucide-react";
import { DropdownMenu,DropdownMenuContent,DropdownMenuItem,DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { useSidebar } from "@/components/sidebar/sidebarcontext";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogFooter} from "@/components/ui/dialog";
import { useRouter } from "next/navigation";
import { AuthContext } from "@/context/authcontext";
import { useUser } from "@/context/userContext";
import Cookies from "js-cookie";


export default function Stores(){
    const {user} = useUser();
    const auth = useContext(AuthContext);
    const router = useRouter();
    const {isSidebarVisible} = useSidebar();
    const [editStore, setIsEditStore] = useState<{name: string}|null>(null);
    const [isEditOpen, setIsEditOpen] = useState(false);
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

    const handleEdit = (stores:{name: string})=>{
        setIsEditStore(stores);
        setIsEditOpen(true);
    }

    const handleDelete =(stores:{name: string})=>{
        const confirmDelete = window.confirm(`Are you sure you want to delete ${stores.name}`);
        if(confirmDelete){
            console.log("Deleting:", stores);
        }
    }

    useEffect(()=>{
        const acesstoken = Cookies.get('acess_token');
        if (!acesstoken){
            router.push("/signin");
          }
      
    },[user,auth,router]);



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

                <div className="border rounded-lg overflow-hidden bg-white dark:bg-gray-900">
                    <Table className="w-full dark:border-gray-700">
                        <TableHeader className="bg-gray-100 dark:bg-gray-800 text-gray-200 dark:border-gray-700 border-b">
                            <TableRow>
                                <TableHead className="w-12 px-4 dark:border-gray-600">
                                    <Checkbox checked={allSelected} onCheckedChange={toggleAllCheckboxes}
                                        className="data-[state=checked]:bg-blue-600
                                        data-[state=checked]:border-blue-600 dark:bg-gray-600"
                                    />
                                </TableHead>
                                <TableHead className="cursor-pointer flex items-center gap-1 dark:border-gray-600">
                                    Name
                                </TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {paginatedStores.map((stores, index)=>(
                                <TableRow key={index} className="bg-white dark:bg-gray-900 text-gray-900 border-b hover:bg-gray-50">
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
                                    <TableCell className="text-gray-600 dark:text-gray-300">{stores.name}</TableCell>
                                    <TableCell className="text-right dark:text-gray-300">
                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <button className="p-2 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700">
                                                    <MoreVertical className="w-5 h-5"/>
                                                </button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="end" className="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-700">
                                                <DropdownMenuItem onClick={()=> handleEdit(stores)}>
                                                    <Edit className="w-4 h-4 mr-2" />
                                                    Edit
                                                </DropdownMenuItem>
                                                <DropdownMenuItem onClick={()=> handleDelete(stores)}>
                                                    <Trash className="w-4 h-4 mr-2 text-red-600"/>
                                                    Delete
                                                </DropdownMenuItem>
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                    <Dialog open = {isEditOpen} onOpenChange={setIsEditOpen}>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Edit Store</DialogTitle>
                            </DialogHeader>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Name</label>
                                    <Input
                                    placeholder="Name"
                                    value={editStore?.name || ""}
                                    onChange={(e)=> setIsEditStore((prev)=> (prev ?{...prev,name:e.target.value}:prev))
                                }
                                />
                                </div>
                            </div>
                            <DialogFooter className="flex justify-end gap-2">
                                <Button variant="outline" onClick={()=> setIsEditOpen(false)}>Cancel</Button>
                                <Button
                                className="bg-blue-600"
                                onClick={()=>{
                                    console.log("Updating:", editStore);
                                    setIsEditOpen(false);
                                }}
                                >
                                    Save
                                </Button>
                            </DialogFooter>
                        </DialogContent>
                    </Dialog>
                </div>
                <div className="flex justify-end items-center p-4 bg-white dark:bg-gray-900">
                    <span className="text-sm text-gray-600">Rows per page:</span>
                    <select
                        className="border rounded-md px-2 py-1 ml-2 dark:bg-gray-900"
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