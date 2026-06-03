"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Camera, Upload, List } from "lucide-react"

export default function IngredientScannerPage() {
  const [loading, setLoading] = useState(false);
  const [ingredients, setIngredients] = useState<string[]>([]);

  const handleUpload = () => {
    setLoading(true);
    // Simulate AI detection
    setTimeout(() => {
      setIngredients(["Rice", "Eggs", "Onion", "Tomato", "Chicken Breast"]);
      setLoading(false);
    }, 2000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Ingredient Scanner</h2>
        <p className="text-muted-foreground">Upload a photo of your pantry or fridge, and let AI identify your ingredients.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Scan Pantry</CardTitle>
            <CardDescription>Take a picture or upload an image.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-center rounded-lg border border-dashed border-muted-foreground/25 px-6 py-10">
              <div className="text-center">
                <Camera className="mx-auto h-12 w-12 text-muted-foreground" aria-hidden="true" />
                <div className="mt-4 flex text-sm leading-6 text-muted-foreground">
                  <label
                    htmlFor="file-upload"
                    className="relative cursor-pointer rounded-md bg-background font-semibold text-primary focus-within:outline-none focus-within:ring-2 focus-within:ring-primary focus-within:ring-offset-2 hover:text-primary/80"
                  >
                    <span>Upload a file</span>
                    <Input id="file-upload" name="file-upload" type="file" className="sr-only" />
                  </label>
                  <p className="pl-1">or drag and drop</p>
                </div>
                <p className="text-xs leading-5 text-muted-foreground">PNG, JPG, GIF up to 10MB</p>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="outline"><Camera className="mr-2 h-4 w-4" /> Open Camera</Button>
            <Button onClick={handleUpload} disabled={loading}>
              {loading ? "Analyzing..." : "Analyze Image"}
            </Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Detected Ingredients</CardTitle>
            <CardDescription>AI-detected items ready for meal planning.</CardDescription>
          </CardHeader>
          <CardContent>
             {loading ? (
               <div className="space-y-2">
                 <div className="h-4 w-full animate-pulse rounded bg-muted"></div>
                 <div className="h-4 w-5/6 animate-pulse rounded bg-muted"></div>
                 <div className="h-4 w-4/6 animate-pulse rounded bg-muted"></div>
               </div>
             ) : ingredients.length > 0 ? (
               <ul className="space-y-2">
                 {ingredients.map((item, i) => (
                   <li key={i} className="flex items-center gap-2 rounded-md bg-muted/50 px-3 py-2 text-sm">
                     <List className="h-4 w-4 text-primary" />
                     {item}
                   </li>
                 ))}
               </ul>
             ) : (
                <div className="flex h-32 items-center justify-center text-muted-foreground text-sm">
                  Upload an image to see results here.
                </div>
             )}
          </CardContent>
          {ingredients.length > 0 && (
            <CardFooter>
              <Button className="w-full">Generate Recipes with these Ingredients</Button>
            </CardFooter>
          )}
        </Card>
      </div>
    </div>
  )
}
