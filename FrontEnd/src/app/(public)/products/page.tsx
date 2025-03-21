"use client"
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { Dialog, DialogClose, DialogFooter, DialogHeader, DialogTitle, DialogTrigger, DialogContent } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PlusCircle, Search, ArrowUp, ArrowDown, Edit, Trash, MoreVertical } from "lucide-react";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { useSidebar } from "@/components/sidebar/sidebarcontext";
import { useContext, useEffect } from "react";
import { AuthContext } from "@/context/authcontext";
import { useRouter } from "next/navigation";

// Define the products array
const products = [
    { name: '1 5/8 screws', description: "", brand: 'Utilities', quantity: 22, category: "Screws" },
    { name: ' 1/2 4x2 Drywall', description: "", brand: 'USG Sheetrock Brand', quantity: 28, category: "Drywall Sheet" },
    { name: "2\"Screws 25lbs", description: "", brand: 'Utilities', quantity: 48, category: "Screws" },
    { name: "3/8 4x8 Blueboard", description: "", brand: 'Imperial Brand', quantity: 22, category: "Drywall Sheet" },
    { name: "5/8 4x12 Blueboard", description: "", brand: 'USG Sheetrock Brand', quantity: 2606, category: "Drywall Sheet" },
    { name: "6 x 1-1/4in Screws", description: "", brand: 'Smart Tools', quantity: 188, category: "Screws" },
    { name: "Basecoat", description: "", brand: 'Imperial Brand', quantity: 4, category: "Veneer Plaster" },
    { name: "Corner Bead 10ft", description: "", brand: 'Smart Tools', quantity: 1620, category: "Corner Bead" },
    { name: "Corner Bead 8ft", description: "", brand: 'Smart Tools', quantity: 2640, category: "Corner Bead" },
    { name: "Corner Bead 9ft", description: "", brand: 'Smart Tools', quantity: 1587, category: "Corner Bead" },
    { name: "Diamond", description: "", brand: 'USG Veneer Plaster', quantity: 262, category: "Veneer Plaster" },
    { name: "Durock 3x5", description: "", brand: 'USG Sheetrock Brand', quantity: 152, category: "Cement Board" },
    { name: "Durock 3x5 -3/8", description: "", brand: 'USG Sheetrock Brand', quantity: 7, category: "Cement Board" },
    { name: "Mesh Tape", description: "", brand: 'Smart Tools', quantity: 1691, category: "Mesh Tape" },
    { name: "Roof Paper Black", description: "", brand: 'Orgill Roofing Felt', quantity: 159, category: "Roof Paper" },
    { name: "Roof Paper White", description: "", brand: 'Utilities', quantity: 157, category: "Roof Paper" },
    { name: "Uni-Kal", description: "", brand: 'Gold Bond', quantity: 775, category: "Veneer Plaster" },
    { name: "X-KALibur", description: "", brand: 'Gold Bond', quantity: 88, category: "Veneer Plaster" },
    { name: "1/2 4x12 Blueboard", description: "", brand: 'USG Sheetrock Brand', quantity: 16239, category: "Drywall Sheet" },
    { name: "1/2 4x8 Blueboard", description: "", brand: 'USG Sheetrock Brand', quantity: 573, category: "Drywall Sheet" },
    { name: "1/2 54 x 12 Blueboard", description: "", brand: 'Gold Bond', quantity: 16, category: "Drywall Sheet" }

];

