"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Analytics</h2>
        <p className="text-muted-foreground">Track your nutrition, weight, and budget trends over time.</p>
      </div>

      <Tabs defaultValue="nutrition" className="space-y-4">
        <TabsList>
          <TabsTrigger value="nutrition">Nutrition</TabsTrigger>
          <TabsTrigger value="budget">Budget</TabsTrigger>
          <TabsTrigger value="weight">Weight</TabsTrigger>
        </TabsList>
        <TabsContent value="nutrition" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Macro Breakdown</CardTitle>
              <CardDescription>Your protein, carbs, and fat intake distribution.</CardDescription>
            </CardHeader>
            <CardContent className="h-[400px] flex items-center justify-center bg-muted/20 rounded-lg">
              <span className="text-muted-foreground">Recharts PieChart / BarChart Here</span>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="budget" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Spending Trends</CardTitle>
              <CardDescription>Daily spending vs. budget limit.</CardDescription>
            </CardHeader>
            <CardContent className="h-[400px] flex items-center justify-center bg-muted/20 rounded-lg">
              <span className="text-muted-foreground">Recharts LineChart Here</span>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="weight" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Weight Progress</CardTitle>
              <CardDescription>Track your weight changes over time.</CardDescription>
            </CardHeader>
            <CardContent className="h-[400px] flex items-center justify-center bg-muted/20 rounded-lg">
              <span className="text-muted-foreground">Recharts AreaChart Here</span>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
