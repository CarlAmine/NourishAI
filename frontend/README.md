# NourishAI Frontend

A modern React + Vite frontend for NourishAI — an AI-powered nutrition and recipe recommendation app.

## Tech Stack

- React 18 + Vite + TypeScript
- Tailwind CSS (forest green / cream design system)
- React Router v6
- Axios
- Recharts
- Lucide React
- Framer Motion

## Setup

```bash
cd frontend
npm install
```

Create a `.env.local` file:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

Then start the dev server:

```bash
npm run dev   # http://localhost:5173
```

## Pages

| Route | Page |
|---|---|
| `/` | Home / Dashboard |
| `/search` | Recipe Search |
| `/recommend` | AI Recommender |
| `/meal-plan` | Weekly Meal Plan |
| `/nutrition` | Nutrition Tracker |

## Backend

Make sure the FastAPI backend is running on port 8000 before starting the frontend.
See `../backend/README.md` for backend setup instructions.
