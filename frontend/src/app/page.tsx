'use client'

import * as React from "react"
import Link from "next/link"
import { ThemeToggle } from "@/components/theme-toggle"
import { TerminalPreview } from "@/components/TerminalPreview"
import { Camera, Sparkles, Receipt, Check, ArrowRight } from "lucide-react"

export default function AppRoot() {
  return (
    <main className="min-h-screen bg-transparent relative selection:bg-brand-orange/30">
      
      {/* NAVBAR */}
      <nav className="fixed top-0 inset-x-0 h-16 z-50 bg-background/70 backdrop-blur-xl border-b border-border">
        <div className="container mx-auto px-6 h-full flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 cursor-pointer group">
            <div className="w-8 h-8 rounded-lg bg-brand-orange flex items-center justify-center transition-transform group-hover:scale-105">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z"></path></svg>
            </div>
            <span className="font-heading font-bold text-xl tracking-tight text-foreground">BudgetBites</span>
          </Link>
          
          <div className="hidden md:flex items-center gap-8 font-sans font-medium text-sm text-muted-foreground">
            <Link href="/dashboard" className="hover:text-foreground transition-colors">Dashboard</Link>
            <Link href="/meal-generator" className="hover:text-foreground transition-colors">Menu</Link>
            <Link href="/analytics" className="hover:text-foreground transition-colors">Analytics</Link>
          </div>
          
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <Link href="/dashboard" className="hidden sm:block text-sm font-medium text-muted-foreground hover:text-foreground transition-colors px-2 py-2">
              Sign In
            </Link>
            <Link href="/dashboard" className="bg-brand-orange hover:bg-brand-orange/90 text-white text-sm font-medium px-5 py-2 rounded-full transition-transform active:scale-[0.97]">
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      <div className="pt-32 pb-16 px-6 container mx-auto">
        {/* HERO SECTION */}
        <section className="grid lg:grid-cols-[55%_45%] gap-12 lg:gap-8 items-center min-h-[70vh]">
          {/* Left Column: Copy */}
          <div className="flex flex-col space-y-7 max-w-2xl">
            <div className="flex flex-col gap-3">
              <div className="w-0.5 h-10 bg-brand-orange"></div>
              <div className="text-[11px] font-bold tracking-[0.2em] text-muted-foreground uppercase">
                AI-Powered Meal Planning
              </div>
            </div>
            
            <h1 className="font-heading text-[56px] leading-[1.05] tracking-[-1.5px] text-foreground">
              Eat well. <span className="italic text-brand-green">Spend less.</span><br/>Know why.
            </h1>
            
            <p className="text-lg text-muted-foreground leading-relaxed font-sans max-w-[480px]">
              Scan your fridge, get macro-balanced meals under your budget. Analyze Zomato orders before you regret them.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center gap-4 pt-4">
              <Link href="/dashboard" className="w-full sm:w-auto bg-foreground text-background hover:bg-foreground/90 font-medium px-7 py-3.5 rounded-lg text-center transition-all active:scale-[0.97] flex items-center justify-center gap-2 group">
                Start for free
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
              </Link>
              <Link href="#features" className="w-full sm:w-auto border-tint bg-transparent hover:bg-surface2 text-foreground font-medium px-7 py-3.5 rounded-lg text-center transition-all active:scale-[0.97]">
                See how it works
              </Link>
            </div>
            
            {/* Stats Row */}
            <div className="pt-10 mt-6 border-t border-border grid grid-cols-3 gap-6">
              <div className="flex flex-col gap-1">
                <span className="font-heading text-[26px] text-foreground tracking-tight">₹340</span>
                <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">Avg saved/week</span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="font-heading text-[26px] text-foreground tracking-tight">2,100</span>
                <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">Kcal tracked</span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="font-heading text-[26px] text-foreground tracking-tight">14k+</span>
                <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">Meals optimized</span>
              </div>
            </div>
          </div>

          {/* Right Column: Live App Card UI */}
          <div className="relative flex justify-center lg:justify-end">
            <div className="relative w-full max-w-[440px]">
              {/* Glow Behind Card */}
              <div className="absolute inset-0 hero-glow rounded-3xl"></div>
              
              {/* Actual Card */}
              <div className="relative bg-card border-tint rounded-[24px] p-7 card-shadow">
                
                <div className="flex items-center justify-between mb-8">
                  <h3 className="font-heading italic text-2xl text-foreground">Today&apos;s Plan</h3>
                  <span className="text-[10px] uppercase tracking-widest font-bold bg-brand-green/15 text-brand-green px-2.5 py-1 rounded-md">Optimized</span>
                </div>

                <div className="space-y-3 mb-8">
                  {/* Meal Row 1 */}
                  <div className="flex items-center justify-between p-2 -mx-2 rounded-lg hover:bg-surface2/50 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="w-1.5 h-1.5 rounded-full bg-amber-500"></div>
                      <div>
                        <div className="text-[15px] font-medium text-foreground">Oats & banana bowl</div>
                        <div className="text-[13px] text-muted-foreground mt-0.5">320 kcal · 12g protein</div>
                      </div>
                    </div>
                    <div className="text-[15px] font-heading font-bold tracking-tight text-foreground">₹48</div>
                  </div>
                  
                  {/* Meal Row 2 */}
                  <div className="flex items-center justify-between p-2 -mx-2 rounded-lg hover:bg-surface2/50 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="w-1.5 h-1.5 rounded-full bg-brand-green"></div>
                      <div>
                        <div className="text-[15px] font-medium text-foreground">Dal rice + sabzi</div>
                        <div className="text-[13px] text-muted-foreground mt-0.5">540 kcal · 22g protein</div>
                      </div>
                    </div>
                    <div className="text-[15px] font-heading font-bold tracking-tight text-foreground">₹95</div>
                  </div>

                  {/* Meal Row 3 */}
                  <div className="flex items-center justify-between p-2 -mx-2 rounded-lg hover:bg-surface2/50 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
                      <div>
                        <div className="text-[15px] font-medium text-foreground">Paneer salad wrap</div>
                        <div className="text-[13px] text-muted-foreground mt-0.5">410 kcal · 28g protein</div>
                      </div>
                    </div>
                    <div className="text-[15px] font-heading font-bold tracking-tight text-foreground">₹110</div>
                  </div>
                </div>

                {/* Progress Bar Area - Split */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-[11px] font-medium">
                      <span className="text-muted-foreground uppercase tracking-wider">Kcal</span>
                      <span className="text-foreground">1,270/2,100</span>
                    </div>
                    <div className="w-full h-1.5 bg-surface2 rounded-full overflow-hidden">
                      <div className="h-full bg-brand-orange w-[60%] rounded-full"></div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-[11px] font-medium">
                      <span className="text-muted-foreground uppercase tracking-wider">Protein</span>
                      <span className="text-foreground">62g/90g</span>
                    </div>
                    <div className="w-full h-1.5 bg-surface2 rounded-full overflow-hidden">
                      <div className="h-full bg-brand-green w-[68%] rounded-full"></div>
                    </div>
                  </div>
                </div>

                {/* Floating Pill */}
                <div className="absolute -bottom-5 -right-5 bg-card border-tint px-5 py-3 rounded-full card-shadow flex items-center gap-3">
                  <div className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-green opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-green"></span>
                  </div>
                  <span className="text-[13px] font-medium text-foreground">Saved ₹183 today</span>
                </div>
                
              </div>
            </div>
          </div>
        </section>

        {/* FEATURES SECTION */}
        <section id="features" className="py-32">
          <div className="flex items-center gap-3 mb-14">
            <h2 className="text-xs font-bold tracking-[0.2em] text-muted-foreground uppercase flex items-center gap-2">
              <span className="text-[10px]">◆</span> What it does
            </h2>
            <div className="h-px w-full bg-border"></div>
          </div>

          {/* Asymmetric 2-column Grid */}
          <div className="grid lg:grid-cols-[1.6fr_1fr] gap-6">
            
            {/* Left Card: Main Feature */}
            <div className="bg-card border-tint rounded-[24px] p-8 card-shadow flex flex-col justify-between transition-colors hover:border-brand-orange/30">
              <div className="mb-10 lg:w-4/5">
                <div className="w-12 h-12 rounded-xl bg-brand-orange/10 text-brand-orange flex items-center justify-center mb-6 border border-brand-orange/20">
                  <Camera className="w-6 h-6" />
                </div>
                <h3 className="font-heading text-[32px] leading-tight text-foreground mb-4">Scan ingredients, get real meals</h3>
                <p className="text-muted-foreground font-sans text-[15px] leading-relaxed max-w-md">
                  Point your camera at your fridge. Our AI instantly identifies what you have and generates perfectly portioned, budget-friendly recipes.
                </p>
              </div>

              <div className="relative w-full h-[220px]">
                {/* Terminal Component for Typing Effect */}
                <TerminalPreview />
                
                {/* Detected Ingredients Overlaid outside the terminal */}
                <div className="absolute -bottom-4 right-4 z-20 flex flex-wrap gap-2 justify-end w-full max-w-[280px]">
                  <span className="text-[11px] font-medium px-2.5 py-1.5 rounded-full bg-brand-green/20 text-brand-green flex items-center gap-1.5 shadow-sm border border-brand-green/30">Eggs <Check className="w-3 h-3"/></span>
                  <span className="text-[11px] font-medium px-2.5 py-1.5 rounded-full bg-brand-green/20 text-brand-green flex items-center gap-1.5 shadow-sm border border-brand-green/30">Paneer <Check className="w-3 h-3"/></span>
                  <span className="text-[11px] font-medium px-2.5 py-1.5 rounded-full bg-brand-green/20 text-brand-green flex items-center gap-1.5 shadow-sm border border-brand-green/30">Spinach <Check className="w-3 h-3"/></span>
                </div>
              </div>
            </div>

            {/* Right Column: 2 Stacked Smaller Cards */}
            <div className="flex flex-col gap-6">
              
              {/* Right Top Card: AI Meal Generation */}
              <div className="bg-card border-tint rounded-[24px] p-7 card-shadow flex-1 transition-colors hover:border-brand-green/30">
                <div className="w-10 h-10 rounded-xl bg-brand-green/10 text-brand-green flex items-center justify-center mb-5 border border-brand-green/20">
                  <Sparkles className="w-5 h-5" />
                </div>
                <h3 className="font-heading text-2xl text-foreground mb-2">AI meal generation</h3>
                <p className="text-muted-foreground text-[14px] leading-relaxed font-sans">
                  Macro-balanced plans built entirely around your budget constraints. Updated daily based on what you have.
                </p>
              </div>

              {/* Right Bottom Card: Analyze Deliveries */}
              <div className="bg-card border-tint rounded-[24px] p-7 card-shadow flex-[1.5] flex flex-col justify-between transition-colors hover:border-blue-500/30">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-500 flex items-center justify-center mb-5 border border-blue-500/20">
                    <Receipt className="w-5 h-5" />
                  </div>
                  <h3 className="font-heading text-2xl text-foreground mb-2">Analyze deliveries</h3>
                  <p className="text-muted-foreground text-[14px] leading-relaxed font-sans mb-6">
                    Paste your Zomato order and instantly see the real cost.
                  </p>
                </div>
                
                {/* Mini Receipt UI */}
                <div className="bg-surface2 rounded-xl p-5 border-tint relative">
                  <div className="flex justify-between items-center text-[13px] mb-3">
                    <span className="text-muted-foreground">Order total</span>
                    <span className="font-semibold text-foreground">₹490</span>
                  </div>
                  <div className="flex justify-between items-center text-[13px] mb-4">
                    <span className="text-muted-foreground">Homemade equiv</span>
                    <span className="font-bold text-brand-green">₹155</span>
                  </div>
                  <div className="h-px w-full bg-border mb-4 border-dashed"></div>
                  <div className="flex items-center justify-center gap-2 text-[12px] bg-brand-orange/10 text-brand-orange py-2 px-3 rounded-lg border border-brand-orange/20">
                    <span className="font-medium tracking-wide">300% markup · 450 empty kcal</span>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </section>

      </div>
    </main>
  )
}
