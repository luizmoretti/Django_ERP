"use client";

import { useState, useContext, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Table, TableHead, TableHeader, TableBody, TableRow, TableCell, TableFooter } from "@/components/ui/table";
import { Checkbox } from "@/components/ui/checkbox";
import { useSidebar } from "@/components/sidebar/sidebarcontext";
import { Plus, Edit, Trash, MoreVertical } from "lucide-react";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Dialog, DialogContent, DialogTrigger, DialogTitle, DialogHeader, DialogFooter } from "@/components/ui/dialog";
import { AuthContext } from "@/context/authcontext";
import { useRouter } from "next/navigation";

interface Supplier {
    id: number;
    name: string;
    address: string;
    city: string;
    state: string;
    zipCode: string;
    email: string;
    phone: string;
}

export default function Suppliers() {
    const auth = useContext(AuthContext);
    const router = useRouter();
    const [editSupplier, setIsEditSupplier] = useState<{ name: string, address: string, city: string, state: string, zipCode: string, email: string, phone: string } | null>(null);
    const [isEditOpen, setIsEditOpen] = useState(false);
    const { isSidebarVisible } = useSidebar();
    const [search, setSearch] = useState("");
    const [selectedRows, setSelectedRows] = useState<{ [key: number]: boolean }>(
        {}

    );
    const [allSelected, setAllSelected] = useState(false);
    const [itemsPerPage, setItemsPerPage] = useState(5);
    const [currentPage, setCurrentPage] = useState(1);
    const [open, setOpen] = useState(false);
    const [newSupplier, setNewSupplier] = useState<Supplier>({
        id: 0,
        name: "",
        address: "",
        city: "",
        state: "",
        zipCode: "",
        email: "",
        phone: "",
    });
    const suppliers: Supplier[] = [
        {
            id: 1,
            name: "Dana WallBoard",
            address: "123 Main St",
            city: "Los Angeles",
            state: "CA",
            zipCode: "90001",
            email: "contact@danawallboard.com",
            phone: "(123) 456-7890",
        },
        {
            id: 2,
            name: "Home Depot",
            address: "456 Market St",
            city: "New York",
            state: "NY",
            zipCode: "1001",
            email: "info@homedepot.com",
            phone: "(987) 654-3210",
        },
        {
            id: 3,
            name: "Smart Tools",
            address: "789 Industrial Rd",
            city: "Chicago",
            state: "IL",
            zipCode: "60007",
            email: "suport@smarttools.com",
            phone: "(555) 789-1234",
        },
        {
            id: 4,
            name: "WallBridge",
            address: "456 Brick Lane",
            city: "Houston",
            state: "TX",
            zipCode: "77002",
            email: "sale@wallbridge.com",
            phone: "(333) 222-1111",
        },
    ];
    const filteredSuppliers = suppliers.filter((store) =>
        store.name.toLowerCase().includes(search.toLowerCase()))

    const sortedSuppliers = [...filteredSuppliers].sort((a, b) =>
        a.name.localeCompare(b.name)
    );

    const totalPages = Math.ceil(filteredSuppliers.length / itemsPerPage);
    const paginatedSuppliers = sortedSuppliers.slice(
        (currentPage - 1) * itemsPerPage,
        currentPage * itemsPerPage
    );

    const toggleAllCheckboxes = () => {
        const newSelectedRows = allSelected ? {} : Object.fromEntries(paginatedSuppliers.map((s) => [s.id, true]));
        setSelectedRows(newSelectedRows);
        setAllSelected(!allSelected);
    };

    const handleEdit = (suppliers: { name: string; address: string; city: string; state: string; zipCode: string; email: string; phone: string }) => {
        setIsEditSupplier(suppliers);
        setIsEditOpen(true);
    }

    const handleDelete = (suppliers: { name: string; address: string; city: string; state: string; zipCode: string; email: string; phone: string }) => {
        const confirmDelete = window.confirm(`Are you sure you want to delete ${suppliers.name}`);
        if (confirmDelete) {
            console.log("Deleting:", suppliers);
        }
    }

    /* useEffect(()=>{
        if(!auth?.user){
            router.push("/signin")
        }
    },[auth,router]);*/

    return (
        <main className={`p-6 transition-margin duration-300 ease-in-out ${useSidebar().isSidebarVisible ? "ml-64" : "ml-0"}`}
            style={{ marginTop: "3.5rem" }}
        >
            <div className="border rounded-lg p-4 space-y-4">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="font-semibold text-lg">Suppliers</h2>
                    <div className="flex items-center gap-3">
                        <Input
                            placeholder="Search..."
                            className="w-64 border rounded-md"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                        <Dialog open={open} onOpenChange={setOpen}>
                            <DialogTrigger asChild>
                                <Button className="bg-blue-600 flex items-center gap-2">
                                    <Plus className="w-4 h-4" />
                                    Add
                                </Button>
                            </DialogTrigger>
                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>New Supplier</DialogTitle>
                                </DialogHeader>
                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Name</label>
                                        <Input
                                            placeholder="Name"
                                            value={newSupplier.name}
                                            onChange={(e) =>
                                                setNewSupplier({ ...newSupplier, name: e.target.value })
                                            }
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium
                                            text-gray-700">Address</label>
                                        <Input
                                            placeholder="Address"
                                            value={newSupplier.address}
                                            onChange={(e) =>
                                                setNewSupplier((prev) => ({
                                                    ...prev,
                                                    address: e.target.value,
                                                }))
                                            }
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">City</label>
                                        <Input
                                            placeholder="City"
                                            value={newSupplier.city}
                                            onChange={(e) => setNewSupplier({ ...newSupplier, city: e.target.value })}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">State</label>
                                        <Input
                                            placeholder="State"
                                            value={newSupplier.state}
                                            onChange={(e) => setNewSupplier({ ...newSupplier, state: e.target.value })}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Zip Code</label>
                                        <Input
                                            placeholder="Zip Code"
                                            value={newSupplier.zipCode}
                                            onChange={(e) => setNewSupplier({ ...newSupplier, zipCode: e.target.value })}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Email</label>
                                        <Input
                                            placeholder="Email"
                                            value={newSupplier.email}
                                            onChange={(e) => setNewSupplier({ ...newSupplier, email: e.target.value })}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Phone</label>
                                        <Input
                                            placeholder="Phone"
                                            value={newSupplier.phone}
                                            onChange={(e) => setNewSupplier({ ...newSupplier, phone: e.target.value })}
                                        />
                                    </div>
                                </div>
                                <DialogFooter>
                                    <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
                                    <Button className="bg-blue-600" onClick={() => setOpen(false)}>Save</Button>
                                </DialogFooter>
                            </DialogContent>
                        </Dialog>
                    </div>
                </div>
                <div className="overflow-x-auto">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>
                                    <Checkbox checked={allSelected} onCheckedChange={(checked) => {
                                        const isChecked = checked === true;
                                        setAllSelected(isChecked);
                                        if (isChecked) {
                                            const newSelectedRows = Object.fromEntries(
                                                suppliers.map((suppliers) => [suppliers.id, true])
                                            );
                                            setSelectedRows(newSelectedRows);
                                        } else {
                                            setSelectedRows({})
                                        }
                                    }}
                                        className="data-[state=checked]:bg-blue-600
                                        data-[state=checked]:border-blue-600"
                                    />
                                </TableHead>
                                <TableHead>Name</TableHead>
                                <TableHead>Address</TableHead>
                                <TableHead>City</TableHead>
                                <TableHead>State</TableHead>
                                <TableHead>Zip Code</TableHead>
                                <TableHead>Email</TableHead>
                                <TableHead>Phone</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {paginatedSuppliers.map((supplier) => (
                                <TableRow key={supplier.id}>
                                    <TableCell>
                                        <Checkbox
                                            checked={selectedRows[supplier.id] || false}
                                            onCheckedChange={(checked) => {
                                                setSelectedRows((prev) => ({
                                                    ...prev,
                                                    [supplier.id]: checked === true,
                                                }));
                                            }}
                                            className="data-[state=checked]:bg-blue-600
                                        data-[state=checked]:border-blue-600"
                                        />
                                    </TableCell>
                                    <TableCell>{supplier.name}</TableCell>
                                    <TableCell>{supplier.address}</TableCell>
                                    <TableCell>{supplier.city}</TableCell>
                                    <TableCell>{supplier.state}</TableCell>
                                    <TableCell>{supplier.zipCode}</TableCell>
                                    <TableCell>{supplier.email}</TableCell>
                                    <TableCell>{supplier.phone}</TableCell>
                                    <TableCell className="text-right">
                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <button className="p-2 rounded-md hover:bg-gray-200">
                                                    <MoreVertical className="w-5 h-5" />
                                                </button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="end">
                                                <DropdownMenuItem onClick={() => handleEdit(supplier)}>
                                                    <Edit className="w-4 h-4 mr-2" />
                                                    Edit
                                                </DropdownMenuItem>
                                                <DropdownMenuItem onClick={() => handleDelete(supplier)}>
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
                                <DialogTitle>Edit Supplier</DialogTitle>
                            </DialogHeader>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Name</label>
                                    <Input
                                        placeholder="Name"
                                        value={editSupplier?.name || ""}
                                        onChange={(e) => setIsEditSupplier((prev) => (prev ? { ...prev, name: e.target.value } : prev))
                                        }
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Address</label>
                                    <Input
                                        placeholder="Address"
                                        value={editSupplier?.address || ""}
                                        onChange={(e) => setIsEditSupplier((prev) => (prev ? { ...prev, address: e.target.value } : prev))
                                        }
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">City</label>
                                    <Input
                                        placeholder="City"
                                        value={editSupplier?.city || ""}
                                        onChange={(e) => setIsEditSupplier((prev) => (prev ? { ...prev, city: e.target.value } : prev))
                                        }
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">State</label>
                                    <Input
                                        placeholder="State"
                                        value={editSupplier?.state || ""}
                                        onChange={(e) => setIsEditSupplier((prev) => (prev ? { ...prev, state: e.target.value } : prev))
                                        }
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Zip Code</label>
                                    <Input
                                        placeholder="Zip Code"
                                        value={editSupplier?.zipCode || ""}
                                        onChange={(e) => setIsEditSupplier((prev) => (prev ? { ...prev, zipCode: e.target.value } : prev))
                                        }
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Email</label>
                                    <Input
                                        placeholder="Email"
                                        value={editSupplier?.email || ""}
                                        onChange={(e) => setIsEditSupplier((prev) => (prev ? { ...prev, email: e.target.value } : prev))
                                        }
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Phone</label>
                                    <Input
                                        placeholder="Phone"
                                        value={editSupplier?.phone || ""}
                                        onChange={(e) => setIsEditSupplier((prev) => (prev ? { ...prev, phone: e.target.value } : prev))
                                        }
                                    />
                                </div>
                            </div>
                            <DialogFooter className="flex justify-end gap-2">
                                <Button variant="outline" onClick={() => setIsEditOpen(false)}>Cancel</Button>
                                <Button
                                    className="bg-blue-600"
                                    onClick={() => {
                                        console.log("Updating:", editSupplier);
                                        setIsEditOpen(false);
                                    }}
                                >
                                    Save
                                </Button>
                            </DialogFooter>
                        </DialogContent>
                    </Dialog>
                </div>
                <div className="flex justify-end items-center p-4 bg-white">
                    <span className="text-sm text-gray-600">Rows per page:</span>
                    <select
                        className="border rounded-md px-2 py-1 ml-2"
                        value={itemsPerPage}
                        onChange={(e) => setItemsPerPage(Number(e.target.value))}
                    >
                        <option value={5}>5</option>
                        <option value={10}>10</option>
                        <option value={15}>15</option>
                    </select>
                    <span className="ml-4 text-sm text-gray-600">
                        {currentPage}-{Math.min(currentPage * itemsPerPage, filteredSuppliers.length)} of {filteredSuppliers.length}
                    </span>
                </div>
            </div>
        </main>
    )
};

