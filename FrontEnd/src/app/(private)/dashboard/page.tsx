"use client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useSidebar } from "@/components/sidebar/sidebarcontext";
import ChartOverview from "@/components/chart";
import { useState } from "react";
import DatePicker from "react-datepicker";


export default function Dashboard() {
  const {isSidebarVisible} =  useSidebar();

  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);

  const handleFilter = ()=> {
    console.log("Filtrando de", startDate, "até", endDate);
  };

  return (
    <main className={`p-4 transition-margin duration-300 ease-in-out ${isSidebarVisible ? "ml-64" : "ml-0"}`} style={{marginTop: "3.5rem"}}>
      <section className="flex items-center gap-2 mb-4">
        <DatePicker
        selected={startDate}
        onChange={(date)=> setStartDate(date)}
        selectsStart
        startDate={startDate}
        endDate={endDate}
        className="border p-2 rounded-md w-40"
        placeholderText="Start Date"
        />
        <DatePicker
        selected={endDate}
        onChange={(date)=> setEndDate(date)}
        selectsEnd
        startDate={startDate}
        endDate={endDate}
        className="border p-2 rounded-md w-40"
        placeholderText="End Date"
        />
        <button
        onClick={handleFilter}
        className="bg-blue-700 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Filter
        </button>
      </section>

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
