"use client"
import {Bar, CartesianGrid, XAxis, YAxis, BarChart, Tooltip, ResponsiveContainer} from "recharts";
import { Card, CardContent,CardHeader, CardTitle } from "../ui/card";
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "../ui/chart";

export default function ChartOverview(){

    const chartData = [
        {name: "Home Depot", value: 1000},
        {name: "Loja 1", value: 2000},
        {name: "Loja 2", value: 3000},
        {name: "Loja 3", value: 4000},
        {name: "Loja 4", value: 5000},
        {name: "Loja 5", value: 6000}
    ];

    const chartConfig = {
        desktop:{
            label:"Desktop",
            color:"#2563eb",
        },
        mobile: {
            label:"Mobile",
            color:"#60a5fa",
        },
    } satisfies ChartConfig

    return(
        <Card className="w-full">
            <CardHeader>
                <div className="flex items-center justify-center">
                    <CardTitle className="text-lg sm:text-xl text-gray-600">
                        Total Stores
                    </CardTitle>
                </div>
            </CardHeader>
            <CardContent>
                <div className="flex justify-center">
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart
                            layout="vertical"
                            data={chartData}
                            margin={{top:20, right: 30, left: 20, bottom:5}}
                        >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis type="number" />
                            <YAxis dataKey="name" type="category" />
                            <Tooltip />
                            <Bar dataKey="value" fill="#2563eb" />
                            <ChartTooltip content={<ChartTooltipContent />} />
                            <Bar dataKey="desktop" fill="var(--color-desktop)"radius={4}/>
                            <Bar dataKey="mobile" fill="var(--color-desktop)"radius={4}/>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    )
}