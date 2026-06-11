"use client"
#usedanalyzerdataforchnages
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Utensils, IndianRupee, AlertCircle } from "lucide-react"

export default function SwiggyAnalyzerPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setResult({
        calories: 1250,
        protein: 45,
        fat: 65,
        carbs: 120,
        healthScore: 4.2,
        costEfficiency: 3.5,
        alternatives: ["Make it at home for ₹120", "Order a healthy bowl instead for ₹180"],
        savings: 150
      });
      setLoading(false);
    }, 2500);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Food Delivery Analyzer</h2>
        <p className="text-muted-foreground">Paste your Swiggy or Zomato order to get a health & cost efficiency breakdown.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Analyze Order</CardTitle>
            <CardDescription>Enter the details of your food delivery order.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Restaurant Name</Label>
              <Input placeholder="e.g. Behrouz Biryani" />
            </div>
            <div className="space-y-2">
              <Label>Ordered Items</Label>
              <Input placeholder="e.g. 1x Chicken Dum Biryani, 1x Raita" />
            </div>
            <div className="space-y-2">
              <Label>Total Cost (₹)</Label>
              <Input placeholder="e.g. 350" type="number" />
            </div>
          </CardContent>
          <CardFooter>
            <Button className="w-full" onClick={handleAnalyze} disabled={loading}>
              {loading ? "Analyzing..." : "Analyze Order"}
            </Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI Verdict</CardTitle>
            <CardDescription>Nutrition and budget efficiency score.</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
               <div className="space-y-2 py-4">
                 <div className="h-4 w-full animate-pulse rounded bg-muted"></div>
                 <div className="h-4 w-5/6 animate-pulse rounded bg-muted"></div>
               </div>
            ) : result ? (
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex flex-col items-center justify-center p-4 bg-muted/30 rounded-lg">
                    <Utensils className="h-6 w-6 text-primary mb-2" />
                    <span className="text-2xl font-bold">{result.calories}</span>
                    <span className="text-xs text-muted-foreground">Calories</span>
                  </div>
                  <div className="flex flex-col items-center justify-center p-4 bg-muted/30 rounded-lg">
                    <IndianRupee className="h-6 w-6 text-primary mb-2" />
                    <span className="text-2xl font-bold">{result.costEfficiency}/10</span>
                    <span className="text-xs text-muted-foreground">Cost Efficiency</span>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <h4 className="font-semibold flex items-center gap-2">
                    <AlertCircle className="h-4 w-4" /> AI Recommendations
                  </h4>
                  <ul className="list-disc pl-5 text-sm text-muted-foreground space-y-1">
                    {result.alternatives.map((alt: string, i: number) => (
                      <li key={i}>{alt}</li>
                    ))}
                  </ul>
                  <div className="mt-4 p-3 bg-green-500/10 text-green-600 rounded-md text-sm font-medium">
                    You could save approx ₹{result.savings} by cooking a similar meal at home!
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex h-32 items-center justify-center text-muted-foreground text-sm">
                Enter your order details to see the analysis.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
