import { ChartOverview } from "@/components/chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DollarSign } from "lucide-react";

export default function Home() {
  return (
    <main className="sm:ml-14 p-4">
      <section className="grid grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-center">
              <CardTitle className="text-lg sm:text-xl text-blue-500 select-none">
                Quantidade de Produtos de entrada
              </CardTitle>
              <DollarSign className="ml-auto w-4 h4"/>
            </div>
    
          </CardHeader>
          <CardContent>
            <p className="text-base sm:text-lg font-bold">4.413</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-center">
              <CardTitle className="text-lg sm:text-xl text-blue-500 select-none">
                Quantidade de saída de produtos
              </CardTitle>
              <DollarSign className="ml-auto w-4 h4"/>
            </div>

          </CardHeader>
          <CardContent>
            <p className="text-base sm:text-lg font-bold">6.722</p>
          </CardContent>
        </Card>

      </section>

      <section className="mt-4 flex flex-col md:flex-row gap-4">
        <ChartOverview/>
      </section>
    </main>
  );
}
