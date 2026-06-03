import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function DashboardPage() {
  return (
    <div className="flex-1 space-y-4">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Daily Budget Left
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₹150.00</div>
            <p className="text-xs text-muted-foreground">
              +20.1% from yesterday
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Calories Consumed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,850 kcal</div>
            <p className="text-xs text-muted-foreground">
              Goal: 2,500 kcal
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Protein Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">110g</div>
            <p className="text-xs text-muted-foreground">
              Goal: 150g
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Weekly Spend
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₹1,050.00</div>
            <p className="text-xs text-muted-foreground">
              +15% from last week
            </p>
          </CardContent>
        </Card>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Nutrition Trends</CardTitle>
            <CardDescription>
              Your macros over the last 7 days.
            </CardDescription>
          </CardHeader>
          <CardContent className="pl-2">
            {/* Chart placeholder */}
            <div className="h-[300px] w-full bg-muted/20 rounded flex items-center justify-center text-muted-foreground">
              Recharts AreaChart goes here
            </div>
          </CardContent>
        </Card>
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Recent Meals</CardTitle>
            <CardDescription>
              You've had 14 meals this week.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* List placeholder */}
            <div className="space-y-8">
              <div className="flex items-center">
                <div className="ml-4 space-y-1">
                  <p className="text-sm font-medium leading-none">Chicken Biryani</p>
                  <p className="text-sm text-muted-foreground">Lunch • 800 kcal</p>
                </div>
                <div className="ml-auto font-medium">+₹180.00</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