export default function Products() {
    const auth = useContext(AuthContext);
    const router = useRouter();
    const [editProduct, setIsEditProduct] = useState<{ name: string; description: string; brand: string; quantity: number; category: string } | null>(null);
    const [isEditOpen, setIsEditOpen] = useState(false);
    // Define the state variables
    const [itemsPerPage, setitemsPerPage] = useState(10);
    // Define the visible products

    // Define the sortConfig state variable
    const [sortConfig, setSortConfig] = useState<{ key: keyof typeof products[0]; order: | "asc" | "desc" } | null>(null);

    // Get sidebar visibility state
    const { isSidebarVisible } = useSidebar();

    // Function to handle sorting
    const handleSort = (key: keyof typeof products[0]) => {
        setSortConfig((prev) => {
            if (!prev || prev.key !== key) {
                return { key, order: prev && prev.order === 'asc' ? 'desc' : 'asc' };

            }
            return { key, order: 'asc' };
        });
    };

    // Sort the products based on the sort Configuration
    const visibleProducts = [...products].sort((a, b) => {
        if (!sortConfig) return 0;
        const key = sortConfig.key as keyof typeof a;
        const order = sortConfig.order === 'asc' ? 1 : -1;
        return String(a[key]).localeCompare(String(b[key])) * order;
    }).slice(0, itemsPerPage);

    //Function to toggle sorting
    const toggleSort = (key: string) => {
        setSortConfig(prev => {
            if (!prev || prev.key !== key) {
                return { key: key as "name" | "brand" | "quantity" | "category", order: 'asc' };
            }
            return { key: key as "name" | "brand" | "quantity" | "category", order: prev.order === 'asc' ? 'desc' : 'asc' };
        });
    };

    //State to manage selected products
    const [selectedProducts, setSelectedProducts] = useState<boolean[]>(Array(visibleProducts.length).fill(false));
    //State to manage selectAll checkbox
    const [selectAll, setSelectAll] = useState(false);
    //Function to handle selectAll checkbox
    const handleselectAll = () => {
        const newSelectAll = !selectAll;
        setSelectAll(newSelectAll);
        setSelectedProducts(Array(visibleProducts.length).fill(newSelectAll));
    };

    //Function to handle individual checkbox change
    const handleCheckboxChange = (index: number) => {
        const updatedSelection = [...selectedProducts];
        updatedSelection[index] = !updatedSelection[index];

        const allSelected = updatedSelection.every((isSelected) => isSelected);
        setSelectAll(allSelected);

        setSelectedProducts(updatedSelection);
    };

    const handleEdit = (products: { name: string; description: string; brand: string; quantity: number; category: string }) => {
        setIsEditProduct(products);
        setIsEditOpen(true);
    }

    const handleDelete = (products: { name: string; description: string; brand: string; quantity: number; category: string }) => {
        const confirmDelete = window.confirm(`Are you sure you want to delete ${products.name}`);
        if (confirmDelete) {
            console.log("Deleting:", products);
        }
    }

   /* useEffect(() => {
        if (!auth?.user) {
            router.push("/signin");
        }

    }, [auth, router]);*/
    /** Este hook useEffect verifica se o usuário está autenticado antes de permitir o acesso à página.
     - Se o objeto `auth` não existir ou não contiver a propriedade `user`, o usuário será redirecionado para a página de login ("/signin").
     - O operador de encadeamento opcional (`?.`) é usado para evitar erros caso `auth` seja `null` ou `undefined`.
     - O método `router.push` é usado para realizar a navegação programática para a página de login.
     - O array de dependências `[auth, router]` garante que o efeito será executado apenas quando `auth` ou `router` mudarem.
     Este código implementa uma proteção de rota, garantindo que apenas usuários autenticados possam acessar a página.*/

    return (
        <main className={`p-4 transition-margin duration-300 ease-in-out ${isSidebarVisible ? "ml-64" : "ml-0"}`} style={{ marginTop: "3.5rem" }}>
            <div className="flex border rounded-lg p-4 mx-auto space-y-4">
                <div className="flex items-center justify-between">
                    <form className="flex items-center gap-2">
                    </form>
                </div>
                <div className="border rounded-lg shadow-md overflow-hidden p-4 bg-white dark:bg-gray-900 w-full">
                    <div className="overflow-x-auto">
                        <Table className="w-full border border-gray-200 dark:border-gray-700">
                            <TableHeader className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200">
                                <TableRow>
                                    <TableHead colSpan={4} className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 text-center text-2xl font-semibold py-4 select-none">
                                        Products
                                    </TableHead>
                                </TableRow>
                                <TableRow>
                                    <TableHead colSpan={4} className="py-3 border border-gray-300 dark:border-gray-600">
                                        <div className="flex items-center justify-between">
                                            <form className="flex items-center gap-3">
                                                <select id="brand" className="w-48 border border-gray-300 rounded-md p-2">
                                                    <option value="">Brands</option>
                                                    <option value="Gold">Gold Bond</option>
                                                    <option value="Imperial">Imperial Brand</option>
                                                    <option value="">Orgill Roofing Felt</option>
                                                    <option value="">Smart Tools</option>
                                                    <option value="USG">USG Sheetrock Brand</option>
                                                    <option value="USG">USG Veneer Plaster</option>
                                                    <option value="">Utilities</option>
                                                </select>
                                                <select id="category" className="w-48 border border-gray-300 rounded-md p-2">
                                                    <option value="">Categories</option>
                                                    <option value="">Cement Board</option>
                                                    <option value="">Corner Bead</option>
                                                    <option value="">Drywall Sheet</option>
                                                    <option value="">Mesh Tape</option>
                                                    <option value="">Roof Paper</option>
                                                    <option value="">Screws</option>
                                                    <option value="">Utilities</option>
                                                    <option value="">Veneer Plaster</option>
                                                </select>
                                                <div className="relative">
                                                    <Search className="absolute top-1/2 left-3 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                                                    <Input name="search" placeholder="Search" className="pl-10 pr-4 w-50 border rounded-md" />
                                                </div>
                                            </form>
                                            <Dialog>
                                                <DialogTrigger asChild>
                                                    <Button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-600 text-white rounded-md">
                                                        <PlusCircle className="w-4 h-4 mr-2" />
                                                        Add Product
                                                    </Button>
                                                </DialogTrigger>
                                                <DialogContent className="bg-white p-6 rounded-lg w-full max-w-lg shadow-xl">
                                                    <DialogHeader>
                                                        <DialogTitle className="text-xl font-semibold">New Product</DialogTitle>
                                                    </DialogHeader>
                                                    <form className="space-y-4">
                                                        <div className="space-y-2">
                                                            <Label htmlFor="name">Name</Label>
                                                            <Input id="name" placeholder="Name" />
                                                        </div>
                                                        <div className="space-y-2">
                                                            <Label htmlFor="description">Description</Label>
                                                            <Input id="description" placeholder="Description" />
                                                        </div>
                                                        <div className="space-y-2">
                                                            <Label htmlFor="quantity">Quantity</Label>
                                                            <Input id="quantity" placeholder="0" disabled className="opacity-50 cursor-not-allowed" />
                                                        </div>
                                                        <div className="space-y-2">
                                                            <Label htmlFor="category">Category</Label>
                                                            <select id="category" className="w-full border border-gray-300 rounded-md p-2">
                                                                <option value="">Select a category</option>
                                                                <option value="">Cement Board</option>
                                                                <option value="">Corner Bead</option>
                                                                <option value="">Drywall Sheet</option>
                                                                <option value="">Mesh Tape</option>
                                                                <option value="">Roof Paper</option>
                                                                <option value="">Screws</option>
                                                                <option value="">Utilities</option>
                                                                <option value="">Veneer Plaster</option>
                                                            </select>
                                                        </div>
                                                        <div className="space-y-2">
                                                            <Label htmlFor="brand">Brand</Label>
                                                            <select id="brand" className="w-full border border-gray-300 rounded-md p-2">
                                                                <option value="">Select a brand</option>
                                                                <option value="Gold">Gold Bond</option>
                                                                <option value="Imperial">Imperial Brand</option>
                                                                <option value="">Orgill Roofing Felt</option>
                                                                <option value="">Smart Tools</option>
                                                                <option value="USG">USG Sheetrock Brand</option>
                                                                <option value="USG">USG Veneer Plaster</option>
                                                                <option value="">Utilities</option>
                                                            </select>
                                                        </div>
                                                        <div className="space-y-2">
                                                            <Label htmlFor="supplier">Supplier</Label>
                                                            <select id="supplier" className="w-full border border-gray-300 rounded-md p-2">
                                                                <option value="">Select a supplier</option>
                                                                <option value="supplier1">Dana WallBoard</option>
                                                                <option value="supplier2">Home Depot</option>
                                                                <option value="supplier3">Smart Tools</option>
                                                            </select>
                                                        </div>
                                                        <DialogFooter className="mt-6 flex justify-end gap-2">
                                                            <DialogClose asChild>
                                                                <Button type="button" variant="outline" className="rounded-md border">Cancel</Button>
                                                            </DialogClose>
                                                            <Button type="submit" className="bg-blue-600 text-white rounded-md">Save</Button>
                                                        </DialogFooter>
                                                    </form>
                                                </DialogContent>
                                            </Dialog>
                                        </div>
                                    </TableHead>
                                </TableRow>

                                <TableRow className="bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 whitespace-nowrap justify-between">
                                    <TableHead className="w-10">
                                        <Checkbox checked={selectAll} onCheckedChange={handleselectAll}
                                            className="data-[state=checked]:bg-blue-600
                                 data-[state=checked]:border-blue-600"
                                        />
                                    </TableHead>
                                    <TableHead
                                        className="cursor-pointer px-4 py-3 uppercase font-medium flex items-center gap-1"
                                        onClick={() => handleSort("name")}
                                    >
                                        Name
                                        {sortConfig?.key === "name" && (sortConfig?.order === "asc" ? <ArrowUp className="w-4 h-4" size={16} />
                                            : <ArrowDown className="w-4 h-4" size={16} />)}
                                    </TableHead>
                                    <TableHead
                                        className="cursor-pointer px-4 py-3 uppercase font-medium items-center gap-2"
                                        onClick={() => handleSort("brand")}
                                    >
                                        Brand
                                        {sortConfig?.key === "brand" && (sortConfig.order === "asc" ? <ArrowUp className="w-4 h-4" />
                                            : <ArrowDown className="w-4 h-4" />)}
                                    </TableHead>
                                    <TableHead className="text-right px-4 py-3 uppercase font-medium">Quantity</TableHead>
                                </TableRow>
                            </TableHeader>

                            <TableBody>
                                {visibleProducts.map((product, index) => (
                                    <TableRow key={index} className="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 border-b hover:bg-gray-100 dark:hover:bg-gray-700">
                                        <TableCell>
                                            <Checkbox
                                                checked={selectedProducts[index]}
                                                onCheckedChange={() => handleCheckboxChange(index)}
                                                className="data-[state=checked]:bg-blue-600
                                        data-[state=checked]:border-blue-600"
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <div className="font-medium dark:text-gray-300">{product.name}</div>
                                            <div className="text-sm text-gray-600 dark:text-gray-300">{product.category}</div>
                                        </TableCell>
                                        <TableCell className="text-gray-600 dark:text-gray-300">{product.brand}</TableCell>
                                        <TableCell className="text-right dark:text-gray-300">{product.quantity}</TableCell>
                                        <TableCell className="text-right dark:text-gray-300">
                                            <DropdownMenu>
                                                <DropdownMenuTrigger asChild>
                                                    <button className="p-2 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700">
                                                        <MoreVertical className="w-5 h-5" />
                                                    </button>
                                                </DropdownMenuTrigger>
                                                <DropdownMenuContent align="end" className="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-700">
                                                    <DropdownMenuItem onClick={() => handleEdit(product)}>
                                                        <Edit className="w-4 h-4 mr-2" />
                                                        Edit
                                                    </DropdownMenuItem>
                                                    <DropdownMenuItem onClick={() => handleDelete(product)}>
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
                        <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>Edit Product</DialogTitle>
                                </DialogHeader>
                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Name</label>
                                        <Input
                                            placeholder="Name"
                                            value={editProduct?.name}
                                            onChange={(e) => setIsEditProduct((prev) => (prev ? { ...prev, name: e.target.value } : prev))
                                            }
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Description</label>
                                        <Input
                                            placeholder="Description"
                                            value={editProduct?.description}
                                            onChange={(e) => setIsEditProduct((prev) => (prev ? { ...prev, description: e.target.value } : prev))
                                            }
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Quantity</label>
                                        <Input
                                            placeholder="22"
                                            value={editProduct?.quantity}
                                            disabled className="opacity-50 cursor-not-allowed" />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Category</label>
                                        <select id="category" className="w-full border border-gray-300 rounded-md p-2">
                                            <option value="">Select a category</option>
                                            <option value="">Cement Board</option>
                                            <option value="">Corner Bead</option>
                                            <option value="">Drywall Sheet</option>
                                            <option value="">Mesh Tape</option>
                                            <option value="">Roof Paper</option>
                                            <option value="">Screws</option>
                                            <option value="">Utilities</option>
                                            <option value="">Veneer Plaster</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Brand</label>
                                        <select id="brand" className="w-full border border-gray-300 rounded-md p-2">
                                            <option value="">Select a brand</option>
                                            <option value="Gold">Gold Bond</option>
                                            <option value="Imperial">Imperial Brand</option>
                                            <option value="">Orgill Roofing Felt</option>
                                            <option value="">Smart Tools</option>
                                            <option value="USG">USG Sheetrock Brand</option>
                                            <option value="USG">USG Veneer Plaster</option>
                                            <option value="">Utilities</option>
                                        </select>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700">Supplier</label>
                                            <select id="supplier" className="w-full border border-gray-300 rounded-md p-2">
                                                <option value="">Select a supplier</option>
                                                <option value="supplier1">Dana WallBoard</option>
                                                <option value="supplier2">Home Depot</option>
                                                <option value="supplier3">Smart Tools</option>
                                            </select>
                                        </div>
                                    </div>
                                    <DialogFooter className="flex justify-end gap-2">
                                        <Button variant="outline" onClick={()=> setIsEditOpen(false)}>Cancel</Button>
                                        <Button
                                            className="bg-blue-600"
                                            onClick={()=>{
                                                console.log("Updating:", editProduct)
                                                setIsEditOpen(false);
                                            }}
                                            >
                                                Save
                                            </Button>
                                    </DialogFooter>
                                </div>
                            </DialogContent>
                        </Dialog>
                        <div className="flex justify-end items-center p-4 bg-white text-gray-600 text-sm">
                            <span className="text-sm text-gray-600 ">Rows per page:</span>
                            <select
                                className="border rounded px-2 py-1 ml-2"
                                value={itemsPerPage}
                                onChange={(e) => setitemsPerPage(Number(e.target.value))}
                            >
                                <option value={5}>5</option>
                                <option value={10}>10</option>
                                <option value={15}>15</option>
                                <option value={25}>25</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}