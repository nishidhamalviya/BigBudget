"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export default function MealGeneratorPage() {
  const [loading, setLoading] = useState(false);

  const handleGenerate = () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => setLoading(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">AI Meal Generator</h2>
        <p className="text-muted-foreground">Let AI curate the perfect meals for your budget and goals.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Parameters</CardTitle>
            <CardDescription>Configure your daily meal plan constraints.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="budget">Daily Budget (₹)</Label>
              <Input id="budget" placeholder="e.g. 250" type="number" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="goal">Fitness Goal</Label>
              <Select>
                <SelectTrigger id="goal">
                  <SelectValue placeholder="Select a goal" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="weight-loss">Weight Loss</SelectItem>
                  <SelectItem value="muscle-gain">Muscle Gain</SelectItem>
                  <SelectItem value="maintenance">Maintenance</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="diet">Diet Preference</Label>
              <Select>
                <SelectTrigger id="diet">
                  <SelectValue placeholder="Select a diet" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="vegetarian">Vegetarian</SelectItem>
                  <SelectItem value="non-vegetarian">Non-Vegetarian</SelectItem>
                  <SelectItem value="vegan">Vegan</SelectItem>
                  <SelectItem value="eggetarian">Eggetarian</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="meals">Meals per Day</Label>
              <Select>
                <SelectTrigger id="meals">
                  <SelectValue placeholder="Number of meals" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="2">2 Meals</SelectItem>
                  <SelectItem value="3">3 Meals</SelectItem>
                  <SelectItem value="4">4 Meals</SelectItem>
                  <SelectItem value="5">5 Meals</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
          <CardFooter>
            <Button className="w-full" onClick={handleGenerate} disabled={loading}>
              {loading ? "Generating..." : "Generate Meal Plan"}
            </Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Generated Plan</CardTitle>
            <CardDescription>Your optimized AI meal plan.</CardDescription>
          </CardHeader>
          <CardContent>
             {loading ? (
               <div className="flex h-full items-center justify-center py-12">
                 <div className="animate-pulse flex flex-col items-center space-y-4">
                   <div className="h-12 w-12 rounded-full bg-muted"></div>
                   <div className="h-4 w-32 rounded bg-muted"></div>
                 </div>
               </div>
             ) : (
                <div className="flex flex-col h-[300px] items-center justify-center text-muted-foreground text-sm text-center">
                  <p>Click Generate to see your personalized</p>
                  <p>budget-friendly meal plan.</p>
                </div>
             )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
