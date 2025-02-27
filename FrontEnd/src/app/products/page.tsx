import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, PlusCircle } from "lucide-react";
import { Table, TableBody, TableHead, TableHeader,TableCell,TableRow,TableFooter } from "@/components/ui/table";
import { Dialog, DialogTrigger,DialogContent,DialogDescription,DialogTitle,DialogHeader,DialogFooter,DialogClose } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";

export default function Products(){
    return(
        <div className="p-6 max-w-4xl mx-auto mt-20 space-y-2">
            <h1 className="text-3xl font-bold">Products</h1>
            <div className="flex items-center justify-between">
                <form className="flex items-center gap-2">
                    <Input name="id" placeholder="Id do produto"/>
                    <Input name="name" placeholder="nome do prod"/>
                    <Button type="submit" variant="link">
                        <Search className="w-4 h-4 mr-2" />
                        Filter 
                    </Button>
                </form>

                <Dialog>
                    <DialogTrigger asChild>
                        <Button>
                            <PlusCircle className="w-4 h-4 mr-2" />
                            Add
                        </Button>
                    </DialogTrigger>

                    <DialogContent>
                        <DialogHeader>
                        <DialogTitle>New Product</DialogTitle>
                        <DialogDescription>Create New Product</DialogDescription>
                        </DialogHeader>

                        <form className="space-y-6">
                            <div className="grid grid-cols-4 items-center text-right gap-3">
                                <Label htmlFor="name">Product</Label>
                                <Input className="col-span-3" id="name"/>
                            </div>
                        </form>

                        <DialogFooter>
                            <DialogClose asChild>
                                <Button type="button" variant="outline">Cancel</Button>
                                <Button type="button" variant="link">Salve</Button>
                            </DialogClose>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>

            <div className="border rounded-lg p-2">
                <Table>
                    <TableHeader>
                  <TableHead>Name</TableHead>
                  <TableHead>Brand</TableHead>
                  <TableHead>Quantity</TableHead>  
                  </TableHeader>
                  <TableBody>
                    {Array.from({length: 10}).map((_, i)=>{
                        return(
                            <TableRow key={i}>
                                <TableCell>1 5/8 screws</TableCell>
                                <DialogDescription>Screws</DialogDescription>
                                <TableCell>Utilities</TableCell>
                                <TableCell>22</TableCell>
                            </TableRow>
                        )
                    })}
                  </TableBody>
                </Table>

            </div>


        </div>
    )
}