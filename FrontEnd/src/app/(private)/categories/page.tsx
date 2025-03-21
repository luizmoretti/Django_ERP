"use client";
import { useState, useContext,useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Table, TableHeader,TableHead,TableRow,TableBody,TableCell } from "@/components/ui/table";
import { Checkbox } from "@/components/ui/checkbox";
import { Plus,MoreVertical,Edit,Trash } from "lucide-react";
import { DropdownMenu,DropdownMenuContent,DropdownMenuItem,DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import {useSidebar} from "@/components/sidebar/sidebarcontext"
import { Dialog,DialogTrigger,DialogContent,DialogHeader,DialogTitle,DialogFooter } from "@/components/ui/dialog";
import { useRouter } from "next/navigation";
import {AuthContext} from "@/context/authcontext";
import { useUser } from "@/context/userContext";
import Cookies from "js-cookie";

export default function CategoriesTable(){
    const {user}= useUser();
    const auth = useContext(AuthContext);
    const router = useRouter();
    const [editCategorie, setIsEditCategorie]= useState<{name:string;description:string}|null>(null);
    const [isEditOpen, setIsEditOpen]= useState(false);
    const { isSidebarVisible } = useSidebar();
    const[search,setSearch] = useState("");
    const[selectedRows,setSelectedRows] = useState<{ [key: number]: boolean }>({});
    const [allSelected, setAllSelected]= useState(false);
    const[itemsPerPage,setItemsPerPage] = useState(5);
    const[currentPage,setCurrentPage] = useState(1);
    const[open,setOpen]= useState(false);
    const[newCategory,setNewCategory] = useState<{ name: string; description: string }>({ name: "", description: "" });
    const[sortConfig,setSortConfig] = useState<{ key: keyof typeof categories[0]; direction: "asc" | "desc" | null }>({ key: "name", direction: null });

    const categories: { name: string; description: string }[] = [
        {name: "Cement Board", description:""},
        {name: "Corner Bead", description:""},
        {name: "Drywall Sheet", description:""},
        {name: "Mesh Tape", description:""},
        {name: "Roof Paper", description:""},
        {name: "Screws", description:""},
        {name: "Utilities", description:""},
        {name: "Veneer Plaster", description:""},
    ];
    const filteredCategories = categories.filter((category)=>
        category.name.toLowerCase().includes(search.toLowerCase())
    );

    const sortedCategories = [...filteredCategories].sort((a,b)=>{
        if(!sortConfig.key) return 0;
        const order = sortConfig.direction === "asc" ? 1 : -1;
        return a[sortConfig.key].localeCompare(b[sortConfig.key]) * order;
    });
    
    const totalPages = Math.ceil(filteredCategories.length / itemsPerPage);
    const paginatedCategories = filteredCategories.slice(
        (currentPage - 1) * itemsPerPage,
        currentPage * itemsPerPage
    );

    const toggleAllCheckboxes = ()=>{
            const newSelectedRows = allSelected ? {} : Object.fromEntries(paginatedCategories.map((_,index)=>[index,true]));
            setSelectedRows(newSelectedRows);
            setAllSelected(!allSelected);
        };

        const handleEdit = (categorie:{name:string;description:string})=>{
            setIsEditCategorie(categorie);
            setIsEditOpen(true);
        }

        const handleDelete = (categorie:{name:string;description:string})=>{
            const confirmDelete = window.confirm(`Are you sure you want to delete ${categorie.name}`);
            if(confirmDelete){
                console.log("Deleting:", categorie);
            }
        }
        
        useEffect(()=>{
            const acessToken= Cookies.get('acess_token');
            if(!acessToken){
                router.push("/signin")
            }
        },[user,auth,router])
    

    return(
        <main className={`p-4 transition-margin duration-300 ease-in-out ${isSidebarVisible ? "ml-64" : "ml-0"}`} style={{marginTop: "3.5rem"}}>
        <div className="border rounded-lg p-4 space-y-4 dark:bg-gray-900">
            <div className="flex justify-between items-center">
                <h2 className="font-semibold text-lg">Categories</h2>
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
                                <DialogTitle>New Category</DialogTitle>
                            </DialogHeader>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Name</label>
                                    <Input
                                        placeholder="Name"
                                        value={newCategory.name}
                                        onChange={(e)=> setNewCategory((prev)=>({...prev,name:e.target.value}))}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Description</label>
                                    <Input
                                        placeholder="Description"
                                        value={newCategory.description}
                                        onChange={(e)=> setNewCategory((prev)=>({...prev,description:e.target.value}))}
                                    />
                                </div>
                            </div>
                            <DialogFooter className="flex justify-end gap-2">
                                <Button variant="outline" onClick={()=> setOpen(false)}>Cancel</Button>
                                <Button className="bg-blue-600" onClick={()=>{
                                    console.log("Saving:",newCategory);
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
                    <Table className="w-full border border-gray-200 dark:border-gray-700">
                        <TableHeader className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 border-b">
                            <TableRow>
                                <TableHead className="w-12 px-4 border-gray-300 dark:border-gray-600">
                                    <Checkbox checked={allSelected} onCheckedChange={toggleAllCheckboxes}
                                    className="data-[state=checked]:bg-blue-600
                                    data-[state=checked]:border-blue-600 dark:border-gray-600"
                                    />
                                </TableHead>
                                <TableHead className=" border-gray-300 dark:border-gray-600 flex items-center gap-1">
                                    Name
                                </TableHead>
                                <TableHead className=" border-gray-300 dark:border-gray-600">Description</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {paginatedCategories.map((category, index)=>(
                                <TableRow key={index} className="dark:bg-gray-900 text-gray-900 border-b hover:bg-gray-50">
                                    <TableCell>
                                        <Checkbox
                                        checked={!!selectedRows[index]}
                                        onCheckedChange={()=>
                                            setSelectedRows((prev)=> ({
                                                ...prev,
                                                [index]: !prev[index]
                                            }))
                                        }
                                        className="data-[state=checked]:bg-blue-600
                                        data-[state=checked]:border-blue-600"
                                        />
                                    </TableCell>
                                    <TableCell className="text-gray-600 dark:text-gray-300">{category.name}</TableCell>
                                    <TableCell className="text-gray-600 dark:text-gray-300">{category.description}</TableCell>
                                    <TableCell className="text-right dark:text-gray-300">
                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <button className="p-2 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700">
                                                    <MoreVertical className="w-5 h-5"/>
                                                </button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="end"className="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-700">
                                                <DropdownMenuItem onClick={()=> handleEdit(category)}>
                                                    <Edit className="w-4 h-4 mr-2" />
                                                    Edit
                                                </DropdownMenuItem>
                                                <DropdownMenuItem onClick={()=> handleDelete(category)}>
                                                    <Trash className="w-4 h-4 mr-2 text-red-600" />
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
                                <DialogTitle>Edit Categorie</DialogTitle>
                            </DialogHeader>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Name</label>
                                    <Input
                                    placeholder="Name"
                                    value={editCategorie?.name ||""}
                                    onChange={(e)=> setIsEditCategorie((prev)=>(prev ?{...prev,name:e.target.value}:prev))
                                }
                                />  
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Description</label>
                                    <Input
                                    placeholder="Description"
                                    value={editCategorie?.description || ""}
                                    onChange={(e)=> setIsEditCategorie((prev)=>(prev ?{...prev,description:e.target.value}: prev))
                                }
                                />
                                </div>
                            </div>
                            <DialogFooter className="flex justify-end gap-2">
                                <Button variant="outline"onClick={()=> setIsEditOpen(false)}>Cancel</Button>
                                <Button
                                className="bg-blue-600"
                                onClick={()=>{
                                    console.log("Updating:",editCategorie);
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
                        className="border rounded-md px-2 py-1 ml-2 dark:bg-gray-900 "
                        value={itemsPerPage}
                        onChange={(e)=> setItemsPerPage(Number(e.target.value))}
                    >
                        <option value={5}>5</option>
                        <option value={10}>10</option>
                        <option value={15}>15</option>
                        </select> 
                        <span className="ml-4 text-sm text-gray-600">
                            {currentPage}-{Math.min(currentPage * itemsPerPage,filteredCategories.length)} of {filteredCategories.length}
                        </span>
                </div>
        </div>
    </main>
    )
}