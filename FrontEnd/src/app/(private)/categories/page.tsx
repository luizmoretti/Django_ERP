"use client";
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Table, TableHeader,TableHead,TableRow,TableBody,TableCell } from "@/components/ui/table";
import { Checkbox } from "@/components/ui/checkbox";
import { Plus, X } from "lucide-react";
import {useSidebar} from "@/components/sidebar/sidebarcontext"
import { Dialog,DialogTrigger,DialogContent,DialogHeader,DialogTitle,DialogFooter } from "@/components/ui/dialog";

export default function CategoriesTable(){
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
    

    return(
        <main className={`p-4 transition-margin duration-300 ease-in-out ${isSidebarVisible ? "ml-64" : "ml-0"}`} style={{marginTop: "3.5rem"}}>
        <div className="border rounded-lg p-4 space-y-4">
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
                                <TableHead>Description</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {paginatedCategories.map((category, index)=>(
                                <TableRow key={index} className="border-b hover:bg-gray-50">
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
                                    <TableCell className="text-gray-600">{category.name}</TableCell>
                                    <TableCell className="text-gray-600">{category.description}</TableCell>
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
                            {currentPage}-{Math.min(currentPage * itemsPerPage,filteredCategories.length)} of {filteredCategories.length}
                        </span>
                </div>
        </div>
    </main>
    )
}