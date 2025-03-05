"use client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useSidebar } from "@/components/sidebar/sidebarcontext";
import ChartOverview from "@/components/chart";

export default function Dashboard() {
  const {isSidebarVisible} =  useSidebar();

  return (
    <main className={`p-4 transition-margin duration-300 ease-in-out ${isSidebarVisible ? "ml-64" : "ml-0"}`} style={{marginTop: "3.5rem"}}>
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <div className="flex items-left justify-left">
                <CardTitle className="text-lg sm:text-xl text-gray-500 select-none">
                  Entry Quantity of Products
                </CardTitle>
              </div>
              <CardContent>
                <p className="text-base sm:text-lg font-semibold">464</p>
              </CardContent>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <div className="text-lg sm:text-xl text-gray-500 justify-left">
                <CardTitle className="text-lg sm:text-xl text-gray-500 select-none">
                  Exit Quantity of Products
                </CardTitle>
              </div>
              <CardContent>
                <p className="text-base sm:text-lg font-semibold">2.112</p>
              </CardContent>
            </CardHeader>
          </Card>
      </section>
      <section className="mt-4">
        <ChartOverview />
      </section>
    </main>
  );
}
