  "use client"
  import { ChartOverview } from "@/components/chart";
  import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
  import { ArrowDown, SquareArrowOutDownLeft } from "lucide-react";
  import { DateRange } from "react-day-picker";
  import { Button } from "@/components/ui/button";
  import { Calendar } from "@/components/ui/calendar";
  import { useSidebar } from "@/components/sidebar/sidebarContext";
  import ""
  

  export default function Home() {
    const {isSidebarVisible} = useSidebar();

    return (
    <main className={`p-4 transition-margin duration-300 ease-in-out ${isSidebarVisible ? "ml-64" : "ml-0"}`} style={{marginTop: "3.5rem"}}>
        <section className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <div className="flex items-left justify-left">
                <CardTitle className="text-lg sm:text-x1 text-gray-500 select-none">
                  Entry Quantity of Products
                </CardTitle>
              </div>
              <CardContent>
                <p className="text-base sm:text-lg font-bold">464</p>
              </CardContent>
            </CardHeader>
          </Card>
       
          <Card>
            <CardHeader>
              <div className="flex items-center justify-left">
                <CardTitle className="text-lg sm:text-x1 text-gray-500 select-none">
                  Exit Quantity of Products
                </CardTitle>
              </div>
              <CardContent>
                <p className="text-base sm:text-lg font-bold">2.112</p>
              </CardContent>
            </CardHeader>
          </Card>
        </section>
        <section className="mt-4">
          <ChartOverview/>
        </section>
    </main>
    );
  }
