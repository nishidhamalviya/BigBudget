# BudgetBite AI

A production-ready Full-Stack AI Budget Meal Curator built with Next.js 15, FastAPI, Prisma, Clerk, and OpenAI.

## Features
- **AI Meal Generator**: Generates cost-optimized meal plans using OpenAI based on your budget, fitness goals, and dietary preferences.
- **Authentication**: Secure login, signup, and user management via Clerk.
- **Dashboard**: Track daily/weekly budget usage, calorie consumption, and macro trends.
- **Modern UI**: Built with ShadCN UI, Tailwind CSS, and Recharts.
- **Robust Backend**: FastAPI backend connected to PostgreSQL via Prisma ORM.

## Tech Stack
- **Frontend**: Next.js 15 (App Router), TypeScript, Tailwind CSS, Shadcn UI, Recharts, Zustand
- **Backend**: FastAPI, Python 3.10+, Prisma Client Python
- **Database**: PostgreSQL
- **Authentication**: Clerk

## Setup Instructions

### 1. Database & Environment Variables
Before running the application, you need to set up your environment variables.

**Backend (`backend/.env`):**
```env
DATABASE_URL="postgresql://user:password@localhost:5432/budgetbites"
OPENAI_API_KEY="sk-your-openai-api-key"
CLERK_SECRET_KEY="sk_test_..."
```

**Frontend (`frontend/.env.local`):**
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="pk_test_..."
CLERK_SECRET_KEY="sk_test_..."
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_API_URL="http://localhost:8000"
```

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Activate the virtual environment (Windows):
   ```bash
   .\venv\Scripts\Activate.ps1
   ```
3. Run Prisma Migrations to create the database tables:
   ```bash
   prisma db push
   # or
   prisma migrate dev
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend will be running at `http://localhost:8000`.

### 3. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies (already installed if you used the script, but just in case):
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
   The frontend will be running at `http://localhost:3000`.

## Deployment
- **Frontend (Vercel)**: Simply connect your GitHub repository to Vercel. Ensure you add the environment variables in the Vercel dashboard.
- **Backend (Railway)**: Connect the `backend` folder to Railway. Set the Start Command to `uvicorn app.main:app --host 0.0.0.0 --port $PORT` and add the required environment variables.
