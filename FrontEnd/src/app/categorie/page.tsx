import { Button } from "@/components/ui/button";
import {Input} from "@/components/ui/input"
import {Search, PlusCircle} from "lucide-react"
import { Table, TableBody, TableHead, TableHeader, TableRow, TableCell } from "@/components/ui/table";
import { Dialog, DialogTrigger,DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";


export default function Categories(){
    return(
        <div className="p-6 max-w-4xl mx-auto mt-20 space-y-2">
           <h1 className="text-3xl font-bold">Categories</h1>
            <div className="flex items-center justify-between">
                <form className="flex items-center gap-2">
                    <Input name="id" placeholder="ID do Pedido" />
                    <Input name="name" placeholder="Nome do Produto"/>
                    <Button type="submit" variant="link">
                        <Search className="w-4 h-4 mr-2" />
                        Filtrar resultados
                    </Button>
                </form>

            <Dialog>
                <DialogTrigger asChild>
                    <Button>
                        <PlusCircle className="w-4 h-4 mr-2" />
                        Novo Produto
                    </Button>
                </DialogTrigger>

                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Novo Produto</DialogTitle>
                        <DialogDescription>Criar novo Produto</DialogDescription>
                    </DialogHeader>

                    <form className="space-y-6">
                        <div className="grid grid-cols-4 items-center text-right gap-3">
                            <Label htmlFor="name">Produto</Label>
                            <Input className="col-span-3" id="name" />

                        </div>

                        <form className="space-y-6">
                            <div className="grid grid-cols-4 items-center text-right gap-3">
                                <Label htmlFor="price">Preco</Label>
                                <Input className="col-span-3" id="price" />
                            </div>
                        </form>

                        <DialogFooter>
                            <DialogClose asChild>
                            <Button type="button" variant="outline">Cancelar</Button>
                            </DialogClose>
                            <Button type="button" variant="link">Salvar</Button>
                        </DialogFooter>
                    </form>
                </DialogContent>
                </Dialog>
            </div>


            <div className="border rounded-lg p-2">
                <Table >
                    <TableHeader>
                        <TableHead>ID</TableHead>
                        <TableHead>Produto</TableHead>
                        <TableHead>Preço</TableHead>
                    </TableHeader>
                    <TableBody>
                      {Array.from({length: 10}).map((_, i)=>{
                        return(
                            <TableRow key={i}>
                                <TableCell>kdklsnslknlskngsln</TableCell>
                                <TableCell>Produto {i}</TableCell>
                                <TableCell>R$ 300,25</TableCell>
                            </TableRow>
                        )
                      })}
                    </TableBody>
                </Table>
            </div>
        </div>
    )
}